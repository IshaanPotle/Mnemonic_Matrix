import json
import random
from datetime import datetime

disciplines = ["DSOC", "DHIS", "DPSY", "DLIT", "DCUL", "DPOL", "DLAW", "DMU"]
carriers = ["MCLI", "MCFI", "MCMO", "MCSO", "MCLA", "MCED"]
concepts = ["cultural_memory", "collective_memory", "trauma", "post_memory", "digital_memory", "cosmopolitan_memory"]
methods = ["MEARC", "MEINT", "MEETH", "MESUR", "MENET"]

items = []
for i in range(1, 101):
    key = f"PAPER{i}"
    title = f"Dummy Paper Title {i}"
    creators = [{"firstName": f"Author{i}", "lastName": f"Last{i}"}]
    year = random.choice(range(1850, datetime.now().year + 1))
    date = str(year)
    item_type = random.choice(["book", "journalArticle"])
    publisher = f"Publisher {random.randint(1, 20)}" if item_type == "book" else None
    publication_title = f"Journal {random.randint(1, 20)}" if item_type == "journalArticle" else None
    abstract = f"This is a dummy abstract for paper {i} about {random.choice(concepts)}."
    tags = random.sample(disciplines + carriers + concepts + methods, k=random.randint(1, 4))
    collections = [f"Collection {random.randint(1, 10)}"]
    # Citations: each paper can cite up to 5 previous papers
    if i > 1:
        citations = [f"PAPER{random.randint(1, i-1)}" for _ in range(random.randint(0, min(5, i-1)))]
        citations = list(set(citations))
    else:
        citations = []
    item = {
        "key": key,
        "title": title,
        "creators": creators,
        "date": date,
        "itemType": item_type,
        "publisher": publisher,
        "publicationTitle": publication_title,
        "abstract": abstract,
        "tags": tags,
        "collections": collections,
        "citations": citations
    }
    # Remove None fields for JSON cleanliness
    item = {k: v for k, v in item.items() if v is not None}
    items.append(item)

with open("sample_zotero_large.json", "w", encoding="utf-8") as f:
    json.dump({"items": items}, f, indent=2, ensure_ascii=False)
print("Generated sample_zotero_large.json with 100 dummy papers.") 