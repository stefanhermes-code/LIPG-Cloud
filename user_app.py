"""
LinkedIn Post Generator - User App
Streamlit-based cloud application for generating LinkedIn posts
"""

import streamlit as st
import os
import sys
from datetime import datetime
import json
import hashlib
import base64
import html

# Ensure we can import from shared_utils when app is at repo root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared_utils.post_generator import generate_ai_post, generate_visual_prompt
from shared_utils.data_manager import (
    save_post_to_database, 
    get_user_post_history,
    authenticate_user,
    update_last_login
)
from shared_utils.config_loader import load_customer_config
from shared_utils.templates_config import get_template, get_all_templates

# Page configuration
st.set_page_config(
    page_title="LinkedIn Post Generator",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'generated_post' not in st.session_state:
    st.session_state.generated_post = ""
if 'visual_prompt' not in st.session_state:
    st.session_state.visual_prompt = ""
if 'generating' not in st.session_state:
    st.session_state.generating = False
if 'last_generation_request' not in st.session_state:
    st.session_state.last_generation_request = None
if 'form_reset' not in st.session_state:
    st.session_state.form_reset = False
if 'reset_key' not in st.session_state:
    st.session_state.reset_key = '0'

# Load customer configuration
try:
    customer_config = load_customer_config()
    customer_name = customer_config.get('customer_name', 'LinkedIn Post Generator')
    background_color = customer_config.get('background_color', '#E9F7EF')
    button_color = customer_config.get('button_color', '#17A2B8')
except Exception as e:
    st.error(f"Error loading configuration: {str(e)}")
    customer_name = "LinkedIn Post Generator"
    background_color = '#E9F7EF'
    button_color = '#17A2B8'

# Get logo path
_base_dir = os.path.dirname(os.path.abspath(__file__))
_logo_path = os.path.join(_base_dir, "static", "logo.png")
_logo_exists = os.path.exists(_logo_path)

# Custom CSS
st.markdown(f"""
    <style>
        .main {{
            background-color: {background_color};
        }}
        .stButton > button {{
            background-color: {button_color};
            color: white;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        .stButton > button:hover {{
            background-color: {button_color}CC;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        .post-container {{
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            border: 2px solid #ddd;
            margin-top: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header-container {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
            margin-bottom: 30px;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .header-logo {{
            max-height: 100px;
            max-width: 200px;
        }}
        .header-text {{
            text-align: center;
        }}
        .header-text h1 {{
            margin: 0;
            color: #333;
            font-size: 2.5em;
        }}
        .header-text h2 {{
            margin: 5px 0 0 0;
            color: #666;
            font-size: 1.3em;
            font-weight: 400;
        }}
        .instructions-box {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            border-left: 4px solid {button_color};
        }}
        .instructions-box h3 {{
            color: {button_color};
            margin-top: 0;
        }}
        .instructions-box ol {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .instructions-box li {{
            margin: 8px 0;
            color: #555;
        }}
    </style>
""", unsafe_allow_html=True)

# Header with Logo
if _logo_exists:
    try:
        col_logo, col_text = st.columns([1, 3])
        with col_logo:
            st.image(_logo_path, use_container_width=True)
        with col_text:
            st.markdown(f"""
                <div class="header-text">
                    <h1>{customer_name}</h1>
                    <h2>LinkedIn Post Generator</h2>
                </div>
            """, unsafe_allow_html=True)
    except Exception:
        # Fallback if logo fails to load
        st.markdown(f"""
            <div class="header-container">
                <div class="header-text">
                    <h1>{customer_name}</h1>
                    <h2>LinkedIn Post Generator</h2>
                </div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div class="header-container">
            <div class="header-text">
                <h1>{customer_name}</h1>
                <h2>LinkedIn Post Generator</h2>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Instructions section
with st.expander("📖 How to Use - Step-by-Step Instructions", expanded=False):
    # Contact button
    st.markdown(f"""
        <div style="text-align: center; margin-top: 20px;">
            <a href="mailto:shermeshtc@gmail.com" style="background-color: {button_color}; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; display: inline-block; font-weight: 600;">
                📧 Contact Support
            </a>
        </div>
    """, unsafe_allow_html=True)

# User Authentication
if not st.session_state.authenticated:
    st.title("🔐 Login to LinkedIn Post Generator")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", type="primary", use_container_width=True):
                if username and password:
                    success, message = authenticate_user(username, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        update_last_login(username)
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.error("⚠️ Please enter both username and password")
    
    st.stop()  # Stop execution until authenticated

# Sidebar for user info and history
with st.sidebar:
    # Logo space at top
    st.markdown("<div style='text-align: center; padding: 20px 0;'>", unsafe_allow_html=True)
    try:
        # Get the absolute path to the logo file
        current_file = os.path.abspath(__file__)
        base_dir = os.path.dirname(current_file)
        logo_path = os.path.join(base_dir, "static", "logo.png")
        
        # Normalize the path (handles any path issues)
        logo_path = os.path.normpath(logo_path)
        
        if os.path.exists(logo_path) and os.path.isfile(logo_path):
            try:
                # Try loading with PIL first to validate the image
                from PIL import Image
                img = Image.open(logo_path)
                st.image(img, use_container_width=True)
            except ImportError:
                # If PIL not available, try direct path
                try:
                    st.image(logo_path, use_container_width=True)
                except Exception:
                    # If that fails, try using base64 encoding
                    try:
                        import base64
                        with open(logo_path, "rb") as f:
                            img_data = base64.b64encode(f.read()).decode()
                            st.markdown(f'<img src="data:image/png;base64,{img_data}" style="max-width: 100%; height: auto;" />', unsafe_allow_html=True)
                    except Exception:
                        st.markdown("<div style='height: 100px; background: #f0f0f0; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #999;'>LIPG Logo</div>", unsafe_allow_html=True)
            except Exception as img_error:
                # If image fails to load, try base64 encoding as fallback
                try:
                    import base64
                    with open(logo_path, "rb") as f:
                        img_data = base64.b64encode(f.read()).decode()
                        st.markdown(f'<img src="data:image/png;base64,{img_data}" style="max-width: 100%; height: auto;" />', unsafe_allow_html=True)
                except Exception:
                    st.markdown("<div style='height: 100px; background: #f0f0f0; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #999;'>LIPG Logo</div>", unsafe_allow_html=True)
        else:
            # Logo file not found
            st.markdown("<div style='height: 100px; background: #f0f0f0; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #999;'>LIPG Logo</div>", unsafe_allow_html=True)
    except Exception as e:
        # Show placeholder if logo can't be loaded
        st.markdown("<div style='height: 100px; background: #f0f0f0; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #999;'>LIPG Logo</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # User Manual in sidebar
    with st.expander("📖 User Manual", expanded=False):
        st.markdown("""
        **Getting Started:**
        1. Enter the **topic** of your LinkedIn post
        2. Specify the **purpose** - what do you want to achieve?
        3. Select your **target audience**
        4. Enter the **key message** - the main point
        5. Choose **tone intensity** and **language style**
        6. Pick the **post length** and **formatting style**
        7. (Optional) Add a **call-to-action**
        8. Select the **post goal**
        9. Click **"Generate Post"** to create your post!
        
        **Tips:**
        - Be specific in your topic and message
        - Choose the right audience for better results
        - Experiment with different tones and styles
        - Use the post history to review past posts
        """)
    
    st.divider()
    
    st.header("👤 User Info")
    st.success(f"Logged in as: **{st.session_state.username}**")
    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.generated_post = ""
        st.session_state.visual_prompt = ""
        st.rerun()
    
    st.divider()
    st.header("📊 Quick Actions")
    if st.button("📜 View Post History"):
        st.session_state.show_history = True
    
    if st.button("🔄 Reset Form"):
        st.session_state.generated_post = ""
        st.session_state.visual_prompt = ""
        st.session_state.generating = False
        st.session_state.form_reset = True
        st.session_state.reset_key = str(datetime.now().timestamp())
        st.rerun()

# Main form
col1, col2 = st.columns([1, 1])

# Get reset key for form fields - changes on reset to clear all fields
reset_key = st.session_state.get('reset_key', '0')

with col1:
    st.header("📝 Post Details")
    
    topic = st.text_input(
        "Topic *",
        placeholder="e.g., AI in Healthcare",
        help="The main subject of your LinkedIn post",
        key=f"topic_{reset_key}"
    )
    
    purpose = st.text_area(
        "Purpose *",
        placeholder="e.g., To inform professionals about AI applications in healthcare",
        help="What do you want to achieve with this post?",
        key=f"purpose_{reset_key}"
    )
    
    audience = st.selectbox(
        "Target Audience",
        ["General", "Professionals", "Executives", "Entrepreneurs", "Students", "Industry Experts"],
        index=0,
        help="Who is your target audience?",
        key=f"audience_{reset_key}"
    )
    
    message = st.text_area(
        "Key Message *",
        placeholder="e.g., AI is transforming healthcare delivery",
        help="The main message you want to convey",
        key=f"message_{reset_key}"
    )
    
    post_goal = st.selectbox(
        "Post Goal",
        ["Educate", "Engage", "Promote", "Inspire", "Inform", "Motivate", "Entertain", "Network", "Advocate"],
        index=0,
        help="What is the primary goal of this post?",
        key=f"post_goal_{reset_key}"
    )

with col2:
    st.header("🎨 Style & Format")
    
    template_type = st.selectbox(
        "Template Type",
        options=list(get_all_templates().keys()),
        format_func=lambda x: get_template(x)['name'],
        index=0,
        help="Choose a post template style",
        key=f"template_{reset_key}"
    )
    
    tone_intensity = st.selectbox(
        "Tone Intensity",
        ["Very Light", "Light", "Moderate", "Strong", "Very Strong"],
        index=2,
        help="How intense should the tone be?",
        key=f"tone_{reset_key}"
    )
    
    language_style = st.selectbox(
        "Language Style",
        ["Professional", "Casual", "Formal", "Conversational", "Technical", "Friendly"],
        index=0,
        help="The style of language to use",
        key=f"language_{reset_key}"
    )
    
    post_length = st.selectbox(
        "Post Length",
        ["Very Short", "Short", "Medium", "Long", "Very Long"],
        index=2,
        help="How long should the post be?",
        key=f"length_{reset_key}"
    )
    
    formatting = st.selectbox(
        "Formatting Style",
        ["Bullet Points", "Numbered List", "Paragraphs", "Mixed Format", "Question & Answer"],
        index=0,
        help="How should the post be structured?",
        key=f"formatting_{reset_key}"
    )
    
    visual_style = st.selectbox(
        "Visual Style",
        ["photo_realistic", "illustration", "minimalist", "infographic", "abstract", "vintage", "modern_flat", "3d_render"],
        format_func=lambda x: x.replace("_", " ").title(),
        index=0,
        help="Style for the visual prompt (for image generation)",
        key=f"visual_{reset_key}"
    )
    
    cta = st.text_input(
        "Call-to-Action (Optional)",
        placeholder="e.g., What are your thoughts?",
        help="Optional call-to-action for your post",
        key=f"cta_{reset_key}"
    )

# Generate button
st.divider()
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
with col_btn2:
    generate_button = st.button("🚀 Generate Post", type="primary", use_container_width=True, disabled=st.session_state.generating)

# Generate post - use request ID to prevent duplicate processing
if generate_button and not st.session_state.generating:
    # Create a unique request ID based on inputs and timestamp
    request_data = f"{topic}|{purpose}|{message}|{audience}|{post_goal}|{template_type}|{datetime.now().isoformat()}"
    request_id = hashlib.md5(request_data.encode()).hexdigest()
    
    # Only process if this is a new request (not already processed)
    if st.session_state.last_generation_request != request_id:
        st.session_state.last_generation_request = request_id
        st.session_state.generating = True
        
        if not topic or not purpose or not message:
            st.error("⚠️ Please fill in all required fields (marked with *)")
            st.session_state.generating = False
        else:
            with st.spinner("✨ Generating your LinkedIn post..."):
                try:
                    post, visual_prompt = generate_ai_post(
                        topic=topic,
                        purpose=purpose,
                        audience=audience,
                        message=message,
                        tone_intensity=tone_intensity,
                        language_style=language_style,
                        post_length=post_length,
                        formatting=formatting,
                        cta=cta,
                        post_goal=post_goal,
                        template_type=template_type,
                        visual_style=visual_style
                    )
                    
                    if post.startswith("⚠️"):
                        st.error(post)
                        st.session_state.generating = False
                    else:
                        st.session_state.generated_post = post
                        st.session_state.visual_prompt = visual_prompt
                        st.session_state.generating = False
                        
                        # Save to database
                        if st.session_state.username:
                            save_post_to_database(
                                user_id=st.session_state.username,
                                topic=topic,
                                purpose=purpose,
                                audience=audience,
                                message=message,
                                tone_intensity=tone_intensity,
                                language_style=language_style,
                                post_length=post_length,
                                formatting=formatting,
                                cta=cta,
                                post_goal=post_goal,
                                generated_post=post
                            )
                        
                        st.success("✅ Post generated successfully!")
                        
                except Exception as e:
                    st.error(f"❌ Error generating post: {str(e)}")
                    st.session_state.generating = False

# Display generated post
if st.session_state.generated_post:
    st.divider()
    st.header("📄 Generated Post")
    
    post_container = st.container()
    with post_container:
        # Display post with proper line breaks preserved
        post_text = st.session_state.generated_post
        
        # Display the post with proper formatting (preserves line breaks)
        st.markdown(f"""
            <div class="post-container" style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #ddd; margin: 20px 0;">
                <h3 style="color: #0077b5; margin-bottom: 15px;">Your LinkedIn Post:</h3>
                <div style="white-space: pre-wrap; font-size: 16px; line-height: 1.8; color: #333; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">{html.escape(post_text)}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Action buttons
        st.markdown("<br>", unsafe_allow_html=True)
        col_copy1, col_copy2, col_copy3, col_copy4 = st.columns([1, 1, 1, 1])
        
        with col_copy2:
            # Copy to clipboard - use a text area that users can easily select and copy
            st.markdown("**Copy Post:**")
            st.text_area(
                "Select all text and copy (Ctrl+A, Ctrl+C)",
                value=post_text,
                height=150,
                key="copy_post_area",
                label_visibility="collapsed"
            )
        
        with col_copy3:
            # Download HTML button
            # Escape HTML entities in post text
            escaped_post_text = html.escape(post_text)
            
            # Create nicely formatted HTML
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LinkedIn Post - {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            background-color: #f5f5f5;
            line-height: 1.6;
        }}
        .post-container {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #0077b5;
        }}
        .post-title {{
            color: #0077b5;
            font-size: 24px;
            margin-bottom: 20px;
            font-weight: 600;
        }}
        .post-content {{
            white-space: pre-wrap;
            font-size: 16px;
            color: #333;
            line-height: 1.8;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="post-container">
        <div class="post-title">LinkedIn Post</div>
        <div class="post-content">{escaped_post_text}</div>
    </div>
    <div class="footer">
        Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
    </div>
</body>
</html>"""
            
            # Create download button
            b64_html = base64.b64encode(html_content.encode('utf-8')).decode()
            filename = f"linkedin_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            href = f'<a href="data:text/html;charset=utf-8;base64,{b64_html}" download="{filename}" style="text-decoration: none; color: white; background-color: #0077b5; padding: 10px 20px; border-radius: 5px; display: inline-block; font-weight: 500;">📥 Download HTML</a>'
            st.markdown(href, unsafe_allow_html=True)
        
        # Visual prompt section
        if st.session_state.visual_prompt:
            st.divider()
            with st.expander("🎨 Visual Prompt for Image Generation"):
                st.text(st.session_state.visual_prompt)
                st.info("💡 Use this prompt with an image generation tool like DALL-E or Midjourney")

# Post history
if st.session_state.get('show_history', False):
    st.divider()
    st.header("📜 Post History")
    
    if st.session_state.username:
        try:
            history = get_user_post_history(st.session_state.username)
            if history:
                for idx, post_data in enumerate(history[:10]):  # Show last 10 posts
                    with st.expander(f"Post #{idx+1} - {post_data.get('topic', 'N/A')} ({post_data.get('date', 'N/A')})"):
                        st.write(f"**Topic:** {post_data.get('topic', 'N/A')}")
                        st.write(f"**Purpose:** {post_data.get('purpose', 'N/A')}")
                        st.write(f"**Generated Post:**")
                        
                        post_text_history = post_data.get('generated_post', 'N/A')
                        st.text(post_text_history)
                        
                        # Download HTML button for this post
                        if post_text_history != 'N/A':
                            escaped_post_text = html.escape(post_text_history)
                            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LinkedIn Post - {post_data.get('date', 'N/A')}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            background-color: #f5f5f5;
            line-height: 1.6;
        }}
        .post-container {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #0077b5;
        }}
        .post-title {{
            color: #0077b5;
            font-size: 24px;
            margin-bottom: 20px;
            font-weight: 600;
        }}
        .post-meta {{
            color: #666;
            font-size: 14px;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #ddd;
        }}
        .post-content {{
            white-space: pre-wrap;
            font-size: 16px;
            color: #333;
            line-height: 1.8;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="post-container">
        <div class="post-title">LinkedIn Post</div>
        <div class="post-meta">
            <strong>Topic:</strong> {html.escape(str(post_data.get('topic', 'N/A')))}<br>
            <strong>Purpose:</strong> {html.escape(str(post_data.get('purpose', 'N/A')))}<br>
            <strong>Date:</strong> {html.escape(str(post_data.get('date', 'N/A')))}
        </div>
        <div class="post-content">{escaped_post_text}</div>
    </div>
    <div class="footer">
        Generated on {post_data.get('date', 'N/A')}
    </div>
</body>
</html>"""
                            
                            b64_html = base64.b64encode(html_content.encode('utf-8')).decode()
                            filename = f"linkedin_post_{post_data.get('date', 'N/A').replace('/', '_').replace(' ', '_')}.html"
                            href = f'<a href="data:text/html;charset=utf-8;base64,{b64_html}" download="{filename}" style="text-decoration: none; color: white; background-color: #0077b5; padding: 8px 16px; border-radius: 5px; display: inline-block; font-weight: 500; margin-top: 10px;">📥 Download HTML</a>'
                            st.markdown(href, unsafe_allow_html=True)
            else:
                st.info("No post history found.")
        except Exception as e:
            st.error(f"Error loading history: {str(e)}")
    
    if st.button("Close History"):
        st.session_state.show_history = False

# Footer
st.divider()
st.markdown("---")
st.markdown(f"<div style='text-align: center; color: #666;'>© {datetime.now().year} {customer_name} - LinkedIn Post Generator</div>", unsafe_allow_html=True)

