"""Tier 2 connector: generic sitemap-based opportunity watcher.
Works for ANY site exposing a standard sitemap.xml (a lot of university and
lab sites do, even without RSS) - fetches candidate URLs whose slug looks
opportunity-shaped, pulls the real page title, and runs it through the same
Research gate every other source uses. Extensible by adding one config row
in sources.SITEMAP_WATCH_SOURCES - no per-site parsing logic required."""

import logging
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from xml.etree import ElementTree as ET

import httpx
from sqlalchemy.orm import Session

from ..classify import classify, classify_research_subcategory, gate_category
from ..models import Opportunity, Source
from .sources import SITEMAP_WATCH_SOURCES
from .utils import safe_add

logger = logging.getLogger("tips.ingestion.sitemap_watcher")

NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

OPPORTUNITY_URL_KEYWORDS = [
    "fellow", "postdoc", "post-doc", "phd", "hiring", "recruit", "join-us",
    "joinus", "opportunit", "grant", "scholar", "internship", "open-position",
    "openposition", "vacancy", "position", "apply",
]

MAX_CANDIDATE_URLS = 15
MAX_SITEMAP_INDEX_CHILDREN = 3
HEADERS = {"User-Agent": "Mozilla/5.0 tips-opportunity-radar/0.1"}


def _looks_like_opportunity(url: str) -> bool:
    slug = url.lower()
    return any(kw in slug for kw in OPPORTUNITY_URL_KEYWORDS)


def _parse_sitemap_xml(content: bytes):
    """Returns (urls, child_sitemaps) - exactly one of the two is populated,
    depending on whether this was a <urlset> or a <sitemapindex>."""
    root = ET.fromstring(content)
    tag = root.tag.split("}")[-1]
    if tag == "sitemapindex":
        children = [
            el.find("sm:loc", NS).text
            for el in root.findall("sm:sitemap", NS)
            if el.find("sm:loc", NS) is not None
        ]
        return None, children
    urls = [
        el.find("sm:loc", NS).text
        for el in root.findall("sm:url", NS)
        if el.find("sm:loc", NS) is not None
    ]
    return urls, None


def _collect_candidate_urls(client: httpx.Client, sitemap_url: str) -> list:
    try:
        resp = client.get(sitemap_url, timeout=15)
        resp.raise_for_status()
        urls, child_sitemaps = _parse_sitemap_xml(resp.content)
    except Exception as exc:
        logger.warning("Sitemap fetch failed for %s: %s", sitemap_url, exc)
        return []

    if urls is None and child_sitemaps:
        urls = []
        for child_url in child_sitemaps[:MAX_SITEMAP_INDEX_CHILDREN]:
            try:
                child_resp = client.get(child_url, timeout=15)
                child_resp.raise_for_status()
                child_urls, _ = _parse_sitemap_xml(child_resp.content)
                urls.extend(child_urls or [])
            except Exception as exc:
                logger.warning("Child sitemap fetch failed for %s: %s", child_url, exc)

    matches = [u for u in (urls or []) if _looks_like_opportunity(u)]
    return matches[:MAX_CANDIDATE_URLS]


def _fetch_title(url: str):
    """Standalone (no shared client) so it's safe to call from a thread pool -
    title fetches across every site are the slow part of this connector, and
    running them one at a time made a full run take minutes."""
    try:
        resp = httpx.get(url, timeout=10, headers=HEADERS, follow_redirects=True)
        resp.raise_for_status()
        match = re.search(r"<title[^>]*>(.*?)</title>", resp.text, re.IGNORECASE | re.DOTALL)
        if match:
            return re.sub(r"\s+", " ", match.group(1)).strip()
    except Exception as exc:
        logger.info("Could not fetch title for %s: %s", url, exc)
    return None


def ensure_source(db: Session, name: str, url: str) -> Source:
    source = db.query(Source).filter(Source.url == url).first()
    if not source:
        source = Source(name=name, type="sitemap", url=url, tier="tier2")
        db.add(source)
        db.commit()
        db.refresh(source)
    return source


def run(db: Session) -> dict:
    now = datetime.utcnow()
    results = {}
    sources_by_cfg = {}
    per_site_new_urls = {}

    with httpx.Client(follow_redirects=True, headers=HEADERS) as client:
        for cfg in SITEMAP_WATCH_SOURCES:
            source = ensure_source(db, cfg["name"], cfg["sitemap_url"])
            sources_by_cfg[cfg["name"]] = source

            candidates = _collect_candidate_urls(client, cfg["sitemap_url"])
            new_urls = [u for u in candidates if not db.query(Opportunity).filter(Opportunity.url == u).first()]
            per_site_new_urls[cfg["name"]] = new_urls

    # Title fetches are the slow, purely I/O-bound part - do them all
    # concurrently across every site instead of one request at a time.
    all_urls = [u for urls in per_site_new_urls.values() for u in urls]
    titles_by_url = {}
    if all_urls:
        with ThreadPoolExecutor(max_workers=16) as pool:
            for url, title in zip(all_urls, pool.map(_fetch_title, all_urls)):
                titles_by_url[url] = title

    for cfg in SITEMAP_WATCH_SOURCES:
        source = sources_by_cfg[cfg["name"]]
        new_count = 0

        for url in per_site_new_urls[cfg["name"]]:
            title = titles_by_url.get(url)
            if not title:
                continue

            category = gate_category(classify(title, ""), title, "")
            if category != "Research":
                continue

            added = safe_add(db, Opportunity(
                title=title,
                summary=f"Found via {cfg['organization']}'s site.",
                url=url,
                category="Research",
                subcategory=classify_research_subcategory(title, ""),
                organization=cfg["organization"],
                geography="Global",
                published_at=now,
                discovered_at=now,
                updated_at=now,
                score=0.5,
                source_id=source.id,
            ))
            if added:
                new_count += 1

        source.last_fetched_at = now
        db.commit()
        results[cfg["name"]] = new_count

    return results
