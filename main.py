import argparse
from zotero_import import import_zotero_json
from auto_tagger import MnemonicTagger
from network_analysis import CitationNetwork

def main():
    parser = argparse.ArgumentParser(description="Mnemonic Matrix System - Phase 1+2+3 Demo")
    parser.add_argument('--import-json', type=str, help='Path to Zotero JSON file to import')
    args = parser.parse_args()

    if args.import_json:
        library = import_zotero_json(args.import_json)
        print(f"Imported {len(library.papers)} papers:")
        tagger = MnemonicTagger()
        for paper in library.papers:
            tags, scores = tagger.categorize(paper)
            print(f"\n- {paper.title} ({paper.key}) by {[str(a) for a in paper.creators]}")
            print(f"  Auto-Tags: {tags}")
            print(f"  Confidence Scores: {scores}")
        # Network analysis
        print("\nCitation Network Analysis:")
        network = CitationNetwork(library)
        print("Most Cited Papers:")
        for key, deg in network.most_cited():
            print(f"  {key}: {deg} citations")
        print("\nCitation Counts (in-degree, out-degree):")
        for key, (in_deg, out_deg) in network.citation_counts().items():
            print(f"  {key}: in={in_deg}, out={out_deg}")
    else:
        print("Please provide --import-json <path> to import a Zotero JSON file.")

if __name__ == "__main__":
    main() 