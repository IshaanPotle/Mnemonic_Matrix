#!/usr/bin/env python3
"""
Simplified test to isolate the tag selection issue
"""

import streamlit as st
from bibtex_processor import parse_bibtex
from auto_tagger import AutoTagger

def main():
    st.title("🧪 Simple Tag Selection Test")
    
    # Load and process papers
    with open('training_papers.bib', 'r', encoding='utf-8') as f:
        bibtex_content = f.read()
    
    papers = parse_bibtex(bibtex_content)
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
    
    # Simple tag selection
    if tag_papers:
        tag_options = list(tag_papers.keys())
        tag_options.sort()
        
        st.subheader("🎯 Tag Selection Test")
        
        # Test 1: Basic selectbox
        st.write("**Test 1: Basic Selectbox**")
        selected_tag1 = st.selectbox(
            "Choose a tag:",
            options=tag_options,
            key="test1"
        )
        
        if selected_tag1:
            st.write(f"✅ Selected: {selected_tag1}")
            st.write(f"📋 Papers: {len(tag_papers[selected_tag1])}")
        
        # Test 2: With format function
        st.write("**Test 2: With Format Function**")
        selected_tag2 = st.selectbox(
            "Choose a tag (with count):",
            options=tag_options,
            format_func=lambda x: f"{x} ({len(tag_papers[x])} papers)",
            key="test2"
        )
        
        if selected_tag2:
            st.write(f"✅ Selected: {selected_tag2}")
            st.write(f"📋 Papers: {len(tag_papers[selected_tag2])}")
        
        # Test 3: Radio buttons
        st.write("**Test 3: Radio Buttons**")
        explorer_choice = st.radio(
            "Choose explorer:",
            ["🏷️ Tag Explorer", "📄 Paper Explorer"],
            horizontal=True,
            key="test3"
        )
        
        st.write(f"✅ Selected: {explorer_choice}")
        
        if explorer_choice == "🏷️ Tag Explorer":
            selected_tag3 = st.selectbox(
                "Select tag:",
                options=tag_options,
                key="test3_tag"
            )
            if selected_tag3:
                st.write(f"✅ Tag selected: {selected_tag3}")

if __name__ == "__main__":
    main()