"""
LinkedIn Post Generator - Admin App
Streamlit-based admin dashboard for managing users, posts, and analytics
"""

import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime, timedelta
import json

# Ensure we can import from shared_utils when app is at repo root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared_utils.data_manager import (
    get_all_posts, 
    get_user_stats, 
    get_all_users,
    delete_post,
    get_analytics_data
)
from shared_utils.config_loader import load_customer_config, save_customer_config

# Page configuration
st.set_page_config(
    page_title="Admin Dashboard - LinkedIn Post Generator",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Admin authentication (simple - in production, use proper auth)
if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False

# Simple password check (in production, use proper authentication)
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')  # Change in production

# Authentication
if not st.session_state.admin_authenticated:
    st.title("🔐 Admin Login")
    password = st.text_input("Enter Admin Password", type="password")
    if st.button("Login"):
        if password == ADMIN_PASSWORD:
            st.session_state.admin_authenticated = True
            st.rerun()
        else:
            st.error("❌ Incorrect password")
    st.stop()

# Load customer configuration
try:
    customer_config = load_customer_config()
    customer_name = customer_config.get('customer_name', 'LinkedIn Post Generator')
    button_color = customer_config.get('button_color', '#17A2B8')
except Exception as e:
    customer_name = "LinkedIn Post Generator"
    button_color = '#17A2B8'

# Get logo path
_base_dir = os.path.dirname(os.path.abspath(__file__))
_logo_path = os.path.join(_base_dir, "static", "logo.png")
_logo_exists = os.path.exists(_logo_path)

# Custom CSS for Admin
st.markdown(f"""
    <style>
        .stButton > button {{
            background-color: {button_color};
            color: white;
            border-radius: 5px;
            font-weight: 600;
        }}
        .admin-header {{
            display: flex;
            align-items: center;
            gap: 20px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            margin-bottom: 20px;
            color: white;
        }}
        .admin-header-logo {{
            max-height: 80px;
            max-width: 150px;
        }}
        .admin-header-text h1 {{
            margin: 0;
            color: white;
        }}
        .admin-header-text p {{
            margin: 5px 0 0 0;
            color: rgba(255,255,255,0.9);
        }}
        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid {button_color};
        }}
    </style>
""", unsafe_allow_html=True)

# Header with Logo
if _logo_exists:
    try:
        col_logo, col_text = st.columns([1, 4])
        with col_logo:
            st.image(_logo_path, use_container_width=True)
        with col_text:
            st.markdown(f"""
                <div class="admin-header-text">
                    <h1>⚙️ Admin Dashboard - {customer_name}</h1>
                    <p>Manage users, posts, and view analytics</p>
                </div>
            """, unsafe_allow_html=True)
    except Exception:
        # Fallback if logo fails to load
        st.markdown(f"""
            <div class="admin-header">
                <div class="admin-header-text">
                    <h1>⚙️ Admin Dashboard - {customer_name}</h1>
                    <p>Manage users, posts, and view analytics</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div class="admin-header">
            <div class="admin-header-text">
                <h1>⚙️ Admin Dashboard - {customer_name}</h1>
                <p>Manage users, posts, and view analytics</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio(
    "Select Page",
    ["Dashboard", "User Management", "Post Management", "Analytics", "Configuration"]
)

# Dashboard Overview
if page == "Dashboard":
    st.header("📊 Dashboard Overview")
    
    try:
        # Get statistics
        stats = get_user_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Users", stats.get('total_users', 0))
        
        with col2:
            st.metric("Total Posts", stats.get('total_posts', 0))
        
        with col3:
            st.metric("Posts Today", stats.get('posts_today', 0))
        
        with col4:
            st.metric("Posts This Week", stats.get('posts_week', 0))
        
        # Recent activity
        st.subheader("📈 Recent Activity")
        try:
            recent_posts = get_all_posts(limit=10)
            if recent_posts:
                df_recent = pd.DataFrame(recent_posts)
                st.dataframe(df_recent[['date', 'user_id', 'topic', 'post_goal']], use_container_width=True)
            else:
                st.info("No recent posts")
        except Exception as e:
            st.error(f"Error loading recent posts: {str(e)}")
    
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")

# User Management
elif page == "User Management":
    st.header("👥 User Management")
    
    try:
        users = get_all_users()
        
        if users:
            st.subheader("All Users")
            df_users = pd.DataFrame(users)
            
            # User statistics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Users", len(users))
            
            with col2:
                active_users = len([u for u in users if u.get('post_count', 0) > 0])
                st.metric("Active Users", active_users)
            
            # Display users table
            st.dataframe(df_users, use_container_width=True)
            
            # User actions
            st.subheader("User Actions")
            selected_user = st.selectbox("Select User", [u['user_id'] for u in users])
            
            if selected_user:
                user_stats = get_user_stats(user_id=selected_user)
                st.json(user_stats)
        else:
            st.info("No users found")
    
    except Exception as e:
        st.error(f"Error loading users: {str(e)}")

# Post Management
elif page == "Post Management":
    st.header("📝 Post Management")
    
    try:
        all_posts = get_all_posts()
        
        if all_posts:
            st.subheader(f"All Posts ({len(all_posts)})")
            
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                filter_user = st.selectbox("Filter by User", ["All"] + list(set([p.get('user_id', 'Unknown') for p in all_posts])))
            with col2:
                filter_goal = st.selectbox("Filter by Goal", ["All"] + list(set([p.get('post_goal', 'Unknown') for p in all_posts])))
            with col3:
                date_range = st.selectbox("Date Range", ["All Time", "Last 7 Days", "Last 30 Days"])
            
            # Apply filters
            filtered_posts = all_posts
            if filter_user != "All":
                filtered_posts = [p for p in filtered_posts if p.get('user_id') == filter_user]
            if filter_goal != "All":
                filtered_posts = [p for p in filtered_posts if p.get('post_goal') == filter_goal]
            if date_range != "All Time":
                cutoff_date = datetime.now() - timedelta(days=7 if date_range == "Last 7 Days" else 30)
                filtered_posts = [p for p in filtered_posts if datetime.fromisoformat(p.get('date', '2000-01-01')) > cutoff_date]
            
            # Display filtered posts
            if filtered_posts:
                df_posts = pd.DataFrame(filtered_posts)
                st.dataframe(df_posts[['date', 'user_id', 'topic', 'post_goal', 'post_length']], use_container_width=True)
                
                # Post details
                st.subheader("Post Details")
                selected_idx = st.number_input("Select Post Index", min_value=0, max_value=len(filtered_posts)-1, value=0)
                
                if 0 <= selected_idx < len(filtered_posts):
                    selected_post = filtered_posts[selected_idx]
                    st.json(selected_post)
                    
                    # Delete option
                    if st.button("🗑️ Delete Post", type="secondary"):
                        try:
                            delete_post(selected_post.get('id'))
                            st.success("Post deleted successfully")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting post: {str(e)}")
            else:
                st.info("No posts match the filters")
        else:
            st.info("No posts found")
    
    except Exception as e:
        st.error(f"Error loading posts: {str(e)}")

# Analytics
elif page == "Analytics":
    st.header("📊 Analytics")
    
    try:
        analytics = get_analytics_data()
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Posts by Goal")
            if 'posts_by_goal' in analytics:
                goal_data = analytics['posts_by_goal']
                st.bar_chart(goal_data)
        
        with col2:
            st.subheader("Posts by Length")
            if 'posts_by_length' in analytics:
                length_data = analytics['posts_by_length']
                st.bar_chart(length_data)
        
        # Time series
        st.subheader("Posts Over Time")
        if 'posts_over_time' in analytics:
            time_data = pd.DataFrame(analytics['posts_by_length'])
            st.line_chart(time_data)
        
        # Template usage
        st.subheader("Template Usage")
        if 'template_usage' in analytics:
            template_data = analytics['template_usage']
            st.bar_chart(template_data)
        
        # Export data
        st.subheader("Export Data")
        if st.button("📥 Download Analytics CSV"):
            try:
                df_analytics = pd.DataFrame(analytics.get('all_posts', []))
                csv = df_analytics.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"analytics_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Error exporting data: {str(e)}")
    
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")

# Configuration
elif page == "Configuration":
    st.header("⚙️ Configuration")
    
    try:
        config = load_customer_config()
        
        st.subheader("Customer Configuration")
        
        customer_name = st.text_input("Customer Name", value=config.get('customer_name', ''))
        background_color = st.color_picker("Background Color", value=config.get('background_color', '#E9F7EF'))
        button_color = st.color_picker("Button Color", value=config.get('button_color', '#17A2B8'))
        
        if st.button("💾 Save Configuration"):
            new_config = {
                'customer_name': customer_name,
                'background_color': background_color,
                'button_color': button_color
            }
            try:
                save_customer_config(new_config)
                st.success("✅ Configuration saved successfully!")
            except Exception as e:
                st.error(f"Error saving configuration: {str(e)}")
        
        st.divider()
        st.subheader("OpenAI API Configuration")
        st.info("Configure API key in environment variables or .env file")
        st.code("OPENAI_API_KEY=your-api-key-here")
        
        st.divider()
        st.subheader("Current Configuration")
        st.json(config)
    
    except Exception as e:
        st.error(f"Error loading configuration: {str(e)}")

# Logout
st.sidebar.divider()
if st.sidebar.button("🚪 Logout"):
    st.session_state.admin_authenticated = False
    st.rerun()

