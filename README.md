# AI Sales Acceleration Engine

Implementation Plan - Synthetic Data Portfolio Version

## Live Demo

[Open AI Sales Acceleration Engine](https://sales-project-hsevarhth4d4g6ed.centralus-01.azurewebsites.net)


## Project Overview

This project demonstrates a realistic, end-to-end AI Sales Acceleration Engine using synthetic data. It showcases predictive modeling, LLM integration, CRM-style workflows, and measurable ROI simulation.

## Project Structure

```
new-plan/
├── AI_Sales_Acceleration_Engine_Implementation_Plan.pdf
├── phase1_company_profile.json          # Detailed company profile (JSON)
├── phase1_summary.md                    # Human-readable summary
├── generate_synthetic_data.py          # Phase 2: Data generation script
├── data/                                # Generated synthetic data
│   ├── crm_leads.csv
│   ├── email_engagement.csv
│   ├── call_transcripts.csv
│   └── revenue_history.csv
├── modules/                             # Phase 3: Core modules
│   ├── __init__.py
│   ├── lead_scoring.py                  # Module 1: Predictive lead scoring
│   ├── email_personalization.py         # Module 2: AI email personalization
│   └── call_intelligence.py             # Module 3: Call analysis & risk detection
├── api/                                 # Phase 3: FastAPI backend
│   └── main.py                          # REST API server
├── dashboard.py                         # Phase 4: Streamlit dashboard
├── phase5_business_impact_report.md     # Phase 5: Business impact (consulting)
├── phase5_architecture.md               # Phase 5: Architecture (Mermaid)
├── phase5_demo_script.md                # Phase 5: Demo script
├── requirements.txt                     # Python dependencies
├── test_modules.py                      # Module testing script
└── README.md                            # This file
```

## Phase 1: Define Scenario ✅

**Status:** Complete

We've created a fictional B2B SaaS company profile:
- **Company:** CloudFlow Solutions (Project Management SaaS)
- **Team:** 85 employees, 15-person sales team
- **Revenue:** $4.2M ARR, 280 customers
- **CRM:** 5,000 leads with detailed breakdown
- **Baseline Metrics:** Defined current performance before AI implementation
- **Target Metrics:** Set improvement goals for AI implementation

See `phase1_summary.md` for detailed metrics and KPIs.

## Phase 2: Generate Synthetic Data ✅

**Status:** Complete

Generated synthetic datasets:
- **CRM Leads:** 5,000 leads with scores, status, and attributes
- **Email Engagement:** Email opens, clicks, and replies per lead
- **Call Transcripts:** 150+ realistic sales call transcripts
- **Revenue History:** 18 months of MRR and revenue data

Run `python generate_synthetic_data.py` to regenerate data.

## Phase 3: Build Core Modules ✅

**Status:** Complete

### Module 1: Predictive Lead Scoring
- **File:** `modules/lead_scoring.py`
- **Features:** XGBoost model for conversion probability prediction
- **Output:** Conversion probability and priority ranking for each lead
- **Usage:** Train model, then predict scores for leads

### Module 2: AI Outreach Personalization (LLM + RAG)
- **File:** `modules/email_personalization.py`
- **Features:** 
  - Product knowledge base with 10+ entries
  - TF-IDF embeddings for semantic search
  - Personalized email generation (with OpenAI API support)
  - A/B variant generation
- **Usage:** Generate personalized emails based on lead profile and RAG context

### Module 3: Call Intelligence & Risk Detection
- **File:** `modules/call_intelligence.py`
- **Features:**
  - Call transcript analysis
  - Sentiment detection (positive/neutral/negative)
  - Risk level assessment (low/medium/high)
  - Objection detection
  - Recommended next steps
- **Usage:** Analyze calls individually or in batch

### FastAPI Backend
- **File:** `api/main.py`
- **Features:** REST API endpoints for all three modules
- **Endpoints:**
  - `/api/leads/train` - Train lead scoring model
  - `/api/leads/score` - Score leads
  - `/api/leads/top` - Get top priority leads
  - `/api/emails/generate` - Generate personalized email
  - `/api/emails/generate-ab` - Generate A/B variants
  - `/api/calls/analyze` - Analyze call transcript
  - `/api/calls/risk-report` - Get risk analysis report

### Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Test modules:**
   ```bash
   python test_modules.py
   ```

3. **Train lead scoring model:**
   ```python
   from modules.lead_scoring import LeadScoringModel
   model = LeadScoringModel()
   model.train("data/crm_leads.csv", "data/email_engagement.csv")
   ```

4. **Start API server:**
   ```bash
   uvicorn api.main:app --reload
   ```
   Then visit http://localhost:8000/docs for interactive API documentation.

## Phase 4: Build Interface ✅

**Status:** Complete

### Streamlit Dashboard
- **File:** `dashboard.py`
- **Features:**
  - 📊 **Sales Overview:** Key metrics, revenue forecast, email engagement charts
  - 🎯 **Lead Scoring:** Top priority leads, individual lead scoring, model training
  - ✉️ **Email Generator:** AI-powered personalized email generation with A/B variants
  - 📞 **Call Intelligence:** Risk analysis reports, individual call analysis, sentiment detection

### Dashboard Pages

1. **Sales Overview**
   - Total leads, qualified leads, conversion metrics
   - Lead status and source distribution charts
   - Revenue history with AI forecast
   - Email engagement metrics over time

2. **Lead Scoring**
   - Model training interface
   - Top priority leads table with conversion probabilities
   - Individual lead search and scoring
   - Interactive visualizations

3. **Email Generator**
   - Lead selection dropdown
   - AI-powered email generation (variant A/B)
   - Personalization score display
   - Email download functionality

4. **Call Intelligence**
   - Risk analysis dashboard
   - Sentiment and objection tracking
   - Individual call transcript analysis
   - Recommended next steps

### Running the Dashboard

1. **Start the API server** (in one terminal):
   ```bash
   uvicorn api.main:app --reload
   ```

2. **Start the Streamlit dashboard** (in another terminal):
   ```bash
   streamlit run dashboard.py
   ```

3. **Open browser:** The dashboard will automatically open at http://localhost:8501

**Note:** The dashboard works in offline mode (without API) but with limited functionality. For full AI features, keep the API server running.

## Phase 5: Consulting Polish ✅

**Status:** Complete

Deliverables for client handoff and demos:

- **Business Impact Report** — `phase5_business_impact_report.md`  
  Executive summary, baseline vs target metrics, revenue impact, risks, and recommendations.

- **Architecture** — `phase5_architecture.md`  
  High-level and data-flow diagrams (Mermaid), component overview, optional OpenAI integration.

- **Demo Script** — `phase5_demo_script.md`  
  Step-by-step script (~15–20 min) for presenting the dashboard and API; includes pre-demo checklist and troubleshooting.

**Optional:** Add `OPENAI_API_KEY` (env or `.env`) when ready to improve email personalization and call analysis; the project runs fully without it.

## Technology Stack

- **Backend:** FastAPI
- **ML:** Scikit-learn / XGBoost
- **LLM:** OpenAI API
- **Vector Database:** pgvector
- **Frontend:** Streamlit or React
- **Deployment:** Docker + Cloud Platform

