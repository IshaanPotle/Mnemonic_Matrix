# Mnemonic Matrix Tagger

An open-source machine learning system for automatically tagging academic papers with matrix categories for memory studies research.

## 🎯 Overview

The Mnemonic Matrix Tagger is a sophisticated ML system that automatically categorizes academic papers into four matrix dimensions:

- **Time Periods** (T1-T5): Historical time periods from 400 BCE to present
- **Disciplines** (DSOC, DHIS, etc.): Academic disciplines and fields
- **Memory Carriers** (MCSO, MCLI, etc.): Media and forms of memory transmission
- **Concept Tags** (CTCollectiveMemory, etc.): Memory-related concepts and theories

## 🚀 Features

- **Multi-label Classification**: Predicts multiple tags across all four categories
- **BibTeX Integration**: Seamlessly works with BibTeX bibliography files
- **Few-shot Learning**: Trains effectively with minimal labeled data
- **Confidence Scoring**: Provides confidence levels for predictions
- **Batch Processing**: Handles large datasets efficiently
- **Export Options**: Multiple output formats (JSON, BibTeX, CSV)

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Quick Start
```bash
# Clone the repository
git clone https://github.com/yourusername/mnemonic-matrix-tagger.git
cd mnemonic-matrix-tagger

# Install dependencies
pip install -r requirements.txt

# Run the system
python bibtex_matrix_tagger.py
```

## 🛠️ Usage

### 1. Prepare Your Data

#### Tagged Papers (Training Data)
Create a BibTeX file with your manually tagged papers:
```bibtex
@article{example_2020,
    title = {Collective Memory in a Global Age},
    author = {Author, A.},
    year = {2020},
    abstract = {This paper examines...},
    keywords = {CTCollectiveMemory, DSOC, T4, MCME},
}
```

#### Untagged Papers (To Be Tagged)
Create a BibTeX file with papers you want to tag:
```bibtex
@article{untagged_2021,
    title = {Memory and Identity},
    author = {Author, B.},
    year = {2021},
    abstract = {This study explores...},
}
```

### 2. Train the Models

```python
from bibtex_matrix_tagger import BibTeXMatrixTagger

# Initialize the tagger
tagger = BibTeXMatrixTagger()

# Parse your tagged papers
tagged_entries = tagger.parse_bibtex_file('your_tagged_papers.bib')

# Train the models
tagger.train_models(tagged_entries)

# Save the trained models
tagger.save_models('trained_models.pkl')
```

### 3. Tag New Papers

```python
# Load trained models
tagger.load_models('trained_models.pkl')

# Parse untagged papers
untagged_entries = tagger.parse_bibtex_file('your_untagged_papers.bib')

# Tag each paper
for entry in untagged_entries:
    paper_text = f"{entry['title']} {entry.get('abstract', '')}"
    predictions = tagger.predict_tags_simple(paper_text)
    print(f"Paper: {entry['title']}")
    print(f"Tags: {predictions}")
```

### 4. Batch Processing

```bash
# Tag all papers in a BibTeX file
python tag_untagged_papers.py

# This will create:
# - tagged_papers_results.json (detailed results)
# - tagged_papers_output.bib (BibTeX with predicted tags)
```

## 📊 Matrix Categories

### Time Periods (T1-T5)
- **T1**: 400 BCE - 1859 (Ancient to Early Modern)
- **T2**: 1860 - 1949 (Modern Period)
- **T3**: 1950 - 1989 (Post-War Period)
- **T4**: 1990 - 2010 (Contemporary Period)
- **T5**: 2011 - Present (Digital Age)

### Disciplines (D-prefix)
- **DSOC**: Sociology
- **DHIS**: History
- **DLIT**: Literature
- **DPOL**: Political Science
- **DPSY**: Psychology
- **DANT**: Anthropology
- **DMED**: Media Studies
- **DPHI**: Philosophy
- And many more...

### Memory Carriers (MC-prefix)
- **MCSO**: Social Media
- **MCLI**: Literature
- **MCPH**: Photography
- **MCME**: Memory Scholars
- **MCMU**: Museums
- **MCC**: Commemorations
- And many more...

### Concept Tags (CT-prefix)
- **CTArchives**: Archives
- **CTCollectiveMemory**: Collective Memory
- **CTCulturalMemory**: Cultural Memory
- **CTGlobalMemory**: Global Memory
- **CTPostMemory**: Postmemory
- **CTTrauma**: Trauma Studies
- **CTCommunicativeMemory**: Communicative Memory
- **CTBanalMnemonics**: Banal Mnemonics
- **CTMemoryPolitics**: Memory Politics
- **CTTravellingMemory**: Travelling Memory
- **CTTransculturalMemory**: Transcultural Memory
- **CTDutyToRemember**: Duty to Remember
- **CTForgetting**: Forgetting
- **CTIdentity**: Identity
- **CTNationalMemory**: National Memory
- **CTHistoricalMemory**: Historical Memory
- **CTAutobiographicalMemory**: Autobiographical Memory
- **CTAgonisticMemory**: Agonistic Memory
- **CTAmnesia**: Amnesia
- **CTAestheticMemory**: Aesthetic Memory
- **CTCanons**: Canons
- **CTCulturalTrauma**: Cultural Trauma
- **CTCosmopolitanMemory**: Cosmopolitan Memory
- **CTCommemoration**: Commemoration
- **CTCatastrophicMemory**: Catastrophic Memory
- **CTCounterMemory**: Counter-Memory
- **CTDialogical**: Dialogical
- **CTDeclarativeMemory**: Declarative Memory
- **CTDigitalMemory**: Digital Memory
- **CTEngrams**: Engrams
- **CTEpisodicMemory**: Episodic Memory
- **CTExplicitMemory**: Explicit Memory
- **CTEntangledMemory**: Entangled Memory
- **CTFamilyMemory**: Family Memory
- **CTFlashbulbMemory**: Flashbulb Memory
- **CTFlashback**: Flashback
- **CTForgettingCurve**: Forgetting Curve
- **CTFalseMemory**: False Memory
- **CTGenreMemory**: Genre Memory
- **CTGlobitalMemory**: Globital Memory
- **CTGenerationalMemory**: Generational Memory
- **CTHeritage**: Heritage
- **CTHyperthymesia**: Hyperthymesia
- **CTImplicitMemory**: Implicit Memory
- **CTIntergenerationalTransmissions**: Intergenerational Transmissions
- **CTIconicMemory**: Iconic Memory
- **CTImaginativeReconstruction**: Imaginative Reconstruction
- **CTLongueDuree**: Longue Durée
- **CTMultidirectionalMemory**: Multidirectional Memory
- **CTMnemonicSecurity**: Mnemonic Security
- **CTMilieuDeMemoire**: Milieu de Mémoire
- **CTMemoryLaws**: Memory Laws
- **CTMnemohistory**: Mnemohistory
- **CTMemoryConsolidation**: Memory Consolidation
- **CTMemoryRetrieval**: Memory Retrieval
- **CTMemoryEncoding**: Memory Encoding
- **CTMemoryStorage**: Memory Storage
- **CTMemoryTrace**: Memory Trace
- **CTMemorySpan**: Memory Span
- **CTMemoryDistortion**: Memory Distortion
- **CTMemoryAccuracy**: Memory Accuracy
- **CTMemoryBias**: Memory Bias
- **CTMemoryEnhancement**: Memory Enhancement
- **CTMemorySuppression**: Memory Suppression
- **CTMemorySchemas**: Memory Schemas
- **CTMnemonics**: Mnemonics
- **CTMnemonicCommunities**: Mnemonic Communities
- **CTMnemonicSocialization**: Mnemonic Socialization
- **CTMemoryEthics**: Memory Ethics
- **CTMemoryPractices**: Memory Practices
- **CTMnemonicStandoff**: Mnemonic Standoff
- **CTNonContemporaneity**: Non-Contemporaneity
- **CTOfficialMemory**: Official Memory
- **CTParticularism**: Particularism
- **CTPrivateMemory**: Private Memory
- **CTPublicMemory**: Public Memory
- **CTPathDependency**: Path-Dependency
- **CTProceduralMemory**: Procedural Memory
- **CTProstheticMemory**: Prosthetic Memory
- **CTPostColonialMemory**: Post-Colonial Memory
- **CTProspectiveMemory**: Prospective Memory
- **CTProfaneMemory**: Profane Memory
- **CTRealmsOfMemory**: Realms of Memory
- **CTRegret**: Regret
- **CTRestitution**: Restitution
- **CTReparations**: Reparations
- **CTRedress**: Redress
- **CTRepressedMemory**: Repressed Memory
- **CTRecoveredMemory**: Recovered Memory
- **CTRetrospectiveMemory**: Retrospective Memory
- **CTRevisionistMemory**: Revisionist Memory
- **CTReligiousMemory**: Religious Memory
- **CTSemanticMemory**: Semantic Memory
- **CTSocialFrameworks**: Social Frameworks
- **CTSlowMemory**: Slow Memory
- **CTSocialMemory**: Social Memory
- **CTScreenMemory**: Screen Memory
- **CTSensoryMemory**: Sensory Memory
- **CTSourceMemory**: Source Memory
- **CTSacredMemory**: Sacred Memory
- **CTTradition**: Tradition
- **CTTransnationalMemory**: Transnational Memory
- **CTTransoceanicMemory**: Transoceanic Memory
- **CTUniversalism**: Universalism
- **CTVernacularMemory**: Vernacular Memory
- **CTWorkingMemory**: Working Memory

## 🔧 Configuration

### Customizing Tag Categories

Edit the `matrix_categories` in `bibtex_matrix_tagger.py`:

```python
self.matrix_categories = {
    'time': ['T1', 'T2', 'T3', 'T4', 'T5'],
    'discipline': ['DSOC', 'DHIS', 'DLIT', ...],
    'memory_carrier': ['MCSO', 'MCLI', 'MCPH', ...],
    'concept_tags': ['CTCollectiveMemory', 'CTCulturalMemory', ...]
}
```

### Model Parameters

Adjust the ML model parameters in `train_models()`:

```python
model = MultiOutputClassifier(RandomForestClassifier(
    n_estimators=100,  # Number of trees
    random_state=42,    # For reproducibility
    max_depth=10        # Tree depth
))
```

## 📈 Performance

### Training Results
- **Accuracy**: 100% on training data (8 papers)
- **Multi-label Support**: Predicts multiple tags per category
- **Scalability**: Handles large datasets efficiently

### Sample Predictions
```
Paper: "Collective Memory and National Identity"
Predicted Tags:
- Time: T4 (1990-2010)
- Memory Carrier: MCME (Memory Scholars)
- Concept Tags: CTCollectiveMemory, CTCulturalHistory
```

## 🎨 Integration with Visualization

The tagged papers can be integrated with the Mnemonic Matrix visualization system:

```python
# Load tagged results
with open('tagged_papers_results.json', 'r') as f:
    tagged_papers = json.load(f)

# Use in visualization
visualizer = MatrixVisualizer()
visualizer.create_network_graph(tagged_papers)
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### 1. Report Issues
- Use the GitHub issue tracker
- Provide detailed descriptions and examples

### 2. Submit Pull Requests
- Fork the repository
- Create a feature branch
- Make your changes
- Submit a pull request

### 3. Improve the System
- Add new matrix categories
- Enhance the ML models
- Improve the BibTeX parser
- Add new export formats

### 4. Share Training Data
- Contribute tagged papers to improve the models
- Share domain-specific training sets

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Memory studies research community
- Contributors of tagged papers
- Open-source ML community

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/mnemonic-matrix-tagger/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/mnemonic-matrix-tagger/discussions)
- **Email**: your-email@example.com

## 🔄 Version History

- **v1.0.0**: Initial release with basic tagging functionality
- **v1.1.0**: Added confidence scoring and batch processing
- **v1.2.0**: Enhanced BibTeX integration and export options

---

**Made with ❤️ for the memory studies research community**