"""
Test script for Phase 3 modules
Run this to verify all modules are working correctly.
"""

import os
import sys

print("=" * 60)
print("Testing AI Sales Acceleration Engine - Phase 3 Modules")
print("=" * 60)

# Test Module 1: Lead Scoring
print("\n[1/3] Testing Lead Scoring Module...")
try:
    from modules.lead_scoring import LeadScoringModel
    
    model = LeadScoringModel()
    print("✓ LeadScoringModel imported successfully")
    
    # Check if data files exist
    if os.path.exists("data/crm_leads.csv") and os.path.exists("data/email_engagement.csv"):
        print("✓ Data files found")
        
        # Try to load data
        leads = model.load_data("data/crm_leads.csv", "data/email_engagement.csv")
        print(f"✓ Data loaded: {len(leads)} leads")
        
        # Try feature engineering
        features = model.engineer_features(leads.head(100))
        print(f"✓ Feature engineering successful: {len(features.columns)} features")
    else:
        print("⚠ Data files not found. Please run generate_synthetic_data.py first.")
    
except Exception as e:
    print(f"✗ Error: {e}")

# Test Module 2: Email Personalization
print("\n[2/3] Testing Email Personalization Module...")
try:
    from modules.email_personalization import EmailPersonalizationEngine
    
    engine = EmailPersonalizationEngine()
    print("✓ EmailPersonalizationEngine imported successfully")
    
    # Test knowledge base
    engine.kb.load_knowledge_base()
    print(f"✓ Knowledge base loaded: {len(engine.kb.knowledge_base)} entries")
    
    # Test embedding creation
    engine.kb.create_embeddings()
    print("✓ Embeddings created successfully")
    
    # Test email generation
    sample_lead = {
        'lead_id': 123,
        'first_name': 'John',
        'last_name': 'Smith',
        'company': 'TechCorp Inc',
        'job_title': 'Director of IT',
        'industry': 'Technology',
        'company_size_bucket': '101-250'
    }
    
    email = engine.generate_personalized_email(sample_lead)
    print(f"✓ Email generated: {len(email['body'])} characters")
    print(f"  Subject: {email['subject'][:50]}...")
    
except Exception as e:
    print(f"✗ Error: {e}")

# Test Module 3: Call Intelligence
print("\n[3/3] Testing Call Intelligence Module...")
try:
    from modules.call_intelligence import CallIntelligenceAnalyzer
    
    analyzer = CallIntelligenceAnalyzer()
    print("✓ CallIntelligenceAnalyzer imported successfully")
    
    # Test call analysis
    sample_call = {
        'call_id': 'CALL-TEST',
        'lead_id': 123,
        'transcript': "AE: Thanks for your time. Prospect: We're interested but need to see ROI. AE: I understand. Let me show you our case studies.",
        'duration_minutes': 30
    }
    
    analysis = analyzer.analyze_call(sample_call)
    print(f"✓ Call analysis successful")
    print(f"  Sentiment: {analysis['sentiment']}")
    print(f"  Risk Level: {analysis['risk_level']}")
    print(f"  Objections: {analysis['objections_detected']}")
    
except Exception as e:
    print(f"✗ Error: {e}")

# Test API
print("\n[Bonus] Testing FastAPI Backend...")
try:
    from api.main import app
    print("✓ FastAPI app imported successfully")
    print("✓ API endpoints available")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 60)
print("Testing Complete!")
print("=" * 60)
print("\nNext steps:")
print("1. Train the lead scoring model: python -c 'from modules.lead_scoring import LeadScoringModel; m = LeadScoringModel(); m.train(\"data/crm_leads.csv\", \"data/email_engagement.csv\")'")
print("2. Start the API server: uvicorn api.main:app --reload")
print("3. Visit http://localhost:8000/docs for API documentation")

