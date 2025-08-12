"""Utility functions for the NSE Trader application."""

def format_currency(value: float) -> str:
    """Format value as Nigerian Naira."""
    if value >= 1_000_000_000_000:  # Trillion
        return f"₦{value/1_000_000_000_000:.2f}T"
    elif value >= 1_000_000_000:  # Billion
        return f"₦{value/1_000_000_000:.2f}B"
    elif value >= 1_000_000:  # Million
        return f"₦{value/1_000_000:.2f}M"
    elif value >= 1_000:  # Thousand
        return f"₦{value/1_000:.2f}K"
    else:
        return f"₦{value:.2f}"

def format_number(value: float, decimals: int = 2) -> str:
    """Format large numbers with K, M, B, T suffixes."""
    if value >= 1_000_000_000_000:  # Trillion
        return f"{value/1_000_000_000_000:.{decimals}f}T"
    elif value >= 1_000_000_000:  # Billion
        return f"{value/1_000_000_000:.{decimals}f}B"
    elif value >= 1_000_000:  # Million
        return f"{value/1_000_000:.{decimals}f}M"
    elif value >= 1_000:  # Thousand
        return f"{value/1_000:.{decimals}f}K"
    else:
        return f"{value:.{decimals}f}"
