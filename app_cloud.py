#!/usr/bin/env python3
"""
Streamlit Cloud App for Mnemonic Matrix - BibTeX Processing System
Complete working version with sidebar fixes and fallback upload
"""

import streamlit as st
import json
import tempfile
import os
from pathlib import Path
from typing import List, Dict
import plotly.graph_objects as go
import plotly.express as px
from collections import Counter
from datetime import datetime
import numpy as np

# Import our modules
from bibtex_processor import BibTeXProcessor
from bibtex_matrix_tagger import BibTeXMatrixTagger
from visualizer import Visualizer

# Page configuration - Simple and clean
st.set_page_config(
    page_title="Mnemonic Matrix - BibTeX Processor",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS to ensure sidebar visibility and add some styling
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Ensure sidebar is visible */
    .css-1d391kg {visibility: visible !important;}
    .css-1lcbmhc {visibility: visible !important;}
    
    /* Make sidebar more prominent */
    .css-1cypcdb {background-color: #f0f2f6 !important;}
    .css-1d391kg {background-color: #f0f2f6 !important;}
    
    /* Ensure sidebar content is visible */
    .css-1lcbmhc {visibility: visible !important;}
    .css-1d391kg {visibility: visible !important;}
    
    /* Force sidebar to be visible */
    .css-1d391kg {display: block !important;}
    .css-1lcbmhc {display: block !important;}
    
    /* Make sidebar wider and more obvious */
    .css-1d391kg {width: 300px !important;}
    .css-1lcbmhc {width: 300px !important;}
    
    /* Force visualizations to use full width */
    .stHorizontalBlock {width: 100% !important;}
    .stVerticalBlock {width: 100% !important;}
    
    /* Ensure HTML components use full width */
    .stHtml {width: 100% !important; max-width: none !important;}
    
    /* Force main content to use full width */
    .main .block-container {max-width: none !important; padding-left: 1rem !important; padding-right: 1rem !important;}
    
    /* Ensure columns use full width */
    .row-widget.stHorizontal {width: 100% !important;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def create_visualizations_cached(papers):
    """Cache the visualizations to prevent recreation."""
    viz = Visualizer()
    return viz.create_visualizations(papers)

class StreamlitApp:
    """Streamlit application for BibTeX processing."""
    
    def __init__(self):
        self.bibtex_processor = BibTeXProcessor()
        self.matrix_tagger = BibTeXMatrixTagger()
        self.visualizer = Visualizer()
        
        # Initialize matrix tagger with trained models
        self._initialize_matrix_tagger()
    
    def _initialize_matrix_tagger(self):
        """Initialize the matrix tagger with new comprehensive system."""
        try:
            # Try to load new models first
            self.matrix_tagger.load_models('matrix_tagger_models_new.pkl')
            st.success("✅ Loaded new comprehensive matrix tagger models")
        except FileNotFoundError:
            try:
                # Fallback to old models
                self.matrix_tagger.load_models('matrix_tagger_models.pkl')
                st.warning("⚠️ Loaded old models (consider retraining for new system)")
            except FileNotFoundError:
                st.error("❌ No trained models found. Please ensure model files are uploaded to GitHub.")
                self.matrix_tagger = None
    
    def process_bibtex_content(self, content: str) -> List[Dict]:
        """Process BibTeX content and return tagged papers."""
        # Save content to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bib', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_file = f.name
        
        try:
            # Parse BibTeX
            papers = self.bibtex_processor.parse_bibtex(temp_file)
            
            # Auto-tag papers with matrix tags using enhanced analysis
            if self.matrix_tagger:
                for paper in papers:
                    paper_text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
                    
                    # Use publication date restriction if year is available
                    year = paper.get('year')
                    if year and year != 'Unknown' and year != '':
                        try:
                            publication_year = int(year)
                            matrix_tags = self.matrix_tagger.predict_tags_with_publication_date_restriction(
                                paper_text, publication_year
                            )
                            st.info(f"📅 Applied publication date restriction for {publication_year}")
                        except ValueError:
                            # Fall back to content-based prediction if year is invalid
                            matrix_tags = self.matrix_tagger.analyze_paper_for_prediction(paper_text)
                            st.warning(f"⚠️ Invalid year '{year}', using content-based prediction")
                    else:
                        # No year available, use content-based prediction
                        matrix_tags = self.matrix_tagger.analyze_paper_for_prediction(paper_text)
                        st.info("ℹ️ No publication year provided, using content-based prediction")
                    
                    # Combine all matrix tags into a single list
                    all_tags = []
                    for category, tags in matrix_tags.items():
                        all_tags.extend(tags)
                    
                    paper['tags'] = all_tags
            else:
                # If no tagger, add empty tags
                for paper in papers:
                    paper['tags'] = []
            
            return papers
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def process_json_papers(self, json_content: str) -> List[Dict]:
        """Process JSON papers and return them with optional auto-tagging."""
        try:
            data = json.loads(json_content)
            papers = data.get('papers', []) if isinstance(data, dict) else data
            
            # Ensure each paper has required fields
            processed_papers = []
            for paper in papers:
                if isinstance(paper, dict) and paper.get('title'):
                    # Add default fields if missing
                    paper.setdefault('authors', [])
                    paper.setdefault('year', 'Unknown')
                    paper.setdefault('journal', 'Unknown')
                    paper.setdefault('abstract', '')
                    paper.setdefault('tags', [])
                    processed_papers.append(paper)
            
            return processed_papers
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON format: {e}")
            return []
    
    def create_zotero_export(self, papers: List[Dict]) -> str:
        """Create a Zotero-compatible export format with matrix tags."""
        zotero_entries = []
        
        for i, paper in enumerate(papers):
            # Create a unique key for Zotero
            key = f"paper_{i}_{paper.get('year', 'unknown')}"
            
            # Format authors
            authors = paper.get('authors', [])
            if authors:
                author_str = " and ".join(authors)
            else:
                author_str = "Unknown"
            
            # Create Zotero entry
            entry_lines = [f"@article{{{key},"]
            entry_lines.append(f"  title = {{{paper.get('title', '')}}},")
            entry_lines.append(f"  author = {{{author_str}}},")
            
            if paper.get('year'):
                entry_lines.append(f"  year = {{{paper.get('year')}}},")
            if paper.get('journal'):
                entry_lines.append(f"  journal = {{{paper.get('journal')}}},")
            if paper.get('abstract'):
                entry_lines.append(f"  abstract = {{{paper.get('abstract')}}},")
            
            # Add tags as keywords
            if paper.get('tags'):
                tags_str = ', '.join(paper.get('tags'))
                entry_lines.append(f"  keywords = {{{tags_str}}},")
            
            entry_lines.append("}")
            zotero_entries.append('\n'.join(entry_lines))
        
        return '\n\n'.join(zotero_entries)
    
    def create_csv_export(self, papers: List[Dict]) -> str:
        """Create CSV export of papers."""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Title', 'Authors', 'Year', 'Journal', 'Abstract', 'Tags'])
        
        # Write data
        for paper in papers:
            authors = ', '.join(paper.get('authors', [])) if paper.get('authors') else 'Unknown'
            tags = ', '.join(paper.get('tags', [])) if paper.get('tags') else ''
            writer.writerow([
                paper.get('title', ''),
                authors,
                paper.get('year', ''),
                paper.get('journal', ''),
                paper.get('abstract', ''),
                tags
            ])
        
        return output.getvalue()
    
    def display_visualizations(self, papers: List[Dict]):
        """Display lightweight visualizations for the papers."""
        st.header("📊 Visualizations")
        
        if not papers:
            st.warning("No papers to visualize.")
            return
        
        # Create simple, lightweight visualizations instead of heavy HTML
        try:
            # Simple tag distribution bar chart
            st.subheader("🏷️ Tag Distribution")
            all_tags = []
            for paper in papers:
                all_tags.extend(paper.get('tags', []))
            
            if all_tags:
                tag_counts = Counter(all_tags)
                fig = px.bar(
                    x=list(tag_counts.keys()),
                    y=list(tag_counts.values()),
                    title="Tag Frequency",
                    labels={'x': 'Tags', 'y': 'Count'}
                )
                fig.update_layout(
                    xaxis_tickangle=-45,
                    height=400,
                    margin=dict(l=50, r=50, t=80, b=80)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No tags found in papers.")
            
            st.markdown("---")
            
            # Simple timeline scatter plot
            st.subheader("📅 Publication Timeline")
            papers_with_years = []
            for paper in papers:
                year = paper.get('year')
                if year and str(year).isdigit():
                    try:
                        papers_with_years.append({
                            'title': paper.get('title', ''),
                            'year': int(year),
                            'tags': len(paper.get('tags', []))
                        })
                    except ValueError:
                        continue
            
            if papers_with_years:
                papers_with_years.sort(key=lambda x: x['year'])
                fig = px.scatter(
                    x=[p['year'] for p in papers_with_years],
                    y=[p['tags'] for p in papers_with_years],
                    text=[p['title'][:30] + '...' if len(p['title']) > 30 else p['title'] for p in papers_with_years],
                    title="Papers by Year and Tag Count",
                    labels={'x': 'Publication Year', 'y': 'Number of Tags'}
                )
                fig.update_traces(textposition="top center")
                fig.update_layout(height=400, margin=dict(l=50, r=50, t=80, b=80))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No papers with valid publication years found.")
            
            st.markdown("---")
            
            # Simple tag category pie chart
            st.subheader("📊 Tag Categories")
            if all_tags:
                category_counts = {'Time': 0, 'Discipline': 0, 'Memory Carrier': 0, 'Concept': 0, 'Other': 0}
                for tag in all_tags:
                    if tag.startswith('T'):
                        category_counts['Time'] += 1
                    elif tag.startswith('D'):
                        category_counts['Discipline'] += 1
                    elif tag.startswith('MC'):
                        category_counts['Memory Carrier'] += 1
                    elif tag.startswith('CT'):
                        category_counts['Concept'] += 1
                    else:
                        category_counts['Other'] += 1
                
                # Only show categories with data
                categories_with_data = {k: v for k, v in category_counts.items() if v > 0}
                if categories_with_data:
                    fig = px.pie(
                        values=list(categories_with_data.values()),
                        names=list(categories_with_data.keys()),
                        title="Tag Distribution by Category"
                    )
                    fig.update_layout(height=400, margin=dict(l=50, r=50, t=80, b=80))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No categorized tags found.")
            else:
                st.info("No tags to categorize.")
                
        except Exception as e:
            st.error(f"Error creating visualizations: {str(e)}")
            st.info("Showing basic paper information instead.")
            
            # Fallback: Show basic paper info
            st.subheader("📋 Paper Summary")
            for i, paper in enumerate(papers):
                with st.expander(f"{paper.get('title', 'Unknown')} ({paper.get('year', 'Unknown')})"):
                    st.write(f"**Authors:** {', '.join(paper.get('authors', [])) if paper.get('authors') else 'Unknown'}")
                    st.write(f"**Journal:** {paper.get('journal', 'Unknown')}")
                    st.write(f"**Tags:** {', '.join(paper.get('tags', [])) if paper.get('tags') else 'None'}")
    
    def run(self):
        """Run the main application."""
        # Main header - simple and clean
        st.title("🧠 Mnemonic Matrix")
        st.markdown("### Advanced BibTeX Processing with ML Auto-tagging")
        
        # Timeline restriction notice
        st.info("🎯 **Timeline Restriction Active:** Timeline tags (T1-T5) are now based on **publication date only**, not the content discussed in the paper.")
        
        # Add main page sidebar indicator
        st.warning("🔍 **LOOK LEFT!** The sidebar should be visible on the left side of this page. If you can't see it:")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Keyboard Shortcut:** Press **'S'** to toggle sidebar")
        with col2:
            st.markdown("**Mouse:** Click **☰** (hamburger) in top-left")
        with col3:
            st.markdown("**Touch:** Look for **▶️** arrow on left edge")
        
        st.markdown("---")
        
        # FALLBACK: Add upload functionality directly on main page in case sidebar is hidden
        st.header("📥 **FALLBACK UPLOAD SECTION** (If sidebar is hidden)")
        st.warning("**If you can't see the sidebar on the left, use this section instead:**")
        
        # Direct file upload on main page
        st.subheader("📁 Upload BibTeX File")
        uploaded_file_main = st.file_uploader("Choose a BibTeX file (Main Page)", type=['bib'], key="main_page_uploader")
        
        if uploaded_file_main is not None:
            content = uploaded_file_main.read().decode('utf-8')
            papers = self.process_bibtex_content(content)
            if papers:
                st.session_state.papers = papers
                st.success(f"✅ Added {len(papers)} papers successfully!")
            else:
                st.error("❌ Failed to process BibTeX file.")
        
        st.markdown("---")
        
        # Force sidebar to be visible with a very prominent header
        st.sidebar.markdown("## 🚨 **SIDEBAR IS HERE!** 🚨")
        st.sidebar.markdown("### 📱 **Sidebar Controls**")
        st.sidebar.markdown("**If you can't see the input methods below:**")
        st.sidebar.markdown("1. **Click the hamburger menu** (☰) in the top left")
        st.sidebar.markdown("2. **Or use the arrow button** (▶️) to expand")
        st.sidebar.markdown("3. **Or press 'S' on your keyboard**")
        st.sidebar.markdown("---")
        
        # Sidebar for input methods
        with st.sidebar:
            st.header("📥 Input Methods")
            st.markdown("**Choose how to add papers:**")
            
            # Add a test button to verify sidebar is working
            if st.button("🔍 **TEST SIDEBAR** - Click me!"):
                st.balloons()
                st.success("🎉 Sidebar is working!")
            
            input_method = st.radio(
                "Choose input method:",
                ["📁 BibTeX Upload", "📋 JSON Input", "✏️ Manual Entry"]
            )
            
            if input_method == "📁 BibTeX Upload":
                st.subheader("📁 BibTeX Upload")
                uploaded_file = st.file_uploader("Choose a BibTeX file", type=['bib'])
                
                if uploaded_file is not None:
                    content = uploaded_file.read().decode('utf-8')
                    papers = self.process_bibtex_content(content)
                    if papers:
                        st.session_state.papers = papers
                        st.success(f"✅ Added {len(papers)} papers successfully!")
                    else:
                        st.error("❌ Failed to process BibTeX file.")
            
            elif input_method == "📋 JSON Input":
                st.subheader("📋 JSON Input")
                json_content = st.text_area("Paste JSON content:")
                
                if st.button("Process JSON", type="primary"):
                    if json_content:
                        papers = self.process_json_papers(json_content)
                        if papers:
                            st.session_state.papers = papers
                            st.success(f"✅ Added {len(papers)} papers successfully!")
                        else:
                            st.error("❌ Please paste valid JSON content.")
                    else:
                        st.error("❌ Please paste JSON content.")
            
            elif input_method == "✏️ Manual Entry":
                st.subheader("✏️ Manual Entry")
                
                title = st.text_input("Paper Title:")
                authors = st.text_input("Authors (comma-separated):")
                year = st.text_input("Year:")
                journal = st.text_input("Journal:")
                abstract = st.text_area("Abstract:")
                
                if st.button("Add Paper", type="primary"):
                    if title:
                        paper = {
                            'title': title,
                            'authors': [author.strip() for author in authors.split(',') if author.strip()],
                            'year': year,
                            'journal': journal,
                            'abstract': abstract,
                            'tags': []
                        }
                        
                        if 'papers' not in st.session_state:
                            st.session_state.papers = []
                        
                        st.session_state.papers.append(paper)
                        st.success("✅ Paper added successfully!")
                    else:
                        st.error("❌ Please enter at least a title.")
        
        # Main content area
        if 'papers' in st.session_state and st.session_state.papers:
            papers = st.session_state.papers
            
            # Display paper count with better spacing
            st.header("📊 Papers Analysis")
            st.markdown("---")
            
            # Use full width for metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📚 Total Papers", len(papers))
            with col2:
                total_tags = sum(len(paper.get('tags', [])) for paper in papers)
                st.metric("🏷️ Total Tags", total_tags)
            with col3:
                avg_tags = total_tags / len(papers) if papers else 0
                st.metric("📈 Avg Tags/Paper", f"{avg_tags:.1f}")
            
            st.markdown("---")
            
            # Action buttons with better spacing
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🤖 Auto-tag Papers", type="primary", use_container_width=True):
                    if self.matrix_tagger:
                        for paper in papers:
                            if not paper.get('tags'):
                                paper_text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
                                
                                # Use publication date restriction if year is available
                                year = paper.get('year')
                                if year and year != 'Unknown' and year != '':
                                    try:
                                        publication_year = int(year)
                                        matrix_tags = self.matrix_tagger.predict_tags_with_publication_date_restriction(
                                            paper_text, publication_year
                                        )
                                        st.info(f"📅 Applied publication date restriction for {publication_year}")
                                    except ValueError:
                                        # Fall back to content-based prediction if year is invalid
                                        matrix_tags = self.matrix_tagger.analyze_paper_for_prediction(paper_text)
                                        st.warning(f"⚠️ Invalid year '{year}', using content-based prediction")
                                else:
                                    # No year available, use content-based prediction
                                    matrix_tags = self.matrix_tagger.analyze_paper_for_prediction(paper_text)
                                    st.info("ℹ️ No publication year provided, using content-based prediction")
                                
                                all_tags = []
                                for category, tags in matrix_tags.items():
                                    all_tags.extend(tags)
                                paper['tags'] = all_tags
                        st.success("✅ Papers auto-tagged successfully!")
                    else:
                        st.error("❌ Matrix tagger not available. Please ensure models are loaded.")
            
            with col2:
                if st.button("🗑️ Clear All Papers", use_container_width=True):
                    st.session_state.papers = []
                    st.rerun()
            
            st.markdown("---")
            
            # Tabs for different views with better spacing
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📊 Visualizations", 
                "📋 Papers List", 
                "🏷️ Tag Analysis", 
                "📈 Timeline",
                "💾 Export"
            ])
            
            with tab1:
                self.display_visualizations(papers)
            
            with tab2:
                st.subheader("📋 Papers List")
                for i, paper in enumerate(papers):
                    with st.expander(f"{paper.get('title', 'Unknown Title')} ({paper.get('year', 'Unknown Year')})"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            authors = paper.get('authors', [])
                            if authors:
                                st.write(f"**Authors:** {', '.join(authors)}")
                            else:
                                st.write("**Authors:** Unknown")
                            st.write(f"**Journal:** {paper.get('journal', 'Unknown')}")
                            st.write(f"**Year:** {paper.get('year', 'Unknown')}")
                            if paper.get('abstract'):
                                st.write(f"**Abstract:** {paper.get('abstract', '')}")
                        
                        with col2:
                            tags = paper.get('tags', [])
                            if tags:
                                st.write("**Tags:**")
                                for tag in tags:
                                    st.markdown(f'<span style="background: #666666; color: white; padding: 4px 8px; border-radius: 12px; margin: 2px; display: inline-block; font-size: 0.8rem;">{tag}</span>', unsafe_allow_html=True)
                            else:
                                st.write("**Tags:** None assigned")
            
            with tab3:
                st.subheader("🏷️ Tag Analysis")
                st.markdown("---")
                if papers:
                    # Collect all tags
                    all_tags = []
                    for paper in papers:
                        all_tags.extend(paper.get('tags', []))
                    
                    if all_tags:
                        # Count tag frequencies
                        tag_counts = Counter(all_tags)
                        
                        # Create bar chart with full width
                        fig = px.bar(
                            x=list(tag_counts.keys()),
                            y=list(tag_counts.values()),
                            title="Tag Distribution",
                            labels={'x': 'Tags', 'y': 'Frequency'}
                        )
                        fig.update_layout(
                            xaxis_tickangle=-45,
                            height=700,  # Increased from 500
                            margin=dict(l=80, r=80, t=100, b=120),  # Increased margins
                            showlegend=True,
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.markdown("---")
                        st.markdown("")  # Extra spacing
                        
                        # Show tag details with better spacing
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("Most Common Tags")
                            st.markdown("---")
                            for tag, count in tag_counts.most_common(10):
                                st.write(f"**{tag}**: {count} papers")
                        
                        with col2:
                            st.subheader("Tag Categories")
                            st.markdown("---")
                            category_counts = {}
                            for tag in all_tags:
                                if tag.startswith('T'):
                                    category = 'Time Periods'
                                elif tag.startswith('D'):
                                    category = 'Disciplines'
                                elif tag.startswith('MC'):
                                    category = 'Memory Carriers'
                                elif tag.startswith('CT'):
                                    category = 'Concept Tags'
                                else:
                                    category = 'Other'
                                
                                category_counts[category] = category_counts.get(category, 0) + 1
                            
                            for category, count in category_counts.items():
                                st.write(f"**{category}**: {count} tags")
                    else:
                        st.info("No tags found in papers.")
                else:
                    st.info("No papers to analyze.")
            
            with tab4:
                st.subheader("📈 Timeline")
                if papers:
                    # Filter papers with valid years
                    papers_with_years = []
                    for paper in papers:
                        year = paper.get('year')
                        if year and year != 'Unknown' and str(year).isdigit():
                            try:
                                papers_with_years.append({
                                    'title': paper.get('title', ''),
                                    'year': int(year),
                                    'tags': paper.get('tags', [])
                                })
                            except ValueError:
                                continue
                    
                    if papers_with_years:
                        # Sort by year
                        papers_with_years.sort(key=lambda x: x['year'])
                        
                        # Create timeline chart
                        years = [p['year'] for p in papers_with_years]
                        titles = [p['title'][:50] + '...' if len(p['title']) > 50 else p['title'] for p in papers_with_years]
                        
                        fig = px.scatter(
                            x=years,
                            y=[1] * len(years),
                            text=titles,
                            title="Paper Timeline by Publication Year",
                            labels={'x': 'Publication Year', 'y': ''}
                        )
                        fig.update_traces(textposition="top center")
                        fig.update_layout(
                            yaxis_showticklabels=False,
                            height=600,  # Increased height
                            margin=dict(l=80, r=80, t=100, b=120),  # Increased margins
                            showlegend=True,
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.markdown("---")
                        st.markdown("")  # Extra spacing
                        
                        # Show timeline statistics
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("Timeline Statistics")
                            st.write(f"**Earliest paper**: {min(years)}")
                            st.write(f"**Latest paper**: {max(years)}")
                            st.write(f"**Time span**: {max(years) - min(years)} years")
                            st.write(f"**Total papers**: {len(papers_with_years)}")
                        
                        with col2:
                            st.subheader("Papers by Decade")
                            decade_counts = {}
                            for year in years:
                                decade = (year // 10) * 10
                                decade_counts[decade] = decade_counts.get(decade, 0) + 1
                            
                            for decade in sorted(decade_counts.keys()):
                                st.write(f"**{decade}s**: {decade_counts[decade]} papers")
                    else:
                        st.info("No papers with valid publication years found.")
                else:
                    st.info("No papers to analyze.")
            
            with tab5:
                st.subheader("💾 Export")
                if papers:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        json_data = json.dumps(papers, indent=2)
                        st.download_button(
                            label="📥 Download JSON",
                            data=json_data,
                            file_name="mnemonic_matrix_papers.json",
                            mime="application/json"
                        )
                    
                    with col2:
                        csv_data = self.create_csv_export(papers)
                        st.download_button(
                            label="📥 Download CSV",
                            data=csv_data,
                            file_name="mnemonic_matrix_papers.csv",
                            mime="text/csv"
                        )
                    
                    with col3:
                        zotero_data = self.create_zotero_export(papers)
                        st.download_button(
                            label="📥 Download BibTeX",
                            data=zotero_data,
                            file_name="mnemonic_matrix_papers.bib",
                            mime="text/plain"
                        )
                    
                    st.success("✅ Export data ready! Click the buttons above to download.")
                else:
                    st.info("No papers to export.")
        else:
            # Welcome message when no papers
            st.success("🎉 **Welcome to Mnemonic Matrix!**")
            st.write("This system automatically categorizes academic papers using advanced ML techniques.")
            
            st.subheader("Key Features:")
            st.write("📚 BibTeX file processing")
            st.write("🤖 ML-powered auto-tagging")
            st.write("📅 Timeline restriction (publication date only)")
            st.write("📊 Beautiful visualizations")
            st.write("💾 Multiple export formats")
            
            st.info("**Get started:** Use the sidebar to upload BibTeX files, paste JSON, or enter papers manually.")
            
            # Show sample data
            st.subheader("📋 Sample Papers")
            sample_papers = [
                {
                    'title': 'Collective Memory in Digital Age',
                    'authors': ['Smith, J.', 'Johnson, A.'],
                    'year': '2020',
                    'journal': 'Memory Studies',
                    'abstract': 'This paper examines collective memory in the digital era...',
                    'tags': ['T5', 'DSOC', 'MCSO', 'CTCollectiveMemory']
                },
                {
                    'title': 'Historical Memory and National Identity',
                    'authors': ['Brown, M.'],
                    'year': '1995',
                    'journal': 'History Today',
                    'abstract': 'Analysis of historical memory in national identity formation...',
                    'tags': ['T4', 'DHIS', 'MCME', 'CTNationalMemory']
                }
            ]
            
            for paper in sample_papers:
                with st.expander(f"{paper['title']} ({paper['year']})"):
                    st.write(f"**Authors:** {', '.join(paper['authors'])}")
                    st.write(f"**Journal:** {paper['journal']}")
                    st.write(f"**Abstract:** {paper['abstract']}")
                    st.write("**Tags:**")
                    for tag in paper['tags']:
                        st.markdown(f'<span style="background: #666666; color: white; padding: 4px 8px; border-radius: 12px; margin: 2px; display: inline-block; font-size: 0.8rem;">{tag}</span>', unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    app = StreamlitApp()
    app.run() 