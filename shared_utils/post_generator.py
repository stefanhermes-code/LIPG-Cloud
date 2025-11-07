"""
Post Generator Module
Core functions for generating LinkedIn posts using OpenAI
"""

import logging
import os
from openai import OpenAI, RateLimitError, APIError, APIConnectionError
import re

# Configure logging
logging.basicConfig(level=logging.INFO)

# Lazy client initialization to avoid errors at import time
_client = None

def get_openai_client():
    """Get or create OpenAI client, checking both environment variables and Streamlit secrets"""
    global _client
    if _client is not None:
        return _client
    
    # Try to get API key from environment variable first
    api_key = os.getenv('OPENAI_API_KEY')
    
    # If not found, try Streamlit secrets (for Streamlit Cloud)
    if not api_key:
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
                api_key = st.secrets['OPENAI_API_KEY']
        except (ImportError, AttributeError):
            pass
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables or Streamlit secrets")
    
    # Create client with explicit retry and timeout limits to prevent excessive retries
    _client = OpenAI(
        api_key=api_key,
        max_retries=2,  # Limit retries to prevent excessive API calls
        timeout=60.0  # 60 second timeout to prevent hanging
    )
    return _client

# Input validation functions
def validate_input(text, field_name, max_length=500):
    """Validate and sanitize user input"""
    if not text or not text.strip():
        raise ValueError(f"{field_name} cannot be empty")
    
    # Remove potentially harmful characters
    text = re.sub(r'[<>"\']', '', text.strip())
    
    if len(text) > max_length:
        raise ValueError(f"{field_name} cannot exceed {max_length} characters")
    
    return text

def validate_topic(topic):
    """Validate topic input"""
    return validate_input(topic, "Topic", 200)

def validate_purpose(purpose):
    """Validate purpose input"""
    return validate_input(purpose, "Purpose", 300)

def validate_message(message):
    """Validate message input"""
    return validate_input(message, "Message", 1000)

def validate_cta(cta):
    """Validate call-to-action input"""
    return validate_input(cta, "Call-to-Action", 200)

def generate_visual_prompt(topic, purpose, audience, post_goal, template_type, visual_style="photo_realistic"):
    """Generate a visual prompt for image generation based on the post content"""
    try:
        # Visual style mappings based on template type
        template_styles = {
            "professional": "clean, corporate, business-focused, professional lighting, modern office setting",
            "storytelling": "warm, personal, authentic, natural lighting, human-centered",
            "industry_insights": "technical, data-driven, charts and graphs, professional, analytical",
            "motivational": "inspiring, uplifting, bright colors, dynamic, energetic",
            "educational": "clear, instructional, step-by-step, informative, clean design",
            "news_commentary": "current, relevant, news-focused, professional, timely",
            "product_showcase": "product-focused, clean background, professional, highlight features",
            "networking": "people-focused, collaborative, professional, connection-oriented"
        }
        
        # Visual style mappings for different image types
        image_styles = {
            "photo_realistic": "photorealistic, high-resolution photography, realistic lighting, professional photography",
            "illustration": "illustration, hand-drawn style, artistic, creative illustration",
            "minimalist": "minimalist design, clean lines, simple shapes, white space, modern minimalist",
            "infographic": "infographic style, data visualization, charts, graphs, informational graphics",
            "abstract": "abstract art, geometric shapes, artistic, creative, non-representational",
            "vintage": "vintage style, retro design, classic, timeless, nostalgic",
            "modern_flat": "flat design, modern, clean, simple, contemporary flat design",
            "3d_render": "3D rendered, three-dimensional, computer generated, modern 3D graphics"
        }
        
        # Color palettes for different goals
        color_palettes = {
            "Educate": "blue and white, professional, clean",
            "Engage": "vibrant colors, energetic, eye-catching",
            "Promote": "brand colors, professional, attention-grabbing",
            "Inspire": "warm tones, uplifting, motivational",
            "Inform": "neutral tones, clear, informative",
            "Motivate": "bold colors, dynamic, energetic",
            "Entertain": "fun colors, playful, engaging",
            "Network": "professional blues and grays, trustworthy",
            "Advocate": "strong colors, impactful, meaningful"
        }
        
        template_style = template_styles.get(template_type, "professional, clean, modern")
        image_style = image_styles.get(visual_style, "photorealistic, high-resolution photography")
        color_palette = color_palettes.get(post_goal, "professional, clean")
        
        visual_prompt = f"""
        Create a LinkedIn post image for: {topic}
        
        Purpose: {purpose}
        Audience: {audience}
        Goal: {post_goal}
        
        Template Style: {template_style}
        Image Type: {image_style}
        Color Palette: {color_palette}
        
        Image Requirements:
        - LinkedIn-optimized (1200x627px recommended)
        - Professional quality
        - Text overlay friendly
        - High contrast for readability
        - Brand-appropriate
        
        Final Style: {image_style} with {template_style} approach
        """
        
        return visual_prompt.strip()
        
    except Exception as e:
        logging.error(f"Error generating visual prompt: {str(e)}")
        return f"Professional LinkedIn post image for: {topic} - {purpose}"

def generate_ai_post(topic, purpose, audience, message, tone_intensity, language_style, post_length, formatting, cta, post_goal, template_type="professional", visual_style="photo_realistic"):
    """
    Generate a LinkedIn post using OpenAI GPT-4
    
    Returns:
        tuple: (generated_post, visual_prompt)
    """
    try:
        # Validate inputs before processing
        topic = validate_topic(topic)
        purpose = validate_purpose(purpose)
        message = validate_message(message)
        # CTA is optional - only validate if provided
        if cta:
            cta = validate_cta(cta)
        
        # Import template function
        from shared_utils.templates_config import get_template
        
        # Get template configuration
        template = get_template(template_type)
        
        # Map post length to character ranges
        length_mappings = {
            "Very Short": "100-300 characters (1-2 sentences)",
            "Short": "300-800 characters (2-4 sentences)", 
            "Medium": "800-1,500 characters (4-8 sentences)",
            "Long": "1,500-2,500 characters (8-15 sentences)",
            "Very Long": "2,500-3,000 characters (15+ sentences)"
        }
        
        character_guidance = length_mappings.get(post_length, "800-1,500 characters")
        
        # Build enhanced prompt with template
        prompt = f"""
        Write a {template['name'].lower()} LinkedIn post about {topic}. 
        
        Purpose: {purpose}
        Target audience: {audience}
        Key message: {message}
        Tone: {tone_intensity} {language_style}
        Post length: {character_guidance} (LinkedIn limit: 3,000 characters max)
        Post structure: {formatting}
        Call-to-action: {cta}
        Post goal: {post_goal}
        
        {template['formatting_style']}
        
        Structure the post using: {formatting}
        - If "Bullet Points": Use bullet points for key takeaways
        - If "Numbered List": Use numbered steps or points
        - If "Paragraphs": Use flowing paragraph format
        - If "Mixed Format": Combine bullets, paragraphs, and lists strategically
        - If "Question & Answer": Use Q&A format with engaging questions
        
        Use LinkedIn-friendly formatting:
        - CAPITALIZATION for emphasis
        - Emojis for engagement
        - Clear structure and flow
        - Line breaks for readability
        
        IMPORTANT: Keep the post within the specified character range. LinkedIn has a 3,000 character limit.
        """
        
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": template['system_prompt']},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        post_content = response.choices[0].message.content.strip()
        
        # Generate visual prompt for the post
        visual_prompt = generate_visual_prompt(topic, purpose, audience, post_goal, template_type, visual_style)
        
        return post_content, visual_prompt
        
    except RateLimitError:
        logging.error("OpenAI API rate limit exceeded")
        return "⚠️ Rate limit exceeded. Please wait a moment and try again.", ""
    except APIConnectionError:
        logging.error("OpenAI API connection error")
        return "⚠️ Connection error. Please check your internet connection and try again.", ""
    except APIError as e:
        logging.error(f"OpenAI API error: {str(e)}")
        return f"⚠️ API error: {str(e)}", ""
    except ValueError as e:
        logging.error(f"Input validation error: {str(e)}")
        return f"⚠️ {str(e)}", ""
    except Exception as e:
        logging.error(f"Unexpected error generating AI post: {str(e)}")
        return "⚠️ An unexpected error occurred while generating the post. Please try again.", ""

