#!/usr/bin/env python3
"""
Matrix Tagger API Server
Provides REST API endpoints for the matrix tagging system
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from bibtex_matrix_tagger import BibTeXMatrixTagger
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global tagger instance
tagger = None

def load_tagger():
    """Load the trained tagger model."""
    global tagger
    if tagger is None:
        tagger = BibTeXMatrixTagger()
        try:
            tagger.load_models('matrix_tagger_models.pkl')
            logger.info("✓ Loaded trained models successfully")
        except FileNotFoundError:
            logger.warning("⚠️ No trained models found. Please train models first.")
            return False
    return True

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'matrix-tagger-api',
        'version': '1.0.0'
    })

@app.route('/api/tag', methods=['POST'])
def tag_paper():
    """Tag a single paper with matrix categories."""
    if not load_tagger():
        return jsonify({'error': 'Models not trained. Please train models first.'}), 400
    
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing required field: text'}), 400
        
        paper_text = data['text']
        title = data.get('title', '')
        abstract = data.get('abstract', '')
        publication_year = data.get('publication_year')  # New field for timeline restriction
        
        # Combine title and abstract if provided separately
        if title and abstract:
            full_text = f"{title} {abstract}"
        else:
            full_text = paper_text
        
        # Use publication date restriction if year is provided
        if publication_year:
            try:
                year = int(publication_year)
                predictions = tagger.predict_tags_with_publication_date_restriction(full_text, year)
                logger.info(f"Used publication date restriction for year {year}")
            except ValueError:
                logger.warning(f"Invalid publication year: {publication_year}, falling back to content-based prediction")
                predictions = tagger.predict_tags_simple(full_text)
        else:
            # Fall back to content-based prediction
            predictions = tagger.predict_tags_simple(full_text)
            logger.info("No publication year provided, using content-based timeline prediction")
        
        return jsonify({
            'success': True,
            'predictions': predictions,
            'input_text': full_text[:200] + '...' if len(full_text) > 200 else full_text,
            'timeline_restriction_applied': publication_year is not None
        })
        
    except Exception as e:
        logger.error(f"Error tagging paper: {str(e)}")
        return jsonify({'error': f'Tagging failed: {str(e)}'}), 500

@app.route('/api/tag/batch', methods=['POST'])
def tag_papers_batch():
    """Tag multiple papers in batch."""
    if not load_tagger():
        return jsonify({'error': 'Models not trained. Please train models first.'}), 400
    
    try:
        data = request.get_json()
        
        if not data or 'papers' not in data:
            return jsonify({'error': 'Missing required field: papers'}), 400
        
        papers = data['papers']
        results = []
        
        for i, paper in enumerate(papers):
            try:
                title = paper.get('title', '')
                abstract = paper.get('abstract', '')
                paper_id = paper.get('id', f'paper_{i}')
                publication_year = paper.get('publication_year')  # New field for timeline restriction
                
                # Combine title and abstract
                full_text = f"{title} {abstract}".strip()
                
                # Use publication date restriction if year is provided
                if publication_year:
                    try:
                        year = int(publication_year)
                        predictions = tagger.predict_tags_with_publication_date_restriction(full_text, year)
                        timeline_restricted = True
                    except ValueError:
                        logger.warning(f"Invalid publication year for paper {paper_id}: {publication_year}")
                        predictions = tagger.predict_tags_simple(full_text)
                        timeline_restricted = False
                else:
                    predictions = tagger.predict_tags_simple(full_text)
                    timeline_restricted = False
                
                results.append({
                    'id': paper_id,
                    'title': title,
                    'predictions': predictions,
                    'timeline_restriction_applied': timeline_restricted
                })
                
            except Exception as e:
                logger.error(f"Error tagging paper {paper_id}: {str(e)}")
                results.append({
                    'id': paper_id,
                    'error': f'Tagging failed: {str(e)}',
                    'timeline_restriction_applied': False
                })
        
        return jsonify({
            'success': True,
            'results': results,
            'total_papers': len(papers),
            'successful_tags': len([r for r in results if 'error' not in r])
        })
        
    except Exception as e:
        logger.error(f"Error in batch tagging: {str(e)}")
        return jsonify({'error': f'Batch tagging failed: {str(e)}'}), 500

@app.route('/api/train', methods=['POST'])
def train_models():
    """Train the models with provided tagged papers."""
    try:
        data = request.get_json()
        
        if not data or 'tagged_papers' not in data:
            return jsonify({'error': 'Missing required field: tagged_papers'}), 400
        
        # Initialize tagger
        global tagger
        tagger = BibTeXMatrixTagger()
        
        # Convert papers to the expected format
        tagged_entries = []
        for paper in data['tagged_papers']:
            entry = {
                'title': paper.get('title', ''),
                'abstract': paper.get('abstract', ''),
                'author': paper.get('author', ''),
                'year': paper.get('year', ''),
                'journal': paper.get('journal', ''),
                'matrix_tags': paper.get('tags', {})
            }
            tagged_entries.append(entry)
        
        # Train models
        tagger.train_models(tagged_entries)
        
        # Save models
        tagger.save_models('matrix_tagger_models.pkl')
        
        return jsonify({
            'success': True,
            'message': f'Models trained successfully with {len(tagged_entries)} papers',
            'papers_used': len(tagged_entries)
        })
        
    except Exception as e:
        logger.error(f"Error training models: {str(e)}")
        return jsonify({'error': f'Training failed: {str(e)}'}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get the available matrix categories."""
    if not load_tagger():
        return jsonify({'error': 'Tagger not initialized'}), 400
    
    return jsonify({
        'success': True,
        'categories': tagger.matrix_categories
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_papers():
    """Analyze the distribution of tags in papers."""
    try:
        data = request.get_json()
        
        if not data or 'papers' not in data:
            return jsonify({'error': 'Missing required field: papers'}), 400
        
        papers = data['papers']
        
        # Count tags by category
        tag_counts = {
            'time': {},
            'discipline': {},
            'memory_carrier': {},
            'concept_tags': {}
        }
        
        for paper in papers:
            tags = paper.get('tags', {})
            for category, tag_list in tags.items():
                if category in tag_counts:
                    for tag in tag_list:
                        tag_counts[category][tag] = tag_counts[category].get(tag, 0) + 1
        
        # Calculate statistics
        total_papers = len(papers)
        papers_with_tags = sum(1 for paper in papers if paper.get('tags'))
        
        return jsonify({
            'success': True,
            'statistics': {
                'total_papers': total_papers,
                'papers_with_tags': papers_with_tags,
                'tag_distribution': tag_counts
            }
        })
        
    except Exception as e:
        logger.error(f"Error analyzing papers: {str(e)}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/export/bibtex', methods=['POST'])
def export_bibtex():
    """Export tagged papers to BibTeX format."""
    try:
        data = request.get_json()
        
        if not data or 'papers' not in data:
            return jsonify({'error': 'Missing required field: papers'}), 400
        
        papers = data['papers']
        bibtex_content = []
        
        for paper in papers:
            # Create keywords string from tags
            all_tags = []
            for category, tags in paper.get('tags', {}).items():
                all_tags.extend(tags)
            
            keywords_str = ', '.join(all_tags) if all_tags else ''
            
            # Create BibTeX entry
            entry_lines = [f"@article{{{paper.get('id', 'paper')},"]
            entry_lines.append(f"  title = {{{paper.get('title', '')}}},")
            
            if paper.get('author'):
                entry_lines.append(f"  author = {{{paper.get('author')}}},")
            if paper.get('year'):
                entry_lines.append(f"  year = {{{paper.get('year')}}},")
            if paper.get('journal'):
                entry_lines.append(f"  journal = {{{paper.get('journal')}}},")
            if paper.get('abstract'):
                entry_lines.append(f"  abstract = {{{paper.get('abstract')}}},")
            if keywords_str:
                entry_lines.append(f"  keywords = {{{keywords_str}}},")
            
            entry_lines.append("}")
            bibtex_content.append('\n'.join(entry_lines))
        
        return jsonify({
            'success': True,
            'bibtex': '\n\n'.join(bibtex_content),
            'papers_exported': len(papers)
        })
        
    except Exception as e:
        logger.error(f"Error exporting BibTeX: {str(e)}")
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

if __name__ == '__main__':
    # Load models on startup
    load_tagger()
    
    # Run the server
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 