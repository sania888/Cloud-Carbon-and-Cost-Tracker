# recommender.py

"""
Recommender Module for Cloud Carbon & Cost Tracker
--------------------------------------------------
Purpose:
    - Analyze calculated cost & emissions data
    - Provide optimization suggestions
    - Act as a foundation for rule-based and AI-enhanced recommendations

Integration:
    - Takes processed output from calculator.py (DataFrame or dict)
    - Can be linked to visualizations for context
"""

import pandas as pd

def generate_recommendations(data: pd.DataFrame) -> list:
    """
    Generate optimization recommendations based on cost and emissions data.

    Parameters:
        data (pd.DataFrame): Must include columns like:
            - 'service'
            - 'region'
            - 'cost_usd'
            - 'emissions_kg'

    Returns:
        list: List of recommendation dicts
    """
    recommendations = []

    # Placeholder for logic (to be implemented in Phase 2)
    # Example structure:
    # recommendations.append({
    #     "category": "Cost Optimization",
    #     "message": "Consider switching to reserved instances for EC2.",
    #     "priority": "High"
    # })

    return recommendations


def filter_by_category(recommendations: list, category: str) -> list:
    """
    Filter recommendations by category.

    Parameters:
        recommendations (list): List of recommendation dicts
        category (str): Category name (e.g., "Cost Optimization")

    Returns:
        list: Filtered recommendations
    """
    return [rec for rec in recommendations if rec.get("category") == category]


def rank_recommendations(recommendations: list) -> list:
    """
    Rank recommendations by priority.

    Parameters:
        recommendations (list): List of recommendation dicts

    Returns:
        list: Sorted recommendations
    """
    priority_order = {"High": 1, "Medium": 2, "Low": 3}
    return sorted(
        recommendations,
        key=lambda x: priority_order.get(x.get("priority", "Medium"), 2)
    )


def display_recommendations(recommendations: list) -> None:
    """
    Print recommendations in a readable format.

    Parameters:
        recommendations (list): List of recommendation dicts
    """
    if not recommendations:
        print("✅ No recommendations at this time.")
        return

    print("\n--- Optimization Recommendations ---")
    for rec in recommendations:
        print(f"[{rec.get('priority', 'Medium')}] {rec.get('category', 'General')}: {rec.get('message', '')}")


if __name__ == "__main__":
    # Example usage with mock data
    sample_data = pd.DataFrame({
        "service": ["EC2", "S3", "RDS"],
        "region": ["us-east-1", "eu-west-1", "ap-south-1"],
        "cost_usd": [1200, 300, 450],
        "emissions_kg": [500, 50, 200]
    })

    recs = generate_recommendations(sample_data)
    recs = rank_recommendations(recs)
    display_recommendations(recs)
