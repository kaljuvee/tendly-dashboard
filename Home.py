import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import json
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Tendly Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database connection
@st.cache_resource
def init_connection():
    """Initialize database connection with caching."""
    db_url = os.getenv('DB_URL')
    if not db_url:
        st.error("DB_URL environment variable not found. Please set it in your environment or .env file.")
        st.stop()
    return create_engine(db_url)

@st.cache_data(ttl=600)  # Cache for 10 minutes
def load_tender_data():
    """Load Estonian tender details data from database."""
    engine = init_connection()
    
    query = """
    SELECT 
        procurement_id,
        tender_name,
        short_description,
        estimated_cost,
        is_cost_classified,
        show_cost,
        procedure_type_code,
        procurement_type_code,
        procurement_sector_code,
        primary_cpv_code,
        primary_cpv_name,
        nuts_code,
        location_additional_info,
        submission_deadline,
        publication_date,
        duration_in_months,
        is_eu_financing,
        is_green,
        has_social_aspects,
        has_innovative_aspects,
        created_at
    FROM estonian_tender_details
    WHERE estimated_cost IS NOT NULL 
    AND estimated_cost > 0
    ORDER BY estimated_cost DESC
    """
    
    df = pd.read_sql_query(query, engine)
    
    # Convert date columns
    date_columns = ['submission_deadline', 'publication_date', 'created_at']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    return df

def create_cost_buckets(df, num_buckets=50):
    """Create cost buckets for the estimated_cost column."""
    min_cost = df['estimated_cost'].min()
    max_cost = df['estimated_cost'].max()
    
    # Use logarithmic scale for better distribution
    log_min = np.log10(min_cost)
    log_max = np.log10(max_cost)
    
    # Create bucket edges on log scale
    log_edges = np.linspace(log_min, log_max, num_buckets + 1)
    bucket_edges = 10 ** log_edges
    
    # Create bucket labels
    bucket_labels = []
    for i in range(len(bucket_edges) - 1):
        start = bucket_edges[i]
        end = bucket_edges[i + 1]
        if start < 1000:
            start_str = f"€{start:.0f}"
        elif start < 1000000:
            start_str = f"€{start/1000:.0f}K"
        else:
            start_str = f"€{start/1000000:.1f}M"
            
        if end < 1000:
            end_str = f"€{end:.0f}"
        elif end < 1000000:
            end_str = f"€{end/1000:.0f}K"
        else:
            end_str = f"€{end/1000000:.1f}M"
            
        bucket_labels.append(f"{start_str} - {end_str}")
    
    # Assign buckets
    df['cost_bucket'] = pd.cut(df['estimated_cost'], bins=bucket_edges, labels=bucket_labels, include_lowest=True)
    
    return df, bucket_edges, bucket_labels

def main():
    """Main dashboard application."""
    
    # Header
    st.title("🏛️ Tendly Dashboard")
    st.markdown("**Estonian Public Procurement Analytics**")
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading tender data..."):
        try:
            df = load_tender_data()
            st.success(f"Loaded {len(df):,} tender records")
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            st.stop()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Cost range filter
    min_cost, max_cost = st.sidebar.slider(
        "Cost Range (€)",
        min_value=float(df['estimated_cost'].min()),
        max_value=float(df['estimated_cost'].max()),
        value=(float(df['estimated_cost'].min()), float(df['estimated_cost'].max())),
        format="€%.0f"
    )
    
    # Sector filter
    sectors = ['All'] + sorted(df['procurement_sector_code'].dropna().unique().tolist())
    selected_sector = st.sidebar.selectbox("Procurement Sector", sectors)
    
    # Procedure type filter
    procedures = ['All'] + sorted(df['procedure_type_code'].dropna().unique().tolist())
    selected_procedure = st.sidebar.selectbox("Procedure Type", procedures)
    
    # Apply filters
    filtered_df = df[
        (df['estimated_cost'] >= min_cost) & 
        (df['estimated_cost'] <= max_cost)
    ]
    
    if selected_sector != 'All':
        filtered_df = filtered_df[filtered_df['procurement_sector_code'] == selected_sector]
    
    if selected_procedure != 'All':
        filtered_df = filtered_df[filtered_df['procedure_type_code'] == selected_procedure]
    
    # Create cost buckets
    if len(filtered_df) > 0:
        filtered_df, bucket_edges, bucket_labels = create_cost_buckets(filtered_df, 50)
    
    # Main content
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tenders", f"{len(filtered_df):,}")
    
    with col2:
        total_value = filtered_df['estimated_cost'].sum()
        if total_value >= 1e9:
            value_str = f"€{total_value/1e9:.1f}B"
        elif total_value >= 1e6:
            value_str = f"€{total_value/1e6:.1f}M"
        elif total_value >= 1e3:
            value_str = f"€{total_value/1e3:.1f}K"
        else:
            value_str = f"€{total_value:.0f}"
        st.metric("Total Value", value_str)
    
    with col3:
        avg_cost = filtered_df['estimated_cost'].mean()
        if avg_cost >= 1e6:
            avg_str = f"€{avg_cost/1e6:.1f}M"
        elif avg_cost >= 1e3:
            avg_str = f"€{avg_cost/1e3:.1f}K"
        else:
            avg_str = f"€{avg_cost:.0f}"
        st.metric("Average Cost", avg_str)
    
    with col4:
        median_cost = filtered_df['estimated_cost'].median()
        if median_cost >= 1e6:
            median_str = f"€{median_cost/1e6:.1f}M"
        elif median_cost >= 1e3:
            median_str = f"€{median_cost/1e3:.1f}K"
        else:
            median_str = f"€{median_cost:.0f}"
        st.metric("Median Cost", median_str)
    
    st.markdown("---")
    
    if len(filtered_df) == 0:
        st.warning("No data available for the selected filters.")
        return
    
    # Main visualization: Cost Distribution with 50 buckets
    st.header("💰 Cost Distribution Analysis")
    
    # Count tenders per bucket
    bucket_counts = filtered_df['cost_bucket'].value_counts().sort_index()
    
    # Create bar chart
    fig_cost = go.Figure()
    
    fig_cost.add_trace(go.Bar(
        x=bucket_counts.index,
        y=bucket_counts.values,
        name="Number of Tenders",
        marker_color='#1f77b4',
        hovertemplate='<b>%{x}</b><br>Tenders: %{y}<extra></extra>'
    ))
    
    fig_cost.update_layout(
        title="Distribution of Tenders by Estimated Cost (50 Buckets)",
        xaxis_title="Cost Range",
        yaxis_title="Number of Tenders",
        height=500,
        showlegend=False,
        xaxis={'tickangle': 45}
    )
    
    st.plotly_chart(fig_cost, use_container_width=True)
    
    # Additional visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 By Procurement Sector")
        sector_counts = filtered_df['procurement_sector_code'].value_counts()
        
        fig_sector = px.pie(
            values=sector_counts.values,
            names=sector_counts.index,
            title="Tenders by Procurement Sector"
        )
        fig_sector.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_sector, use_container_width=True)
    
    with col2:
        st.subheader("🏗️ By Procedure Type")
        procedure_counts = filtered_df['procedure_type_code'].value_counts()
        
        fig_procedure = px.bar(
            x=procedure_counts.index,
            y=procedure_counts.values,
            title="Tenders by Procedure Type",
            labels={'x': 'Procedure Type', 'y': 'Number of Tenders'}
        )
        st.plotly_chart(fig_procedure, use_container_width=True)
    
    # Timeline analysis
    st.subheader("📅 Timeline Analysis")
    
    # Filter data with valid submission deadlines
    timeline_df = filtered_df[filtered_df['submission_deadline'].notna()].copy()
    
    if len(timeline_df) > 0:
        timeline_df['submission_month'] = timeline_df['submission_deadline'].dt.to_period('M')
        monthly_counts = timeline_df.groupby('submission_month').size()
        
        fig_timeline = px.line(
            x=monthly_counts.index.astype(str),
            y=monthly_counts.values,
            title="Tender Submissions Over Time",
            labels={'x': 'Month', 'y': 'Number of Tenders'}
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.info("No timeline data available for the selected filters.")
    
    # Top categories by value
    st.subheader("🏆 Top Categories by Total Value")
    
    category_value = filtered_df.groupby('primary_cpv_name')['estimated_cost'].agg(['sum', 'count']).reset_index()
    category_value = category_value.sort_values('sum', ascending=False).head(10)
    
    fig_categories = px.bar(
        category_value,
        x='sum',
        y='primary_cpv_name',
        orientation='h',
        title="Top 10 Categories by Total Estimated Value",
        labels={'sum': 'Total Estimated Value (€)', 'primary_cpv_name': 'Category'},
        hover_data=['count']
    )
    fig_categories.update_layout(height=500)
    st.plotly_chart(fig_categories, use_container_width=True)
    
    # Data table
    st.subheader("📋 Recent Tenders")
    
    # Display recent tenders
    display_df = filtered_df[['tender_name', 'estimated_cost', 'primary_cpv_name', 
                             'procurement_sector_code', 'submission_deadline']].copy()
    display_df['estimated_cost'] = display_df['estimated_cost'].apply(
        lambda x: f"€{x:,.0f}" if pd.notna(x) else "N/A"
    )
    display_df = display_df.sort_values('submission_deadline', ascending=False, na_position='last')
    
    st.dataframe(
        display_df.head(20),
        column_config={
            "tender_name": "Tender Name",
            "estimated_cost": "Estimated Cost",
            "primary_cpv_name": "Category",
            "procurement_sector_code": "Sector",
            "submission_deadline": "Submission Deadline"
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Footer
    st.markdown("---")
    st.markdown("*Data source: Estonian Public Procurement Database*")

if __name__ == "__main__":
    main()
