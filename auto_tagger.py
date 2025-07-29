#!/usr/bin/env python3
"""
Auto Tagger - Predicts tags for papers based on title and abstract
"""

import re
from typing import List, Dict
from collections import Counter

class AutoTagger:
    """Simple rule-based auto-tagger for academic papers."""
    
    def __init__(self):
        # Define tag categories and keywords
        self.tag_categories = {
            'memory_studies': [
                'memory', 'collective memory', 'cosmopolitan memory', 'global memory',
                'holocaust', 'remembering', 'forgetting', 'memorialization'
            ],
            'sociology': [
                'sociology', 'social theory', 'social memory', 'collective identity',
                'social construction', 'cultural memory', 'national memory'
            ],
            'political_science': [
                'politics', 'political', 'citizenship', 'cosmopolitan', 'nationalism',
                'solidarity', 'human rights', 'cultural rights', 'minority rights'
            ],
            'history': [
                'history', 'historical', 'past', 'historical memory', 'commemoration',
                'historical consciousness', 'temporal', 'chronological'
            ],
            'psychology': [
                'psychology', 'psychological', 'cognitive', 'mental', 'individual memory',
                'memory processes', 'cognitive psychology', 'mental processes'
            ],
            'philosophy': [
                'philosophy', 'philosophical', 'ethics', 'moral', 'value', 'theoretical',
                'epistemology', 'ontology', 'hermeneutics'
            ],
            'cultural_studies': [
                'culture', 'cultural', 'identity', 'representation', 'discourse',
                'cultural studies', 'cultural analysis', 'symbolic'
            ],
            'media_studies': [
                'media', 'communication', 'journalism', 'broadcasting', 'digital media',
                'social media', 'mass communication', 'media representation'
            ],
            'globalization': [
                'global', 'globalization', 'transnational', 'international', 'cosmopolitan',
                'global citizenship', 'world society', 'international relations'
            ],
            'research_methods': [
                'methodology', 'method', 'theoretical', 'empirical', 'qualitative',
                'quantitative', 'case study', 'analysis', 'framework'
            ]
        }
        
        # Common academic terms
        self.academic_terms = [
            'methodology', 'framework', 'model', 'theory', 'hypothesis',
            'empirical', 'theoretical', 'practical', 'implementation',
            'evaluation', 'assessment', 'analysis', 'synthesis', 'approach',
            'perspective', 'conceptualization', 'understanding'
        ]
        
        # Specific keyword patterns from your papers
        self.specific_keywords = {
            'CT': 'content_type',  # Content Type
            'D': 'discipline',      # Discipline
            'M': 'method',          # Method
            'T': 'type'            # Type
        }
    
    def predict_tags(self, title: str, abstract: str = '', keywords: List[str] = None) -> List[str]:
        """Predict tags for a paper based on title, abstract, and keywords."""
        # Combine title and abstract for analysis
        text = f"{title} {abstract}".lower()
        
        tags = []
        
        # Check each category
        for category, keywords_list in self.tag_categories.items():
            for keyword in keywords_list:
                if keyword.lower() in text:
                    tags.append(category)
                    break  # Only add category once
        
        # Add specific academic terms found
        for term in self.academic_terms:
            if term.lower() in text:
                tags.append(term)
        
        # Add domain-specific tags based on content
        domain_tags = self._extract_domain_tags(text)
        tags.extend(domain_tags)
        
        # Process specific keywords if provided
        if keywords:
            specific_tags = self._process_specific_keywords(keywords)
            tags.extend(specific_tags)
        
        # Remove duplicates and return
        return list(set(tags))
    
    def _extract_domain_tags(self, text: str) -> List[str]:
        """Extract domain-specific tags from text."""
        tags = []
        
        # Memory and identity
        if any(word in text for word in ['identity', 'identification', 'self']):
            tags.append('identity_studies')
        if any(word in text for word in ['trauma', 'traumatic', 'suffering']):
            tags.append('trauma_studies')
        if any(word in text for word in ['narrative', 'story', 'storytelling']):
            tags.append('narrative_studies')
        
        # Research methods
        if any(word in text for word in ['survey', 'questionnaire', 'interview']):
            tags.append('survey_research')
        if any(word in text for word in ['experiment', 'trial', 'randomized']):
            tags.append('experimental')
        if any(word in text for word in ['case study', 'case analysis']):
            tags.append('case_study')
        if any(word in text for word in ['comparative', 'comparison']):
            tags.append('comparative_analysis')
        
        # Data types
        if any(word in text for word in ['time series', 'temporal', 'longitudinal']):
            tags.append('time_series')
        if any(word in text for word in ['image', 'visual', 'picture', 'photo']):
            tags.append('image_analysis')
        if any(word in text for word in ['text', 'document', 'corpus', 'language']):
            tags.append('text_analysis')
        
        # Application domains
        if any(word in text for word in ['education', 'learning', 'student', 'pedagogy']):
            tags.append('education')
        if any(word in text for word in ['museum', 'exhibition', 'curation']):
            tags.append('museum_studies')
        if any(word in text for word in ['archive', 'archival', 'documentation']):
            tags.append('archival_studies')
        
        return tags
    
    def _process_specific_keywords(self, keywords: List[str]) -> List[str]:
        """Process specific keywords from the papers."""
        tags = []
        
        for keyword in keywords:
            keyword_upper = keyword.upper()
            
            # Process content types (CT)
            if keyword_upper.startswith('CT'):
                content_type = keyword_upper[2:]  # Remove 'CT' prefix
                tags.append(f'content_type_{content_type.lower()}')
            
            # Process disciplines (D)
            elif keyword_upper.startswith('D'):
                discipline = keyword_upper[1:]  # Remove 'D' prefix
                tags.append(f'discipline_{discipline.lower()}')
            
            # Process methods (M)
            elif keyword_upper.startswith('M'):
                method = keyword_upper[1:]  # Remove 'M' prefix
                tags.append(f'method_{method.lower()}')
            
            # Process types (T)
            elif keyword_upper.startswith('T'):
                type_code = keyword_upper[1:]  # Remove 'T' prefix
                tags.append(f'type_{type_code.lower()}')
            
            # Add the original keyword as well
            tags.append(keyword.lower())
        
        return tags
    
    def get_tag_statistics(self, papers: List[Dict]) -> Dict:
        """Get statistics about tags across papers."""
        all_tags = []
        for paper in papers:
            all_tags.extend(paper.get('tags', []))
        
        tag_counts = Counter(all_tags)
        
        return {
            'total_papers': len(papers),
            'unique_tags': len(set(all_tags)),
            'tag_frequency': dict(tag_counts.most_common()),
            'most_common_tags': tag_counts.most_common(10)
        }