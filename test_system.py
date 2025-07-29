#!/usr/bin/env python3
"""
Test script for the updated BibTeX processing system
"""

from bibtex_processor import BibTeXProcessor
from auto_tagger import AutoTagger

def test_system():
    """Test the system with actual training_papers.bib file."""
    
    # Initialize components
    bp = BibTeXProcessor()
    at = AutoTagger()
    
    # Parse papers from the actual training file
    papers = bp.parse_bibtex('training_papers.bib')
    print(f"✅ Found {len(papers)} papers")
    
    # Process each paper
    for i, paper in enumerate(papers):
        raw_title = paper.get('title', 'Unknown')
        cleaned_title = bp._clean_field_value(raw_title)
        
        print(f"\n📄 Paper {i+1}:")
        print(f"   Raw title: {raw_title}")
        print(f"   Cleaned title: {cleaned_title}")
        print(f"   Authors: {', '.join(paper.get('authors', []))}")
        print(f"   Year: {paper.get('year', 'Unknown')}")
        print(f"   Journal: {paper.get('journal', 'Unknown')}")
        print(f"   Keywords: {paper.get('keywords', [])}")
        
        # Auto-tag
        existing_keywords = paper.get('keywords', [])
        tags = at.predict_tags(
            paper.get('title', ''), 
            paper.get('abstract', ''), 
            existing_keywords
        )
        print(f"   Auto-tags: {len(tags)} tags")
        print("-" * 80)

if __name__ == "__main__":
    test_system()