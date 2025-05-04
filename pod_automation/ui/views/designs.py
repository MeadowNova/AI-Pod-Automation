"""
Designs view for POD Automation System dashboard.
Provides UI for generating and managing designs.
"""

import os
import sys
import logging
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st

# Import utilities
from pod_automation.config.logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)

class DesignsView:
    """Designs view for POD Automation System dashboard."""
    
    def __init__(self, system, db):
        """Initialize designs view.
        
        Args:
            system: POD Automation System instance
            db: Database instance
        """
        self.system = system
        self.db = db
    
    def show(self):
        """Show designs view."""
        st.title("Designs")
        
        # Add tabs
        tab1, tab2, tab3 = st.tabs(["Generate Design", "Manage Designs", "Create Mockups"])
        
        with tab1:
            self._show_generate_design()
        
        with tab2:
            self._show_manage_designs()
        
        with tab3:
            self._show_create_mockups()
    
    def _show_generate_design(self):
        """Show generate design tab."""
        st.header("Generate Design")
        
        with st.form("generate_design_form"):
            # Input fields
            keyword = st.text_input("Keyword", "cat lover")
            
            num_designs = st.slider("Number of Designs", 1, 10, 3)
            
            style = st.selectbox(
                "Style",
                ["None", "Minimalist", "Vintage", "Watercolor", "Geometric", "Abstract", "Cartoon", "Realistic"],
                index=0
            )
            
            colors_input = st.text_input("Colors (comma-separated, optional)")
            
            advanced_options = st.expander("Advanced Options")
            
            with advanced_options:
                use_trend_analysis = st.checkbox("Use Trend Analysis", value=False)
                
                custom_prompt = st.text_area("Custom Prompt (optional)")
            
            submitted = st.form_submit_button("Generate Design")
            
            if submitted:
                with st.spinner("Generating designs..."):
                    # Parse colors
                    colors = [color.strip() for color in colors_input.split(",")] if colors_input else None
                    
                    # Set style to None if "None" is selected
                    style = None if style == "None" else style
                    
                    # Generate designs
                    designs = self.system.design_pipeline.run_pipeline(
                        analyze_trends=use_trend_analysis,
                        base_keyword=keyword,
                        num_designs=num_designs,
                        style=style,
                        colors=colors,
                        custom_prompt=custom_prompt if custom_prompt else None
                    )
                
                # Display results
                if designs:
                    st.success(f"Generated {len(designs)} designs!")
                    
                    # Save designs to database
                    design_ids = []
                    
                    for design_path in designs:
                        design_name = os.path.basename(design_path)
                        
                        design_data = {
                            "name": design_name,
                            "path": design_path,
                            "keyword": keyword,
                            "prompt": self.system.design_pipeline.last_prompt,
                            "metadata": json.dumps({
                                "style": style,
                                "colors": colors,
                                "use_trend_analysis": use_trend_analysis,
                                "custom_prompt": custom_prompt
                            })
                        }
                        
                        design_id = self.db.create("designs", design_data)
                        design_ids.append(design_id)
                    
                    # Display designs
                    for i, design_path in enumerate(designs):
                        st.subheader(f"Design {i+1}")
                        st.image(design_path)
                        st.write(f"Design ID: {design_ids[i]}")
                        st.write(f"Path: {design_path}")
                        
                        # Add actions
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("Create Mockups", key=f"mockups_{i}"):
                                st.session_state.create_mockups_design_id = design_ids[i]
                                st.session_state.create_mockups_design_path = design_path
                                st.session_state.active_tab = "Create Mockups"
                        
                        with col2:
                            if st.button("Publish", key=f"publish_{i}"):
                                st.session_state.publish_design_id = design_ids[i]
                                st.session_state.publish_design_path = design_path
                else:
                    st.error("Failed to generate designs. Please try again.")
    
    def _show_manage_designs(self):
        """Show manage designs tab."""
        st.header("Manage Designs")
        
        # Add filters
        col1, col2 = st.columns(2)
        
        with col1:
            keyword_filter = st.text_input("Filter by Keyword")
        
        with col2:
            sort_by = st.selectbox(
                "Sort by",
                ["Newest First", "Oldest First", "Keyword (A-Z)", "Keyword (Z-A)"]
            )
        
        # Build query
        query = "SELECT * FROM designs"
        params = []
        
        if keyword_filter:
            query += " WHERE keyword LIKE ?"
            params.append(f"%{keyword_filter}%")
        
        if sort_by == "Newest First":
            query += " ORDER BY created_at DESC"
        elif sort_by == "Oldest First":
            query += " ORDER BY created_at ASC"
        elif sort_by == "Keyword (A-Z)":
            query += " ORDER BY keyword ASC"
        elif sort_by == "Keyword (Z-A)":
            query += " ORDER BY keyword DESC"
        
        query += " LIMIT 100"
        
        # Execute query
        designs = self.db.query(query, tuple(params))
        
        # Display designs
        if designs:
            st.write(f"Found {len(designs)} designs")
            
            # Create a grid layout
            cols = st.columns(3)
            
            for i, design in enumerate(designs):
                with cols[i % 3]:
                    if os.path.exists(design["path"]):
                        st.image(design["path"], caption=design["name"])
                    else:
                        st.warning(f"Image not found: {design['path']}")
                    
                    st.write(f"ID: {design['id']}")
                    st.write(f"Keyword: {design['keyword']}")
                    st.write(f"Created: {design['created_at']}")
                    
                    # Add actions
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("Details", key=f"details_{design['id']}"):
                            st.session_state.design_details_id = design['id']
                    
                    with col2:
                        if st.button("Delete", key=f"delete_{design['id']}"):
                            if self.db.delete("designs", design['id']):
                                st.success(f"Deleted design with ID {design['id']}")
                                st.rerun()
        else:
            st.info("No designs found.")
        
        # Show design details if requested
        if hasattr(st.session_state, "design_details_id"):
            design_id = st.session_state.design_details_id
            design = self.db.read("designs", design_id)
            
            if design:
                st.subheader(f"Design Details: {design['name']}")
                
                if os.path.exists(design["path"]):
                    st.image(design["path"], caption=design["name"])
                else:
                    st.warning(f"Image not found: {design['path']}")
                
                st.write(f"ID: {design['id']}")
                st.write(f"Keyword: {design['keyword']}")
                st.write(f"Created: {design['created_at']}")
                
                # Show prompt
                st.subheader("Prompt")
                st.write(design["prompt"])
                
                # Show metadata
                if design["metadata"]:
                    try:
                        metadata = json.loads(design["metadata"])
                        st.subheader("Metadata")
                        st.json(metadata)
                    except:
                        pass
                
                # Get mockups for design
                mockups_query = "SELECT * FROM mockups WHERE design_id = ?"
                mockups = self.db.query(mockups_query, (design_id,))
                
                if mockups:
                    st.subheader("Mockups")
                    
                    for mockup in mockups:
                        st.write(f"Product Type: {mockup['product_type']}")
                        
                        if os.path.exists(mockup["path"]):
                            st.image(mockup["path"], caption=mockup["product_type"])
                        else:
                            st.warning(f"Mockup image not found: {mockup['path']}")
                
                # Get products for design
                products_query = "SELECT * FROM products WHERE design_id = ?"
                products = self.db.query(products_query, (design_id,))
                
                if products:
                    st.subheader("Products")
                    
                    for product in products:
                        st.write(f"Title: {product['title']}")
                        st.write(f"Product Type: {product['product_type']}")
                        st.write(f"Platform: {product['platform']}")
                        st.write(f"Status: {product['status']}")
                
                # Add actions
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("Create Mockups", key=f"details_mockups_{design_id}"):
                        st.session_state.create_mockups_design_id = design_id
                        st.session_state.create_mockups_design_path = design["path"]
                        st.session_state.active_tab = "Create Mockups"
                
                with col2:
                    if st.button("Publish", key=f"details_publish_{design_id}"):
                        st.session_state.publish_design_id = design_id
                        st.session_state.publish_design_path = design["path"]
                
                with col3:
                    if st.button("Close", key=f"details_close_{design_id}"):
                        del st.session_state.design_details_id
                        st.rerun()
    
    def _show_create_mockups(self):
        """Show create mockups tab."""
        st.header("Create Mockups")
        
        # Check if design ID is provided
        design_id = st.session_state.get("create_mockups_design_id")
        design_path = st.session_state.get("create_mockups_design_path")
        
        if design_id and design_path:
            # Get design from database
            design = self.db.read("designs", design_id)
            
            if design:
                st.subheader(f"Create Mockups for: {design['name']}")
                
                if os.path.exists(design["path"]):
                    st.image(design["path"], caption=design["name"])
                else:
                    st.warning(f"Image not found: {design['path']}")
                
                with st.form("create_mockups_form"):
                    # Input fields
                    product_types = st.multiselect(
                        "Product Types",
                        ["t-shirt", "hoodie", "mug", "poster", "phone case"],
                        ["t-shirt"]
                    )
                    
                    submitted = st.form_submit_button("Create Mockups")
                    
                    if submitted:
                        with st.spinner("Creating mockups..."):
                            # Create mockups
                            mockups = self.system.mockup_generator.create_mockups_for_design(
                                design["path"],
                                product_types=product_types
                            )
                        
                        # Display results
                        if mockups:
                            st.success(f"Created {len(mockups)} mockups!")
                            
                            # Save mockups to database
                            mockup_ids = []
                            
                            for product_type, mockup_path in mockups.items():
                                mockup_data = {
                                    "design_id": design_id,
                                    "product_type": product_type,
                                    "path": mockup_path,
                                    "metadata": json.dumps({
                                        "created_at": datetime.now().isoformat()
                                    })
                                }
                                
                                mockup_id = self.db.create("mockups", mockup_data)
                                mockup_ids.append(mockup_id)
                            
                            # Display mockups
                            for product_type, mockup_path in mockups.items():
                                st.subheader(f"{product_type.title()} Mockup")
                                st.image(mockup_path)
                        else:
                            st.error("Failed to create mockups. Please try again.")
            else:
                st.error(f"Design with ID {design_id} not found.")
        else:
            # Show design selection
            st.subheader("Select Design")
            
            # Get designs from database
            designs = self.db.query(
                "SELECT * FROM designs ORDER BY created_at DESC LIMIT 100"
            )
            
            if designs:
                # Create a grid layout
                cols = st.columns(3)
                
                for i, design in enumerate(designs):
                    with cols[i % 3]:
                        if os.path.exists(design["path"]):
                            st.image(design["path"], caption=design["name"])
                        else:
                            st.warning(f"Image not found: {design['path']}")
                        
                        st.write(f"ID: {design['id']}")
                        st.write(f"Keyword: {design['keyword']}")
                        
                        if st.button("Select", key=f"select_{design['id']}"):
                            st.session_state.create_mockups_design_id = design['id']
                            st.session_state.create_mockups_design_path = design['path']
                            st.rerun()
            else:
                st.info("No designs found. Generate designs first.")