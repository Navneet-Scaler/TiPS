"""One-off + repeatable cleanup for rows ingested before the Research/
Competitions opportunity-gate existed. Safe to run any time - it only
deletes rows from sources that were removed entirely, and re-gates
everything else through the current classifier."""

import logging

from sqlalchemy.orm import Session

from ..classify import gate_category
from ..models import Opportunity

logger = logging.getLogger("tips.ingestion.cleanup")

# Sources removed outright (papers / noisy generic search) - no amount of
# re-gating salvages these, they were never opportunities.
REMOVED_SOURCE_ORGANIZATIONS = ["arXiv", "OpenReview"]


def run_cleanup(db: Session) -> dict:
    deleted = 0
    for org in REMOVED_SOURCE_ORGANIZATIONS:
        count = db.query(Opportunity).filter(Opportunity.organization == org).delete(synchronize_session=False)
        deleted += count
    db.commit()

    reclassified = 0
    rows = db.query(Opportunity).filter(Opportunity.category.in_(["Research", "Competitions"])).all()
    for row in rows:
        gated = gate_category(row.category, row.title, row.summary or "")
        if gated != row.category:
            row.category = gated
            row.subcategory = None
            reclassified += 1
    db.commit()

    return {"deleted_dead_source_rows": deleted, "reclassified_rows": reclassified}
