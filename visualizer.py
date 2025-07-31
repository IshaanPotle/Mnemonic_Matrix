#!/usr/bin/env python3
"""
Visualizer - Creates HTML visualizations for tagged papers
"""

import json
from typing import List, Dict
from pathlib import Path
from collections import Counter
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import numpy as np
from scipy.spatial.distance import pdist, squareform

class Visualizer:
    """Creates interactive HTML visualizations for paper data."""
    
    def __init__(self):
        self.colors = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
    
    def create_visualizations(self, papers: List[Dict]) -> Dict[str, str]:
        """Create all visualizations for the papers."""
        if not papers:
            return {"error": "No papers provided for visualization."}
        
        visualizations = {}
        
        # Create tag network
        try:
            network_html = self._create_tag_network(papers)
            visualizations['tag_network'] = network_html
        except Exception as e:
            visualizations['tag_network'] = f"<p>Error creating tag network: {str(e)}</p>"
        
        # Create tag distribution
        try:
            distribution_html = self._create_tag_distribution(papers)
            visualizations['tag_distribution'] = distribution_html
        except Exception as e:
            visualizations['tag_distribution'] = f"<p>Error creating tag distribution: {str(e)}</p>"
        
        # Create paper timeline
        try:
            timeline_html = self._create_paper_timeline(papers)
            visualizations['paper_timeline'] = timeline_html
        except Exception as e:
            visualizations['paper_timeline'] = f"<p>Error creating paper timeline: {str(e)}</p>"
        
        return visualizations
    
    def _create_tag_network(self, papers: List[Dict]) -> str:
        """Create an interactive tag network visualization with force-directed layout and clustering."""
        # Collect all tags and their frequencies
        tag_counts = {}
        paper_tag_connections = []
        
        for paper in papers:
            paper_id = paper.get('id', 'unknown')
            paper_title = paper.get('title', 'Unknown Title')
            
            for tag in paper.get('tags', []):
                if tag not in tag_counts:
                    tag_counts[tag] = 0
                tag_counts[tag] += 1
                paper_tag_connections.append((paper_id, tag, paper_title))
        
        # Filter tags by frequency to reduce clutter
        min_frequency = 1
        max_frequency = max(tag_counts.values()) if tag_counts else 1
        
        # Keep only tags that appear at least once, but limit to top tags for readability
        filtered_tags = {tag: count for tag, count in tag_counts.items() if count >= min_frequency}
        
        # Sort by frequency and take top tags for better visualization
        sorted_tags = sorted(filtered_tags.items(), key=lambda x: x[1], reverse=True)
        top_tags = sorted_tags[:40]  # Increased limit for better coverage
        
        if not top_tags:
            return "<p>No tags found in the papers.</p>"
        
        # Create nodes for tags with enhanced properties
        tag_nodes = []
        tag_to_index = {}
        
        for i, (tag, count) in enumerate(top_tags):
            # Calculate node size based on frequency with better scaling
            size = 12 + (count / max_frequency) * 35  # Larger base size and range
            
            # Calculate color based on frequency with modern color scheme
            color_value = count / max_frequency
            # Use a modern, vibrant color scheme for light theme
            if color_value > 0.7:
                color = '#e74c3c'  # Red for high frequency
            elif color_value > 0.4:
                color = '#3498db'  # Blue for medium frequency
            elif color_value > 0.2:
                color = '#2ecc71'  # Green for lower frequency
            else:
                color = '#f39c12'  # Orange for lowest frequency
            
            tag_nodes.append({
                'id': tag,
                'label': tag,
                'size': size,
                'color': color,
                'frequency': count,
                'index': i
            })
            tag_to_index[tag] = i
        
        # Create edges between tags that co-occur in the same papers
        edges = []
        tag_cooccurrence = {}
        
        for paper in papers:
            paper_tags = paper.get('tags', [])
            # Only consider tags that are in our filtered list
            paper_tags = [tag for tag in paper_tags if tag in dict(top_tags)]
            
            # Create connections between all tags in this paper
            for i, tag1 in enumerate(paper_tags):
                for tag2 in paper_tags[i+1:]:
                    edge_key = tuple(sorted([tag1, tag2]))
                    if edge_key not in tag_cooccurrence:
                        tag_cooccurrence[edge_key] = 0
                    tag_cooccurrence[edge_key] += 1
        
        # Create edges with weights based on co-occurrence
        # Sort by weight and take only the strongest connections to reduce clutter
        sorted_edges = sorted(tag_cooccurrence.items(), key=lambda x: x[1], reverse=True)
        max_edges = min(len(sorted_edges), 60)  # Limit number of edges for clarity
        
        for (tag1, tag2), weight in sorted_edges[:max_edges]:
            if weight >= 1:  # Only show edges with at least 1 co-occurrence
                edges.append({
                    'source': tag1,
                    'target': tag2,
                    'weight': weight,
                    'width': min(weight * 1.2, 5)  # Reduced width cap
                })
        
        # Generate force-directed layout positions
        import numpy as np
        from scipy.spatial.distance import pdist, squareform
        
        # Create adjacency matrix for layout calculation
        n_nodes = len(tag_nodes)
        adjacency_matrix = np.zeros((n_nodes, n_nodes))
        
        for edge in edges:
            source_idx = tag_to_index[edge['source']]
            target_idx = tag_to_index[edge['target']]
            adjacency_matrix[source_idx][target_idx] = edge['weight']
            adjacency_matrix[target_idx][source_idx] = edge['weight']
        
        # Enhanced force-directed layout simulation with better spacing
        positions = self._force_directed_layout(adjacency_matrix, n_iterations=150)
        
        # Create the network visualization with enhanced features
        fig = go.Figure()
        
        # Add edges with animated effects and better styling
        if edges:
            for edge in edges:
                source_idx = tag_to_index[edge['source']]
                target_idx = tag_to_index[edge['target']]
                
                source_pos = positions[source_idx]
                target_pos = positions[target_idx]
                
                # Create animated edge trace for this connection
                fig.add_trace(go.Scatter(
                    x=[source_pos[0], target_pos[0]],
                    y=[source_pos[1], target_pos[1]],
                    mode='lines',
                                    line=dict(
                    width=min(edge['width'] * 0.8, 4),  # Slightly thicker edges
                    color='rgba(52,73,94,0.4)',  # Dark blue-gray for light theme
                    shape='spline'
                ),
                    hoverinfo='text',
                    text=[f"<b>{edge['source']} ↔ {edge['target']}</b><br>Co-occurrence: {edge['weight']} papers"],
                    showlegend=False,
                    hoverlabel=dict(
                        bgcolor="rgba(255,255,255,0.95)", 
                        font_size=12, 
                        bordercolor="rgba(0,0,0,0.2)",
                        font_color="#2c3e50"
                    ),
                    name='Connections'
                ))
        
        # Add nodes with enhanced interactive features
        node_x = [positions[i][0] for i in range(n_nodes)]
        node_y = [positions[i][1] for i in range(n_nodes)]
        node_sizes = [node['size'] for node in tag_nodes]
        node_colors = [node['color'] for node in tag_nodes]
        node_labels = [node['label'] for node in tag_nodes]
        node_frequencies = [node['frequency'] for node in tag_nodes]
        
        # Create hover text with more information
        hover_texts = []
        for node in tag_nodes:
            # Find connected tags
            connected_tags = []
            for edge in edges:
                if edge['source'] == node['id']:
                    connected_tags.append(edge['target'])
                elif edge['target'] == node['id']:
                    connected_tags.append(edge['source'])
            
            connected_text = f"<br>Connected to: {', '.join(connected_tags[:5])}"
            if len(connected_tags) > 5:
                connected_text += f" (+{len(connected_tags)-5} more)"
            
            hover_texts.append(
                f"<b>{node['label']}</b><br>"
                f"Frequency: {node['frequency']} papers<br>"
                f"Connections: {len(connected_tags)} tags{connected_text}"
            )
        
        fig.add_trace(go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            marker=dict(
                size=node_sizes,
                color=node_colors,
                line=dict(width=2, color='rgba(255,255,255,0.9)'),
                opacity=0.95,
                symbol='circle',
                gradient=dict(
                    type="radial",
                    color=node_colors
                )
            ),
            text=node_labels,
            textposition="middle center",
            textfont=dict(size=11, color='white', family='Arial Black'),
            hoverinfo='text',
            hovertext=hover_texts,
            name='Tags',
            customdata=node_labels,  # Store tag names for click events
            hovertemplate='%{hovertext}<extra></extra>'
        ))
        
        # Add frequency legend with modern color scheme
        legend_items = [
            ('High Frequency (>70%)', '#e74c3c'),
            ('Medium Frequency (40-70%)', '#3498db'),
            ('Low Frequency (20-40%)', '#2ecc71'),
            ('Very Low Frequency (<20%)', '#f39c12')
        ]
        
        for label, color in legend_items:
            fig.add_trace(go.Scatter(
                x=[None], y=[None],
                mode='markers',
                marker=dict(size=10, color=color),
                name=label,
                showlegend=True
            ))
        
        # Update layout for modern light theme and enhanced interactivity
        fig.update_layout(
            title={
                'text': '🔗 Interactive Knowledge Network',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 26, 'color': '#2c3e50', 'family': 'Arial Black'}
            },
            xaxis=dict(
                showticklabels=False,
                showgrid=True,
                gridcolor='rgba(200,200,200,0.3)',
                zeroline=False,
                showline=False,
                range=[-600, 600]
            ),
            yaxis=dict(
                showticklabels=False,
                showgrid=True,
                gridcolor='rgba(200,200,200,0.3)',
                zeroline=False,
                showline=False,
                range=[-600, 600]
            ),
            plot_bgcolor='#f8f9fa',
            paper_bgcolor='#ffffff',
            margin=dict(l=50, r=50, t=120, b=50),
            height=900,
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.98,
                xanchor="left",
                x=0.02,
                bgcolor='rgba(255,255,255,0.95)',
                bordercolor='rgba(0,0,0,0.2)',
                borderwidth=1,
                font=dict(color='#2c3e50', size=12, family='Arial')
            ),
            # Enhanced interactivity
            clickmode='event+select',
            dragmode='pan',
            hovermode='closest',
            # Animation settings
            uirevision=True,
            # Add selection styling
            selectdirection='any'
        )
        
        # Add JavaScript for enhanced interactive features
        js_code = """
        <script>
        // Enhanced interactive features with dark theme
        let selectedNode = null;
        let highlightedEdges = [];
        
        function handleNodeClick(event) {
            const point = event.points[0];
            const tagName = point.data.customdata[point.pointIndex];
            
            // Highlight connected nodes
            highlightConnections(tagName);
            
            // Show detailed relationship information
            showRelationshipDetails(tagName);
            
            // Store selected node
            selectedNode = tagName;
        }
        
        function highlightConnections(tagName) {
            // Remove previous highlights
            clearHighlights();
            
            // Find and highlight connected nodes
            const plotDiv = document.querySelector('.plotly-graph-div');
            if (plotDiv && plotDiv._fullData) {
                const data = plotDiv._fullData;
                const nodeTrace = data.find(trace => trace.name === 'Tags');
                const edgeTraces = data.filter(trace => trace.name === 'Connections');
                
                if (nodeTrace) {
                    // Highlight connected nodes
                    const connectedNodes = [];
                    edgeTraces.forEach(edgeTrace => {
                        if (edgeTrace.text && edgeTrace.text[0] && edgeTrace.text[0].includes(tagName)) {
                            // This edge connects to our selected node
                            const connectedTag = edgeTrace.text[0].split(' ↔ ').find(tag => tag !== tagName);
                            if (connectedTag) {
                                connectedNodes.push(connectedTag);
                            }
                        }
                    });
                    
                    // Apply highlighting
                    highlightNodes(connectedNodes);
                }
            }
        }
        
        function highlightNodes(nodeNames) {
            const plotDiv = document.querySelector('.plotly-graph-div');
            if (plotDiv) {
                // Add glow effect to connected nodes
                const style = document.createElement('style');
                style.id = 'node-highlights';
                style.textContent = `
                    .js-plotly-plot .plotly .main-svg .trace:nth-child(2) .points path {
                        filter: drop-shadow(0 0 10px rgba(255,255,255,0.5));
                    }
                `;
                document.head.appendChild(style);
            }
        }
        
        function clearHighlights() {
            const existingStyle = document.getElementById('node-highlights');
            if (existingStyle) {
                existingStyle.remove();
            }
        }
        
        function showRelationshipDetails(tagName) {
            // Create an enhanced tooltip
            const tooltip = document.createElement('div');
            tooltip.innerHTML = `
                <div style="background: rgba(255,255,255,0.98); color: #2c3e50; padding: 18px; border-radius: 12px; 
                     border: 1px solid rgba(0,0,0,0.1); box-shadow: 0 8px 32px rgba(0,0,0,0.15); 
                     max-width: 320px; font-family: Arial, sans-serif; backdrop-filter: blur(10px);">
                    <h3 style="margin: 0 0 12px 0; color: #3498db; font-size: 18px;">${tagName}</h3>
                    <p style="margin: 8px 0; font-size: 14px; color: #34495e;">Click to explore connections</p>
                    <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(0,0,0,0.1);">
                        <small style="color: #7f8c8d;">Connected nodes will be highlighted</small>
                    </div>
                </div>
            `;
            tooltip.style.cssText = `
                position: absolute;
                z-index: 1000;
                pointer-events: none;
            `;
            document.body.appendChild(tooltip);
            
            setTimeout(() => {
                document.body.removeChild(tooltip);
            }, 4000);
        }
        
        // Add enhanced controls with modern light theme
        function addNetworkControls() {
            const controls = document.createElement('div');
            controls.innerHTML = `
                <div style="background: rgba(255,255,255,0.95); padding: 15px; border-radius: 12px; 
                     border: 1px solid rgba(0,0,0,0.1); box-shadow: 0 8px 32px rgba(0,0,0,0.1); 
                     backdrop-filter: blur(10px);">
                    <h4 style="margin: 0 0 15px 0; color: #2c3e50; font-size: 16px; font-family: Arial, sans-serif;">🎮 Network Controls</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                        <button onclick="resetZoom()" style="padding: 10px 14px; background: linear-gradient(45deg, #3498db, #2980b9); 
                                color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 12px; font-weight: bold; 
                                transition: all 0.3s ease;">🔍 Reset</button>
                        <button onclick="fitToView()" style="padding: 10px 14px; background: linear-gradient(45deg, #27ae60, #229954); 
                                color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 12px; font-weight: bold; 
                                transition: all 0.3s ease;">📐 Fit</button>
                        <button onclick="refreshNetwork()" style="padding: 10px 14px; background: linear-gradient(45deg, #e74c3c, #c0392b); 
                                color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 12px; font-weight: bold; 
                                transition: all 0.3s ease;">🔄 Refresh</button>
                        <button onclick="toggleAutoRefresh()" id="autoRefreshBtn" style="padding: 10px 14px; background: linear-gradient(45deg, #f39c12, #e67e22); 
                                color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 12px; font-weight: bold; 
                                transition: all 0.3s ease;">⏰ Auto</button>
                    </div>
                    <div style="margin-top: 12px; font-size: 11px; color: #7f8c8d; font-family: Arial, sans-serif;">
                        <div>⌨️ Ctrl+R: Refresh</div>
                        <div>⌨️ Ctrl+Z: Reset Zoom</div>
                        <div>⌨️ Ctrl+F: Fit View</div>
                    </div>
                </div>
            `;
            controls.style.cssText = `
                position: absolute;
                top: 10px;
                right: 10px;
                z-index: 1000;
                font-family: Arial, sans-serif;
            `;
            document.body.appendChild(controls);
            
            // Add status indicator
            const statusDiv = document.createElement('div');
            statusDiv.id = 'refreshStatus';
            statusDiv.style.cssText = `
                position: absolute;
                top: 10px;
                left: 10px;
                z-index: 1000;
                background: rgba(255,255,255,0.95);
                color: #2c3e50;
                padding: 10px 16px;
                border-radius: 8px;
                font-size: 12px;
                font-family: Arial, sans-serif;
                font-weight: bold;
                border: 1px solid rgba(0,0,0,0.1);
                box-shadow: 0 4px 16px rgba(0,0,0,0.1);
                display: none;
            `;
            document.body.appendChild(statusDiv);
        }
        
        let autoRefreshInterval = null;
        let isAutoRefreshEnabled = false;
        
        function resetZoom() {
            const plotDiv = document.querySelector('.plotly-graph-div');
            if (plotDiv && plotDiv._fullData) {
                Plotly.relayout(plotDiv, {
                    'xaxis.range': null,
                    'yaxis.range': null
                });
                showStatus('🔍 Zoom reset');
            }
        }
        
        function fitToView() {
            const plotDiv = document.querySelector('.plotly-graph-div');
            if (plotDiv && plotDiv._fullData) {
                const xData = plotDiv._fullData[1].x;
                const yData = plotDiv._fullData[1].y;
                
                if (xData && yData && xData.length > 0) {
                    const xMin = Math.min(...xData);
                    const xMax = Math.max(...xData);
                    const yMin = Math.min(...yData);
                    const yMax = Math.max(...yData);
                    
                    const padding = 50;
                    Plotly.relayout(plotDiv, {
                        'xaxis.range': [xMin - padding, xMax + padding],
                        'yaxis.range': [yMin - padding, yMax + padding]
                    });
                    showStatus('📐 Fitted to view');
                }
            }
        }
        
        function refreshNetwork() {
            showStatus('🔄 Refreshing network...');
            
            const plotDiv = document.querySelector('.plotly-graph-div');
            if (plotDiv && plotDiv._fullData) {
                const data = plotDiv._fullData;
                const nodeTrace = data.find(trace => trace.name === 'Tags');
                
                if (nodeTrace) {
                    const numNodes = nodeTrace.x.length;
                    const newX = [];
                    const newY = [];
                    
                    for (let i = 0; i < numNodes; i++) {
                        newX.push((Math.random() - 0.5) * 400);
                        newY.push((Math.random() - 0.5) * 400);
                    }
                    
                    Plotly.restyle(plotDiv, {
                        x: [newX],
                        y: [newY]
                    }, [1]);
                    
                    showStatus('✅ Network refreshed');
                }
            }
        }
        
        function toggleAutoRefresh() {
            const btn = document.getElementById('autoRefreshBtn');
            
            if (isAutoRefreshEnabled) {
                if (autoRefreshInterval) {
                    clearInterval(autoRefreshInterval);
                    autoRefreshInterval = null;
                }
                isAutoRefreshEnabled = false;
                btn.style.background = 'linear-gradient(45deg, #f39c12, #e67e22)';
                btn.textContent = '⏰ Auto';
                showStatus('⏹️ Auto refresh disabled');
            } else {
                autoRefreshInterval = setInterval(() => {
                    refreshNetwork();
                }, 8000);
                isAutoRefreshEnabled = true;
                btn.style.background = 'linear-gradient(45deg, #e67e22, #d35400)';
                btn.textContent = '⏹️ Stop';
                showStatus('▶️ Auto refresh enabled (8s)');
            }
        }
        
        function showStatus(message) {
            const statusDiv = document.getElementById('refreshStatus');
            if (statusDiv) {
                statusDiv.textContent = message;
                statusDiv.style.display = 'block';
                
                setTimeout(() => {
                    statusDiv.style.display = 'none';
                }, 3000);
            }
        }
        
        // Enhanced keyboard shortcuts
        document.addEventListener('keydown', function(event) {
            switch(event.key) {
                case 'r':
                case 'R':
                    if (event.ctrlKey) {
                        event.preventDefault();
                        refreshNetwork();
                    }
                    break;
                case 'z':
                case 'Z':
                    if (event.ctrlKey) {
                        event.preventDefault();
                        resetZoom();
                    }
                    break;
                case 'f':
                case 'F':
                    if (event.ctrlKey) {
                        event.preventDefault();
                        fitToView();
                    }
                    break;
            }
        });
        
        // Initialize controls when page loads
        window.addEventListener('load', addNetworkControls);
        </script>
        """
        
        return fig.to_html(include_plotlyjs=True, full_html=False) + js_code
    
    def _force_directed_layout(self, adjacency_matrix, n_iterations=150):
        """Generate force-directed layout positions for nodes with enhanced spacing."""
        import numpy as np
        
        n_nodes = len(adjacency_matrix)
        
        # Initialize random positions with larger spread
        positions = np.random.rand(n_nodes, 2) * 800 - 400
        
        # Force-directed layout simulation with enhanced parameters
        for iteration in range(n_iterations):
            forces = np.zeros((n_nodes, 2))
            
            # Enhanced repulsive forces between all nodes
            for i in range(n_nodes):
                for j in range(i + 1, n_nodes):
                    diff = positions[i] - positions[j]
                    distance = np.linalg.norm(diff)
                    if distance > 0:
                        # Stronger repulsive force for better spacing
                        force_magnitude = 2000 / (distance ** 2)
                        # Add minimum distance constraint
                        if distance < 50:  # Minimum distance between nodes
                            force_magnitude += 500 / distance
                        force = force_magnitude * diff / distance
                        forces[i] += force
                        forces[j] -= force
            
            # Attractive forces for connected nodes
            for i in range(n_nodes):
                for j in range(n_nodes):
                    if adjacency_matrix[i][j] > 0:
                        diff = positions[j] - positions[i]
                        distance = np.linalg.norm(diff)
                        if distance > 0:
                            # Balanced attractive force
                            force_magnitude = 0.05 * adjacency_matrix[i][j] * distance
                            force = force_magnitude * diff / distance
                            forces[i] += force
                            forces[j] -= force
            
            # Update positions with adaptive step size
            step_size = 0.15 if iteration < 50 else 0.1  # Faster initial convergence
            positions += forces * step_size
            
            # Keep nodes within larger bounds
            positions = np.clip(positions, -500, 500)
        
        return positions
    
    def _create_tag_distribution(self, papers: List[Dict]) -> str:
        """Create a tag distribution visualization."""
        # Collect tag frequencies
        tag_counts = Counter()
        for paper in papers:
            tag_counts.update(paper.get('tags', []))
        
        if not tag_counts:
            return "<p>No tags found in the papers.</p>"
        
        # Sort tags by frequency and take top tags for readability
        sorted_tags = tag_counts.most_common(20)  # Limit to top 20 for readability
        tags, counts = zip(*sorted_tags)
        
        # Create color mapping based on tag categories
        memory_studies_tags = ['memory_studies', 'collective_memory', 'cosmopolitan_memory', 'cultural_memory', 'social_memory']
        sociology_tags = ['sociology', 'social_theory', 'social_construction']
        political_tags = ['political_science', 'politics', 'citizenship', 'cosmopolitan']
        history_tags = ['history', 'historical', 'commemoration']
        
        colors = []
        for tag in tags:
            if any(mt in tag.lower() for mt in memory_studies_tags):
                colors.append('#FF6B6B')  # Red for memory studies
            elif any(st in tag.lower() for st in sociology_tags):
                colors.append('#4ECDC4')  # Teal for sociology
            elif any(pt in tag.lower() for pt in political_tags):
                colors.append('#45B7D1')  # Blue for political science
            elif any(ht in tag.lower() for ht in history_tags):
                colors.append('#96CEB4')  # Green for history
            else:
                colors.append('#F7DC6F')  # Yellow for others
        
        fig = go.Figure(data=[
            go.Bar(
                x=tags,
                y=counts,
                marker_color=colors,
                text=counts,
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Frequency: %{y}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title={
                'text': 'Tag Distribution - Most Common Tags',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            xaxis=dict(
                title='Tags',
                tickangle=45,
                tickfont=dict(size=10)
            ),
            yaxis=dict(
                title='Frequency',
                showgrid=True,
                gridcolor='lightgray'
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=50, r=50, t=80, b=100),
            height=500,
            showlegend=False
        )
        
        return fig.to_html(include_plotlyjs=True, full_html=False)
    
    def _create_paper_timeline(self, papers: List[Dict]) -> str:
        """Create an interactive paper timeline visualization."""
        # Extract years and create timeline data
        year_counts = Counter()
        paper_details = []
        
        for paper in papers:
            year = paper.get('year', 'Unknown')
            if year and year != 'Unknown':
                try:
                    year_int = int(year)
                    year_counts[year_int] += 1
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
            return "<p>No valid years found in the papers.</p>"
        
        # Sort by year
        sorted_years = sorted(year_counts.items())
        years, counts = zip(*sorted_years)
        
        # Create timeline visualization
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
            paper_ids = [p['id'] for p in paper_details]
            
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
                customdata=np.column_stack((paper_authors, paper_journals, paper_tags)),
                hovertemplate='<b>%{text}</b><br>Year: %{x}<br>Authors: %{customdata[0]}<br>Journal: %{customdata[1]}<br>Tags: %{customdata[2]}<br><i>Click for details</i><extra></extra>'
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
            ),
            # Add click event handling
            clickmode='event+select',
            dragmode='pan'
        )
        
        # Add JavaScript for interactive features
        js_code = """
        <script>
        // Function to handle paper clicks and show details
        function handlePaperClick(event) {
            const point = event.points[0];
            const paperId = point.data.customdata[point.pointIndex];
            
            // Show paper details
            showPaperDetails(paperId);
        }
        
        function showPaperDetails(paperId) {
            // This would show detailed paper information
            console.log('Showing details for paper:', paperId);
        }
        </script>
        """
        
        return fig.to_html(include_plotlyjs=True, full_html=False) + js_code
    
    def _create_paper_dashboard(self, papers: List[Dict], output_file: Path):
        """Create a comprehensive paper dashboard."""
        # Calculate statistics
        total_papers = len(papers)
        
        all_tags = []
        for paper in papers:
            all_tags.extend(paper.get('tags', []))
        
        unique_tags = len(set(all_tags))
        avg_tags_per_paper = len(all_tags) / total_papers if total_papers > 0 else 0
        
        # Create dashboard HTML
        dashboard_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Paper Analysis Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
                .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .stat-box {{ background-color: #e8f4fd; padding: 15px; border-radius: 8px; text-align: center; }}
                .papers-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                .papers-table th, .papers-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                .papers-table th {{ background-color: #f2f2f2; }}
                .tag {{ background-color: #007bff; color: white; padding: 2px 6px; border-radius: 3px; margin: 1px; display: inline-block; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Paper Analysis Dashboard</h1>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="stats">
                <div class="stat-box">
                    <h3>📄 Total Papers</h3>
                    <h2>{total_papers}</h2>
                </div>
                <div class="stat-box">
                    <h3>🏷️ Unique Tags</h3>
                    <h2>{unique_tags}</h2>
                </div>
                <div class="stat-box">
                    <h3>📊 Avg Tags/Paper</h3>
                    <h2>{avg_tags_per_paper:.1f}</h2>
                </div>
            </div>
            
            <h2>📋 Papers Overview</h2>
            <table class="papers-table">
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Authors</th>
                        <th>Year</th>
                        <th>Tags</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for paper in papers:
            title = paper.get('title', 'Unknown')[:50] + ('...' if len(paper.get('title', '')) > 50 else '')
            authors = ', '.join(paper.get('authors', [])[:3])
            if len(paper.get('authors', [])) > 3:
                authors += '...'
            year = paper.get('year', 'Unknown')
            tags = ' '.join([f'<span class="tag">{tag}</span>' for tag in paper.get('tags', [])])
            
            dashboard_html += f"""
                    <tr>
                        <td>{title}</td>
                        <td>{authors}</td>
                        <td>{year}</td>
                        <td>{tags}</td>
                    </tr>
            """
        
        dashboard_html += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(dashboard_html)