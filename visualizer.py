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
        """Create a simple HTML-based tag network visualization."""
        # Collect all matrix tags and their frequencies
        tag_counts = {}
        tag_metadata = {}
        
        # Define matrix tag categories with colors
        matrix_categories = {
            'time': {
                'name': '⏰ Time Periods',
                'tags': ['T1', 'T2', 'T3', 'T4', 'T5'],
                'color': '#FF6B9D'
            },
            'discipline': {
                'name': '🎓 Academic Disciplines', 
                'tags': ['DSOC', 'DHIS', 'DSPY', 'DNEU', 'DPOL', 'DANT', 'DGEO', 
                         'DARC', 'DLIT', 'DCUL', 'DLAW', 'DPHI', 'DPSY', 'DMED', 
                         'DEDU', 'DHUM', 'DSS', 'DMU', 'DHE', 'DAR'],
                'color': '#4ECDC4'
            },
            'memory_carrier': {
                'name': '🏛️ Memory Carriers',
                'tags': ['MCSO', 'MCLI', 'MCFI', 'MCT', 'MCAR', 'MCPH', 'MCC', 
                         'MCMO', 'MCA', 'MCB', 'MCME', 'MCLA', 'MCED', 'MCMU', 
                         'MCF', 'MCT', 'MCNAT'],
                'color': '#45B7D1'
            },
            'concept_tags': {
                'name': '🧠 Memory Concepts',
                'tags': ['CTArchives', 'CTAutobiographicalMemory', 'CTAgonisticMemory', 'CTAmnesia', 'CTAestheticMemory',
                         'CTBanalMnemonics', 'CTCanons', 'CTCommunicativeMemory', 'CTCulturalTrauma', 'CTCollectiveMemory', 
                         'CTCulturalMemory', 'CTCosmopolitanMemory', 'CTCommemoration', 'CTCatastrophicMemory', 'CTCounterMemory',
                         'CTDialogical', 'CTDeclarativeMemory', 'CTDigitalMemory', 'CTDutyToRemember', 'CTEngrams', 
                         'CTEpisodicMemory', 'CTExplicitMemory', 'CTEntangledMemory', 'CTFamilyMemory', 'CTFlashbulbMemory', 
                         'CTFlashback', 'CTForgetting', 'CTForgettingCurve', 'CTFalseMemory', 'CTGenreMemory', 'CTGlobitalMemory', 
                         'CTGlobalMemory', 'CTGenerationalMemory', 'CTHeritage', 'CTHistoricalMemory', 'CTHyperthymesia',
                         'CTIdentity', 'CTImplicitMemory', 'CTIntergenerationalTransmissions', 'CTIconicMemory', 'CTImaginativeReconstruction',
                         'CTLongueDuree', 'CTMultidirectionalMemory', 'CTMnemonicSecurity', 'CTMilieuDeMemoire', 'CTMemoryLaws', 
                         'CTMnemohistory', 'CTMemoryConsolidation', 'CTMemoryRetrieval', 'CTMemoryEncoding', 'CTMemoryStorage', 
                         'CTMemoryTrace', 'CTMemorySpan', 'CTMemoryDistortion', 'CTMemoryAccuracy', 'CTMemoryBias', 'CTMemoryEnhancement',
                         'CTMemorySuppression', 'CTMemorySchemas', 'CTMnemonics', 'CTMemoryPolitics', 'CTMnemonicCommunities',
                         'CTMnemonicSocialization', 'CTMemoryEthics', 'CTMemoryPractices', 'CTMnemonicStandoff', 'CTNationalMemory', 
                         'CTNonContemporaneity', 'CTOfficialMemory', 'CTParticularism', 'CTPrivateMemory', 'CTPublicMemory', 
                         'CTPathDependency', 'CTProceduralMemory', 'CTProstheticMemory', 'CTPostColonialMemory', 'CTProspectiveMemory', 
                         'CTProfaneMemory', 'CTPostMemory', 'CTRealmsOfMemory', 'CTRegret', 'CTRestitution', 'CTReparations', 
                         'CTRedress', 'CTRepressedMemory', 'CTRecoveredMemory', 'CTRetrospectiveMemory', 'CTRevisionistMemory', 
                         'CTReligiousMemory', 'CTSemanticMemory', 'CTSocialFrameworks', 'CTSlowMemory', 'CTSocialMemory', 
                         'CTScreenMemory', 'CTSensoryMemory', 'CTSourceMemory', 'CTSacredMemory', 'CTTrauma', 'CTTradition', 
                         'CTTravellingMemory', 'CTTransnationalMemory', 'CTTransculturalMemory', 'CTTransoceanicMemory', 
                         'CTUniversalism', 'CTVernacularMemory', 'CTWorkingMemory'],
                'color': '#F7DC6F'
            }
        }
        
        # Collect tag data
        for paper in papers:
            for tag in paper.get('tags', []):
                if tag not in tag_counts:
                    tag_counts[tag] = 0
                    # Find which category this tag belongs to
                    tag_category = None
                    for cat_name, cat_info in matrix_categories.items():
                        if tag in cat_info['tags']:
                            tag_category = cat_name
                            break
                    
                    tag_metadata[tag] = {
                        'category': tag_category,
                        'category_name': matrix_categories.get(tag_category, {}).get('name', 'Unknown'),
                        'category_color': matrix_categories.get(tag_category, {}).get('color', '#95a5a6')
                    }
                
                tag_counts[tag] += 1
        
        # Show ALL matrix tags that appear in papers (no artificial limit)
        filtered_tags = {tag: count for tag, count in tag_counts.items() if count >= 1}
        sorted_tags = sorted(filtered_tags.items(), key=lambda x: x[1], reverse=True)
        all_used_tags = sorted_tags  # Show all tags, not just top 20
        
        # Also get all possible matrix tags for completeness analysis
        all_possible_tags = set()
        for cat_info in matrix_categories.values():
            all_possible_tags.update(cat_info['tags'])
        
        # Find missing tags (tags in matrix but not in papers)
        used_tag_set = set(tag_counts.keys())
        missing_tags = all_possible_tags - used_tag_set
        
        if not all_used_tags:
            return "<p style='color: #E8E8E8; font-family: Arial, sans-serif; text-align: center; padding: 20px;'>No matrix tags found in the papers.</p>"
        
        node_count = len(all_used_tags)
        
        # Create simple HTML visualization
        html_parts = []
        html_parts.append(f"""
        <div style="background-color: #1A1A1A; padding: 20px; border-radius: 10px; color: #E8E8E8;">
            <h3 style="text-align: center; color: #FF6B9D; margin-bottom: 20px;">🌟 Memory Studies Knowledge Network ({node_count} nodes)</h3>
        """)
        
        # Group tags by category
        categories = {}
        for tag, count in all_used_tags:
            metadata = tag_metadata.get(tag, {})
            category = metadata.get('category', 'unknown')
            if category not in categories:
                categories[category] = []
            categories[category].append((tag, count))
        
        # Display each category
        for cat_name, cat_info in matrix_categories.items():
            if cat_name in categories:
                html_parts.append(f"""
                <div style="margin-bottom: 20px; padding: 15px; background-color: rgba(255,255,255,0.05); border-radius: 8px; border-left: 4px solid {cat_info['color']};">
                    <h4 style="color: {cat_info['color']}; margin-bottom: 10px;">{cat_info['name']}</h4>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                """)
                
                for tag, count in categories[cat_name]:
                    size = 12 + (count / max(tag_counts.values())) * 8  # 12-20px font size
                    html_parts.append(f"""
                    <span style="
                        background-color: {cat_info['color']};
                        color: white;
                        padding: 5px 10px;
                        border-radius: 15px;
                        font-size: {size}px;
                        font-weight: bold;
                        display: inline-block;
                        margin: 2px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                    " title="Frequency: {count} papers">
                        {tag} ({count})
                    </span>
                    """)
                
                html_parts.append("</div></div>")
        
        html_parts.append("</div>")
        
        # Create interactive Plotly network graph
        import plotly.graph_objects as go
        import numpy as np
        
        # Create nodes for the graph
        node_labels = []
        node_sizes = []
        node_colors = []
        node_positions = []
        
        # Calculate node positions in a circle layout
        for i, (tag, count) in enumerate(all_used_tags):
            node_labels.append(tag)
            
            # Smart node sizing: consider both frequency and importance
            base_size = 20 + count * 5  # Base size from frequency
            
            # Boost size for rare but important tags (appear in 1-2 papers)
            if count <= 2:
                base_size += 10  # Make rare tags more visible
            
            node_sizes.append(base_size)
            
            # Get category color
            metadata = tag_metadata.get(tag, {})
            category = metadata.get('category', 'unknown')
            color = matrix_categories.get(category, {}).get('color', '#95a5a6')
            node_colors.append(color)
            
            # Position nodes in a circle
            angle = 2 * np.pi * i / len(all_used_tags)
            radius = 100
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            node_positions.append([x, y])
        
        # Create edges based on co-occurrence
        edges = []
        edge_weights = []
        
        for i, (tag1, count1) in enumerate(all_used_tags):
            for j, (tag2, count2) in enumerate(all_used_tags[i+1:], i+1):
                # Check if tags appear together in papers
                co_occurrence = 0
                for paper in papers:
                    paper_tags = paper.get('tags', [])
                    if tag1 in paper_tags and tag2 in paper_tags:
                        co_occurrence += 1
                
                if co_occurrence > 0:
                    edges.append([i, j])
                    edge_weights.append(co_occurrence)
        
        # Create the network graph
        fig = go.Figure()
        
        # Add edges
        if edges:
            edge_x = []
            edge_y = []
            edge_hover_texts = []
            
            for edge, weight in zip(edges, edge_weights):
                x0, y0 = node_positions[edge[0]]
                x1, y1 = node_positions[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
                
                # Create detailed hover text for edge
                tag1 = node_labels[edge[0]]
                tag2 = node_labels[edge[1]]
                
                # Find papers that contain both tags
                papers_with_both_tags = []
                for paper in papers:
                    paper_tags = paper.get('tags', [])
                    if tag1 in paper_tags and tag2 in paper_tags:
                        title = paper.get('title', 'Unknown Title')
                        authors = ', '.join(paper.get('authors', []))[:40] + '...' if len(', '.join(paper.get('authors', []))) > 40 else ', '.join(paper.get('authors', []))
                        year = paper.get('year', 'Unknown')
                        papers_with_both_tags.append(f"• {title} ({year})")
                
                # Create detailed edge hover text
                edge_hover_text = f"""
                <b>{tag1} ↔ {tag2}</b><br>
                <b>Co-occurrence:</b> {weight} papers<br>
                <b>Papers with both tags:</b><br>
                {chr(10).join(papers_with_both_tags[:2])}
                """
                if len(papers_with_both_tags) > 2:
                    edge_hover_text += f"<br>... and {len(papers_with_both_tags) - 2} more"
                
                edge_hover_texts.extend([edge_hover_text, "", ""])
            
            fig.add_trace(go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=1, color='#888'),
                hoverinfo='text',
                hovertext=edge_hover_texts,
                mode='lines'))
        
        # Add nodes
        node_x = [pos[0] for pos in node_positions]
        node_y = [pos[1] for pos in node_positions]
        
        # Create comprehensive hover text with detailed information
        hover_texts = []
        for i, (tag, count) in enumerate(all_used_tags):
            metadata = tag_metadata.get(tag, {})
            category_name = metadata.get('category_name', 'Unknown')
            
            # Find papers that contain this tag
            papers_with_tag = []
            for paper in papers:
                if tag in paper.get('tags', []):
                    title = paper.get('title', 'Unknown Title')
                    authors = ', '.join(paper.get('authors', []))[:50] + '...' if len(', '.join(paper.get('authors', []))) > 50 else ', '.join(paper.get('authors', []))
                    year = paper.get('year', 'Unknown')
                    papers_with_tag.append(f"• {title} ({year}) by {authors}")
            
            # Create detailed hover text
            hover_text = f"""
            <b>{tag}</b><br>
            <b>Category:</b> {category_name}<br>
            <b>Frequency:</b> {count} papers<br>
            <b>Papers:</b><br>
            {chr(10).join(papers_with_tag[:3])}
            """
            if len(papers_with_tag) > 3:
                hover_text += f"<br>... and {len(papers_with_tag) - 3} more papers"
            
            hover_texts.append(hover_text)
        
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_labels,
            textposition="middle center",
            hovertext=hover_texts,
            marker=dict(
                size=node_sizes,
                color=node_colors,
                line=dict(width=2, color='white')
            ),
            textfont=dict(size=10, color='white')
        ))
        
        # Create legend for categories with completeness info
        legend_items = []
        for cat_name, cat_info in matrix_categories.items():
            if cat_name in categories:
                # Calculate category completeness
                category_tags = set(cat_info['tags'])
                used_category_tags = category_tags.intersection(used_tag_set)
                completeness = len(used_category_tags) / len(category_tags) * 100
                
                legend_items.append(
                    go.Scatter(
                        x=[None], y=[None],
                        mode='markers',
                        marker=dict(size=10, color=cat_info['color']),
                        name=f"{cat_info['name']} ({len(used_category_tags)}/{len(category_tags)} tags)",
                        showlegend=True
                    )
                )
        
        # Add legend traces
        for item in legend_items:
            fig.add_trace(item)
        
        # Calculate matrix completeness
        total_possible_tags = len(all_possible_tags)
        total_used_tags = len(used_tag_set)
        matrix_completeness = (total_used_tags / total_possible_tags) * 100 if total_possible_tags > 0 else 0
        
        # Update layout
        fig.update_layout(
            title=f'🌟 Interactive Memory Studies Knowledge Network ({node_count} nodes, {matrix_completeness:.1f}% matrix coverage)',
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='#1A1A1A',
            paper_bgcolor='#0F0F0F',
            height=600,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='rgba(30,30,30,0.95)',
                bordercolor='rgba(255,255,255,0.2)',
                borderwidth=1,
                font=dict(color='#E8E8E8', size=12)
            )
        )
        
        # Create matrix completeness analysis
        completeness_html = f"""
        <div style="background-color: #1A1A1A; padding: 15px; border-radius: 8px; margin-top: 20px; color: #E8E8E8;">
            <h4 style="color: #FF6B9D; margin-bottom: 10px;">📊 Matrix Completeness Analysis</h4>
            <p><strong>Overall Coverage:</strong> {total_used_tags}/{total_possible_tags} tags ({matrix_completeness:.1f}%)</p>
            <p><strong>Missing Tags:</strong> {len(missing_tags)} tags not represented in your corpus</p>
        """
        
        # Show category-wise completeness
        for cat_name, cat_info in matrix_categories.items():
            category_tags = set(cat_info['tags'])
            used_category_tags = category_tags.intersection(used_tag_set)
            category_completeness = len(used_category_tags) / len(category_tags) * 100
            
            completeness_html += f"""
            <div style="margin: 5px 0; padding: 5px; background-color: rgba(255,255,255,0.05); border-radius: 5px;">
                <span style="color: {cat_info['color']};">{cat_info['name']}:</span> {len(used_category_tags)}/{len(category_tags)} tags ({category_completeness:.1f}%)
            </div>
            """
        
        completeness_html += "</div>"
        
        # Combine the interactive graph with completeness analysis
        full_html = fig.to_html(include_plotlyjs=True, full_html=False) + completeness_html
        
        return full_html
    
    def _force_directed_layout(self, adjacency_matrix, n_iterations=250):
        """Generate force-directed layout positions for nodes with enhanced spacing and collision detection."""
        import numpy as np
        
        n_nodes = len(adjacency_matrix)
        
        # Initialize positions in a more controlled way to ensure visibility
        positions = np.random.rand(n_nodes, 2) * 400 - 200  # Larger spread for better visibility
        
        # Enhanced force-directed layout simulation with compact parameters
        for iteration in range(n_iterations):
            forces = np.zeros((n_nodes, 2))
            
            # Enhanced repulsive forces between all nodes with collision detection
            for i in range(n_nodes):
                for j in range(i + 1, n_nodes):
                    diff = positions[i] - positions[j]
                    distance = np.linalg.norm(diff)
                    
                    if distance > 0:
                        # Repulsive force for better spacing
                        min_distance = 150  # Larger minimum distance for better visibility
                        
                        if distance < min_distance:
                            # Strong repulsion when nodes are too close
                            force_magnitude = 12000 / (distance ** 2) + 800 / distance
                        else:
                            # Normal repulsion
                            force_magnitude = 6000 / (distance ** 2)
                        
                        force = force_magnitude * diff / distance
                        forces[i] += force
                        forces[j] -= force
            
            # Attractive forces for connected nodes with distance-based scaling
            for i in range(n_nodes):
                for j in range(n_nodes):
                    if adjacency_matrix[i][j] > 0:
                        diff = positions[j] - positions[i]
                        distance = np.linalg.norm(diff)
                        
                        if distance > 0:
                            # Distance-based attractive force
                            ideal_distance = 200  # Larger ideal distance for better visibility
                            if distance > ideal_distance:
                                # Pull nodes closer if they're too far
                                force_magnitude = 0.4 * adjacency_matrix[i][j] * (distance - ideal_distance)
                            else:
                                # Push nodes apart if they're too close
                                force_magnitude = 0.2 * adjacency_matrix[i][j] * (ideal_distance - distance)
                            
                            force = force_magnitude * diff / distance
                            forces[i] += force
                            forces[j] -= force
            
            # Boundary forces to keep nodes within larger, visible bounds
            boundary_force = 500  # Strong boundary force for better layout
            for i in range(n_nodes):
                # X-axis boundary
                if positions[i][0] < -300:
                    forces[i][0] += boundary_force
                elif positions[i][0] > 300:
                    forces[i][0] -= boundary_force
                
                # Y-axis boundary
                if positions[i][1] < -300:
                    forces[i][1] += boundary_force
                elif positions[i][1] > 300:
                    forces[i][1] -= boundary_force
            
            # Update positions with adaptive step size
            step_size = 0.3 if iteration < 150 else 0.15  # Faster convergence for compact layout
            positions += forces * step_size
            
            # Keep nodes within larger, visible bounds
            positions = np.clip(positions, -300, 300)
        
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
                'font': {'size': 18, 'color': '#E8E8E8'}
            },
            xaxis=dict(
                title=dict(text='Tags', font=dict(color='#E8E8E8')),
                tickangle=45,
                tickfont=dict(size=10, color='#E8E8E8'),
                gridcolor='rgba(255,255,255,0.1)',
                zerolinecolor='rgba(255,255,255,0.2)',
                tickcolor='#E8E8E8'
            ),
            yaxis=dict(
                title=dict(text='Frequency', font=dict(color='#E8E8E8')),
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)',
                tickfont=dict(color='#E8E8E8'),
                zerolinecolor='rgba(255,255,255,0.2)',
                tickcolor='#E8E8E8'
            ),
            plot_bgcolor='#1A1A1A',
            paper_bgcolor='#0F0F0F',
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
                'font': {'size': 18, 'color': '#E8E8E8'}
            },
            xaxis=dict(
                title=dict(text='Publication Year', font=dict(color='#E8E8E8')),
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)',
                tickfont=dict(color='#E8E8E8'),
                zerolinecolor='rgba(255,255,255,0.2)',
                tickcolor='#E8E8E8'
            ),
            yaxis=dict(
                title=dict(text='Number of Papers', font=dict(color='#E8E8E8')),
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)',
                tickfont=dict(color='#E8E8E8'),
                zerolinecolor='rgba(255,255,255,0.2)',
                tickcolor='#E8E8E8'
            ),
            plot_bgcolor='#1A1A1A',
            paper_bgcolor='#0F0F0F',
            margin=dict(l=50, r=50, t=80, b=50),
            height=500,
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='rgba(30,30,30,0.95)',
                bordercolor='rgba(255,255,255,0.2)',
                borderwidth=1,
                font=dict(color='#E8E8E8', size=12)
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
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #0F0F0F; color: #E8E8E8; }}
                .header {{ background-color: #1A1A1A; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #444444; }}
                .header h1 {{ color: #64B5F6; text-shadow: 0 0 10px rgba(100, 181, 246, 0.3); }}
                .header p {{ color: #B0B0B0; }}
                .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .stat-box {{ background-color: #1A1A1A; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #444444; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2); }}
                .stat-box h3 {{ color: #64B5F6; }}
                .stat-box h2 {{ color: #E8E8E8; }}
                .papers-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                .papers-table th, .papers-table td {{ border: 1px solid #444444; padding: 8px; text-align: left; }}
                .papers-table th {{ background-color: #1A1A1A; color: #64B5F6; }}
                .papers-table td {{ background-color: #1A1A1A; color: #E8E8E8; }}
                .tag {{ background: linear-gradient(135deg, #64B5F6, #1976D2); color: white; padding: 2px 6px; border-radius: 3px; margin: 1px; display: inline-block; font-size: 12px; box-shadow: 0 2px 4px rgba(100, 181, 246, 0.3); }}
                h2 {{ color: #64B5F6; }}
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