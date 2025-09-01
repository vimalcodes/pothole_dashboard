import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="Malaysia Pothole Detection Dashboard",
    page_icon="🕳️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .severity-critical { color: #dc2626; font-weight: bold; }
    .severity-high { color: #ea580c; font-weight: bold; }
    .severity-medium { color: #d97706; font-weight: bold; }
    .severity-low { color: #16a34a; font-weight: bold; }
    .status-new { color: #dc2626; font-weight: bold; }
    .status-progress { color: #d97706; font-weight: bold; }
    .status-completed { color: #16a34a; font-weight: bold; }
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        background: white;
    }
    .upload-info {
        background: #f0f9ff;
        border: 2px dashed #0ea5e9;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Authentication functions
def init_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_role" not in st.session_state:
        st.session_state.user_role = None

def authenticate_user(username, password):
    users = {
        "admin": {"password": "pothole123", "role": "admin"},
        "viewer": {"password": "view123", "role": "viewer"}
    }
    
    if username in users and users[username]["password"] == password:
        st.session_state.authenticated = True
        st.session_state.user_role = users[username]["role"]
        st.session_state.username = username
        return True
    return False

def logout():
    st.session_state.authenticated = False
    st.session_state.user_role = None
    if "username" in st.session_state:
        del st.session_state.username

# Login page
def show_login():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown("## 🔐 Login to Dashboard")
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        login_button = st.form_submit_button("Login", use_container_width=True)
        
        if login_button:
            if authenticate_user(username, password):
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    st.markdown("### Demo Credentials:")
    st.info("**Admin:** username=`admin`, password=`pothole123`")
    st.info("**Viewer:** username=`viewer`, password=`view123`")
    st.markdown('</div>', unsafe_allow_html=True)

# Load data function - NO SAMPLE DATA
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            # Validate required columns
            required_cols = ['pothole_id', 'latitude', 'longitude', 'state', 'address', 
                           'size', 'severity', 'date_detected', 'time_detected', 'user_id', 'status']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                st.error(f"Missing required columns: {', '.join(missing_cols)}")
                return None
            return df
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            return None
    else:
        # Return empty dataframe - NO SAMPLE DATA
        return pd.DataFrame(columns=['pothole_id', 'latitude', 'longitude', 'state', 'address', 
                                   'size', 'severity', 'date_detected', 'time_detected', 'user_id', 'status'])

# Upload instructions page
def show_upload_instructions():
    st.markdown('<div class="upload-info">', unsafe_allow_html=True)
    st.markdown("## 📁 Upload Required")
    st.markdown("### Please upload a CSV file to get started")
    
    st.markdown("**Required CSV Format (11 columns):**")
    st.code("""
pothole_id,latitude,longitude,state,address,size,severity,date_detected,time_detected,user_id,status
PH001,3.139000,101.686900,Kuala Lumpur,"Jalan Bukit Bintang",Medium,High,2024-12-15,14:30,U1001,New
    """)
    
    st.markdown("**Column Specifications:**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        - **pothole_id**: Unique identifier (PH001, PH002...)
        - **latitude**: GPS latitude (decimal format)
        - **longitude**: GPS longitude (decimal format)
        - **state**: Malaysian state name
        - **address**: Street address
        - **size**: Small, Medium, Large
        """)
    
    with col2:
        st.markdown("""
        - **severity**: Low, Medium, High, Critical
        - **date_detected**: Date (YYYY-MM-DD)
        - **time_detected**: Time (HH:MM)
        - **user_id**: User identifier
        - **status**: New, In Progress, Completed
        """)
    
    st.markdown("👆 **Use the sidebar to upload your CSV file**")
    st.markdown('</div>', unsafe_allow_html=True)

# Main dashboard
def show_dashboard():
    # Header with logout
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.markdown(f"**👤 {st.session_state.username} ({st.session_state.user_role})**")
    with col2:
        st.markdown('<h1 class="main-header">🕳️ Malaysia Pothole Detection Dashboard</h1>', unsafe_allow_html=True)
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()
    
    # Sidebar - File Upload
    st.sidebar.header("📁 Data Upload")
    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV file",
        type=['csv'],
        help="Upload pothole detection data from your mobile app"
    )
    
    # Load and validate data
    df = load_data(uploaded_file)
    if df is None:
        return
    
    # Handle empty dataframe (no file uploaded)
    if df.empty:
        st.sidebar.warning("📁 No data loaded. Please upload a CSV file.")
        show_upload_instructions()
        return
    
    # Convert date column (only if data exists)
    try:
        df['date_detected'] = pd.to_datetime(df['date_detected'])
    except Exception as e:
        st.error(f"Error processing dates: {str(e)}")
        return
    
    # Display data info
    st.sidebar.success(f"✅ Loaded {len(df)} records")
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # State filter
    states = ['All'] + sorted(df['state'].unique())
    selected_state = st.sidebar.selectbox("Select State", states)
    
    # Date range filter
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("From", df['date_detected'].min().date())
    with col2:
        end_date = st.date_input("To", df['date_detected'].max().date())
    
    # Multi-select filters
    severities = st.sidebar.multiselect("Severity", df['severity'].unique(), 
                                       default=df['severity'].unique())
    statuses = st.sidebar.multiselect("Status", df['status'].unique(), 
                                     default=df['status'].unique())
    sizes = st.sidebar.multiselect("Size", df['size'].unique(), 
                                  default=df['size'].unique())
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_state != 'All':
        filtered_df = filtered_df[filtered_df['state'] == selected_state]
    
    filtered_df = filtered_df[
        (filtered_df['date_detected'].dt.date >= start_date) &
        (filtered_df['date_detected'].dt.date <= end_date) &
        (filtered_df['severity'].isin(severities)) &
        (filtered_df['status'].isin(statuses)) &
        (filtered_df['size'].isin(sizes))
    ]
    
    # Key Metrics
    st.header("📊 Overview")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Potholes", len(filtered_df))
    
    with col2:
        critical_count = len(filtered_df[filtered_df['severity'] == 'Critical'])
        st.metric("Critical Issues", critical_count,
                 delta=f"{critical_count/len(filtered_df)*100:.1f}%" if len(filtered_df) > 0 else "0%")
    
    with col3:
        new_count = len(filtered_df[filtered_df['status'] == 'New'])
        st.metric("New Reports", new_count)
    
    with col4:
        completed = len(filtered_df[filtered_df['status'] == 'Completed'])
        completion_rate = completed/len(filtered_df)*100 if len(filtered_df) > 0 else 0
        st.metric("Completion Rate", f"{completion_rate:.1f}%", f"{completed} completed")
    
    with col5:
        unique_users = filtered_df['user_id'].nunique()
        st.metric("Active Users", unique_users)
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Map View", "📈 Analytics", "📋 Data Table", "📊 Export & Reports"])
    
    with tab1:
        st.subheader("Interactive Pothole Map")
        
        if len(filtered_df) > 0:
            # Create folium map
            center_lat = filtered_df['latitude'].mean()
            center_lng = filtered_df['longitude'].mean()
            
            m = folium.Map(
                location=[center_lat, center_lng], 
                zoom_start=10,
                tiles='OpenStreetMap'
            )
            
            # Color mapping
            color_map = {
                'Low': 'green',
                'Medium': 'orange',
                'High': 'red', 
                'Critical': 'darkred'
            }
            
            # Size mapping
            size_map = {
                'Small': 6,
                'Medium': 9,
                'Large': 12
            }
            
            # Add markers
            for idx, row in filtered_df.iterrows():
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=size_map.get(row['size'], 8),
                    popup=folium.Popup(f"""
                    <div style='width:250px'>
                    <b>🆔 {row['pothole_id']}</b><br>
                    <b>📍 Location:</b> {row['address']}<br>
                    <b>🏛️ State:</b> {row['state']}<br>
                    <b>⚡ Severity:</b> {row['severity']}<br>
                    <b>📏 Size:</b> {row['size']}<br>
                    <b>📊 Status:</b> {row['status']}<br>
                    <b>📅 Detected:</b> {row['date_detected'].strftime('%Y-%m-%d')} {row['time_detected']}<br>
                    <b>👤 User:</b> {row['user_id']}
                    </div>
                    """, max_width=300),
                    color=color_map.get(row['severity'], 'blue'),
                    fill=True,
                    fillColor=color_map.get(row['severity'], 'blue'),
                    fillOpacity=0.8,
                    weight=2
                ).add_to(m)
            
            # Display map
            st_folium(m, width=1200, height=500, returned_objects=["last_clicked"])
            
            # Legend
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Severity Legend:**")
                st.markdown("🟢 Low | 🟠 Medium | 🔴 High | 🟤 Critical")
            with col2:
                st.markdown("**Size Legend:**")
                st.markdown("Small ● | Medium ●● | Large ●●●")
            
        else:
            st.info("No potholes to display with current filters.")
    
    with tab2:
        st.subheader("Analytics Dashboard")
        
        if len(filtered_df) > 0:
            # Row 1: Distributions
            col1, col2 = st.columns(2)
            
            with col1:
                # Severity distribution
                severity_counts = filtered_df['severity'].value_counts()
                fig_severity = px.pie(
                    values=severity_counts.values,
                    names=severity_counts.index,
                    title="Distribution by Severity Level",
                    color_discrete_map={
                        'Low': '#22c55e',
                        'Medium': '#f59e0b',
                        'High': '#ef4444',
                        'Critical': '#7f1d1d'
                    }
                )
                fig_severity.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_severity, use_container_width=True)
            
            with col2:
                # Status distribution
                status_counts = filtered_df['status'].value_counts()
                fig_status = px.bar(
                    x=status_counts.values,
                    y=status_counts.index,
                    orientation='h',
                    title="Reports by Status",
                    color=status_counts.index,
                    color_discrete_map={
                        'New': '#ef4444',
                        'In Progress': '#f59e0b',
                        'Completed': '#22c55e'
                    }
                )
                fig_status.update_layout(showlegend=False)
                st.plotly_chart(fig_status, use_container_width=True)
            
            # Row 2: Trends and Geography
            col1, col2 = st.columns(2)
            
            with col1:
                # Time series
                daily_reports = filtered_df.groupby(filtered_df['date_detected'].dt.date).size().reset_index()
                daily_reports.columns = ['date', 'count']
                
                fig_timeline = px.line(
                    daily_reports, 
                    x='date', 
                    y='count',
                    title="Daily Pothole Reports Trend",
                    markers=True
                )
                fig_timeline.update_layout(xaxis_title="Date", yaxis_title="Number of Reports")
                st.plotly_chart(fig_timeline, use_container_width=True)
            
            with col2:
                # State distribution
                state_counts = filtered_df['state'].value_counts().head(10)
                fig_states = px.bar(
                    x=state_counts.values,
                    y=state_counts.index,
                    orientation='h',
                    title="Top States by Pothole Reports",
                    color=state_counts.values,
                    color_continuous_scale='Reds'
                )
                fig_states.update_layout(showlegend=False, coloraxis_showscale=False)
                st.plotly_chart(fig_states, use_container_width=True)
            
            # Row 3: Additional insights
            col1, col2 = st.columns(2)
            
            with col1:
                # Size vs Severity heatmap
                heatmap_data = filtered_df.groupby(['size', 'severity']).size().unstack(fill_value=0)
                if not heatmap_data.empty:
                    fig_heatmap = px.imshow(
                        heatmap_data.values,
                        x=heatmap_data.columns,
                        y=heatmap_data.index,
                        title="Size vs Severity Distribution",
                        color_continuous_scale='Reds',
                        text_auto=True
                    )
                    st.plotly_chart(fig_heatmap, use_container_width=True)
            
            with col2:
                # User activity
                user_activity = filtered_df['user_id'].value_counts().head(10)
                fig_users = px.bar(
                    x=user_activity.values,
                    y=user_activity.index,
                    orientation='h',
                    title="Top 10 Most Active Users",
                    color=user_activity.values,
                    color_continuous_scale='Blues'
                )
                fig_users.update_layout(showlegend=False, coloraxis_showscale=False)
                st.plotly_chart(fig_users, use_container_width=True)
        
        else:
            st.info("No data available for analytics with current filters.")
    
    with tab3:
        st.subheader("Pothole Data Table")
        
        if len(filtered_df) > 0:
            # Search functionality
            search_term = st.text_input("🔍 Search in table", placeholder="Search by ID, address, or user...")
            
            if search_term:
                mask = (
                    filtered_df['pothole_id'].str.contains(search_term, case=False, na=False) |
                    filtered_df['address'].str.contains(search_term, case=False, na=False) |
                    filtered_df['user_id'].str.contains(search_term, case=False, na=False) |
                    filtered_df['state'].str.contains(search_term, case=False, na=False)
                )
                display_df = filtered_df[mask]
            else:
                display_df = filtered_df
            
            # Column selection
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"Showing {len(display_df)} of {len(filtered_df)} records")
            with col2:
                if st.session_state.user_role == "admin":
                    if st.button("📝 Edit Mode", help="Enable editing for admin users"):
                        st.info("Edit mode would be implemented here for admin users")
            
            # Display table
            st.dataframe(
                display_df.style.format({
                    'latitude': '{:.6f}',
                    'longitude': '{:.6f}',
                    'date_detected': lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else ''
                }),
                use_container_width=True,
                height=400
            )
            
            # Quick stats for filtered data
            if len(display_df) > 0:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Filtered Records", len(display_df))
                with col2:
                    st.metric("Unique States", display_df['state'].nunique())
                with col3:
                    st.metric("Critical Issues", len(display_df[display_df['severity'] == 'Critical']))
                with col4:
                    st.metric("Unique Users", display_df['user_id'].nunique())
        
        else:
            st.info("No data matches current filters.")
    
    with tab4:
        st.subheader("📊 Export & Reports")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📥 Data Export")
            
            if len(filtered_df) > 0:
                # Export CSV
                csv_data = filtered_df.to_csv(index=False)
                st.download_button(
                    label="📄 Download Filtered Data (CSV)",
                    data=csv_data,
                    file_name=f"pothole_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
                # Summary report
                summary_report = f"""# Pothole Detection Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary Statistics
- Total Potholes: {len(filtered_df)}
- States Covered: {filtered_df['state'].nunique()}
- Date Range: {filtered_df['date_detected'].min().strftime('%Y-%m-%d')} to {filtered_df['date_detected'].max().strftime('%Y-%m-%d')}

## Severity Breakdown
{filtered_df['severity'].value_counts().to_string()}

## Status Overview  
{filtered_df['status'].value_counts().to_string()}

## Top 5 States
{filtered_df['state'].value_counts().head().to_string()}
"""
                
                st.download_button(
                    label="📋 Download Summary Report",
                    data=summary_report,
                    file_name=f"pothole_summary_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        
        with col2:
            st.markdown("### 📈 Quick Reports")
            
            if len(filtered_df) > 0:
                # Generate quick insights
                st.markdown("**Key Insights:**")
                
                most_affected_state = filtered_df['state'].value_counts().index[0]
                st.write(f"• Most affected state: **{most_affected_state}** ({filtered_df['state'].value_counts().iloc[0]} reports)")
                
                critical_percentage = len(filtered_df[filtered_df['severity'] == 'Critical']) / len(filtered_df) * 100
                st.write(f"• Critical issues: **{critical_percentage:.1f}%** of all reports")
                
                completion_rate = len(filtered_df[filtered_df['status'] == 'Completed']) / len(filtered_df) * 100
                st.write(f"• Completion rate: **{completion_rate:.1f}%**")
                
                most_active_user = filtered_df['user_id'].value_counts().index[0]
                user_reports = filtered_df['user_id'].value_counts().iloc[0]
                st.write(f"• Most active reporter: **{most_active_user}** ({user_reports} reports)")
                
                # Recent activity
                recent_reports = len(filtered_df[filtered_df['date_detected'] >= (datetime.now() - timedelta(days=7))])
                st.write(f"• Reports in last 7 days: **{recent_reports}**")
            
            else:
                st.info("No data available for reporting.")

# Main app flow
def main():
    init_session_state()
    
    if not st.session_state.authenticated:
        show_login()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()