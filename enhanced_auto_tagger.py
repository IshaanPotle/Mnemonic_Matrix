import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score
from sklearn.metrics import classification_report
from config import TIME_PERIODS, DISCIPLINES, MEMORY_CARRIERS, KEY_CONCEPTS, METHODS
import joblib
import os

class EnhancedMnemonicTagger:
    def __init__(self, training_papers=None):
        self.training_papers = training_papers or []
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            stop_words='english',
            min_df=2
        )
        self.classifiers = {}
        self.is_trained = False
        
    def prepare_text_features(self, paper):
        """Extract and combine text features from paper"""
        text_parts = []
        if paper.title:
            text_parts.append(paper.title)
        if paper.abstract:
            text_parts.append(paper.abstract)
        if paper.publication_title:
            text_parts.append(paper.publication_title)
        if paper.tags:
            text_parts.append(' '.join(paper.tags))
        if paper.collections:
            text_parts.append(' '.join(paper.collections))
        
        return ' '.join(text_parts)
    
    def extract_year(self, paper):
        """Extract year from paper date"""
        if paper.date:
            match = re.search(r"(\d{4})", paper.date)
            if match:
                return int(match.group(1))
        return None
    
    def get_time_period(self, year):
        """Get time period based on year"""
        if year is None:
            return "T5"  # Default to recent
        if year < 1860:
            return "T1"
        elif year < 1950:
            return "T2"
        elif year < 1990:
            return "T3"
        elif year < 2000:
            return "T4"
        else:
            return "T5"
    
    def train_classifiers(self):
        """Train ML classifiers on labeled data"""
        if not self.training_papers:
            print("No training data provided. Using rule-based approach only.")
            return
        
        # Prepare training data
        texts = [self.prepare_text_features(paper) for paper in self.training_papers]
        X = self.vectorizer.fit_transform(texts)
        
        # Train classifiers for each category
        categories = ['disciplines', 'memory_carriers', 'concepts', 'methods']
        
        for category in categories:
            # Prepare labels for this category
            y = []
            for paper in self.training_papers:
                if hasattr(paper, 'true_tags') and category in paper.true_tags:
                    y.append(1)  # Has this category
                else:
                    y.append(0)  # Doesn't have this category
            
            if len(set(y)) < 2:  # Need both positive and negative examples
                print(f"Warning: Insufficient training data for {category}")
                continue
            
            # Train ensemble of classifiers
            classifiers = {
                'rf': RandomForestClassifier(n_estimators=100, random_state=42),
                'nb': MultinomialNB(),
                'svm': SVC(kernel='linear', probability=True, random_state=42)
            }
            
            best_score = 0
            best_classifier = None
            
            for name, clf in classifiers.items():
                try:
                    scores = cross_val_score(clf, X, y, cv=min(3, len(self.training_papers)), scoring='f1')
                    avg_score = scores.mean()
                    if avg_score > best_score:
                        best_score = avg_score
                        best_classifier = clf
                except:
                    continue
            
            if best_classifier:
                best_classifier.fit(X, y)
                self.classifiers[category] = best_classifier
                print(f"Trained {category} classifier with F1 score: {best_score:.3f}")
        
        self.is_trained = True
    
    def predict_category(self, paper, category):
        """Predict if paper belongs to a category using trained classifier"""
        if category not in self.classifiers:
            return 0.0
        
        text = self.prepare_text_features(paper)
        X = self.vectorizer.transform([text])
        prob = self.classifiers[category].predict_proba(X)[0]
        return prob[1]  # Probability of positive class
    
    def categorize(self, paper):
        """Enhanced categorization using ML + rule-based approach"""
        text = f"{paper.title} {paper.abstract or ''}"
        tags = {"time": [], "disciplines": [], "memory_carriers": [], "concepts": [], "methods": []}
        scores = {"disciplines": 0.0, "concepts": 0.0, "memory_carriers": 0.0, "methods": 0.0}
        
        # Time period (rule-based, very reliable)
        year = self.extract_year(paper)
        time_period = self.get_time_period(year)
        tags["time"].append(time_period)
        
        # ML-based predictions for other categories
        if self.is_trained:
            for category in ['disciplines', 'memory_carriers', 'concepts', 'methods']:
                ml_score = self.predict_category(paper, category)
                
                # Combine ML prediction with rule-based
                rule_based_score = self._rule_based_score(paper, category, text)
                
                # Weighted combination (ML gets higher weight if trained)
                combined_score = 0.7 * ml_score + 0.3 * rule_based_score
                
                if combined_score > 0.5:  # Threshold for inclusion
                    if category == 'disciplines':
                        # For disciplines, we need to predict specific ones
                        predicted_disciplines = self._predict_specific_disciplines(paper, text)
                        tags["disciplines"] = predicted_disciplines
                    elif category == 'concepts':
                        predicted_concepts = self._predict_specific_concepts(paper, text)
                        tags["concepts"] = predicted_concepts
                    elif category == 'memory_carriers':
                        predicted_carriers = self._predict_specific_carriers(paper, text)
                        tags["memory_carriers"] = predicted_carriers
                    elif category == 'methods':
                        predicted_methods = self._predict_specific_methods(paper, text)
                        tags["methods"] = predicted_methods
                
                scores[category] = combined_score
        else:
            # Fallback to rule-based only
            self._rule_based_categorization(paper, text, tags, scores)
        
        return tags, scores
    
    def _rule_based_score(self, paper, category, text):
        """Calculate rule-based score for a category"""
        if category == 'disciplines':
            found = any(d.lower() in [t.lower() for t in paper.tags + paper.collections] 
                       or d.lower() in text.lower() for d in DISCIPLINES)
        elif category == 'concepts':
            found = any(c.replace('_', ' ') in text.lower() or c in text.lower() 
                       for c in KEY_CONCEPTS)
        elif category == 'memory_carriers':
            found = any(m.lower() in [t.lower() for t in paper.tags] 
                       or m.lower() in text.lower() for m in MEMORY_CARRIERS)
        elif category == 'methods':
            found = any(m.lower() in [t.lower() for t in paper.tags] 
                       or m.lower() in text.lower() for m in METHODS)
        else:
            found = False
        
        return 1.0 if found else 0.0
    
    def _predict_specific_disciplines(self, paper, text):
        """Predict specific disciplines using keyword matching"""
        found_disciplines = []
        for d in DISCIPLINES:
            if (d.lower() in [t.lower() for t in paper.tags + paper.collections] 
                or d.lower() in text.lower()):
                found_disciplines.append(d)
        return found_disciplines
    
    def _predict_specific_concepts(self, paper, text):
        """Predict specific concepts using keyword matching"""
        found_concepts = []
        for c in KEY_CONCEPTS:
            if c.replace('_', ' ') in text.lower() or c in text.lower():
                found_concepts.append(c)
        return found_concepts
    
    def _predict_specific_carriers(self, paper, text):
        """Predict specific memory carriers using keyword matching"""
        found_carriers = []
        for m in MEMORY_CARRIERS:
            if (m.lower() in [t.lower() for t in paper.tags] 
                or m.lower() in text.lower()):
                found_carriers.append(m)
        return found_carriers
    
    def _predict_specific_methods(self, paper, text):
        """Predict specific methods using keyword matching"""
        found_methods = []
        for m in METHODS:
            if (m.lower() in [t.lower() for t in paper.tags] 
                or m.lower() in text.lower()):
                found_methods.append(m)
        return found_methods
    
    def _rule_based_categorization(self, paper, text, tags, scores):
        """Fallback rule-based categorization"""
        # Disciplines
        found_disciplines = self._predict_specific_disciplines(paper, text)
        tags["disciplines"] = found_disciplines
        scores["disciplines"] = 1.0 if found_disciplines else 0.0
        
        # Concepts
        found_concepts = self._predict_specific_concepts(paper, text)
        tags["concepts"] = found_concepts
        scores["concepts"] = 1.0 if found_concepts else 0.0
        
        # Memory Carriers
        found_carriers = self._predict_specific_carriers(paper, text)
        tags["memory_carriers"] = found_carriers
        scores["memory_carriers"] = 1.0 if found_carriers else 0.0
        
        # Methods
        found_methods = self._predict_specific_methods(paper, text)
        tags["methods"] = found_methods
        scores["methods"] = 1.0 if found_methods else 0.0
    
    def save_model(self, filepath):
        """Save trained model to file"""
        if self.is_trained:
            model_data = {
                'vectorizer': self.vectorizer,
                'classifiers': self.classifiers,
                'is_trained': self.is_trained
            }
            joblib.dump(model_data, filepath)
            print(f"Model saved to {filepath}")
    
    def load_model(self, filepath):
        """Load trained model from file"""
        if os.path.exists(filepath):
            model_data = joblib.load(filepath)
            self.vectorizer = model_data['vectorizer']
            self.classifiers = model_data['classifiers']
            self.is_trained = model_data['is_trained']
            print(f"Model loaded from {filepath}")
            return True
        return False 