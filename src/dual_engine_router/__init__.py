"""
Dual-Engine Router with LangChain
==================================
Routes queries to PDF RAG or SQL engines using LangChain framework
"""

from .langchain_rag import LangChainDualEngineRAG

__all__ = ['LangChainDualEngineRAG']
