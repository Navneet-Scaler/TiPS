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
         tier="tier1", domain="Autonomous Driving", summary="Autonomous driving perception and motion prediction challenges."),
    dict(title="nuScenes Challenges", organization="Motional", url="https://www.nuscenes.org/",
         tier="tier1", domain="Autonomous Driving", summary="Autonomous driving dataset with recurring detection/tracking challenges."),
    dict(title="AI City Challenge", organization="NVIDIA", url="https://www.aicitychallenge.org/",
         tier="tier1", domain="Computer Vision", summary="CVPR workshop challenge on traffic and smart-city computer vision."),
    dict(title="RoboCup", organization="RoboCup Federation", url="https://www.robocup.org/",
         tier="tier1", domain="Robotics", summary="Annual international robotics and AI competition across multiple leagues."),
    dict(title="MineRL Competition", organization="MineRL", url="https://minerl.io/",
         tier="tier1", domain="Reinforcement Learning", summary="Sample-efficient RL competition using Minecraft as the environment."),
    dict(title="Lux AI Challenge", organization="Lux AI", url="https://www.lux-ai.org/",
         tier="tier1", domain="Reinforcement Learning", summary="Multi-agent RL/scripted-bot competition run on Kaggle."),
    dict(title="CARLA Autonomous Driving Challenge", organization="CARLA", url="https://leaderboard.carla.org/",
         tier="tier1", domain="Autonomous Driving", summary="Simulated autonomous driving leaderboard and annual challenge."),
    dict(title="Grand Challenge (Medical Imaging)", organization="Grand Challenge", url="https://grand-challenge.org/challenges/",
         tier="tier1", domain="Healthcare / Medical AI", summary="Hosts hundreds of biomedical imaging AI challenges."),
    dict(title="PhysioNet Challenges", organization="PhysioNet", url="https://physionet.org/about/challenge/",
         tier="tier1", domain="Healthcare / Medical AI", summary="Annual clinical signal-processing and medical ML challenge, MIT-run."),
    dict(title="CASP (Protein Structure Prediction)", organization="CASP", url="https://predictioncenter.org/",
         tier="tier1", domain="Drug Discovery", summary="Critical Assessment of Structure Prediction - the AlphaFold-era protein challenge."),
    dict(title="BioASQ", organization="BioASQ", url="http://bioasq.org/",
         tier="tier1", domain="NLP", summary="Biomedical semantic indexing and QA shared task series."),
    dict(title="MICCAI Grand Challenges", organization="MICCAI", url="https://miccai.org/index.php/special-interest-groups/challenges/",
         tier="tier1", domain="Healthcare / Medical AI", summary="Medical Image Computing conference's satellite grand challenges."),
    dict(title="WeatherBench", organization="WeatherBench", url="https://sites.research.google/gr/weatherbench/",
         tier="tier1", domain="Climate / Earth Observation", summary="Benchmark for data-driven medium-range weather forecasting models."),

    # ---- Tier 1: Computer vision challenge ecosystem (datasets + recurring challenges) ----
    dict(title="ImageNet Challenge", organization="ImageNet", url="https://www.image-net.org/",
         tier="tier1", domain="Computer Vision", summary="The dataset and challenge that launched modern deep learning-based vision."),
    dict(title="COCO Challenges", organization="COCO Consortium", url="https://cocodataset.org/",
         tier="tier1", domain="Computer Vision", summary="Common Objects in Context - object detection/segmentation/captioning challenges."),
    dict(title="Open Images Challenge", organization="Google", url="https://storage.googleapis.com/openimages/web/index.html",
         tier="tier1", domain="Computer Vision", summary="Large-scale annotated image dataset with recurring detection challenges."),
    dict(title="KITTI Vision Benchmark", organization="KIT / Toyota", url="https://www.cvlibs.net/datasets/kitti/",
         tier="tier1", domain="Autonomous Driving", summary="Autonomous driving benchmark suite for stereo, flow, and 3D object detection."),
    dict(title="VOT Challenge", organization="VOT Initiative", url="https://www.votchallenge.net/",
         tier="tier1", domain="Computer Vision", summary="Annual visual object tracking challenge, ICCV/ECCV workshop-affiliated."),
    dict(title="xView Challenges", organization="Defense Innovation Unit", url="http://xviewdataset.org/",
         tier="tier1", domain="Computer Vision", summary="Satellite imagery object detection challenge series."),
    dict(title="VisDrone Challenge", organization="AISKYEYE", url="http://aiskyeye.com/",
         tier="tier1", domain="Computer Vision", summary="Drone-captured visual data challenge - detection, tracking, counting."),
    dict(title="ImageCLEF (incl. GeoLifeCLEF, PlantCLEF)", organization="CLEF Initiative", url="https://www.imageclef.org/",
         tier="tier1", domain="Computer Vision", summary="Multimedia retrieval and biodiversity image recognition shared tasks."),

    # ---- Tier 1: Robotics & reinforcement learning environments/competitions ----
    dict(title="MBZIRC", organization="Khalifa University", url="https://www.mbzirc.com/",
         tier="tier1", domain="Robotics", summary="Mohamed Bin Zayed International Robotics Challenge - major prize-backed robotics competition."),
    dict(title="FIRST Robotics Competition", organization="FIRST", url="https://www.firstinspires.org/robotics/frc",
         tier="tier1", domain="Robotics", summary="Global student robotics competition, one of the largest robotics leagues."),
    dict(title="VEX Robotics Competition", organization="REC Foundation", url="https://www.roboticseducation.org/",
         tier="tier1", domain="Robotics", summary="Student robotics competition league running across schools worldwide."),
    dict(title="World Robot Olympiad", organization="WRO Association", url="https://wro-association.org/",
         tier="tier1", domain="Robotics", summary="International robotics competition for students, multiple age categories."),
    dict(title="RoboMaster", organization="DJI", url="https://www.robomaster.com/en-US",
         tier="tier1", domain="Robotics", summary="DJI-run robotics combat competition popular across Chinese universities."),
    dict(title="Neural MMO", organization="OpenAI / CarperAI", url="https://neuralmmo.github.io/",
         tier="tier1", domain="Reinforcement Learning", summary="Massively multi-agent RL research environment and competition."),
    dict(title="Google Research Football", organization="Google Research", url="https://github.com/google-research/football",
         tier="tier1", domain="Reinforcement Learning", summary="RL environment and competition based on simulated football."),
    dict(title="Habitat Challenge", organization="Meta AI", url="https://aihabitat.org/challenge/",
         tier="tier1", domain="Robotics", summary="Embodied AI navigation challenge in photorealistic 3D environments."),
    dict(title="ManiSkill", organization="Hillbot / UC San Diego", url="https://www.maniskill.ai/",
         tier="tier1", domain="Robotics", summary="Robot manipulation learning benchmark and challenge."),
    dict(title="AI2-THOR", organization="Allen Institute for AI", url="https://ai2thor.allenai.org/",
         tier="tier1", domain="Robotics", summary="Embodied AI simulation environment used in several navigation challenges."),
    dict(title="OpenSpiel", organization="Google DeepMind", url="https://openspiel.readthedocs.io/",
         tier="tier1", domain="Reinforcement Learning", summary="Framework for RL research in games, used in multi-agent competitions."),

    # ---- Tier 1: Scientific & medical AI ----
    dict(title="DREAM Challenges", organization="Sage Bionetworks", url="https://dreamchallenges.org/",
         tier="tier1", domain="Healthcare / Medical AI", summary="Crowdsourced biomedical prediction challenges across genomics and health."),
    dict(title="BioCreative", organization="BioCreative", url="https://biocreative.bioinformatics.udel.edu/",
         tier="tier1", domain="NLP", summary="Biomedical text mining and NLP shared task series."),
    dict(title="PrecisionFDA Challenges", organization="US FDA", url="https://precision.fda.gov/",
         tier="tier1", domain="Healthcare / Medical AI", summary="FDA-run genomics and precision medicine algorithm challenges."),
    dict(title="Open Catalyst Project", organization="Meta AI / Carnegie Mellon", url="https://opencatalystproject.org/",
         tier="tier1", domain="Drug Discovery", summary="ML challenge for catalyst discovery to accelerate renewable energy storage."),
    dict(title="DeepChem / MoleculeNet", organization="DeepChem", url="https://deepchem.io/",
         tier="tier1", domain="Drug Discovery", summary="Open molecular ML benchmark suite for drug discovery models."),
    dict(title="Therapeutics Data Commons", organization="Harvard / MIT", url="https://tdcommons.ai/",
         tier="tier1", domain="Drug Discovery", summary="ML benchmark platform for therapeutics and drug discovery challenges."),

    # ---- Tier 1: Climate & earth observation ----
    dict(title="AI for Earth", organization="Microsoft", url="https://www.microsoft.com/en-us/ai/ai-for-earth",
         tier="tier1", domain="Climate / Earth Observation", summary="Microsoft's environmental AI grant and challenge program."),
    dict(title="ClimateBench", organization="Climate Informatics community", url="https://github.com/duncanwp/ClimateBench",
         tier="tier1", domain="Climate / Earth Observation", summary="Benchmark dataset for ML-based climate model emulation."),
    dict(title="ISPRS Challenges", organization="ISPRS", url="https://www.isprs.org/",
         tier="tier1", domain="Climate / Earth Observation", summary="International photogrammetry and remote sensing challenge series."),
    dict(title="FloodNet Challenge", organization="CodaLab community", url="https://competitions.codalab.org/",
         tier="tier1", domain="Climate / Earth Observation", summary="Post-disaster flood damage assessment from drone imagery, recurring challenge."),
    dict(title="Open Cities AI Challenge", organization="DrivenData", url="https://www.drivendata.org/competitions/60/building-segmentation-disaster-resilience/",
         tier="tier1", domain="Climate / Earth Observation", summary="Building segmentation challenge for disaster-resilience planning."),
    dict(title="RSNA AI Challenges", organization="Radiological Society of North America", url="https://www.rsna.org/",
         tier="tier1", domain="Healthcare / Medical AI", summary="Annual medical imaging AI challenge run alongside the RSNA conference."),
    dict(title="ISIC Skin Imaging Challenge", organization="ISIC Archive", url="https://www.isic-archive.com/",
         tier="tier1", domain="Healthcare / Medical AI", summary="Skin lesion image analysis challenge, recurring MICCAI-affiliated benchmark."),
    dict(title="Climate Change AI Programs", organization="Climate Change AI", url="https://www.climatechange.ai/",
         tier="tier1", domain="Climate / Earth Observation", summary="Community running workshops, summer schools, and challenge programs at the ML/climate intersection."),

    # ---- Tier 1: Security / CTF competitions (bug bounty + capture-the-flag) ----
    dict(title="HackerOne Programs", organization="HackerOne", url="https://hackerone.com/directory/programs",
         tier="tier1", domain="AI Safety", summary="Directory of live bug bounty programs, including AI/LLM red-teaming programs."),
    dict(title="Bugcrowd Programs", organization="Bugcrowd", url="https://bugcrowd.com/programs",
         tier="tier1", domain="AI Safety", summary="Crowdsourced security bug bounty platform, growing AI/LLM red-team category."),
    dict(title="Synack Red Team", organization="Synack", url="https://www.synack.com/",
         tier="tier1", domain="AI Safety", summary="Vetted red-team security testing platform, increasingly covers AI systems."),
    dict(title="Hack The Box", organization="Hack The Box", url="https://www.hackthebox.com/",
         tier="tier1", domain="AI Safety", summary="Cybersecurity CTF and skills platform with recurring competitive seasons."),
    dict(title="TryHackMe", organization="TryHackMe", url="https://tryhackme.com/",
         tier="tier1", domain="AI Safety", summary="Gamified cybersecurity learning platform with recurring CTF competitions."),
    dict(title="picoCTF", organization="Carnegie Mellon University", url="https://picoctf.org/",
         tier="tier1", domain="AI Safety", summary="CMU's free annual CTF competition, popular with students."),
    dict(title="DEF CON AI Village CTF", organization="AI Village", url="https://aivillage.org/",
         tier="tier1", domain="AI Safety", summary="DEF CON's AI-focused village, runs AI red-teaming CTF challenges annually."),

    # ---- Tier 1: More data science competition platforms ----
    dict(title="Analytics Vidhya DataHack", organization="Analytics Vidhya", url="https://datahack.analyticsvidhya.com/",
         tier="tier1", domain="Data Science", summary="India-based data science hackathon and competition platform."),
    dict(title="MachineHack", organization="MachineHack", url="https://machinehack.com/",
         tier="tier1", domain="Data Science", summary="ML competition platform focused on practical business use cases."),
    dict(title="Bitgrit Competitions", organization="Bitgrit", url="https://bitgrit.net/competition/",
         tier="tier1", domain="Data Science", summary="Data science competition platform with a global participant base."),
    dict(title="KDD Cup", organization="ACM SIGKDD", url="https://kdd.org/kdd-cup",
         tier="tier1", domain="Data Science", summary="Premier annual data mining competition run alongside the KDD conference."),
    dict(title="IEEE DataPort Challenges", organization="IEEE", url="https://ieee-dataport.org/",
         tier="tier1", domain="Data Science", summary="IEEE's open data platform, hosts recurring dataset-driven AI challenges."),
    dict(title="Numerai Tournament (homepage)", organization="Numerai", url="https://numer.ai/",
         tier="tier1", domain="Finance / Quant", summary="Numerai's homepage - the live tournament itself is tracked separately with real round data."),

    # ---- Tier 1: More computer vision / speech benchmarks ----
    dict(title="VQA Challenge", organization="Georgia Tech / VirginiaTech", url="https://visualqa.org/challenge.html",
         tier="tier1", domain="Multimodal / Generative", summary="Visual Question Answering challenge, a foundational multimodal AI benchmark."),
    dict(title="Argoverse Challenges", organization="Argo AI / Woven Planet", url="https://www.argoverse.org/",
         tier="tier1", domain="Autonomous Driving", summary="Motion forecasting and 3D tracking challenges for autonomous driving."),
    dict(title="VoxCeleb Speaker Recognition Challenge", organization="VoxCeleb", url="https://mm.kaist.ac.kr/datasets/voxceleb/",
         tier="tier1", domain="Speech", summary="Recurring speaker recognition and diarization challenge series."),
    dict(title="ICASSP Challenges", organization="IEEE ICASSP", url="https://2026.ieeeicassp.org/",
         tier="tier1", domain="Speech", summary="IEEE's signal processing conference, hosts recurring speech/audio challenges."),

    # ---- Tier 1: More robotics/RL environments (GitHub-hosted) ----
    dict(title="MineDojo", organization="NVIDIA / Caltech", url="https://minedojo.org/",
         tier="tier1", domain="Reinforcement Learning", summary="Open-ended embodied agent benchmark built on Minecraft."),
    dict(title="Unity ML-Agents", organization="Unity Technologies", url="https://github.com/Unity-Technologies/ml-agents",
         tier="tier1", domain="Reinforcement Learning", summary="RL training toolkit and environment suite used in several agent competitions."),

    # ---- Tier 1: GitHub-hosted LLM/agent benchmarks ----
    dict(title="HumanEval Benchmark", organization="OpenAI", url="https://github.com/openai/human-eval",
         tier="tier1", domain="Agents", summary="Code-generation correctness benchmark, the standard for coding-agent evals."),
    dict(title="MMLU Benchmark", organization="UC Berkeley / Hendrycks et al.", url="https://github.com/hendrycks/test",
         tier="tier1", domain="NLP", summary="Massive Multitask Language Understanding benchmark, a standard LLM eval suite."),
    dict(title="GAIA Benchmark", organization="Meta AI / Hugging Face", url="https://huggingface.co/gaia-benchmark",
         tier="tier1", domain="Agents", summary="General AI Assistants benchmark for real-world agentic task completion."),

    # ---- Tier 1: Company-run official AI competition/program pages ----
    dict(title="Google AI Competitions", organization="Google AI", url="https://ai.google/",
         tier="tier1", domain="General ML", summary="Google's AI research hub, source of recurring open challenges."),
    dict(title="Google DeepMind Challenges", organization="Google DeepMind", url="https://deepmind.google/",
         tier="tier1", domain="General ML", summary="DeepMind research programs and occasional public challenges."),
    dict(title="NVIDIA Developer Challenges", organization="NVIDIA", url="https://developer.nvidia.com/",
         tier="tier1", domain="General ML", summary="NVIDIA developer program - hosts GTC hackathons and dev challenges."),
    dict(title="Hugging Face Community Events", organization="Hugging Face", url="https://huggingface.co/",
         tier="tier1", domain="General ML", summary="Frequent community sprints and model/dataset competitions."),
    dict(title="Mistral AI", organization="Mistral AI", url="https://mistral.ai/",
         tier="tier1", domain="NLP", summary="Open-weight LLM lab, occasional hackathons and fine-tuning challenges."),
    dict(title="Cohere", organization="Cohere", url="https://cohere.com/",
         tier="tier1", domain="NLP", summary="Enterprise LLM platform running periodic developer challenges."),
    dict(title="Databricks", organization="Databricks", url="https://www.databricks.com/",
         tier="tier1", domain="Data Science", summary="Data/AI platform running hackathons and the annual Data + AI Summit."),
    dict(title="Scale AI", organization="Scale AI", url="https://scale.com/",
         tier="tier1", domain="Data Science", summary="Data labeling and evaluation company, runs SEAL leaderboard evaluations."),
    dict(title="Waymo AI Research", organization="Waymo", url="https://waymo.com/research/",
         tier="tier1", domain="Robotics", summary="Autonomous driving research division, source of the Waymo Open Dataset challenges."),
    dict(title="Alibaba DAMO Academy", organization="Alibaba DAMO Academy", url="https://damo.alibaba.com/",
         tier="tier1", domain="General ML", summary="Alibaba's research division across NLP, vision, and quantum computing."),
    dict(title="Tencent AI Lab", organization="Tencent AI Lab", url="https://ai.tencent.com/ailab/en/",
         tier="tier1", domain="General ML", summary="Tencent's AI research lab across NLP, CV, and gaming AI."),
    dict(title="Huawei Noah's Ark Lab", organization="Huawei", url="https://www.noahlab.com.hk/",
         tier="tier1", domain="General ML", summary="Huawei's AI research lab, publishes open efficiency and NLP benchmarks."),
    dict(title="Baidu Research", organization="Baidu Research", url="http://research.baidu.com/",
         tier="tier1", domain="General ML", summary="Baidu's AI research division spanning NLP, autonomous driving, and speech."),
    dict(title="ByteDance AI Lab", organization="ByteDance", url="https://ailab.bytedance.com/",
         tier="tier1", domain="General ML", summary="ByteDance's research lab, recurring competitions in recommendation and vision."),
    dict(title="Adobe Research", organization="Adobe", url="https://research.adobe.com/",
         tier="tier1", domain="Multimodal / Generative", summary="Adobe's research division, strong generative media and creative AI focus."),
    dict(title="Intel AI Developer Program", organization="Intel", url="https://www.intel.com/content/www/us/en/developer/topic-technology/artificial-intelligence/overview.html",
         tier="tier1", domain="General ML", summary="Intel's AI developer program, periodic edge-AI hackathons and challenges."),
]

GOVERNMENT_AND_BUILDER_PLATFORMS = [
    # ---- Tier 3: Government / national hackathons ----
    dict(title="NASA Space Apps Challenge", organization="NASA", url="https://www.spaceappschallenge.org/",
         tier="tier3", domain="Data Science", summary="NASA's global annual hackathon using open space and earth science data."),
    dict(title="ISRO Open Challenges", organization="Indian Space Research Organisation", url="https://www.isro.gov.in/",
         tier="tier3", domain="Data Science", summary="India's space agency, periodically runs open data and innovation challenges."),
    dict(title="Smart India Hackathon", organization="Government of India", url="https://sih.gov.in/",
         tier="tier3", domain="General ML", summary="India's flagship national-level student hackathon across government ministries."),
    dict(title="DRDO Open Challenges", organization="Defence Research and Development Organisation", url="https://www.drdo.gov.in/",
         tier="tier3", domain="Robotics", summary="India's defense R&D body, runs open innovation and robotics challenges."),
    dict(title="Startup Weekend", organization="Techstars", url="https://startupweekend.org/",
         tier="tier3", domain="General ML", summary="54-hour global startup-building weekend event series, frequent AI tracks."),
    dict(title="Microsoft Imagine Cup", organization="Microsoft", url="https://imaginecup.microsoft.com/",
         tier="tier3", domain="General ML", summary="Microsoft's global student technology competition, strong AI track focus."),
    dict(title="Google Solution Challenge", organization="Google Developer Student Clubs", url="https://developers.google.com/community/gdsc-solution-challenge",
         tier="tier3", domain="General ML", summary="Google's annual student hackathon solving for the UN Sustainable Development Goals."),

    # ---- Tier 3: Web3 / builder grant ecosystems ----
    dict(title="Gitcoin Grants", organization="Gitcoin", url="https://www.gitcoin.co/",
         tier="tier3", domain="Agents", summary="Quadratic-funding grants platform for open-source and public-goods builders."),
    dict(title="Questbook", organization="Questbook", url="https://questbook.app/",
         tier="tier3", domain="Agents", summary="Web3 grants discovery and application platform."),
    dict(title="Superteam", organization="Superteam", url="https://superteam.fun/",
         tier="tier3", domain="Agents", summary="Solana ecosystem talent and bounty network, frequent builder challenges."),
    dict(title="Encode Club", organization="Encode Club", url="https://www.encode.club/",
         tier="tier3", domain="Agents", summary="Web3 hackathon and education community, runs recurring cohort hackathons."),
    dict(title="Open Source Collective", organization="Open Source Collective", url="https://oscollective.org/",
         tier="tier3", domain="General ML", summary="Fiscal host and funding platform for open-source projects and maintainers."),
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
         tier="tier3", domain="Finance / Quant", summary="Monthly quant puzzles used as an informal recruiting and skills challenge."),
    dict(title="Citadel Datathons", organization="Citadel / Citadel Securities", url="https://www.citadel.com/careers/students/",
         tier="tier3", domain="Finance / Quant", summary="Citadel's student datathon and quant challenge recruiting programs."),
    dict(title="Two Sigma Data Challenges", organization="Two Sigma", url="https://www.twosigma.com/careers/",
         tier="tier3", domain="Finance / Quant", summary="Two Sigma's recurring data science and quant modeling challenges."),
    dict(title="QuantConnect Competitions", organization="QuantConnect", url="https://www.quantconnect.com/competitions",
         tier="tier3", domain="Finance / Quant", summary="Algorithmic trading competitions on an open quant research platform."),

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
    all_entries = PLATFORMS + ELITE_ORGS + GOVERNMENT_AND_BUILDER_PLATFORMS

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
