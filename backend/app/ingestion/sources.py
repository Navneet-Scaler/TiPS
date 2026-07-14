"""Tier 1/2 source registry: official APIs and RSS feeds.
Add a source here and the RSS connector picks it up automatically -
this is the connector pattern from the plan: N sources, one connector."""

RSS_SOURCES = [
    # AI Labs
    {"name": "OpenAI Blog", "url": "https://openai.com/news/rss.xml", "organization": "OpenAI"},
    {"name": "Google DeepMind Blog", "url": "https://deepmind.google/blog/rss.xml", "organization": "Google DeepMind"},
    {"name": "Hugging Face Blog", "url": "https://huggingface.co/blog/feed.xml", "organization": "Hugging Face"},
    {"name": "NVIDIA Developer Blog", "url": "https://developer.nvidia.com/blog/feed", "organization": "NVIDIA"},
    {"name": "Microsoft Research Blog", "url": "https://www.microsoft.com/en-us/research/feed/", "organization": "Microsoft Research"},
    {"name": "Meta AI Blog", "url": "https://ai.meta.com/blog/rss/", "organization": "Meta AI"},
    {"name": "Berkeley AI Research", "url": "https://bair.berkeley.edu/blog/feed.xml", "organization": "Berkeley BAIR"},

    # Research - arXiv subdomains (NLP, CV, RL, robotics, multi-agent, HCI)
    {"name": "arXiv cs.AI", "url": "http://export.arxiv.org/rss/cs.AI", "organization": "arXiv"},
    {"name": "arXiv cs.LG", "url": "http://export.arxiv.org/rss/cs.LG", "organization": "arXiv"},
    {"name": "arXiv cs.CL", "url": "http://export.arxiv.org/rss/cs.CL", "organization": "arXiv"},
    {"name": "arXiv cs.CV", "url": "http://export.arxiv.org/rss/cs.CV", "organization": "arXiv"},
    {"name": "arXiv cs.RO", "url": "http://export.arxiv.org/rss/cs.RO", "organization": "arXiv"},
    {"name": "arXiv cs.MA", "url": "http://export.arxiv.org/rss/cs.MA", "organization": "arXiv"},
    {"name": "arXiv cs.HC", "url": "http://export.arxiv.org/rss/cs.HC", "organization": "arXiv"},
    {"name": "arXiv stat.ML", "url": "http://export.arxiv.org/rss/stat.ML", "organization": "arXiv"},

    # AI Safety / Alignment research ecosystem - the plan's "hidden signal" tier
    {"name": "LessWrong (AI)", "url": "https://www.lesswrong.com/feed.xml?view=curated-rss", "organization": "LessWrong"},
    {"name": "Alignment Forum", "url": "https://www.alignmentforum.org/feed.xml", "organization": "Alignment Forum"},
    {"name": "EA Forum", "url": "https://forum.effectivealtruism.org/feed.xml", "organization": "EA Forum"},

    # Research newsletters (human-curated digests, re-extracted as structured items)
    {"name": "Import AI", "url": "https://importai.substack.com/feed", "organization": "Import AI"},
    {"name": "The Batch", "url": "https://www.deeplearning.ai/the-batch/feed/", "organization": "DeepLearning.AI"},

    # Universities
    {"name": "MIT News AI", "url": "https://news.mit.edu/rss/topic/artificial-intelligence2", "organization": "MIT"},
    {"name": "Stanford HAI News", "url": "https://hai.stanford.edu/news/rss.xml", "organization": "Stanford HAI"},
    {"name": "CMU School of Computer Science", "url": "https://www.cs.cmu.edu/rss.xml", "organization": "CMU"},

    # Engineering / dev-tool blogs (career + product signal)
    {"name": "GitHub Blog", "url": "https://github.blog/feed/", "organization": "GitHub"},
    {"name": "Cloudflare Blog", "url": "https://blog.cloudflare.com/rss/", "organization": "Cloudflare"},
    {"name": "Vercel Blog", "url": "https://vercel.com/atom", "organization": "Vercel"},
    {"name": "Docker Blog", "url": "https://www.docker.com/blog/feed/", "organization": "Docker"},

    # Competitions / hackathons
    {"name": "Devpost Software Challenges", "url": "https://devpost.com/software/challenges.rss", "organization": "Devpost"},

    # Foundations / open source
    {"name": "Linux Foundation Blog", "url": "https://www.linuxfoundation.org/blog/rss.xml", "organization": "Linux Foundation"},
]

# Public JSON API sources - each connector below hits these directly (no scraping).

REDDIT_SUBREDDITS = [
    "MachineLearning",
    "LocalLLaMA",
    "artificial",
    "learnmachinelearning",
    "datascience",
    "computervision",
    "opensource",
    "PhD",
    "gradadmissions",
]

HN_KEYWORDS = ["AI hackathon", "AI fellowship", "AI residency", "open source AI", "AI grant", "AI internship"]

GITHUB_TOPICS = ["ai-agents", "llm", "machine-learning", "generative-ai"]

# Greenhouse job-board tokens (the string in boards-api.greenhouse.io/v1/boards/<token>/jobs)
GREENHOUSE_BOARDS = [
    {"token": "anthropic", "organization": "Anthropic"},
    {"token": "scaleai", "organization": "Scale AI"},
    {"token": "stripe", "organization": "Stripe"},
    {"token": "airbnb", "organization": "Airbnb"},
    {"token": "robinhood", "organization": "Robinhood"},
    {"token": "coinbase", "organization": "Coinbase"},
]
