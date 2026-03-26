"""
FastAPI Backend for AI Sales Acceleration Engine
Serves all three core modules via REST API.
"""
import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import pandas as pd
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.lead_scoring import LeadScoringModel
from modules.email_personalization import EmailPersonalizationEngine
from modules.call_intelligence import CallIntelligenceAnalyzer

app = FastAPI(
    title="AI Sales Acceleration Engine API",
    description="API for predictive lead scoring, email personalization, and call intelligence",
    version="1.0.0"
)

# Serve React build output when hosting frontend + backend in one App Service.
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"
FRONTEND_ASSETS = FRONTEND_DIST / "assets"

if FRONTEND_ASSETS.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_ASSETS)), name="assets")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models (lazy loading)
lead_scoring_model = None
email_engine = None
call_analyzer = None


# Pydantic models for request/response
class LeadScoreRequest(BaseModel):
    lead_ids: Optional[List[int]] = None  # If None, score all leads


class LeadScoreResponse(BaseModel):
    lead_id: int
    conversion_probability: float
    priority_rank: int


class EmailGenerationRequest(BaseModel):
    lead_id: int
    variant: Optional[str] = "A"


class ABVariantRequest(BaseModel):
    lead_id: int


class EmailGenerationResponse(BaseModel):
    lead_id: int
    subject: str
    body: str
    variant: str
    personalization_score: float


class CallAnalysisRequest(BaseModel):
    call_id: Optional[int] = None
    transcript: Optional[str] = None


class CallAnalysisResponse(BaseModel):
    call_id: str
    lead_id: int
    summary: str
    objections_detected: List[str]
    sentiment: str
    risk_level: str
    recommended_next_steps: List[str]


class DailySuggestion(BaseModel):
    """Suggestion item for daily AI sales copilot."""
    suggestion_type: str
    lead_id: int
    company: str
    reason: str
    priority: int
    recommended_action: str


class FollowupSimulationRequest(BaseModel):
    """Request body for autonomous follow-up simulation."""
    lead_id: Optional[int] = None
    days: int = 14
    steps: int = 4


class FollowupSimulationStep(BaseModel):
    """Single step in follow-up sequence."""
    step_number: int
    channel: str
    suggested_day_offset: int
    message_focus: str
    expected_open_rate: float
    expected_reply_rate: float


class FollowupSimulationResponse(BaseModel):
    """Response summarizing autonomous follow-up simulation."""
    lead_id: int
    total_days: int
    total_steps: int
    projected_overall_open_rate: float
    projected_overall_reply_rate: float
    projected_conversion_lift: float
    sequence: List[FollowupSimulationStep]


@app.on_event("startup")
async def startup_event():
    """Initialize models on startup."""
    global lead_scoring_model, email_engine, call_analyzer
    
    print("Initializing AI Sales Acceleration Engine...")
    
    # Initialize lead scoring model (will load if trained)
    lead_scoring_model = LeadScoringModel()
    
    # Initialize email personalization engine
    email_engine = EmailPersonalizationEngine()
    
    # Initialize call analyzer
    call_analyzer = CallIntelligenceAnalyzer()
    
    print("All modules initialized successfully!")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Sales Acceleration Engine API",
        "version": "1.0.0",
        "endpoints": {
            "lead_scoring": "/api/leads/score",
            "email_generation": "/api/emails/generate",
            "call_analysis": "/api/calls/analyze"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "modules_loaded": True}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Serve React/Vite favicon if present."""
    favicon_path = FRONTEND_DIST / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(str(favicon_path))
    raise HTTPException(status_code=404, detail="Not found")


# ==================== Data Access Endpoints ====================

@app.get("/api/data/leads", tags=["Data"])
async def get_leads(limit: int = Query(5000, ge=1, le=10000)):
    """Return CRM leads for dashboard/frontend consumption."""
    try:
        leads_df = pd.read_csv("data/crm_leads.csv").head(limit)
        return leads_df.to_dict("records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/data/email-engagement", tags=["Data"])
async def get_email_engagement(limit: int = Query(50000, ge=1, le=200000)):
    """Return email engagement events."""
    try:
        email_df = pd.read_csv("data/email_engagement.csv").head(limit)
        return email_df.to_dict("records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/data/call-transcripts", tags=["Data"])
async def get_call_transcripts(limit: int = Query(5000, ge=1, le=50000)):
    """Return call transcripts and metadata."""
    try:
        calls_df = pd.read_csv("data/call_transcripts.csv").head(limit)
        return calls_df.to_dict("records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/data/revenue-history", tags=["Data"])
async def get_revenue_history(limit: int = Query(120, ge=1, le=500)):
    """Return revenue history for charts/forecast."""
    try:
        revenue_df = pd.read_csv("data/revenue_history.csv").head(limit)
        return revenue_df.to_dict("records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Lead Scoring Endpoints ====================

@app.post("/api/leads/train", tags=["Lead Scoring"])
async def train_lead_scoring_model():
    """Train the lead scoring model."""
    try:
        global lead_scoring_model
        if lead_scoring_model is None:
            lead_scoring_model = LeadScoringModel()
        
        lead_scoring_model.train(
            crm_path="data/crm_leads.csv",
            email_path="data/email_engagement.csv"
        )
        
        return {"message": "Model trained successfully", "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/leads/score", response_model=List[LeadScoreResponse], tags=["Lead Scoring"])
async def score_leads(request: LeadScoreRequest):
    """Score leads and return conversion probabilities."""
    try:
        global lead_scoring_model
        if lead_scoring_model is None:
            lead_scoring_model = LeadScoringModel()
        
        # Use the model's own loader on the full dataset to match training
        leads_df = lead_scoring_model.load_data(
            crm_path="data/crm_leads.csv",
            email_path="data/email_engagement.csv",
        )
        # Score all leads first (more stable with scaler/model expectations)
        scores_all = lead_scoring_model.predict(leads_df)

        # If specific lead_ids were requested, filter scores down to just those
        if request.lead_ids:
            scores = scores_all[scores_all["lead_id"].isin(request.lead_ids)]
        else:
            scores = scores_all
        
        # Convert to response format
        results = [
            LeadScoreResponse(
                lead_id=int(row['lead_id']),
                conversion_probability=float(row['conversion_probability']),
                priority_rank=int(row['priority_rank'])
            )
            for _, row in scores.iterrows()
        ]
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/leads/top", tags=["Lead Scoring"])
async def get_top_leads(limit: int = Query(10, ge=1, le=100)):
    """Get top priority leads."""
    try:
        global lead_scoring_model
        if lead_scoring_model is None:
            lead_scoring_model = LeadScoringModel()
        
        # Load and score all leads
        leads_df = pd.read_csv("data/crm_leads.csv")
        email_df = pd.read_csv("data/email_engagement.csv")
        
        email_metrics = email_df.groupby('lead_id').agg({
            'opened': 'sum',
            'clicked': 'sum',
            'replied': 'sum',
            'email_sequence_step': 'max'
        }).reset_index()
        email_metrics.columns = ['lead_id', 'total_opens', 'total_clicks', 'total_replies', 'max_sequence_step']
        # Reset index before merge to avoid index mismatch
        leads_df = leads_df.reset_index(drop=True)
        leads_df = leads_df.merge(email_metrics, on='lead_id', how='left')
        
        scores = lead_scoring_model.predict(leads_df)
        
        # Merge with lead details
        top_leads = leads_df.merge(scores, on='lead_id').sort_values(
            'conversion_probability', ascending=False
        ).head(limit)
        
        return top_leads[['lead_id', 'company', 'first_name', 'last_name', 'status', 
                          'conversion_probability', 'priority_rank']].to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Email Personalization Endpoints ====================

@app.post("/api/emails/generate", response_model=EmailGenerationResponse, tags=["Email Personalization"])
async def generate_email(request: EmailGenerationRequest):
    """Generate personalized email for a lead."""
    try:
        global email_engine
        if email_engine is None:
            email_engine = EmailPersonalizationEngine()
        
        # Load lead data
        leads_df = pd.read_csv("data/crm_leads.csv")
        lead_data = leads_df[leads_df['lead_id'] == request.lead_id].iloc[0].to_dict()
        
        if lead_data is None:
            raise HTTPException(status_code=404, detail=f"Lead {request.lead_id} not found")
        
        # Generate email
        email = email_engine.generate_personalized_email(lead_data, variant=request.variant)
        
        return EmailGenerationResponse(
            lead_id=request.lead_id,
            subject=email['subject'],
            body=email['body'],
            variant=email['variant'],
            personalization_score=email['personalization_score']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/emails/generate-ab", tags=["Email Personalization"])
async def generate_ab_variants(request: ABVariantRequest):
    """Generate A/B test variants for a lead."""
    try:
        global email_engine
        if email_engine is None:
            email_engine = EmailPersonalizationEngine()
        
        # Load lead data
        leads_df = pd.read_csv("data/crm_leads.csv")
        lead_match = leads_df[leads_df['lead_id'] == request.lead_id]
        if len(lead_match) == 0:
            raise HTTPException(status_code=404, detail=f"Lead {request.lead_id} not found")
        lead_data = lead_match.iloc[0].to_dict()
        
        # Generate variants
        variants = email_engine.generate_ab_variants(lead_data)
        
        return variants
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Call Intelligence Endpoints ====================

@app.post("/api/calls/analyze", response_model=CallAnalysisResponse, tags=["Call Intelligence"])
async def analyze_call(request: CallAnalysisRequest):
    """Analyze a call transcript."""
    try:
        global call_analyzer
        if call_analyzer is None:
            call_analyzer = CallIntelligenceAnalyzer()
        
        if request.call_id:
            # Load call from database
            calls_df = pd.read_csv("data/call_transcripts.csv")
            call_data = calls_df[calls_df['call_id'] == f"CALL-{request.call_id}"].iloc[0].to_dict()
        elif request.transcript:
            # Use provided transcript
            call_data = {
                'call_id': 'CALL-CUSTOM',
                'lead_id': 0,
                'transcript': request.transcript,
                'duration_minutes': 0
            }
        else:
            raise HTTPException(status_code=400, detail="Either call_id or transcript must be provided")
        
        # Analyze call
        analysis = call_analyzer.analyze_call(call_data)
        
        return CallAnalysisResponse(
            call_id=analysis['call_id'],
            lead_id=int(analysis['lead_id']),
            summary=analysis['summary'],
            objections_detected=analysis['objections_detected'] if isinstance(analysis['objections_detected'], list) else [analysis['objections_detected']],
            sentiment=analysis['sentiment'],
            risk_level=analysis['risk_level'],
            recommended_next_steps=analysis['recommended_next_steps']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/calls/risk-report", tags=["Call Intelligence"])
async def get_risk_report(limit: int = Query(100, ge=1, le=1000)):
    """Get risk analysis report for recent calls."""
    try:
        global call_analyzer
        if call_analyzer is None:
            call_analyzer = CallIntelligenceAnalyzer()
        
        # Load calls
        calls_df = pd.read_csv("data/call_transcripts.csv").head(limit)
        
        # Analyze calls
        analyzed_calls = call_analyzer.analyze_call_batch(calls_df)
        
        # Check if risk_level column exists (in case merge failed)
        if 'risk_level' not in analyzed_calls.columns:
            # If merge failed, use the results_df directly
            # Extract just the analysis results
            analysis_cols = ['call_id', 'lead_id', 'summary', 'objections_detected', 
                           'sentiment', 'risk_level', 'recommended_next_steps']
            available_cols = [col for col in analysis_cols if col in analyzed_calls.columns]
            analyzed_calls = analyzed_calls[available_cols].copy()
            # Fill missing risk_level with default
            if 'risk_level' not in analyzed_calls.columns:
                analyzed_calls['risk_level'] = 'medium'
        
        # Generate report
        risk_report = call_analyzer.generate_risk_report(analyzed_calls)
        
        return risk_report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== AI Sales Copilot Endpoints ====================

@app.get("/api/copilot/daily-suggestions", response_model=List[DailySuggestion], tags=["AI Copilot"])
async def get_daily_suggestions(limit: int = Query(10, ge=1, le=50)):
    """
    Generate daily AI sales copilot suggestions.

    Heuristics (no external API required):
    - High-scoring leads with no email in last 7 days -> "outreach" suggestion
    - Leads with multiple opens but no reply -> "follow-up" suggestion
    - Leads with high-risk calls in last 14 days -> "risk-mitigation" suggestion
    """
    try:
        leads_df = pd.read_csv("data/crm_leads.csv")
        email_df = pd.read_csv("data/email_engagement.csv")
        calls_df = pd.read_csv("data/call_transcripts.csv")

        # Prepare email recency metrics
        email_df["sent_at"] = pd.to_datetime(email_df["sent_at"])
        email_metrics = (
            email_df.groupby("lead_id")
            .agg(
                last_email_at=("sent_at", "max"),
                total_emails=("email_sequence_step", "count"),
                total_opens=("opened", "sum"),
                total_replies=("replied", "sum"),
            )
            .reset_index()
        )

        # Prepare call risk metrics
        calls_df["call_date"] = pd.to_datetime(calls_df["call_date"])
        recent_cutoff = pd.Timestamp.now() - pd.Timedelta(days=14)
        recent_calls = calls_df[calls_df["call_date"] >= recent_cutoff]
        call_risks = (
            recent_calls.groupby("lead_id")
            .agg(
                high_risk_calls=("risk_level", lambda s: (s == "high").sum()),
                medium_risk_calls=("risk_level", lambda s: (s == "medium").sum()),
            )
            .reset_index()
        )

        # Merge into leads
        leads = (
            leads_df.merge(email_metrics, on="lead_id", how="left")
            .merge(call_risks, on="lead_id", how="left")
        )

        leads["high_risk_calls"] = leads["high_risk_calls"].fillna(0)
        leads["medium_risk_calls"] = leads["medium_risk_calls"].fillna(0)
        leads["total_emails"] = leads["total_emails"].fillna(0)
        leads["total_opens"] = leads["total_opens"].fillna(0)
        leads["total_replies"] = leads["total_replies"].fillna(0)

        now = pd.Timestamp.now()
        leads["days_since_last_email"] = (now - leads["last_email_at"]).dt.days.replace({pd.NaT: 999})

        suggestions: List[DailySuggestion] = []

        # 1) Outreach suggestions: strong leads without recent emails
        outreach_candidates = leads[
            (leads["lead_score_baseline"] >= 70)
            & (leads["days_since_last_email"] >= 7)
            & (leads["status"].isin(["New", "Contacted", "Qualified"]))
        ].copy()
        outreach_candidates["priority"] = 1
        for _, row in outreach_candidates.head(limit).iterrows():
            suggestions.append(
                DailySuggestion(
                    suggestion_type="outreach",
                    lead_id=int(row["lead_id"]),
                    company=str(row["company"]),
                    reason=f"High baseline score ({row['lead_score_baseline']:.1f}) with no email in last {int(row['days_since_last_email'])} days.",
                    priority=1,
                    recommended_action="Send a personalized intro email referencing their industry and role.",
                )
            )

        # 2) Follow-up suggestions: engaged but no reply
        followup_candidates = leads[
            (leads["total_opens"] >= 3)
            & (leads["total_replies"] == 0)
            & (leads["status"].isin(["Contacted", "Qualified", "Demo Scheduled", "Proposal Sent"]))
        ].copy()
        followup_candidates["priority"] = 2
        for _, row in followup_candidates.head(limit - len(suggestions)).iterrows():
            suggestions.append(
                DailySuggestion(
                    suggestion_type="follow-up",
                    lead_id=int(row["lead_id"]),
                    company=str(row["company"]),
                    reason=f"{int(row['total_opens'])} opens and 0 replies across {int(row['total_emails'])} emails.",
                    priority=2,
                    recommended_action="Send a concise follow-up with a single clear CTA (e.g., 15-min discovery call).",
                )
            )

        # 3) Risk-mitigation suggestions: recent high/medium risk calls
        risk_candidates = leads[
            (leads["high_risk_calls"] + leads["medium_risk_calls"] > 0)
            & (leads["status"].isin(["Proposal Sent", "Negotiation"]))
        ].copy()
        risk_candidates["priority"] = 3
        for _, row in risk_candidates.head(max(0, limit - len(suggestions))).iterrows():
            risk_count = int(row["high_risk_calls"] + row["medium_risk_calls"])
            suggestions.append(
                DailySuggestion(
                    suggestion_type="risk-mitigation",
                    lead_id=int(row["lead_id"]),
                    company=str(row["company"]),
                    reason=f"{risk_count} recent medium/high-risk calls detected.",
                    priority=3,
                    recommended_action="Send a value-focused follow-up addressing key objections and next steps.",
                )
            )

        # Sort by priority and baseline score
        leads_score_map = leads.set_index("lead_id")["lead_score_baseline"].to_dict()
        suggestions_sorted = sorted(
            suggestions,
            key=lambda s: (s.priority, -leads_score_map.get(s.lead_id, 0)),
        )

        return suggestions_sorted[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/api/copilot/simulate-followup",
    response_model=FollowupSimulationResponse,
    tags=["AI Copilot"],
)
async def simulate_followup(request: FollowupSimulationRequest):
    """
    Simulate an autonomous follow-up sequence for a given lead.

    Uses simple heuristics based on baseline score and current status to estimate:
    - Per-step open / reply rates
    - Overall expected engagement
    - Approximate conversion lift vs. baseline
    """
    try:
        leads_df = pd.read_csv("data/crm_leads.csv")

        # Pick lead
        if request.lead_id:
            lead_match = leads_df[leads_df["lead_id"] == request.lead_id]
            if len(lead_match) == 0:
                raise HTTPException(status_code=404, detail=f"Lead {request.lead_id} not found")
            lead = lead_match.iloc[0]
        else:
            # Default: pick a high-scoring open lead
            open_mask = ~leads_df["status"].isin(["Closed Won", "Closed Lost"])
            lead = leads_df[open_mask].sort_values("lead_score_baseline", ascending=False).iloc[0]

        lead_id = int(lead["lead_id"])
        baseline_score = float(lead["lead_score_baseline"])
        status = str(lead["status"])

        # Base engagement factors
        base_open = 0.18 + (baseline_score / 1000.0)  # 18%–28%
        base_reply = 0.02 + (baseline_score / 4000.0)  # ~2%–4.5%

        if status in ["Demo Scheduled", "Proposal Sent", "Negotiation"]:
            base_open += 0.05
            base_reply += 0.015

        steps = max(1, min(request.steps, 8))
        total_days = max(7, min(request.days, 30))
        day_gap = max(2, total_days // max(steps, 1))

        sequence: List[FollowupSimulationStep] = []
        cumulative_open = 0.0
        cumulative_reply = 0.0

        channel_pattern = ["Email", "Email", "Call + Email", "Email + Content"]
        focus_pattern = [
            "Intro + pain discovery",
            "ROI story + social proof",
            "Objection handling + live call",
            "Urgency + next steps",
        ]

        for i in range(steps):
            step_num = i + 1
            suggested_day = min(total_days, step_num * day_gap)

            # Slight decay over time
            decay_factor = 1 - (i * 0.08)
            step_open = max(0.05, base_open * decay_factor)
            step_reply = max(0.01, base_reply * decay_factor)

            cumulative_open = 1 - (1 - cumulative_open) * (1 - step_open)
            cumulative_reply = 1 - (1 - cumulative_reply) * (1 - step_reply)

            sequence.append(
                FollowupSimulationStep(
                    step_number=step_num,
                    channel=channel_pattern[i % len(channel_pattern)],
                    suggested_day_offset=int(suggested_day),
                    message_focus=focus_pattern[i % len(focus_pattern)],
                    expected_open_rate=float(step_open),
                    expected_reply_rate=float(step_reply),
                )
            )

        # Simple heuristic for conversion lift vs. baseline behaviour
        projected_conversion_lift = min(0.25, cumulative_reply * 3.0)

        return FollowupSimulationResponse(
            lead_id=lead_id,
            total_days=total_days,
            total_steps=steps,
            projected_overall_open_rate=float(cumulative_open),
            projected_overall_reply_rate=float(cumulative_reply),
            projected_conversion_lift=float(projected_conversion_lift),
            sequence=sequence,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/{full_path:path}", include_in_schema=False)
async def spa_fallback(full_path: str):
    """
    Serve SPA index for non-API routes so direct URL refresh works.
    Keep API paths unresolved here.
    """
    if full_path.startswith("api"):
        raise HTTPException(status_code=404, detail="Not found")

    index_path = FRONTEND_DIST / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    raise HTTPException(status_code=404, detail="Frontend build not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

