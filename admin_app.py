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
    get_analytics_data,
    get_all_auth_users,
    create_user,
    delete_user,
    enable_disable_user,
    update_user_password,
    update_user_tier,
    update_user_role,
    update_user_company,
    get_user,
    create_company,
    get_company,
    get_all_companies,
    update_company_subscription,
    enable_disable_company,
    delete_company,
    get_company_users,
    is_subscription_active
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
    # Get customer-specific logo path from config, or use default
    configured_logo_path = customer_config.get('logo_path', 'static/logo.png')
except Exception as e:
    customer_name = "LinkedIn Post Generator"
    button_color = '#17A2B8'
    configured_logo_path = 'static/logo.png'

# Get logo path - use customer-specific logo if configured, otherwise default
_base_dir = os.path.dirname(os.path.abspath(__file__))
_logo_path = os.path.join(_base_dir, configured_logo_path)
_logo_exists = os.path.exists(_logo_path)

# If customer logo doesn't exist, try default logo as fallback
if not _logo_exists and configured_logo_path != 'static/logo.png':
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
    ["Dashboard", "Company Management", "User Management", "Post Management", "Analytics", "Configuration"]
)

# Dashboard Overview
if page == "Dashboard":
    st.header("📊 Dashboard Overview")
    
    try:
        # Get statistics
        stats = get_user_stats()  # Now uses auth.json, so total_users is correct
        
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

# Company Management
elif page == "Company Management":
    st.header("🏢 Company Management")
    
    # Tabs for different company management actions
    tab1, tab2, tab3 = st.tabs(["View Companies", "Add New Company", "Manage Existing Company"])
    
    with tab1:
        st.subheader("All Companies")
        try:
            companies = get_all_companies()
            
            if companies:
                # Statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Companies", len(companies))
                with col2:
                    active_subs = len([c for c in companies if is_subscription_active(c.get('id'))])
                    st.metric("Active Subscriptions", active_subs)
                with col3:
                    monthly_count = len([c for c in companies if c.get('subscription_type') == 'monthly'])
                    st.metric("Monthly Plans", monthly_count)
                with col4:
                    annual_count = len([c for c in companies if c.get('subscription_type') == 'annual'])
                    st.metric("Annual Plans", annual_count)
                
                # Display companies table
                df_companies = pd.DataFrame(companies)
                # Format dates
                if 'start_date' in df_companies.columns:
                    df_companies['start_date'] = pd.to_datetime(df_companies['start_date']).dt.strftime('%Y-%m-%d')
                if 'expiration_date' in df_companies.columns:
                    df_companies['expiration_date'] = pd.to_datetime(df_companies['expiration_date']).dt.strftime('%Y-%m-%d')
                if 'created_date' in df_companies.columns:
                    df_companies['created_date'] = pd.to_datetime(df_companies['created_date']).dt.strftime('%Y-%m-%d')
                
                # Add subscription status
                df_companies['subscription_status'] = df_companies['id'].apply(
                    lambda x: '✅ Active' if is_subscription_active(x) else '❌ Expired'
                )
                
                st.dataframe(df_companies, use_container_width=True)
            else:
                st.info("No companies found. Create your first company in the 'Add New Company' tab.")
        except Exception as e:
            st.error(f"Error loading companies: {str(e)}")
    
    with tab2:
        st.subheader("➕ Add New Company")
        
        # Clear any previous success messages when entering this tab
        if 'company_created' in st.session_state:
            if st.session_state.company_created:
                # Show success message once, then clear
                company_id = st.session_state.get('company_created_id', '')
                st.success(f"✅ Company created successfully! Company ID: {company_id}")
                st.session_state.company_created = False
                st.session_state.company_created_id = ""
                # Clear form fields by resetting form state
                if 'company_form_cleared' not in st.session_state:
                    st.session_state.company_form_cleared = True
        
        # Use form with clear_on_submit to clear fields after successful submission
        with st.form("add_company_form", clear_on_submit=True):
            company_name = st.text_input("Company Name *", help="Name of the company", value="")
            subscription_type = st.selectbox("Subscription Type *", ["monthly", "annual"], index=0)
            
            # Calculate default expiration based on subscription type
            default_expiration = (datetime.now() + timedelta(days=30)).date() if subscription_type == "monthly" else (datetime.now() + timedelta(days=365)).date()
            
            start_date = st.date_input("Start Date", value=datetime.now().date())
            expiration_date = st.date_input("Expiration Date", value=default_expiration)
            
            submitted = st.form_submit_button("Create Company", type="primary", use_container_width=True)
            
            if submitted:
                # Only process if form was actually submitted (button clicked)
                if company_name:
                    success, company_id = create_company(
                        company_name, 
                        subscription_type, 
                        start_date.isoformat(), 
                        expiration_date.isoformat()
                    )
                    if success:
                        st.session_state.company_created = True
                        st.session_state.company_created_id = company_id
                        # Don't rerun here - let clear_on_submit handle clearing the form
                        # The success message will show on next rerun (when user interacts)
                    else:
                        st.error(f"❌ Error: {company_id}")
                else:
                    st.error("⚠️ Company name is required")
        
        # Success message is shown in the form above
    
    with tab3:
        st.subheader("⚙️ Manage Existing Company")
        try:
            companies = get_all_companies()
            if companies:
                # Clear confirmation state if company was deleted
                if 'confirm_delete_company' in st.session_state:
                    # Check if the confirmed company still exists
                    confirmed_id = st.session_state.confirm_delete_company
                    if confirmed_id and not any(c['id'] == confirmed_id for c in companies):
                        # Company was deleted, clear confirmation state
                        st.session_state.confirm_delete_company = None
                
                selected_company_id = st.selectbox("Select Company", 
                                                   [c['id'] for c in companies],
                                                   format_func=lambda x: f"{x} - {next((c['name'] for c in companies if c['id'] == x), 'Unknown')}")
                
                if selected_company_id:
                    company_info = get_company(selected_company_id)
                    if company_info:
                        st.write(f"**Company ID:** {company_info.get('id')}")
                        st.write(f"**Company Name:** {company_info.get('name')}")
                        st.write(f"**Subscription Type:** {company_info.get('subscription_type', 'monthly').title()}")
                        st.write(f"**Start Date:** {company_info.get('start_date', 'N/A')}")
                        st.write(f"**Expiration Date:** {company_info.get('expiration_date', 'N/A')}")
                        st.write(f"**Status:** {'✅ Active' if is_subscription_active(selected_company_id) else '❌ Expired'}")
                        st.write(f"**Enabled:** {'✅ Yes' if company_info.get('enabled', True) else '❌ No'}")
                        
                        st.divider()
                        st.subheader("Company Branding")
                        st.write("💡 Company-specific branding will override global branding for users in this company.")
                        
                        # Use form to prevent flashing/reruns on every input change
                        with st.form(f"branding_form_{selected_company_id}", clear_on_submit=False):
                            # Logo upload section
                            st.write("**Company Logo:**")
                            col_upload, col_preview = st.columns([2, 1])
                            
                            with col_upload:
                                uploaded_logo = st.file_uploader(
                                    "Upload Company Logo",
                                    type=['png', 'jpg', 'jpeg', 'gif', 'svg'],
                                    help="Upload a logo image file (PNG, JPG, GIF, or SVG). Recommended size: max 200px width, 100px height.",
                                    key=f"logo_upload_{selected_company_id}"
                                )
                                
                                # Manual path input (fallback)
                                st.caption("Or enter logo path manually:")
                                company_logo = st.text_input("Logo Path", 
                                                            value=company_info.get('logo_path', '') or '',
                                                            help="Path to company logo (e.g., 'static/htc_logo.png'). Leave empty to use global logo.",
                                                            key=f"company_logo_{selected_company_id}")
                            
                            with col_preview:
                                # Show current logo if exists
                                current_logo_path = company_info.get('logo_path')
                                if current_logo_path:
                                    _base_dir = os.path.dirname(os.path.abspath(__file__))
                                    _test_logo_path = os.path.join(_base_dir, current_logo_path)
                                    if os.path.exists(_test_logo_path):
                                        try:
                                            st.write("**Current Logo:**")
                                            st.image(_test_logo_path, width=150)
                                        except Exception:
                                            st.info("Logo file exists but cannot be displayed")
                                
                                # Show preview of uploaded logo
                                if uploaded_logo:
                                    st.write("**Preview:**")
                                    st.image(uploaded_logo, width=150)
                            
                            # Colors - use session state to prevent reruns
                            bg_key = f"company_bg_{selected_company_id}"
                            btn_key = f"company_btn_{selected_company_id}"
                            
                            # Initialize session state if not exists
                            if bg_key not in st.session_state:
                                st.session_state[bg_key] = company_info.get('background_color') or '#E9F7EF'
                            if btn_key not in st.session_state:
                                st.session_state[btn_key] = company_info.get('button_color') or '#17A2B8'
                            
                            company_bg = st.color_picker("Background Color", 
                                                         value=st.session_state[bg_key],
                                                         help="Company-specific background color. Leave as default to use global color.",
                                                         key=f"company_bg_picker_{selected_company_id}")
                            company_btn = st.color_picker("Button Color", 
                                                          value=st.session_state[btn_key],
                                                          help="Company-specific button color. Leave as default to use global color.",
                                                          key=f"company_btn_picker_{selected_company_id}")
                            
                            submitted = st.form_submit_button("💾 Save Branding", use_container_width=True)
                            
                            if submitted:
                                # Handle logo upload
                                final_logo_path = company_logo  # Default to manual path
                                
                                if uploaded_logo:
                                    # Save uploaded file
                                    try:
                                        _base_dir = os.path.dirname(os.path.abspath(__file__))
                                        static_dir = os.path.join(_base_dir, "static")
                                        os.makedirs(static_dir, exist_ok=True)
                                        
                                        # Generate filename based on company ID and original filename
                                        file_ext = os.path.splitext(uploaded_logo.name)[1].lower()
                                        logo_filename = f"company_{selected_company_id}_logo{file_ext}"
                                        logo_path = os.path.join(static_dir, logo_filename)
                                        
                                        # Save the file
                                        with open(logo_path, "wb") as f:
                                            f.write(uploaded_logo.getbuffer())
                                        
                                        # Set the relative path
                                        final_logo_path = f"static/{logo_filename}"
                                        
                                        # Sync logo file to GitHub
                                        from shared_utils.data_manager import sync_logo_to_github
                                        sync_success = sync_logo_to_github(logo_path)
                                        if sync_success:
                                            st.success(f"✅ Logo saved and synced to GitHub: {final_logo_path}")
                                        else:
                                            st.warning(f"⚠️ Logo saved to: {final_logo_path}, but GitHub sync failed. Please commit manually.")
                                            st.info("💡 For Streamlit Cloud, the logo file must be in GitHub. You may need to commit it manually.")
                                    except Exception as e:
                                        st.error(f"❌ Error uploading logo: {str(e)}")
                                        final_logo_path = company_logo  # Fall back to manual path
                                
                                # Update company with branding
                                companies = get_all_companies()
                                for company in companies:
                                    if company.get('id') == selected_company_id:
                                        company['logo_path'] = final_logo_path if final_logo_path else None
                                        company['background_color'] = company_bg if company_bg != '#E9F7EF' else None
                                        company['button_color'] = company_btn if company_btn != '#17A2B8' else None
                                        # Save companies
                                        from shared_utils.data_manager import _load_json_file, _save_json_file, COMPANIES_FILE
                                        _save_json_file(COMPANIES_FILE, companies)
                                        
                                        # Update session state
                                        st.session_state[bg_key] = company_bg
                                        st.session_state[btn_key] = company_btn
                                
                                st.success("✅ Company branding updated!")
                                st.rerun()
                        
                        # Show company users
                        st.divider()
                        st.subheader("Company Users")
                        company_users = get_company_users(selected_company_id)
                        if company_users:
                            df_users = pd.DataFrame(company_users)
                            # Only select columns that exist in the DataFrame
                            available_columns = df_users.columns.tolist()
                            display_columns = ['username', 'email', 'tier', 'role', 'enabled']
                            columns_to_show = [col for col in display_columns if col in available_columns]
                            if columns_to_show:
                                st.dataframe(df_users[columns_to_show], use_container_width=True)
                            else:
                                st.dataframe(df_users, use_container_width=True)
                        else:
                            st.info("No users assigned to this company")
                        
                        st.divider()
                        
                        # Actions
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            if company_info.get('enabled', True):
                                if st.button("🚫 Disable Company", type="secondary"):
                                    success, message = enable_disable_company(selected_company_id, False)
                                    if success:
                                        st.success(message)
                                    else:
                                        st.error(message)
                            else:
                                if st.button("✅ Enable Company", type="primary"):
                                    success, message = enable_disable_company(selected_company_id, True)
                                    if success:
                                        st.success(message)
                                    else:
                                        st.error(message)
                        
                        with col2:
                            st.subheader("Update Subscription")
                            # Use form to prevent reruns on every input change
                            with st.form(f"subscription_form_{selected_company_id}"):
                                sub_key = f"sub_type_{selected_company_id}"
                                if sub_key not in st.session_state:
                                    st.session_state[sub_key] = company_info.get('subscription_type', 'monthly')
                                
                                new_sub_type = st.selectbox("Subscription Type", ["monthly", "annual"],
                                                           index=0 if st.session_state[sub_key] == 'monthly' else 1,
                                                           key=f"sub_select_{selected_company_id}")
                                
                                start_date_str = company_info.get('start_date', datetime.now().isoformat())
                                if 'T' in start_date_str:
                                    start_date_val = datetime.fromisoformat(start_date_str.split('T')[0]).date()
                                else:
                                    start_date_val = datetime.fromisoformat(start_date_str).date()
                                
                                exp_date_str = company_info.get('expiration_date', datetime.now().isoformat())
                                if 'T' in exp_date_str:
                                    exp_date_val = datetime.fromisoformat(exp_date_str.split('T')[0]).date()
                                else:
                                    exp_date_val = datetime.fromisoformat(exp_date_str).date()
                                
                                new_start = st.date_input("Start Date", value=start_date_val, key=f"start_date_{selected_company_id}")
                                new_expiration = st.date_input("Expiration Date", value=exp_date_val, key=f"exp_date_{selected_company_id}")
                                
                                submitted_sub = st.form_submit_button("Update Subscription", use_container_width=True)
                                
                                if submitted_sub:
                                    if (new_sub_type != company_info.get('subscription_type') or 
                                        new_start.isoformat() != start_date_str.split('T')[0] or
                                        new_expiration.isoformat() != exp_date_str.split('T')[0]):
                                        success, message = update_company_subscription(
                                            selected_company_id, new_sub_type, 
                                            new_start.isoformat(), new_expiration.isoformat()
                                        )
                                        if success:
                                            st.success(message)
                                            st.session_state[sub_key] = new_sub_type
                                            st.rerun()
                                        else:
                                            st.error(message)
                                    else:
                                        st.info("No changes to save")
                        
                        with col3:
                            st.subheader("Delete Company")
                            delete_key = f"delete_company_{selected_company_id}"
                            
                            # Show warning if this company is pending deletion
                            if st.session_state.get('confirm_delete_company') == selected_company_id:
                                st.warning("⚠️ Click the button again to confirm deletion")
                            
                            if st.button("🗑️ Delete Company", type="secondary", key=delete_key):
                                if st.session_state.get('confirm_delete_company') != selected_company_id:
                                    # First click - set confirmation
                                    st.session_state.confirm_delete_company = selected_company_id
                                else:
                                    # Second click - actually delete
                                    success, message = delete_company(selected_company_id)
                                    if success:
                                        # Clear confirmation state
                                        st.session_state.confirm_delete_company = None
                                        st.success(message)
                                    else:
                                        st.error(message)
                                        # Clear confirmation on error too
                                        st.session_state.confirm_delete_company = None
            else:
                st.info("No companies found. Create your first company in the 'Add New Company' tab.")
        except Exception as e:
            st.error(f"Error managing companies: {str(e)}")

# User Management
elif page == "User Management":
    st.header("👥 User Management")
    
    # Tabs for different user management actions
    tab1, tab2, tab3 = st.tabs(["View Users", "Add New User", "Manage Existing User"])
    
    with tab1:
        st.subheader("All Users")
        try:
            users = get_all_auth_users()
            
            if users:
                # Statistics
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                with col1:
                    st.metric("Total Users", len(users))
                with col2:
                    enabled_count = len([u for u in users if u.get('enabled', True)])
                    st.metric("Enabled Users", enabled_count)
                with col3:
                    disabled_count = len([u for u in users if not u.get('enabled', True)])
                    st.metric("Disabled Users", disabled_count)
                with col4:
                    basic_count = len([u for u in users if u.get('tier', 'Basic') == 'Basic'])
                    st.metric("Basic Tier", basic_count)
                with col5:
                    standard_count = len([u for u in users if u.get('tier', 'Basic') == 'Standard'])
                    st.metric("Standard Tier", standard_count)
                with col6:
                    premium_count = len([u for u in users if u.get('tier', 'Basic') == 'Premium'])
                    st.metric("Premium Tier", premium_count)
                
                # Display users table
                df_users = pd.DataFrame(users)
                # Format dates
                if 'created_date' in df_users.columns:
                    df_users['created_date'] = pd.to_datetime(df_users['created_date']).dt.strftime('%Y-%m-%d %H:%M')
                if 'last_login' in df_users.columns:
                    df_users['last_login'] = df_users['last_login'].apply(lambda x: pd.to_datetime(x).strftime('%Y-%m-%d %H:%M') if x else 'Never')
                
                st.dataframe(df_users, use_container_width=True)
            else:
                st.info("No users found. Create your first user in the 'Add New User' tab.")
        except Exception as e:
            st.error(f"Error loading users: {str(e)}")
    
    with tab2:
        st.subheader("➕ Add New User")
        
        # Clear any previous success messages when entering this tab
        if 'user_created' in st.session_state:
            if st.session_state.user_created:
                # Show success message once, then clear
                message = st.session_state.get('user_created_message', 'User created successfully!')
                st.success(f"✅ {message}")
                st.session_state.user_created = False
                st.session_state.user_created_message = ""
                # Clear form fields by resetting form state
                if 'user_form_cleared' not in st.session_state:
                    st.session_state.user_form_cleared = True
        
        # Use form with clear_on_submit to clear fields after successful submission
        with st.form("add_user_form", clear_on_submit=True):
            new_username = st.text_input("Username *", help="Unique username for the user", value="")
            new_password = st.text_input("Password *", type="password", help="User's password", value="")
            new_email = st.text_input("Email (Optional)", help="User's email address", value="")
            
            # Company selection
            companies = get_all_companies()
            company_options = [None] + [c['id'] for c in companies]
            company_labels = ["No Company"] + [f"{c['id']} - {c['name']}" for c in companies]
            selected_company_idx = st.selectbox("Company (Optional)", range(len(company_options)), 
                                                format_func=lambda x: company_labels[x], index=0)
            selected_company_id = company_options[selected_company_idx] if selected_company_idx > 0 else None
            
            new_tier = st.selectbox("Tier *", ["Basic", "Standard", "Premium"], index=0, help="User subscription tier")
            new_role = st.selectbox("Role *", ["Admin", "User", "Viewer"], index=1, help="User role within company")
            enabled = st.checkbox("Enable User", value=True, help="User can login if enabled")
            
            submitted = st.form_submit_button("Create User", type="primary", use_container_width=True)
            
            if submitted:
                # Only process if form was actually submitted (button clicked)
                if new_username and new_password:
                    success, message = create_user(new_username, new_password, enabled, new_email, new_tier, selected_company_id, new_role)
                    if success:
                        st.session_state.user_created = True
                        st.session_state.user_created_message = message
                        # Don't rerun here - let clear_on_submit handle clearing the form
                        # The success message will show on next rerun (when user interacts)
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.error("⚠️ Username and password are required")
        
        # Success message is shown in the form above
    
    with tab3:
        st.subheader("⚙️ Manage Existing User")
        try:
            users = get_all_auth_users()
            if users:
                selected_username = st.selectbox("Select User", [u['username'] for u in users])
                
                if selected_username:
                    user_info = get_user(selected_username)
                    if user_info:
                        st.write(f"**Username:** {user_info.get('username')}")
                        st.write(f"**Email:** {user_info.get('email', 'N/A')}")
                        st.write(f"**Tier:** {user_info.get('tier', 'Basic')}")
                        company_id = user_info.get('company_id')
                        if company_id:
                            company = get_company(company_id)
                            company_name = company.get('name', 'Unknown') if company else 'Unknown'
                            st.write(f"**Company:** {company_id} - {company_name}")
                        else:
                            st.write(f"**Company:** No company assigned")
                        st.write(f"**Role:** {user_info.get('role', 'User')}")
                        st.write(f"**Status:** {'✅ Enabled' if user_info.get('enabled', True) else '❌ Disabled'}")
                        st.write(f"**Created:** {user_info.get('created_date', 'N/A')}")
                        st.write(f"**Last Login:** {user_info.get('last_login', 'Never')}")
                        
                        st.divider()
                        
                        # Actions
                        col1, col2, col3, col4, col5 = st.columns(5)
                        
                        with col1:
                            if user_info.get('enabled', True):
                                if st.button("🚫 Disable User", type="secondary"):
                                    success, message = enable_disable_user(selected_username, False)
                                    if success:
                                        st.success(message)
                                    else:
                                        st.error(message)
                            else:
                                if st.button("✅ Enable User", type="primary"):
                                    success, message = enable_disable_user(selected_username, True)
                                    if success:
                                        st.success(message)
                                    else:
                                        st.error(message)
                        
                        with col2:
                            st.subheader("Change Tier")
                            current_tier = user_info.get('tier', 'Basic')
                            tier_options = ["Basic", "Standard", "Premium"]
                            tier_index = tier_options.index(current_tier) if current_tier in tier_options else 0
                            
                            new_tier = st.selectbox("Select Tier", tier_options, 
                                                   index=tier_index,
                                                   key=f"tier_select_{selected_username}")
                            
                            if st.button("Update Tier", key=f"tier_btn_{selected_username}"):
                                if new_tier != current_tier:
                                    success, message = update_user_tier(selected_username, new_tier)
                                    if success:
                                        st.success(message)
                                    else:
                                        st.error(message)
                        
                        with col3:
                            st.subheader("Change Role")
                            current_role = user_info.get('role', 'User')
                            role_options = ["Admin", "User", "Viewer"]
                            role_index = role_options.index(current_role) if current_role in role_options else 1
                            
                            new_role = st.selectbox("Select Role", role_options,
                                                   index=role_index,
                                                   key=f"role_select_{selected_username}")
                            
                            if st.button("Update Role", key=f"role_btn_{selected_username}"):
                                if new_role != current_role:
                                    success, message = update_user_role(selected_username, new_role)
                                    if success:
                                        st.success(message)
                                    else:
                                        st.error(message)
                        
                        with col4:
                            st.subheader("Change Company")
                            companies = get_all_companies()
                            company_options = [None] + [c['id'] for c in companies]
                            company_labels = ["No Company"] + [f"{c['id']} - {c['name']}" for c in companies]
                            current_company_id = user_info.get('company_id')
                            current_company_idx = 0 if not current_company_id else (
                                company_options.index(current_company_id) if current_company_id in company_options else 0
                            )
                            
                            new_company_idx = st.selectbox("Select Company", range(len(company_options)),
                                                          index=current_company_idx,
                                                          format_func=lambda x: company_labels[x],
                                                          key=f"company_select_{selected_username}")
                            new_company_id = company_options[new_company_idx] if new_company_idx > 0 else None
                            
                            if st.button("Update Company", key=f"company_btn_{selected_username}"):
                                if new_company_id != current_company_id:
                                    success, message = update_user_company(selected_username, new_company_id)
                                    if success:
                                        st.success(message)
                                    else:
                                        st.error(message)
                        
                        with col5:
                            st.subheader("Reset Password")
                            # Use a form to handle password reset properly
                            with st.form(f"reset_pwd_form_{selected_username}", clear_on_submit=True):
                                new_password = st.text_input("New Password", type="password", key=f"reset_pwd_{selected_username}")
                                submitted = st.form_submit_button("Update Password", use_container_width=True)
                                
                                if submitted:
                                    if new_password and new_password.strip():
                                        success, message = update_user_password(selected_username, new_password.strip())
                                        if success:
                                            st.success(message)
                                        else:
                                            st.error(message)
                                    else:
                                        st.error("Please enter a new password")
                        
                        st.divider()
                        col_delete = st.columns(1)[0]
                        with col_delete:
                            st.subheader("Delete User")
                            if st.button("🗑️ Delete User", type="secondary"):
                                if st.session_state.get('confirm_delete') != selected_username:
                                    st.session_state.confirm_delete = selected_username
                                    st.warning("⚠️ Click again to confirm deletion")
                                else:
                                    success, message = delete_user(selected_username)
                                    if success:
                                        st.success(message)
                                        st.session_state.confirm_delete = None
                                    else:
                                        st.error(message)
            else:
                st.info("No users found. Create your first user in the 'Add New User' tab.")
        except Exception as e:
            st.error(f"Error managing users: {str(e)}")

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
        logo_path = st.text_input("Logo Path", value=config.get('logo_path', 'static/logo.png'), 
                                  help="Path to customer logo file (relative to LIPG Cloud folder, e.g., 'static/customer_logo.png')")
        
        # Show current logo if it exists
        if logo_path:
            _base_dir = os.path.dirname(os.path.abspath(__file__))
            _test_logo_path = os.path.join(_base_dir, logo_path)
            if os.path.exists(_test_logo_path):
                st.success(f"✅ Logo file found at: {logo_path}")
                try:
                    st.image(_test_logo_path, width=200)
                except Exception as e:
                    st.warning(f"⚠️ Could not display logo: {str(e)}")
            else:
                st.warning(f"⚠️ Logo file not found at: {logo_path}")
                st.info("💡 Place the customer logo file in the specified location, or use 'static/logo.png' for default logo.")
        
        if st.button("💾 Save Configuration"):
            new_config = {
                'customer_name': customer_name,
                'background_color': background_color,
                'button_color': button_color,
                'logo_path': logo_path
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

