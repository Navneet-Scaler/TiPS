"""Keyword-based classification. Deliberately simple for V1 -
swap for an LLM enrichment pass later without changing callers."""

from typing import Optional

CATEGORY_KEYWORDS = {
    "Career": ["hiring", "job", "career", "we're hiring", "join our team", "recruiting", "internship", "new grad"],
    "Research": ["research", "fellowship", "residency", "phd", "postdoc", "call for papers", "cfp", "paper"],
    "Learning": ["course", "workshop", "tutorial", "bootcamp", "webinar", "masterclass", "certification"],
    "Competitions": ["hackathon", "competition", "challenge", "kaggle"],
    "Funding": ["grant", "credits", "funding", "sponsorship", "scholarship"],
    "Open Source": ["open source", "github", "release", "sdk", "library", "contribute"],
    "Startup": ["accelerator", "incubator", "startup", "demo day", "pitch"],
    "Publishing": ["conference", "journal", "workshop track", "proceedings"],
    "Beta Programs": ["beta", "early access", "preview", "waitlist"],
}

DEFAULT_CATEGORY = "Community"

# Finer-grained Research sub-types, checked in order - first match wins.
# Ordering matters: "seeking collaborators" is checked first since it's the
# most time-sensitive and easy to miss inside a longer PhD/fellowship post.
RESEARCH_SUBCATEGORY_KEYWORDS = [
    ("Seeking Collaborators", [
        "seeking collaborator", "looking for collaborator", "seeking co-author",
        "looking for co-author", "open to collaboration", "call for collaboration",
        "collaborators wanted",
    ]),
    ("Recruiting Students", [
        "recruiting phd student", "accepting phd student", "looking for phd student",
        "accepting ra", "accepting ras", "hiring ra", "our lab is hiring",
        "recruiting ra", "lab is recruiting",
    ]),
    ("Compute Grant", [
        "compute grant", "gpu credits", "tpu research cloud", "researcher access program",
        "compute allocation", "cloud credits for research", "academic access",
    ]),
    ("Undergrad Research", [
        "reu", "urop", "surf program", "undergraduate research", "amgen scholars",
    ]),
    ("Government Program", [
        "darpa", "iarpa", "nsf award", "horizon europe", "ukri", "grants.gov",
        "nih reporter", "national science foundation",
    ]),
    ("PhD Fellowship", [
        "phd fellowship", "graduate fellowship", "doctoral fellowship", "phd scholar",
    ]),
    ("Fellowship", [
        "fellowship", "residency", "visiting researcher", "visiting scholar",
    ]),
    ("PhD / Postdoc", [
        "phd position", "postdoc", "post-doc", "predoc", "pre-doc", "doctoral position",
    ]),
]


def classify(title: str, summary: str) -> str:
    text = f"{title} {summary or ''}".lower()
    best_category = DEFAULT_CATEGORY
    best_hits = 0
    for category, keywords in CATEGORY_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in text)
        if hits > best_hits:
            best_hits = hits
            best_category = category
    return best_category


def classify_research_subcategory(title: str, summary: str) -> Optional[str]:
    text = f"{title} {summary or ''}".lower()
    for subcategory, keywords in RESEARCH_SUBCATEGORY_KEYWORDS:
        if any(kw in text for kw in keywords):
            return subcategory
    return None


# Startup tab sub-types, ordered so more specific programs win over the
# generic "accelerator" bucket. dilution_type is inferred separately below.
STARTUP_SUBCATEGORY_KEYWORDS = [
    ("Co-founder Matching", [
        "looking for a co-founder", "seeking co-founder", "co-founder matching", "cofounder matching",
    ]),
    ("Compute/Credit Program", [
        "gpu credits", "cloud credits", "compute credits", "api credits", "credits for startups",
    ]),
    ("Pitch Competition", [
        "pitch competition", "pitch contest", "cash prize", "pitch day",
    ]),
    ("Demo Day", [
        "demo day",
    ]),
    ("Venture Studio", [
        "venture studio", "co-building", "pre-team",
    ]),
    ("Founder Fellowship", [
        "founder fellowship", "entrepreneur in residence", "eir program",
    ]),
    ("Startup Visa / Relocation", [
        "startup visa", "global talent visa", "tech visa", "relocation program",
    ]),
    ("Grant (non-dilutive)", [
        "non-dilutive", "non dilutive", "startup grant", "innovation grant", "seed fund scheme",
    ]),
    ("Incubator", [
        "incubator", "incubation",
    ]),
    ("Accelerator", [
        "accelerator", "cohort", "batch",
    ]),
]

DILUTION_EQUITY_KEYWORDS = ["equity", "safe note", "convertible", "% stake", "takes equity"]
DILUTION_NONDILUTIVE_KEYWORDS = [
    "equity-free", "equity free", "non-dilutive", "non dilutive", "no equity",
    "free gpu", "free credits", "grant", "no stake",
]


def classify_startup_subcategory(title: str, summary: str) -> Optional[str]:
    text = f"{title} {summary or ''}".lower()
    for subcategory, keywords in STARTUP_SUBCATEGORY_KEYWORDS:
        if any(kw in text for kw in keywords):
            return subcategory
    return None


def classify_dilution_type(title: str, summary: str) -> str:
    text = f"{title} {summary or ''}".lower()
    if any(kw in text for kw in DILUTION_NONDILUTIVE_KEYWORDS):
        return "non-dilutive"
    if any(kw in text for kw in DILUTION_EQUITY_KEYWORDS):
        return "equity"
    return "unknown"


FUNDED_KEYWORDS = [
    "funded", "stipend", "salary", "paid fellowship", "compensation", "living stipend",
    "grant of", "$", "fully funded",
]


def is_funded(title: str, summary: str) -> bool:
    text = f"{title} {summary or ''}".lower()
    return any(kw in text for kw in FUNDED_KEYWORDS)


def score(published_recency_days: float) -> float:
    if published_recency_days <= 1:
        return 1.0
    if published_recency_days <= 7:
        return 0.7
    if published_recency_days <= 30:
        return 0.4
    return 0.1
