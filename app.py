#!/usr/bin/env python3
"""
Streamlit App for Mnemonic Matrix - BibTeX Processing System
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
from auto_tagger import AutoTagger
from visualizer import Visualizer

# Page configuration
st.set_page_config(
    page_title="Mnemonic Matrix - BibTeX Processor",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .paper-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
    }
    .tag {
        background-color: #1f77b4;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-size: 0.8rem;
        margin: 0.1rem;
        display: inline-block;
    }
    .tag-input {
        border: 1px solid #ccc;
        border-radius: 0.3rem;
        padding: 0.2rem 0.5rem;
        margin: 0.1rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def create_visualizations_cached(papers):
    """Cache the visualizations to prevent recreation."""
    viz = Visualizer()
    return viz.create_visualizations(papers)

@st.cache_data
def get_papers_data(papers):
    """Cache the processed papers data."""
    return papers

class StreamlitApp:
    """Streamlit application for BibTeX processing."""
    
    def __init__(self):
        self.bibtex_processor = BibTeXProcessor()
        self.auto_tagger = AutoTagger()
        self.visualizer = Visualizer()
        
        # Create directories
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
    
    def process_bibtex_content(self, content: str) -> List[Dict]:
        """Process BibTeX content and return tagged papers."""
        # Save content to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bib', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_file = f.name
        
        try:
            # Parse BibTeX
            papers = self.bibtex_processor.parse_bibtex(temp_file)
            
            # Auto-tag papers
            for paper in papers:
                paper['tags'] = self.auto_tagger.predict_tags(
                    paper.get('title', ''), 
                    paper.get('abstract', ''), 
                    paper.get('keywords', [])
                )
            
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
        """Create a Zotero-compatible export format."""
        zotero_entries = []
        
        for i, paper in enumerate(papers):
            # Create a unique key for Zotero
            key = f"paper_{i}_{paper.get('year', 'unknown')}"
            
            # Format authors for Zotero
            authors = paper.get('authors', [])
            if isinstance(authors, list):
                author_str = " and ".join(authors)
            else:
                author_str = str(authors)
            
            # Create Zotero entry
            zotero_entry = f"""@article{{{key},
  title = {{{paper.get('title', 'Unknown Title')}}},
  author = {{{author_str}}},
  journal = {{{paper.get('journal', 'Unknown')}}},
  year = {{{paper.get('year', 'Unknown')}}},
  abstract = {{{paper.get('abstract', '')}}},
  keywords = {{{', '.join(paper.get('tags', []))}}},
  doi = {{{paper.get('doi', '')}}},
  url = {{{paper.get('url', '')}}}
}}"""
            zotero_entries.append(zotero_entry)
        
        return "\n\n".join(zotero_entries)
    
    def display_visualizations(self, papers: List[Dict]):
        """Display visualizations for the papers."""
        st.header("📊 Visualizations")
        
        if not papers:
            st.warning("No papers to visualize.")
            return
        
        # Create visualizations
        viz = Visualizer()
        viz_data = viz.create_visualizations(papers)
        
        if viz_data:
            # Display tag network
            if 'tag_network' in viz_data:
                st.subheader("🏷️ Tag Network")
                if viz_data['tag_network'].startswith('<'):
                    st.components.v1.html(viz_data['tag_network'], height=600)
                else:
                    st.write(viz_data['tag_network'])
            
            # Display tag distribution
            if 'tag_distribution' in viz_data:
                st.subheader("📈 Tag Distribution")
                if viz_data['tag_distribution'].startswith('<'):
                    st.components.v1.html(viz_data['tag_distribution'], height=500)
                else:
                    st.write(viz_data['tag_distribution'])
            
            # Display year distribution
            if 'paper_timeline' in viz_data:
                st.subheader("📅 Publication Timeline")
                if viz_data['paper_timeline'].startswith('<'):
                    st.components.v1.html(viz_data['paper_timeline'], height=500)
                else:
                    st.write(viz_data['paper_timeline'])
    
    def display_analysis_tools(self, papers: List[Dict]):
        """Display analysis tools and summary statistics."""
        if not papers:
            return
        
        # Summary statistics
        st.subheader("📊 Summary Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Papers", len(papers))
        
        with col2:
            # Count unique tags
            all_tags = set()
            for paper in papers:
                all_tags.update(paper.get('tags', []))
            st.metric("Unique Tags", len(all_tags))
        
        with col3:
            # Count papers with abstracts
            papers_with_abstracts = sum(1 for p in papers if p.get('abstract'))
            st.metric("Papers with Abstracts", papers_with_abstracts)
        
        # Year distribution
        st.subheader("📅 Publication Year Distribution")
        year_counts = {}
        for paper in papers:
            year = paper.get('year', 'Unknown')
            if year != 'Unknown':
                year_counts[year] = year_counts.get(year, 0) + 1
        
        if year_counts:
            import plotly.express as px
            
            years, counts = zip(*sorted(year_counts.items()))
            fig = px.bar(
                x=list(years),
                y=list(counts),
                title="Papers by Publication Year",
                labels={'x': 'Year', 'y': 'Number of Papers'}
            )
            
            fig.update_layout(
                plot_bgcolor='white',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Tag frequency analysis
        st.subheader("🏷️ Tag Frequency Analysis")
        tag_counts = {}
        for paper in papers:
            for tag in paper.get('tags', []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        if tag_counts:
            # Show top 20 tags
            sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Top 10 Tags:**")
                for tag, count in sorted_tags[:10]:
                    st.write(f"• {tag}: {count} papers")
            
            with col2:
                st.write("**Tags 11-20:**")
                for tag, count in sorted_tags[10:20]:
                    st.write(f"• {tag}: {count} papers")

    def create_paper_timeline_plotly(self, papers: List[Dict]):
        """Create a Plotly timeline visualization for papers."""
        if not papers:
            return None
        
        # Extract years and create timeline data
        year_counts = {}
        paper_details = []
        
        for paper in papers:
            year = paper.get('year', 'Unknown')
            if year and year != 'Unknown':
                try:
                    year_int = int(year)
                    year_counts[year_int] = year_counts.get(year_int, 0) + 1
                    paper_details.append({
                        'year': year_int,
                        'title': paper.get('title', 'Unknown'),
                        'authors': ', '.join(paper.get('authors', [])),
                        'journal': paper.get('journal', 'Unknown'),
                        'tags': paper.get('tags', []),
                        'id': paper.get('id', 'unknown')
                    })
                except ValueError:
                    continue
        
        if not year_counts:
            return None
        
        # Sort by year
        sorted_years = sorted(year_counts.items())
        years, counts = zip(*sorted_years)
        
        # Create timeline visualization
        import plotly.graph_objects as go
        
        fig = go.Figure()
        
        # Add bar chart for year distribution
        fig.add_trace(go.Bar(
            x=years,
            y=counts,
            name='Papers per Year',
            marker_color='#4ECDC4',
            text=counts,
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Papers: %{y}<extra></extra>'
        ))
        
        # Add scatter plot for individual papers with interactive features
        if paper_details:
            paper_years = [p['year'] for p in paper_details]
            paper_titles = [p['title'][:50] + '...' if len(p['title']) > 50 else p['title'] for p in paper_details]
            paper_authors = [p['authors'] for p in paper_details]
            paper_journals = [p['journal'] for p in paper_details]
            paper_tags = [', '.join(p['tags'][:5]) + '...' if len(p['tags']) > 5 else ', '.join(p['tags']) for p in paper_details]
            
            fig.add_trace(go.Scatter(
                x=paper_years,
                y=[1] * len(paper_years),  # Place all papers at y=1 for visibility
                mode='markers+text',
                name='Individual Papers',
                text=paper_titles,
                textposition='top center',
                textfont=dict(size=8),
                marker=dict(
                    size=10,
                    color='#FF6B6B',
                    symbol='circle',
                    line=dict(width=2, color='white')
                ),
                customdata=list(zip(paper_authors, paper_journals, paper_tags)),
                hovertemplate='<b>%{text}</b><br>Year: %{x}<br>Authors: %{customdata[0]}<br>Journal: %{customdata[1]}<br>Tags: %{customdata[2]}<extra></extra>'
            ))
        
        fig.update_layout(
            title={
                'text': 'Paper Timeline - Click on papers to see details',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            xaxis=dict(
                title='Publication Year',
                showgrid=True,
                gridcolor='lightgray'
            ),
            yaxis=dict(
                title='Number of Papers',
                showgrid=True,
                gridcolor='lightgray'
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=50, r=50, t=80, b=50),
            height=500,
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        return fig

def main():
    """Main Streamlit application."""
    
    # Initialize app
    app = StreamlitApp()
    
    # Header
    st.markdown('<h1 class="main-header">📚 Mnemonic Matrix</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">BibTeX Processing & Auto-tagging System</p>', unsafe_allow_html=True)
    
    # Initialize session state for papers
    if 'papers' not in st.session_state:
        st.session_state.papers = []
    
    # Sidebar
    st.sidebar.title("📋 Input Papers")
    
    # Input method selection
    input_method = st.sidebar.selectbox(
        "Choose input method:",
        ["📄 BibTeX Upload", "📝 JSON Input", "✏️ Manual Entry"]
    )
    
    if input_method == "📄 BibTeX Upload":
        # File upload
        uploaded_file = st.sidebar.file_uploader(
            "Choose a BibTeX file",
            type=['bib'],
            help="Upload a .bib file containing your papers"
        )
        
        # Text input as alternative
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Or paste BibTeX content:**")
        bibtex_content = st.sidebar.text_area(
            "Paste your BibTeX content here",
            height=200,
            help="Paste your BibTeX entries directly"
        )
        
        # Add to papers button
        add_bibtex_button = st.sidebar.button("📥 Add Papers", type="primary")
        
        if add_bibtex_button and (uploaded_file is not None or bibtex_content.strip()):
            with st.spinner("🔄 Adding papers..."):
                # Get content
                if uploaded_file is not None:
                    content = uploaded_file.getvalue().decode('utf-8')
                    st.success(f"📁 Added file: {uploaded_file.name}")
                else:
                    content = bibtex_content
                    st.success("📝 Added pasted content")
                
                # Process papers
                new_papers = app.process_bibtex_content(content)
                st.session_state.papers.extend(new_papers)
                st.success(f"✅ Added {len(new_papers)} papers to your collection!")
    
    elif input_method == "📝 JSON Input":
        st.sidebar.markdown("**Enter papers as JSON:**")
        json_content = st.sidebar.text_area(
            "Paste JSON papers here",
            height=300,
            help="Enter papers in JSON format. Example: [{'title': 'Paper Title', 'authors': ['Author Name'], 'year': '2023', 'journal': 'Journal Name'}]"
        )
        
        add_json_button = st.sidebar.button("📥 Add Papers", type="primary")
        
        if add_json_button and json_content.strip():
            with st.spinner("🔄 Adding papers..."):
                new_papers = app.process_json_papers(json_content)
                if new_papers:
                    st.session_state.papers.extend(new_papers)
                    st.success(f"✅ Added {len(new_papers)} papers to your collection!")
                else:
                    st.error("❌ No valid papers found in JSON content.")
    
    elif input_method == "✏️ Manual Entry":
        st.sidebar.markdown("**Manual paper entry:**")
        num_papers = st.sidebar.number_input("Number of papers to add:", min_value=1, max_value=50, value=5)
        
        manual_papers = []
        for i in range(num_papers):
            with st.sidebar.expander(f"Paper {i+1}"):
                title = st.text_input(f"Title {i+1}", key=f"title_{i}")
                authors = st.text_input(f"Authors (comma-separated) {i+1}", key=f"authors_{i}")
                year = st.text_input(f"Year {i+1}", key=f"year_{i}")
                journal = st.text_input(f"Journal/Conference {i+1}", key=f"journal_{i}")
                
                if title:
                    paper = {
                        'title': title,
                        'authors': [a.strip() for a in authors.split(',') if a.strip()] if authors else [],
                        'year': year or 'Unknown',
                        'journal': journal or 'Unknown',
                        'abstract': '',
                        'tags': []
                    }
                    manual_papers.append(paper)
        
        add_manual_button = st.sidebar.button("📥 Add Papers", type="primary")
        
        if add_manual_button and manual_papers:
            st.session_state.papers.extend(manual_papers)
            st.success(f"✅ Added {len(manual_papers)} papers to your collection!")
    
    # Processing section
    st.sidebar.markdown("---")
    st.sidebar.title("🚀 Process Papers")
    
    if st.session_state.papers:
        st.sidebar.markdown(f"**Papers in collection:** {len(st.session_state.papers)}")
        
        # Process button
        process_button = st.sidebar.button("🤖 Auto-tag Papers", type="primary")
        
        if process_button:
            with st.spinner("🔄 Auto-tagging papers..."):
                for paper in st.session_state.papers:
                    if not paper.get('tags'):  # Only tag if not already tagged
                        paper['tags'] = app.auto_tagger.predict_tags(
                            paper.get('title', ''),
                            paper.get('abstract', ''),
                            paper.get('keywords', [])
                        )
                st.success(f"✅ Auto-tagged {len(st.session_state.papers)} papers!")
        
        # Clear papers button
        if st.sidebar.button("🗑️ Clear All Papers"):
            st.session_state.papers = []
            st.success("🗑️ Cleared all papers!")
            st.rerun()
    
    # Main content area
    papers = st.session_state.papers
    
    if papers:
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            all_tags = []
            for paper in papers:
                all_tags.extend(paper.get('tags', []))
            
            unique_tags = len(set(all_tags))
            avg_tags = len(all_tags) / len(papers) if papers else 0
            
            with col1:
                st.metric("📄 Total Papers", len(papers))
            with col2:
                st.metric("🏷️ Unique Tags", unique_tags)
            with col3:
                st.metric("📊 Avg Tags/Paper", f"{avg_tags:.1f}")
            with col4:
                st.metric("📈 Total Tags", len(all_tags))
            
            # Tabs for different views
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📊 Visualizations", 
                "📋 Papers List", 
                "🏷️ Tag Analysis", 
                "📈 Timeline",
                "💾 Export"
            ])
            
            with tab1:
                app.display_visualizations(papers)
            
            with tab2:
                st.header("📋 Papers Overview")
                
                for i, paper in enumerate(papers):
                    with st.expander(f"📄 {paper.get('title', 'Unknown Title')}"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"**Authors:** {', '.join(paper.get('authors', []))}")
                            st.markdown(f"**Journal/Conference:** {paper.get('journal', 'Unknown')}")
                            st.markdown(f"**Year:** {paper.get('year', 'Unknown')}")
                            if paper.get('abstract'):
                                st.markdown(f"**Abstract:** {paper.get('abstract', '')[:200]}...")
                        
                        with col2:
                            tags = paper.get('tags', [])
                            if tags:
                                st.markdown("**Auto-generated Tags:**")
                                for tag in tags:
                                    st.markdown(f'<span class="tag">{tag}</span>', unsafe_allow_html=True)
                            else:
                                st.markdown("**Tags:** *Not yet processed*")
            
            with tab3:
                st.header("🏷️ Tag Analysis")
                
                if all_tags:
                    # Tag statistics
                    tag_counts = Counter(all_tags)
                    top_tags = tag_counts.most_common(10)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Top 10 Tags")
                        for tag, count in top_tags:
                            st.markdown(f"**{tag}:** {count} papers")
                    
                    with col2:
                        st.subheader("Tag Categories")
                        categories = {
                            'Memory Studies': sum(1 for tag in all_tags if 'memory' in tag),
                            'Sociology': sum(1 for tag in all_tags if 'sociology' in tag),
                            'Political Science': sum(1 for tag in all_tags if 'political' in tag),
                            'History': sum(1 for tag in all_tags if 'history' in tag),
                            'Psychology': sum(1 for tag in all_tags if 'psychology' in tag),
                            'Philosophy': sum(1 for tag in all_tags if 'philosophy' in tag),
                        }
                        
                        for category, count in categories.items():
                            if count > 0:
                                st.markdown(f"**{category}:** {count} papers")
                else:
                    st.info("📝 No tags yet. Click 'Auto-tag Papers' to generate tags.")
            
            with tab4:
                st.header("📈 Publication Timeline")
                
                timeline_fig = app.create_paper_timeline_plotly(papers)
                if timeline_fig:
                    st.plotly_chart(timeline_fig, use_container_width=True)
                
                # Year distribution
                year_counts = Counter()
                for paper in papers:
                    year = paper.get('year', 'Unknown')
                    if year and year.isdigit():
                        year_counts[int(year)] += 1
                
                if year_counts:
                    st.subheader("Papers by Year")
                    for year, count in sorted(year_counts.items()):
                        st.markdown(f"**{year}:** {count} papers")
            
            with tab5:
                st.header("💾 Export Options")
                
                col1, col2 = st.columns(2)
            
            # Create JSON for download
            results_json = {
                "papers": papers,
                "statistics": {
                    "total_papers": len(papers),
                    "unique_tags": unique_tags,
                    "total_tags": len(all_tags),
                    "avg_tags_per_paper": avg_tags,
                    "processed_at": datetime.now().isoformat()
                }
            }
            
            st.download_button(
                label="📥 Download Results (JSON)",
                data=json.dumps(results_json, indent=2),
                file_name="processed_papers.json",
                mime="application/json"
            )
            
            with col2:
                st.subheader("📚 Export to Zotero")
                # Create Zotero-compatible BibTeX
                zotero_bibtex = app.create_zotero_export(papers)
                
                st.download_button(
                    label="📚 Download BibTeX for Zotero",
                    data=zotero_bibtex,
                    file_name="papers_for_zotero.bib",
                    mime="text/plain"
                )
                
                st.markdown("**Instructions for Zotero import:**")
                st.markdown("""
                1. Download the BibTeX file above
                2. Open Zotero
                3. Go to File → Import
                4. Select the downloaded .bib file
                5. Your papers will be imported with auto-generated tags as keywords
                """)
    
    else:
        # Welcome screen
        st.markdown("""
        ## 🎯 Welcome to Mnemonic Matrix
        
        This application automatically tags papers using ML and exports them for Zotero import.
        
        ### 📋 How to use:
        1. **Add papers** using any input method in the sidebar
        2. **Click "Auto-tag Papers"** to generate ML tags
        3. **View results** in the different tabs
        4. **Export to Zotero** using the "Export" tab
        
        ### 📊 What you'll get:
        - **ML-powered auto-tagging** of papers based on content
        - **Flexible paper input** (BibTeX, JSON, or manual entry)
        - **Interactive visualizations** showing tag relationships
        - **Zotero-compatible export** for easy import
        - **Statistical analysis** of your paper collection
        
        ### 📝 Supported input formats:
        - **BibTeX:** Standard .bib files
        - **JSON:** Array of paper objects with title, authors, year, journal
        - **Manual:** Form-based entry for individual papers
        
        ### 🤖 ML Auto-tagging:
        - Automatically analyzes paper titles, abstracts, and content
        - Generates relevant tags using machine learning
        - Covers academic fields, research methods, and topics
        - Tags are exported as keywords for Zotero
        """)
        
        # Example JSON
        with st.expander("📖 Example JSON Format"):
            st.code("""
[
  {
    "title": "Machine Learning Applications in Healthcare",
    "authors": ["Smith, John", "Johnson, Mary"],
    "year": "2023",
    "journal": "Journal of Medical AI"
  },
  {
    "title": "Data Science in Education",
    "authors": ["Brown, Alice"],
    "year": "2022",
    "journal": "Educational Technology"
  }
]
            """, language="json")

if __name__ == "__main__":
    main()