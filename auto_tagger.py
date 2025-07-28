from config import TIME_PERIODS, DISCIPLINES, MEMORY_CARRIERS, KEY_CONCEPTS, METHODS
import re

class MnemonicTagger:
    def __init__(self):
        # Lowercase keyword maps for simple matching
        self.time_periods = TIME_PERIODS
        self.disciplines = [d.lower() for d in DISCIPLINES]
        self.memory_carriers = [m.lower() for m in MEMORY_CARRIERS]
        self.key_concepts = [c.lower() for c in KEY_CONCEPTS]
        self.methods = [m.lower() for m in METHODS]

    def categorize(self, paper):
        text = f"{paper.title} {paper.abstract or ''}"
        tags = {"time": [], "disciplines": [], "memory_carriers": [], "concepts": [], "methods": []}
        scores = {"disciplines": 0.0, "concepts": 0.0}

        # Time: by year
        year = None
        if paper.date:
            match = re.search(r"(\d{4})", paper.date)
            if match:
                year = int(match.group(1))
        if year:
            if year < 1860:
                tags["time"].append("T1")
            elif year < 1950:
                tags["time"].append("T2")
            elif year < 1990:
                tags["time"].append("T3")
            elif year < 2000:
                tags["time"].append("T4")
            else:
                tags["time"].append("T5")

        # Disciplines: look for discipline codes in tags, collections, or text
        found_disciplines = []
        for d in self.disciplines:
            if d in [t.lower() for t in paper.tags + paper.collections] or d in text.lower():
                found_disciplines.append(d.upper())
        tags["disciplines"] = found_disciplines
        scores["disciplines"] = 1.0 if found_disciplines else 0.0

        # Memory Carriers: look for carrier codes in tags or text
        found_carriers = []
        for m in self.memory_carriers:
            if m in [t.lower() for t in paper.tags] or m in text.lower():
                found_carriers.append(m.upper())
        tags["memory_carriers"] = found_carriers

        # Concepts: look for concept keywords in text
        found_concepts = []
        for c in self.key_concepts:
            if c.replace('_', ' ') in text.lower() or c in text.lower():
                found_concepts.append(c)
        tags["concepts"] = found_concepts
        scores["concepts"] = 1.0 if found_concepts else 0.0

        # Methods: look for method codes in tags or text
        found_methods = []
        for m in self.methods:
            if m in [t.lower() for t in paper.tags] or m in text.lower():
                found_methods.append(m.upper())
        tags["methods"] = found_methods

        return tags, scores 