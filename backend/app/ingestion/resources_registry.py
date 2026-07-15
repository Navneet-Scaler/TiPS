"""Curated registry for the Resources tab: free datasets, tools, and
reference material - distinct from Learning (structured courses) and Open
Source (code contribution activity). This is "here's where to find the
raw material," not "here's a class to take" or "here's an issue to fix"."""

import logging
from datetime import datetime

from sqlalchemy.orm import Session

from ..models import Opportunity, Source
from .utils import filter_dead_urls, safe_add

logger = logging.getLogger("tips.ingestion.resources_registry")

REGISTRY_URL = "https://tips.local/registry/resource-platforms"

PROGRAMS = [
    dict(title="Papers with Code Datasets", organization="Papers with Code", url="https://paperswithcode.com/datasets",
         summary="Datasets indexed alongside the papers and benchmarks that use them."),
    dict(title="Hugging Face Datasets Hub", organization="Hugging Face", url="https://huggingface.co/datasets",
         summary="The largest open ML dataset hub, searchable and versioned."),
    dict(title="Google Dataset Search", organization="Google", url="https://datasetsearch.research.google.com/",
         summary="Search engine specifically for datasets across the open web."),
    dict(title="AWS Open Data Registry", organization="Amazon Web Services", url="https://registry.opendata.aws/",
         summary="Public datasets hosted free on AWS, spanning climate, genomics, and satellite imagery."),
    dict(title="Kaggle Datasets", organization="Kaggle", url="https://www.kaggle.com/datasets",
         summary="Community-uploaded datasets with built-in notebooks and starter code."),
    dict(title="Google AI Education Hub", organization="Google", url="https://ai.google/education/",
         summary="Free AI/ML learning material and educational resources from Google."),
    dict(title="Made With ML", organization="Made With ML", url="https://madewithml.com/",
         summary="Free, practical MLOps and applied ML course material and reference guides."),
    dict(title="fast.ai Course Materials", organization="fast.ai", url="https://course.fast.ai/",
         summary="Free deep learning course with open notebooks, widely used self-study resource."),
    dict(title="Awesome Machine Learning", organization="GitHub community", url="https://github.com/josephmisiti/awesome-machine-learning",
         summary="Community-curated list of ML frameworks, libraries, and reference resources by language."),
    dict(title="Awesome LLM Resources", organization="GitHub community", url="https://github.com/Hannibal046/Awesome-LLM",
         summary="Curated list of open LLM papers, tools, datasets, and tutorials."),
    dict(title="OpenAI Cookbook", organization="OpenAI", url="https://cookbook.openai.com/",
         summary="Practical guides and code examples for building with the OpenAI API."),
    dict(title="Anthropic Cookbook", organization="Anthropic", url="https://github.com/anthropics/anthropic-cookbook",
         summary="Practical guides and code examples for building with Claude."),
]


def ensure_source(db: Session) -> Source:
    source = db.query(Source).filter(Source.url == REGISTRY_URL).first()
    if not source:
        source = Source(name="Curated Resources Registry", type="registry", url=REGISTRY_URL, tier="tier3")
        db.add(source)
        db.commit()
        db.refresh(source)
    return source


def run(db: Session) -> dict:
    source = ensure_source(db)
    now = datetime.utcnow()
    new_count = 0

    unchecked = [p for p in PROGRAMS if not db.query(Opportunity).filter(Opportunity.url == p["url"]).first()]
    dead_urls = filter_dead_urls([p["url"] for p in unchecked])

    for program in unchecked:
        if program["url"] in dead_urls:
            logger.info("Skipping dead link for %s: %s", program["title"], program["url"])
            continue

        added = safe_add(db, Opportunity(
            title=program["title"],
            summary=program["summary"],
            url=program["url"],
            category="Resources",
            organization=program["organization"],
            geography="Global",
            is_remote=True,
            is_paid=False,
            is_rolling=True,
            published_at=now,
            discovered_at=now,
            updated_at=now,
            score=0.4,
            source_id=source.id,
        ))
        if added:
            new_count += 1

    source.last_fetched_at = now
    db.commit()
    return {"programs_added": new_count, "total_tracked": len(PROGRAMS)}
