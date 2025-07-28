import streamlit as st
import json
from zotero_import import import_zotero_json
from auto_tagger import MnemonicTagger
from network_analysis import CitationNetwork
from visualizations import plot_citation_network, plot_timeline, plot_tag_distribution

st.set_page_config(page_title="Mnemonic Matrix Dashboard", layout="wide")
st.title("Mnemonic Matrix Academic Dashboard")

uploaded_file = st.file_uploader("Upload Zotero JSON file", type=["json"])

if uploaded_file:
    data = json.load(uploaded_file)
    # Save to temp file for import function
    with open("_tmp_upload.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    library = import_zotero_json("_tmp_upload.json")
    tagger = MnemonicTagger()
    for paper in library.papers:
        tags, scores = tagger.categorize(paper)
        paper.auto_tags = tags
        paper.confidence_scores = scores
    st.success(f"Imported {len(library.papers)} papers.")

    # Visualizations
    st.header("Timeline of Papers")
    st.plotly_chart(plot_timeline(library.papers), use_container_width=True)

    st.header("Discipline Distribution")
    st.plotly_chart(plot_tag_distribution(library.papers, tag_type='disciplines'), use_container_width=True)

    st.header("Concept Distribution")
    st.plotly_chart(plot_tag_distribution(library.papers, tag_type='concepts'), use_container_width=True)

    st.header("Citation Network")
    network = CitationNetwork(library)
    st.plotly_chart(plot_citation_network(network.get_graph()), use_container_width=True)

    st.header("Paper Table")
    table_data = [{
        'Key': p.key,
        'Title': p.title,
        'Year': p.date,
        'Disciplines': ', '.join(p.auto_tags.get('disciplines', [])),
        'Concepts': ', '.join(p.auto_tags.get('concepts', [])),
        'Citations': len(p.citations)
    } for p in library.papers]
    st.dataframe(table_data)
else:
    st.info("Please upload a Zotero JSON file to begin.") 