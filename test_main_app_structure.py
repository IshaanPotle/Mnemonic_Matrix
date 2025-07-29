#!/usr/bin/env python3
"""
Test that mimics the exact structure of the main app
"""

import streamlit as st
from bibtex_processor import BibTeXProcessor
from auto_tagger import AutoTagger

def test_main_app_structure():
    st.title("🧪 Main App Structure Test")
    
    # Load and process papers
    processor = BibTeXProcessor()
    papers = processor.parse_bibtex('training_papers.bib')
    tagger = AutoTagger()
    
    for paper in papers:
        paper['tags'] = tagger.predict_tags(paper)
    
    st.write(f"✅ Processed {len(papers)} papers")
    
    # Mimic the exact structure from main app
    st.subheader("🔍 Interactive Explorers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏷️ Tag Explorer")
        
        # Build tag relationships and paper mappings (exact copy from main app)
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
        
        # Create tag selection interface (exact copy from main app)
        if tag_relationships:
            # Sort tags by frequency
            tag_frequencies = {tag: len(tag_papers[tag]) for tag in tag_papers.keys()}
            sorted_tags = sorted(tag_frequencies.items(), key=lambda x: x[1], reverse=True)
            tag_options = [tag for tag, _ in sorted_tags]
            
            # Create a container for the tag selector
            tag_container = st.container()
            
            with tag_container:
                # Simple tag selection without any session state
                selected_tag = st.selectbox(
                    "Select a tag to explore its relationships:",
                    options=tag_options,
                    format_func=lambda x: f"{x} ({tag_frequencies[x]} papers)",
                    key="tag_selector_final"
                )
            
            # Create a container for the tag content
            content_container = st.container()
            
            with content_container:
                if selected_tag:
                    st.write(f"🔍 Debug: Processing tag '{selected_tag}'")
                    
                    col1_inner, col2_inner = st.columns([1, 1])
                    
                    with col1_inner:
                        st.subheader(f"📋 Papers with '{selected_tag}'")
                        papers_with_tag = tag_papers[selected_tag]
                        st.write(f"🔍 Debug: Found {len(papers_with_tag)} papers with this tag")
                        
                        for i, paper in enumerate(papers_with_tag):
                            with st.expander(f"{paper['title'][:60]}..."):
                                st.write(f"**Authors:** {paper['authors']}")
                                st.write(f"**Year:** {paper['year']}")
                                st.write(f"**Journal:** {paper['journal']}")
                    
                    with col2_inner:
                        st.subheader(f"🔗 Related Tags")
                        related_tags = tag_relationships[selected_tag]
                        st.write(f"🔍 Debug: Found {len(related_tags)} related tags")
                        
                        if related_tags:
                            # Show related tags with their frequencies
                            related_tag_freqs = []
                            for tag in related_tags:
                                freq = tag_frequencies.get(tag, 0)
                                related_tag_freqs.append((tag, freq))
                            
                            # Sort by frequency
                            related_tag_freqs.sort(key=lambda x: x[1], reverse=True)
                            
                            for tag, freq in related_tag_freqs:
                                st.write(f"• **{tag}** ({freq} papers)")
                        else:
                            st.info("No related tags found.")
                    
                    # Remove co-occurrence matrix for now to simplify
                    st.write(f"🔍 Debug: Finished processing tag '{selected_tag}'")
    
    with col2:
        st.subheader("📄 Paper Explorer")
        st.write("Paper explorer content would go here...")

if __name__ == "__main__":
    test_main_app_structure()