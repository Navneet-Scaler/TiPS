"""Curated registry of named research programs that have no RSS/API -
independent alignment programs, corporate PhD fellowships, government
research programs, undergrad research programs, and compute grants.

These run on seasonal cycles rather than continuous feeds, so instead of
scraping each program's page we track them as a maintained list and refresh
their 'still open' status here. Add a row -> it shows up on the next run."""

from datetime import datetime

from sqlalchemy.orm import Session

from ..models import Opportunity, Source
from .utils import safe_add

REGISTRY_URL = "https://tips.local/registry/research-programs"

PROGRAMS = [
    # Independent alignment / safety research programs
    dict(title="MATS - ML Alignment Theory Scholars", organization="MATS", subcategory="Fellowship",
         url="https://www.matsprogram.org/", geography="Global", is_remote=True, is_paid=True,
         summary="Independent research program pairing scholars with alignment researchers for a mentored research sprint."),
    dict(title="SPAR - Supervised Program for Alignment Research", organization="SPAR", subcategory="Fellowship",
         url="https://sparai.org/", geography="Global", is_remote=True, is_paid=False,
         summary="Part-time mentored alignment research program for students and early-career researchers."),
    dict(title="AI Safety Camp", organization="AI Safety Camp", subcategory="Fellowship",
         url="https://aisafety.camp/", geography="Global", is_remote=True, is_paid=False,
         summary="Multi-week collaborative research sprint on open AI safety problems."),
    dict(title="Astra Fellowship", organization="Constellation", subcategory="Fellowship",
         url="https://www.constellation.org/programs/astra-fellowship", geography="United States", is_remote=False, is_paid=True,
         summary="In-person fellowship pairing fellows with mentors at leading AI safety organizations."),
    dict(title="Redwood Research MLAB", organization="Redwood Research", subcategory="Fellowship",
         url="https://www.redwoodresearch.org/mlab", geography="United States", is_remote=False, is_paid=True,
         summary="Machine Learning for Alignment Bootcamp - intensive applied alignment research training."),
    dict(title="FAR AI Visiting Researcher Program", organization="FAR AI", subcategory="Fellowship",
         url="https://www.far.ai/programs", geography="Global", is_remote=True, is_paid=True,
         summary="Visiting researcher positions on adversarial robustness and AI safety."),
    dict(title="CHAI Fellowship (Berkeley)", organization="CHAI Berkeley", subcategory="Fellowship",
         url="https://humancompatible.ai/jobs", geography="United States", is_remote=False, is_paid=True,
         summary="Center for Human-Compatible AI research fellowship at UC Berkeley."),
    dict(title="Center for AI Safety (CAIS) Philosophy Fellowship", organization="CAIS", subcategory="Fellowship",
         url="https://safe.ai/work-with-us", geography="Global", is_remote=True, is_paid=True,
         summary="Funded fellowship for research on AI safety, philosophy, and governance."),
    dict(title="GovAI Fellowship", organization="GovAI", subcategory="Fellowship",
         url="https://www.governance.ai/fellowship", geography="United Kingdom", is_remote=False, is_paid=True,
         summary="Research fellowship on AI governance and policy at the Centre for the Governance of AI."),
    dict(title="Apart Research Fellowship", organization="Apart Research", subcategory="Fellowship",
         url="https://www.apartresearch.com/", geography="Global", is_remote=True, is_paid=True,
         summary="Sprint-based AI safety research fellowship with hackathon-style research sprints."),
    dict(title="Pivotal Research Fellowship", organization="Pivotal Research", subcategory="Fellowship",
         url="https://www.pivotal-research.org/", geography="United Kingdom", is_remote=False, is_paid=True,
         summary="Summer research fellowship for aspiring AI safety and biosecurity researchers."),
    dict(title="BASE - Black in AI Safety Fellowship", organization="BASE", subcategory="Fellowship",
         url="https://www.blackinaisafety.org/", geography="Global", is_remote=True, is_paid=True,
         summary="Fellowship supporting Black researchers entering AI safety research."),

    # Corporate PhD fellowships
    dict(title="Google PhD Fellowship", organization="Google", subcategory="PhD Fellowship",
         url="https://research.google/programs-and-events/phd-fellowship/", geography="Global", is_remote=False, is_paid=True,
         summary="Fully funded PhD fellowship recognizing outstanding graduate students in computer science."),
    dict(title="Apple Scholars in AIML", organization="Apple", subcategory="PhD Fellowship",
         url="https://machinelearning.apple.com/updates/apple-scholars-aiml", geography="Global", is_remote=False, is_paid=True,
         summary="PhD fellowship for students conducting research in AI/ML."),
    dict(title="Meta PhD Fellowship", organization="Meta", subcategory="PhD Fellowship",
         url="https://research.facebook.com/fellowship/", geography="Global", is_remote=False, is_paid=True,
         summary="Fellowship supporting PhD students doing innovative computer science research."),
    dict(title="Microsoft Research PhD Fellowship", organization="Microsoft Research", subcategory="PhD Fellowship",
         url="https://www.microsoft.com/en-us/research/academic-program/phd-fellowship/", geography="Global", is_remote=False, is_paid=True,
         summary="Two-year fellowship for PhD students in computing-related fields."),
    dict(title="NVIDIA Graduate Fellowship", organization="NVIDIA", subcategory="PhD Fellowship",
         url="https://www.nvidia.com/en-us/research/graduate-fellowships/", geography="Global", is_remote=False, is_paid=True,
         summary="Fellowship for PhD students doing research relevant to NVIDIA's technology areas."),
    dict(title="Qualcomm Innovation Fellowship", organization="Qualcomm", subcategory="PhD Fellowship",
         url="https://www.qualcomm.com/research/university-relations/innovation-fellowship", geography="Global", is_remote=False, is_paid=True,
         summary="Fellowship funding innovative PhD research proposals in wireless and AI technologies."),
    dict(title="IBM PhD Fellowship", organization="IBM", subcategory="PhD Fellowship",
         url="https://research.ibm.com/university/awards/fellowships.html", geography="Global", is_remote=False, is_paid=True,
         summary="Global program recognizing outstanding PhD students in fields of interest to IBM."),

    # Government / defense research programs
    dict(title="DARPA Open Program Calls", organization="DARPA", subcategory="Government Program",
         url="https://www.darpa.mil/work-with-us/opportunities", geography="United States", is_remote=False, is_paid=True,
         summary="Rolling calls for proposals across DARPA's AI and autonomy research programs."),
    dict(title="IARPA Research Programs", organization="IARPA", subcategory="Government Program",
         url="https://www.iarpa.gov/engage-with-us/open-broad-agency-announcements", geography="United States", is_remote=False, is_paid=True,
         summary="Intelligence Advanced Research Projects Activity open research solicitations."),
    dict(title="NSF Core Programs - IIS / CCF", organization="NSF", subcategory="Government Program",
         url="https://www.nsf.gov/funding/opportunities", geography="United States", is_remote=False, is_paid=True,
         summary="Rolling and deadline-based funding opportunities in AI-relevant NSF core programs."),
    dict(title="Horizon Europe AI Calls", organization="European Commission", subcategory="Government Program",
         url="https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-search", geography="Europe", is_remote=False, is_paid=True,
         summary="EU research and innovation funding calls relevant to AI."),
    dict(title="UKRI Gateway to Research Calls", organization="UKRI", subcategory="Government Program",
         url="https://gtr.ukri.org/", geography="United Kingdom", is_remote=False, is_paid=True,
         summary="UK Research and Innovation funding opportunities and award database."),

    # Undergrad research programs
    dict(title="NSF REU Sites (AI/CS)", organization="NSF", subcategory="Undergrad Research",
         url="https://www.nsf.gov/crssprgm/reu/", geography="United States", is_remote=False, is_paid=True,
         summary="Research Experiences for Undergraduates - funded summer research placements."),
    dict(title="MIT UROP", organization="MIT", subcategory="Undergrad Research",
         url="https://urop.mit.edu/", geography="United States", is_remote=False, is_paid=True,
         summary="Undergraduate Research Opportunities Program pairing students with MIT labs."),
    dict(title="Stanford SURF", organization="Stanford", subcategory="Undergrad Research",
         url="https://undergradresearch.stanford.edu/", geography="United States", is_remote=False, is_paid=True,
         summary="Stanford Undergraduate Research Fellowship funded summer research program."),
    dict(title="Amgen Scholars Program", organization="Amgen Foundation", subcategory="Undergrad Research",
         url="https://www.amgenscholars.com/", geography="Global", is_remote=False, is_paid=True,
         summary="Funded summer research program at top universities for undergraduates in the sciences."),

    # Compute grants for researchers
    dict(title="OpenAI Researcher Access Program", organization="OpenAI", subcategory="Compute Grant",
         url="https://openai.com/form/researcher-access-program/", geography="Global", is_remote=True, is_paid=True,
         summary="API credits for researchers studying safety, alignment, and societal impact of AI."),
    dict(title="Anthropic Academic Access Program", organization="Anthropic", subcategory="Compute Grant",
         url="https://www.anthropic.com/contact-sales/for-researchers", geography="Global", is_remote=True, is_paid=True,
         summary="Claude API access for academic researchers working on AI safety and related fields."),
    dict(title="Google TPU Research Cloud", organization="Google", subcategory="Compute Grant",
         url="https://sites.research.google/trc/about/", geography="Global", is_remote=True, is_paid=True,
         summary="Free TPU compute for researchers pursuing open machine learning research."),
    dict(title="NSF ACCESS Compute Allocations", organization="NSF", subcategory="Compute Grant",
         url="https://access-ci.org/", geography="United States", is_remote=True, is_paid=True,
         summary="Advanced computing resource allocations for academic researchers."),
    dict(title="Hugging Face Compute Grants", organization="Hugging Face", subcategory="Compute Grant",
         url="https://huggingface.co/community-projects", geography="Global", is_remote=True, is_paid=True,
         summary="GPU compute grants for open-source ML research and community projects."),

    # Independent researcher funding
    dict(title="Long-Term Future Fund", organization="EA Funds", subcategory="Fellowship",
         url="https://funds.effectivealtruism.org/funds/far-future", geography="Global", is_remote=True, is_paid=True,
         summary="Grants for independent researchers and projects improving the long-term future, AI safety heavy."),
    dict(title="Survival and Flourishing Fund", organization="SFF", subcategory="Fellowship",
         url="https://survivalandflourishing.fund/", geography="Global", is_remote=True, is_paid=True,
         summary="Grants to organizations and independent researchers working on existential risk reduction."),
    dict(title="Open Philanthropy AI Grants", organization="Open Philanthropy", subcategory="Fellowship",
         url="https://www.openphilanthropy.org/grants/", geography="Global", is_remote=True, is_paid=True,
         summary="Institutional grants for technical AI safety and governance research."),
    dict(title="Manifund Regranting Rounds", organization="Manifund", subcategory="Fellowship",
         url="https://manifund.org/", geography="Global", is_remote=True, is_paid=True,
         summary="Crowdfunding and regranting platform with a heavy AI safety research presence."),
]


def ensure_source(db: Session) -> Source:
    source = db.query(Source).filter(Source.url == REGISTRY_URL).first()
    if not source:
        source = Source(name="Curated Research Programs Registry", type="registry", url=REGISTRY_URL, tier="tier3")
        db.add(source)
        db.commit()
        db.refresh(source)
    return source


def run(db: Session) -> dict:
    source = ensure_source(db)
    now = datetime.utcnow()
    new_count = 0

    for program in PROGRAMS:
        if db.query(Opportunity).filter(Opportunity.url == program["url"]).first():
            continue

        added = safe_add(db, Opportunity(
            title=program["title"],
            summary=program["summary"],
            url=program["url"],
            category="Research",
            subcategory=program["subcategory"],
            organization=program["organization"],
            geography=program["geography"],
            is_remote=program["is_remote"],
            is_paid=program["is_paid"],
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
    return {"programs_added": new_count, "total_tracked": len(PROGRAMS)}
