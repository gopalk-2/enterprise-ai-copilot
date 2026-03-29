"""
Graph Ingestion — Entity & Relationship Extraction
Extracts entities (Department, Policy, Person, Product, Tool) and relationships
from documents using the LLM, then stores them in Neo4j.
"""

import json
import re
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from .graph_store import run_cypher, is_available

llm = OllamaLLM(model="mistral", temperature=0.0)

extraction_prompt = ChatPromptTemplate.from_template(
    """You are an entity and relationship extractor for an Enterprise Knowledge Graph.

Given the following document text, extract ALL entities and relationships.

Entity types: Department, Policy, Person, Role, Product, Tool, Location, Process
Relationship types: OWNS, AUTHORED_BY, APPLIES_TO, USES, LOCATED_IN, REPORTS_TO, PART_OF, MANAGES

Output ONLY a valid JSON object with this exact structure (no other text):
{{
  "entities": [
    {{"type": "Department", "name": "Engineering"}},
    {{"type": "Policy", "name": "Remote Work Policy"}}
  ],
  "relationships": [
    {{"from": "Engineering", "to": "Remote Work Policy", "type": "OWNS"}},
    {{"from": "Remote Work Policy", "to": "All Employees", "type": "APPLIES_TO"}}
  ]
}}

DOCUMENT TEXT:
{text}

JSON OUTPUT:"""
)


def extract_entities_and_relationships(text: str) -> dict:
    """Use LLM to extract entities and relationships from text."""
    try:
        response = llm.invoke(extraction_prompt.format(text=text[:3000]))
        
        # Extract JSON from the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {"entities": [], "relationships": []}
    except Exception as e:
        print(f"Entity extraction error: {e}")
        return {"entities": [], "relationships": []}


def ingest_to_graph(text: str, source_name: str):
    """Extract entities from text and store them in Neo4j."""
    if not is_available():
        print(f"⚠️ Neo4j not available. Skipping graph ingestion for {source_name}")
        return
    
    extracted = extract_entities_and_relationships(text)
    entities = extracted.get("entities", [])
    relationships = extracted.get("relationships", [])
    
    # Create entity nodes
    for entity in entities:
        entity_type = entity.get("type", "Entity")
        name = entity.get("name", "")
        if not name:
            continue
        
        cypher = f"""
        MERGE (n:{entity_type} {{name: $name}})
        SET n.source = $source
        """
        run_cypher(cypher, {"name": name, "source": source_name})
    
    # Create relationships
    for rel in relationships:
        from_name = rel.get("from", "")
        to_name = rel.get("to", "")
        rel_type = rel.get("type", "RELATED_TO")
        
        if not from_name or not to_name:
            continue
        
        # Use generic node matching since we may not know the exact labels
        cypher = f"""
        MATCH (a {{name: $from_name}})
        MATCH (b {{name: $to_name}})
        MERGE (a)-[:{rel_type}]->(b)
        """
        run_cypher(cypher, {"from_name": from_name, "to_name": to_name})
    
    print(f"📊 Graph ingested: {len(entities)} entities, {len(relationships)} relationships from {source_name}")


def ingest_all_documents():
    """Ingest all documents from the data directory into the knowledge graph."""
    import os
    
    data_path = "/Users/gopalkumar/Desktop/enterprise-ai-assistant/data/documents"
    
    if not os.path.exists(data_path):
        print(f"Data path not found: {data_path}")
        return
    
    # Use the existing document loader
    from ingestion.pipeline.document_loader import load_documents
    
    raw_docs = load_documents()
    print(f"Ingesting {len(raw_docs)} documents into knowledge graph...")
    
    for doc in raw_docs:
        source = doc["metadata"].get("source", "unknown")
        ingest_to_graph(doc["text"], source)
    
    print("✅ Knowledge graph ingestion complete!")
