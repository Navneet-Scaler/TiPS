"""Curated registry for the Recognition tab: awards, fellows programs, and
rankings that AI/ML researchers and practitioners can be nominated for or
apply to. Unlike Research/Competitions, retrospective language ("X won...")
is exactly the point here, not noise - see gate_category, which doesn't
gate this category at all."""

import logging
from datetime import datetime

from sqlalchemy.orm import Session

from ..models import Opportunity, Source
from .utils import filter_dead_urls, safe_add

logger = logging.getLogger("tips.ingestion.recognition_registry")

REGISTRY_URL = "https://tips.local/registry/recognition-programs"

PROGRAMS = [
    dict(title="ACM A.M. Turing Award", organization="ACM", url="https://amturing.acm.org/",
         summary="Computing's highest honor, frequently awarded to AI/ML pioneers."),
    dict(title="AAAI Fellows Program", organization="AAAI", url="https://aaai.org/about-aaai/aaai-fellows/",
         summary="Recognizes significant, sustained contributions to AI - nomination-based."),
    dict(title="ACL Fellows", organization="Association for Computational Linguistics", url="https://www.aclweb.org/portal/acl-fellows",
         summary="Recognizes outstanding contributions to computational linguistics and NLP."),
    dict(title="IEEE Fellow Program", organization="IEEE", url="https://www.ieee.org/membership/fellows/index.html",
         summary="IEEE's highest grade of membership, recognizes extraordinary technical contributions."),
    dict(title="Sloan Research Fellowship", organization="Alfred P. Sloan Foundation", url="https://sloan.org/fellowships",
         summary="Early-career award for researchers, strong representation from AI/ML/CS."),
    dict(title="MacArthur Fellowship", organization="MacArthur Foundation", url="https://www.macfound.org/programs/fellows/",
         summary="The 'genius grant' - unrestricted award, has recognized several AI researchers."),
    dict(title="AI2050 Fellows", organization="Schmidt Sciences", url="https://ai2050.schmidtsciences.org/fellows/",
         summary="Recognizes researchers tackling hard problems in AI safety and society."),
    dict(title="Kaggle Rankings & Grandmaster Tiers", organization="Kaggle", url="https://www.kaggle.com/rankings",
         summary="Competitive data science ranking system - Grandmaster is the top public recognition tier."),
    dict(title="NeurIPS Test of Time Award", organization="NeurIPS", url="https://neurips.cc/",
         summary="Annual award recognizing a past paper with the most lasting impact on the field."),
    dict(title="ACM SIGAI Autonomous Agents Award", organization="ACM SIGAI", url="https://sigai.acm.org/",
         summary="Recognizes influential research contributions in autonomous agents and multi-agent systems."),
    dict(title="Women in Machine Learning Awards", organization="WiML", url="https://wimlworkshop.org/",
         summary="Recognizes contributions from women in the machine learning research community."),
    dict(title="Rising Stars in AI/ML/EECS", organization="Various universities", url="https://risingstars-eecs.mit.edu/",
         summary="Academic career workshop and recognition program for early-career women in AI/EECS."),
]


def ensure_source(db: Session) -> Source:
    source = db.query(Source).filter(Source.url == REGISTRY_URL).first()
    if not source:
        source = Source(name="Curated Recognition Programs Registry", type="registry", url=REGISTRY_URL, tier="tier3")
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
            category="Recognition",
            organization=program["organization"],
            geography="Global",
            is_remote=True,
            is_paid=True,
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
