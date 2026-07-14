"""Shared insert helper. Commits one opportunity at a time so a single duplicate
or constraint violation can't roll back an entire connector's batch."""

import logging

import httpx
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models import Opportunity

logger = logging.getLogger("tips.ingestion.utils")


def safe_add(db: Session, opportunity: Opportunity) -> bool:
    db.add(opportunity)
    try:
        db.commit()
        return True
    except IntegrityError:
        db.rollback()
        return False


def url_is_dead(url: str) -> bool:
    """Confirms a URL is actually gone (404/410) before we skip a curated
    registry entry over it. Any other outcome - timeout, block, redirect,
    5xx - is treated as "can't tell" rather than dead, since plenty of sites
    reject HEAD requests or bot-like traffic without the program itself
    being gone."""
    try:
        resp = httpx.head(url, timeout=8, follow_redirects=True)
        if resp.status_code in (404, 410):
            return True
        if resp.status_code == 405:  # HEAD not allowed - confirm with GET instead
            resp = httpx.get(url, timeout=8, follow_redirects=True)
            return resp.status_code in (404, 410)
        return False
    except Exception as exc:
        logger.info("Could not verify %s (%s) - keeping it", url, exc)
        return False
