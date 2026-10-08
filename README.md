# EKIP — Electrical Engineering AI Assistant

A domain-specific Retrieval-Augmented Generation (RAG) system designed for Electrical & Computer Engineering education.

## Overview

EKIP is an AI-powered academic assistant that allows students to ask technical questions and receive answers grounded in an indexed Electrical Engineering knowledge base.

Instead of requiring students to manually search through textbooks and academic material, EKIP retrieves the most relevant information and uses a local Large Language Model to generate an answer with source references.

## Architecture

Academic Documents
        │
        ▼
 Text Extraction / OCR
        │
        ▼
     Chunking
        │
        ▼
HuggingFace Embeddings
        │
        ▼
      FAISS
        │
        ▼
Relevant Context
        │
        ▼
 Mistral via Ollama
        │
        ▼
 Answer + Sources