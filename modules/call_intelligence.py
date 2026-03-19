"""
Module 3: Call Intelligence & Risk Detection
Analyzes sales call transcripts to extract summaries, objections, sentiment, and risk levels.
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Tuple
from datetime import datetime
import openai
from openai import OpenAI
import os


class CallIntelligenceAnalyzer:
    """Analyzes sales call transcripts for insights, sentiment, and risk detection."""
    
    def __init__(self, openai_api_key: str = None):
        # Initialize OpenAI client if API key provided
        self.client = None
        if openai_api_key:
            self.client = OpenAI(api_key=openai_api_key)
        elif os.getenv('OPENAI_API_KEY'):
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def analyze_call(self, call_data: Dict) -> Dict:
        """Analyze a single call transcript and extract insights."""
        transcript = call_data.get('transcript', '')
        call_id = call_data.get('call_id', '')
        lead_id = call_data.get('lead_id', '')
        duration = call_data.get('duration_minutes', 0)
        
        # Extract basic information
        analysis = {
            'call_id': call_id,
            'lead_id': lead_id,
            'duration_minutes': duration,
            'analyzed_at': datetime.now().isoformat()
        }
        
        # Use OpenAI for advanced analysis if available
        if self.client:
            ai_analysis = self._analyze_with_openai(transcript)
            analysis.update(ai_analysis)
        else:
            # Use rule-based analysis (fallback)
            analysis.update(self._analyze_with_rules(transcript))
        
        return analysis
    
    def _analyze_with_openai(self, transcript: str) -> Dict:
        """Analyze call using OpenAI API."""
        prompt = f"""Analyze the following sales call transcript and extract:

1. A brief summary (2-3 sentences)
2. Primary objections mentioned (list)
3. Overall sentiment (positive, neutral, or negative)
4. Risk level (low, medium, or high) - based on likelihood of deal closing
5. Recommended next steps (2-3 actionable items)

Call Transcript:
{transcript}

Provide your analysis in the following JSON format:
{{
    "summary": "brief summary",
    "objections": ["objection1", "objection2"],
    "sentiment": "positive/neutral/negative",
    "risk_level": "low/medium/high",
    "next_steps": ["step1", "step2", "step3"]
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert sales call analyst. Extract key insights from sales conversations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            import json
            analysis_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON from response
            try:
                # Extract JSON if wrapped in markdown code blocks
                if '```json' in analysis_text:
                    analysis_text = analysis_text.split('```json')[1].split('```')[0].strip()
                elif '```' in analysis_text:
                    analysis_text = analysis_text.split('```')[1].split('```')[0].strip()
                
                analysis_dict = json.loads(analysis_text)
                return {
                    'summary': analysis_dict.get('summary', ''),
                    'objections_detected': analysis_dict.get('objections', []),
                    'sentiment': analysis_dict.get('sentiment', 'neutral'),
                    'risk_level': analysis_dict.get('risk_level', 'medium'),
                    'recommended_next_steps': analysis_dict.get('next_steps', [])
                }
            except json.JSONDecodeError:
                # Fallback to rule-based if JSON parsing fails
                return self._analyze_with_rules(transcript)
                
        except Exception as e:
            print(f"OpenAI API error: {e}. Using rule-based fallback.")
            return self._analyze_with_rules(transcript)
    
    def _analyze_with_rules(self, transcript: str) -> Dict:
        """Rule-based analysis of call transcript (fallback)."""
        transcript_lower = transcript.lower()
        
        # Extract summary (first 200 characters)
        summary = transcript[:200] + "..." if len(transcript) > 200 else transcript
        
        # Detect objections (common patterns)
        objection_keywords = {
            'price': ['expensive', 'cost', 'price', 'budget', 'afford', 'cheaper'],
            'timing': ['later', 'next year', 'not now', 'postpone', 'delay', 'timing'],
            'competitor': ['already using', 'competitor', 'other tool', 'switching'],
            'roi': ['roi', 'return', 'justify', 'value', 'benefit'],
            'complexity': ['complex', 'complicated', 'difficult', 'learning curve', 'training']
        }
        
        detected_objections = []
        for objection_type, keywords in objection_keywords.items():
            if any(keyword in transcript_lower for keyword in keywords):
                detected_objections.append(objection_type.replace('_', ' ').title())
        
        # Determine sentiment
        positive_words = ['interested', 'great', 'excellent', 'love', 'perfect', 'yes', 'sounds good']
        negative_words = ['not interested', 'no', 'can\'t', 'won\'t', 'problem', 'concern', 'worried']
        
        positive_count = sum(1 for word in positive_words if word in transcript_lower)
        negative_count = sum(1 for word in negative_words if word in transcript_lower)
        
        if positive_count > negative_count:
            sentiment = 'positive'
        elif negative_count > positive_count:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Determine risk level
        risk_indicators = {
            'high': ['not interested', 'no budget', 'postpone', 'next year', 'competitor', 'decided against'],
            'medium': ['concern', 'worried', 'need to think', 'discuss', 'consider'],
            'low': ['interested', 'sounds good', 'let\'s proceed', 'schedule demo', 'send proposal']
        }
        
        risk_level = 'medium'  # default
        for level, indicators in risk_indicators.items():
            if any(indicator in transcript_lower for indicator in indicators):
                risk_level = level
                break
        
        # Generate next steps
        next_steps = []
        if 'demo' in transcript_lower or 'see' in transcript_lower:
            next_steps.append("Schedule product demo")
        if 'proposal' in transcript_lower or 'quote' in transcript_lower:
            next_steps.append("Send detailed proposal")
        if 'think' in transcript_lower or 'consider' in transcript_lower:
            next_steps.append("Follow up in 3-5 days")
        if 'objection' in transcript_lower or any(obj in detected_objections for obj in ['Price', 'ROI']):
            next_steps.append("Send ROI calculator and case studies")
        if not next_steps:
            next_steps.append("Send follow-up email with relevant resources")
            next_steps.append("Schedule next touchpoint")
        
        return {
            'summary': summary,
            'objections_detected': detected_objections if detected_objections else ['None detected'],
            'sentiment': sentiment,
            'risk_level': risk_level,
            'recommended_next_steps': next_steps[:3]
        }
    
    def analyze_call_batch(self, calls_df: pd.DataFrame) -> pd.DataFrame:
        """Analyze multiple calls and return results as DataFrame."""
        print("Analyzing call transcripts...")
        
        results = []
        for idx, row in calls_df.iterrows():
            call_data = row.to_dict()
            analysis = self.analyze_call(call_data)
            results.append(analysis)
            
            if (idx + 1) % 10 == 0:
                print(f"Analyzed {idx + 1}/{len(calls_df)} calls...")
        
        results_df = pd.DataFrame(results)
        
        # Reset indices to avoid merge issues
        calls_df = calls_df.reset_index(drop=True)
        results_df = results_df.reset_index(drop=True)
        
        # Merge with original call data
        # Use call_id as primary key (it's unique)
        if 'call_id' in calls_df.columns and 'call_id' in results_df.columns:
            merged = calls_df.merge(results_df, on='call_id', how='left', suffixes=('', '_analysis'))
            # Drop duplicate columns from merge
            cols_to_drop = [col for col in merged.columns if col.endswith('_analysis') and col.replace('_analysis', '') in calls_df.columns]
            merged = merged.drop(columns=cols_to_drop)
        else:
            # Fallback: just return the results
            merged = results_df
        
        return merged
    
    def generate_risk_report(self, analyzed_calls_df: pd.DataFrame) -> Dict:
        """Generate risk analysis report from analyzed calls."""
        total_calls = len(analyzed_calls_df)
        
        # Risk level distribution (with error handling)
        if 'risk_level' in analyzed_calls_df.columns:
            risk_distribution = analyzed_calls_df['risk_level'].value_counts().to_dict()
        else:
            risk_distribution = {'medium': total_calls}  # Default if missing
        
        # Sentiment distribution (with error handling)
        if 'sentiment' in analyzed_calls_df.columns:
            sentiment_distribution = analyzed_calls_df['sentiment'].value_counts().to_dict()
        else:
            sentiment_distribution = {'neutral': total_calls}  # Default if missing
        
        # Top objections (with error handling)
        all_objections = []
        if 'objections_detected' in analyzed_calls_df.columns:
            for objections_list in analyzed_calls_df['objections_detected']:
                if isinstance(objections_list, list):
                    all_objections.extend(objections_list)
                elif isinstance(objections_list, str):
                    all_objections.append(objections_list)
        
        objection_counts = pd.Series(all_objections).value_counts().head(5).to_dict() if all_objections else {}
        
        # High-risk calls (with error handling)
        if 'risk_level' in analyzed_calls_df.columns:
            high_risk_calls = analyzed_calls_df[analyzed_calls_df['risk_level'] == 'high']
        else:
            high_risk_calls = pd.DataFrame()  # Empty dataframe if column missing
        
        report = {
            'total_calls_analyzed': total_calls,
            'risk_distribution': risk_distribution,
            'sentiment_distribution': sentiment_distribution,
            'top_objections': objection_counts,
            'high_risk_calls_count': len(high_risk_calls),
            'high_risk_call_ids': high_risk_calls['call_id'].tolist() if len(high_risk_calls) > 0 else [],
            'average_sentiment_score': self._calculate_sentiment_score(analyzed_calls_df),
            'generated_at': datetime.now().isoformat()
        }
        
        return report
    
    def _calculate_sentiment_score(self, df: pd.DataFrame) -> float:
        """Calculate average sentiment score (-1 to 1)."""
        if 'sentiment' not in df.columns:
            return 0.0  # Default neutral score
        sentiment_map = {'positive': 1, 'neutral': 0, 'negative': -1}
        scores = df['sentiment'].map(sentiment_map)
        return float(scores.mean()) if not scores.isna().all() else 0.0


if __name__ == "__main__":
    # Initialize analyzer
    analyzer = CallIntelligenceAnalyzer()
    
    # Load call transcripts
    calls_df = pd.read_csv("data/call_transcripts.csv")
    
    print("=" * 60)
    print("Call Intelligence Analysis")
    print("=" * 60)
    
    # Analyze calls (sample of 10 for demo)
    sample_calls = calls_df.head(10)
    analyzed_calls = analyzer.analyze_call_batch(sample_calls)
    
    # Generate risk report
    risk_report = analyzer.generate_risk_report(analyzed_calls)
    
    print("\nRisk Analysis Report:")
    print(f"Total Calls Analyzed: {risk_report['total_calls_analyzed']}")
    print(f"\nRisk Distribution: {risk_report['risk_distribution']}")
    print(f"\nSentiment Distribution: {risk_report['sentiment_distribution']}")
    print(f"\nTop Objections: {risk_report['top_objections']}")
    print(f"\nHigh-Risk Calls: {risk_report['high_risk_calls_count']}")
    
    # Save analyzed calls
    analyzed_calls.to_csv("data/call_analysis.csv", index=False)
    print("\nAnalyzed calls saved to data/call_analysis.csv")

