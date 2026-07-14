"""Keyword-based classification. Deliberately simple for V1 -
swap for an LLM enrichment pass later without changing callers."""

import re
from typing import Optional


def _has_keyword(text: str, keyword: str) -> bool:
    """Word-boundary match - a plain `in` check would match "residency"
    inside "presidency" or "ai" inside half the English language. Symbol-only
    keywords (e.g. "$") have no word boundary to anchor on, so those fall
    back to a plain substring check."""
    if not keyword[0].isalnum() and not keyword[-1].isalnum():
        return keyword in text
    return re.search(rf"\b{re.escape(keyword)}\b", text) is not None


def _any_keyword(text: str, keywords: list) -> bool:
    return any(_has_keyword(text, kw) for kw in keywords)

CATEGORY_KEYWORDS = {
    "Career": ["hiring", "job", "career", "we're hiring", "join our team", "recruiting", "internship", "new grad"],
    "Research": ["fellowship", "residency", "postdoc", "call for papers", "cfp", "research grant", "phd position"],
    "Learning": ["course", "workshop", "tutorial", "bootcamp", "webinar", "masterclass", "certification"],
    "Competitions": ["hackathon", "kaggle competition", "pitch competition", "case competition", "coding challenge"],
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
        hits = sum(1 for kw in keywords if _has_keyword(text, kw))
        if hits > best_hits:
            best_hits = hits
            best_category = category
    return best_category


def classify_research_subcategory(title: str, summary: str) -> Optional[str]:
    text = f"{title} {summary or ''}".lower()
    for subcategory, keywords in RESEARCH_SUBCATEGORY_KEYWORDS:
        if _any_keyword(text, keywords):
            return subcategory
    return None


# Competition sub-types. Requires an actual "you can enter this" signal -
# a paper that happens to use the word "challenge" in its abstract must not
# match here, which is why single generic words are avoided.
COMPETITION_SUBCATEGORY_KEYWORDS = [
    ("Hackathon", [
        "hackathon", "hack night", "build weekend", "submit your project", "start a submission",
    ]),
    ("ML Competition", [
        "kaggle competition", "leaderboard", "benchmark competition", "shared task",
    ]),
    ("Pitch Competition", [
        "pitch competition", "pitch contest", "demo day pitch",
    ]),
    ("Case Competition", [
        "case competition",
    ]),
    ("Government Challenge", [
        "grand challenge", "innovation challenge", "national challenge",
    ]),
]


def classify_competition_subcategory(title: str, summary: str) -> Optional[str]:
    text = f"{title} {summary or ''}".lower()
    for subcategory, keywords in COMPETITION_SUBCATEGORY_KEYWORDS:
        if _any_keyword(text, keywords):
            return subcategory
    return None


# AI/ML sub-field tagging - checked in order, first match wins, so more
# specific sub-fields are listed before the broader parent field they'd
# otherwise be absorbed into (e.g. "Autonomous Driving" before "Robotics").
# This is a "nice to have" tag on top of category/subcategory, not a gate.
AI_DOMAIN_KEYWORDS = [
    ("Agents", ["agent", "agentic", "autonomous agent", "multi-agent", "tool use", "mcp"]),
    ("Autonomous Driving", ["autonomous driving", "self-driving", "driverless", "adas"]),
    ("Object Detection & Segmentation", ["object detection", "segmentation", "instance segmentation", "semantic segmentation"]),
    ("3D / Point Cloud", ["point cloud", "3d reconstruction", "lidar", "depth estimation"]),
    ("Computer Vision", ["computer vision", "image recognition", "image classification", "vision"]),
    ("Speech", ["speech recognition", "asr", "text-to-speech", "voice ai", "audio"]),
    ("Machine Translation", ["machine translation", "translation task"]),
    ("Question Answering", ["question answering", "qa benchmark", "reading comprehension"]),
    ("NLP", ["nlp", "language model", "llm", "text generation", "chatbot", "named entity"]),
    ("Robotics", ["robotics", "robot", "manipulation", "humanoid"]),
    ("Reinforcement Learning", ["reinforcement learning", "rl agent", "policy learning", "game playing"]),
    ("Multimodal / Generative", ["generative ai", "diffusion", "text-to-image", "multimodal", "genai", "image generation"]),
    ("Healthcare / Medical AI", ["medical imaging", "clinical", "healthcare ai", "biomedical", "genomics", "protein"]),
    ("Drug Discovery", ["drug discovery", "molecular", "therapeutics", "molecule"]),
    ("Climate / Earth Observation", ["climate", "earth observation", "satellite imagery", "remote sensing", "weather forecasting", "flood"]),
    ("Finance / Quant", ["quant", "trading", "algorithmic trading", "financial modeling"]),
    ("Recommender Systems", ["recommender system", "recommendation engine", "collaborative filtering"]),
    ("Graph ML", ["graph neural network", "graph ml", "knowledge graph"]),
    ("Time Series", ["time series", "forecasting model", "anomaly detection"]),
    ("Federated Learning", ["federated learning", "on-device learning"]),
    ("Data Science", ["data science", "kaggle", "datathon", "predictive modeling"]),
    ("AI Safety", ["ai safety", "alignment", "interpretability", "red team"]),
]


def classify_ai_domain(title: str, summary: str) -> Optional[str]:
    text = f"{title} {summary or ''}".lower()
    for domain, keywords in AI_DOMAIN_KEYWORDS:
        if _any_keyword(text, keywords):
            return domain
    return None


# Categories that require a real opportunity-shaped signal before an item is
# allowed to stay in them - without this, a paper abstract that happens to
# contain "research" or "challenges" gets bucketed as an actual opportunity.
# Anything that fails its gate falls back to the generic Community bucket
# rather than being dropped, since it may still be useful signal there.
GATED_CATEGORIES = {
    "Research": classify_research_subcategory,
    "Competitions": classify_competition_subcategory,
}


def gate_category(category: str, title: str, summary: str) -> str:
    gate_fn = GATED_CATEGORIES.get(category)
    if gate_fn is None:
        return category
    return category if gate_fn(title, summary) else DEFAULT_CATEGORY


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
        if _any_keyword(text, keywords):
            return subcategory
    return None


def classify_dilution_type(title: str, summary: str) -> str:
    text = f"{title} {summary or ''}".lower()
    if _any_keyword(text, DILUTION_NONDILUTIVE_KEYWORDS):
        return "non-dilutive"
    if _any_keyword(text, DILUTION_EQUITY_KEYWORDS):
        return "equity"
    return "unknown"


FUNDED_KEYWORDS = [
    "funded", "stipend", "salary", "paid fellowship", "compensation", "living stipend",
    "grant of", "$", "fully funded",
]


def is_funded(title: str, summary: str) -> bool:
    text = f"{title} {summary or ''}".lower()
    return _any_keyword(text, FUNDED_KEYWORDS)


def score(published_recency_days: float) -> float:
    if published_recency_days <= 1:
        return 1.0
    if published_recency_days <= 7:
        return 0.7
    if published_recency_days <= 30:
        return 0.4
    return 0.1
