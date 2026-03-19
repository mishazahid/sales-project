"""
Module 1: Predictive Lead Scoring
Uses XGBoost to predict conversion probability and rank leads by priority.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, roc_auc_score, accuracy_score
import xgboost as xgb
import joblib
import os
from datetime import datetime
from typing import Dict, List, Tuple


class LeadScoringModel:
    """Predictive lead scoring model using XGBoost."""
    
    def __init__(self, model_path: str = "models/lead_scoring_model.pkl"):
        self.model_path = model_path
        self.model = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.feature_names = []
        
    def load_data(self, crm_path: str, email_path: str) -> pd.DataFrame:
        """Load and merge CRM leads with email engagement data."""
        print("Loading CRM leads...")
        leads = pd.read_csv(crm_path)
        
        print("Loading email engagement data...")
        email_engagement = pd.read_csv(email_path)
        
        # Aggregate email metrics per lead
        email_metrics = email_engagement.groupby('lead_id').agg({
            'opened': 'sum',
            'clicked': 'sum',
            'replied': 'sum',
            'email_sequence_step': 'max'
        }).reset_index()
        
        email_metrics.columns = ['lead_id', 'total_opens', 'total_clicks', 'total_replies', 'max_sequence_step']
        
        # Merge with leads
        leads = leads.merge(email_metrics, on='lead_id', how='left')
        leads['total_opens'] = leads['total_opens'].fillna(0)
        leads['total_clicks'] = leads['total_clicks'].fillna(0)
        leads['total_replies'] = leads['total_replies'].fillna(0)
        leads['max_sequence_step'] = leads['max_sequence_step'].fillna(0)
        
        return leads
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create features for the model."""
        print("Engineering features...")
        
        # Copy dataframe
        features_df = df.copy()
        
        # Encode categorical variables
        categorical_cols = ['industry', 'company_size_bucket', 'lead_source', 'country', 'job_title']
        
        for col in categorical_cols:
            if col in features_df.columns:
                le = LabelEncoder()
                features_df[f'{col}_encoded'] = le.fit_transform(features_df[col].astype(str))
                self.label_encoders[col] = le
        
        # Create derived features
        features_df['days_since_created'] = (
            pd.to_datetime('now') - pd.to_datetime(features_df['created_at'])
        ).dt.days
        
        # Email engagement rates
        features_df['email_open_rate'] = features_df['total_opens'] / (features_df['max_sequence_step'] + 1)
        features_df['email_click_rate'] = features_df['total_clicks'] / (features_df['total_opens'] + 1)
        features_df['email_reply_rate'] = features_df['total_replies'] / (features_df['max_sequence_step'] + 1)
        
        # Status encoding (higher value = closer to conversion)
        status_map = {
            'New': 1,
            'Contacted': 2,
            'Qualified': 3,
            'Demo Scheduled': 4,
            'Proposal Sent': 5,
            'Negotiation': 6,
            'Closed Won': 7,
            'Closed Lost': 0
        }
        features_df['status_encoded'] = features_df['status'].map(status_map).fillna(0)
        
        # Company size numeric
        size_map = {
            '10-50': 30,
            '50-100': 75,
            '101-250': 175,
            '251-500': 375
        }
        features_df['company_size_numeric'] = features_df['company_size_bucket'].map(size_map).fillna(100)
        
        # Deal size features
        features_df['deal_size_log'] = np.log1p(features_df['estimated_deal_size'])
        
        # Select features for model
        feature_cols = [
            'lead_score_baseline',
            'industry_encoded',
            'company_size_bucket_encoded',
            'lead_source_encoded',
            'country_encoded',
            'job_title_encoded',
            'status_encoded',
            'days_since_created',
            'total_opens',
            'total_clicks',
            'total_replies',
            'max_sequence_step',
            'email_open_rate',
            'email_click_rate',
            'email_reply_rate',
            'company_size_numeric',
            'deal_size_log'
        ]
        
        # Filter to available columns
        available_features = [col for col in feature_cols if col in features_df.columns]
        self.feature_names = available_features
        
        return features_df[available_features + ['lead_id', 'converted']]
    
    def train(self, crm_path: str, email_path: str, test_size: float = 0.2):
        """Train the lead scoring model."""
        print("=" * 60)
        print("Training Predictive Lead Scoring Model")
        print("=" * 60)
        
        # Load and prepare data
        leads = self.load_data(crm_path, email_path)
        features_df = self.engineer_features(leads)
        
        # Prepare training data
        X = features_df[self.feature_names]
        y = features_df['converted'].astype(int)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train XGBoost model
        print("\nTraining XGBoost model...")
        self.model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric='logloss'
        )
        
        self.model.fit(
            X_train_scaled, y_train,
            eval_set=[(X_test_scaled, y_test)],
            verbose=False
        )
        
        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        print("\n" + "=" * 60)
        print("Model Performance Metrics")
        print("=" * 60)
        print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
        print(f"ROC-AUC: {roc_auc_score(y_test, y_pred_proba):.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        # Save model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_names': self.feature_names
        }, self.model_path)
        print(f"\nModel saved to {self.model_path}")
        
        return self.model
    
    def predict(self, leads_df: pd.DataFrame) -> pd.DataFrame:
        """Predict conversion probability for leads."""
        if self.model is None:
            # Load saved model
            if os.path.exists(self.model_path):
                model_data = joblib.load(self.model_path)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.label_encoders = model_data['label_encoders']
                self.feature_names = model_data['feature_names']
            else:
                raise ValueError("Model not trained. Please train the model first.")
        
        # Engineer features
        features_df = self.engineer_features(leads_df)
        
        # Prepare features
        X = features_df[self.feature_names]
        X_scaled = self.scaler.transform(X)
        
        # Predict
        conversion_proba = self.model.predict_proba(X_scaled)[:, 1]
        
        # Create results dataframe
        results = pd.DataFrame({
            'lead_id': features_df['lead_id'],
            'conversion_probability': conversion_proba,
            'priority_rank': pd.Series(conversion_proba).rank(ascending=False, method='dense').astype(int)
        })
        
        return results
    
    def score_leads(self, crm_path: str, email_path: str, output_path: str = "data/lead_scores.csv"):
        """Score all leads and save results."""
        print("Scoring leads...")
        
        # Load data
        leads = self.load_data(crm_path, email_path)
        
        # Predict
        scores = self.predict(leads)
        
        # Merge with original lead data
        scored_leads = leads[['lead_id', 'first_name', 'last_name', 'company', 'status', 'lead_score_baseline']].merge(
            scores, on='lead_id'
        )
        
        # Sort by priority
        scored_leads = scored_leads.sort_values('conversion_probability', ascending=False)
        
        # Save
        scored_leads.to_csv(output_path, index=False)
        print(f"Scored leads saved to {output_path}")
        print(f"\nTop 10 High-Priority Leads:")
        print(scored_leads[['lead_id', 'company', 'conversion_probability', 'priority_rank']].head(10).to_string())
        
        return scored_leads


if __name__ == "__main__":
    # Train and score leads
    model = LeadScoringModel()
    
    # Train model
    model.train(
        crm_path="data/crm_leads.csv",
        email_path="data/email_engagement.csv"
    )
    
    # Score all leads
    scored_leads = model.score_leads(
        crm_path="data/crm_leads.csv",
        email_path="data/email_engagement.csv",
        output_path="data/lead_scores.csv"
    )

