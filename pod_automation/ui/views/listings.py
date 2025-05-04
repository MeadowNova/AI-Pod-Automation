"""
Listings view for POD Automation System dashboard.
Provides UI for managing and optimizing listings.
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

class ListingsView:
    """Listings view for POD Automation System dashboard."""
    
    def __init__(self, system, db):
        """Initialize listings view.
        
        Args:
            system: POD Automation System instance
            db: Database instance
        """
        self.system = system
        self.db = db
    
    def show(self):
        """Show listings view."""
        st.title("Listings")
        
        # Add tabs
        tab1, tab2, tab3 = st.tabs(["Optimize Listing", "Manage Listings", "Import Listings"])
        
        with tab1:
            self._show_optimize_listing()
        
        with tab2:
            self._show_manage_listings()
        
        with tab3:
            self._show_import_listings()
    
    def _show_optimize_listing(self):
        """Show optimize listing tab."""
        st.header("Optimize Listing")
        
        with st.form("optimize_listing_form"):
            # Input fields
            keyword = st.text_input("Keyword", "cat lover")
            
            product_type = st.selectbox(
                "Product Type",
                ["t-shirt", "hoodie", "mug", "poster", "phone case"]
            )
            
            title = st.text_input("Title (optional)")
            
            description = st.text_area("Description (optional)")
            
            tags_input = st.text_input("Tags (comma-separated, optional)")
            
            submitted = st.form_submit_button("Optimize Listing")
            
            if submitted:
                with st.spinner("Optimizing listing..."):
                    # Parse tags
                    tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else None
                    
                    # Optimize listing
                    optimized_listing = self.system.seo_optimizer.optimize_listing(
                        keyword,
                        product_type,
                        title=title,
                        description=description,
                        tags=tags
                    )
                
                # Display results
                st.success("Listing optimized successfully!")
                
                st.subheader("Optimized Title")
                st.write(optimized_listing["title"])
                st.write(f"Character count: {len(optimized_listing['title'])}/140")
                
                st.subheader("Optimized Tags")
                st.write(", ".join(optimized_listing["tags"]))
                st.write(f"Tag count: {len(optimized_listing['tags'])}/13")
                
                st.subheader("Optimized Description")
                st.write(optimized_listing["description"])
                
                # Save to database
                if st.button("Save to Database"):
                    # Create product record
                    product_data = {
                        "title": optimized_listing["title"],
                        "description": optimized_listing["description"],
                        "product_type": product_type,
                        "platform": "draft",
                        "status": "optimized",
                        "metadata": json.dumps({
                            "keyword": keyword,
                            "optimization_date": datetime.now().isoformat()
                        })
                    }
                    
                    product_id = self.db.create("products", product_data)
                    
                    # Create tags records
                    for tag in optimized_listing["tags"]:
                        tag_data = {
                            "product_id": product_id,
                            "tag": tag
                        }
                        
                        self.db.create("tags", tag_data)
                    
                    st.success(f"Saved to database with ID {product_id}")
    
    def _show_manage_listings(self):
        """Show manage listings tab."""
        st.header("Manage Listings")
        
        # Add filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            platform_filter = st.selectbox(
                "Platform",
                ["All", "Etsy", "Printify", "Draft"],
                index=0
            )
        
        with col2:
            status_filter = st.selectbox(
                "Status",
                ["All", "Optimized", "Published", "Draft"],
                index=0
            )
        
        with col3:
            product_type_filter = st.selectbox(
                "Product Type",
                ["All", "t-shirt", "hoodie", "mug", "poster", "phone case"],
                index=0
            )
        
        # Build query
        query = "SELECT * FROM products"
        params = []
        
        conditions = []
        
        if platform_filter != "All":
            conditions.append("platform = ?")
            params.append(platform_filter.lower())
        
        if status_filter != "All":
            conditions.append("status = ?")
            params.append(status_filter.lower())
        
        if product_type_filter != "All":
            conditions.append("product_type = ?")
            params.append(product_type_filter)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY created_at DESC LIMIT 100"
        
        # Execute query
        products = self.db.query(query, tuple(params))
        
        # Display products
        if products:
            st.write(f"Found {len(products)} listings")
            
            for product in products:
                with st.expander(f"{product['title']} ({product['product_type']})"):
                    st.write(f"Platform: {product['platform']}")
                    st.write(f"Status: {product['status']}")
                    st.write(f"Created: {product['created_at']}")
                    
                    # Get tags for product
                    tags_query = "SELECT tag FROM tags WHERE product_id = ?"
                    tags_result = self.db.query(tags_query, (product['id'],))
                    
                    tags = [tag["tag"] for tag in tags_result]
                    
                    st.write(f"Tags: {', '.join(tags)}")
                    
                    # Get design for product
                    if product['design_id']:
                        design = self.db.read("designs", product['design_id'])
                        
                        if design and os.path.exists(design['path']):
                            st.image(design['path'], caption=design['name'])
                    
                    # Add actions
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("Edit", key=f"edit_{product['id']}"):
                            st.session_state.edit_product_id = product['id']
                    
                    with col2:
                        if st.button("Delete", key=f"delete_{product['id']}"):
                            if self.db.delete("products", product['id']):
                                st.success(f"Deleted product with ID {product['id']}")
                                st.rerun()
        else:
            st.info("No listings found.")
        
        # Edit product if requested
        if hasattr(st.session_state, "edit_product_id"):
            product_id = st.session_state.edit_product_id
            product = self.db.read("products", product_id)
            
            if product:
                st.subheader(f"Edit Listing: {product['title']}")
                
                with st.form("edit_product_form"):
                    # Input fields
                    title = st.text_input("Title", product['title'])
                    
                    description = st.text_area("Description", product['description'])
                    
                    # Get tags for product
                    tags_query = "SELECT tag FROM tags WHERE product_id = ?"
                    tags_result = self.db.query(tags_query, (product_id,))
                    
                    tags = [tag["tag"] for tag in tags_result]
                    
                    tags_input = st.text_input("Tags (comma-separated)", ", ".join(tags))
                    
                    status = st.selectbox(
                        "Status",
                        ["draft", "optimized", "published"],
                        index=["draft", "optimized", "published"].index(product['status']) if product['status'] in ["draft", "optimized", "published"] else 0
                    )
                    
                    submitted = st.form_submit_button("Save Changes")
                    
                    if submitted:
                        # Update product
                        product_data = {
                            "title": title,
                            "description": description,
                            "status": status,
                            "updated_at": datetime.now().isoformat()
                        }
                        
                        if self.db.update("products", product_id, product_data):
                            # Parse tags
                            new_tags = [tag.strip() for tag in tags_input.split(",")]
                            
                            # Delete existing tags
                            self.db.query(f"DELETE FROM tags WHERE product_id = ?", (product_id,))
                            
                            # Create new tags
                            for tag in new_tags:
                                tag_data = {
                                    "product_id": product_id,
                                    "tag": tag
                                }
                                
                                self.db.create("tags", tag_data)
                            
                            st.success(f"Updated product with ID {product_id}")
                            
                            # Clear edit product ID
                            del st.session_state.edit_product_id
                            
                            # Rerun to refresh
                            st.rerun()
    
    def _show_import_listings(self):
        """Show import listings tab."""
        st.header("Import Listings")
        
        # Add import options
        import_source = st.selectbox(
            "Import Source",
            ["Etsy", "Printify"]
        )
        
        if import_source == "Etsy":
            with st.form("import_etsy_form"):
                # Input fields
                shop_id = st.text_input(
                    "Etsy Shop ID",
                    value=self.system.config.get("etsy.shop_id", "")
                )
                
                limit = st.slider("Number of Listings", 1, 100, 20)
                
                submitted = st.form_submit_button("Import Listings")
                
                if submitted:
                    with st.spinner("Importing listings from Etsy..."):
                        # TODO: Implement Etsy import
                        st.error("Etsy import not implemented yet")
        
        elif import_source == "Printify":
            with st.form("import_printify_form"):
                # Input fields
                shop_id = st.text_input(
                    "Printify Shop ID",
                    value=self.system.config.get("printify.shop_id", "")
                )
                
                limit = st.slider("Number of Products", 1, 100, 20)
                
                submitted = st.form_submit_button("Import Products")
                
                if submitted:
                    with st.spinner("Importing products from Printify..."):
                        # TODO: Implement Printify import
                        st.error("Printify import not implemented yet")