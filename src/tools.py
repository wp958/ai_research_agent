"""
Agent Tools
Each tool is a function that the Agent can call.
"""

import os
from tavily import TavilyClient
from config import TAVILY_API_KEY, MAX_SEARCH_RESULTS

# ============================================================
# [NEW] Import ChromaDB + Embedding for RAG tool
# ============================================================
import chromadb
from sentence_transformers import SentenceTransformer

# Path to project 1's vector database
RAG_DB_DIR = r"D:\zhuo mian\rag\src\vector_db"
RAG_EMBEDDING_MODEL = "shibing624/text2vec-base-chinese"

# Load RAG components (only once)
_rag_model = None
_rag_collection = None

def _init_rag():
    """Load RAG model and database (lazy loading)"""
    global _rag_model, _rag_collection
    if _rag_model is None:
        print("  Loading RAG embedding model...")
        _rag_model = SentenceTransformer(RAG_EMBEDDING_MODEL)
        print("  Loading RAG database...")
        client = chromadb.PersistentClient(path=RAG_DB_DIR)
        _rag_collection = client.get_collection("capital")
        print("  RAG ready! %d chunks loaded" % _rag_collection.count())


# ============================================================
# Tool 1: Web Search (Tavily)
# ============================================================

def web_search(query):
    """
    Search the internet for real-time information.
    """
    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        results = client.search(query, max_results=MAX_SEARCH_RESULTS)

        if not results.get('results'):
            return "No results found."

        output = []
        for i, item in enumerate(results['results']):
            title = item.get('title', 'No title')
            url = item.get('url', '')
            content = item.get('content', '')[:300]
            output.append(
                "[Result %d]\nTitle: %s\nURL: %s\nContent: %s" % (i + 1, title, url, content)
            )

        return "\n\n".join(output)

    except Exception as e:
        return "Search failed: %s" % str(e)


# ============================================================
# [NEW] Tool 2: Knowledge Base Search (RAG from Project 1)
# ============================================================

def knowledge_search(query):
    """
    Search the local knowledge base (Capital by Marx).
    Uses vector similarity search on ChromaDB.
    """
    try:
        _init_rag()

        query_embedding = _rag_model.encode([query]).tolist()

        results = _rag_collection.query(
            query_embeddings=query_embedding,
            n_results=3
        )

        if not results['documents'][0]:
            return "No relevant content found in knowledge base."

        output = []
        documents = results['documents'][0]
        distances = results['distances'][0]

        for i, (doc, dist) in enumerate(zip(documents, distances)):
            relevance = max(0, (1 - dist) * 100)
            output.append(
                "[Knowledge %d] (relevance: %.1f%%)\n%s" % (i + 1, relevance, doc[:400])
            )

        return "\n\n".join(output)

    except Exception as e:
        return "Knowledge search failed: %s" % str(e)


# ============================================================
# Tool 3: Text Summarizer
# ============================================================

def summarize_text(text):
    """
    Summarize a long text into key points.
    """
    if not text or len(text) < 100:
        return text

    sentences = []
    for sep in ['。', '！', '？', '. ', '! ', '? ']:
        if sep in text:
            parts = text.split(sep)
            for p in parts:
                p = p.strip()
                if len(p) > 20:
                    sentences.append(p + sep.strip())
            break

    if not sentences:
        return text[:500] + "..."

    sentences.sort(key=len, reverse=True)
    top_sentences = sentences[:5]

    return "\n".join("- %s" % s for s in top_sentences)


# ============================================================
# Tool 4: Calculator
# ============================================================

def calculate(expression):
    """
    Evaluate a math expression safely.
    """
    try:
        allowed = set('0123456789+-*/.() ')
        if not all(c in allowed for c in expression):
            return "Error: invalid characters in expression"

        result = eval(expression)
        return "%s = %s" % (expression, str(result))

    except Exception as e:
        return "Calculation error: %s" % str(e)


# ============================================================
# Tool Definitions (for LLM Function Calling)
# ============================================================

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the internet for real-time information, current events, recent news, or anything that requires up-to-date information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query keywords"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "knowledge_search",
            "description": "Search the local knowledge base which contains the complete text of"
                           " Capital (Das Kapital) by Karl Marx. Use this tool when the user asks"
                           " about economics, capitalism, commodities, surplus value, labor,"
                           " capital accumulation, or anything related to Marxist economic theory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query about Marxist economics or Capital"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "summarize_text",
            "description": "Summarize a long text into key points. Use this when you have a long text and need to extract the main ideas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The long text to summarize"
                    }
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a mathematical expression. Use this when the user needs mathematical calculations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The math expression to evaluate, e.g. '2+3*4'"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]

# Map tool names to functions
TOOL_MAP = {
    "web_search": web_search,
    "knowledge_search": knowledge_search,
    "summarize_text": summarize_text,
    "calculate": calculate,
}