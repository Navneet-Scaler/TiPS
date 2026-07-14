"""Curated registry of named startup programs with no reliable feed/API -
accelerators, incubators, corporate compute programs, government schemes.

Each entry follows the CORE PRINCIPLE for the Startup tab: a clear applicant
action, an identifiable provider, a deadline-or-rolling status, and an
application URL. Nothing here is funding-round news or generic company
data - that belongs in Trending/Timeline, not this tab."""

import logging
from datetime import datetime

from sqlalchemy.orm import Session

from ..models import Opportunity, Source
from .utils import filter_dead_urls, safe_add

logger = logging.getLogger("tips.ingestion.startup_registry")

REGISTRY_URL = "https://tips.local/registry/startup-programs"

# sub_type mirrors classify.STARTUP_SUBCATEGORY_KEYWORDS categories.
# dilution: equity / non-dilutive / unknown. region: India / Global / both.
PROGRAMS = [
    # GLOBAL - VC-run, check-writing accelerators
    dict(title="Y Combinator", organization="Y Combinator", sub_type="Accelerator", dilution="equity",
         region="Global", is_rolling=False, url="https://www.ycombinator.com/apply",
         summary="Flagship accelerator, 4 batches/year, ~60% AI companies in recent cohorts. $500K standard deal."),
    dict(title="Techstars", organization="Techstars", sub_type="Accelerator", dilution="equity",
         region="Global", is_rolling=False, url="https://www.techstars.com/accelerators",
         summary="Global accelerator network with AI-focused vertical tracks in multiple cities."),
    dict(title="500 Global", organization="500 Global", sub_type="Accelerator", dilution="equity",
         region="Global", is_rolling=False, url="https://500.co/accelerator",
         summary="Seed accelerator with strong emerging-markets and AI portfolio focus."),
    dict(title="Antler", organization="Antler", sub_type="Venture Studio", dilution="equity",
         region="Global", is_rolling=False, url="https://www.antler.co/apply",
         summary="Pre-team venture studio - recruits individual founders before a co-founder is found."),
    dict(title="Seedcamp", organization="Seedcamp", sub_type="Accelerator", dilution="equity",
         region="Global", is_rolling=True, url="https://seedcamp.com/",
         summary="Europe-focused early-stage fund and accelerator, rolling applications."),
    dict(title="South Park Commons", organization="South Park Commons", sub_type="Founder Fellowship", dilution="equity",
         region="Global", is_rolling=True, url="https://www.southparkcommons.com/apply",
         summary="Fellowship for founders pre-idea or pre-team, rolling cohort admission."),
    dict(title="Entrepreneur First", organization="Entrepreneur First", sub_type="Venture Studio", dilution="equity",
         region="Global", is_rolling=False, url="https://www.joinef.com/apply/",
         summary="Recruits individuals, not teams - matches co-founders on-program."),
    dict(title="Creative Destruction Lab", organization="CDL", sub_type="Accelerator", dilution="equity",
         region="Global", is_rolling=False, url="https://creativedestructionlab.com/apply/",
         summary="Science- and deep-tech-focused accelerator with mentor-driven objective setting."),
    dict(title="Founder Institute", organization="Founder Institute", sub_type="Accelerator", dilution="equity",
         region="Global", is_rolling=True, url="https://fi.co/apply",
         summary="Pre-seed accelerator network with chapters in 200+ cities, rolling cohorts."),
    dict(title="Alchemist Accelerator", organization="Alchemist", sub_type="Accelerator", dilution="equity",
         region="Global", is_rolling=False, url="https://www.alchemistaccelerator.com/apply",
         summary="Enterprise/B2B-focused accelerator, no consumer startups."),
    dict(title="a16z Speedrun", organization="Andreessen Horowitz", sub_type="Accelerator", dilution="equity",
         region="Global", is_rolling=False, url="https://a16z.com/speedrun/",
         summary="Gaming and consumer tech accelerator run by a16z, increasingly AI-native tooling focused."),
    dict(title="Sequoia Arc", organization="Sequoia Capital", sub_type="Accelerator", dilution="equity",
         region="Global", is_rolling=False, url="https://www.sequoiacap.com/arc/",
         summary="Sequoia's global seed-stage program for early founders."),

    # GLOBAL - AI-specific programs
    dict(title="AI2 Incubator", organization="Allen Institute for AI", sub_type="Accelerator", dilution="equity",
         region="Global", is_rolling=True, url="https://www.ai2incubator.com/apply",
         summary="AI-focused incubator from the Allen Institute, rolling applications."),
    dict(title="Conviction 8-Week AI Program", organization="Conviction (Sarah Guo)", sub_type="Accelerator", dilution="equity",
         region="Global", is_rolling=False, url="https://www.conviction.com/",
         summary="Intensive 8-week program for AI-native founders."),
    dict(title="F/ai", organization="OpenAI, Anthropic, Google, Meta, Microsoft, Mistral", sub_type="Accelerator", dilution="equity",
         region="Global", is_rolling=True, url="https://www.f-ai.paris/",
         summary="Jointly-backed Paris AI accelerator; selection is by partner referral rather than open application."),

    # GLOBAL - Corporate/equity-free compute programs (rolling, no deadline)
    dict(title="NVIDIA Inception", organization="NVIDIA", sub_type="Compute/Credit Program", dilution="non-dilutive",
         region="Global", is_rolling=True, url="https://www.nvidia.com/en-us/startups/",
         summary="19,000+ member companies, free GPU/cloud credits, no equity taken, rolling enrollment."),
    dict(title="Google for Startups Accelerator: AI First", organization="Google", sub_type="Accelerator", dilution="non-dilutive",
         region="Global", is_rolling=False, url="https://startup.google.com/programs/accelerator/ai-first/",
         summary="Equity-free program for AI-first startups, includes Google Cloud credits and mentorship."),
    dict(title="Microsoft for Startups Founders Hub", organization="Microsoft", sub_type="Compute/Credit Program", dilution="non-dilutive",
         region="Global", is_rolling=True, url="https://www.microsoft.com/en-us/startups",
         summary="Free Azure credits, OpenAI API access, and go-to-market support, no equity, rolling."),
    dict(title="AWS Activate", organization="Amazon Web Services", sub_type="Compute/Credit Program", dilution="non-dilutive",
         region="Global", is_rolling=True, url="https://aws.amazon.com/startups/",
         summary="AWS credits and technical support for startups, rolling enrollment."),
    dict(title="AWS Generative AI Accelerator (GAIA)", organization="Amazon Web Services", sub_type="Accelerator", dilution="non-dilutive",
         region="Global", is_rolling=False, url="https://aws.amazon.com/startups/",
         summary="Equity-free generative AI accelerator program from AWS."),
    dict(title="Plug and Play", organization="Plug and Play", sub_type="Accelerator", dilution="equity",
         region="Global", is_rolling=False, url="https://www.plugandplaytechcenter.com/apply/",
         summary="100+ vertical accelerator programs annually across fintech, health, mobility, and more."),

    # GLOBAL - hard tech / physical AI
    dict(title="HAX (SOSV)", organization="SOSV", sub_type="Accelerator", dilution="equity",
         region="Global", is_rolling=False, url="https://hax.co/apply/",
         summary="Hard-tech and physical AI/robotics-focused accelerator, part of SOSV."),
    dict(title="Elev X! Ignite", organization="NEC X", sub_type="Accelerator", dilution="equity",
         region="Global", is_rolling=False, url="https://necx.co/elevx/",
         summary="Deep-tech accelerator backed by NEC X, hard-tech and robotics focus."),

    # GLOBAL - government / regional
    dict(title="MassChallenge", organization="MassChallenge", sub_type="Accelerator", dilution="non-dilutive",
         region="Global", is_rolling=False, url="https://masschallenge.org/apply",
         summary="Equity-free accelerator with cash prizes, multiple country tracks."),
    dict(title="Station F Programs", organization="Station F", sub_type="Incubator", dilution="equity",
         region="Global", is_rolling=True, url="https://stationf.co/",
         summary="30+ accelerator programs under one Paris campus, rolling applications vary by program."),

    # GLOBAL - university-affiliated
    dict(title="Stanford StartX", organization="Stanford University", sub_type="Accelerator", dilution="non-dilutive",
         region="Global", is_rolling=False, url="https://startx.com/apply/",
         summary="Equity-free accelerator for Stanford-affiliated founders."),
    dict(title="MIT delta v", organization="MIT", sub_type="Accelerator", dilution="non-dilutive",
         region="Global", is_rolling=False, url="https://deltav.mit.edu/",
         summary="MIT's student venture accelerator, summer cohort."),
    dict(title="Berkeley SkyDeck", organization="UC Berkeley", sub_type="Accelerator", dilution="equity",
         region="Global", is_rolling=False, url="https://skydeck.berkeley.edu/apply/",
         summary="UC Berkeley's startup accelerator, open to Berkeley-affiliated and external founders."),
    dict(title="Harvard Innovation Labs", organization="Harvard University", sub_type="Incubator", dilution="non-dilutive",
         region="Global", is_rolling=True, url="https://innovationlabs.harvard.edu/",
         summary="Harvard's cross-school innovation and startup incubator."),

    # GLOBAL - co-founder matching
    dict(title="YC Co-Founder Matching", organization="Y Combinator", sub_type="Co-founder Matching", dilution="unknown",
         region="Global", is_rolling=True, url="https://www.startupschool.org/cofounder-matching",
         summary="Free tool that has facilitated 100,000+ founder introductions."),
    dict(title="CoFoundersLab", organization="CoFoundersLab", sub_type="Co-founder Matching", dilution="unknown",
         region="Global", is_rolling=True, url="https://cofounderslab.com/",
         summary="Dedicated co-founder matching platform with a large member base."),

    # GLOBAL - startup visa / relocation
    dict(title="UK Global Talent Visa", organization="UK Government", sub_type="Startup Visa / Relocation", dilution="unknown",
         region="Global", is_rolling=True, url="https://www.gov.uk/global-talent",
         summary="Visa route for tech founders and researchers to relocate to the UK."),
    dict(title="France Tech Visa", organization="French Government", sub_type="Startup Visa / Relocation", dilution="unknown",
         region="Global", is_rolling=True, url="https://www.frenchtechvisa.tech/",
         summary="Fast-track visa for founders, employees, and investors relocating to France."),

    # INDIA - government schemes
    dict(title="Startup India Seed Fund Scheme (SISFS)", organization="Government of India", sub_type="Grant (non-dilutive)",
         dilution="non-dilutive", region="India", is_rolling=True, url="https://seedfund.startupindia.gov.in/",
         summary="Up to Rs 20L concept-validation grant, Rs 50L prototype grant, disbursed via 250+ empanelled incubators."),
    dict(title="Startup India Fund of Funds 2.0", organization="SIDBI / Government of India", sub_type="Grant (non-dilutive)",
         dilution="non-dilutive", region="India", is_rolling=True, url="https://www.startupindia.gov.in/",
         summary="Rs 10,000 crore corpus targeting AI/deep tech, deployed through SEBI-registered AIFs."),
    dict(title="Credit Guarantee Scheme for Startups (CGSS)", organization="Government of India", sub_type="Grant (non-dilutive)",
         dilution="non-dilutive", region="India", is_rolling=True, url="https://www.startupindia.gov.in/",
         summary="Collateral-free loans up to Rs 20 crore for DPIIT-recognized startups."),
    dict(title="Atal Innovation Mission", organization="NITI Aayog", sub_type="Grant (non-dilutive)",
         dilution="non-dilutive", region="India", is_rolling=True, url="https://aim.gov.in/",
         summary="Government innovation and incubation support program under NITI Aayog."),
    dict(title="NIDHI-PRAYAS", organization="Department of Science & Technology", sub_type="Grant (non-dilutive)",
         dilution="non-dilutive", region="India", is_rolling=True, url="https://www.nidhi-prayas.org/",
         summary="Hardware prototyping grants up to Rs 10L plus FabLab access."),
    dict(title="IndiaAI Mission Compute Access", organization="Government of India", sub_type="Compute/Credit Program",
         dilution="non-dilutive", region="India", is_rolling=True, url="https://indiaai.gov.in/",
         summary="Subsidized GPU compute access for AI startups, 38,000+ GPUs onboarded as of early 2026."),
    dict(title="IndiaAI Startups Global (Station F)", organization="IndiaAI / Station F", sub_type="Accelerator",
         dilution="equity", region="India", is_rolling=False, url="https://indiaai.gov.in/",
         summary="Funded 4-month Paris program for Indian AI startups via IndiaAI's Station F partnership."),
    dict(title="MeitY Startup Hub", organization="Ministry of Electronics & IT", sub_type="Incubator",
         dilution="non-dilutive", region="India", is_rolling=True, url="https://meitystartuphub.in/",
         summary="Central government startup hub aggregating schemes, incubators, and funding for tech startups."),

    # INDIA - university & national incubators
    dict(title="T-Hub", organization="T-Hub", sub_type="Incubator", dilution="equity",
         region="India", is_rolling=True, url="https://www.t-hub.co/",
         summary="One of the world's largest innovation campuses, Telangana-based, multiple sector tracks."),
    dict(title="NSRCEL - IIM Bangalore", organization="IIM Bangalore", sub_type="Accelerator", dilution="equity",
         region="India", is_rolling=False, url="https://www.nsrcel.org/",
         summary="Launchpad, Women Startup Programme, Fintech and Climate tracks."),
    dict(title="CIIE.CO - IIM Ahmedabad", organization="IIM Ahmedabad", sub_type="Incubator", dilution="equity",
         region="India", is_rolling=False, url="https://ciie.co/",
         summary="IIM Ahmedabad's startup incubator with multiple sector-specific programs."),
    dict(title="SINE - IIT Bombay", organization="IIT Bombay", sub_type="Incubator", dilution="equity",
         region="India", is_rolling=True, url="https://sineiitb.org/",
         summary="Society for Innovation and Entrepreneurship, IIT Bombay's startup incubator."),
    dict(title="NASSCOM 10,000 Startups", organization="NASSCOM", sub_type="Accelerator", dilution="equity",
         region="India", is_rolling=True, url="https://10000startups.com/",
         summary="Long-running national startup acceleration program by NASSCOM."),

    # INDIA - corporate & VC-run
    dict(title="Peak XV Surge", organization="Peak XV Partners", sub_type="Accelerator", dilution="equity",
         region="India", is_rolling=False, url="https://www.peakxv.com/",
         summary="Up to $3M seed investment, 16-week accelerator program."),
    dict(title="Peak XV Spark Fellowship", organization="Peak XV Partners", sub_type="Founder Fellowship", dilution="non-dilutive",
         region="India", is_rolling=False, url="https://www.peakxv.com/",
         summary="$100K grant for women founders, no equity taken."),
    dict(title="Accel Atoms", organization="Accel", sub_type="Accelerator", dilution="equity",
         region="India", is_rolling=False, url="https://www.accel.com/",
         summary="AI pre-seed focused accelerator run by Accel."),
    dict(title="100X.VC", organization="100X.VC", sub_type="Accelerator", dilution="equity",
         region="India", is_rolling=False, url="https://www.100x.vc/",
         summary="India's iSAFE-note based seed investment and cohort program."),
    dict(title="Google for Startups Accelerator India: AI First", organization="Google", sub_type="Accelerator",
         dilution="non-dilutive", region="India", is_rolling=False, url="https://startup.google.com/programs/accelerator/ai-first/india/",
         summary="Equity-free AI-focused accelerator track for Indian startups."),
    dict(title="NVIDIA Inception India", organization="NVIDIA", sub_type="Compute/Credit Program", dilution="non-dilutive",
         region="India", is_rolling=True, url="https://www.nvidia.com/en-in/startups/",
         summary="Free GPU/cloud credits and technical resources for Indian AI startups, rolling enrollment."),
    dict(title="Antler India", organization="Antler", sub_type="Venture Studio", dilution="equity",
         region="India", is_rolling=False, url="https://www.antler.co/apply",
         summary="Antler's India-based pre-team venture studio cohort."),
]


def ensure_source(db: Session) -> Source:
    source = db.query(Source).filter(Source.url == REGISTRY_URL).first()
    if not source:
        source = Source(name="Curated Startup Programs Registry", type="registry", url=REGISTRY_URL, tier="tier3")
        db.add(source)
        db.commit()
        db.refresh(source)
    return source


def run(db: Session) -> dict:
    source = ensure_source(db)
    now = datetime.utcnow()
    new_count = 0

    unchecked = [p for p in PROGRAMS if not db.query(Opportunity).filter(Opportunity.url == p["url"]).first()]
    dead_urls = filter_dead_urls([p["url"] for p in unchecked])

    for program in unchecked:
        if program["url"] in dead_urls:
            logger.info("Skipping dead link for %s: %s", program["title"], program["url"])
            continue

        added = safe_add(db, Opportunity(
            title=program["title"],
            summary=program["summary"],
            url=program["url"],
            category="Startup",
            subcategory=program["sub_type"],
            organization=program["organization"],
            geography=program["region"],
            is_remote=True,
            is_paid=program["dilution"] == "non-dilutive",
            is_rolling=program["is_rolling"],
            dilution_type=program["dilution"],
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
