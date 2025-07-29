#!/usr/bin/env python3
"""
Debug script to test tag selection functionality
"""

import streamlit as st
import json
from bibtex_processor import parse_bibtex
from auto_tagger import AutoTagger

def debug_tag_selection():
    """Debug the tag selection issue"""
    
    st.title("🔍 Debug Tag Selection")
    
    # Load test data
    with open('training_papers.bib', 'r', encoding='utf-8') as f:
        bibtex_content = f.read()
    
    # Parse papers
    papers = parse_bibtex(bibtex_content)
    st.write(f"✅ Parsed {len(papers)} papers")
    
    # Auto-tag papers
    tagger = AutoTagger()
    for paper in papers:
        paper['tags'] = tagger.predict_tags(paper)
    
    st.write(f"✅ Tagged {len(papers)} papers")
    
    # Show all tags
    all_tags = set()
    for paper in papers:
        all_tags.update(paper.get('tags', []))
    
    st.write(f"✅ Found {len(all_tags)} unique tags")
    st.write("All tags:", sorted(all_tags))
    
    # Test tag selection
    st.subheader("🧪 Testing Tag Selection")
    
    # Build tag relationships
    tag_relationships = {}
    tag_papers = {}
    
    for paper in papers:
        paper_tags = paper.get('tags', [])
        paper_info = {
            'title': paper.get('title', 'Unknown'),
            'authors': ', '.join(paper.get('authors', [])),
            'year': paper.get('year', 'Unknown'),
            'journal': paper.get('journal', 'Unknown')
        }
        
        for tag in paper_tags:
            if tag not in tag_relationships:
                tag_relationships[tag] = set()
                tag_papers[tag] = []
            
            # Add relationships with other tags in this paper
            for other_tag in paper_tags:
                if other_tag != tag:
                    tag_relationships[tag].add(other_tag)
            
            # Add paper to tag's paper list
            tag_papers[tag].append(paper_info)
    
    if tag_relationships:
        # Sort tags by frequency
        tag_frequencies = {tag: len(papers) for tag, papers in tag_papers.items()}
        sorted_tags = sorted(tag_frequencies.items(), key=lambda x: x[1], reverse=True)
        tag_options = [tag for tag, _ in sorted_tags]
        
        st.write(f"✅ Found {len(tag_options)} tags with relationships")
        st.write("Top 10 tags:", tag_options[:10])
        
        # Test the selectbox
        st.subheader("🎯 Testing Selectbox")
        
        selected_tag = st.selectbox(
            "Select a tag to explore:",
            options=tag_options,
            format_func=lambda x: f"{x} ({tag_frequencies[x]} papers)",
            key="debug_tag_selector"
        )
        
        if selected_tag:
            st.success(f"✅ Selected tag: {selected_tag}")
            
            # Show papers with this tag
            papers_with_tag = tag_papers[selected_tag]
            st.write(f"📋 Papers with '{selected_tag}': {len(papers_with_tag)}")
            
            for i, paper in enumerate(papers_with_tag):
                st.write(f"{i+1}. {paper['title'][:60]}...")
            
            # Show related tags
            related_tags = tag_relationships[selected_tag]
            st.write(f"🔗 Related tags: {len(related_tags)}")
            for tag in sorted(related_tags)[:10]:
                st.write(f"• {tag}")

if __name__ == "__main__":
    debug_tag_selection()