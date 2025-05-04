"""
Analytics view for POD Automation System dashboard.
Provides UI for viewing analytics and reports.
"""

import os
import sys
import logging
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Import utilities
from pod_automation.config.logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)

class AnalyticsView:
    """Analytics view for POD Automation System dashboard."""
    
    def __init__(self, system, db):
        """Initialize analytics view.
        
        Args:
            system: POD Automation System instance
            db: Database instance
        """
        self.system = system
        self.db = db
    
    def show(self):
        """Show analytics view."""
        st.title("Analytics")
        
        # Add tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Designs", "Products", "Trends"])
        
        with tab1:
            self._show_overview()
        
        with tab2:
            self._show_design_analytics()
        
        with tab3:
            self._show_product_analytics()
        
        with tab4:
            self._show_trend_analytics()
    
    def _show_overview(self):
        """Show overview tab."""
        st.header("Overview")
        
        # Get counts
        design_count = self.db.count("designs")
        mockup_count = self.db.count("mockups")
        product_count = self.db.count("products")
        workflow_count = self.db.count("workflows")
        
        # Display counts
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Designs", design_count)
        
        with col2:
            st.metric("Mockups", mockup_count)
        
        with col3:
            st.metric("Products", product_count)
        
        with col4:
            st.metric("Workflows", workflow_count)
        
        # Get recent activity
        recent_designs = self.db.query(
            "SELECT COUNT(*) as count, DATE(created_at) as date FROM designs GROUP BY DATE(created_at) ORDER BY date DESC LIMIT 30"
        )
        
        recent_products = self.db.query(
            "SELECT COUNT(*) as count, DATE(created_at) as date FROM products GROUP BY DATE(created_at) ORDER BY date DESC LIMIT 30"
        )
        
        # Create activity chart
        if recent_designs or recent_products:
            st.subheader("Recent Activity")
            
            # Convert to DataFrames
            if recent_designs:
                df_designs = pd.DataFrame(recent_designs)
                df_designs["date"] = pd.to_datetime(df_designs["date"])
                df_designs = df_designs.sort_values("date")
            else:
                df_designs = pd.DataFrame(columns=["date", "count"])
            
            if recent_products:
                df_products = pd.DataFrame(recent_products)
                df_products["date"] = pd.to_datetime(df_products["date"])
                df_products = df_products.sort_values("date")
            else:
                df_products = pd.DataFrame(columns=["date", "count"])
            
            # Create date range
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
            date_range = pd.date_range(start=start_date, end=end_date)
            
            # Create complete DataFrame
            df_activity = pd.DataFrame({"date": date_range})
            
            # Merge with designs and products
            df_activity = df_activity.merge(
                df_designs, on="date", how="left"
            ).rename(columns={"count": "designs"})
            
            df_activity = df_activity.merge(
                df_products, on="date", how="left"
            ).rename(columns={"count": "products"})
            
            # Fill NaN with 0
            df_activity = df_activity.fillna(0)
            
            # Create chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df_activity["date"],
                y=df_activity["designs"],
                name="Designs",
                mode="lines+markers",
                line=dict(color="blue", width=2),
                marker=dict(size=8)
            ))
            
            fig.add_trace(go.Scatter(
                x=df_activity["date"],
                y=df_activity["products"],
                name="Products",
                mode="lines+markers",
                line=dict(color="green", width=2),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title="Activity Over Time",
                xaxis_title="Date",
                yaxis_title="Count",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Get platform distribution
        platform_distribution = self.db.query(
            "SELECT platform, COUNT(*) as count FROM products GROUP BY platform"
        )
        
        if platform_distribution:
            st.subheader("Platform Distribution")
            
            # Convert to DataFrame
            df_platforms = pd.DataFrame(platform_distribution)
            
            # Create chart
            fig = px.pie(
                df_platforms,
                values="count",
                names="platform",
                title="Products by Platform",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig.update_traces(textposition="inside", textinfo="percent+label")
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Get product type distribution
        product_type_distribution = self.db.query(
            "SELECT product_type, COUNT(*) as count FROM products GROUP BY product_type"
        )
        
        if product_type_distribution:
            st.subheader("Product Type Distribution")
            
            # Convert to DataFrame
            df_product_types = pd.DataFrame(product_type_distribution)
            
            # Create chart
            fig = px.bar(
                df_product_types,
                x="product_type",
                y="count",
                title="Products by Type",
                color="product_type",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig.update_layout(
                xaxis_title="Product Type",
                yaxis_title="Count"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def _show_design_analytics(self):
        """Show design analytics tab."""
        st.header("Design Analytics")
        
        # Get design keywords
        design_keywords = self.db.query(
            "SELECT keyword, COUNT(*) as count FROM designs GROUP BY keyword ORDER BY count DESC LIMIT 20"
        )
        
        if design_keywords:
            st.subheader("Top Keywords")
            
            # Convert to DataFrame
            df_keywords = pd.DataFrame(design_keywords)
            
            # Create chart
            fig = px.bar(
                df_keywords,
                x="keyword",
                y="count",
                title="Designs by Keyword",
                color="keyword",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig.update_layout(
                xaxis_title="Keyword",
                yaxis_title="Count"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Get design creation over time
        design_creation = self.db.query(
            "SELECT COUNT(*) as count, DATE(created_at) as date FROM designs GROUP BY DATE(created_at) ORDER BY date"
        )
        
        if design_creation:
            st.subheader("Design Creation Over Time")
            
            # Convert to DataFrame
            df_creation = pd.DataFrame(design_creation)
            df_creation["date"] = pd.to_datetime(df_creation["date"])
            
            # Create chart
            fig = px.line(
                df_creation,
                x="date",
                y="count",
                title="Designs Created Over Time",
                markers=True
            )
            
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Count"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Get mockup distribution
        mockup_distribution = self.db.query(
            "SELECT product_type, COUNT(*) as count FROM mockups GROUP BY product_type"
        )
        
        if mockup_distribution:
            st.subheader("Mockup Distribution")
            
            # Convert to DataFrame
            df_mockups = pd.DataFrame(mockup_distribution)
            
            # Create chart
            fig = px.pie(
                df_mockups,
                values="count",
                names="product_type",
                title="Mockups by Product Type",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig.update_traces(textposition="inside", textinfo="percent+label")
            
            st.plotly_chart(fig, use_container_width=True)
    
    def _show_product_analytics(self):
        """Show product analytics tab."""
        st.header("Product Analytics")
        
        # Get product status distribution
        status_distribution = self.db.query(
            "SELECT status, COUNT(*) as count FROM products GROUP BY status"
        )
        
        if status_distribution:
            st.subheader("Product Status Distribution")
            
            # Convert to DataFrame
            df_status = pd.DataFrame(status_distribution)
            
            # Create chart
            fig = px.pie(
                df_status,
                values="count",
                names="status",
                title="Products by Status",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig.update_traces(textposition="inside", textinfo="percent+label")
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Get product creation over time
        product_creation = self.db.query(
            "SELECT COUNT(*) as count, DATE(created_at) as date FROM products GROUP BY DATE(created_at) ORDER BY date"
        )
        
        if product_creation:
            st.subheader("Product Creation Over Time")
            
            # Convert to DataFrame
            df_creation = pd.DataFrame(product_creation)
            df_creation["date"] = pd.to_datetime(df_creation["date"])
            
            # Create chart
            fig = px.line(
                df_creation,
                x="date",
                y="count",
                title="Products Created Over Time",
                markers=True
            )
            
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Count"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Get platform and product type distribution
        platform_product_distribution = self.db.query(
            "SELECT platform, product_type, COUNT(*) as count FROM products GROUP BY platform, product_type"
        )
        
        if platform_product_distribution:
            st.subheader("Platform and Product Type Distribution")
            
            # Convert to DataFrame
            df_platform_product = pd.DataFrame(platform_product_distribution)
            
            # Create chart
            fig = px.bar(
                df_platform_product,
                x="platform",
                y="count",
                color="product_type",
                title="Products by Platform and Type",
                barmode="group",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig.update_layout(
                xaxis_title="Platform",
                yaxis_title="Count"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Get top tags
        top_tags = self.db.query(
            "SELECT tag, COUNT(*) as count FROM tags GROUP BY tag ORDER BY count DESC LIMIT 20"
        )
        
        if top_tags:
            st.subheader("Top Tags")
            
            # Convert to DataFrame
            df_tags = pd.DataFrame(top_tags)
            
            # Create chart
            fig = px.bar(
                df_tags,
                x="tag",
                y="count",
                title="Most Used Tags",
                color="tag",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig.update_layout(
                xaxis_title="Tag",
                yaxis_title="Count"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def _show_trend_analytics(self):
        """Show trend analytics tab."""
        st.header("Trend Analytics")
        
        # Get trends from database
        trends = self.db.query(
            "SELECT * FROM trends ORDER BY created_at DESC LIMIT 100"
        )
        
        if trends:
            # Convert to DataFrame
            df_trends = pd.DataFrame(trends)
            
            # Group by keyword and get latest score
            df_trends["created_at"] = pd.to_datetime(df_trends["created_at"])
            df_trends = df_trends.sort_values("created_at", ascending=False)
            df_latest_trends = df_trends.drop_duplicates(subset=["keyword"])
            
            # Sort by score
            df_latest_trends = df_latest_trends.sort_values("score", ascending=False)
            
            # Display top trends
            st.subheader("Top Trends")
            
            # Create chart
            fig = px.bar(
                df_latest_trends.head(20),
                x="keyword",
                y="score",
                title="Top Trending Keywords",
                color="keyword",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig.update_layout(
                xaxis_title="Keyword",
                yaxis_title="Trend Score"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display trend history for selected keyword
            st.subheader("Trend History")
            
            selected_keyword = st.selectbox(
                "Select Keyword",
                df_trends["keyword"].unique()
            )
            
            if selected_keyword:
                # Filter trends for selected keyword
                df_keyword_trends = df_trends[df_trends["keyword"] == selected_keyword]
                df_keyword_trends = df_keyword_trends.sort_values("created_at")
                
                # Create chart
                fig = px.line(
                    df_keyword_trends,
                    x="created_at",
                    y="score",
                    title=f"Trend History for '{selected_keyword}'",
                    markers=True
                )
                
                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Trend Score"
                )
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No trend data available. Run trend analysis first.")