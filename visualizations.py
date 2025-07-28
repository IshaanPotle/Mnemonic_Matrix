import networkx as nx
import plotly.express as px
import plotly.graph_objects as go
from networkx.readwrite import json_graph
from collections import Counter
import pandas as pd

# Citation network visualization (returns Plotly Figure)
def plot_citation_network(graph):
    pos = nx.spring_layout(graph, seed=42)
    edge_x = []
    edge_y = []
    for edge in graph.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=0.5, color='#888'), hoverinfo='none', mode='lines')

    node_x = []
    node_y = []
    node_text = []
    for node in graph.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(str(node))
    node_trace = go.Scatter(
        x=node_x, y=node_y, mode='markers+text', text=node_text, textposition='top center',
        marker=dict(size=10, color='blue'), hoverinfo='text')

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=40),
                        xaxis=dict(showgrid=False, zeroline=False),
                        yaxis=dict(showgrid=False, zeroline=False)))
    return fig

# Timeline visualization (papers per year)
def plot_timeline(papers):
    years = []
    for paper in papers:
        try:
            year = int(str(paper.date)[:4])
            years.append(year)
        except:
            continue
    df = pd.DataFrame({'year': years})
    fig = px.histogram(df, x='year', nbins=30, title='Papers per Year')
    return fig

# Tag/discipline distribution (bar chart)
def plot_tag_distribution(papers, tag_type='disciplines'):
    tags = []
    for paper in papers:
        if hasattr(paper, 'auto_tags') and tag_type in paper.auto_tags:
            tags.extend(paper.auto_tags[tag_type])
    tag_counts = Counter(tags)
    df = pd.DataFrame({'tag': list(tag_counts.keys()), 'count': list(tag_counts.values())})
    fig = px.bar(df, x='tag', y='count', title=f'{tag_type.capitalize()} Distribution')
    return fig 