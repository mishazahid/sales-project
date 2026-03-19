# AI Sales Acceleration Engine — Demo Script

Use this script to present the solution in ~15–20 minutes. Ensure the API and dashboard are running before you start.

---

## Pre-Demo Checklist

- [ ] Data generated: `python generate_synthetic_data.py`
- [ ] Lead scoring model trained (via dashboard or API)
- [ ] Terminal 1: `uvicorn api.main:app --reload` (API on http://localhost:8000)
- [ ] Terminal 2: `streamlit run dashboard.py` (Dashboard on http://localhost:8501)
- [ ] Optional: Set `OPENAI_API_KEY` for enhanced email/call analysis

---

## Demo Flow

### 1. Intro (1–2 min)

- **Message:** “We’re going to walk through an AI Sales Acceleration Engine built for a B2B SaaS sales team.”
- **Show:** Open the Streamlit dashboard (http://localhost:8501).
- **Say:** “Everything you see runs on synthetic data so we can demo without touching real CRM or PII.”

---

### 2. Sales Overview (2–3 min)

- **Navigate:** Sales Overview (first page).
- **Show:** Total leads, qualified leads, conversion rate, lead status pie chart, leads by source.
- **Say:** “This is the baseline picture: 5,000 leads, mix of statuses and sources.”
- **Show:** Revenue history + forecast chart, email engagement over time.
- **Say:** “We have 18 months of synthetic MRR and a simple forecast; the engine will help improve conversion and productivity so this curve can shift up.”

---

### 3. Lead Scoring (4–5 min)

- **Navigate:** Lead Scoring.
- **Say:** “Today, prioritization is often manual and inconsistent. We replace that with a predictive model.”
- **Show:** “Model Training” expander → click **Train Model** (if not already trained). Briefly explain: “Model uses CRM + email engagement to predict conversion probability.”
- **Show:** Set “Number of leads” to 20 → click **Refresh Lead Scores**.
- **Say:** “These are the top 20 leads by conversion probability. Reps can focus here first.”
- **Show:** Bar chart of top 10 leads.
- **Show:** Search & Score — pick one lead, click **Get AI Score**.
- **Say:** “We can score a single lead on demand; same logic can power lead lists and round-robins in a real CRM.”

---

### 4. Email Personalization (4–5 min)

- **Navigate:** Email Generator.
- **Say:** “Generic emails get low reply rates. We personalize using the lead’s company, industry, and role plus our product knowledge base.”
- **Select:** Any lead from the dropdown.
- **Click:** Generate Personalized Email (Variant A).
- **Show:** Subject, body, personalization score.
- **Say:** “Copy is tailored to their profile; with an optional API key we can use an LLM for even stronger copy.”
- **Click:** Generate A/B Variants.
- **Show:** Variant A vs B side by side.
- **Say:** “Teams can run A/B tests on subject lines and messaging.”

---

### 5. Call Intelligence (4–5 min)

- **Navigate:** Call Intelligence.
- **Say:** “Calls often get summarized by hand and risks are spotted too late. We analyze transcripts automatically.”
- **Show:** Set “Number of calls to analyze” (e.g. 50) → click **Generate Risk Report**.
- **Show:** Risk distribution, sentiment distribution, top objections, high-risk call count.
- **Say:** “Managers get an aggregate view of pipeline risk and common objections.”
- **Show:** “Analyze Individual Call” — select a call, click **Analyze Call with AI**.
- **Show:** Summary, sentiment, risk level, objections, recommended next steps.
- **Say:** “Reps get consistent, actionable follow-up suggestions without spending 10 minutes per call on notes.”

---

### 6. Wrap-Up (1–2 min)

- **Say:** “We’ve shown three pillars: **better prioritization** (lead scoring), **better outreach** (personalized email), and **better follow-up** (call intelligence). All of this runs without an API key; adding one improves email and call analysis.”
- **Optional:** Open http://localhost:8000/docs and show the API endpoints.
- **Say:** “The same API can power a custom CRM tab, Slack bot, or scheduled reports. The business impact report and architecture doc are in the repo for next steps and rollout.”

---

## Quick Commands Reference

| Action | Command |
|--------|--------|
| Generate data | `python generate_synthetic_data.py` |
| Start API | `uvicorn api.main:app --reload` |
| Start dashboard | `streamlit run dashboard.py` |
| API docs | http://localhost:8000/docs |
| Dashboard | http://localhost:8501 |

---

## If Something Fails

- **Dashboard says “API not connected”**  
  Start the API in a separate terminal and refresh the dashboard.

- **Lead scoring returns errors**  
  Train the model first (Lead Scoring → Train Model).

- **Email/Call analysis is “template” or “rule-based”**  
  Expected without an API key; optional OpenAI key improves quality.

- **No data / missing CSVs**  
  Run `python generate_synthetic_data.py` from the project root.
