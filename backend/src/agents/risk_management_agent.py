"""
Risk Management Agent - Manages position sizing and risk parameters
"""

CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "max_position_size": {
            "type": "number",
            "description": "Maximum position size in USD",
            "default": 10000
        },
        "stop_loss_pct": {
            "type": "number",
            "description": "Stop loss percentage",
            "default": 2.0
        },
        "take_profit_pct": {
            "type": "number",
            "description": "Take profit percentage",
            "default": 5.0
        }
    }
}

def main(context: dict, max_position_size: float = 10000, stop_loss_pct: float = 2.0, take_profit_pct: float = 5.0):
    """
    Calculate risk parameters for trade
    
    Args:
        context: Execution context
        max_position_size: Max position in USD
        stop_loss_pct: Stop loss percentage
        take_profit_pct: Take profit percentage
    
    Returns:
        Dict with risk parameters
    """
    return {
        "status": "success",
        "max_position": max_position_size,
        "stop_loss": stop_loss_pct,
        "take_profit": take_profit_pct,
        "risk_reward_ratio": take_profit_pct / stop_loss_pct
    }
