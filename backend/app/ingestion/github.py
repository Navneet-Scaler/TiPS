"""Tier 1 connector: GitHub public REST API (no auth for low-volume search).
Covers new repos per AI topic and open 'good first issue' bounties -
one connector, many repos, per the plan's connector-not-scraper principle."""

import logging
from datetime import datetime, timedelta

import httpx
from sqlalchemy.orm import Session

from ..models import Opportunity, Source
from .sources import GITHUB_TOPICS
from .utils import safe_add

logger = logging.getLogger("tips.ingestion.github")

HEADERS = {"Accept": "application/vnd.github+json", "User-Agent": "tips-opportunity-radar"}


def ensure_source(db: Session) -> Source:
    source = db.query(Source).filter(Source.url == "https://github.com").first()
    if not source:
        source = Source(name="GitHub", type="github", url="https://github.com", tier="tier1")
        db.add(source)
        db.commit()
        db.refresh(source)
    return source


def run(db: Session) -> dict:
    source = ensure_source(db)
    now = datetime.utcnow()
    since = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    results = {}

    with httpx.Client() as client:
        # New/trending repositories per topic
        for topic in GITHUB_TOPICS:
            new_count = 0
            try:
                resp = client.get(
                    "https://api.github.com/search/repositories",
                    params={"q": f"topic:{topic} created:>{since}", "sort": "stars", "order": "desc", "per_page": 10},
                    headers=HEADERS,
                    timeout=10,
                )
                resp.raise_for_status()
                items = resp.json().get("items", [])
            except Exception as exc:
                logger.warning("GitHub repo search failed for topic %s: %s", topic, exc)
                results[f"topic:{topic}"] = f"error: {exc}"
                continue

            for repo in items:
                url = repo.get("html_url")
                if not url or db.query(Opportunity).filter(Opportunity.url == url).first():
                    continue

                added = safe_add(db, Opportunity(
                    title=f"New repo: {repo.get('full_name')}",
                    summary=repo.get("description"),
                    url=url,
                    category="Open Source",
                    organization=repo.get("owner", {}).get("login"),
                    geography="Global",
                    published_at=now,
                    discovered_at=now,
                    updated_at=now,
                    score=0.8,
                    source_id=source.id,
                ))
                if added:
                    new_count += 1
            results[f"topic:{topic}"] = new_count

        # Good first issues on AI repos
        try:
            resp = client.get(
                "https://api.github.com/search/issues",
                params={"q": "label:\"good first issue\" language:python state:open ai OR llm OR ml", "sort": "created", "order": "desc", "per_page": 20},
                headers=HEADERS,
                timeout=10,
            )
            resp.raise_for_status()
            issues = resp.json().get("items", [])
        except Exception as exc:
            logger.warning("GitHub issue search failed: %s", exc)
            issues = []
            results["good_first_issues"] = f"error: {exc}"

        new_count = 0
        for issue in issues:
            url = issue.get("html_url")
            if not url or db.query(Opportunity).filter(Opportunity.url == url).first():
                continue

            repo_name = issue.get("repository_url", "").split("/repos/")[-1]
            added = safe_add(db, Opportunity(
                title=issue.get("title", "Untitled issue"),
                summary=f"Good first issue in {repo_name}",
                url=url,
                category="Open Source",
                subcategory="Good First Issue",
                organization=repo_name,
                geography="Global",
                published_at=now,
                discovered_at=now,
                updated_at=now,
                score=0.6,
                source_id=source.id,
            ))
            if added:
                new_count += 1
        if "good_first_issues" not in results:
            results["good_first_issues"] = new_count

    source.last_fetched_at = now
    db.commit()
    return results
