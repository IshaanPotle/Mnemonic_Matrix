#!/usr/bin/env python3
"""
BibTeX Processor - Parses BibTeX files and extracts paper information
"""

import re
from typing import List, Dict
from pathlib import Path

class BibTeXProcessor:
    """Processes BibTeX files and extracts structured paper data."""
    
    def __init__(self):
        # Updated pattern to handle the specific format in training_papers.bib
        # This format has @articletitle = {title}, instead of @article{key, title = {title}
        self.entry_pattern = r'@(\w+)\s*=\s*\{([^}]*)\}'
        # Field pattern for standard BibTeX format (as fallback)
        self.standard_entry_pattern = r'@(\w+)\s*\{\s*([^,]+)\s*,(.*?)(?=@\w+\s*\{|$)'
        # Simple field pattern - we'll handle nested braces manually
        self.field_pattern = r'(\w+)\s*=\s*\{'
    
    def parse_bibtex(self, file_path: str) -> List[Dict]:
        """Parse a BibTeX file and extract paper information."""
        # Try different encodings to handle various file formats
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        content = None
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            raise Exception(f"Error reading BibTeX file: Could not decode with any of the attempted encodings: {encodings}")
        
        # Use standard format parser since the file uses @article{key, format
        papers = self._parse_standard_format(content)
        
        return papers
    
    def _parse_specific_format(self, content: str) -> List[Dict]:
        """Parse the specific format used in training_papers.bib."""
        papers = []
        
        # Split content into sections by looking for @articletitle patterns
        sections = re.split(r'(?=@articletitle)', content)
        
        for section in sections:
            if not section.strip():
                continue
                
            # Extract all fields from this section
            fields = self._extract_fields_with_nested_braces(section)
            
            if not fields:
                continue
                
            paper = {
                'id': f"paper_{len(papers)+1}",
                'type': 'article',
                'title': '',
                'authors': [],
                'abstract': '',
                'year': '',
                'journal': '',
                'volume': '',
                'pages': '',
                'doi': '',
                'url': '',
                'keywords': [],
                'issn': '',
                'language': '',
                'month': '',
                'shorttitle': '',
                'urldate': '',
                'copyright': ''
            }
            
            # Process fields
            for field_name, field_value in fields:
                field_name = field_name.lower().strip()
                field_value = field_value.strip()
                
                if field_name == 'articletitle':
                    paper['title'] = self._clean_field_value(field_value)
                elif field_name in ['author', 'authors']:
                    paper['authors'] = self._parse_authors(field_value)
                elif field_name == 'abstract':
                    paper['abstract'] = self._clean_field_value(field_value)
                elif field_name == 'year':
                    paper['year'] = field_value
                elif field_name in ['journal', 'booktitle']:
                    paper['journal'] = self._clean_field_value(field_value)
                elif field_name == 'volume':
                    paper['volume'] = field_value
                elif field_name == 'pages':
                    paper['pages'] = field_value
                elif field_name == 'doi':
                    paper['doi'] = field_value
                elif field_name == 'url':
                    paper['url'] = field_value
                elif field_name in ['keywords', 'keyword']:
                    paper['keywords'] = self._parse_keywords(field_value)
                elif field_name == 'issn':
                    paper['issn'] = field_value
                elif field_name == 'language':
                    paper['language'] = field_value
                elif field_name == 'month':
                    paper['month'] = field_value
                elif field_name == 'shorttitle':
                    paper['shorttitle'] = self._clean_field_value(field_value)
                elif field_name == 'urldate':
                    paper['urldate'] = field_value
                elif field_name == 'copyright':
                    paper['copyright'] = field_value
            
            # Only add if we have a title
            if paper['title']:
                papers.append(paper)
        
        return papers
    
    def _parse_standard_format(self, content: str) -> List[Dict]:
        """Parse standard BibTeX format as fallback."""
        entries = re.findall(self.standard_entry_pattern, content, re.DOTALL | re.IGNORECASE)
        
        papers = []
        for entry_type, entry_key, entry_content in entries:
            if entry_type.lower() in ['article', 'inproceedings', 'conference', 'book', 'incollection']:
                paper = self._parse_entry(entry_type, entry_key, entry_content)
                if paper:
                    papers.append(paper)
        
        return papers
    
    def _parse_entry(self, entry_type: str, entry_key: str, content: str) -> Dict:
        """Parse a single BibTeX entry."""
        # Extract fields with the new method
        fields = self._extract_fields_with_nested_braces(content)
        
        paper = {
            'id': entry_key.strip(),
            'type': entry_type.lower(),
            'title': '',
            'authors': [],
            'abstract': '',
            'year': '',
            'journal': '',
            'volume': '',
            'pages': '',
            'doi': '',
            'url': '',
            'keywords': [],
            'issn': '',
            'language': '',
            'month': '',
            'shorttitle': '',
            'urldate': '',
            'copyright': ''
        }
        
        # Process fields
        for field_name, field_value in fields:
            field_name = field_name.lower().strip()
            field_value = field_value.strip()
            
            if field_name == 'title':
                paper['title'] = self._clean_field_value(field_value)
            elif field_name in ['author', 'authors']:
                paper['authors'] = self._parse_authors(field_value)
            elif field_name == 'abstract':
                paper['abstract'] = self._clean_field_value(field_value)
            elif field_name == 'year':
                paper['year'] = field_value
            elif field_name in ['journal', 'booktitle']:
                paper['journal'] = self._clean_field_value(field_value)
            elif field_name == 'volume':
                paper['volume'] = field_value
            elif field_name == 'pages':
                paper['pages'] = field_value
            elif field_name == 'doi':
                paper['doi'] = field_value
            elif field_name == 'url':
                paper['url'] = field_value
            elif field_name in ['keywords', 'keyword']:
                paper['keywords'] = self._parse_keywords(field_value)
            elif field_name == 'issn':
                paper['issn'] = field_value
            elif field_name == 'language':
                paper['language'] = field_value
            elif field_name == 'month':
                paper['month'] = field_value
            elif field_name == 'shorttitle':
                paper['shorttitle'] = self._clean_field_value(field_value)
            elif field_name == 'urldate':
                paper['urldate'] = field_value
            elif field_name == 'copyright':
                paper['copyright'] = field_value
        
        return paper
    
    def _clean_field_value(self, value: str) -> str:
        """Clean and normalize field values."""
        if not value:
            return ""
            
        # Remove extra whitespace and newlines
        value = re.sub(r'\s+', ' ', value.strip())
        
        # Handle LaTeX commands and formatting
        # Remove LaTeX commands with arguments like \text{word} -> word
        value = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', value)
        # Remove LaTeX commands without arguments like \textbf
        value = re.sub(r'\\[a-zA-Z]+', '', value)
        
        # Handle special LaTeX formatting - remove single curly braces used for grouping
        # This is the key fix for titles like "Collective {Memory} in a {Global} {Age}"
        value = re.sub(r'\{([^}]*)\}', r'\1', value)
        
        # Remove any remaining LaTeX commands
        value = re.sub(r'\\[a-zA-Z]+', '', value)
        
        # Clean up any remaining artifacts
        value = re.sub(r'\s+', ' ', value)  # Multiple spaces to single space
        value = value.strip()
        
        return value
    
    def _parse_authors(self, authors_str: str) -> List[str]:
        """Parse author string into list of authors."""
        if not authors_str:
            return []
        
        # Split by 'and' or '&'
        authors = re.split(r'\s+and\s+|\s*&\s*', authors_str, flags=re.IGNORECASE)
        
        # Clean each author name
        cleaned_authors = []
        for author in authors:
            author = self._clean_field_value(author)
            if author:
                cleaned_authors.append(author)
        
        return cleaned_authors
    
    def _parse_keywords(self, keywords_str: str) -> List[str]:
        """Parse keywords string into list of keywords."""
        if not keywords_str:
            return []
        
        # Split by common separators
        keywords = re.split(r'[,;]', keywords_str)
        
        # Clean each keyword
        cleaned_keywords = []
        for keyword in keywords:
            keyword = self._clean_field_value(keyword)
            if keyword:
                cleaned_keywords.append(keyword)
        
        return cleaned_keywords
    
    def validate_paper(self, paper: Dict) -> bool:
        """Validate that a paper has required fields."""
        return bool(paper.get('title') and paper.get('authors'))

    def _extract_fields_with_nested_braces(self, content: str) -> List[tuple]:
        """Extract fields handling nested braces properly."""
        fields = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if '=' not in line or '{' not in line:
                continue
                
            # Find field name
            match = re.match(r'(\w+)\s*=\s*\{', line)
            if not match:
                continue
                
            field_name = match.group(1)
            
            # Extract the value by counting braces
            brace_count = 0
            value_start = line.find('{') + 1
            value = ""
            
            # Start with the rest of this line
            remaining = line[value_start:]
            
            for char in remaining:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    if brace_count == 0:
                        break
                    brace_count -= 1
                value += char
            
            # If we didn't find the closing brace, continue to next lines
            if brace_count > 0:
                for next_line in lines[lines.index(line) + 1:]:
                    for char in next_line:
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            if brace_count == 0:
                                break
                            brace_count -= 1
                        value += char
                    if brace_count == 0:
                        break
            
            if value:
                fields.append((field_name, value))
        
        return fields