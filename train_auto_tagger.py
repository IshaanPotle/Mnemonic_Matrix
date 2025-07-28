import json
from zotero_import import import_zotero_json
from enhanced_auto_tagger import EnhancedMnemonicTagger
from data_models import Paper
import os

def load_training_data(json_path):
    """Load the 8 labeled papers with their true tags"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    training_papers = []
    for item in data.get('items', []):
        # Create paper object
        from zotero_import import parse_authors, parse_citations
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
        
        # Add true tags from the labeled data
        paper.true_tags = {
            'disciplines': item.get('true_disciplines', []),
            'memory_carriers': item.get('true_memory_carriers', []),
            'concepts': item.get('true_concepts', []),
            'methods': item.get('true_methods', []),
            'time': item.get('true_time', [])
        }
        
        training_papers.append(paper)
    
    return training_papers

def evaluate_model(tagger, test_papers):
    """Evaluate the trained model on test papers"""
    print("\n=== Model Evaluation ===")
    
    total_papers = len(test_papers)
    correct_predictions = {
        'disciplines': 0,
        'memory_carriers': 0,
        'concepts': 0,
        'methods': 0
    }
    
    for paper in test_papers:
        predicted_tags, scores = tagger.categorize(paper)
        
        # Compare with true tags
        for category in ['disciplines', 'memory_carriers', 'concepts', 'methods']:
            if hasattr(paper, 'true_tags') and category in paper.true_tags:
                true_tags = set(paper.true_tags[category])
                predicted_tags_set = set(predicted_tags[category])
                
                # Check if prediction is correct (exact match for now)
                if true_tags == predicted_tags_set:
                    correct_predictions[category] += 1
    
    # Calculate accuracy
    for category in correct_predictions:
        accuracy = correct_predictions[category] / total_papers
        print(f"{category.capitalize()} Accuracy: {accuracy:.3f} ({correct_predictions[category]}/{total_papers})")
    
    return correct_predictions

def main():
    print("=== Enhanced Auto-Tagger Training ===")
    
    # Check if training data exists
    training_data_path = "training_papers.json"
    if not os.path.exists(training_data_path):
        print(f"Training data file '{training_data_path}' not found.")
        print("Please create a JSON file with your 8 labeled papers in this format:")
        print("""
{
  "items": [
    {
      "key": "PAPER1",
      "title": "Paper Title",
      "creators": [{"firstName": "Author", "lastName": "Name"}],
      "date": "2020",
      "itemType": "journalArticle",
      "abstract": "Paper abstract...",
      "tags": [],
      "collections": [],
      "true_disciplines": ["DSOC", "DHIS"],
      "true_memory_carriers": ["MCLI"],
      "true_concepts": ["cultural_memory"],
      "true_methods": ["MEARC"],
      "true_time": ["T5"]
    }
  ]
}
        """)
        return
    
    # Load training data
    print("Loading training data...")
    training_papers = load_training_data(training_data_path)
    print(f"Loaded {len(training_papers)} training papers")
    
    # Create and train the enhanced tagger
    print("\nTraining enhanced auto-tagger...")
    tagger = EnhancedMnemonicTagger(training_papers)
    tagger.train_classifiers()
    
    # Save the trained model
    model_path = "trained_auto_tagger.joblib"
    tagger.save_model(model_path)
    
    # Test on training data (for demonstration)
    print("\n=== Testing on Training Data ===")
    for i, paper in enumerate(training_papers):
        predicted_tags, scores = tagger.categorize(paper)
        print(f"\nPaper {i+1}: {paper.title}")
        print(f"True tags: {paper.true_tags}")
        print(f"Predicted tags: {predicted_tags}")
        print(f"Confidence scores: {scores}")
    
    # Evaluate model
    evaluate_model(tagger, training_papers)
    
    print(f"\nModel saved to {model_path}")
    print("You can now use this trained model for the remaining 410+ papers!")

if __name__ == "__main__":
    main() 