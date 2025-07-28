import json
from zotero_import import import_zotero_json
from enhanced_auto_tagger import EnhancedMnemonicTagger
import os

def apply_trained_tagger(input_json_path, output_json_path, model_path="trained_auto_tagger.joblib"):
    """Apply trained auto-tagger to papers and save results"""
    
    # Load the trained model
    tagger = EnhancedMnemonicTagger()
    if not tagger.load_model(model_path):
        print(f"Trained model not found at {model_path}")
        print("Please run train_auto_tagger.py first to train the model.")
        return
    
    # Load papers
    print(f"Loading papers from {input_json_path}...")
    library = import_zotero_json(input_json_path)
    print(f"Loaded {len(library.papers)} papers")
    
    # Apply auto-tagging
    print("Applying auto-tagging...")
    results = []
    
    for i, paper in enumerate(library.papers):
        if i % 50 == 0:
            print(f"Processing paper {i+1}/{len(library.papers)}...")
        
        # Get predictions
        predicted_tags, confidence_scores = tagger.categorize(paper)
        
        # Store results
        paper.auto_tags = predicted_tags
        paper.confidence_scores = confidence_scores
        
        # Prepare output data
        result_item = {
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
            'citations': [c.cited_key for c in paper.citations],
            # Auto-generated tags
            'auto_disciplines': predicted_tags['disciplines'],
            'auto_memory_carriers': predicted_tags['memory_carriers'],
            'auto_concepts': predicted_tags['concepts'],
            'auto_methods': predicted_tags['methods'],
            'auto_time': predicted_tags['time'],
            # Confidence scores
            'confidence_disciplines': confidence_scores.get('disciplines', 0.0),
            'confidence_concepts': confidence_scores.get('concepts', 0.0),
            'confidence_memory_carriers': confidence_scores.get('memory_carriers', 0.0),
            'confidence_methods': confidence_scores.get('methods', 0.0)
        }
        results.append(result_item)
    
    # Save results
    output_data = {'items': results}
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"Results saved to {output_json_path}")
    
    # Print summary statistics
    print("\n=== Auto-Tagging Summary ===")
    total_papers = len(results)
    
    # Count papers with each type of tag
    discipline_count = sum(1 for r in results if r['auto_disciplines'])
    concept_count = sum(1 for r in results if r['auto_concepts'])
    carrier_count = sum(1 for r in results if r['auto_memory_carriers'])
    method_count = sum(1 for r in results if r['auto_methods'])
    
    print(f"Papers with discipline tags: {discipline_count}/{total_papers} ({discipline_count/total_papers:.1%})")
    print(f"Papers with concept tags: {concept_count}/{total_papers} ({concept_count/total_papers:.1%})")
    print(f"Papers with memory carrier tags: {carrier_count}/{total_papers} ({carrier_count/total_papers:.1%})")
    print(f"Papers with method tags: {method_count}/{total_papers} ({method_count/total_papers:.1%})")
    
    # Average confidence scores
    avg_discipline_conf = sum(r['confidence_disciplines'] for r in results) / total_papers
    avg_concept_conf = sum(r['confidence_concepts'] for r in results) / total_papers
    avg_carrier_conf = sum(r['confidence_memory_carriers'] for r in results) / total_papers
    avg_method_conf = sum(r['confidence_methods'] for r in results) / total_papers
    
    print(f"\nAverage confidence scores:")
    print(f"Disciplines: {avg_discipline_conf:.3f}")
    print(f"Concepts: {avg_concept_conf:.3f}")
    print(f"Memory Carriers: {avg_carrier_conf:.3f}")
    print(f"Methods: {avg_method_conf:.3f}")

def main():
    print("=== Apply Trained Auto-Tagger ===")
    
    # Check for input file
    input_file = "papers_to_tag.json"  # Your 410+ papers
    if not os.path.exists(input_file):
        print(f"Input file '{input_file}' not found.")
        print("Please provide your papers in JSON format.")
        return
    
    # Check for trained model
    model_file = "trained_auto_tagger.joblib"
    if not os.path.exists(model_file):
        print(f"Trained model '{model_file}' not found.")
        print("Please run train_auto_tagger.py first to train the model.")
        return
    
    # Apply tagging
    output_file = "tagged_papers.json"
    apply_trained_tagger(input_file, output_file, model_file)
    
    print(f"\nAuto-tagging complete! Results saved to {output_file}")

if __name__ == "__main__":
    main() 