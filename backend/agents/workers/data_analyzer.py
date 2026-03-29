from langchain.tools import tool

@tool
def query_database(sql_description: str) -> str:
    """Query the enterprise database based on a natural language description. Returns tabular data."""
    # Simulated enterprise data responses
    data_map = {
        "revenue": {
            "summary": "Q3 2025 Revenue Summary",
            "data": [
                {"quarter": "Q1", "revenue": 2400000, "growth": "12%"},
                {"quarter": "Q2", "revenue": 2850000, "growth": "18%"},
                {"quarter": "Q3", "revenue": 3420000, "growth": "20%"},
            ],
            "total": "$8,670,000"
        },
        "subscription": {
            "summary": "Active Subscriptions by Tier",
            "data": [
                {"tier": "Copilot Standard", "count": 1240, "mrr": "$62,000"},
                {"tier": "Enterprise Copilot", "count": 385, "mrr": "$192,500"},
                {"tier": "Custom AI Agents", "count": 47, "mrr": "$141,000"},
            ],
            "total_mrr": "$395,500"
        },
        "employee": {
            "summary": "Employee Distribution",
            "data": [
                {"department": "Engineering", "headcount": 128, "percentage": "42%"},
                {"department": "Sales", "headcount": 64, "percentage": "21%"},
                {"department": "Marketing", "headcount": 38, "percentage": "12%"},
                {"department": "Support", "headcount": 45, "percentage": "15%"},
                {"department": "Operations", "headcount": 30, "percentage": "10%"},
            ],
            "total": 305
        }
    }
    
    query_lower = sql_description.lower()
    for key, value in data_map.items():
        if key in query_lower:
            import json
            return json.dumps(value, indent=2)
    
    return '{"summary": "No matching data found", "data": [], "note": "Try querying about revenue, subscriptions, or employees."}'


@tool
def generate_chart_data(data_description: str) -> str:
    """Generate chart-ready data from a description. Returns JSON with chart type and data points."""
    import json
    
    desc_lower = data_description.lower()
    
    if "revenue" in desc_lower or "financial" in desc_lower:
        return json.dumps({
            "chart_type": "bar",
            "title": "Quarterly Revenue (2025)",
            "x_key": "quarter",
            "y_key": "revenue",
            "data": [
                {"quarter": "Q1", "revenue": 2400000},
                {"quarter": "Q2", "revenue": 2850000},
                {"quarter": "Q3", "revenue": 3420000},
                {"quarter": "Q4", "revenue": 3800000},
            ]
        })
    elif "subscription" in desc_lower or "tier" in desc_lower:
        return json.dumps({
            "chart_type": "pie",
            "title": "Subscriptions by Tier",
            "name_key": "tier",
            "value_key": "count",
            "data": [
                {"tier": "Standard", "count": 1240},
                {"tier": "Enterprise", "count": 385},
                {"tier": "Custom Agents", "count": 47},
            ]
        })
    else:
        return json.dumps({
            "chart_type": "bar",
            "title": "Department Headcount",
            "x_key": "department",
            "y_key": "headcount",
            "data": [
                {"department": "Engineering", "headcount": 128},
                {"department": "Sales", "headcount": 64},
                {"department": "Marketing", "headcount": 38},
                {"department": "Support", "headcount": 45},
                {"department": "Ops", "headcount": 30},
            ]
        })


@tool
def calculate_statistics(dataset_name: str) -> str:
    """Calculate statistical summaries for enterprise datasets."""
    import json
    
    stats_map = {
        "revenue": {
            "metric": "Quarterly Revenue",
            "mean": "$2,890,000",
            "median": "$2,850,000",
            "min": "$2,400,000 (Q1)",
            "max": "$3,420,000 (Q3)",
            "yoy_growth": "18.5%",
            "trend": "Upward"
        },
        "support": {
            "metric": "Support Ticket Resolution",
            "avg_resolution_hours": 4.2,
            "sla_compliance": "94.7%",
            "csat_score": 4.6,
            "tickets_per_month": 342,
            "trend": "Improving"
        },
        "performance": {
            "metric": "System Performance",
            "avg_latency_ms": 245,
            "p99_latency_ms": 890,
            "uptime": "99.97%",
            "error_rate": "0.03%",
            "trend": "Stable"
        }
    }
    
    name_lower = dataset_name.lower()
    for key, value in stats_map.items():
        if key in name_lower:
            return json.dumps(value, indent=2)
    
    return json.dumps({"error": "Dataset not found. Available: revenue, support, performance"})


def get_data_analyzer_tools():
    """Return all data analyzer tools."""
    return [query_database, generate_chart_data, calculate_statistics]
