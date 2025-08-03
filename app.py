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
from bibtex_matrix_tagger import BibTeXMatrixTagger
from visualizer import Visualizer

# Page configuration - Hide default Streamlit elements
st.set_page_config(
    page_title="Mnemonic Matrix - BibTeX Processor",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Mnemonic Matrix - Advanced BibTeX Processing with ML Auto-tagging"
    }
)

# Hide default Streamlit elements and enhance aesthetics
st.markdown("""
<style>
    /* Hide default Streamlit header and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Hide Streamlit's default branding */
    .stDeployButton {display: none !important;}
    .stFloatingActionButton {display: none !important;}
    
    /* Hide Streamlit's default header */
    .stApp > header {display: none !important;}
    
    /* Remove any remaining Streamlit branding */
    .stApp > div:first-child {display: none !important;}
    
    /* Hide any remaining Streamlit floating elements */
    .stApp > div[data-testid="stFloatingActionButton"] {display: none !important;}
    .stApp > div[data-testid="stDeployButton"] {display: none !important;}
    
    /* Hide Streamlit's search icon */
    .stApp svg[data-testid="SearchIcon"] {display: none !important;}
    .stApp div[data-testid="stFloatingActionButton"] {display: none !important;}
    
    /* Hide ALL possible blue elements - extremely aggressive */
    svg[fill*="blue"], svg[stroke*="blue"], 
    svg[fill="#1f77b4"], svg[stroke="#1f77b4"],
    svg[fill="#0066cc"], svg[stroke="#0066cc"],
    svg[fill="#0000ff"], svg[stroke="#0000ff"],
    svg[fill="#0066ff"], svg[stroke="#0066ff"],
    svg[fill="#1e90ff"], svg[stroke="#1e90ff"],
    svg[fill="#4169e1"], svg[stroke="#4169e1"] {
        display: none !important;
    }
    
    /* Hide any element with blue in any form */
    *[style*="blue"] {display: none !important;}
    *[style*="#0000ff"] {display: none !important;}
    *[style*="#0066cc"] {display: none !important;}
    *[style*="#1f77b4"] {display: none !important;}
    *[style*="#0066ff"] {display: none !important;}
    *[style*="#1e90ff"] {display: none !important;}
    *[style*="#4169e1"] {display: none !important;}
    
    /* Hide any floating action buttons or search icons */
    div[data-testid*="Floating"], div[data-testid*="Search"],
    button[data-testid*="Floating"], button[data-testid*="Search"],
    svg[data-testid*="Search"], svg[data-testid*="Floating"] {
        display: none !important;
    }
    
    /* Hide any remaining Streamlit default elements */
    .stApp > div:not([data-testid="stAppViewContainer"]) {
        display: none !important;
    }
    
    /* Enhanced aesthetics - smooth transitions */
    * {
        transition: all 0.3s ease;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #1A1A1A;
    }
    ::-webkit-scrollbar-thumb {
        background: #666666;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #888888;
    }
    
    /* Dark theme base styles */
    .stApp {
        background-color: #0F0F0F !important;
        color: #E8E8E8 !important;
    }
    
    /* Streamlit elements dark theme */
    .stButton > button {
        background-color: #444444 !important;
        color: white !important;
        border: none !important;
        border-radius: 0.5rem !important;
        padding: 0.5rem 1rem !important;
        box-shadow: 0 2px 4px rgba(68, 68, 68, 0.3) !important;
    }
    
    .stButton > button:hover {
        background-color: #666666 !important;
        box-shadow: 0 4px 8px rgba(102, 102, 102, 0.4) !important;
    }
    
    /* Text areas and inputs */
    .stTextArea textarea, .stTextInput input {
        background-color: #1A1A1A !important;
        color: #E8E8E8 !important;
        border: 1px solid #444444 !important;
        border-radius: 0.5rem !important;
    }
    
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #666666 !important;
        box-shadow: 0 0 0 2px rgba(102, 102, 102, 0.2) !important;
    }
    
    /* Select boxes */
    .stSelectbox select {
        background-color: #1A1A1A !important;
        color: #E8E8E8 !important;
        border: 1px solid #444444 !important;
        border-radius: 0.5rem !important;
    }
    
    /* File uploader */
    .stFileUploader {
        background-color: #1A1A1A !important;
        border: 1px solid #444444 !important;
        border-radius: 0.5rem !important;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #1A1A1A !important;
    }
    
    /* Success messages */
    .stSuccess {
        background-color: #1A1A1A !important;
        color: #E8E8E8 !important;
        border: 1px solid #444444 !important;
    }
    
    /* Error messages */
    .stError {
        background-color: #1A1A1A !important;
        color: #E8E8E8 !important;
        border: 1px solid #444444 !important;
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
        self.matrix_tagger = BibTeXMatrixTagger()
        self.visualizer = Visualizer()
        
        # Create directories
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize matrix tagger with trained models
        self._initialize_matrix_tagger()
    
    def _initialize_matrix_tagger(self):
        """Initialize the matrix tagger with new comprehensive system."""
        try:
            # Try to load new models first
            self.matrix_tagger.load_models('matrix_tagger_models_new.pkl')
            print("✅ Loaded new comprehensive matrix tagger models")
        except FileNotFoundError:
            try:
                # Fallback to old models
                self.matrix_tagger.load_models('matrix_tagger_models.pkl')
                print("⚠️  Loaded old models (consider retraining for new system)")
            except FileNotFoundError:
                print("❌ No trained models found. Please run bibtex_matrix_tagger.py to train models.")
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
            for paper in papers:
                paper_text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
                matrix_tags = self.matrix_tagger.analyze_paper_for_prediction(paper_text)
                
                # Combine all matrix tags into a single list
                all_tags = []
                for category, tags in matrix_tags.items():
                    all_tags.extend(tags)
                
                paper['tags'] = all_tags
            
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
            
            # Format authors for Zotero
            authors = paper.get('authors', [])
            if isinstance(authors, list):
                author_str = " and ".join(authors)
            else:
                author_str = str(authors)
            
            # Get matrix tags for this paper using enhanced analysis
            paper_text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
            matrix_tags = self.matrix_tagger.analyze_paper_for_prediction(paper_text)
            
            # Combine all matrix tags into keywords
            all_matrix_tags = []
            for category, tags in matrix_tags.items():
                all_matrix_tags.extend(tags)
            
            # Add existing tags if any
            existing_tags = paper.get('tags', [])
            all_tags = all_matrix_tags + existing_tags
            
            # Create Zotero entry with matrix tags
            zotero_entry = f"""@article{{{key},
  title = {{{paper.get('title', 'Unknown Title')}}},
  author = {{{author_str}}},
  journal = {{{paper.get('journal', 'Unknown')}}},
  year = {{{paper.get('year', 'Unknown')}}},
  abstract = {{{paper.get('abstract', '')}}},
  keywords = {{{', '.join(all_tags)}}},
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
    
    # Simple header
    st.title("📚 Mnemonic Matrix")
    st.markdown("**Advanced BibTeX Processing & ML Auto-tagging System**")
    
    # Initialize session state for papers
    if 'papers' not in st.session_state:
        st.session_state.papers = []
    
    # Sidebar for input
    with st.sidebar:
        st.header("📋 Input Papers")
        st.markdown("Upload or enter your research papers")
        
        input_method = st.selectbox(
            "Choose input method:",
            ["📄 BibTeX Upload", "📝 JSON Input", "✏️ Manual Entry"]
        )
        
        if input_method == "📄 BibTeX Upload":
            st.subheader("📄 BibTeX Upload")
            
            # File upload
            uploaded_file = st.file_uploader(
                "Choose a BibTeX file",
                type=['bib'],
                help="Upload a .bib file containing your papers"
            )
            
            # Text input as alternative
            st.subheader("📝 Or paste BibTeX content")
            bibtex_content = st.text_area(
                "Paste BibTeX content here:",
                height=200,
                help="Paste your BibTeX content directly"
            )
            
            if st.button("Add Papers", type="primary"):
                if uploaded_file:
                    content = uploaded_file.read().decode('utf-8')
                    papers = app.process_bibtex_content(content)
                    st.session_state.papers.extend(papers)
                    st.success(f"Added {len(papers)} papers successfully!")
                elif bibtex_content:
                    papers = app.process_bibtex_content(bibtex_content)
                    st.session_state.papers.extend(papers)
                    st.success(f"Added {len(papers)} papers successfully!")
                else:
                    st.error("Please upload a file or paste BibTeX content.")
        
        elif input_method == "📝 JSON Input":
            st.subheader("📝 JSON Input")
            json_content = st.text_area(
                "Paste JSON papers array:",
                height=300,
                help="Paste JSON array of paper objects"
            )
            
            if st.button("Add Papers", type="primary"):
                if json_content:
                    papers = app.process_json_papers(json_content)
                    st.session_state.papers.extend(papers)
                    st.success(f"Added {len(papers)} papers successfully!")
                else:
                    st.error("Please paste JSON content.")
        
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
                    st.session_state.papers.append(paper)
                    st.success("Paper added successfully!")
                else:
                    st.error("Please enter at least a title.")
    
    # Main content area
    if st.session_state.papers:
        st.header("📊 Papers Analysis")
        
        # Display paper count
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Papers", len(st.session_state.papers))
        with col2:
            total_tags = sum(len(paper.get('tags', [])) for paper in st.session_state.papers)
            st.metric("Total Tags", total_tags)
        with col3:
            avg_tags = total_tags / len(st.session_state.papers) if st.session_state.papers else 0
            st.metric("Avg Tags/Paper", f"{avg_tags:.1f}")
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🤖 Auto-tag Papers", type="primary"):
                for paper in st.session_state.papers:
                    if not paper.get('tags'):
                        paper_text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
                        matrix_tags = app.matrix_tagger.analyze_paper_for_prediction(paper_text)
                        all_tags = []
                        for category, tags in matrix_tags.items():
                            all_tags.extend(tags)
                        paper['tags'] = all_tags
                st.success("Papers auto-tagged successfully!")
        
        with col2:
            if st.button("🗑️ Clear All Papers"):
                st.session_state.papers = []
                st.rerun()
        
        # Tabs for different views
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Visualizations", 
            "📋 Papers List", 
            "🏷️ Tag Analysis", 
            "📈 Timeline",
            "💾 Export"
        ])
        
        with tab1:
            st.subheader("📊 Visualizations")
            app.display_visualizations(st.session_state.papers)
        
        with tab2:
            st.subheader("📋 Papers List")
            for i, paper in enumerate(st.session_state.papers):
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
                                st.markdown(f'<span style="background: #666666; color: white; padding: 2px 6px; border-radius: 3px; margin: 1px; display: inline-block; font-size: 12px;">{tag}</span>', unsafe_allow_html=True)
                        else:
                            st.write("**Tags:** None")
        
        with tab3:
            st.subheader("🏷️ Tag Analysis")
            all_tags = []
            for paper in st.session_state.papers:
                all_tags.extend(paper.get('tags', []))
            
            if all_tags:
                tag_counts = Counter(all_tags)
                top_tags = tag_counts.most_common(10)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Top 10 Tags")
                    for tag, count in top_tags:
                        st.write(f"**{tag}:** {count} papers")
                
                with col2:
                    st.subheader("Tag Categories")
                    categories = {
                        'Memory Studies': sum(1 for tag in all_tags if 'memory' in tag.lower()),
                        'Sociology': sum(1 for tag in all_tags if 'sociology' in tag.lower()),
                        'Political Science': sum(1 for tag in all_tags if 'political' in tag.lower()),
                        'History': sum(1 for tag in all_tags if 'history' in tag.lower()),
                        'Psychology': sum(1 for tag in all_tags if 'psychology' in tag.lower()),
                        'Philosophy': sum(1 for tag in all_tags if 'philosophy' in tag.lower()),
                    }
                    
                    for category, count in categories.items():
                        if count > 0:
                            st.write(f"**{category}:** {count} papers")
            else:
                st.info("📝 No tags yet. Click 'Auto-tag Papers' to generate tags.")
        
        with tab4:
            st.subheader("📈 Publication Timeline")
            timeline_fig = app.create_paper_timeline_plotly(st.session_state.papers)
            if timeline_fig:
                st.plotly_chart(timeline_fig, use_container_width=True)
            
            # Year distribution
            year_counts = Counter()
            for paper in st.session_state.papers:
                year = paper.get('year', 'Unknown')
                if year and year.isdigit():
                    year_counts[int(year)] += 1
            
            if year_counts:
                st.subheader("Papers by Year")
                for year, count in sorted(year_counts.items()):
                    st.write(f"**{year}:** {count} papers")
        
        with tab5:
            st.subheader("💾 Export Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📚 Export to Zotero")
                if st.button("📥 Export to Zotero", type="primary"):
                    zotero_bibtex = app.create_zotero_export(st.session_state.papers)
                    st.download_button(
                        label="Download BibTeX file",
                        data=zotero_bibtex,
                        file_name="papers_with_matrix_tags.bib",
                        mime="text/plain"
                    )
                    st.info("Download the file and import it into Zotero!")
            
            with col2:
                st.subheader("📄 Export as JSON")
                papers_with_matrix_tags = []
                for paper in st.session_state.papers:
                    paper_text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
                    matrix_tags = app.matrix_tagger.analyze_paper_for_prediction(paper_text)
                    
                    paper_with_tags = paper.copy()
                    paper_with_tags['matrix_tags'] = matrix_tags
                    papers_with_matrix_tags.append(paper_with_tags)
                
                results_json = {
                    "papers": papers_with_matrix_tags,
                    "statistics": {
                        "total_papers": len(st.session_state.papers),
                        "unique_tags": len(set(all_tags)),
                        "total_tags": len(all_tags),
                        "avg_tags_per_paper": len(all_tags) / len(st.session_state.papers) if st.session_state.papers else 0,
                        "processed_at": datetime.now().isoformat()
                    }
                }
                
                st.download_button(
                    label="Download Results (JSON)",
                    data=json.dumps(results_json, indent=2),
                    file_name="processed_papers_with_matrix_tags.json",
                    mime="application/json"
                )
    
    else:
        # Welcome screen
        st.header("🎯 Welcome to Mnemonic Matrix")
        st.markdown("This application automatically tags papers using ML and exports them for Zotero import.")
        
        st.subheader("📋 How to use:")
        st.markdown("""
        1. **Add papers** using any input method in the sidebar
        2. **Click "Auto-tag Papers"** to generate ML tags
        3. **View results** in the papers list
        4. **Export to Zotero** using the export button
        """)
        
        st.subheader("📊 What you'll get:")
        st.markdown("""
        - **ML-powered auto-tagging** of papers based on content
        - **Flexible paper input** (BibTeX, JSON, or manual entry)
        - **Zotero-compatible export** for easy import
        - **Statistical analysis** of your paper collection
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