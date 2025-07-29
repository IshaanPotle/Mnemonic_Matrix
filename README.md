# Mnemonic Matrix - BibTeX Processing System

A simple system for processing BibTeX files, auto-tagging papers, and generating visualizations.

## Workflow

1. **Upload BibTeX** → Parse paper information
2. **Auto-tag** → Apply intelligent tagging based on content
3. **Visualize** → Generate interactive HTML visualizations

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Usage

```bash
# Process a BibTeX file
python main.py path/to/your/papers.bib

# Process with statistics
python main.py path/to/your/papers.bib --stats

# Skip visualizations
python main.py path/to/your/papers.bib --no-viz
```

### Example

```bash
python main.py training_papers.bib --stats
```

## Output

The system generates:

- **`data/processed_papers.json`** - Processed papers with tags
- **`output/tag_network.html`** - Interactive tag network visualization
- **`output/tag_distribution.html`** - Tag frequency distribution
- **`output/paper_timeline.html`** - Papers over time
- **`output/paper_dashboard.html`** - Comprehensive paper overview

## Features

### BibTeX Processing
- Parses standard BibTeX format
- Extracts title, authors, abstract, year, journal, etc.
- Handles multiple entry types (article, inproceedings, book)

### Auto-tagging
- Rule-based tagging system
- Categorizes by research area (ML, CS, business, etc.)
- Identifies research methods and data types
- Detects application domains

### Visualizations
- **Tag Network**: Shows relationships between tags
- **Tag Distribution**: Frequency of different tags
- **Paper Timeline**: Papers published over time
- **Dashboard**: Comprehensive overview with statistics

## File Structure

```
Mnemonic Matrix/
├── main.py              # Main application
├── bibtex_processor.py  # BibTeX parsing
├── auto_tagger.py       # Auto-tagging logic
├── visualizer.py        # Visualization generation
├── requirements.txt     # Dependencies
├── data/               # Processed data
└── output/             # Generated visualizations
```

## Supported BibTeX Fields

- `title` - Paper title
- `author` - Authors (supports "and" and "&" separators)
- `abstract` - Abstract text
- `year` - Publication year
- `journal` / `booktitle` - Publication venue
- `volume` - Journal volume
- `pages` - Page numbers
- `doi` - Digital Object Identifier
- `url` - Paper URL
- `keywords` - Keywords (comma/semicolon separated)

## Auto-tagging Categories

- **Machine Learning**: AI, neural networks, deep learning, etc.
- **Data Science**: Analytics, big data, statistics, etc.
- **Computer Science**: Algorithms, programming, software engineering, etc.
- **Research Methods**: Experiments, surveys, case studies, etc.
- **Academic Fields**: Psychology, economics, education, etc.
- **Technology**: Blockchain, cloud computing, IoT, etc.
- **Business**: Management, marketing, finance, etc.

## Example Output

After processing, you'll get:

1. **JSON file** with structured paper data and tags
2. **Interactive visualizations** showing:
   - How tags relate to each other
   - Most common tags
   - Publication timeline
   - Paper summary dashboard

## Requirements

- Python 3.7+
- plotly (for visualizations)
- pandas (for data processing)

## License

This project is for academic research purposes.