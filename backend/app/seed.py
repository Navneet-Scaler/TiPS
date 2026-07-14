"""Seed a handful of realistic demo opportunities across every category so the
dashboard has content immediately, before the first RSS ingestion cycle completes."""

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from .models import Opportunity

SEED_DATA = [
    dict(title="DeepMind Research Scientist Internship 2026", category="Research", organization="Google DeepMind",
         geography="UK", is_remote=False, is_paid=True, summary="Research internship program for PhD and MS students working on foundation models.",
         url="https://tips.local/seed/deepmind-internship", hours_ago=2, deadline_days=45),
    dict(title="MIT CSAIL Summer School on AI Safety", category="Learning", organization="MIT", geography="United States",
         is_remote=False, is_paid=False, summary="Two-week intensive summer school covering interpretability and alignment.",
         url="https://tips.local/seed/mit-summer-school", hours_ago=5, deadline_days=30),
    dict(title="ETHGlobal AI Agents Hackathon", category="Competitions", organization="ETHGlobal", geography="Global",
         is_remote=True, is_paid=True, summary="48-hour hackathon focused on autonomous AI agents, $50k prize pool.",
         url="https://tips.local/seed/ethglobal-hackathon", hours_ago=1, deadline_days=12),
    dict(title="Anthropic Fellows Program", category="Research", organization="Anthropic", geography="United States",
         is_remote=False, is_paid=True, summary="Safety-focused research fellowship for early-career researchers.",
         url="https://tips.local/seed/anthropic-fellows", hours_ago=8, deadline_days=20),
    dict(title="Hugging Face GPU Grant for OSS Maintainers", category="Funding", organization="Hugging Face", geography="Global",
         is_remote=True, is_paid=True, summary="Free A100 compute credits for open-source ML tooling maintainers.",
         url="https://tips.local/seed/hf-gpu-grant", hours_ago=3, deadline_days=None),
    dict(title="LFX Mentorship: Kubernetes AI Workloads", category="Open Source", organization="Linux Foundation",
         geography="Global", is_remote=True, is_paid=True, summary="Paid open-source mentorship building AI scheduling primitives for k8s.",
         url="https://tips.local/seed/lfx-mentorship", hours_ago=14, deadline_days=18),
    dict(title="Y Combinator W27 Batch - AI Track", category="Startup", organization="Y Combinator", geography="United States",
         is_remote=False, is_paid=True, summary="Accelerator batch application open for AI-first startups.",
         url="https://tips.local/seed/yc-w27", hours_ago=20, deadline_days=60),
    dict(title="NeurIPS 2026 Call for Papers", category="Publishing", organization="NeurIPS", geography="Global",
         is_remote=True, is_paid=False, summary="Main track and workshop CFP now open, abstract deadline approaching.",
         url="https://tips.local/seed/neurips-cfp", hours_ago=30, deadline_days=75),
    dict(title="r/MachineLearning: Professor recruiting RAs for RL lab", category="Community", organization="Reddit",
         geography="Global", is_remote=True, is_paid=True, summary="Thread from a CMU professor looking for research assistants, unlisted elsewhere yet.",
         url="https://tips.local/seed/reddit-ra-thread", hours_ago=6, deadline_days=None),
    dict(title="OpenAI API Research Preview: Extended Context", category="Beta Programs", organization="OpenAI",
         geography="Global", is_remote=True, is_paid=False, summary="Trusted tester program for a new long-context API tier.",
         url="https://tips.local/seed/openai-preview", hours_ago=4, deadline_days=None),
    dict(title="NVIDIA Inception Compute Sponsorship", category="Funding", organization="NVIDIA", geography="Global",
         is_remote=True, is_paid=True, summary="Cloud GPU credits for startups building on NVIDIA infrastructure.",
         url="https://tips.local/seed/nvidia-inception", hours_ago=11, deadline_days=None),
    dict(title="Stanford HAI Seminar Series", category="Learning", organization="Stanford", geography="United States",
         is_remote=True, is_paid=False, summary="Weekly seminar with recorded talks from leading AI researchers.",
         url="https://tips.local/seed/stanford-hai", hours_ago=16, deadline_days=None),
]


def seed_if_empty(db: Session):
    if db.query(Opportunity).first():
        return

    now = datetime.utcnow()
    for item in SEED_DATA:
        published_at = now - timedelta(hours=item["hours_ago"])
        deadline = now + timedelta(days=item["deadline_days"]) if item.get("deadline_days") else None
        recency_days = item["hours_ago"] / 24
        score = 1.0 if recency_days <= 1 else 0.7 if recency_days <= 7 else 0.4

        db.add(Opportunity(
            title=item["title"],
            summary=item["summary"],
            url=item["url"],
            category=item["category"],
            organization=item["organization"],
            geography=item["geography"],
            is_remote=item["is_remote"],
            is_paid=item["is_paid"],
            deadline=deadline,
            published_at=published_at,
            discovered_at=published_at,
            updated_at=published_at,
            score=score,
        ))

    db.commit()
