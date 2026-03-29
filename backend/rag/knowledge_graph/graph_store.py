"""
Neo4j Graph Store — Connection Manager
Handles Neo4j driver lifecycle and Cypher query execution.
Falls back gracefully if Neo4j is not available.
"""

import os
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "enterprise_ai")

_driver = None


def get_driver():
    """Get or create a Neo4j driver instance."""
    global _driver
    if _driver is None:
        try:
            from neo4j import GraphDatabase
            _driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
            # Verify connectivity
            _driver.verify_connectivity()
            print("✅ Connected to Neo4j successfully.")
        except Exception as e:
            print(f"⚠️ Neo4j connection failed: {e}. Graph features will be disabled.")
            _driver = None
    return _driver


def close_driver():
    """Close the Neo4j driver."""
    global _driver
    if _driver:
        _driver.close()
        _driver = None


def run_cypher(query: str, params: dict = None):
    """Execute a Cypher query and return the results as a list of dicts."""
    driver = get_driver()
    if driver is None:
        return []
    
    try:
        with driver.session() as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]
    except Exception as e:
        print(f"Cypher query error: {e}")
        return []


def is_available() -> bool:
    """Check if Neo4j is available."""
    return get_driver() is not None
