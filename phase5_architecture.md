# AI Sales Acceleration Engine — Architecture

## High-Level Architecture

```mermaid
flowchart TB
    subgraph UI["Presentation Layer"]
        Dashboard["Streamlit Dashboard\n(Port 8501)"]
    end

    subgraph API["API Layer"]
        FastAPI["FastAPI Server\n(Port 8000)"]
    end

    subgraph Modules["Core AI Modules"]
        M1["Module 1\nLead Scoring\n(XGBoost)"]
        M2["Module 2\nEmail Personalization\n(RAG + optional LLM)"]
        M3["Module 3\nCall Intelligence\n(Rules + optional LLM)"]
    end

    subgraph Data["Data Layer"]
        CRM["crm_leads.csv"]
        Email["email_engagement.csv"]
        Calls["call_transcripts.csv"]
        Revenue["revenue_history.csv"]
        KB["product_knowledge_base.json"]
        Model["lead_scoring_model.pkl"]
    end

    Dashboard -->|HTTP/REST| FastAPI
    FastAPI --> M1
    FastAPI --> M2
    FastAPI --> M3
    M1 --> CRM
    M1 --> Email
    M1 --> Model
    M2 --> CRM
    M2 --> KB
    M3 --> Calls
    Dashboard --> CRM
    Dashboard --> Email
    Dashboard --> Revenue
```

## Data Flow by Use Case

### 1. Lead Scoring

```mermaid
sequenceDiagram
    participant User
    participant Dashboard
    participant API
    participant LeadScoring
    participant Data

    User->>Dashboard: View top leads / Score lead
    Dashboard->>API: GET /api/leads/top or POST /api/leads/score
    API->>Data: Read crm_leads + email_engagement
    API->>LeadScoring: predict(leads_df)
    LeadScoring->>Data: Load model (if trained)
    LeadScoring-->>API: conversion_probability, priority_rank
    API-->>Dashboard: JSON response
    Dashboard-->>User: Table + charts
```

### 2. Email Personalization

```mermaid
sequenceDiagram
    participant User
    participant Dashboard
    participant API
    participant EmailEngine
    participant KB

    User->>Dashboard: Select lead, Generate email
    Dashboard->>API: POST /api/emails/generate
    API->>EmailEngine: generate_personalized_email(lead_data)
    EmailEngine->>KB: find_relevant_content(industry, role)
    KB-->>EmailEngine: RAG context
    EmailEngine-->>API: subject, body (template or OpenAI)
    API-->>Dashboard: JSON response
    Dashboard-->>User: Email preview + download
```

### 3. Call Intelligence

```mermaid
sequenceDiagram
    participant User
    participant Dashboard
    participant API
    participant CallAnalyzer
    participant Data

    User->>Dashboard: Analyze call / Risk report
    Dashboard->>API: POST /api/calls/analyze or GET /api/calls/risk-report
    API->>Data: Read call_transcripts
    API->>CallAnalyzer: analyze_call() or analyze_call_batch()
    CallAnalyzer-->>API: summary, sentiment, risk_level, next_steps
    API-->>Dashboard: JSON response
    Dashboard-->>User: Report + recommendations
```

## Component Overview

| Component | Tech | Purpose |
|-----------|------|---------|
| **Streamlit Dashboard** | Streamlit, Plotly | Single UI for overview, lead scoring, email gen, call analysis |
| **FastAPI** | FastAPI, Uvicorn | REST API; serves all three modules |
| **Lead Scoring** | XGBoost, scikit-learn, joblib | Train/predict conversion probability; persist model |
| **Email Personalization** | TF-IDF, optional OpenAI | RAG over product KB; generate personalized emails |
| **Call Intelligence** | Rules + optional OpenAI | Summarize calls, sentiment, risk, objections, next steps |
| **Data** | CSV, JSON | Synthetic CRM, email, calls, revenue; product KB; saved model |

## Optional Integration (OpenAI)

When `OPENAI_API_KEY` is set:

- **Email module:** Uses GPT for higher-quality, contextual email copy (fallback: templates).
- **Call module:** Uses GPT for richer summaries and risk/objection extraction (fallback: rule-based).

No API key is required for lead scoring or for running the full demo.
