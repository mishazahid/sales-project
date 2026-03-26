"""
Module 2: AI Outreach Personalization (LLM + RAG)
Creates product knowledge base, stores embeddings, and generates personalized emails.
"""

import pandas as pd
import numpy as np
import json
import os
from typing import List, Dict, Tuple
from datetime import datetime
import openai
from openai import OpenAI
import pickle

# For vector similarity (using simple cosine similarity for demo)
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer


class ProductKnowledgeBase:
    """Manages product knowledge base and embeddings."""
    
    def __init__(self, knowledge_base_path: str = "data/product_knowledge_base.json"):
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_base = []
        self.embeddings = None
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.embeddings_matrix = None
        
    def create_knowledge_base(self):
        """Create product knowledge base with key information."""
        knowledge_base = [
            {
                "id": "kb_001",
                "category": "Product Features",
                "content": "CloudFlow Solutions offers real-time collaboration, task management, resource allocation, and AI-powered project insights. Our platform integrates with 50+ tools including Slack, Jira, and Microsoft Teams.",
                "use_cases": ["Team collaboration", "Project tracking", "Resource management"]
            },
            {
                "id": "kb_002",
                "category": "Product Features",
                "content": "Advanced reporting and analytics dashboard provides visibility into project health, team productivity, and resource utilization. Customizable reports can be exported to PDF or Excel.",
                "use_cases": ["Reporting", "Analytics", "Performance tracking"]
            },
            {
                "id": "kb_003",
                "category": "Product Features",
                "content": "Automated workflow builder allows teams to create custom processes without coding. Templates available for agile, waterfall, and hybrid methodologies.",
                "use_cases": ["Process automation", "Workflow customization", "Methodology support"]
            },
            {
                "id": "kb_004",
                "category": "ROI & Benefits",
                "content": "Customers report 30% reduction in project delivery time, 25% improvement in team productivity, and 40% reduction in project management overhead. Average ROI achieved within 6 months.",
                "use_cases": ["ROI justification", "Efficiency gains", "Cost savings"]
            },
            {
                "id": "kb_005",
                "category": "ROI & Benefits",
                "content": "CloudFlow reduces manual status updates by 60% through automated progress tracking and AI-powered insights. Teams save 5-10 hours per week on administrative tasks.",
                "use_cases": ["Time savings", "Automation benefits", "Productivity"]
            },
            {
                "id": "kb_006",
                "category": "Industry Solutions",
                "content": "Marketing agencies use CloudFlow to manage multiple client campaigns, track deliverables, and improve client communication. Features include client portals and white-label options.",
                "use_cases": ["Marketing agencies", "Client management", "Multi-project tracking"]
            },
            {
                "id": "kb_007",
                "category": "Industry Solutions",
                "content": "Professional services firms leverage CloudFlow for resource planning, project profitability tracking, and client collaboration. Integration with accounting systems available.",
                "use_cases": ["Professional services", "Resource planning", "Profitability"]
            },
            {
                "id": "kb_008",
                "category": "Industry Solutions",
                "content": "Technology companies use CloudFlow for sprint planning, bug tracking, and release management. Native integrations with GitHub, GitLab, and CI/CD pipelines.",
                "use_cases": ["Tech companies", "Sprint planning", "Development workflows"]
            },
            {
                "id": "kb_009",
                "category": "Pricing & Plans",
                "content": "Starter plan at $29/user/month for teams of 5-20 users. Professional plan at $49/user/month for 21-100 users with advanced features. Enterprise plan at $79/user/month with custom integrations and dedicated support.",
                "use_cases": ["Pricing questions", "Plan selection", "Budget planning"]
            },
            {
                "id": "kb_010",
                "category": "Implementation",
                "content": "Average implementation time is 2-4 weeks. Includes data migration, team training, and custom workflow setup. Dedicated customer success manager assigned to Enterprise customers.",
                "use_cases": ["Implementation timeline", "Onboarding", "Support"]
            }
        ]
        
        self.knowledge_base = knowledge_base
        
        # Save knowledge base
        os.makedirs(os.path.dirname(self.knowledge_base_path), exist_ok=True)
        with open(self.knowledge_base_path, 'w') as f:
            json.dump(knowledge_base, f, indent=2)
        
        print(f"Created knowledge base with {len(knowledge_base)} entries")
        return knowledge_base
    
    def load_knowledge_base(self):
        """Load knowledge base from file."""
        if os.path.exists(self.knowledge_base_path):
            with open(self.knowledge_base_path, 'r') as f:
                self.knowledge_base = json.load(f)
        else:
            self.create_knowledge_base()
    
    def create_embeddings(self):
        """Create embeddings for knowledge base using TF-IDF (or OpenAI if API key available)."""
        if not self.knowledge_base:
            self.load_knowledge_base()
        
        # Combine content for each knowledge base entry
        texts = [f"{item['content']} {' '.join(item.get('use_cases', []))}" for item in self.knowledge_base]
        
        # Create TF-IDF embeddings
        self.embeddings_matrix = self.vectorizer.fit_transform(texts)
        
        print(f"Created embeddings for {len(texts)} knowledge base entries")
        return self.embeddings_matrix
    
    def find_relevant_content(self, query: str, top_k: int = 3) -> List[Dict]:
        """Find most relevant knowledge base entries for a query."""
        if self.embeddings_matrix is None:
            self.create_embeddings()
        
        # Vectorize query
        query_vector = self.vectorizer.transform([query])
        
        # Calculate similarity
        similarities = cosine_similarity(query_vector, self.embeddings_matrix)[0]
        
        # Get top K indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Return relevant entries
        relevant_entries = []
        for idx in top_indices:
            entry = self.knowledge_base[idx].copy()
            entry['similarity_score'] = float(similarities[idx])
            relevant_entries.append(entry)
        
        return relevant_entries


class EmailPersonalizationEngine:
    """Generates personalized emails using LLM and RAG."""
    
    def __init__(self, knowledge_base_path: str = "data/product_knowledge_base.json", 
                 openai_api_key: str = None):
        self.kb = ProductKnowledgeBase(knowledge_base_path)
        self.kb.load_knowledge_base()
        self.kb.create_embeddings()
        
        # Initialize OpenAI client if API key provided
        self.client = None
        try:
            if openai_api_key:
                self.client = OpenAI(api_key=openai_api_key)
            elif os.getenv('OPENAI_API_KEY'):
                self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        except Exception as e:
            # Keep the app bootable even if OpenAI client init fails.
            print(f"OpenAI client initialization failed: {e}. Using template fallback.")
            self.client = None
    
    def generate_personalized_email(self, lead_data: Dict, variant: str = "A") -> Dict:
        """Generate personalized email for a lead using RAG."""
        
        # Extract lead information
        company = lead_data.get('company', '')
        industry = lead_data.get('industry', '')
        job_title = lead_data.get('job_title', '')
        first_name = lead_data.get('first_name', '')
        company_size = lead_data.get('company_size_bucket', '')
        
        # Build query for RAG
        query = f"{industry} {company_size} company {job_title}"
        
        # Find relevant knowledge base content
        relevant_content = self.kb.find_relevant_content(query, top_k=3)
        
        # Build context from relevant content
        context = "\n\n".join([
            f"Key Point: {entry['content']}\nRelevant Use Cases: {', '.join(entry.get('use_cases', []))}"
            for entry in relevant_content
        ])
        
        # Generate email using LLM or template
        if self.client:
            # Use OpenAI API
            email = self._generate_with_openai(lead_data, context, variant)
        else:
            # Use template-based generation (fallback)
            email = self._generate_with_template(lead_data, context, variant)
        
        return email
    
    def _generate_with_openai(self, lead_data: Dict, context: str, variant: str) -> Dict:
        """Generate email using OpenAI API."""
        prompt = f"""You are a sales representative for CloudFlow Solutions, a B2B project management software.

Lead Information:
- Name: {lead_data.get('first_name', '')} {lead_data.get('last_name', '')}
- Company: {lead_data.get('company', '')}
- Job Title: {lead_data.get('job_title', '')}
- Industry: {lead_data.get('industry', '')}
- Company Size: {lead_data.get('company_size_bucket', '')}

Product Context:
{context}

Generate a personalized, professional sales email (variant {variant}) that:
1. Addresses the lead by first name
2. References their company and industry
3. Highlights relevant product features based on their profile
4. Includes a clear value proposition
5. Has a soft call-to-action
6. Is concise (150-200 words)

Email:"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert B2B sales email writer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            email_body = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API error: {e}. Using template fallback.")
            email_body = self._generate_with_template(lead_data, context, variant)['body']
        
        subject = f"{lead_data.get('company', 'Company')} - Streamline Your {lead_data.get('industry', 'Team')} Projects with CloudFlow"
        
        return {
            'subject': subject,
            'body': email_body,
            'variant': variant,
            'personalization_score': 0.85,
            'relevant_kb_entries': len(context.split('\n\n'))
        }
    
    def _generate_with_template(self, lead_data: Dict, context: str, variant: str) -> Dict:
        """Generate email using template (fallback when OpenAI not available)."""
        first_name = lead_data.get('first_name', '')
        company = lead_data.get('company', '')
        industry = lead_data.get('industry', '')
        job_title = lead_data.get('job_title', '')
        
        # Extract key benefits from context
        benefits = []
        if 'productivity' in context.lower() or 'efficiency' in context.lower():
            benefits.append("improve team productivity by 25%")
        if 'time' in context.lower() or 'save' in context.lower():
            benefits.append("save 5-10 hours per week on administrative tasks")
        if 'ROI' in context or 'roi' in context.lower():
            benefits.append("achieve ROI within 6 months")
        
        benefit_text = ", ".join(benefits[:2]) if benefits else "streamline project management and improve team collaboration"
        
        if variant == "A":
            email_body = f"""Hi {first_name},

I noticed that {company} operates in the {industry} space. Many {industry} companies like yours are struggling with project management complexity and team coordination.

CloudFlow Solutions can help {company} {benefit_text}. Our platform is specifically designed for {industry} companies of your size.

Key benefits for {company}:
• Real-time collaboration across teams
• Automated workflow management
• Advanced analytics and reporting
• Integration with your existing tools

Would you be open to a brief 15-minute conversation to explore how CloudFlow could help {company} streamline project delivery?

Best regards,
[Your Name]
CloudFlow Solutions"""
        else:  # variant B
            email_body = f"""Hello {first_name},

{company} likely faces the same project management challenges that many {industry} companies experience: keeping teams aligned, tracking progress, and managing resources efficiently.

CloudFlow Solutions has helped similar {industry} companies reduce project delivery time by 30% and improve team productivity by 25%.

Here's what sets CloudFlow apart:
✓ Built specifically for mid-market {industry} companies
✓ AI-powered insights to identify bottlenecks early
✓ Seamless integration with tools you already use
✓ Dedicated support during implementation

I'd love to show you how {company} could benefit. Are you available for a quick demo this week?

Best,
[Your Name]
CloudFlow Solutions"""
        
        subject = f"{company} - Transform Your {industry} Project Management"
        
        return {
            'subject': subject,
            'body': email_body,
            'variant': variant,
            'personalization_score': 0.75,
            'relevant_kb_entries': 2
        }
    
    def generate_ab_variants(self, lead_data: Dict) -> Dict:
        """Generate A/B test variants for a lead."""
        variant_a = self.generate_personalized_email(lead_data, variant="A")
        variant_b = self.generate_personalized_email(lead_data, variant="B")
        
        return {
            'lead_id': lead_data.get('lead_id'),
            'variant_a': variant_a,
            'variant_b': variant_b,
            'generated_at': datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Initialize email personalization engine
    engine = EmailPersonalizationEngine()
    
    # Example: Generate email for a lead
    sample_lead = {
        'lead_id': 123,
        'first_name': 'John',
        'last_name': 'Smith',
        'company': 'TechCorp Inc',
        'job_title': 'Director of IT',
        'industry': 'Technology',
        'company_size_bucket': '101-250'
    }
    
    print("=" * 60)
    print("Generating Personalized Email")
    print("=" * 60)
    
    email_variants = engine.generate_ab_variants(sample_lead)
    
    print("\nVariant A:")
    print(f"Subject: {email_variants['variant_a']['subject']}")
    print(f"\nBody:\n{email_variants['variant_a']['body']}")
    
    print("\n" + "=" * 60)
    print("\nVariant B:")
    print(f"Subject: {email_variants['variant_b']['subject']}")
    print(f"\nBody:\n{email_variants['variant_b']['body']}")

