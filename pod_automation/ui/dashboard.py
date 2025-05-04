"""
Streamlit dashboard for POD Automation System.
Provides a user-friendly interface for interacting with the system.
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
from pod_automation.utils.logging_config import get_logger
from pod_automation.core.config import get_config
from pod_automation.core.system import PODAutomationSystem

# Import views - commented out until these are implemented
# from pod_automation.ui.views.listings import ListingsView
# from pod_automation.ui.views.designs import DesignsView
# from pod_automation.ui.views.analytics import AnalyticsView

# Initialize logger
logger = get_logger(__name__)

class Dashboard:
    """Streamlit dashboard for POD Automation System."""

    def __init__(self, system: Optional[PODAutomationSystem] = None):
        """Initialize dashboard.

        Args:
            system: POD Automation System instance (optional)
        """
        # Initialize system
        self.system = system or PODAutomationSystem()

        # Initialize database - temporarily disabled
        self.db = None

        # Initialize workflow manager - temporarily disabled
        self.workflow_manager = None

        # Initialize views - temporarily disabled
        self.listings_view = None
        self.designs_view = None
        self.analytics_view = None

    def run_dashboard(self):
        """Run the Streamlit dashboard."""
        # Set page config
        st.set_page_config(
            page_title="POD Automation System",
            page_icon="🚀",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # Add sidebar
        self._add_sidebar()

        # Add main content
        self._add_main_content()

    def _add_sidebar(self):
        """Add sidebar to dashboard."""
        with st.sidebar:
            st.title("POD Automation System")
            st.markdown("---")

            # Add navigation
            st.header("Navigation")
            page = st.radio(
                "Select Page",
                ["Dashboard", "Listings", "Designs", "Analytics", "Settings"]
            )

            st.markdown("---")

            # Add system status
            st.header("System Status")

            # Validate API connections
            if st.button("Validate API Connections"):
                with st.spinner("Validating API connections..."):
                    validation = self.system.validate_api_connections()

                st.write("API Connections:")
                st.write(f"- Printify: {'✅' if validation['printify'] else '❌'}")
                st.write(f"- Etsy: {'✅' if validation['etsy'] else '❌'}")
                st.write(f"- Stable Diffusion: {'✅' if validation['stable_diffusion'] else '❌'}")

            st.markdown("---")

            # Add about section
            st.header("About")
            st.write("POD Automation System")
            st.write("Version 1.0.0")
            st.write("© 2023 POD Automation")

            # Store page selection in session state
            st.session_state.page = page

    def _add_main_content(self):
        """Add main content to dashboard."""
        # Get page from session state
        page = st.session_state.get("page", "Dashboard")

        # Display page
        if page == "Dashboard":
            self._show_dashboard()
        elif page == "Listings":
            # Temporarily show placeholder until ListingsView is implemented
            st.title("Listings")
            st.info("Listings view is under development.")
        elif page == "Designs":
            # Temporarily show placeholder until DesignsView is implemented
            st.title("Designs")
            st.info("Designs view is under development.")
        elif page == "Analytics":
            # Temporarily show placeholder until AnalyticsView is implemented
            st.title("Analytics")
            st.info("Analytics view is under development.")
        elif page == "Settings":
            self._show_settings()

    def _show_dashboard(self):
        """Show dashboard page."""
        st.title("Dashboard")

        # Add quick actions
        st.header("Quick Actions")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Generate Design", key="generate_design"):
                st.session_state.page = "Designs"

        with col2:
            if st.button("Optimize Listing", key="optimize_listing"):
                st.session_state.page = "Listings"

        with col3:
            if st.button("Run Full Pipeline", key="run_pipeline"):
                st.session_state.show_pipeline_form = True

        # Show pipeline form if requested
        if st.session_state.get("show_pipeline_form", False):
            st.subheader("Run Full Pipeline")

            with st.form("pipeline_form"):
                keyword = st.text_input("Keyword", "cat lover")
                product_types = st.multiselect(
                    "Product Types",
                    ["t-shirt", "hoodie", "mug", "poster", "phone case"],
                    ["t-shirt"]
                )
                publish = st.checkbox("Publish Products")

                submitted = st.form_submit_button("Run Pipeline")

                if submitted:
                    with st.spinner("Running pipeline..."):
                        # Temporarily disabled until full pipeline is implemented
                        # results = self.system.run_full_pipeline(
                        #     keyword=keyword,
                        #     product_types=product_types,
                        #     publish=publish
                        # )
                        results = {"status": "Pipeline functionality is under development"}

                    st.success("Pipeline completed!")
                    st.json(results)

        # Add recent workflows
        st.header("Recent Workflows")

        # Temporarily disabled until workflow manager is implemented
        # workflows = self.workflow_manager.list_workflows(limit=5)
        workflows = []

        if workflows:
            for workflow in workflows:
                with st.expander(f"{workflow['name']} ({workflow['status']})"):
                    st.write(f"Started: {workflow['started_at']}")
                    st.write(f"Completed: {workflow['completed_at']}")

                    # Get workflow steps
                    # steps = self.db.query(
                    #     "SELECT * FROM workflow_steps WHERE workflow_id = ? ORDER BY id",
                    #     (workflow['id'],)
                    # )
                    steps = []

                    if steps:
                        st.subheader("Steps")
                        for step in steps:
                            st.write(f"- {step['step_name']}: {step['status']}")
        else:
            st.info("No workflows found. Workflow functionality is under development.")

        # Add recent designs
        st.header("Recent Designs")

        # Temporarily disabled until database is implemented
        # designs = self.db.query(
        #     "SELECT * FROM designs ORDER BY created_at DESC LIMIT 5"
        # )
        designs = []

        if designs:
            for design in designs:
                with st.expander(f"{design['name']}"):
                    st.write(f"Created: {design['created_at']}")
                    st.write(f"Keyword: {design['keyword']}")

                    if os.path.exists(design['path']):
                        st.image(design['path'], caption=design['name'])
        else:
            st.info("No designs found. Design functionality is under development.")

        # Add recent products
        st.header("Recent Products")

        # Temporarily disabled until database is implemented
        # products = self.db.query(
        #     "SELECT * FROM products ORDER BY created_at DESC LIMIT 5"
        # )
        products = []

        if products:
            for product in products:
                with st.expander(f"{product['title']} ({product['product_type']})"):
                    st.write(f"Created: {product['created_at']}")
                    st.write(f"Platform: {product['platform']}")
                    st.write(f"Status: {product['status']}")

                    # Get design
                    # design = self.db.read("designs", product['design_id'])
                    design = None

                    if design and os.path.exists(design['path']):
                        st.image(design['path'], caption=design['name'])
        else:
            st.info("No products found. Product functionality is under development.")

    def _show_settings(self):
        """Show settings page."""
        st.title("Settings")

        # Add API settings
        st.header("API Settings")

        with st.form("api_settings_form"):
            # Printify API
            st.subheader("Printify API")
            printify_api_key = st.text_input(
                "Printify API Key",
                value=self.system.config.get("api.printify", ""),
                type="password"
            )
            printify_shop_id = st.text_input(
                "Printify Shop ID",
                value=self.system.config.get("printify.shop_id", "")
            )

            # Etsy API
            st.subheader("Etsy API")
            etsy_api_key = st.text_input(
                "Etsy API Key",
                value=self.system.config.get("api.etsy", ""),
                type="password"
            )
            etsy_api_secret = st.text_input(
                "Etsy API Secret",
                value=self.system.config.get("etsy.api_secret", ""),
                type="password"
            )
            etsy_shop_id = st.text_input(
                "Etsy Shop ID",
                value=self.system.config.get("etsy.shop_id", "")
            )

            # Stable Diffusion API
            st.subheader("Stable Diffusion API")
            stable_diffusion_api_key = st.text_input(
                "OpenRouter API Key",
                value=self.system.config.get("api.openrouter", ""),
                type="password"
            )

            submitted = st.form_submit_button("Save Settings")

            if submitted:
                # Save API keys to config
                self.system.config.set("api.printify", printify_api_key)
                self.system.config.set("printify.shop_id", printify_shop_id)
                self.system.config.set("api.etsy", etsy_api_key)
                self.system.config.set("etsy.api_secret", etsy_api_secret)
                self.system.config.set("etsy.shop_id", etsy_shop_id)
                self.system.config.set("api.openrouter", stable_diffusion_api_key)

                # Save config
                self.system.config.save_config()

                # Reinitialize components
                self.system.initialize_components()

                st.success("Settings saved successfully!")

        # Add system settings
        st.header("System Settings")

        with st.form("system_settings_form"):
            # Data directories
            st.subheader("Data Directories")
            data_dir = st.text_input(
                "Data Directory",
                value=self.system.config.get("data_dir", "data")
            )

            # Default product types
            st.subheader("Default Product Types")
            default_product_types = st.multiselect(
                "Default Product Types",
                ["t-shirt", "hoodie", "mug", "poster", "phone case"],
                self.system.config.get("default_product_types", ["t-shirt"])
            )

            submitted = st.form_submit_button("Save Settings")

            if submitted:
                # Save settings to config
                self.system.config.set("data_dir", data_dir)
                self.system.config.set("default_product_types", default_product_types)

                # Save config
                self.system.config.save_config()

                st.success("Settings saved successfully!")


def main():
    """Run the dashboard."""
    try:
        # Create system
        system = PODAutomationSystem()

        # Create dashboard
        dashboard = Dashboard(system)

        # Run dashboard
        dashboard.run_dashboard()
    except Exception as e:
        import streamlit as st
        st.error(f"Error running dashboard: {str(e)}")
        logger.error(f"Error running dashboard: {str(e)}")


if __name__ == "__main__":
    main()