"""Curated registry for the Beta Programs tab: closed betas, research
previews, and early-access programs run directly by AI labs and platforms."""

import logging
from datetime import datetime

from sqlalchemy.orm import Session

from ..models import Opportunity, Source
from .utils import filter_dead_urls, safe_add

logger = logging.getLogger("tips.ingestion.beta_registry")

REGISTRY_URL = "https://tips.local/registry/beta-programs"

PROGRAMS = [
    dict(title="Google Labs", organization="Google", url="https://labs.google/",
         summary="Google's experimental AI products hub - sign up for early access to unreleased tools."),
    dict(title="Anthropic Early Access", organization="Anthropic", url="https://www.anthropic.com/contact-sales",
         summary="Request early access to new Claude capabilities and enterprise features."),
    dict(title="Meta AI Blog - Product Previews", organization="Meta AI", url="https://ai.meta.com/blog/",
         summary="Announcements and sign-ups for Meta's experimental AI models and research previews."),
    dict(title="GitHub Next", organization="GitHub", url="https://githubnext.com/",
         summary="GitHub's incubator for experimental developer tools, several open for early testing."),
    dict(title="Mistral La Plateforme", organization="Mistral AI", url="https://mistral.ai/products/la-plateforme",
         summary="Mistral's API platform - new model previews often ship here first."),
    dict(title="OpenAI Researcher Access Program", organization="OpenAI", url="https://openai.com/form/researcher-access-program/",
         summary="Early API access track for researchers studying safety and societal impact."),
    dict(title="Perplexity Labs", organization="Perplexity", url="https://www.perplexity.ai/hub",
         summary="Perplexity's experimental features and product announcements hub."),
]


def ensure_source(db: Session) -> Source:
    source = db.query(Source).filter(Source.url == REGISTRY_URL).first()
    if not source:
        source = Source(name="Curated Beta Programs Registry", type="registry", url=REGISTRY_URL, tier="tier3")
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
            category="Beta Programs",
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
