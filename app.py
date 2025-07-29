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
            tagged_papers = []
            for paper in papers:
                # Get existing keywords from BibTeX
                existing_keywords = paper.get('keywords', [])
                
                # Predict tags using title, abstract, and existing keywords
                tags = self.auto_tagger.predict_tags(
                    paper.get('title', ''), 
                    paper.get('abstract', ''), 
                    existing_keywords
                )
                paper['tags'] = tags
                tagged_papers.append(paper)
            
            return tagged_papers
        except Exception as e:
            # Provide more helpful error messages
            if "encoding" in str(e).lower() or "decode" in str(e).lower():
                raise Exception(f"File encoding issue: {str(e)}. Please ensure your BibTeX file is saved in UTF-8 encoding.")
            else:
                raise Exception(f"Error processing BibTeX file: {str(e)}")
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file)
            except:
                pass
    
    def display_visualizations(self, papers: List[Dict]):
        """Display visualizations for the papers."""
        if not papers:
            st.warning("No papers to visualize. Please upload and process papers first.")
            return
        
        st.header("📊 Visualizations")
        
        # Store papers in session state to prevent recreation
        if 'processed_papers' not in st.session_state:
            st.session_state.processed_papers = papers
        
        # Create separate tabs for different functionality
        charts_tab, analysis_tab = st.tabs(["📊 Charts & Explorers", "📈 Analysis Tools"])
        
        # Tab 1: Charts and Explorers
        with charts_tab:
            st.subheader("📊 Interactive Charts & Explorers")
            
            # Create visualizations only once and store in session state
            if 'charts_html' not in st.session_state:
                with st.spinner("Creating visualizations..."):
                    visualizations = create_visualizations_cached(st.session_state.processed_papers)
                    st.session_state.charts_html = visualizations
            
            # Display cached visualizations first
            visualizations = st.session_state.charts_html
            
            if 'tag_network' in visualizations:
                st.subheader("🔗 Tag Network")
                st.components.v1.html(visualizations['tag_network'], height=600)
            
            if 'tag_distribution' in visualizations:
                st.subheader("📈 Tag Distribution")
                st.components.v1.html(visualizations['tag_distribution'], height=500)
            
            if 'paper_timeline' in visualizations:
                st.subheader("📅 Paper Timeline")
                st.components.v1.html(visualizations['paper_timeline'], height=500)
            
            # Add explorers below charts
            st.markdown("---")
            st.subheader("🔍 Interactive Explorers")
            
            # Simple tag explorer - just show all tags with their papers
            st.subheader("🏷️ Tag Explorer")
            
            # Build tag data
            tag_papers = {}
            for paper in papers:
                for tag in paper.get('tags', []):
                    if tag not in tag_papers:
                        tag_papers[tag] = []
                    tag_papers[tag].append(paper)
            
            if tag_papers:
                # Sort tags by frequency
                sorted_tags = sorted(tag_papers.items(), key=lambda x: len(x[1]), reverse=True)
                
                # Show top 10 tags with their papers
                for tag, papers_list in sorted_tags[:10]:
                    with st.expander(f"🏷️ {tag} ({len(papers_list)} papers)"):
                        for paper in papers_list:
                            st.write(f"• **{paper.get('title', 'Unknown')[:60]}...** ({paper.get('year', 'Unknown')})")
                            st.write(f"  Authors: {', '.join(paper.get('authors', []))}")
                            st.write(f"  Journal: {paper.get('journal', 'Unknown')}")
                            st.write("---")
            
            # Simple paper explorer - just show all papers with their details
            st.subheader("📄 Paper Explorer")
            
            for i, paper in enumerate(papers):
                with st.expander(f"📄 {paper.get('title', 'Unknown')[:60]}... ({paper.get('year', 'Unknown')})"):
                    st.write(f"**Title:** {paper.get('title', 'Unknown')}")
                    st.write(f"**Authors:** {', '.join(paper.get('authors', []))}")
                    st.write(f"**Year:** {paper.get('year', 'Unknown')}")
                    st.write(f"**Journal:** {paper.get('journal', 'Unknown')}")
                    
                    if paper.get('abstract'):
                        st.write(f"**Abstract:** {paper.get('abstract')[:200]}...")
                    
                    if paper.get('doi'):
                        st.write(f"**DOI:** {paper.get('doi')}")
                    
                    if paper.get('url'):
                        st.write(f"**URL:** [{paper.get('url')}]({paper.get('url')})")
                    
                    # Show tags
                    tags = paper.get('tags', [])
                    if tags:
                        st.write("**Tags:**")
                        for tag in tags:
                            st.write(f"• {tag}")
                    else:
                        st.write("**Tags:** None")
        
        # Tab 2: Analysis Tools
        with analysis_tab:
            st.subheader("📈 Analysis Tools")
            self.display_analysis_tools(st.session_state.processed_papers)
    
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
    
    # Sidebar
    st.sidebar.title("📋 Upload BibTeX")
    
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
    
    # Process button
    process_button = st.sidebar.button("🚀 Process Papers", type="primary")
    
    # Main content area
    if process_button and (uploaded_file is not None or bibtex_content.strip()):
        
        with st.spinner("🔄 Processing papers..."):
            
            # Get content
            if uploaded_file is not None:
                content = uploaded_file.getvalue().decode('utf-8')
                st.success(f"📁 Processed file: {uploaded_file.name}")
            else:
                content = bibtex_content
                st.success("📝 Processed pasted content")
            
            # Process papers
            papers = app.process_bibtex_content(content)
            
            if not papers:
                st.error("❌ No papers found in the BibTeX content. Please check the format.")
                return
            
            st.success(f"✅ Successfully processed {len(papers)} papers!")
            
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
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Visualizations", "📋 Papers List", "🏷️ Tag Analysis", "📈 Timeline"])
            
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
                            st.markdown("**Tags:**")
                            for tag in paper.get('tags', []):
                                st.markdown(f'<span class="tag">{tag}</span>', unsafe_allow_html=True)
            
            with tab3:
                st.header("🏷️ Tag Analysis")
                
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
                        'Machine Learning': sum(1 for tag in all_tags if 'machine_learning' in tag),
                        'Data Science': sum(1 for tag in all_tags if 'data_science' in tag),
                        'Computer Science': sum(1 for tag in all_tags if 'computer_science' in tag),
                        'Research Methods': sum(1 for tag in all_tags if 'research_methods' in tag),
                        'Technology': sum(1 for tag in all_tags if 'technology' in tag),
                        'Business': sum(1 for tag in all_tags if 'business' in tag),
                    }
                    
                    for category, count in categories.items():
                        if count > 0:
                            st.markdown(f"**{category}:** {count} papers")
            
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
            
            # Download results
            st.markdown("---")
            st.header("💾 Download Results")
            
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
    
    else:
        # Welcome screen
        st.markdown("""
        ## 🎯 Welcome to Mnemonic Matrix
        
        This application processes BibTeX files and automatically tags papers based on their content.
        
        ### 📋 How to use:
        1. **Upload a BibTeX file** (.bib format) using the sidebar, OR
        2. **Paste BibTeX content** directly into the text area
        3. **Click "Process Papers"** to start the analysis
        4. **Explore the results** in the different tabs
        
        ### 📊 What you'll get:
        - **Auto-tagged papers** with intelligent categorization
        - **Interactive visualizations** showing tag relationships
        - **Statistical analysis** of your paper collection
        - **Downloadable results** in JSON format
        
        ### 📝 Supported BibTeX fields:
        - `title`, `author`, `abstract`, `year`
        - `journal`, `booktitle`, `volume`, `pages`
        - `doi`, `url`, `keywords`
        
        ### 🏷️ Auto-tagging categories:
        - Machine Learning, Data Science, Computer Science
        - Research Methods, Academic Fields, Technology
        - Business, Healthcare, Education, and more
        """)
        
        # Example BibTeX
        with st.expander("📖 Example BibTeX Format"):
            st.code("""
@article{example,
  title={Machine Learning Applications in Healthcare},
  author={Smith, John and Johnson, Mary},
  journal={Journal of Medical AI},
  year={2023},
  abstract={This paper explores machine learning algorithms in healthcare...},
  keywords={machine learning, healthcare, deep learning}
}
            """, language="bibtex")

if __name__ == "__main__":
    main()