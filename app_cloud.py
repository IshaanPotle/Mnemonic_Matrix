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
import pandas as pd

# Import our modules
from bibtex_processor import BibTeXProcessor
from bibtex_matrix_tagger import BibTeXMatrixTagger
from visualizer import Visualizer

# Page configuration - Simple and clean
st.set_page_config(
    page_title="Mnemonic Matrix - BibTeX Processor",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark Theme CSS
st.markdown("""
<style>
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Dark theme base colors */
    :root {
        --primary-color: #1f1f1f;
        --secondary-color: #2d2d2d;
        --accent-color: #4a9eff;
        --text-color: #ffffff;
        --text-secondary: #b0b0b0;
        --border-color: #404040;
        --success-color: #00d4aa;
        --warning-color: #ffb347;
        --error-color: #ff6b6b;
    }
    
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        color: var(--text-color);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        visibility: visible !important;
        background: linear-gradient(180deg, #1f1f1f 0%, #2d2d2d 100%) !important;
        border-right: 2px solid var(--border-color) !important;
        width: 300px !important;
        display: block !important;
    }
    
    .css-1lcbmhc {
        visibility: visible !important;
        background: transparent !important;
        display: block !important;
        width: 300px !important;
    }
    
    /* Sidebar text */
    .css-1lcbmhc .stMarkdown {
        color: var(--text-color) !important;
    }
    
    /* Main content area */
    .main .block-container {
        max-width: none !important;
        padding: 2rem !important;
        background: transparent !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-color) !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Text elements */
    .stMarkdown {
        color: var(--text-color) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(45deg, var(--accent-color), #6bb6ff) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 8px rgba(74, 158, 255, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(74, 158, 255, 0.4) !important;
    }
    
    /* File uploader */
    .stFileUploader {
        background: var(--secondary-color) !important;
        border: 2px dashed var(--border-color) !important;
        border-radius: 12px !important;
        padding: 2rem !important;
    }
    
    /* Expanders */
    .streamlit-expander {
        background: var(--secondary-color) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        margin: 0.5rem 0 !important;
    }
    
    .streamlit-expanderHeader {
        background: var(--secondary-color) !important;
        color: var(--text-color) !important;
        border-radius: 8px 8px 0 0 !important;
    }
    
    /* Info boxes */
    .stAlert {
        background: var(--secondary-color) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        color: var(--text-color) !important;
    }
    
    /* Success alerts */
    .stAlert[data-testid="alert-success"] {
        background: rgba(0, 212, 170, 0.1) !important;
        border-color: var(--success-color) !important;
        color: var(--success-color) !important;
    }
    
    /* Warning alerts */
    .stAlert[data-testid="alert-warning"] {
        background: rgba(255, 179, 71, 0.1) !important;
        border-color: var(--warning-color) !important;
        color: var(--warning-color) !important;
    }
    
    /* Error alerts */
    .stAlert[data-testid="alert-error"] {
        background: rgba(255, 107, 107, 0.1) !important;
        border-color: var(--error-color) !important;
        color: var(--error-color) !important;
    }
    
    /* Info alerts */
    .stAlert[data-testid="alert-info"] {
        background: rgba(74, 158, 255, 0.1) !important;
        border-color: var(--accent-color) !important;
        color: var(--accent-color) !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--secondary-color) !important;
        border-radius: 8px !important;
        padding: 0.5rem !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--text-secondary) !important;
        border-radius: 6px !important;
        margin: 0 0.25rem !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--accent-color) !important;
        color: white !important;
    }
    
    /* Columns */
    .stHorizontalBlock {width: 100% !important;}
    .stVerticalBlock {width: 100% !important;}
    .stHtml {width: 100% !important; max-width: none !important;}
    .row-widget.stHorizontal {width: 100% !important;}
    
    /* Plotly charts dark theme */
    .js-plotly-plot {
        background: transparent !important;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--secondary-color);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--accent-color);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #6bb6ff;
    }
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
        """Display lightweight but interactive visualizations for the papers."""
        st.header("📊 Visualizations")
        
        if not papers:
            st.warning("No papers to visualize.")
            return
        
        try:
            # Interactive Tag Network (Proper Network Graph)
            st.subheader("🏷️ Interactive Tag Network")
            st.markdown("---")
            
            # Create proper network graph
            all_tags = []
            for paper in papers:
                all_tags.extend(paper.get('tags', []))
            
            if all_tags:
                tag_counts = Counter(all_tags)
                
                # Create network data
                nodes = []
                edges = []
                node_positions = {}
                
                # Define tag categories and colors (dark theme optimized)
                category_colors = {
                    'T': '#FF6B9D',  # Time - Bright Pink
                    'D': '#4ECDC4',  # Discipline - Cyan
                    'MC': '#4A9EFF', # Memory Carrier - Blue
                    'CT': '#00D4AA'  # Concept Tags - Teal
                }
                
                # Create nodes with proper positioning and better sizing
                import math
                node_radius = 2.5
                max_freq = max(tag_counts.values()) if tag_counts else 1
                min_freq = min(tag_counts.values()) if tag_counts else 1
                
                for i, (tag, count) in enumerate(tag_counts.items()):
                    # Determine category and color
                    if tag.startswith('T'):
                        category = 'T'
                        color = category_colors['T']
                    elif tag.startswith('D'):
                        category = 'D'
                        color = category_colors['D']
                    elif tag.startswith('MC'):
                        category = 'MC'
                        color = category_colors['MC']
                    elif tag.startswith('CT'):
                        category = 'CT'
                        color = category_colors['CT']
                    else:
                        category = 'Other'
                        color = '#95A5A6'
                    
                    # Position nodes in a circle with some randomization for better spread
                    angle = 2 * math.pi * i / len(tag_counts)
                    # Add slight randomization to prevent perfect circle overlap
                    random_offset = (hash(tag) % 100) / 1000  # Small random offset
                    x = (node_radius + random_offset) * math.cos(angle)
                    y = (node_radius + random_offset) * math.sin(angle)
                    
                    node_positions[tag] = (x, y)
                    
                    # Better size calculation based on frequency
                    # Scale between 15 and 60 pixels based on relative frequency
                    size = 15 + (count - min_freq) / (max_freq - min_freq) * 45 if max_freq > min_freq else 30
                    
                    nodes.append({
                        'id': tag,
                        'label': tag,
                        'size': size,
                        'color': color,
                        'category': category,
                        'x': x,
                        'y': y,
                        'frequency': count
                    })
                
                # Create edges between co-occurring tags
                tag_cooccurrence = {}
                for paper in papers:
                    paper_tags = paper.get('tags', [])
                    for i, tag1 in enumerate(paper_tags):
                        for j, tag2 in enumerate(paper_tags):
                            if i != j:
                                pair = tuple(sorted([tag1, tag2]))
                                tag_cooccurrence[pair] = tag_cooccurrence.get(pair, 0) + 1
                
                # Add edges for co-occurring tags with better filtering
                max_weight = max(tag_cooccurrence.values()) if tag_cooccurrence else 1
                for (tag1, tag2), weight in tag_cooccurrence.items():
                    # Show edges for tags that co-occur, with lower threshold to show more connections
                    min_threshold = 1  # Show all co-occurrences, even if just once
                    if weight >= min_threshold:
                        edges.append({
                            'source': tag1,
                            'target': tag2,
                            'weight': weight
                        })
                
                # Create the network visualization
                fig = go.Figure()
                
                # Add edges with better styling
                for edge in edges:
                    if edge['source'] in node_positions and edge['target'] in node_positions:
                        x0, y0 = node_positions[edge['source']]
                        x1, y1 = node_positions[edge['target']]
                        
                        # Calculate edge width based on weight
                        max_edge_weight = max([e['weight'] for e in edges]) if edges else 1
                        edge_width = max(1, min(8, edge['weight'] / max_edge_weight * 8))
                        
                        # Calculate edge opacity based on weight
                        edge_opacity = max(0.3, min(0.8, edge['weight'] / max_edge_weight))
                        
                        fig.add_trace(go.Scatter(
                            x=[x0, x1, None],
                            y=[y0, y1, None],
                            mode='lines',
                            line=dict(
                                width=edge_width, 
                                color=f'rgba(74, 158, 255, {edge_opacity})',
                                dash='solid'
                            ),
                            hoverinfo='text',
                            hovertext=f"Co-occurrence: {edge['weight']} times",
                            showlegend=False,
                            name=f"{edge['source']}-{edge['target']}"
                        ))
                
                # Add nodes with enhanced styling and click functionality
                for node in nodes:
                    # Calculate text size based on node size
                    text_size = max(8, min(14, node['size'] * 0.3))
                    
                    fig.add_trace(go.Scatter(
                        x=[node['x']],
                        y=[node['y']],
                        mode='markers+text',
                        marker=dict(
                            size=node['size'],
                            color=node['color'],
                            line=dict(width=3, color='white'),
                            opacity=0.9,
                            symbol='circle'
                        ),
                        text=[node['label']],
                        textposition="middle center",
                        textfont=dict(
                            size=text_size, 
                            color='white',
                            family="Arial Black"
                        ),
                        name=node['category'],
                        hovertemplate=f"<b>{node['label']}</b><br>" +
                                    f"Frequency: {node['frequency']}<br>" +
                                    f"Category: {node['category']}<br>" +
                                    f"Size: {node['size']:.0f}px<br>" +
                                    f"<i>Click to highlight connections</i><extra></extra>",
                        showlegend=False,
                        customdata=[node['frequency'], node['category'], node['id']]
                    ))
                
                # Update layout with dark theme and interactive features
                fig.update_layout(
                    title=dict(
                        text="Tag Co-occurrence Network - Click nodes to highlight connections",
                        font=dict(color='white', size=20),
                        x=0.5,
                        xanchor='center'
                    ),
                    xaxis=dict(
                        showgrid=False, 
                        zeroline=False, 
                        showticklabels=False,
                        color='white',
                        range=[-3.5, 3.5]  # Fixed range for better layout
                    ),
                    yaxis=dict(
                        showgrid=False, 
                        zeroline=False, 
                        showticklabels=False,
                        color='white',
                        range=[-3.5, 3.5]  # Fixed range for better layout
                    ),
                    height=700,
                    showlegend=True,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=50, r=50, t=100, b=50),
                    font=dict(color='white'),
                    hovermode='closest',
                    clickmode='event+select'
                )
                
                # Add enhanced legend with statistics
                legend_items = []
                for category, color in category_colors.items():
                    count = sum(1 for node in nodes if node['category'] == category)
                    if count > 0:  # Only show categories that exist
                        legend_items.append(f"<span style='color:{color}'>●</span> {category} ({count})")
                
                # Add statistics
                total_nodes = len(nodes)
                total_edges = len(edges)
                avg_connections = total_edges / total_nodes if total_nodes > 0 else 0
                
                legend_text = f"<b>Tag Categories:</b><br>" + "<br>".join(legend_items) + \
                            f"<br><br><b>Statistics:</b><br>" + \
                            f"Total Tags: {total_nodes}<br>" + \
                            f"Connections: {total_edges}<br>" + \
                            f"Avg. Connections: {avg_connections:.1f}"
                
                fig.add_annotation(
                    x=0.02, y=0.98,
                    xref="paper", yref="paper",
                    text=legend_text,
                    showarrow=False,
                    font=dict(size=11, color='white'),
                    bgcolor="rgba(45, 45, 45, 0.95)",
                    bordercolor="#4A9EFF",
                    borderwidth=2,
                    align="left"
                )
                
                # Add instructions
                fig.add_annotation(
                    x=0.98, y=0.02,
                    xref="paper", yref="paper",
                    text="<b>💡 Tips:</b><br>• Hover for details<br>• Click to select<br>• Drag to pan<br>• Scroll to zoom",
                    showarrow=False,
                    font=dict(size=10, color='white'),
                    bgcolor="rgba(45, 45, 45, 0.8)",
                    bordercolor="#4A9EFF",
                    borderwidth=1,
                    align="right"
                )
                
                # Display the chart with click functionality
                st.plotly_chart(fig, use_container_width=True, key="network_graph")
                
                # Add click-to-highlight functionality using Plotly's built-in features
                st.markdown("""
                <div id="network-highlight-info" style="
                    background: rgba(45, 45, 45, 0.9);
                    border: 2px solid #4A9EFF;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 10px 0;
                    color: white;
                    font-family: Arial, sans-serif;
                ">
                    <h4 style="margin: 0 0 10px 0; color: #4A9EFF;">🎯 Click-to-Highlight Instructions</h4>
                    <p style="margin: 5px 0;">• <strong>Click any node</strong> to highlight ONLY its direct connections</p>
                    <p style="margin: 5px 0;">• <strong>Connected nodes</strong> will be bright and larger</p>
                    <p style="margin: 5px 0;">• <strong>ALL other nodes</strong> will be dimmed and smaller</p>
                    <p style="margin: 5px 0;">• <strong>ALL other edges</strong> will be nearly invisible</p>
                    <p style="margin: 5px 0;">• <strong>Click again</strong> to reset the view</p>
                </div>
                
                <script>
                // Enhanced click-to-highlight functionality
                function setupNetworkHighlighting() {
                    // Wait for Plotly to be ready
                    if (typeof Plotly === 'undefined') {
                        setTimeout(setupNetworkHighlighting, 100);
                        return;
                    }
                    
                    // Get the plot element
                    var plotElement = document.querySelector('.js-plotly-plot .plotly');
                    if (!plotElement) {
                        setTimeout(setupNetworkHighlighting, 100);
                        return;
                    }
                    
                    // Store original data for reset functionality
                    var originalData = null;
                    var isHighlighted = false;
                    
                    // Function to reset all nodes to original state
                    function resetHighlight() {
                        if (originalData) {
                            Plotly.restyle(plotElement, {
                                'marker.opacity': [0.9],
                                'marker.size': originalData.marker.size,
                                'line.width': [1]
                            });
                            isHighlighted = false;
                        }
                    }
                    
                    // Function to highlight connections
                    function highlightConnections(clickedNodeId) {
                        if (isHighlighted) {
                            resetHighlight();
                            return;
                        }
                        
                        // Store original data
                        if (!originalData) {
                            var data = plotElement.data;
                            originalData = {
                                marker: {
                                    size: data[0].marker.size,
                                    opacity: data[0].marker.opacity
                                }
                            };
                        }
                        
                        // Find connected nodes
                        var connectedNodes = new Set();
                        var connectedEdges = new Set();
                        var nodeTraces = [];
                        var edgeTraces = [];
                        
                        // Separate node and edge traces
                        plotElement.data.forEach((trace, index) => {
                            if (trace.mode && trace.mode.includes('markers')) {
                                nodeTraces.push({trace: trace, index: index});
                            } else if (trace.mode && trace.mode.includes('lines')) {
                                edgeTraces.push({trace: trace, index: index});
                            }
                        });
                        
                        // Find connected nodes through edges
                        edgeTraces.forEach(edgeTrace => {
                            var traceName = edgeTrace.trace.name;
                            if (traceName && traceName.includes(clickedNodeId)) {
                                var parts = traceName.split('-');
                                if (parts.length >= 2) {
                                    connectedNodes.add(parts[0]);
                                    connectedNodes.add(parts[1]);
                                    connectedEdges.add(edgeTrace.index);
                                }
                            }
                        });
                        
                        // Add the clicked node itself
                        connectedNodes.add(clickedNodeId);
                        
                        // Update ALL node opacities and sizes
                        nodeTraces.forEach(nodeTrace => {
                            var nodeId = nodeTrace.trace.customdata ? nodeTrace.trace.customdata[2] : null;
                            if (nodeId && connectedNodes.has(nodeId)) {
                                // Highlight connected nodes (clicked node + its direct connections)
                                Plotly.restyle(plotElement, {
                                    'marker.opacity': [1.0],
                                    'marker.size': [nodeTrace.trace.marker.size * 1.3]
                                }, [nodeTrace.index]);
                            } else {
                                // Dim ALL other nodes (not connected to clicked node)
                                Plotly.restyle(plotElement, {
                                    'marker.opacity': [0.15],
                                    'marker.size': [nodeTrace.trace.marker.size * 0.7]
                                }, [nodeTrace.index]);
                            }
                        });
                        
                        // Update ALL edge opacities
                        edgeTraces.forEach(edgeTrace => {
                            if (connectedEdges.has(edgeTrace.index)) {
                                // Highlight ONLY edges connected to the clicked node
                                Plotly.restyle(plotElement, {
                                    'line.width': [4],
                                    'opacity': [1.0]
                                }, [edgeTrace.index]);
                            } else {
                                // Dim ALL other edges (not connected to clicked node)
                                Plotly.restyle(plotElement, {
                                    'line.width': [1],
                                    'opacity': [0.05]
                                }, [edgeTrace.index]);
                            }
                        });
                        
                        isHighlighted = true;
                    }
                    
                    // Add click event listener
                    plotElement.on('plotly_click', function(data) {
                        if (data.points && data.points.length > 0) {
                            var clickedPoint = data.points[0];
                            var nodeId = clickedPoint.customdata ? clickedPoint.customdata[2] : null;
                            
                            if (nodeId) {
                                highlightConnections(nodeId);
                            }
                        }
                    });
                    
                    // Add double-click to reset
                    plotElement.on('plotly_doubleclick', function() {
                        resetHighlight();
                    });
                }
                
                // Initialize when page loads
                document.addEventListener('DOMContentLoaded', setupNetworkHighlighting);
                
                // Re-initialize when Streamlit reruns
                if (window.parent !== window) {
                    window.parent.addEventListener('load', setupNetworkHighlighting);
                }
                </script>
                """, unsafe_allow_html=True)
                
                # Debug information
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🔗 Total Edges", len(edges))
                with col2:
                    st.metric("📊 Total Nodes", len(nodes))
                with col3:
                    st.metric("📈 Co-occurrences", len(tag_cooccurrence))
                
                st.info("💡 **Interactive:** Click on any node to highlight its connections! Hover for details.")
            else:
                st.info("No tags found in papers.")
            
            st.markdown("---")
            
            # Interactive Tag Distribution
            st.subheader("📈 Interactive Tag Distribution")
            
            if all_tags:
                tag_counts = Counter(all_tags)
                fig = px.bar(
                    x=list(tag_counts.keys()),
                    y=list(tag_counts.values()),
                    title="Tag Frequency Distribution",
                    labels={'x': 'Tags', 'y': 'Frequency'},
                    color=list(tag_counts.values()),
                    color_continuous_scale='viridis'
                )
                fig.update_layout(
                    title=dict(font=dict(color='white', size=18)),
                    xaxis=dict(
                        tickangle=-45,
                        color='white',
                        gridcolor='rgba(255,255,255,0.1)'
                    ),
                    yaxis=dict(
                        color='white',
                        gridcolor='rgba(255,255,255,0.1)'
                    ),
                    height=500,
                    margin=dict(l=50, r=50, t=80, b=80),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig, use_container_width=True)
                st.info("💡 **Interactive:** Hover over bars to see exact values, zoom and pan")
            else:
                st.info("No tags to display.")
            
            st.markdown("---")
            
            # Interactive Timeline
            st.subheader("📅 Interactive Publication Timeline")
            
            papers_with_years = []
            for paper in papers:
                year = paper.get('year')
                if year and str(year).isdigit():
                    try:
                        papers_with_years.append({
                            'title': paper.get('title', ''),
                            'year': int(year),
                            'tags': len(paper.get('tags', [])),
                            'journal': paper.get('journal', 'Unknown')
                        })
                    except ValueError:
                        continue
            
            if papers_with_years:
                papers_with_years.sort(key=lambda x: x['year'])
                
                # Create DataFrame for proper hover_data support
                df = pd.DataFrame(papers_with_years)
                
                fig = px.scatter(
                    df,
                    x='year',
                    y='tags',
                    size='tags',
                    color='journal',
                    hover_data=['title'],
                    title="Papers by Publication Year and Tag Count",
                    labels={'year': 'Publication Year', 'tags': 'Number of Tags', 'journal': 'Journal'}
                )
                fig.update_layout(
                    title=dict(font=dict(color='white', size=18)),
                    xaxis=dict(
                        color='white',
                        gridcolor='rgba(255,255,255,0.1)'
                    ),
                    yaxis=dict(
                        color='white',
                        gridcolor='rgba(255,255,255,0.1)'
                    ),
                    height=500,
                    margin=dict(l=50, r=50, t=80, b=80),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig, use_container_width=True)
                st.info("💡 **Interactive:** Hover for details, click and drag to zoom, double-click to reset")
            else:
                st.info("No papers with valid publication years found.")
            
            st.markdown("---")
            
            # Interactive Tag Categories
            st.subheader("📊 Interactive Tag Categories")
            
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
                        title="Tag Distribution by Category",
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig.update_layout(
                        height=500, 
                        margin=dict(l=50, r=50, t=80, b=80),
                        title=dict(font=dict(color='white', size=18)),
                        font=dict(color='white'),
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.info("💡 **Interactive:** Click on pie slices to highlight, hover for details")
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
        # Clean header
        st.title("🧠 Mnemonic Matrix")
        st.markdown("### Advanced BibTeX Processing with ML Auto-tagging")
        
        # Timeline restriction notice (simplified)
        st.info("🎯 Timeline tags are based on publication date only")
        
        st.markdown("---")
        
        # Main page input methods
        st.header("📥 Upload Papers")
        
        # Input method selection
        input_method = st.radio(
            "Choose input method:",
            ["📁 BibTeX Upload", "📋 JSON Input", "✏️ Manual Entry"],
            horizontal=True
        )
        
        if input_method == "📁 BibTeX Upload":
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
            json_input = st.text_area("Enter JSON data:", height=200)
            if st.button("Process JSON"):
                try:
                    papers = json.loads(json_input)
                    if isinstance(papers, list):
                        st.session_state.papers = papers
                        st.success(f"✅ Added {len(papers)} papers successfully!")
                    else:
                        st.error("❌ JSON must be a list of papers.")
                except json.JSONDecodeError:
                    st.error("❌ Invalid JSON format.")
        
        elif input_method == "✏️ Manual Entry":
            st.subheader("Add Paper Manually")
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Title")
                authors = st.text_input("Authors (comma-separated)")
            with col2:
                year = st.number_input("Year", min_value=1900, max_value=2030, value=2023)
                abstract = st.text_area("Abstract")
            
            if st.button("Add Paper"):
                if title and authors and year and abstract:
                    paper = {
                        "title": title,
                        "authors": [author.strip() for author in authors.split(",")],
                        "year": year,
                        "abstract": abstract
                    }
                    if "papers" not in st.session_state:
                        st.session_state.papers = []
                    st.session_state.papers.append(paper)
                    st.success("✅ Paper added successfully!")
                else:
                    st.error("❌ Please fill in all fields.")
        
        # Display current papers count and actions
        if "papers" in st.session_state and st.session_state.papers:
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Current Papers", len(st.session_state.papers))
            with col2:
                if st.button("🗑️ Clear All Papers"):
                    st.session_state.papers = []
                    st.rerun()
            with col3:
                if st.button("📥 Load Sample Data"):
                    sample_papers = self.get_sample_papers()
                    st.session_state.papers = sample_papers
                    st.success("✅ Sample data loaded!")
                    st.rerun()
        
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
            
            st.info("**Get started:** Use the upload section above to upload BibTeX files, paste JSON, or enter papers manually.")
            
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