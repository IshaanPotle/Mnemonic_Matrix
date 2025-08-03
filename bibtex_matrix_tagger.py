#!/usr/bin/env python3
"""
BibTeX Matrix Tagger - Parses BibTeX files and implements ML tagging for comprehensive matrix categories
"""

import re
import json
from typing import List, Dict, Tuple
from collections import defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pickle

class BibTeXMatrixTagger:
    """Parses BibTeX files and implements ML tagging for comprehensive matrix categories."""
    
    def __init__(self):
        # Comprehensive matrix tag categories (Updated August 1, 2025)
        self.matrix_categories = {
            'time': {
                'name': 'Time of Publication',
                'description': 'Simply the year the article or book was published',
                'tags': ['T1', 'T2', 'T3', 'T4', 'T5'],
                'descriptions': {
                    'T1': '400 BCE to 1859',
                    'T2': '1860 to 1949',
                    'T3': '1950 to 1989',
                    'T4': '1990 to 2010',
                    'T5': '2011 to Present'
                }
            },
            'discipline': {
                'name': 'Discipline',
                'description': 'What discipline produced the publication - based on author affiliation, journal, methods used',
                'tags': ['DSOC', 'DHIS', 'DSPY', 'DNEU', 'DPOL', 'DANT', 'DGEO', 
                         'DARC', 'DLIT', 'DCUL', 'DLAW', 'DPHI', 'DPSY', 'DMED', 
                         'DEDU', 'DHUM', 'DSS', 'DMU', 'DHE', 'DAR'],
                'descriptions': {
                    'DSOC': 'Sociology',
                    'DHIS': 'History',
                    'DSPY': 'Social Psychology',
                    'DNEU': 'Neuroscience',
                    'DPOL': 'Political Science (subtypes: IR, Human rights, Transitional Justice)',
                    'DANT': 'Anthropology',
                    'DGEO': 'Geography',
                    'DARC': 'Archaeology',
                    'DLIT': 'Literature',
                    'DCUL': 'Cultural Studies',
                    'DLAW': 'Legal Studies',
                    'DPHI': 'Philosophy',
                    'DPSY': 'Psychology',
                    'DMED': 'Film/Media Studies',
                    'DEDU': 'Education',
                    'DHUM': 'Humanities (for stuff that cannot be categorized elsewhere)',
                    'DSS': 'Social Sciences (includes Economics, Criminology, Social Work)',
                    'DMU': 'Museum Studies',
                    'DHE': 'Heritage Studies',
                    'DAR': 'Archival Studies'
                }
            },
            'memory_carrier': {
                'name': 'Memory Carriers',
                'description': 'By what MEANS of memory is this publication focused on',
                'tags': ['MCSO', 'MCLI', 'MCFI', 'MCT', 'MCAR', 'MCPH', 'MCC', 
                         'MCMO', 'MCA', 'MCB', 'MCME', 'MCLA', 'MCED', 'MCMU', 
                         'MCF', 'MCT', 'MCNAT'],
                'descriptions': {
                    'MCSO': 'Social media',
                    'MCLI': 'Literature',
                    'MCFI': 'Film',
                    'MCT': 'TV',
                    'MCAR': 'Art',
                    'MCPH': 'Photography',
                    'MCC': 'Commemorations',
                    'MCMO': 'Monuments',
                    'MCA': 'Activists',
                    'MCB': 'Brain',
                    'MCME': 'Memory scholars',
                    'MCLA': 'Law',
                    'MCED': 'Educational',
                    'MCMU': 'Museums',
                    'MCF': 'Family',
                    'MCT': 'Testimony',
                    'MCNAT': 'Nation'
                }
            },
            'concept_tags': {
                'name': 'Concept Tags',
                'description': 'What memory concept(s) a publication is MOST concerned with',
                'tags': [
                    # A
                    'CTArchives', 'CTAutobiographicalMemory', 'CTAgonisticMemory', 'CTAmnesia', 'CTAestheticMemory',
                    # B
                    'CTBanalMnemonics',
                    # C
                    'CTCanons', 'CTCommunicativeMemory', 'CTCulturalTrauma', 'CTCollectiveMemory', 'CTCulturalMemory',
                    'CTCosmopolitanMemory', 'CTCommemoration', 'CTCatastrophicMemory', 'CTCounterMemory',
                    # D
                    'CTDialogical', 'CTDeclarativeMemory', 'CTDigitalMemory', 'CTDutyToRemember',
                    # E
                    'CTEngrams', 'CTEpisodicMemory', 'CTExplicitMemory', 'CTEntangledMemory',
                    # F
                    'CTFamilyMemory', 'CTFlashbulbMemory', 'CTFlashback', 'CTForgetting', 'CTForgettingCurve', 'CTFalseMemory',
                    # G
                    'CTGenreMemory', 'CTGlobitalMemory', 'CTGlobalMemory', 'CTGenerationalMemory',
                    # H
                    'CTHeritage', 'CTHistoricalMemory', 'CTHyperthymesia',
                    # I
                    'CTIdentity', 'CTImplicitMemory', 'CTIntergenerationalTransmissions', 'CTIconicMemory', 'CTImaginativeReconstruction',
                    # L
                    'CTLongueDuree',
                    # M
                    'CTMultidirectionalMemory', 'CTMnemonicSecurity', 'CTMilieuDeMemoire', 'CTMemoryLaws', 'CTMnemohistory',
                    'CTMemoryConsolidation', 'CTMemoryRetrieval', 'CTMemoryEncoding', 'CTMemoryStorage', 'CTMemoryTrace',
                    'CTMemorySpan', 'CTMemoryDistortion', 'CTMemoryAccuracy', 'CTMemoryBias', 'CTMemoryEnhancement',
                    'CTMemorySuppression', 'CTMemorySchemas', 'CTMnemonics', 'CTMemoryPolitics', 'CTMnemonicCommunities',
                    'CTMnemonicSocialization', 'CTMemoryEthics', 'CTMemoryPractices', 'CTMnemonicStandoff',
                    # N
                    'CTNationalMemory', 'CTNonContemporaneity',
                    # O
                    'CTOfficialMemory',
                    # P
                    'CTParticularism', 'CTPrivateMemory', 'CTPublicMemory', 'CTPathDependency', 'CTProceduralMemory',
                    'CTProstheticMemory', 'CTPostColonialMemory', 'CTProspectiveMemory', 'CTProfaneMemory', 'CTPostMemory',
                    # R
                    'CTRealmsOfMemory', 'CTRegret', 'CTRestitution', 'CTReparations', 'CTRedress', 'CTRepressedMemory',
                    'CTRecoveredMemory', 'CTRetrospectiveMemory', 'CTRevisionistMemory', 'CTReligiousMemory',
                    # S
                    'CTSemanticMemory', 'CTSocialFrameworks', 'CTSlowMemory', 'CTSocialMemory', 'CTScreenMemory',
                    'CTSensoryMemory', 'CTSourceMemory', 'CTSacredMemory',
                    # T
                    'CTTrauma', 'CTTradition', 'CTTravellingMemory', 'CTTransnationalMemory', 'CTTransculturalMemory', 'CTTransoceanicMemory',
                    # U
                    'CTUniversalism',
                    # V
                    'CTVernacularMemory',
                    # W
                    'CTWorkingMemory'
                ],
                'descriptions': {
                    'CTArchives': 'Archives',
                    'CTAutobiographicalMemory': 'Autobiographical Memory',
                    'CTAgonisticMemory': 'Agonistic Memory',
                    'CTAmnesia': 'Amnesia',
                    'CTAestheticMemory': 'Aesthetic Memory',
                    'CTBanalMnemonics': 'Banal Mnemonics',
                    'CTCanons': 'Canons',
                    'CTCommunicativeMemory': 'Communicative Memory',
                    'CTCulturalTrauma': 'Cultural Trauma',
                    'CTCollectiveMemory': 'Collective Memory',
                    'CTCulturalMemory': 'Cultural Memory',
                    'CTCosmopolitanMemory': 'Cosmopolitan Memory',
                    'CTCommemoration': 'Commemoration',
                    'CTCatastrophicMemory': 'Catastrophic Memory',
                    'CTCounterMemory': 'Counter-Memory',
                    'CTDialogical': 'Dialogical',
                    'CTDeclarativeMemory': 'Declarative Memory',
                    'CTDigitalMemory': 'Digital Memory',
                    'CTDutyToRemember': 'Duty to Remember',
                    'CTEngrams': 'Engrams',
                    'CTEpisodicMemory': 'Episodic Memory',
                    'CTExplicitMemory': 'Explicit Memory',
                    'CTEntangledMemory': 'Entangled Memory',
                    'CTFamilyMemory': 'Family Memory',
                    'CTFlashbulbMemory': 'Flashbulb Memory',
                    'CTFlashback': 'Flashback',
                    'CTForgetting': 'Forgetting',
                    'CTForgettingCurve': 'Forgetting Curve',
                    'CTFalseMemory': 'False Memory',
                    'CTGenreMemory': 'Genre Memory',
                    'CTGlobitalMemory': 'Globital Memory',
                    'CTGlobalMemory': 'Global Memory',
                    'CTGenerationalMemory': 'Generational Memory',
                    'CTHeritage': 'Heritage',
                    'CTHistoricalMemory': 'Historical Memory',
                    'CTHyperthymesia': 'Hyperthymesia',
                    'CTIdentity': 'Identity',
                    'CTImplicitMemory': 'Implicit Memory',
                    'CTIntergenerationalTransmissions': 'Intergenerational Transmissions',
                    'CTIconicMemory': 'Iconic Memory',
                    'CTImaginativeReconstruction': 'Imaginative Reconstruction',
                    'CTLongueDuree': 'Longue Durée',
                    'CTMultidirectionalMemory': 'Multidirectional Memory',
                    'CTMnemonicSecurity': 'Mnemonic Security',
                    'CTMilieuDeMemoire': 'Milieu de Memoire',
                    'CTMemoryLaws': 'Memory Laws',
                    'CTMnemohistory': 'Mnemohistory',
                    'CTMemoryConsolidation': 'Memory Consolidation',
                    'CTMemoryRetrieval': 'Memory Retrieval',
                    'CTMemoryEncoding': 'Memory Encoding',
                    'CTMemoryStorage': 'Memory Storage',
                    'CTMemoryTrace': 'Memory Trace',
                    'CTMemorySpan': 'Memory Span',
                    'CTMemoryDistortion': 'Memory Distortion',
                    'CTMemoryAccuracy': 'Memory Accuracy',
                    'CTMemoryBias': 'Memory Bias',
                    'CTMemoryEnhancement': 'Memory Enhancement',
                    'CTMemorySuppression': 'Memory Suppression',
                    'CTMemorySchemas': 'Memory Schemas',
                    'CTMnemonics': 'Mnemonics',
                    'CTMemoryPolitics': 'Memory Politics',
                    'CTMnemonicCommunities': 'Mnemonic Communities',
                    'CTMnemonicSocialization': 'Mnemonic Socialization',
                    'CTMemoryEthics': 'Memory Ethics',
                    'CTMemoryPractices': 'Memory Practices',
                    'CTMnemonicStandoff': 'Mnemonic Standoff',
                    'CTNationalMemory': 'National Memory',
                    'CTNonContemporaneity': 'Non-Contemporaneity',
                    'CTOfficialMemory': 'Official Memory',
                    'CTParticularism': 'Particularism',
                    'CTPrivateMemory': 'Private Memory',
                    'CTPublicMemory': 'Public Memory',
                    'CTPathDependency': 'Path-Dependency',
                    'CTProceduralMemory': 'Procedural Memory',
                    'CTProstheticMemory': 'Prosthetic Memory',
                    'CTPostColonialMemory': 'Post-Colonial Memory',
                    'CTProspectiveMemory': 'Prospective Memory',
                    'CTProfaneMemory': 'Profane Memory',
                    'CTPostMemory': 'Post-Memory',
                    'CTRealmsOfMemory': 'Realms of Memory',
                    'CTRegret': 'Regret',
                    'CTRestitution': 'Restitution',
                    'CTReparations': 'Reparations',
                    'CTRedress': 'Redress',
                    'CTRepressedMemory': 'Repressed Memory',
                    'CTRecoveredMemory': 'Recovered Memory',
                    'CTRetrospectiveMemory': 'Retrospective Memory',
                    'CTRevisionistMemory': 'Revisionist Memory',
                    'CTReligiousMemory': 'Religious Memory',
                    'CTSemanticMemory': 'Semantic Memory',
                    'CTSocialFrameworks': 'Social Frameworks',
                    'CTSlowMemory': 'Slow Memory',
                    'CTSocialMemory': 'Social Memory',
                    'CTScreenMemory': 'Screen Memory',
                    'CTSensoryMemory': 'Sensory Memory',
                    'CTSourceMemory': 'Source Memory',
                    'CTSacredMemory': 'Sacred Memory',
                    'CTTrauma': 'Trauma',
                    'CTTradition': 'Tradition',
                    'CTTravellingMemory': 'Traveling Memory',
                    'CTTransnationalMemory': 'Transnational Memory',
                    'CTTransculturalMemory': 'Transcultural Memory',
                    'CTTransoceanicMemory': 'Transoceanic Memory',
                    'CTUniversalism': 'Universalism',
                    'CTVernacularMemory': 'Vernacular Memory',
                    'CTWorkingMemory': 'Working Memory'
                }
            }
        }
        
        # Enhanced tag patterns for better extraction
        self.tag_patterns = {
            'time': r'T[1-5]',
            'discipline': r'D[A-Z]{2,4}',
            'memory_carrier': r'MC[A-Z]{2,4}',
            'concept_tags': r'CT[A-Za-z]+'
        }
        
        # Keywords for improved ML prediction
        self.category_keywords = {
            'time': {
                'T1': ['ancient', 'classical', 'antiquity', 'rome', 'greece', 'bce', '400 bce', '500 bce', 'before 1860', 'ancient times'],
                'T2': ['1860', '1949', 'nineteenth century', 'industrial revolution', 'early modern'],
                'T3': ['1950', '1989', 'post-war', 'cold war', 'mid twentieth', 'modern era'],
                'T4': ['1990', '2010', 'late twentieth', 'early twenty-first', 'late modern'],
                'T5': ['2011', 'present day', 'twenty-first century', 'contemporary era', 'current period', 'recent years']
            },
            'discipline': {
                'DSOC': ['sociology', 'social', 'sociological', 'society', 'social theory', 'sociologist'],
                'DHIS': ['history', 'historical', 'historian', 'historiography', 'past', 'historian'],
                'DSPY': ['social psychology', 'psychological', 'behavior', 'social behavior', 'group psychology'],
                'DNEU': ['neuroscience', 'neural', 'brain', 'cognitive science', 'neuro', 'neurological'],
                'DPOL': ['political science', 'politics', 'government', 'policy', 'political', 'international relations', 'human rights', 'transitional justice'],
                'DANT': ['anthropology', 'anthropological', 'cultural anthropology', 'ethnography', 'anthropologist'],
                'DGEO': ['geography', 'geographical', 'spatial', 'place', 'location', 'geographer'],
                'DARC': ['archaeology', 'archaeological', 'excavation', 'artifacts', 'material', 'archaeologist'],
                'DLIT': ['literature', 'literary', 'text', 'narrative', 'fiction', 'literary studies'],
                'DCUL': ['cultural studies', 'culture', 'cultural', 'cultural theory', 'cultural studies'],
                'DLAW': ['legal studies', 'law', 'legal', 'jurisprudence', 'legal studies', 'justice', 'legal scholar'],
                'DPHI': ['philosophy', 'philosophical', 'ethics', 'metaphysics', 'epistemology', 'philosopher'],
                'DPSY': ['psychology', 'psychological', 'mental health', 'therapy', 'psychologist'],
                'DMED': ['film studies', 'media studies', 'film', 'cinema', 'media', 'film scholar'],
                'DEDU': ['education', 'educational', 'pedagogy', 'learning', 'teaching', 'educational studies'],
                'DHUM': ['humanities', 'humanistic', 'arts', 'humanities studies', 'humanist'],
                'DSS': ['social sciences', 'social science', 'interdisciplinary', 'economics', 'criminology', 'social work'],
                'DMU': ['museum studies', 'museum', 'curation', 'exhibition', 'museum studies'],
                'DHE': ['heritage studies', 'heritage', 'cultural heritage', 'heritage scholar'],
                'DAR': ['archival studies', 'archives', 'archival', 'archivist', 'archival studies']
            },
            'memory_carrier': {
                'MCSO': ['social media', 'social', 'media', 'platform', 'digital social'],
                'MCLI': ['literature', 'text', 'book', 'writing', 'narrative', 'literary'],
                'MCFI': ['film', 'cinema', 'movie', 'motion picture', 'cinematic'],
                'MCT': ['television', 'tv', 'broadcast', 'television media'],
                'MCAR': ['art', 'artistic', 'visual art', 'painting', 'sculpture', 'artwork'],
                'MCPH': ['photography', 'photo', 'image', 'visual', 'picture', 'photographic'],
                'MCC': ['commemorations', 'commemoration', 'ceremony', 'ritual', 'memorial service'],
                'MCMO': ['monuments', 'monument', 'memorial', 'statue', 'memorial structure'],
                'MCA': ['activists', 'activism', 'social movement', 'protest', 'activist'],
                'MCB': ['brain', 'neural', 'cognitive', 'neurological', 'brain function'],
                'MCME': ['memory scholars', 'memory studies', 'memory researcher', 'memory academic'],
                'MCLA': ['law', 'legal', 'legal system', 'jurisprudence', 'legal framework'],
                'MCED': ['educational', 'education', 'school', 'learning', 'pedagogy'],
                'MCMU': ['museums', 'museum', 'exhibition', 'display', 'curation'],
                'MCF': ['family', 'domestic', 'household', 'kinship', 'personal', 'family memory'],
                'MCT': ['testimony', 'witness', 'oral history', 'testimonial', 'witness account'],
                'MCNAT': ['nation', 'national', 'state', 'government', 'national identity']
            },
            'concept_tags': {
                'CTArchives': ['archives', 'archival', 'documentation', 'records', 'archival memory'],
                'CTAutobiographicalMemory': ['autobiographical memory', 'personal memory', 'life story', 'autobiography'],
                'CTAgonisticMemory': ['agonistic memory', 'conflict memory', 'contestation', 'memory conflict'],
                'CTAmnesia': ['amnesia', 'memory loss', 'forgetting', 'memory impairment'],
                'CTAestheticMemory': ['aesthetic memory', 'artistic memory', 'beauty memory', 'aesthetic experience'],
                'CTBanalMnemonics': ['banal mnemonics', 'everyday memory', 'mundane memory', 'ordinary memory'],
                'CTCanons': ['canons', 'canonical', 'tradition', 'classical', 'canonical memory'],
                'CTCommunicativeMemory': ['communicative memory', 'communication', 'memory communication'],
                'CTCulturalTrauma': ['cultural trauma', 'trauma culture', 'collective trauma'],
                'CTCollectiveMemory': ['collective memory', 'shared memory', 'group memory', 'social memory'],
                'CTCulturalMemory': ['cultural memory', 'cultural heritage', 'cultural tradition'],
                'CTCosmopolitanMemory': ['cosmopolitan memory', 'global memory', 'world memory'],
                'CTCommemoration': ['commemoration', 'memorial', 'remembrance', 'anniversary'],
                'CTCatastrophicMemory': ['catastrophic memory', 'disaster memory', 'catastrophe'],
                'CTCounterMemory': ['counter memory', 'oppositional memory', 'resistance memory'],
                'CTDialogical': ['dialogical', 'dialogue', 'conversation', 'dialogical memory'],
                'CTDeclarativeMemory': ['declarative memory', 'explicit memory', 'conscious memory'],
                'CTDigitalMemory': ['digital memory', 'online memory', 'virtual memory', 'digital'],
                'CTDutyToRemember': ['duty to remember', 'obligation', 'memory obligation'],
                'CTEngrams': ['engrams', 'memory traces', 'neural patterns', 'memory imprint'],
                'CTEpisodicMemory': ['episodic memory', 'event memory', 'episode memory'],
                'CTExplicitMemory': ['explicit memory', 'conscious memory', 'declarative memory'],
                'CTEntangledMemory': ['entangled memory', 'interconnected memory', 'memory entanglement'],
                'CTFamilyMemory': ['family memory', 'domestic memory', 'kinship memory'],
                'CTFlashbulbMemory': ['flashbulb memory', 'vivid memory', 'intense memory'],
                'CTFlashback': ['flashback', 'memory flashback', 'intrusive memory'],
                'CTForgetting': ['forgetting', 'memory loss', 'oblivion', 'memory decay'],
                'CTForgettingCurve': ['forgetting curve', 'memory decay', 'memory retention'],
                'CTFalseMemory': ['false memory', 'memory error', 'inaccurate memory'],
                'CTGenreMemory': ['genre memory', 'memory genre', 'memory type'],
                'CTGlobitalMemory': ['globital memory', 'global digital', 'digital global'],
                'CTGlobalMemory': ['global memory', 'world memory', 'international memory'],
                'CTGenerationalMemory': ['generational memory', 'generation memory', 'intergenerational'],
                'CTHeritage': ['heritage', 'cultural heritage', 'inheritance', 'heritage memory'],
                'CTHistoricalMemory': ['historical memory', 'memory of history', 'past memory'],
                'CTHyperthymesia': ['hyperthymesia', 'exceptional memory', 'superior memory'],
                'CTIdentity': ['identity', 'memory identity', 'identity formation'],
                'CTImplicitMemory': ['implicit memory', 'unconscious memory', 'automatic memory'],
                'CTIntergenerationalTransmissions': ['intergenerational transmission', 'generation transmission'],
                'CTIconicMemory': ['iconic memory', 'visual memory', 'image memory'],
                'CTImaginativeReconstruction': ['imaginative reconstruction', 'creative memory'],
                'CTLongueDuree': ['longue durée', 'long term', 'enduring memory'],
                'CTMultidirectionalMemory': ['multidirectional memory', 'multi-directional', 'memory flows'],
                'CTMnemonicSecurity': ['mnemonic security', 'memory security', 'memory protection'],
                'CTMilieuDeMemoire': ['milieu de mémoire', 'memory environment', 'memory space'],
                'CTMemoryLaws': ['memory laws', 'legal memory', 'memory legislation'],
                'CTMnemohistory': ['mnemohistory', 'history of memory', 'memory historiography'],
                'CTMemoryConsolidation': ['memory consolidation', 'memory strengthening'],
                'CTMemoryRetrieval': ['memory retrieval', 'recall', 'remembering'],
                'CTMemoryEncoding': ['memory encoding', 'memory formation', 'memory creation'],
                'CTMemoryStorage': ['memory storage', 'memory preservation', 'memory retention'],
                'CTMemoryTrace': ['memory trace', 'neural trace', 'memory imprint'],
                'CTMemorySpan': ['memory span', 'memory capacity', 'memory duration'],
                'CTMemoryDistortion': ['memory distortion', 'memory alteration', 'memory error'],
                'CTMemoryAccuracy': ['memory accuracy', 'memory precision', 'memory reliability'],
                'CTMemoryBias': ['memory bias', 'memory distortion', 'memory error'],
                'CTMemoryEnhancement': ['memory enhancement', 'memory improvement', 'memory training'],
                'CTMemorySuppression': ['memory suppression', 'memory inhibition', 'forgetting'],
                'CTMemorySchemas': ['memory schemas', 'memory frameworks', 'memory organization'],
                'CTMnemonics': ['mnemonics', 'memory techniques', 'memory strategies'],
                'CTMemoryPolitics': ['memory politics', 'political memory', 'memory policy'],
                'CTMnemonicCommunities': ['mnemonic communities', 'memory communities'],
                'CTMnemonicSocialization': ['mnemonic socialization', 'memory learning'],
                'CTMemoryEthics': ['memory ethics', 'ethical memory', 'memory morality'],
                'CTMemoryPractices': ['memory practices', 'memory activities', 'memory rituals'],
                'CTMnemonicStandoff': ['mnemonic standoff', 'memory conflict', 'memory dispute'],
                'CTNationalMemory': ['national memory', 'state memory', 'country memory'],
                'CTNonContemporaneity': ['non-contemporaneity', 'temporal disjunction'],
                'CTOfficialMemory': ['official memory', 'institutional memory', 'state memory'],
                'CTParticularism': ['particularism', 'specific memory', 'particular memory'],
                'CTPrivateMemory': ['private memory', 'personal memory', 'individual memory'],
                'CTPublicMemory': ['public memory', 'collective memory', 'shared memory'],
                'CTPathDependency': ['path dependency', 'memory paths', 'memory trajectories'],
                'CTProceduralMemory': ['procedural memory', 'skill memory', 'habit memory'],
                'CTProstheticMemory': ['prosthetic memory', 'external memory', 'memory aids'],
                'CTPostColonialMemory': ['post-colonial memory', 'colonial memory', 'imperial memory'],
                'CTProspectiveMemory': ['prospective memory', 'future memory', 'memory planning'],
                'CTProfaneMemory': ['profane memory', 'secular memory', 'non-religious memory'],
                'CTPostMemory': ['post-memory', 'memory after', 'memory transmission'],
                'CTRealmsOfMemory': ['realms of memory', 'memory domains', 'memory spheres'],
                'CTRegret': ['regret', 'memory regret', 'remorse'],
                'CTRestitution': ['restitution', 'memory restitution', 'compensation'],
                'CTReparations': ['reparations', 'memory reparations', 'compensation'],
                'CTRedress': ['redress', 'memory redress', 'justice'],
                'CTRepressedMemory': ['repressed memory', 'suppressed memory', 'hidden memory'],
                'CTRecoveredMemory': ['recovered memory', 'retrieved memory', 'restored memory'],
                'CTRetrospectiveMemory': ['retrospective memory', 'looking back', 'memory review'],
                'CTRevisionistMemory': ['revisionist memory', 'memory revision', 'memory change'],
                'CTReligiousMemory': ['religious memory', 'sacred memory', 'spiritual memory'],
                'CTSemanticMemory': ['semantic memory', 'knowledge memory', 'fact memory'],
                'CTSocialFrameworks': ['social frameworks', 'memory frameworks', 'social structures'],
                'CTSlowMemory': ['slow memory', 'gradual memory', 'memory time'],
                'CTSocialMemory': ['social memory', 'memory society', 'social remembrance'],
                'CTScreenMemory': ['screen memory', 'protective memory', 'memory defense'],
                'CTSensoryMemory': ['sensory memory', 'sensory recall', 'perceptual memory'],
                'CTSourceMemory': ['source memory', 'memory source', 'origin memory'],
                'CTSacredMemory': ['sacred memory', 'holy memory', 'spiritual memory'],
                'CTTrauma': ['trauma', 'traumatic memory', 'trauma studies'],
                'CTTradition': ['tradition', 'traditional memory', 'customary memory'],
                'CTTravellingMemory': ['traveling memory', 'mobile memory', 'memory movement'],
                'CTTransnationalMemory': ['transnational memory', 'cross-national memory'],
                'CTTransculturalMemory': ['transcultural memory', 'cross-cultural memory'],
                'CTTransoceanicMemory': ['transoceanic memory', 'ocean memory', 'maritime memory'],
                'CTUniversalism': ['universalism', 'universal memory', 'global memory'],
                'CTVernacularMemory': ['vernacular memory', 'local memory', 'folk memory'],
                'CTWorkingMemory': ['working memory', 'short-term memory', 'immediate memory']
            }
        }
        
        self.training_data = []
        self.models = {}
        self.vectorizer = None
        
    def parse_bibtex_file(self, file_path: str) -> List[Dict]:
        """Parse BibTeX file and extract entries with matrix tags."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into individual entries
        entries = re.split(r'\n@', content)
        parsed_entries = []
        
        for entry in entries:
            if entry.strip():
                parsed_entry = self._parse_single_entry(entry)
                if parsed_entry:
                    parsed_entries.append(parsed_entry)
        
        return parsed_entries
    
    def _parse_single_entry(self, entry_text: str) -> Dict:
        """Parse a single BibTeX entry."""
        # Extract entry key
        key_match = re.search(r'\{([^,]+),', entry_text)
        if not key_match:
            return None
        
        entry_key = key_match.group(1)
        
        # Extract fields
        title_match = re.search(r'title\s*=\s*\{([^}]+)\}', entry_text)
        author_match = re.search(r'author\s*=\s*\{([^}]+)\}', entry_text)
        year_match = re.search(r'year\s*=\s*\{([^}]+)\}', entry_text)
        journal_match = re.search(r'journal\s*=\s*\{([^}]+)\}', entry_text)
        abstract_match = re.search(r'abstract\s*=\s*\{([^}]+)\}', entry_text)
        keywords_match = re.search(r'keywords\s*=\s*\{([^}]+)\}', entry_text)
        
        # Extract matrix tags from keywords
        matrix_tags = {}
        if keywords_match:
            keywords = keywords_match.group(1)
            matrix_tags = self._extract_matrix_tags(keywords)
        
        return {
            'entry_key': entry_key,
            'title': title_match.group(1) if title_match else 'Unknown Title',
            'author': author_match.group(1) if author_match else 'Unknown Author',
            'year': year_match.group(1) if year_match else 'Unknown Year',
            'journal': journal_match.group(1) if journal_match else 'Unknown Journal',
            'abstract': abstract_match.group(1) if abstract_match else '',
            'matrix_tags': matrix_tags
        }
    
    def _extract_matrix_tags(self, keywords: str) -> Dict[str, List[str]]:
        """Extract matrix tags from keywords string."""
        extracted_tags = {
            'time': [],
            'discipline': [],
            'memory_carrier': [],
            'concept_tags': []
        }
        
        # Split keywords and extract tags
        keyword_list = [k.strip() for k in keywords.split(',')]
        
        for keyword in keyword_list:
            for category, pattern in self.tag_patterns.items():
                if re.match(pattern, keyword):
                    extracted_tags[category].append(keyword)
        
        return extracted_tags
    
    def prepare_training_data(self, tagged_entries: List[Dict]) -> Tuple[List[str], Dict[str, List[List[int]]]]:
        """Prepare training data for ML models."""
        texts = []
        labels = {category: [] for category in self.matrix_categories.keys()}
        
        for entry in tagged_entries:
            # Combine title and abstract for text features
            text = f"{entry.get('title', '')} {entry.get('abstract', '')}"
            texts.append(text)
            
            # Create binary labels for each category
            for category in self.matrix_categories.keys():
                category_tags = entry.get('matrix_tags', {}).get(category, [])
                
                # Handle both old and new matrix_categories structure
                if isinstance(self.matrix_categories[category], dict):
                    # New structure with 'tags' key
                    available_tags = self.matrix_categories[category]['tags']
                else:
                    # Old structure with direct list
                    available_tags = self.matrix_categories[category]
                
                # Create binary vector for this category
                binary_labels = [1 if tag in category_tags else 0 for tag in available_tags]
                labels[category].append(binary_labels)
        
        return texts, labels
    
    def train_models(self, tagged_entries: List[Dict]):
        """Train ML models for each matrix category."""
        if not tagged_entries:
            print("❌ No tagged entries provided for training.")
            return
        
        print(f"🔄 Training models with {len(tagged_entries)} tagged papers...")
        
        # Prepare training data
        texts, labels = self.prepare_training_data(tagged_entries)
        
        # Create TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 3),
            stop_words='english',
            min_df=2,
            max_df=0.95
        )
        
        # Fit vectorizer
        X = self.vectorizer.fit_transform(texts)
        
        # Train models for each category
        for category, category_info in self.matrix_categories.items():
            print(f"📚 Training {category} model...")
            
            y = labels[category]
            
            # Create multi-output classifier
            classifier = MultiOutputClassifier(
                RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42,
                    class_weight='balanced'
                )
            )
            
            # Train the model
            classifier.fit(X, y)
            
            # Store the model
            self.models[category] = classifier
            
            # Print training results
            y_pred = classifier.predict(X)
            correct_predictions = sum(1 for true, pred in zip(y, y_pred) if list(true) == list(pred))
            accuracy = correct_predictions / len(y) if y else 0
            print(f"✅ {category} model accuracy: {accuracy:.2f}")
        
        print("🎯 All matrix category models trained successfully!")
    
    def predict_tags(self, paper_text: str) -> Dict[str, List[str]]:
        """Predict matrix tags for a paper using trained models."""
        if not self.models or not self.vectorizer:
            print("❌ Models not trained. Please train models first.")
            return {}
        
        # Vectorize the text
        X = self.vectorizer.transform([paper_text])
        
        predictions = {}
        
        for category, model in self.models.items():
            # Get predictions
            y_pred = model.predict(X)[0]
            
            # Convert to tag names
            predicted_tags = []
            for i, predicted in enumerate(y_pred):
                if predicted == 1:
                    # Handle both old and new matrix_categories structure
                    if isinstance(self.matrix_categories[category], dict):
                        # New structure with 'tags' key
                        predicted_tags.append(self.matrix_categories[category]['tags'][i])
                    else:
                        # Old structure with direct list
                        predicted_tags.append(self.matrix_categories[category][i])
            
            predictions[category] = predicted_tags
        
        return predictions
    
    def predict_tags_with_confidence(self, paper_text: str) -> Dict[str, List[Tuple[str, float]]]:
        """Predict matrix tags with confidence scores."""
        if not self.models or not self.vectorizer:
            print("❌ Models not trained. Please train models first.")
            return {}
        
        # Vectorize the text
        X = self.vectorizer.transform([paper_text])
        
        predictions = {}
        
        for category, model in self.models.items():
            # Get prediction probabilities
            y_proba = model.predict_proba(X)
            
            predicted_tags_with_confidence = []
            
            for i, proba in enumerate(y_proba):
                if isinstance(proba, np.ndarray):
                    confidence = float(proba[1]) if len(proba) > 1 else float(proba[0])
                else:
                    confidence = float(proba)
                
                if confidence > 0.3:  # Confidence threshold
                    # Handle both old and new matrix_categories structure
                    if isinstance(self.matrix_categories[category], dict):
                        # New structure with 'tags' key
                        tag_name = self.matrix_categories[category]['tags'][i]
                    else:
                        # Old structure with direct list
                        tag_name = self.matrix_categories[category][i]
                    predicted_tags_with_confidence.append((tag_name, confidence))
            
            predictions[category] = predicted_tags_with_confidence
        
        return predictions
    
    def predict_tags_simple(self, paper_text: str) -> Dict[str, List[str]]:
        """Predict matrix tags without confidence scores (simpler version)."""
        if not self.models or not self.vectorizer:
            print("❌ Models not trained. Please train models first.")
            return {}
        
        X = self.vectorizer.transform([paper_text])
        
        predictions = {}
        total_predicted_tags = 0
        
        # First pass: Get initial predictions
        for category, model in self.models.items():
            # Get predictions
            y_pred = model.predict(X)[0]
            
            # Convert to tag names
            predicted_tags = []
            for i, predicted in enumerate(y_pred):
                if predicted == 1:
                    # Handle both old and new matrix_categories structure
                    if isinstance(self.matrix_categories[category], dict):
                        # New structure with 'tags' key
                        predicted_tags.append(self.matrix_categories[category]['tags'][i])
                    else:
                        # Old structure with direct list
                        predicted_tags.append(self.matrix_categories[category][i])
            
            predictions[category] = predicted_tags
            total_predicted_tags += len(predicted_tags)
        
        # Apply mutual exclusivity rules
        predictions = self._apply_mutual_exclusivity(predictions, paper_text)
        
        # Recalculate total tags after exclusivity rules
        total_predicted_tags = sum(len(tags) for tags in predictions.values())
        
        # If we have less than 3 tags, enhance predictions
        if total_predicted_tags < 3:
            print(f"🔍 Enhancing predictions (only {total_predicted_tags} tags found, need at least 3)")
            
            # Get confidence scores for better selection
            enhanced_predictions = self._enhance_predictions_with_keywords(paper_text, predictions)
            
            # Ensure we have at least 3 tags
            final_predictions = self._ensure_minimum_tags(enhanced_predictions, paper_text)
            
            return final_predictions
        
        return predictions
    
    def _enhance_predictions_with_keywords(self, paper_text: str, initial_predictions: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Enhance predictions using keyword analysis."""
        enhanced_predictions = initial_predictions.copy()
        paper_text_lower = paper_text.lower()
        
        # Analyze text for keywords and add relevant tags
        for category, category_info in self.matrix_categories.items():
            if isinstance(category_info, dict):
                # New structure
                available_tags = category_info['tags']
                descriptions = category_info.get('descriptions', {})
            else:
                # Old structure
                available_tags = category_info
                descriptions = {}
            
            # Check each tag's keywords
            for tag in available_tags:
                if tag not in enhanced_predictions[category]:
                    # Get keywords for this tag
                    keywords = self.category_keywords.get(category, {}).get(tag, [])
                    
                    # Check if any keywords are in the text (with word boundary check for short keywords)
                    for keyword in keywords:
                        keyword_lower = keyword.lower()
                        if len(keyword_lower) <= 3:
                            # For short keywords, check word boundaries to avoid false matches
                            import re
                            if re.search(r'\b' + re.escape(keyword_lower) + r'\b', paper_text_lower):
                                enhanced_predictions[category].append(tag)
                                print(f"  📝 Added {tag} based on keyword '{keyword}'")
                                break
                        elif keyword_lower in paper_text_lower:
                            enhanced_predictions[category].append(tag)
                            print(f"  📝 Added {tag} based on keyword '{keyword}'")
                            break
        
        # Apply mutual exclusivity after keyword enhancement
        enhanced_predictions = self._apply_mutual_exclusivity(enhanced_predictions, paper_text)
        
        return enhanced_predictions
    
    def _ensure_minimum_tags(self, predictions: Dict[str, List[str]], paper_text: str) -> Dict[str, List[str]]:
        """Ensure we have at least one tag from each of the four main categories."""
        paper_text_lower = paper_text.lower()
        
        # Define the four main categories
        main_categories = ['time', 'discipline', 'memory_carrier', 'concept_tags']
        
        print(f"🎯 Ensuring at least one tag from each of the 4 main categories")
        
        # Check each category and add a tag if missing
        for category in main_categories:
            if not predictions.get(category, []):
                print(f"  📝 Missing tag from {category} category")
                
                if isinstance(self.matrix_categories[category], dict):
                    available_tags = self.matrix_categories[category]['tags']
                else:
                    available_tags = self.matrix_categories[category]
                
                # Find the most relevant tag for this category
                best_tag = None
                best_score = 0
                
                for tag in available_tags:
                    # Calculate relevance score based on keywords
                    keywords = self.category_keywords.get(category, {}).get(tag, [])
                    score = sum(1 for keyword in keywords if keyword.lower() in paper_text_lower)
                    
                    if score > best_score:
                        best_score = score
                        best_tag = tag
                
                # If no keyword match found, use default tags for each category
                if not best_tag or best_score == 0:
                    if category == 'time':
                        best_tag = 'T4'  # Default to modern period
                    elif category == 'discipline':
                        best_tag = 'DHIS'  # Default to history
                    elif category == 'memory_carrier':
                        best_tag = 'MCME'  # Default to media
                    elif category == 'concept_tags':
                        best_tag = 'CTCollectiveMemory'  # Default to collective memory
                
                predictions[category] = [best_tag]
                print(f"  🎯 Added {best_tag} to {category} category")
        
        # Also ensure we have at least 3 tags total (minimum requirement)
        total_tags = sum(len(tags) for tags in predictions.values())
        
        if total_tags < 3:
            print(f"  🔧 Adding additional tags to reach minimum 3 (currently have {total_tags})")
            
            # Add common tags based on text content
            if 'memory' in paper_text_lower and 'CTCollectiveMemory' not in predictions.get('concept_tags', []):
                predictions['concept_tags'].append('CTCollectiveMemory')
                total_tags += 1
                print(f"  🔧 Added CTCollectiveMemory (memory keyword found)")
            
            if 'history' in paper_text_lower or 'historical' in paper_text_lower:
                if 'DHIS' not in predictions.get('discipline', []):
                    predictions['discipline'].append('DHIS')
                    total_tags += 1
                    print(f"  🔧 Added DHIS (history keyword found)")
            
            if 'social' in paper_text_lower or 'society' in paper_text_lower:
                if 'DSOC' not in predictions.get('discipline', []):
                    predictions['discipline'].append('DSOC')
                    total_tags += 1
                    print(f"  🔧 Added DSOC (social keyword found)")
            
            # Add more concept tags if needed
            if total_tags < 3:
                additional_concept_tags = ['CTCulturalMemory', 'CTHistoricalMemory', 'CTSocialMemory']
                for tag in additional_concept_tags:
                    if tag not in predictions.get('concept_tags', []) and total_tags < 3:
                        predictions['concept_tags'].append(tag)
                        total_tags += 1
                        print(f"  🔧 Added {tag} (additional concept tag)")
        
        # Apply mutual exclusivity rules after adding all tags
        predictions = self._apply_mutual_exclusivity(predictions, paper_text)
        
        return predictions
    
    def _apply_mutual_exclusivity(self, predictions: Dict[str, List[str]], paper_text: str) -> Dict[str, List[str]]:
        """Apply mutual exclusivity rules for certain categories."""
        paper_text_lower = paper_text.lower()
        
        # Time periods should be mutually exclusive - keep only the most specific/relevant one
        if 'time' in predictions and len(predictions['time']) > 1:
            print(f"🕒 Multiple time tags detected: {predictions['time']}")
            
            # Priority order: T5 (most recent) > T4 > T3 > T2 > T1 (most ancient)
            time_priority = ['T5', 'T4', 'T3', 'T2', 'T1']
            
            # Find the highest priority time tag that was predicted
            selected_time = None
            for priority_tag in time_priority:
                if priority_tag in predictions['time']:
                    selected_time = priority_tag
                    break
            
            if selected_time:
                predictions['time'] = [selected_time]
                print(f"  🎯 Selected time tag: {selected_time} (highest priority)")
            else:
                # Fallback: use keyword analysis to determine the most appropriate time period
                time_scores = {}
                for tag in predictions['time']:
                    keywords = self.category_keywords.get('time', {}).get(tag, [])
                    score = sum(1 for keyword in keywords if keyword.lower() in paper_text_lower)
                    time_scores[tag] = score
                
                if time_scores:
                    best_time = max(time_scores, key=time_scores.get)
                    predictions['time'] = [best_time]
                    print(f"  🎯 Selected time tag: {best_time} (best keyword match)")
        
        # Memory carriers should be mutually exclusive - keep only the most relevant one
        if 'memory_carrier' in predictions and len(predictions['memory_carrier']) > 1:
            print(f"📺 Multiple memory carrier tags detected: {predictions['memory_carrier']}")
            
            # Use keyword analysis to find the most relevant memory carrier
            carrier_scores = {}
            for tag in predictions['memory_carrier']:
                keywords = self.category_keywords.get('memory_carrier', {}).get(tag, [])
                score = sum(1 for keyword in keywords if keyword.lower() in paper_text_lower)
                carrier_scores[tag] = score
            
            if carrier_scores:
                best_carrier = max(carrier_scores, key=carrier_scores.get)
                predictions['memory_carrier'] = [best_carrier]
                print(f"  🎯 Selected memory carrier: {best_carrier} (best keyword match)")
        
        return predictions
    
    def analyze_paper_for_prediction(self, paper_text: str) -> Dict[str, List[str]]:
        """Analyze paper text and provide detailed prediction analysis."""
        print(f"\n🔍 Analyzing paper: '{paper_text[:100]}...'")
        
        # Basic text analysis
        paper_text_lower = paper_text.lower()
        word_count = len(paper_text.split())
        
        print(f"  📊 Text length: {word_count} words")
        
        # Keyword analysis
        found_keywords = {}
        for category, category_keywords in self.category_keywords.items():
            category_found = []
            for tag, keywords in category_keywords.items():
                for keyword in keywords:
                    if keyword.lower() in paper_text_lower:
                        category_found.append((tag, keyword))
            
            if category_found:
                found_keywords[category] = category_found
        
        print(f"  🔍 Found keywords:")
        for category, keywords in found_keywords.items():
            category_name = self.matrix_categories[category].get('name', category.upper()) if isinstance(self.matrix_categories[category], dict) else category.upper()
            print(f"    {category_name}: {len(keywords)} keyword matches")
            for tag, keyword in keywords[:3]:  # Show top 3
                print(f"      - {tag}: '{keyword}'")
        
        # Get ML predictions
        ml_predictions = self.predict_tags_simple(paper_text)
        
        print(f"  🤖 ML Predictions:")
        for category, tags in ml_predictions.items():
            if tags:
                category_name = self.matrix_categories[category].get('name', category.upper()) if isinstance(self.matrix_categories[category], dict) else category.upper()
                print(f"    {category_name}: {', '.join(tags)}")
        
        return ml_predictions
    
    def save_models(self, filepath: str):
        """Save trained models to file."""
        model_data = {
            'models': self.models,
            'vectorizer': self.vectorizer,
            'matrix_categories': self.matrix_categories
        }
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"💾 Models saved to {filepath}")
    
    def load_models(self, filepath: str):
        """Load trained models from file."""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.models = model_data['models']
        self.vectorizer = model_data['vectorizer']
        self.matrix_categories = model_data['matrix_categories']
        print(f"📂 Models loaded from {filepath}")
    
    def analyze_tagged_papers(self, tagged_entries: List[Dict]):
        """Analyze the distribution of matrix tags in tagged papers."""
        print("\n=== MATRIX TAG ANALYSIS ===")
        
        # Count tags by category
        category_counts = {category: {} for category in self.matrix_categories.keys()}
        
        for entry in tagged_entries:
            matrix_tags = entry.get('matrix_tags', {})
            
            for category, tags in matrix_tags.items():
                for tag in tags:
                    if tag not in category_counts[category]:
                        category_counts[category][tag] = 0
                    category_counts[category][tag] += 1
        
        # Print analysis
        for category, counts in category_counts.items():
            # Handle both old and new matrix_categories structure
            if isinstance(self.matrix_categories[category], dict):
                # New structure with 'name' key
                category_name = self.matrix_categories[category].get('name', category.upper())
                descriptions = self.matrix_categories[category].get('descriptions', {})
            else:
                # Old structure
                category_name = category.upper()
                descriptions = {}
            
            print(f"\n📊 {category_name} ({category.upper()}):")
            
            if counts:
                sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
                for tag, count in sorted_counts:
                    description = descriptions.get(tag, '')
                    print(f"  {tag}: {count} papers - {description}")
            else:
                print("  No tags found")
        
        # Overall statistics
        total_papers = len(tagged_entries)
        total_tags = sum(len(tags) for entry in tagged_entries 
                        for tags in entry.get('matrix_tags', {}).values())
        
        print(f"\n📈 Overall Statistics:")
        print(f"  Total papers: {total_papers}")
        print(f"  Total matrix tags: {total_tags}")
        print(f"  Average tags per paper: {total_tags/total_papers:.1f}" if total_papers > 0 else "  Average tags per paper: 0")

def main():
    """Main function to demonstrate the matrix tagger."""
    tagger = BibTeXMatrixTagger()
    
    # Force retraining with new comprehensive system
    print("🔄 Retraining models with new comprehensive matrix tag system...")
    
    # Parse tagged papers
    tagged_entries = tagger.parse_bibtex_file('export-data (1).bib')
    
    if tagged_entries:
        # Train models with new system
        tagger.train_models(tagged_entries)
        
        # Save new models
        tagger.save_models('matrix_tagger_models_new.pkl')
        
        # Analyze tagged papers
        tagger.analyze_tagged_papers(tagged_entries)
    else:
        print("❌ No tagged papers found for training")
        return
    
    # Test prediction with enhanced analysis
    test_text = "Memory Unbound: The Holocaust and the Formation of Cosmopolitan Memory"
    predictions = tagger.analyze_paper_for_prediction(test_text)
    
    print(f"\n🧪 Final Prediction for: '{test_text}'")
    total_tags = sum(len(tags) for tags in predictions.values())
    print(f"📊 Total tags predicted: {total_tags}")
    
    for category, tags in predictions.items():
        if tags:
            category_name = tagger.matrix_categories[category].get('name', category.upper()) if isinstance(tagger.matrix_categories[category], dict) else category.upper()
            print(f"  {category_name}: {', '.join(tags)}")

if __name__ == "__main__":
    main() 