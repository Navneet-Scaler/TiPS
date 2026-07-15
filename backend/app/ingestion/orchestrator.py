"""Runs every registered connector. Add a connector module with a run(db) -> dict
function and register it here - this is the single place that fans out ingestion."""

import logging

from sqlalchemy.orm import Session

from . import (
    rss,
    reddit,
    hackernews,
    github,
    greenhouse,
    research_registry,
    startup_registry,
    devpost,
    unstop,
    zindi,
    competitions_registry,
    huggingface_spaces,
    numerai,
    sitemap_watcher,
)

logger = logging.getLogger("tips.ingestion.orchestrator")

CONNECTORS = {
    "rss": rss.run_ingestion,
    "reddit": reddit.run,
    "hackernews": hackernews.run,
    "github": github.run,
    "greenhouse": greenhouse.run,
    "devpost": devpost.run,
    "unstop": unstop.run,
    "zindi": zindi.run,
    "huggingface_spaces": huggingface_spaces.run,
    "numerai": numerai.run,
    "sitemap_watcher": sitemap_watcher.run,
    "research_registry": research_registry.run,
    "startup_registry": startup_registry.run,
    "competitions_registry": competitions_registry.run,
}


def run_all(db: Session) -> dict:
    results = {}
    for name, run_fn in CONNECTORS.items():
        try:
            results[name] = run_fn(db)
        except Exception as exc:
            logger.exception("Connector %s failed entirely", name)
            results[name] = f"error: {exc}"
    return results
