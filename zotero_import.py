import json
from data_models import Author, Citation, Paper, Library
from typing import List

def parse_authors(creators: List[dict]) -> List[Author]:
    authors = []
    for creator in creators:
        first = creator.get('firstName', '')
        last = creator.get('lastName', '')
        authors.append(Author(first, last))
    return authors

def parse_citations(citations: List[str]) -> List[Citation]:
    return [Citation(key) for key in citations]

def import_zotero_json(json_path: str) -> Library:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    papers = []
    for item in data.get('items', []):
        creators = parse_authors(item.get('creators', []))
        citations = parse_citations(item.get('citations', [])) if 'citations' in item else []
        paper = Paper(
            key=item.get('key'),
            title=item.get('title'),
            creators=creators,
            date=item.get('date', ''),
            item_type=item.get('itemType', ''),
            abstract=item.get('abstract', None),
            publisher=item.get('publisher', None),
            publication_title=item.get('publicationTitle', None),
            tags=item.get('tags', []),
            collections=item.get('collections', []),
            citations=citations
        )
        papers.append(paper)
    return Library(papers)

def export_zotero_json(library: Library, json_path: str):
    items = []
    for paper in library.papers:
        item = {
            'key': paper.key,
            'title': paper.title,
            'creators': [{'firstName': a.first_name, 'lastName': a.last_name} for a in paper.creators],
            'date': paper.date,
            'itemType': paper.item_type,
            'abstract': paper.abstract,
            'publisher': paper.publisher,
            'publicationTitle': paper.publication_title,
            'tags': paper.tags,
            'collections': paper.collections,
            'citations': [c.cited_key for c in paper.citations]
        }
        items.append(item)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({'items': items}, f, indent=2, ensure_ascii=False) 