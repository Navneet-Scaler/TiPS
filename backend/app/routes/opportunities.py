from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Opportunity
from ..schemas import OpportunityOut, StatsOut

router = APIRouter(prefix="/api/opportunities", tags=["opportunities"])


@router.get("", response_model=list[OpportunityOut])
def list_opportunities(
    db: Session = Depends(get_db),
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    q: Optional[str] = None,
    geography: Optional[str] = None,
    is_remote: Optional[bool] = None,
    is_paid: Optional[bool] = None,
    dilution_type: Optional[str] = None,
    is_rolling: Optional[bool] = None,
    tier: Optional[str] = None,
    domain: Optional[str] = None,
    include_expired: bool = False,
    sort: str = Query("recent", pattern="^(recent|trending)$"),
    limit: int = 60,
    offset: int = 0,
):
    query = db.query(Opportunity)

    if not include_expired:
        now = datetime.utcnow()
        query = query.filter(or_(Opportunity.deadline.is_(None), Opportunity.deadline >= now))

    if category:
        query = query.filter(Opportunity.category == category)
    if subcategory:
        query = query.filter(Opportunity.subcategory == subcategory)
    if geography:
        query = query.filter(Opportunity.geography == geography)
    if is_remote is not None:
        query = query.filter(Opportunity.is_remote == is_remote)
    if is_paid is not None:
        query = query.filter(Opportunity.is_paid == is_paid)
    if dilution_type:
        query = query.filter(Opportunity.dilution_type == dilution_type)
    if is_rolling is not None:
        query = query.filter(Opportunity.is_rolling == is_rolling)
    if tier:
        query = query.filter(Opportunity.tier == tier)
    if domain:
        query = query.filter(Opportunity.domain == domain)
    if q:
        like = f"%{q}%"
        query = query.filter((Opportunity.title.ilike(like)) | (Opportunity.summary.ilike(like)) | (Opportunity.organization.ilike(like)))

    if sort == "trending":
        query = query.order_by(Opportunity.score.desc(), Opportunity.published_at.desc())
    else:
        query = query.order_by(Opportunity.published_at.desc())

    return query.offset(offset).limit(limit).all()


@router.get("/timeline", response_model=list[OpportunityOut])
def timeline(db: Session = Depends(get_db), hours: int = 48, limit: int = 100):
    since = datetime.utcnow() - timedelta(hours=hours)
    return (
        db.query(Opportunity)
        .filter(Opportunity.discovered_at >= since)
        .order_by(Opportunity.discovered_at.desc())
        .limit(limit)
        .all()
    )


@router.get("/research/subcategories")
def research_subcategories(db: Session = Depends(get_db)):
    rows = (
        db.query(Opportunity.subcategory, func.count(Opportunity.id))
        .filter(Opportunity.category == "Research")
        .group_by(Opportunity.subcategory)
        .order_by(func.count(Opportunity.id).desc())
        .all()
    )
    return {(sub or "General"): count for sub, count in rows}


@router.get("/startup/subtypes")
def startup_subtypes(db: Session = Depends(get_db)):
    rows = (
        db.query(Opportunity.subcategory, func.count(Opportunity.id))
        .filter(Opportunity.category == "Startup")
        .group_by(Opportunity.subcategory)
        .order_by(func.count(Opportunity.id).desc())
        .all()
    )
    return {(sub or "General"): count for sub, count in rows}


@router.get("/competitions/tiers")
def competitions_tiers(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    rows = (
        db.query(Opportunity.tier, func.count(Opportunity.id))
        .filter(
            Opportunity.category == "Competitions",
            or_(Opportunity.deadline.is_(None), Opportunity.deadline >= now),
        )
        .group_by(Opportunity.tier)
        .all()
    )
    return {(t or "tier2"): count for t, count in rows}


@router.get("/competitions/domains")
def competitions_domains(db: Session = Depends(get_db), tier: Optional[str] = None):
    now = datetime.utcnow()
    query = db.query(Opportunity.domain, func.count(Opportunity.id)).filter(
        Opportunity.category == "Competitions",
        or_(Opportunity.deadline.is_(None), Opportunity.deadline >= now),
    )
    if tier:
        query = query.filter(Opportunity.tier == tier)
    rows = query.group_by(Opportunity.domain).order_by(func.count(Opportunity.id).desc()).all()
    return {(d or "General"): count for d, count in rows}


@router.get("/stats", response_model=StatsOut)
def stats(db: Session = Depends(get_db)):
    total = db.query(func.count(Opportunity.id)).scalar()

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = datetime.utcnow() - timedelta(days=7)

    new_today = db.query(func.count(Opportunity.id)).filter(Opportunity.discovered_at >= today_start).scalar()
    new_this_week = db.query(func.count(Opportunity.id)).filter(Opportunity.discovered_at >= week_start).scalar()

    by_category = dict(
        db.query(Opportunity.category, func.count(Opportunity.id)).group_by(Opportunity.category).all()
    )
    by_org_rows = (
        db.query(Opportunity.organization, func.count(Opportunity.id))
        .group_by(Opportunity.organization)
        .order_by(func.count(Opportunity.id).desc())
        .limit(10)
        .all()
    )
    by_organization = {org or "Unknown": count for org, count in by_org_rows}

    return StatsOut(
        total=total or 0,
        new_today=new_today or 0,
        new_this_week=new_this_week or 0,
        by_category=by_category,
        by_organization=by_organization,
    )
