#!/usr/bin/env python3
"""
Tag Untagged Papers - Batch tagging of untagged papers using trained ML models
"""

import json
import re
from bibtex_matrix_tagger import BibTeXMatrixTagger

def create_bibtex_entry(entry_data, predicted_tags):
    """Create a BibTeX entry with matrix tags."""
    # Extract basic fields
    entry_key = entry_data.get('entry_key', 'unknown')
    title = entry_data.get('title', 'Unknown Title')
    author = entry_data.get('author', 'Unknown Author')
    year = entry_data.get('year', 'Unknown Year')
    journal = entry_data.get('journal', 'Unknown Journal')
    abstract = entry_data.get('abstract', '')
    
    # Create keywords string with matrix tags
    all_tags = []
    for category, tags in predicted_tags.items():
        all_tags.extend(tags)
    
    keywords = ', '.join(all_tags) if all_tags else 'untagged'
    
    # Create BibTeX entry
    bibtex_entry = f"""@article{{{entry_key},
  title = {{{title}}},
  author = {{{author}}},
  year = {{{year}}},
  journal = {{{journal}}},
  abstract = {{{abstract}}},
  keywords = {{{keywords}}}
}}"""
    
    return bibtex_entry

def main():
    """Main function to tag untagged papers."""
    print("🔄 Loading matrix tagger...")
    tagger = BibTeXMatrixTagger()
    
    # Try to load existing models
    try:
        tagger.load_models('matrix_tagger_models.pkl')
        print("✅ Loaded existing trained models")
    except FileNotFoundError:
        print("❌ No trained models found. Please train models first.")
        return
    
    # Parse untagged papers
    print("📖 Parsing untagged papers...")
    untagged_entries = tagger.parse_bibtex_file('export-data.bib')
    
    if not untagged_entries:
        print("❌ No untagged papers found in export-data.bib")
        return
    
    print(f"📊 Found {len(untagged_entries)} untagged papers")
    
    # Tag each paper
    tagged_entries = []
    tag_statistics = {
        'time': {},
        'discipline': {},
        'memory_carrier': {},
        'concept_tags': {}
    }
    
    print("\n🏷️  Tagging papers...")
    for i, entry in enumerate(untagged_entries, 1):
        print(f"  Processing paper {i}/{len(untagged_entries)}: {entry.get('title', 'Unknown')[:50]}...")
        
        # Create text for prediction
        text = f"{entry.get('title', '')} {entry.get('abstract', '')}"
        
        # Predict tags
        predicted_tags = tagger.predict_tags_simple(text)
        
        # Update statistics
        for category, tags in predicted_tags.items():
            for tag in tags:
                if tag not in tag_statistics[category]:
                    tag_statistics[category][tag] = 0
                tag_statistics[category][tag] += 1
        
        # Create tagged entry
        tagged_entry = entry.copy()
        tagged_entry['matrix_tags'] = predicted_tags
        tagged_entry['predicted_tags'] = predicted_tags
        
        tagged_entries.append(tagged_entry)
    
    # Generate output files
    print("\n📝 Generating output files...")
    
    # Create BibTeX file with predicted tags
    bibtex_content = ""
    for entry in tagged_entries:
        bibtex_entry = create_bibtex_entry(entry, entry['predicted_tags'])
        bibtex_content += bibtex_entry + "\n\n"
    
    with open('tagged_papers_with_matrix_tags.bib', 'w', encoding='utf-8') as f:
        f.write(bibtex_content)
    
    # Create JSON summary
    json_summary = {
        'total_papers': len(tagged_entries),
        'tag_statistics': tag_statistics,
        'tagged_papers': []
    }
    
    for entry in tagged_entries:
        paper_summary = {
            'title': entry.get('title', 'Unknown'),
            'author': entry.get('author', 'Unknown'),
            'year': entry.get('year', 'Unknown'),
            'journal': entry.get('journal', 'Unknown'),
            'matrix_tags': entry['predicted_tags']
        }
        json_summary['tagged_papers'].append(paper_summary)
    
    with open('tagged_papers_summary.json', 'w', encoding='utf-8') as f:
        json.dump(json_summary, f, indent=2, ensure_ascii=False)
    
    # Print statistics
    print("\n📊 Tagging Statistics:")
    print(f"  Total papers tagged: {len(tagged_entries)}")
    
    for category, stats in tag_statistics.items():
        category_name = tagger.matrix_categories[category]['name']
        print(f"\n  {category_name}:")
        if stats:
            sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
            for tag, count in sorted_stats[:10]:  # Show top 10
                description = tagger.matrix_categories[category]['descriptions'].get(tag, '')
                print(f"    {tag}: {count} papers - {description}")
        else:
            print("    No tags predicted")
    
    print(f"\n✅ Tagging complete!")
    print(f"  📄 BibTeX file: tagged_papers_with_matrix_tags.bib")
    print(f"  📊 Summary file: tagged_papers_summary.json")

if __name__ == "__main__":
    main() 