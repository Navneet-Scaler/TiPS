import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship

from .database import Base


def gen_id():
    return str(uuid.uuid4())


class Source(Base):
    __tablename__ = "sources"

    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # rss, api, website
    url = Column(String, nullable=False, unique=True)
    tier = Column(String, default="tier2")
    active = Column(Boolean, default=True)
    last_fetched_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    opportunities = relationship("Opportunity", back_populates="source")


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(String, primary_key=True, default=gen_id)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    url = Column(String, nullable=False, unique=True)

    category = Column(String, nullable=False, index=True)   # Learning, Research, Career, ...
    subcategory = Column(String, nullable=True)
    organization = Column(String, nullable=True, index=True)
    geography = Column(String, default="Global", index=True)

    is_remote = Column(Boolean, default=False)
    is_paid = Column(Boolean, default=False)
    deadline = Column(DateTime, nullable=True)
    is_rolling = Column(Boolean, default=False)  # explicit "no fixed deadline" vs unknown
    dilution_type = Column(String, nullable=True)  # equity / non-dilutive / unknown

    published_at = Column(DateTime, nullable=True, index=True)
    discovered_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow)

    score = Column(Float, default=0.0)

    source_id = Column(String, ForeignKey("sources.id"))
    source = relationship("Source", back_populates="opportunities")
