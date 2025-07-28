from typing import List, Dict, Optional

class Author:
    def __init__(self, first_name: str, last_name: str):
        self.first_name = first_name
        self.last_name = last_name

    def __repr__(self):
        return f"{self.first_name} {self.last_name}"

class Citation:
    def __init__(self, cited_key: str):
        self.cited_key = cited_key

    def __repr__(self):
        return f"Citation({self.cited_key})"

class Paper:
    def __init__(self,
                 key: str,
                 title: str,
                 creators: List[Author],
                 date: str,
                 item_type: str,
                 abstract: Optional[str] = None,
                 publisher: Optional[str] = None,
                 publication_title: Optional[str] = None,
                 tags: Optional[List[str]] = None,
                 collections: Optional[List[str]] = None,
                 citations: Optional[List[Citation]] = None):
        self.key = key
        self.title = title
        self.creators = creators
        self.date = date
        self.item_type = item_type
        self.abstract = abstract
        self.publisher = publisher
        self.publication_title = publication_title
        self.tags = tags or []
        self.collections = collections or []
        self.citations = citations or []
        self.auto_tags = {}
        self.confidence_scores = {}

    def __repr__(self):
        return f"Paper({self.key}, {self.title})"

class Library:
    def __init__(self, papers: Optional[List[Paper]] = None):
        self.papers = papers or []
        self.paper_dict = {paper.key: paper for paper in self.papers}

    def add_paper(self, paper: Paper):
        self.papers.append(paper)
        self.paper_dict[paper.key] = paper

    def get_paper(self, key: str) -> Optional[Paper]:
        return self.paper_dict.get(key) 