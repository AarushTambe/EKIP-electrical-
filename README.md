# EKIP — Electrical Engineering AI Assistant

> A domain-specific Retrieval-Augmented Generation (RAG) system for Electrical & Computer Engineering education.

## Overview

EKIP is an AI-powered academic assistant designed to help Electrical & Computer Engineering students resolve technical doubts using a curated academic knowledge base.

Instead of requiring students to manually search through textbooks, notes, and other academic resources, EKIP retrieves the most relevant information and uses a local Large Language Model to generate a grounded answer with source references.

The current system is being developed specifically toward the needs of **Electrical & Computer Engineering students at MIT World Peace University (MIT-WPU), Pune**.

## Problem

Electrical Engineering students often need to search across multiple textbooks, lecture materials, notes, and academic resources to resolve a single technical doubt.

This creates several problems:

- Time-consuming manual searching
- Difficulty locating the most relevant section of a textbook
- Information distributed across multiple sources
- Difficulty interpreting large technical documents
- No single interface for asking academic questions

EKIP aims to provide a simpler interaction:

**Login → Ask a doubt → Get the answer.**

The complexity of document processing, indexing, retrieval, and knowledge management remains behind the interface.

## Current Architecture

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