"""
Agent Metadata Definitions
Defines inputs, outputs, and dependencies for each agent type
"""

from typing import Dict, List, Any

# Standard data types for connections
class DataType:
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"
    DATAFRAME = "dataframe"
    SIGNAL = "signal"  # Trading signal (BUY/SELL/NOTHING)
    RISK_STATUS = "risk_status"
    MARKET_DATA = "market_data"
    POSITION = "position"
    SENTIMENT = "sentiment"


# Agent metadata mapping
AGENT_METADATA: Dict[str, Dict[str, Any]] = {
    # ============================================================================
    # TRADING AGENTS
    # ============================================================================
    
    "risk_agent": {
        "category": "Trading",
        "description": "Risk management - checks P&L, limits, balances. RUNS FIRST before any trading.",
        "inputs": [
            {"name": "portfolio_data", "type": DataType.OBJECT, "required": False, "description": "Current portfolio state"}
        ],
        "outputs": [
            {"name": "risk_status", "type": DataType.RISK_STATUS, "description": "Risk assessment with can_trade flag"},
            {"name": "can_trade", "type": DataType.BOOLEAN, "description": "Whether trading is allowed"},
            {"name": "limits", "type": DataType.OBJECT, "description": "Current risk limits"}
        ],
        "depends_on": [],  # Runs first
        "tags": ["risk", "circuit-breaker", "first-run"]
    },
    
    "trading_agent": {
        "category": "Trading",
        "description": "Primary trading execution agent. Supports Hyperliquid, BirdEye, Extended Exchange.",
        "inputs": [
            {"name": "risk_status", "type": DataType.RISK_STATUS, "required": True, "from": "risk_agent"},
            {"name": "market_signals", "type": DataType.ARRAY, "required": False, "description": "Signals from analysis agents"},
            {"name": "sentiment_score", "type": DataType.SENTIMENT, "required": False, "from": "sentiment_agent"}
        ],
        "outputs": [
            {"name": "trade_decision", "type": DataType.SIGNAL, "description": "BUY, SELL, or NOTHING"},
            {"name": "confidence", "type": DataType.NUMBER, "description": "Confidence score 0-1"},
            {"name": "position", "type": DataType.POSITION, "description": "Current position state"}
        ],
        "depends_on": ["risk_agent"],
        "tags": ["trading", "execution", "swarm-capable"]
    },
    
    "strategy_agent": {
        "category": "Trading",
        "description": "Executes user-defined strategies from src/strategies/",
        "inputs": [
            {"name": "market_data", "type": DataType.MARKET_DATA, "required": True},
            {"name": "strategy_name", "type": DataType.STRING, "required": True}
        ],
        "outputs": [
            {"name": "signal", "type": DataType.SIGNAL, "description": "Strategy signal"},
            {"name": "confidence", "type": DataType.NUMBER}
        ],
        "depends_on": [],
        "tags": ["trading", "strategy", "backtest"]
    },
    
    "copybot_agent": {
        "category": "Trading",
        "description": "Copies trades from successful wallets/traders",
        "inputs": [
            {"name": "wallet_addresses", "type": DataType.ARRAY, "required": True}
        ],
        "outputs": [
            {"name": "copy_signals", "type": DataType.ARRAY, "description": "Trades to copy"},
            {"name": "wallet_performance", "type": DataType.OBJECT}
        ],
        "depends_on": [],
        "tags": ["trading", "copy-trading", "social"]
    },
    
    # ============================================================================
    # MARKET ANALYSIS AGENTS
    # ============================================================================
    
    "sentiment_agent": {
        "category": "Market Analysis",
        "description": "Analyzes market sentiment from social media, news",
        "inputs": [
            {"name": "tokens", "type": DataType.ARRAY, "required": True, "description": "Tokens to analyze"}
        ],
        "outputs": [
            {"name": "sentiment_score", "type": DataType.SENTIMENT, "description": "Overall sentiment -1 to 1"},
            {"name": "trending_topics", "type": DataType.ARRAY}
        ],
        "depends_on": [],
        "tags": ["analysis", "sentiment", "twitter", "social-media"]
    },
    
    "whale_agent": {
        "category": "Market Analysis",
        "description": "Tracks large wallet movements (whale watching)",
        "inputs": [
            {"name": "tokens", "type": DataType.ARRAY, "required": True}
        ],
        "outputs": [
            {"name": "whale_activity", "type": DataType.ARRAY, "description": "Recent large transactions"},
            {"name": "accumulation_signal", "type": DataType.SIGNAL}
        ],
        "depends_on": [],
        "tags": ["analysis", "on-chain", "whales"]
    },
    
    "funding_agent": {
        "category": "Market Analysis",
        "description": "Monitors perpetual funding rates across exchanges",
        "inputs": [
            {"name": "symbols", "type": DataType.ARRAY, "required": True}
        ],
        "outputs": [
            {"name": "funding_rates", "type": DataType.OBJECT},
            {"name": "arb_opportunities", "type": DataType.ARRAY}
        ],
        "depends_on": [],
        "tags": ["analysis", "funding", "arbitrage"]
    },
    
    "liquidation_agent": {
        "category": "Market Analysis",
        "description": "Tracks liquidation data from exchanges",
        "inputs": [
            {"name": "symbols", "type": DataType.ARRAY, "required": True}
        ],
        "outputs": [
            {"name": "liquidation_data", "type": DataType.OBJECT},
            {"name": "volatility_signal", "type": DataType.SIGNAL}
        ],
        "depends_on": [],
        "tags": ["analysis", "liquidations", "volatility"]
    },
    
    "chartanalysis_agent": {
        "category": "Market Analysis",
        "description": "Technical analysis using AI vision models",
        "inputs": [
            {"name": "symbol", "type": DataType.STRING, "required": True},
            {"name": "timeframe", "type": DataType.STRING, "required": False}
        ],
        "outputs": [
            {"name": "chart_pattern", "type": DataType.STRING},
            {"name": "signal", "type": DataType.SIGNAL}
        ],
        "depends_on": [],
        "tags": ["analysis", "technical", "ai-vision"]
    },
    
    "coingecko_agent": {
        "category": "Market Analysis",
        "description": "Fetches token metadata from CoinGecko API",
        "inputs": [
            {"name": "token_ids", "type": DataType.ARRAY, "required": True}
        ],
        "outputs": [
            {"name": "token_metadata", "type": DataType.OBJECT},
            {"name": "market_data", "type": DataType.MARKET_DATA}
        ],
        "depends_on": [],
        "tags": ["analysis", "metadata", "coingecko"]
    },
    
    # ============================================================================
    # RESEARCH AGENTS
    # ============================================================================
    
    "rbi_agent": {
        "category": "Research",
        "description": "Research-Based Inference - codes backtests from videos/PDFs/text",
        "inputs": [
            {"name": "source", "type": DataType.STRING, "required": True, "description": "YouTube URL, PDF path, or text description"}
        ],
        "outputs": [
            {"name": "backtest_code", "type": DataType.STRING},
            {"name": "backtest_results", "type": DataType.OBJECT},
            {"name": "performance_metrics", "type": DataType.OBJECT}
        ],
        "depends_on": [],
        "tags": ["research", "backtest", "deepseek", "strategy-generation"]
    },
    
    "research_agent": {
        "category": "Research",
        "description": "General market research and analysis",
        "inputs": [
            {"name": "research_topic", "type": DataType.STRING, "required": True}
        ],
        "outputs": [
            {"name": "research_report", "type": DataType.STRING},
            {"name": "opportunities", "type": DataType.ARRAY}
        ],
        "depends_on": [],
        "tags": ["research", "analysis"]
    },
    
    "websearch_agent": {
        "category": "Research",
        "description": "Web search capabilities for market research",
        "inputs": [
            {"name": "query", "type": DataType.STRING, "required": True}
        ],
        "outputs": [
            {"name": "search_results", "type": DataType.ARRAY},
            {"name": "summary", "type": DataType.STRING}
        ],
        "depends_on": [],
        "tags": ["research", "web-search"]
    },
    
    # ============================================================================
    # ARBITRAGE AGENTS
    # ============================================================================
    
    "fundingarb_agent": {
        "category": "Arbitrage",
        "description": "Funding rate arbitrage strategies",
        "inputs": [
            {"name": "symbols", "type": DataType.ARRAY, "required": True}
        ],
        "outputs": [
            {"name": "arb_opportunities", "type": DataType.ARRAY},
            {"name": "expected_yield", "type": DataType.NUMBER}
        ],
        "depends_on": ["funding_agent"],
        "tags": ["arbitrage", "funding-rate"]
    },
    
    "listingarb_agent": {
        "category": "Arbitrage",
        "description": "New listing arbitrage opportunities",
        "inputs": [
            {"name": "exchanges", "type": DataType.ARRAY, "required": True}
        ],
        "outputs": [
            {"name": "listing_opportunities", "type": DataType.ARRAY},
            {"name": "price_differences", "type": DataType.OBJECT}
        ],
        "depends_on": [],
        "tags": ["arbitrage", "listings", "new-tokens"]
    },
    
    # ============================================================================
    # SPECIALIZED TRADING AGENTS
    # ============================================================================
    
    "sniper_agent": {
        "category": "Specialized Trading",
        "description": "Fast execution for new token launches",
        "inputs": [
            {"name": "token_address", "type": DataType.STRING, "required": True}
        ],
        "outputs": [
            {"name": "execution_result", "type": DataType.OBJECT},
            {"name": "entry_price", "type": DataType.NUMBER}
        ],
        "depends_on": [],
        "tags": ["specialized", "launch", "fast-execution"]
    },
    
    "solana_agent": {
        "category": "Specialized Trading",
        "description": "Solana-specific trading operations",
        "inputs": [
            {"name": "token_address", "type": DataType.STRING, "required": True}
        ],
        "outputs": [
            {"name": "position", "type": DataType.POSITION},
            {"name": "transaction_hash", "type": DataType.STRING}
        ],
        "depends_on": [],
        "tags": ["specialized", "solana", "dex"]
    },
    
    "polymarket_agent": {
        "category": "Specialized Trading",
        "description": "Polymarket prediction market integration",
        "inputs": [
            {"name": "event_id", "type": DataType.STRING, "required": True}
        ],
        "outputs": [
            {"name": "prediction", "type": DataType.OBJECT},
            {"name": "bet_size", "type": DataType.NUMBER}
        ],
        "depends_on": [],
        "tags": ["specialized", "prediction-market", "polymarket"]
    },
    
    # ============================================================================
    # COORDINATION AGENTS
    # ============================================================================
    
    "swarm_agent": {
        "category": "Coordination",
        "description": "Coordinates multiple agents simultaneously",
        "inputs": [
            {"name": "agent_configs", "type": DataType.ARRAY, "required": True}
        ],
        "outputs": [
            {"name": "swarm_results", "type": DataType.OBJECT},
            {"name": "consensus", "type": DataType.OBJECT}
        ],
        "depends_on": [],
        "tags": ["coordination", "multi-agent", "swarm"]
    },
}


def get_agent_metadata(agent_type: str) -> Dict[str, Any]:
    """Get metadata for a specific agent type"""
    return AGENT_METADATA.get(agent_type, {
        "category": "Other",
        "description": f"{agent_type.replace('_', ' ').title()}",
        "inputs": [],
        "outputs": [],
        "depends_on": [],
        "tags": []
    })


def can_connect(source_agent: str, target_agent: str) -> Dict[str, Any]:
    """
    Check if two agents can be connected
    
    Returns:
        {
            "valid": bool,
            "reason": str,
            "compatible_types": list
        }
    """
    source_meta = get_agent_metadata(source_agent)
    target_meta = get_agent_metadata(target_agent)
    
    # Check if target depends on source
    if source_agent in target_meta.get("depends_on", []):
        return {
            "valid": True,
            "reason": f"{target_agent} depends on {source_agent}",
            "required": True
        }
    
    # Check if any source outputs match target inputs
    source_outputs = {out["type"] for out in source_meta.get("outputs", [])}
    target_inputs = {inp["type"] for inp in target_meta.get("inputs", [])}
    
    compatible = source_outputs & target_inputs
    
    if compatible:
        return {
            "valid": True,
            "reason": f"Compatible types: {', '.join(compatible)}",
            "compatible_types": list(compatible)
        }
    
    return {
        "valid": False,
        "reason": "No compatible input/output types",
        "compatible_types": []
    }


def get_workflow_templates() -> List[Dict[str, Any]]:
    """Get pre-defined workflow templates"""
    return [
        {
            "name": "Risk-First Trading",
            "description": "Safe trading with risk checks",
            "agents": ["risk_agent", "trading_agent"],
            "connections": [
                {"from": "risk_agent", "to": "trading_agent", "type": "risk_status"}
            ]
        },
        {
            "name": "Sentiment-Driven Trading",
            "description": "Trade based on social sentiment",
            "agents": ["sentiment_agent", "risk_agent", "trading_agent"],
            "connections": [
                {"from": "sentiment_agent", "to": "trading_agent", "type": "sentiment"},
                {"from": "risk_agent", "to": "trading_agent", "type": "risk_status"}
            ]
        },
        {
            "name": "Multi-Signal Analysis",
            "description": "Combine multiple analysis sources",
            "agents": ["sentiment_agent", "whale_agent", "liquidation_agent", "risk_agent", "trading_agent"],
            "connections": [
                {"from": "sentiment_agent", "to": "trading_agent"},
                {"from": "whale_agent", "to": "trading_agent"},
                {"from": "liquidation_agent", "to": "trading_agent"},
                {"from": "risk_agent", "to": "trading_agent"}
            ]
        },
        {
            "name": "Funding Arbitrage",
            "description": "Exploit funding rate differences",
            "agents": ["funding_agent", "fundingarb_agent", "trading_agent"],
            "connections": [
                {"from": "funding_agent", "to": "fundingarb_agent"},
                {"from": "fundingarb_agent", "to": "trading_agent"}
            ]
        },
        {
            "name": "Research to Strategy",
            "description": "Research strategy and backtest",
            "agents": ["rbi_agent", "strategy_agent", "trading_agent"],
            "connections": [
                {"from": "rbi_agent", "to": "strategy_agent"},
                {"from": "strategy_agent", "to": "trading_agent"}
            ]
        }
    ]
