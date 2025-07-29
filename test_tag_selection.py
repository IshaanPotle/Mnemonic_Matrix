#!/usr/bin/env python3
"""
Simple test to check tag selection behavior
"""

import streamlit as st
from bibtex_processor import BibTeXProcessor
from auto_tagger import AutoTagger

def test_tag_selection():
    st.title("🧪 Tag Selection Test")
    
    # Load and process papers
    with open('training_papers.bib', 'r', encoding='utf-8') as f:
        bibtex_content = f.read()
    
    processor = BibTeXProcessor()
    papers = processor.parse_bibtex('training_papers.bib')
    tagger = AutoTagger()
    
    for paper in papers:
        paper['tags'] = tagger.predict_tags(paper)
    
    st.write(f"✅ Processed {len(papers)} papers")
    
    # Build tag data
    tag_papers = {}
    for paper in papers:
        for tag in paper.get('tags', []):
            if tag not in tag_papers:
                tag_papers[tag] = []
            tag_papers[tag].append(paper)
    
    if tag_papers:
        tag_options = list(tag_papers.keys())
        tag_options.sort()
        
        st.subheader("🎯 Testing Tag Selection")
        
        # Test 1: Basic selectbox
        st.write("**Test 1: Basic Selectbox**")
        selected_tag = st.selectbox(
            "Choose a tag:",
            options=tag_options,
            key="test_tag_selector"
        )
        
        if selected_tag:
            st.success(f"✅ Selected: {selected_tag}")
            st.write(f"📋 Papers: {len(tag_papers[selected_tag])}")
            
            # Show papers with this tag
            st.write("**Papers with this tag:**")
            for i, paper in enumerate(tag_papers[selected_tag]):
                st.write(f"{i+1}. {paper.get('title', 'Unknown')[:60]}...")

if __name__ == "__main__":
    test_tag_selection()