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
        # Enhanced prompt with better structure and guidance
        cta_instruction = f"Include a clear call-to-action: {cta}" if cta else "End with an engaging call-to-action that encourages interaction (questions, comments, or shares)."
        
        tone_guidance = {
            "Very Light": "subtle, gentle, understated",
            "Light": "pleasant, friendly, approachable",
            "Moderate": "balanced, professional, engaging",
            "Strong": "confident, assertive, impactful",
            "Very Strong": "powerful, compelling, commanding"
        }.get(tone_intensity, "professional and engaging")
        
        formatting_instructions = {
            "Bullet Points": "Use bullet points (•) for key takeaways. Make each point concise and impactful.",
            "Numbered List": "Use numbered steps or points (1., 2., 3.). Create a logical sequence.",
            "Paragraphs": "Use flowing paragraph format with smooth transitions between ideas.",
            "Mixed Format": "Combine bullets, paragraphs, and lists strategically for maximum engagement.",
            "Question & Answer": "Use Q&A format with engaging questions that spark discussion."
        }.get(formatting, "Use a clear, structured format.")
        
        prompt = f"""Create a compelling {template['name'].lower()} LinkedIn post about: {topic}

CONTEXT:
- Purpose: {purpose}
- Target Audience: {audience}
- Key Message: {message}
- Post Goal: {post_goal}

STYLE REQUIREMENTS:
- Tone: {tone_guidance} with a {language_style.lower()} language style
- Length: {character_guidance} (LinkedIn maximum: 3,000 characters)
- Format: {formatting_instructions}

CONTENT GUIDELINES:
{template['formatting_style']}

- Start with a hook that grabs attention (question, bold statement, or relatable scenario)
- Develop the main message clearly and concisely
- Use LinkedIn-optimized formatting:
  • Strategic CAPITALIZATION for emphasis on key points
  • Relevant emojis (2-4 max) to enhance readability and engagement
  • Clear line breaks between sections for easy scanning
  • Short paragraphs (2-3 sentences max) for mobile readability
- {cta_instruction}

QUALITY STANDARDS:
- Professional yet approachable
- Actionable insights or value
- Authentic voice that resonates with {audience.lower()}
- Engaging and shareable content
- No hashtags unless specifically requested

CRITICAL: The post must be exactly within {character_guidance}. Do not exceed 3,000 characters total.
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
        
        # Validate post length
        if len(post_content) > 3000:
            logging.warning(f"Generated post exceeds 3000 characters ({len(post_content)} chars). Truncating...")
            post_content = post_content[:2997] + "..."
        
        # Check if post is too short (might indicate an error)
        if len(post_content) < 50:
            logging.warning(f"Generated post is very short ({len(post_content)} chars). This might indicate an issue.")
        
        # Generate visual prompt for the post
        visual_prompt = generate_visual_prompt(topic, purpose, audience, post_goal, template_type, visual_style)
        
        return post_content, visual_prompt
        
    except RateLimitError:
        error_msg = (
            "⚠️ **Rate Limit Exceeded**\n\n"
            "The AI service is temporarily busy. Please:\n"
            "• Wait 30-60 seconds and try again\n"
            "• Check if you have API usage limits\n"
            "• Contact support if this persists"
        )
        logging.error("OpenAI API rate limit exceeded")
        return error_msg, ""
    except APIConnectionError:
        error_msg = (
            "⚠️ **Connection Error**\n\n"
            "Unable to connect to the AI service. Please:\n"
            "• Check your internet connection\n"
            "• Verify your network settings\n"
            "• Try again in a few moments"
        )
        logging.error("OpenAI API connection error")
        return error_msg, ""
    except APIError as e:
        error_code = getattr(e, 'code', None)
        error_type = getattr(e, 'type', 'Unknown')
        
        if 'insufficient_quota' in str(e).lower() or 'billing' in str(e).lower():
            error_msg = (
                "⚠️ **API Quota Exceeded**\n\n"
                "The API quota has been exceeded. Please:\n"
                "• Check your OpenAI account billing\n"
                "• Contact your administrator\n"
                "• Try again later"
            )
        elif 'invalid_api_key' in str(e).lower():
            error_msg = (
                "⚠️ **API Configuration Error**\n\n"
                "The API key is invalid or missing. Please:\n"
                "• Contact your administrator\n"
                "• Verify API configuration"
            )
        else:
            error_msg = (
                f"⚠️ **API Error**\n\n"
                f"An error occurred: {str(e)[:200]}\n\n"
                f"Error Type: {error_type}\n"
                f"Please try again or contact support if the issue persists."
            )
        logging.error(f"OpenAI API error: {str(e)} (Code: {error_code}, Type: {error_type})")
        return error_msg, ""
    except ValueError as e:
        error_msg = (
            f"⚠️ **Input Validation Error**\n\n"
            f"{str(e)}\n\n"
            f"Please check your input and try again."
        )
        logging.error(f"Input validation error: {str(e)}")
        return error_msg, ""
    except Exception as e:
        error_msg = (
            "⚠️ **Unexpected Error**\n\n"
            "An unexpected error occurred while generating your post.\n\n"
            "Please:\n"
            "• Try again in a moment\n"
            "• Check that all required fields are filled\n"
            "• Contact support if the problem continues\n\n"
            f"Error details: {type(e).__name__}"
        )
        logging.error(f"Unexpected error generating AI post: {str(e)}", exc_info=True)
        return error_msg, ""

