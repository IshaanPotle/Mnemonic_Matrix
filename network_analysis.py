import networkx as nx
from data_models import Library

class CitationNetwork:
    def __init__(self, library: Library):
        self.library = library
        self.graph = nx.DiGraph()
        self._build_graph()

    def _build_graph(self):
        # Add nodes for each paper
        for paper in self.library.papers:
            self.graph.add_node(paper.key, title=paper.title)
        # Add edges for citations
        for paper in self.library.papers:
            for citation in paper.citations:
                if citation.cited_key in self.graph:
                    self.graph.add_edge(paper.key, citation.cited_key)

    def most_cited(self, top_n=5):
        # Returns the top_n most cited papers (by in-degree)
        in_degrees = self.graph.in_degree()
        sorted_papers = sorted(in_degrees, key=lambda x: x[1], reverse=True)
        return [(key, deg) for key, deg in sorted_papers[:top_n]]

    def citation_counts(self):
        # Returns a dict of paper key to (in-degree, out-degree)
        return {key: (self.graph.in_degree(key), self.graph.out_degree(key)) for key in self.graph.nodes}

    def get_graph(self):
        return self.graph 