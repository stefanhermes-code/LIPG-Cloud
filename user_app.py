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
                    <h1>💼 {customer_name}</h1>
                    <h2>LinkedIn Post Generator</h2>
                </div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div class="header-container">
            <div class="header-text">
                <h1>💼 {customer_name}</h1>
                <h2>LinkedIn Post Generator</h2>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Instructions section
with st.expander("📖 How to Use - Step-by-Step Instructions", expanded=False):
    st.markdown(f"""
        <div class="instructions-box">
            <h3>Getting Started</h3>
            <ol>
                <li><strong>Enter the topic</strong> of your LinkedIn post (what you want to write about)</li>
                <li><strong>Specify the purpose</strong> - what do you want to achieve with this post?</li>
                <li><strong>Select your target audience</strong> from the dropdown menu</li>
                <li><strong>Enter the key message</strong> - the main point you want to convey</li>
                <li><strong>Choose the tone intensity</strong> - how strong should the tone be?</li>
                <li><strong>Select the language style</strong> - professional, casual, technical, etc.</li>
                <li><strong>Pick the post length</strong> - from very short to very long</li>
                <li><strong>Choose the formatting style</strong> - bullet points, paragraphs, numbered lists, etc.</li>
                <li><strong>Optional:</strong> Add a call-to-action to encourage engagement</li>
                <li><strong>Select the post goal</strong> - educate, engage, promote, inspire, etc.</li>
                <li><strong>Click "Generate Post"</strong> and your AI-powered LinkedIn post will be created!</li>
            </ol>
        </div>
    """, unsafe_allow_html=True)
    
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

# Main form
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 Post Details")
    
    topic = st.text_input(
        "Topic *",
        placeholder="e.g., AI in Healthcare",
        help="The main subject of your LinkedIn post"
    )
    
    purpose = st.text_area(
        "Purpose *",
        placeholder="e.g., To inform professionals about AI applications in healthcare",
        help="What do you want to achieve with this post?"
    )
    
    audience = st.selectbox(
        "Target Audience",
        ["General", "Professionals", "Executives", "Entrepreneurs", "Students", "Industry Experts"],
        help="Who is your target audience?"
    )
    
    message = st.text_area(
        "Key Message *",
        placeholder="e.g., AI is transforming healthcare delivery",
        help="The main message you want to convey"
    )
    
    post_goal = st.selectbox(
        "Post Goal",
        ["Educate", "Engage", "Promote", "Inspire", "Inform", "Motivate", "Entertain", "Network", "Advocate"],
        help="What is the primary goal of this post?"
    )

with col2:
    st.header("🎨 Style & Format")
    
    template_type = st.selectbox(
        "Template Type",
        options=list(get_all_templates().keys()),
        format_func=lambda x: get_template(x)['name'],
        help="Choose a post template style"
    )
    
    tone_intensity = st.selectbox(
        "Tone Intensity",
        ["Very Light", "Light", "Moderate", "Strong", "Very Strong"],
        index=2,
        help="How intense should the tone be?"
    )
    
    language_style = st.selectbox(
        "Language Style",
        ["Professional", "Casual", "Formal", "Conversational", "Technical", "Friendly"],
        help="The style of language to use"
    )
    
    post_length = st.selectbox(
        "Post Length",
        ["Very Short", "Short", "Medium", "Long", "Very Long"],
        index=2,
        help="How long should the post be?"
    )
    
    formatting = st.selectbox(
        "Formatting Style",
        ["Bullet Points", "Numbered List", "Paragraphs", "Mixed Format", "Question & Answer"],
        help="How should the post be structured?"
    )
    
    visual_style = st.selectbox(
        "Visual Style",
        ["photo_realistic", "illustration", "minimalist", "infographic", "abstract", "vintage", "modern_flat", "3d_render"],
        format_func=lambda x: x.replace("_", " ").title(),
        help="Style for the visual prompt (for image generation)"
    )
    
    cta = st.text_input(
        "Call-to-Action (Optional)",
        placeholder="e.g., What are your thoughts?",
        help="Optional call-to-action for your post"
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
        st.markdown(f"""
            <div class="post-container">
                <h3>Your LinkedIn Post:</h3>
                <p style="white-space: pre-wrap; font-size: 16px;">{st.session_state.generated_post}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Copy button
        st.code(st.session_state.generated_post, language=None)
        
        col_copy1, col_copy2, col_copy3 = st.columns([1, 1, 1])
        with col_copy2:
            if st.button("📋 Copy to Clipboard", use_container_width=True):
                st.write("Post copied! (Use Ctrl+C to copy from the code block above)")
        
        # Visual prompt section
        if st.session_state.visual_prompt:
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
                        st.text(post_data.get('generated_post', 'N/A'))
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

