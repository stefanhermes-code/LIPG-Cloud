"""
Post Templates Configuration
Different templates for various LinkedIn post types and industries
"""

POST_TEMPLATES = {
    "professional": {
        "name": "Professional",
        "description": "Standard professional post format",
        "system_prompt": "You are a professional LinkedIn post writer. Create engaging, professional content that builds thought leadership and drives engagement.",
        "formatting_style": "Use professional language with strategic use of emojis, bullet points, and clear call-to-actions."
    },
    
    "storytelling": {
        "name": "Storytelling",
        "description": "Personal story-driven posts",
        "system_prompt": "You are a master storyteller on LinkedIn. Create compelling personal stories that connect with your audience and drive engagement.",
        "formatting_style": "Use storytelling techniques with emotional hooks, personal anecdotes, and relatable experiences."
    },
    
    "industry_insights": {
        "name": "Industry Insights",
        "description": "Technical and industry-specific content",
        "system_prompt": "You are an industry expert writing LinkedIn posts. Share valuable insights, trends, and technical knowledge that positions you as a thought leader.",
        "formatting_style": "Use technical language appropriately, include data points, and provide actionable insights."
    },
    
    "motivational": {
        "name": "Motivational",
        "description": "Inspirational and motivational content",
        "system_prompt": "You are a motivational speaker on LinkedIn. Create inspiring content that motivates and energizes your audience.",
        "formatting_style": "Use uplifting language, powerful quotes, and energizing calls-to-action."
    },
    
    "educational": {
        "name": "Educational",
        "description": "How-to and educational content",
        "system_prompt": "You are an educator on LinkedIn. Create informative, step-by-step content that teaches valuable skills and knowledge.",
        "formatting_style": "Use clear structure, numbered steps, and practical examples."
    },
    
    "news_commentary": {
        "name": "News Commentary",
        "description": "Current events and news commentary",
        "system_prompt": "You are a LinkedIn commentator on current events. Provide thoughtful analysis and professional commentary on relevant news and trends.",
        "formatting_style": "Use balanced perspective, cite sources, and encourage discussion."
    },
    
    "product_showcase": {
        "name": "Product Showcase",
        "description": "Product and service promotion",
        "system_prompt": "You are a marketing professional on LinkedIn. Create compelling content that showcases products or services without being overly salesy.",
        "formatting_style": "Use benefit-focused language, social proof, and clear value propositions."
    },
    
    "networking": {
        "name": "Networking",
        "description": "Connection and relationship building",
        "system_prompt": "You are a networking expert on LinkedIn. Create content that builds relationships and encourages professional connections.",
        "formatting_style": "Use conversational tone, ask engaging questions, and encourage interaction."
    }
}

INDUSTRY_SPECIFIC_TEMPLATES = {
    "technology": {
        "name": "Technology",
        "keywords": ["AI", "software", "development", "innovation", "digital transformation"],
        "tone": "Technical but accessible",
        "audience": "Tech professionals, developers, IT leaders"
    },
    
    "healthcare": {
        "name": "Healthcare",
        "keywords": ["patient care", "medical", "health", "wellness", "treatment"],
        "tone": "Compassionate and professional",
        "audience": "Healthcare professionals, patients, medical staff"
    },
    
    "finance": {
        "name": "Finance",
        "keywords": ["investment", "financial", "market", "economy", "banking"],
        "tone": "Authoritative and trustworthy",
        "audience": "Financial professionals, investors, business leaders"
    },
    
    "education": {
        "name": "Education",
        "keywords": ["learning", "teaching", "students", "academic", "knowledge"],
        "tone": "Inspiring and informative",
        "audience": "Educators, students, academic professionals"
    },
    
    "marketing": {
        "name": "Marketing",
        "keywords": ["brand", "campaign", "strategy", "digital", "content"],
        "tone": "Creative and strategic",
        "audience": "Marketers, brand managers, content creators"
    }
}

def get_template(template_name):
    """Get template configuration by name"""
    return POST_TEMPLATES.get(template_name, POST_TEMPLATES["professional"])

def get_industry_template(industry):
    """Get industry-specific template configuration"""
    return INDUSTRY_SPECIFIC_TEMPLATES.get(industry, INDUSTRY_SPECIFIC_TEMPLATES["technology"])

def get_all_templates():
    """Get all available templates"""
    return POST_TEMPLATES

def get_all_industries():
    """Get all available industries"""
    return INDUSTRY_SPECIFIC_TEMPLATES

