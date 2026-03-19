import os
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker


fake = Faker()
random.seed(42)
np.random.seed(42)


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)


def generate_crm_leads(n_leads: int = 5000) -> pd.DataFrame:
    """Generate synthetic CRM lead data."""
    industries = [
        "Technology",
        "Professional Services",
        "Marketing Agency",
        "Consulting",
        "Manufacturing",
        "Healthcare",
    ]
    lead_sources = [
        "Website Form",
        "Content Download",
        "Webinar",
        "Referral",
        "Trade Show",
        "Cold Outreach",
    ]
    statuses = [
        "New",
        "Contacted",
        "Qualified",
        "Demo Scheduled",
        "Proposal Sent",
        "Negotiation",
        "Closed Won",
        "Closed Lost",
    ]

    leads = []
    start_date = datetime.today() - timedelta(days=365)

    for lead_id in range(1, n_leads + 1):
        created_at = start_date + timedelta(
            days=random.randint(0, 365),
            seconds=random.randint(0, 86400),
        )
        source = random.choices(
            lead_sources,
            weights=[0.36, 0.24, 0.16, 0.12, 0.08, 0.04],
            k=1,
        )[0]
        status = random.choices(
            statuses,
            weights=[0.24, 0.32, 0.18, 0.09, 0.07, 0.04, 0.02, 0.04],
            k=1,
        )[0]
        company_size = random.choice(["50-100", "101-250", "251-500"])

        # Simulated score and conversion label (for later modeling)
        lead_score = np.clip(
            np.random.normal(loc=60, scale=15), 0, 100
        )  # baseline, AI will improve later
        converted = int(status == "Closed Won")

        leads.append(
            {
                "lead_id": lead_id,
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "email": fake.email(),
                "company": fake.company(),
                "job_title": random.choice(
                    [
                        "Head of Operations",
                        "VP Engineering",
                        "CTO",
                        "Director of IT",
                        "Project Manager",
                        "COO",
                    ]
                ),
                "industry": random.choice(industries),
                "company_size_bucket": company_size,
                "country": fake.country(),
                "lead_source": source,
                "status": status,
                "created_at": created_at,
                "lead_score_baseline": round(float(lead_score), 1),
                "converted": converted,
                "estimated_deal_size": random.choice(
                    [10000, 12000, 15000, 18000, 20000]
                ),
            }
        )

    df = pd.DataFrame(leads)
    df.sort_values("created_at", inplace=True)
    return df


def generate_email_engagement(leads: pd.DataFrame, emails_per_lead_range=(1, 10)) -> pd.DataFrame:
    """Generate synthetic email engagement events linked to leads."""
    records = []
    for _, lead in leads.iterrows():
        n_emails = random.randint(*emails_per_lead_range)
        for i in range(n_emails):
            sent_at = lead["created_at"] + timedelta(
                days=random.randint(0, 60),
                seconds=random.randint(0, 86400),
            )

            # Baseline engagement probabilities
            open_prob = 0.22
            click_prob = 0.035
            reply_prob = 0.021

            opened = int(random.random() < open_prob)
            clicked = int(opened and random.random() < click_prob)
            replied = int(opened and random.random() < reply_prob)

            records.append(
                {
                    "lead_id": lead["lead_id"],
                    "email_sequence_step": i + 1,
                    "subject_line": f"{lead['company']} - Improving project delivery with CloudFlow",
                    "sent_at": sent_at,
                    "opened": opened,
                    "clicked": clicked,
                    "replied": replied,
                }
            )

    return pd.DataFrame(records)


def generate_call_transcripts(
    leads: pd.DataFrame,
    n_calls: int = 150,
) -> pd.DataFrame:
    """Generate lightweight synthetic call transcripts with sentiment and risk labels."""
    objection_templates = [
        "We don't have budget for this right now.",
        "We're already using another project management tool.",
        "Security and compliance are a major concern for us.",
        "Implementation time is a big risk for our team.",
        "We need to see stronger ROI before moving forward.",
    ]

    positive_outcomes = [
        "Booked follow-up demo with the technical team.",
        "Verbal commitment to pilot in one department.",
        "Customer asked for a proposal and pricing breakdown.",
    ]

    neutral_outcomes = [
        "Sent product overview and case studies.",
        "Prospect will evaluate internally and get back.",
        "Added prospect to nurture sequence.",
    ]

    negative_outcomes = [
        "Prospect decided to postpone project to next year.",
        "Prospect chose a competitor due to existing relationship.",
    ]

    sentiments = ["positive", "neutral", "negative"]
    risks = ["low", "medium", "high"]

    sampled_leads = leads.sample(min(n_calls, len(leads)), random_state=42)
    records = []

    for _, lead in sampled_leads.iterrows():
        call_date = lead["created_at"] + timedelta(
            days=random.randint(1, 45),
            seconds=random.randint(0, 86400),
        )

        sentiment = random.choices(sentiments, weights=[0.45, 0.35, 0.20], k=1)[0]
        risk_level = random.choices(risks, weights=[0.4, 0.4, 0.2], k=1)[0]

        # Build a simple synthetic transcript text
        objection = random.choice(objection_templates)
        if sentiment == "positive":
            outcome = random.choice(positive_outcomes)
        elif sentiment == "neutral":
            outcome = random.choice(neutral_outcomes)
        else:
            outcome = random.choice(negative_outcomes)

        transcript = (
            f"AE: Thanks for taking the time today. I'd love to understand how your team manages projects.\n"
            f"{lead['first_name']}: We currently use a mix of spreadsheets and another tool, but it's not ideal.\n"
            f"AE: Many of our customers felt the same before switching to CloudFlow.\n"
            f"{lead['first_name']}: {objection}\n"
            f"AE: I understand. Here's how we typically address that concern...\n"
            f"NARRATOR: The call ended with the following outcome: {outcome}"
        )

        records.append(
            {
                "call_id": f"CALL-{lead['lead_id']}",
                "lead_id": lead["lead_id"],
                "call_date": call_date,
                "duration_minutes": random.randint(20, 45),
                "transcript": transcript,
                "primary_objection": objection,
                "sentiment": sentiment,
                "risk_level": risk_level,
                "next_step_summary": outcome,
            }
        )

    return pd.DataFrame(records)


def generate_revenue_history(
    months: int = 18,
    base_mrr: float = 350_000.0,
    growth_rate_annual: float = 0.35,
) -> pd.DataFrame:
    """Generate 12–24 months of synthetic revenue history with trend + noise."""
    today = datetime.today()
    start_month = today.replace(day=1) - timedelta(days=30 * (months - 1))

    monthly_growth = (1 + growth_rate_annual) ** (1 / 12) - 1

    records = []
    mrr = base_mrr

    for i in range(months):
        month_start = start_month + timedelta(days=30 * i)

        # Apply growth plus some random variation
        mrr *= 1 + monthly_growth
        mrr_with_noise = mrr * np.random.normal(loc=1.0, scale=0.03)

        new_mrr = mrr_with_noise * np.random.uniform(0.25, 0.35)
        churn_mrr = mrr_with_noise * np.random.uniform(0.02, 0.04)

        records.append(
            {
                "month": month_start.strftime("%Y-%m"),
                "mrr": round(float(mrr_with_noise), 2),
                "new_mrr": round(float(new_mrr), 2),
                "churn_mrr": round(float(churn_mrr), 2),
                "net_new_mrr": round(float(new_mrr - churn_mrr), 2),
            }
        )

    return pd.DataFrame(records)


def main():
    # CRM Leads
    leads_df = generate_crm_leads(n_leads=5000)
    leads_path = os.path.join(DATA_DIR, "crm_leads.csv")
    leads_df.to_csv(leads_path, index=False)

    # Email Engagement
    email_df = generate_email_engagement(leads_df)
    email_path = os.path.join(DATA_DIR, "email_engagement.csv")
    email_df.to_csv(email_path, index=False)

    # Call Transcripts
    calls_df = generate_call_transcripts(leads_df, n_calls=150)
    calls_path = os.path.join(DATA_DIR, "call_transcripts.csv")
    calls_df.to_csv(calls_path, index=False)

    # Revenue History
    revenue_df = generate_revenue_history(months=18)
    revenue_path = os.path.join(DATA_DIR, "revenue_history.csv")
    revenue_df.to_csv(revenue_path, index=False)

    print("Synthetic data generated:")
    print(f"- CRM leads: {leads_path} ({len(leads_df)} rows)")
    print(f"- Email engagement: {email_path} ({len(email_df)} rows)")
    print(f"- Call transcripts: {calls_path} ({len(calls_df)} rows)")
    print(f"- Revenue history: {revenue_path} ({len(revenue_df)} rows)")


if __name__ == "__main__":
    main()


