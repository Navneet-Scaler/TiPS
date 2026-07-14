"""Shared insert helper. Commits one opportunity at a time so a single duplicate
or constraint violation can't roll back an entire connector's batch."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models import Opportunity


def safe_add(db: Session, opportunity: Opportunity) -> bool:
    db.add(opportunity)
    try:
        db.commit()
        return True
    except IntegrityError:
        db.rollback()
        return False
