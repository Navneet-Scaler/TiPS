"""Curated registry covering every named competition/hackathon platform and
elite challenge organization that doesn't expose a free, unauthenticated API
(Kaggle needs an API key, TAIKAI/Commudle/HackerEarth/etc. only serve their
SPA shell at the paths tried, DARPA/XPRIZE/NASA don't expose challenge feeds
at all). Rather than skip them, each gets one verified, live, homepage-or-
challenges-page entry so the platform is represented and users have a direct
link in - exactly the same pattern as the Research/Startup registries.

tier1 = the platform itself hosts/announces the competition.
tier3 = elite/grand-challenge organizations (government, defense, big-prize).
"""

from datetime import datetime

from sqlalchemy.orm import Session

from ..models import Opportunity, Source
from .utils import filter_dead_urls, safe_add

REGISTRY_URL = "https://tips.local/registry/competitions-platforms"

# Each entry: title, organization, url, tier, domain, summary.
PLATFORMS = [
    # ---- Tier 1: Competition platforms without a free public API ----
    dict(title="AIcrowd Challenges", organization="AIcrowd", url="https://www.aicrowd.com/challenges",
         tier="tier1", domain="Data Science", summary="AI/ML research challenges spanning RL, NLP, and CV, many run with NeurIPS/ICLR."),
    dict(title="EvalAI Challenges", organization="EvalAI", url="https://eval.ai/",
         tier="tier1", domain="Data Science", summary="Open-source evaluation platform hosting AI benchmark challenges, many academic."),
    dict(title="Codabench Competitions", organization="Codabench", url="https://www.codabench.org/",
         tier="tier1", domain="Data Science", summary="Successor to CodaLab - hosts reproducible ML benchmark competitions."),
    dict(title="DrivenData Challenges", organization="DrivenData", url="https://www.drivendata.org/competitions/",
         tier="tier1", domain="Data Science", summary="Social-impact data science competitions - health, climate, humanitarian AI."),
    dict(title="Tianchi Competitions", organization="Alibaba Tianchi", url="https://tianchi.aliyun.com/competition/",
         tier="tier1", domain="Data Science", summary="Alibaba's data science competition platform, large Asia-Pacific ML community."),
    dict(title="Signate Competitions", organization="Signate", url="https://signate.jp/competitions",
         tier="tier1", domain="Data Science", summary="Japan's leading data science competition platform."),
    dict(title="OpenML Benchmarks", organization="OpenML", url="https://www.openml.org/",
         tier="tier1", domain="Data Science", summary="Open platform for sharing ML datasets, tasks, and benchmark results."),
    dict(title="Topcoder Challenges", organization="Topcoder", url="https://www.topcoder.com/challenges",
         tier="tier1", domain="General ML", summary="Long-running competitive programming and data science challenge platform."),
    dict(title="HackerEarth Challenges", organization="HackerEarth", url="https://www.hackerearth.com/challenges/",
         tier="tier1", domain="General ML", summary="Hosts hackathons and ML competitions for companies and universities."),
    dict(title="TAIKAI Hackathons", organization="TAIKAI", url="https://taikai.network/",
         tier="tier1", domain="General ML", summary="Web3 and tech hackathon hosting platform used by many blockchain ecosystems."),
    dict(title="HeroX Challenges", organization="HeroX", url="https://www.herox.com/challenges",
         tier="tier1", domain="General ML", summary="Crowdsourced innovation challenge platform, XPRIZE's official partner."),
    dict(title="InnoCentive Challenges", organization="InnoCentive (Wazoku)", url="https://www.innocentive.com/",
         tier="tier1", domain="General ML", summary="Open innovation challenge marketplace for R&D problems, including AI/data."),
    dict(title="ChallengeRocket", organization="ChallengeRocket", url="https://challengerocket.com/",
         tier="tier1", domain="General ML", summary="European coding challenge and hackathon platform."),
    dict(title="DoraHacks", organization="DoraHacks", url="https://dorahacks.io/hackathon",
         tier="tier1", domain="General ML", summary="Global hackathon and grant platform, heavy Web3 and builder-community focus."),
    dict(title="lablab.ai Hackathons", organization="lablab.ai", url="https://lablab.ai/event",
         tier="tier1", domain="General ML", summary="AI-focused hackathon platform running frequent generative-AI events."),
    dict(title="Commudle Events", organization="Commudle", url="https://www.commudle.com/",
         tier="tier1", domain="General ML", summary="Developer community and hackathon discovery platform."),
    dict(title="Reskilll Challenges", organization="Reskilll", url="https://reskilll.com/",
         tier="tier1", domain="General ML", summary="India-focused student hackathon and skilling challenge platform."),
    dict(title="Devfolio Hackathons", organization="Devfolio", url="https://devfolio.co/hackathons",
         tier="tier1", domain="General ML", summary="Hackathon hosting platform behind ETHIndia and many major Indian hackathons."),
    dict(title="Major League Hacking Events", organization="MLH", url="https://mlh.io/seasons/2026/events",
         tier="tier1", domain="General ML", summary="The official student hackathon league - hundreds of member events per season."),

    # ---- Tier 1: AI research competition hosts (conference tracks) ----
    dict(title="NeurIPS Competition Track", organization="NeurIPS", url="https://neurips.cc/Conferences/2026/CompetitionTrack",
         tier="tier1", domain="Data Science", summary="Official NeurIPS competition track - the top ML research competitions of the year."),
    dict(title="ICML Challenges", organization="ICML", url="https://icml.cc/",
         tier="tier1", domain="Data Science", summary="International Conference on Machine Learning - workshop and challenge tracks."),
    dict(title="ICLR Challenges", organization="ICLR", url="https://iclr.cc/",
         tier="tier1", domain="Data Science", summary="International Conference on Learning Representations challenge tracks."),
    dict(title="CVPR Challenges", organization="CVPR", url="https://cvpr.thecvf.com/",
         tier="tier1", domain="Computer Vision", summary="Premier computer vision conference - dozens of workshop challenges yearly."),
    dict(title="ICCV Challenges", organization="ICCV", url="https://iccv2027.thecvf.com/",
         tier="tier1", domain="Computer Vision", summary="International Conference on Computer Vision challenge tracks."),
    dict(title="ECCV Challenges", organization="ECCV", url="https://eccv2026.ecva.net/",
         tier="tier1", domain="Computer Vision", summary="European Conference on Computer Vision challenge tracks."),
    dict(title="WACV Challenges", organization="WACV", url="https://wacv2026.thecvf.com/",
         tier="tier1", domain="Computer Vision", summary="Winter Conference on Applications of Computer Vision challenges."),
    dict(title="AAAI Competitions", organization="AAAI", url="https://aaai.org/conference/aaai/",
         tier="tier1", domain="General ML", summary="Association for the Advancement of AI - annual conference competitions."),
    dict(title="IJCAI Competitions", organization="IJCAI", url="https://www.ijcai.org/",
         tier="tier1", domain="General ML", summary="International Joint Conference on AI - competition and demo tracks."),
    dict(title="ACL Shared Tasks", organization="ACL", url="https://www.aclweb.org/portal/",
         tier="tier1", domain="NLP", summary="Association for Computational Linguistics - annual NLP shared tasks."),
    dict(title="EMNLP Shared Tasks", organization="EMNLP", url="https://2026.emnlp.org/",
         tier="tier1", domain="NLP", summary="Empirical Methods in NLP conference shared tasks."),
    dict(title="SemEval", organization="SemEval", url="https://semeval.github.io/",
         tier="tier1", domain="NLP", summary="Long-running semantic evaluation shared task series in NLP."),
    dict(title="WMT (Conference on Machine Translation)", organization="WMT", url="https://www2.statmt.org/wmt26/",
         tier="tier1", domain="NLP", summary="Annual machine translation shared tasks, the standard MT benchmark venue."),
    dict(title="TREC", organization="NIST TREC", url="https://trec.nist.gov/",
         tier="tier1", domain="NLP", summary="Text REtrieval Conference - NIST-run information retrieval evaluation tracks."),
    dict(title="CLEF", organization="CLEF Initiative", url="https://www.clef-initiative.eu/",
         tier="tier1", domain="NLP", summary="Conference and Labs of the Evaluation Forum - multilingual IR/NLP shared tasks."),

    # ---- Tier 1: Benchmark & evaluation platforms ----
    dict(title="Papers with Code", organization="Papers with Code", url="https://paperswithcode.com/",
         tier="tier1", domain="Data Science", summary="Links papers to code, datasets, and leaderboards - tracks active benchmark competitions."),
    dict(title="Hugging Face Competitions", organization="Hugging Face", url="https://huggingface.co/competitions",
         tier="tier1", domain="NLP", summary="Community ML competitions hosted directly on the Hugging Face Hub."),
    dict(title="MLCommons Benchmarks", organization="MLCommons", url="https://mlcommons.org/benchmarks/",
         tier="tier1", domain="General ML", summary="Industry-standard MLPerf benchmark suite and open challenges."),
    dict(title="Chatbot Arena (LMSYS)", organization="LMSYS", url="https://lmarena.ai/",
         tier="tier1", domain="NLP", summary="Crowdsourced LLM evaluation arena, community and lab submissions welcome."),
    dict(title="SWE-bench", organization="SWE-bench", url="https://www.swebench.com/",
         tier="tier1", domain="Agents", summary="Benchmark for AI coding agents resolving real GitHub issues."),
    dict(title="Open LLM Leaderboard", organization="Hugging Face", url="https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard",
         tier="tier1", domain="NLP", summary="Open leaderboard tracking open-source LLM benchmark performance."),
    dict(title="HELM", organization="Stanford CRFM", url="https://crfm.stanford.edu/helm/",
         tier="tier1", domain="NLP", summary="Holistic Evaluation of Language Models - Stanford's standardized LLM benchmark."),
    dict(title="MTEB", organization="Hugging Face / Contextual AI", url="https://huggingface.co/spaces/mteb/leaderboard",
         tier="tier1", domain="NLP", summary="Massive Text Embedding Benchmark leaderboard for embedding models."),

    # ---- Tier 1: Computer vision / robotics / scientific ecosystems ----
    dict(title="Ego4D Challenges", organization="Meta AI", url="https://ego4d-data.org/",
         tier="tier1", domain="Computer Vision", summary="Egocentric video understanding benchmark and annual challenge."),
    dict(title="Waymo Open Dataset Challenges", organization="Waymo", url="https://waymo.com/open/challenges/",
         tier="tier1", domain="Robotics", summary="Autonomous driving perception and motion prediction challenges."),
    dict(title="nuScenes Challenges", organization="Motional", url="https://www.nuscenes.org/",
         tier="tier1", domain="Robotics", summary="Autonomous driving dataset with recurring detection/tracking challenges."),
    dict(title="AI City Challenge", organization="NVIDIA", url="https://www.aicitychallenge.org/",
         tier="tier1", domain="Computer Vision", summary="CVPR workshop challenge on traffic and smart-city computer vision."),
    dict(title="RoboCup", organization="RoboCup Federation", url="https://www.robocup.org/",
         tier="tier1", domain="Robotics", summary="Annual international robotics and AI competition across multiple leagues."),
    dict(title="MineRL Competition", organization="MineRL", url="https://minerl.io/",
         tier="tier1", domain="Reinforcement Learning", summary="Sample-efficient RL competition using Minecraft as the environment."),
    dict(title="Lux AI Challenge", organization="Lux AI", url="https://www.lux-ai.org/",
         tier="tier1", domain="Reinforcement Learning", summary="Multi-agent RL/scripted-bot competition run on Kaggle."),
    dict(title="CARLA Autonomous Driving Challenge", organization="CARLA", url="https://leaderboard.carla.org/",
         tier="tier1", domain="Robotics", summary="Simulated autonomous driving leaderboard and annual challenge."),
    dict(title="Grand Challenge (Medical Imaging)", organization="Grand Challenge", url="https://grand-challenge.org/challenges/",
         tier="tier1", domain="Computer Vision", summary="Hosts hundreds of biomedical imaging AI challenges."),
    dict(title="PhysioNet Challenges", organization="PhysioNet", url="https://physionet.org/about/challenge/",
         tier="tier1", domain="Data Science", summary="Annual clinical signal-processing and medical ML challenge, MIT-run."),
    dict(title="CASP (Protein Structure Prediction)", organization="CASP", url="https://predictioncenter.org/",
         tier="tier1", domain="Data Science", summary="Critical Assessment of Structure Prediction - the AlphaFold-era protein challenge."),
    dict(title="BioASQ", organization="BioASQ", url="http://bioasq.org/",
         tier="tier1", domain="NLP", summary="Biomedical semantic indexing and QA shared task series."),
    dict(title="MICCAI Grand Challenges", organization="MICCAI", url="https://miccai.org/index.php/special-interest-groups/challenges/",
         tier="tier1", domain="Computer Vision", summary="Medical Image Computing conference's satellite grand challenges."),
    dict(title="WeatherBench", organization="WeatherBench", url="https://sites.research.google/gr/weatherbench/",
         tier="tier1", domain="Data Science", summary="Benchmark for data-driven medium-range weather forecasting models."),

    # ---- Tier 1: Company-run official AI competition/program pages ----
    dict(title="Google AI Competitions", organization="Google AI", url="https://ai.google/",
         tier="tier1", domain="General ML", summary="Google's AI research hub, source of recurring open challenges."),
    dict(title="Google DeepMind Challenges", organization="Google DeepMind", url="https://deepmind.google/",
         tier="tier1", domain="General ML", summary="DeepMind research programs and occasional public challenges."),
    dict(title="NVIDIA Developer Challenges", organization="NVIDIA", url="https://developer.nvidia.com/",
         tier="tier1", domain="General ML", summary="NVIDIA developer program - hosts GTC hackathons and dev challenges."),
    dict(title="Hugging Face Community Events", organization="Hugging Face", url="https://huggingface.co/",
         tier="tier1", domain="General ML", summary="Frequent community sprints and model/dataset competitions."),
]

ELITE_ORGS = [
    # ---- Tier 3: Grand challenge organizations ----
    dict(title="XPRIZE Competitions", organization="XPRIZE Foundation", url="https://www.xprize.org/prizes",
         tier="tier3", domain="General ML", summary="Multi-million dollar global grand challenges across AI, climate, and health."),
    dict(title="NASA Centennial Challenges", organization="NASA", url="https://www.nasa.gov/directorates/stmd/centennial-challenges-program/",
         tier="tier3", domain="Robotics", summary="NASA's public prize competition program for aerospace and robotics innovation."),
    dict(title="NASA Tournament Lab", organization="NASA", url="https://www.nasa.gov/nasa-tournament-lab/",
         tier="tier3", domain="Data Science", summary="NASA's open innovation platform for crowdsourced problem-solving challenges."),
    dict(title="ESA Open Space Innovation Platform", organization="European Space Agency", url="https://ideas.esa.int/",
         tier="tier3", domain="Data Science", summary="ESA's platform for crowdsourced space-tech and AI innovation challenges."),
    dict(title="Horizon Europe Open Calls", organization="European Commission", url="https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-search",
         tier="tier3", domain="General ML", summary="EU's flagship research funding program, including AI grand-challenge calls."),
    dict(title="EIC Challenges", organization="European Innovation Council", url="https://eic.ec.europa.eu/eic-funding-opportunities_en",
         tier="tier3", domain="General ML", summary="EU deep-tech innovation challenges, including AI and robotics prizes."),

    # ---- Tier 3: Defense innovation ----
    dict(title="DARPA Open Solicitations", organization="DARPA", url="https://www.darpa.mil/work-with-us/opportunities",
         tier="tier3", domain="Agents", summary="US defense research agency's open AI/autonomy challenge solicitations."),
    dict(title="DIU (Defense Innovation Unit)", organization="DIU", url="https://www.diu.mil/work-with-us",
         tier="tier3", domain="General ML", summary="US DoD unit fielding commercial AI/tech solutions via open solicitations."),
    dict(title="AFWERX Challenges", organization="AFWERX", url="https://afwerx.com/",
         tier="tier3", domain="General ML", summary="US Air Force innovation arm running recurring SBIR/tech challenges."),
    dict(title="iDEX India", organization="Innovation for Defence Excellence", url="https://idex.gov.in/",
         tier="tier3", domain="General ML", summary="Indian Ministry of Defence's open innovation challenge program."),

    # ---- Tier 3: Government AI challenge programs ----
    dict(title="NIST Challenges", organization="NIST", url="https://www.nist.gov/programs-projects",
         tier="tier3", domain="General ML", summary="US National Institute of Standards - runs recurring AI evaluation challenges."),
    dict(title="NSF Challenge Competitions", organization="National Science Foundation", url="https://www.nsf.gov/funding/opportunities",
         tier="tier3", domain="General ML", summary="NSF-run prize competitions and challenge-based funding calls."),
    dict(title="Grants.gov Challenges", organization="US Government", url="https://www.grants.gov/",
         tier="tier3", domain="General ML", summary="Central US federal grants and challenge.gov prize listing portal."),

    # ---- Tier 3: Semiconductor & cloud provider programs ----
    dict(title="NVIDIA Inception Challenges", organization="NVIDIA", url="https://www.nvidia.com/en-us/startups/",
         tier="tier3", domain="General ML", summary="NVIDIA's startup program, periodically runs AI hackathons for members."),
    dict(title="Qualcomm Innovation Challenge", organization="Qualcomm", url="https://www.qualcomm.com/research",
         tier="tier3", domain="Robotics", summary="Qualcomm's edge-AI and on-device ML innovation challenges."),
    dict(title="Google Cloud AI Challenges", organization="Google Cloud", url="https://cloud.google.com/programs/startups",
         tier="tier3", domain="General ML", summary="Google Cloud's startup and hackathon program with AI-focused tracks."),
    dict(title="Microsoft Azure AI Challenges", organization="Microsoft", url="https://developer.microsoft.com/en-us/",
         tier="tier3", domain="General ML", summary="Microsoft's developer program - recurring Azure AI hackathons."),

    # ---- Tier 3: Quant / finance ----
    dict(title="Jane Street Puzzles", organization="Jane Street", url="https://www.janestreet.com/puzzles/",
         tier="tier3", domain="Data Science", summary="Monthly quant puzzles used as an informal recruiting and skills challenge."),
    dict(title="Citadel Datathons", organization="Citadel / Citadel Securities", url="https://www.citadel.com/careers/students/",
         tier="tier3", domain="Data Science", summary="Citadel's student datathon and quant challenge recruiting programs."),
    dict(title="Two Sigma Data Challenges", organization="Two Sigma", url="https://www.twosigma.com/careers/",
         tier="tier3", domain="Data Science", summary="Two Sigma's recurring data science and quant modeling challenges."),
    dict(title="QuantConnect Competitions", organization="QuantConnect", url="https://www.quantconnect.com/competitions",
         tier="tier3", domain="Data Science", summary="Algorithmic trading competitions on an open quant research platform."),

    # ---- Tier 3: Blockchain ecosystem hackathons ----
    dict(title="ETHGlobal Hackathons", organization="ETHGlobal", url="https://ethglobal.com/",
         tier="tier3", domain="Agents", summary="The largest recurring Ethereum hackathon series, increasingly AI-agent focused."),
    dict(title="Solana Hackathons", organization="Solana Foundation", url="https://solana.com/hackathon",
         tier="tier3", domain="Agents", summary="Solana's global hackathon series, regularly features AI-agent tracks."),
    dict(title="Polygon Bounties", organization="Polygon", url="https://polygon.technology/community",
         tier="tier3", domain="Agents", summary="Polygon ecosystem bounty and builder program."),

    # ---- Tier 3: Big-tech research programs (recurring AI research opportunities) ----
    dict(title="Meta AI Research", organization="Meta AI", url="https://ai.meta.com/research/",
         tier="tier3", domain="General ML", summary="Meta's AI research division - periodic open research challenges and grants."),
    dict(title="Anthropic Research", organization="Anthropic", url="https://www.anthropic.com/research",
         tier="tier3", domain="AI Safety", summary="Anthropic's research program, including red-teaming and safety challenges."),
    dict(title="OpenAI Research", organization="OpenAI", url="https://openai.com/research/",
         tier="tier3", domain="General ML", summary="OpenAI's research hub - occasional open evaluation/red-team challenges."),
]


def ensure_source(db: Session) -> Source:
    source = db.query(Source).filter(Source.url == REGISTRY_URL).first()
    if not source:
        source = Source(name="Curated Competition Platforms Registry", type="registry", url=REGISTRY_URL, tier="tier3")
        db.add(source)
        db.commit()
        db.refresh(source)
    return source


def run(db: Session) -> dict:
    source = ensure_source(db)
    now = datetime.utcnow()
    added_count = 0
    all_entries = PLATFORMS + ELITE_ORGS

    unchecked = [e for e in all_entries if not db.query(Opportunity).filter(Opportunity.url == e["url"]).first()]
    dead_urls = filter_dead_urls([e["url"] for e in unchecked])

    for entry in unchecked:
        if entry["url"] in dead_urls:
            continue

        added = safe_add(db, Opportunity(
            title=entry["title"],
            summary=entry["summary"],
            url=entry["url"],
            category="Competitions",
            subcategory="Platform / Program",
            tier=entry["tier"],
            domain=entry["domain"],
            organization=entry["organization"],
            geography="Global",
            is_remote=True,
            is_paid=False,
            is_rolling=True,
            published_at=now,
            discovered_at=now,
            updated_at=now,
            score=0.4,
            source_id=source.id,
        ))
        if added:
            added_count += 1

    source.last_fetched_at = now
    db.commit()
    return {"entries_added": added_count, "total_tracked": len(all_entries)}
