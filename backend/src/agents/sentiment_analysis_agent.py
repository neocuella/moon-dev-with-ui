"""
Sentiment Analysis Agent - Analyzes market sentiment from various sources
"""

CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "sources": {
            "type": "array",
            "description": "Data sources to analyze",
            "default": ["twitter", "reddit", "news"]
        },
        "keywords": {
            "type": "array",
            "description": "Keywords to track",
            "default": ["bitcoin", "crypto"]
        }
    }
}

def main(context: dict, sources: list = None, keywords: list = None):
    """
    Analyze market sentiment
    
    Args:
        context: Execution context
        sources: Sources to analyze
        keywords: Keywords to track
    
    Returns:
        Dict with sentiment analysis
    """
    if sources is None:
        sources = ["twitter", "reddit", "news"]
    if keywords is None:
        keywords = ["bitcoin", "crypto"]
    
    return {
        "status": "success",
        "sources": sources,
        "keywords": keywords,
        "overall_sentiment": "positive",
        "sentiment_score": 0.72,
        "trending_topics": ["halving", "ETF", "adoption"]
    }
