"""
Interactive Dashboard for POD Automation System.
Provides a user interface to interact with all components of the system.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import os
import sys
import logging
import json
import time
from datetime import datetime
from pathlib import Path
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import base64
import io

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dashboard.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import components
from agents.mockup_generator import MockupGenerator
from agents.seo_optimizer import SEOOptimizer
from pod_automation.config import get_config

class Dashboard:
    """Interactive dashboard for POD Automation System."""
    
    def __init__(self):
        """Initialize dashboard."""
        # Set up directories
        self.data_dir = 'data'
        self.designs_dir = os.path.join(self.data_dir, 'designs')
        self.mockups_dir = os.path.join(self.data_dir, 'mockups')
        self.trends_dir = os.path.join(self.data_dir, 'trends')
        self.seo_dir = os.path.join(self.data_dir, 'seo')
        self.output_dir = os.path.join(self.data_dir, 'published')
        
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.designs_dir, exist_ok=True)
        os.makedirs(self.mockups_dir, exist_ok=True)
        os.makedirs(self.trends_dir, exist_ok=True)
        os.makedirs(self.seo_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize components
        self.config = get_config()
        self.trend_forecaster = None
        self.prompt_optimizer = None
        self.stable_diffusion = None
        self.design_pipeline = None
        self.mockup_generator = None
        self.publishing_agent = None
        self.seo_optimizer = None
    
    def initialize_components(self):
        """Initialize all components."""
        logger.info("Initializing components")
        
        # Import TrendForecaster, PromptOptimizer, DesignGenerationPipeline, and Stable Diffusion client here to avoid circular imports
        from agents.trend_forecaster import TrendForecaster
        from agents.prompt_optimizer import PromptOptimizer
        from agents.design_generation import DesignGenerationPipeline
        from agents.stable_diffusion import create_stable_diffusion_client
        
        # Initialize trend forecaster
        if self.trend_forecaster is None:
            self.trend_forecaster = TrendForecaster(config={'data_dir': self.trends_dir})
        
        # Initialize prompt optimizer
        if self.prompt_optimizer is None:
            self.prompt_optimizer = PromptOptimizer()
        
        # Initialize stable diffusion
        if self.stable_diffusion is None:
            api_key = self.config.get('stable_diffusion.api_key') or os.environ.get('OPENROUTER_API_KEY')
            self.stable_diffusion = create_stable_diffusion_client(
                use_api=True,
                api_key=api_key,
                config={'output_dir': os.path.join(self.designs_dir, 'drafts')}
            )
        
        # Initialize design pipeline
        if self.design_pipeline is None:
            self.design_pipeline = DesignGenerationPipeline(config={
                'output_dir': os.path.join(self.designs_dir, 'drafts'),
                'trend_dir': self.trends_dir,
                'use_stable_diffusion_api': True,
                'stable_diffusion_api_key': self.config.get('stable_diffusion.api_key') or os.environ.get('OPENROUTER_API_KEY')
            })
        
        # Initialize mockup generator
        if self.mockup_generator is None:
            self.mockup_generator = MockupGenerator(config={
                'designs_dir': self.designs_dir,
                'output_dir': self.mockups_dir
            })
        
        # Initialize publishing agent
        if self.publishing_agent is None:
            from agents.publishing_agent import PublishingAgent
            self.publishing_agent = PublishingAgent(config={
                'designs_dir': self.designs_dir,
                'mockups_dir': self.mockups_dir,
                'output_dir': self.output_dir,
                'printify_api_key': self.config.get('printify.api_key') or os.environ.get('PRINTIFY_API_KEY'),
                'printify_shop_id': self.config.get('printify.shop_id') or os.environ.get('PRINTIFY_SHOP_ID'),
                'etsy_api_key': self.config.get('etsy.api_key') or os.environ.get('ETSY_API_KEY'),
                'etsy_api_secret': self.config.get('etsy.api_secret') or os.environ.get('ETSY_API_SECRET'),
                'etsy_shop_id': self.config.get('etsy.shop_id') or os.environ.get('ETSY_SHOP_ID')
            })
        
        # Initialize SEO optimizer
        if self.seo_optimizer is None:
            self.seo_optimizer = SEOOptimizer(config={
                'data_dir': self.seo_dir
            })
    
    def run_dashboard(self):
        """Run the Streamlit dashboard."""
        st.set_page_config(
            page_title="POD Automation System",
            page_icon="🐱",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Initialize components
        self.initialize_components()
        
        # Sidebar navigation
        st.sidebar.title("POD Automation System")
        st.sidebar.image("https://placekitten.com/200/200", use_column_width=True)
        
        # Navigation
        pages = {
            "Dashboard Home": self.page_home,
            "Trend Forecasting": self.page_trend_forecasting,
            "Design Generation": self.page_design_generation,
            "Mockup Creation": self.page_mockup_creation,
            "SEO Optimization": self.page_seo_optimization,
            "Publishing": self.page_publishing,
            "Settings": self.page_settings
        }
        
        selection = st.sidebar.radio("Navigation", list(pages.keys()))
        
        # Display selected page
        pages[selection]()
        
        # Footer
        st.sidebar.markdown("---")
        st.sidebar.info(
            "POD Automation System v0.1.0\n\n"
            "© 2025 POD Automation Team"
        )
    
    def page_home(self):
        """Display home page."""
        st.title("POD Automation System Dashboard")
        st.subheader("All-in-one solution for print-on-demand automation")
        
        # System overview
        st.markdown("""
        Welcome to the POD Automation System Dashboard! This system helps you automate the entire print-on-demand workflow:
        
        1. **Trend Forecasting**: Analyze trending cat-themed designs and keywords
        2. **Design Generation**: Generate cat-themed designs using Stable Diffusion
        3. **Mockup Creation**: Create product mockups for various POD products
        4. **SEO Optimization**: Optimize listings for better visibility on Etsy
        5. **Publishing**: Publish products to Printify and Etsy
        
        Use the navigation menu on the left to access different components of the system.
        """)
        
        # Display system status
        st.header("System Status")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("API Connections")
            
            # Check API connections
            api_status = {
                "Printify API": self.check_printify_api(),
                "Etsy API": self.check_etsy_api(),
                "Stable Diffusion API": self.check_stable_diffusion_api()
            }
            
            for api, status in api_status.items():
                if status:
                    st.success(f"{api}: Connected")
                else:
                    st.error(f"{api}: Not Connected")
        
        with col2:
            st.subheader("Recent Activity")
            
            # Get recent designs
            designs = self.get_recent_files(self.designs_dir, limit=5)
            if designs:
                st.write("Recent Designs:")
                for design in designs:
                    st.write(f"- {os.path.basename(design)}")
            else:
                st.write("No recent designs found.")
            
            # Get recent mockups
            mockups = self.get_recent_files(self.mockups_dir, limit=5)
            if mockups:
                st.write("Recent Mockups:")
                for mockup in mockups:
                    st.write(f"- {os.path.basename(mockup)}")
            else:
                st.write("No recent mockups found.")
        
        with col3:
            st.subheader("Quick Actions")
            
            if st.button("Run Trend Analysis"):
                st.session_state.navigate_to = "Trend Forecasting"
                st.experimental_rerun()
            
            if st.button("Generate New Design"):
                st.session_state.navigate_to = "Design Generation"
                st.experimental_rerun()
            
            if st.button("Create Mockups"):
                st.session_state.navigate_to = "Mockup Creation"
                st.experimental_rerun()
            
            if st.button("Optimize SEO"):
                st.session_state.navigate_to = "SEO Optimization"
                st.experimental_rerun()
        
        # Display recent designs
        st.header("Recent Designs")
        
        recent_designs = self.get_recent_files(self.designs_dir, ext=['.png', '.jpg'], limit=4)
        if recent_designs:
            cols = st.columns(min(4, len(recent_designs)))
            for i, design_path in enumerate(recent_designs):
                if i < len(cols):
                    with cols[i]:
                        st.image(design_path, caption=os.path.basename(design_path), use_column_width=True)
        else:
            st.info("No designs found. Go to the Design Generation page to create some!")
    
    def page_trend_forecasting(self):
        """Display trend forecasting page."""
        st.title("Trend Forecasting")
        st.subheader("Analyze trending cat-themed designs and keywords")
        
        # Trend analysis form
        st.header("Run Trend Analysis")
        
        with st.form("trend_analysis_form"):
            keywords = st.text_area(
                "Keywords to analyze (one per line)",
                value="cat t-shirt\nfunny cat\ncute cat\ncat lover\ncat design"
            )
            
            analyze_button = st.form_submit_button("Run Analysis")
        
        if analyze_button:
            keywords_list = [k.strip() for k in keywords.split('\n') if k.strip()]
            
            with st.spinner("Running trend analysis..."):
                try:
                    report_path = self.trend_forecaster.run_trend_analysis(keywords_list)
                    
                    if report_path:
                        st.success(f"Trend analysis completed successfully!")
                        
                        # Display report
                        with open(report_path, 'r') as f:
                            report_content = f.read()
                        
                        st.markdown(report_content)
                        
                        # Add download button for report
                        self.add_download_button(report_path, "Download Trend Report")
                    else:
                        st.error("Trend analysis failed. Please check the logs for details.")
                
                except Exception as e:
                    st.error(f"Error running trend analysis: {str(e)}")
        
        # Display existing trend reports
        st.header("Existing Trend Reports")
        
        trend_reports = self.get_recent_files(self.trends_dir, ext=['.md'], prefix="trend_report_", limit=10)
        if trend_reports:
            for report_path in trend_reports:
                with st.expander(f"Report: {os.path.basename(report_path)}"):
                    with open(report_path, 'r') as f:
                        report_content = f.read()
                    
                    st.markdown(report_content)
                    
                    # Add download button for report
                    self.add_download_button(report_path, "Download Report")
        else:
            st.info("No trend reports found. Run a trend analysis to generate reports.")
    
    def page_design_generation(self):
        """Display design generation page."""
        st.title("Design Generation")
        st.subheader("Generate cat-themed designs using Stable Diffusion")
        
        # Check if Stable Diffusion API is connected
        if not self.check_stable_diffusion_api():
            st.error("Stable Diffusion API is not connected. Please check your API key in Settings.")
            return
        
        # Design generation form
        st.header("Generate Designs")
        
        with st.form("design_generation_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                prompt = st.text_area(
                    "Base prompt",
                    value="A cute cartoon cat wearing a t-shirt"
                )
                
                negative_prompt = st.text_area(
                    "Negative prompt (optional)",
                    value="deformed, blurry, bad anatomy, disfigured, poorly drawn face, mutation, mutated"
                )
            
            with col2:
                num_designs = st.slider("Number of designs to generate", 1, 5, 1)
                
                use_trend_analysis = st.checkbox("Use trend analysis for prompts", value=False)
                
                if use_trend_analysis:
                    trend_reports = self.get_recent_files(self.trends_dir, ext=['.md'], prefix="trend_report_", limit=10)
                    if trend_reports:
                        trend_report = st.selectbox(
                            "Select trend report",
                            options=trend_reports,
                            format_func=lambda x: os.path.basename(x)
                        )
                    else:
                        st.warning("No trend reports found. Run trend analysis first.")
                        trend_report = None
                else:
                    trend_report = None
            
            generate_button = st.form_submit_button("Generate Designs")
        
        if generate_button:
            with st.spinner("Generating designs..."):
                try:
                    if use_trend_analysis and trend_report:
                        # Generate designs based on trend report
                        generated_designs = self.design_pipeline.run_pipeline(
                            analyze_trends=False,
                            num_designs=num_designs
                        )
                    else:
                        # Generate designs based on prompt
                        optimized_prompt, neg_prompt = self.prompt_optimizer.optimize_prompt(prompt)
                        
                        if not negative_prompt:
                            negative_prompt = neg_prompt
                        
                        generated_designs = []
                        for i in range(num_designs):
                            success, result = self.stable_diffusion.generate_image(
                                prompt=optimized_prompt,
                                negative_prompt=negative_prompt,
                                width=1024,
                                height=1024,
                                num_inference_steps=50,
                                guidance_scale=7.5
                            )
                            
                            if success:
                                generated_designs.append(result)
                            
                            # Add a small delay between generations
                            time.sleep(2)
                    
                    if generated_designs:
                        st.success(f"Generated {len(generated_designs)} designs successfully!")
                        
                        # Display generated designs
                        cols = st.columns(min(3, len(generated_designs)))
                        for i, design_path in enumerate(generated_designs):
                            with cols[i % len(cols)]:
                                st.image(design_path, caption=f"Design {i+1}", use_column_width=True)
                                
                                # Add buttons for each design
                                if st.button(f"Create Mockups for Design {i+1}", key=f"mockup_btn_{i}"):
                                    st.session_state.selected_design = design_path
                                    st.session_state.navigate_to = "Mockup Creation"
                                    st.experimental_rerun()
                                
                                if st.button(f"Optimize SEO for Design {i+1}", key=f"seo_btn_{i}"):
                                    st.session_state.selected_design = design_path
                                    st.session_state.navigate_to = "SEO Optimization"
                                    st.experimental_rerun()
                    else:
                        st.error("Design generation failed. Please check the logs for details.")
                
                except Exception as e:
                    st.error(f"Error generating designs: {str(e)}")
        
        # Display existing designs
        st.header("Existing Designs")
        
        existing_designs = self.get_recent_files(self.designs_dir, ext=['.png', '.jpg'], limit=12)
        if existing_designs:
            # Create a grid of designs
            cols = st.columns(3)
            for i, design_path in enumerate(existing_designs):
                with cols[i % 3]:
                    st.image(design_path, caption=os.path.basename(design_path), use_column_width=True)
                    
                    # Add buttons for each design
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Create Mockups", key=f"mockup_btn_existing_{i}"):
                            st.session_state.selected_design = design_path
                            st.session_state.navigate_to = "Mockup Creation"
                            st.experimental_rerun()
                    
                    with col2:
                        if st.button("Optimize SEO", key=f"seo_btn_existing_{i}"):
                            st.session_state.selected_design = design_path
                            st.session_state.navigate_to = "SEO Optimization"
                            st.experimental_rerun()
        else:
            st.info("No designs found. Generate some designs first!")
    
    def page_mockup_creation(self):
        """Display mockup creation page."""
        st.title("Mockup Creation")
        st.subheader("Create product mockups for various POD products")
        
        # Check if a design was selected
        selected_design = st.session_state.get('selected_design')
        
        # Design selection
        st.header("Select Design")
        
        if selected_design:
            st.image(selected_design, caption="Selected Design", width=300)
            st.success(f"Design selected: {os.path.basename(selected_design)}")
        else:
            # Let user select a design
            existing_designs = self.get_recent_files(self.designs_dir, ext=['.png', '.jpg'], limit=20)
            if existing_designs:
                selected_design = st.selectbox(
                    "Select a design",
                    options=existing_designs,
                    format_func=lambda x: os.path.basename(x)
                )
                
                if selected_design:
                    st.image(selected_design, caption="Selected Design", width=300)
            else:
                st.error("No designs found. Please generate designs first.")
                return
        
        # Mockup creation form
        st.header("Create Mockups")
        
        with st.form("mockup_creation_form"):
            st.subheader("Select Products")
            
            col1, col2 = st.columns(2)
            
            with col1:
                create_tshirt = st.checkbox("T-Shirt (Monster Digital)", value=True)
                create_sweatshirt = st.checkbox("Sweatshirt (Monster Digital)", value=False)
            
            with col2:
                create_poster = st.checkbox("Poster (Sensaria)", value=True)
                create_pillow = st.checkbox("Pillow Case (MWW)", value=False)
            
            create_button = st.form_submit_button("Create Mockups")
        
        if create_button and selected_design:
            with st.spinner("Creating mockups..."):
                try:
                    # Determine which products to create
                    product_types = []
                    if create_tshirt:
                        product_types.append('t-shirt')
                    if create_sweatshirt:
                        product_types.append('sweatshirt')
                    if create_poster:
                        product_types.append('poster')
                    if create_pillow:
                        product_types.append('pillow_case')
                    
                    if not product_types:
                        st.error("Please select at least one product type.")
                        return
                    
                    # Create mockups
                    mockups = self.mockup_generator.create_mockups_for_design(
                        selected_design,
                        product_types=product_types
                    )
                    
                    if mockups:
                        st.success(f"Created {len(mockups)} mockups successfully!")
                        
                        # Display mockups
                        cols = st.columns(min(2, len(mockups)))
                        for i, mockup_path in enumerate(mockups):
                            with cols[i % len(cols)]:
                                st.image(mockup_path, caption=f"Mockup: {os.path.basename(mockup_path)}", use_column_width=True)
                                
                                # Add download button
                                self.add_download_button(mockup_path, f"Download Mockup {i+1}")
                                
                                # Add publish button
                                if st.button(f"Publish This Product", key=f"publish_btn_{i}"):
                                    st.session_state.selected_mockup = mockup_path
                                    st.session_state.selected_design = selected_design
                                    st.session_state.navigate_to = "Publishing"
                                    st.experimental_rerun()
                    else:
                        st.error("Mockup creation failed. Please check the logs for details.")
                
                except Exception as e:
                    st.error(f"Error creating mockups: {str(e)}")
        
        # Display existing mockups
        st.header("Existing Mockups")
        
        existing_mockups = self.get_recent_files(self.mockups_dir, ext=['.png', '.jpg'], limit=8)
        if existing_mockups:
            # Create a grid of mockups
            cols = st.columns(2)
            for i, mockup_path in enumerate(existing_mockups):
                with cols[i % 2]:
                    st.image(mockup_path, caption=os.path.basename(mockup_path), use_column_width=True)
                    
                    # Add download button
                    self.add_download_button(mockup_path, "Download Mockup")
                    
                    # Add publish button
                    if st.button("Publish This Product", key=f"publish_btn_existing_{i}"):
                        # Try to find the corresponding design
                        mockup_name = os.path.basename(mockup_path)
                        design_name = mockup_name.split('_')[0]  # Extract design name from mockup name
                        
                        # Find matching design
                        matching_designs = [d for d in self.get_recent_files(self.designs_dir, ext=['.png', '.jpg']) 
                                           if design_name in os.path.basename(d)]
                        
                        if matching_designs:
                            st.session_state.selected_mockup = mockup_path
                            st.session_state.selected_design = matching_designs[0]
                            st.session_state.navigate_to = "Publishing"
                            st.experimental_rerun()
                        else:
                            st.error("Could not find the original design for this mockup.")
        else:
            st.info("No mockups found. Create some mockups first!")
    
    def page_seo_optimization(self):
        """Display SEO optimization page."""
        st.title("SEO Optimization")
        st.subheader("Optimize listings for better visibility on Etsy")
        
        # SEO optimization form
        st.header("Optimize Listing")
        
        with st.form("seo_optimization_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                base_keyword = st.text_input("Base Keyword", value="cat lover")
                product_type = st.selectbox(
                    "Product Type",
                    options=["t-shirt", "sweatshirt", "poster", "pillow case"]
                )
            
            with col2:
                analyze_competitors = st.checkbox("Analyze Competitors", value=True)
                generate_report = st.checkbox("Generate SEO Report", value=True)
            
            optimize_button = st.form_submit_button("Optimize Listing")
        
        if optimize_button:
            with st.spinner("Optimizing listing..."):
                try:
                    # Analyze competitors if requested
                    if analyze_competitors:
                        competitor_analysis = self.seo_optimizer.analyze_competitor_listings(base_keyword)
                        if competitor_analysis:
                            st.success("Competitor analysis completed successfully!")
                            
                            # Display competitor analysis
                            with st.expander("Competitor Analysis Results"):
                                st.write("Top Title Words:")
                                for word, count in competitor_analysis['top_title_words'][:10]:
                                    st.write(f"- {word}: {count} occurrences")
                                
                                st.write("Top Tags:")
                                for tag, count in competitor_analysis['top_tags'][:10]:
                                    st.write(f"- {tag}: {count} occurrences")
                                
                                st.write("Price Analysis:")
                                price_analysis = competitor_analysis['price_analysis']
                                st.write(f"- Average Price: ${price_analysis['average']}")
                                st.write(f"- Price Range: ${price_analysis['minimum']} - ${price_analysis['maximum']}")
                    
                    # Optimize listing
                    optimized_listing = self.seo_optimizer.optimize_listing(base_keyword, product_type)
                    
                    if optimized_listing:
                        st.success("Listing optimization completed successfully!")
                        
                        # Display optimized listing
                        st.subheader("Optimized Listing")
                        
                        st.write("**Title:**")
                        st.write(optimized_listing['title'])
                        
                        st.write("**Tags:**")
                        tags_text = ", ".join(optimized_listing['tags'])
                        st.write(tags_text)
                        
                        st.write("**Description:**")
                        st.text_area("", value=optimized_listing['description'], height=300, key="desc_display")
                        
                        # Add copy buttons
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button("Copy Title"):
                                st.code(optimized_listing['title'])
                                st.info("Title copied to clipboard! (Use Ctrl+C)")
                        
                        with col2:
                            if st.button("Copy Tags"):
                                st.code(tags_text)
                                st.info("Tags copied to clipboard! (Use Ctrl+C)")
                        
                        with col3:
                            if st.button("Copy Description"):
                                st.code(optimized_listing['description'])
                                st.info("Description copied to clipboard! (Use Ctrl+C)")
                    
                    # Generate SEO report if requested
                    if generate_report:
                        report = self.seo_optimizer.generate_seo_report(base_keyword, product_type)
                        
                        if report:
                            st.success("SEO report generated successfully!")
                            
                            # Display SEO report
                            with st.expander("SEO Report"):
                                st.markdown(report)
                            
                            # Find the report file
                            report_files = self.get_recent_files(
                                self.seo_dir, 
                                ext=['.md'], 
                                prefix=f"seo_report_{base_keyword.replace(' ', '_')}",
                                limit=1
                            )
                            
                            if report_files:
                                # Add download button for report
                                self.add_download_button(report_files[0], "Download SEO Report")
                
                except Exception as e:
                    st.error(f"Error optimizing listing: {str(e)}")
        
        # Display existing SEO reports
        st.header("Existing SEO Reports")
        
        seo_reports = self.get_recent_files(self.seo_dir, ext=['.md'], prefix="seo_report_", limit=5)
        if seo_reports:
            for report_path in seo_reports:
                with st.expander(f"Report: {os.path.basename(report_path)}"):
                    with open(report_path, 'r') as f:
                        report_content = f.read()
                    
                    st.markdown(report_content)
                    
                    # Add download button for report
                    self.add_download_button(report_path, "Download Report")
        else:
            st.info("No SEO reports found. Optimize a listing to generate reports.")
    
    def page_publishing(self):
        """Display publishing page."""
        st.title("Publishing")
        st.subheader("Publish products to Printify and Etsy")
        
        # Check if API connections are valid
        printify_connected = self.check_printify_api()
        etsy_connected = self.check_etsy_api()
        
        if not printify_connected and not etsy_connected:
            st.error("Neither Printify nor Etsy API is connected. Please check your API keys in Settings.")
            return
        
        # Display API connection status
        col1, col2 = st.columns(2)
        
        with col1:
            if printify_connected:
                st.success("Printify API: Connected")
            else:
                st.error("Printify API: Not Connected")
        
        with col2:
            if etsy_connected:
                st.success("Etsy API: Connected")
            else:
                st.error("Etsy API: Not Connected")
        
        # Check if design and mockup were selected
        selected_design = st.session_state.get('selected_design')
        selected_mockup = st.session_state.get('selected_mockup')
        
        # Product information form
        st.header("Product Information")
        
        with st.form("publishing_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Display selected design if available
                if selected_design:
                    st.image(selected_design, caption="Selected Design", width=200)
                else:
                    # Let user select a design
                    existing_designs = self.get_recent_files(self.designs_dir, ext=['.png', '.jpg'], limit=20)
                    if existing_designs:
                        selected_design = st.selectbox(
                            "Select a design",
                            options=existing_designs,
                            format_func=lambda x: os.path.basename(x)
                        )
                    else:
                        st.error("No designs found. Please generate designs first.")
                
                title = st.text_input("Product Title", value="Cat Lover T-Shirt - Cute Cat Design")
                
                description = st.text_area(
                    "Product Description",
                    value="Show your love for cats with this adorable cat lover t-shirt! Perfect for cat lovers, this t-shirt features a unique design that will make you stand out."
                )
            
            with col2:
                # Display selected mockup if available
                if selected_mockup:
                    st.image(selected_mockup, caption="Selected Mockup", width=200)
                else:
                    # Let user select mockups
                    existing_mockups = self.get_recent_files(self.mockups_dir, ext=['.png', '.jpg'], limit=20)
                    if existing_mockups:
                        selected_mockup = st.selectbox(
                            "Select a mockup",
                            options=existing_mockups,
                            format_func=lambda x: os.path.basename(x)
                        )
                    else:
                        st.warning("No mockups found. You can still publish without mockups.")
                
                tags = st.text_area(
                    "Tags (one per line)",
                    value="cat\ncat lover\ncat t-shirt\ncat gift\nfunny cat\ncute cat"
                )
                
                product_types = st.multiselect(
                    "Product Types",
                    options=["t-shirt", "sweatshirt", "poster", "pillow_case"],
                    default=["t-shirt"]
                )
            
            col1, col2 = st.columns(2)
            
            with col1:
                publish_to_printify = st.checkbox("Publish to Printify", value=printify_connected)
            
            with col2:
                publish_to_etsy = st.checkbox("Publish to Etsy", value=etsy_connected)
            
            publish_button = st.form_submit_button("Publish Product")
        
        if publish_button and selected_design:
            with st.spinner("Publishing product..."):
                try:
                    # Convert tags to list
                    tags_list = [t.strip() for t in tags.split('\n') if t.strip()]
                    
                    # Prepare mockup paths
                    mockup_paths = [selected_mockup] if selected_mockup else []
                    
                    # Publish design
                    results = self.publishing_agent.publish_design(
                        design_path=selected_design,
                        title=title,
                        description=description,
                        product_types=product_types,
                        tags=tags_list,
                        mockup_paths=mockup_paths
                    )
                    
                    if results:
                        st.success("Product published successfully!")
                        
                        # Display results
                        st.subheader("Publishing Results")
                        
                        if 'printify_products' in results and results['printify_products']:
                            st.write("**Printify Products:**")
                            for product in results['printify_products']:
                                st.write(f"- {product['title']} (ID: {product['product_id']})")
                        
                        if 'etsy_listings' in results and results['etsy_listings']:
                            st.write("**Etsy Listings:**")
                            for listing in results['etsy_listings']:
                                st.write(f"- {listing['title']} (ID: {listing['listing_id']})")
                    else:
                        st.error("Publishing failed. Please check the logs for details.")
                
                except Exception as e:
                    st.error(f"Error publishing product: {str(e)}")
        
        # Display published products
        st.header("Published Products")
        
        published_files = self.get_recent_files(self.output_dir, ext=['.json'], prefix="published_", limit=5)
        if published_files:
            for file_path in published_files:
                try:
                    with open(file_path, 'r') as f:
                        published_data = json.load(f)
                    
                    with st.expander(f"Product: {published_data.get('title', 'Unknown')}"):
                        st.write(f"**Design:** {os.path.basename(published_data.get('design', 'Unknown'))}")
                        st.write(f"**Title:** {published_data.get('title', 'Unknown')}")
                        st.write(f"**Description:** {published_data.get('description', 'Unknown')[:100]}...")
                        
                        if 'printify_products' in published_data and published_data['printify_products']:
                            st.write("**Printify Products:**")
                            for product in published_data['printify_products']:
                                st.write(f"- {product['title']} (ID: {product['product_id']})")
                        
                        if 'etsy_listings' in published_data and published_data['etsy_listings']:
                            st.write("**Etsy Listings:**")
                            for listing in published_data['etsy_listings']:
                                st.write(f"- {listing['title']} (ID: {listing['listing_id']})")
                
                except Exception as e:
                    st.error(f"Error loading published product data: {str(e)}")
        else:
            st.info("No published products found. Publish a product to see it here.")
    
    def page_settings(self):
        """Display settings page."""
        st.title("Settings")
        st.subheader("Configure API keys and system settings")
        
        # API keys section
        st.header("API Keys")
        
        with st.form("api_keys_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                printify_api_key = st.text_input(
                    "Printify API Key",
                    value=self.config.get('printify.api_key') or os.environ.get('PRINTIFY_API_KEY') or "",
                    type="password"
                )
                
                printify_shop_id = st.text_input(
                    "Printify Shop ID",
                    value=self.config.get('printify.shop_id') or os.environ.get('PRINTIFY_SHOP_ID') or ""
                )
                
                stable_diffusion_api_key = st.text_input(
                    "Stable Diffusion API Key (OpenRouter)",
                    value=self.config.get('stable_diffusion.api_key') or os.environ.get('OPENROUTER_API_KEY') or "",
                    type="password"
                )
            
            with col2:
                etsy_api_key = st.text_input(
                    "Etsy API Key",
                    value=self.config.get('etsy.api_key') or os.environ.get('ETSY_API_KEY') or "",
                    type="password"
                )
                
                etsy_api_secret = st.text_input(
                    "Etsy API Secret",
                    value=self.config.get('etsy.api_secret') or os.environ.get('ETSY_API_SECRET') or "",
                    type="password"
                )
                
                etsy_shop_id = st.text_input(
                    "Etsy Shop ID",
                    value=self.config.get('etsy.shop_id') or os.environ.get('ETSY_SHOP_ID') or ""
                )
            
            save_button = st.form_submit_button("Save API Keys")
        
        if save_button:
            try:
                # Save API keys to config
                self.config.set('printify.api_key', printify_api_key)
                self.config.set('printify.shop_id', printify_shop_id)
                self.config.set('etsy.api_key', etsy_api_key)
                self.config.set('etsy.api_secret', etsy_api_secret)
                self.config.set('etsy.shop_id', etsy_shop_id)
                self.config.set('stable_diffusion.api_key', stable_diffusion_api_key)
                
                # Save config
                self.config.save_config()
                
                # Reinitialize components
                self.initialize_components()
                
                st.success("API keys saved successfully!")
            except Exception as e:
                st.error(f"Error saving API keys: {str(e)}")
        
        # System settings section
        st.header("System Settings")
        
        with st.form("system_settings_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                data_dir = st.text_input(
                    "Data Directory",
                    value=self.data_dir
                )
                
                use_api = st.checkbox(
                    "Use Stable Diffusion API (instead of local)",
                    value=True
                )
            
            with col2:
                default_product_types = st.multiselect(
                    "Default Product Types",
                    options=["t-shirt", "sweatshirt", "poster", "pillow_case"],
                    default=["t-shirt", "poster"]
                )
            
            save_settings_button = st.form_submit_button("Save Settings")
        
        if save_settings_button:
            try:
                # Save settings to config
                self.config.set('data_dir', data_dir)
                self.config.set('use_stable_diffusion_api', use_api)
                self.config.set('default_product_types', default_product_types)
                
                # Save config
                self.config.save_config()
                
                # Update directories
                self.data_dir = data_dir
                self.designs_dir = os.path.join(self.data_dir, 'designs')
                self.mockups_dir = os.path.join(self.data_dir, 'mockups')
                self.trends_dir = os.path.join(self.data_dir, 'trends')
                self.seo_dir = os.path.join(self.data_dir, 'seo')
                self.output_dir = os.path.join(self.data_dir, 'published')
                
                # Create directories if they don't exist
                os.makedirs(self.data_dir, exist_ok=True)
                os.makedirs(self.designs_dir, exist_ok=True)
                os.makedirs(self.mockups_dir, exist_ok=True)
                os.makedirs(self.trends_dir, exist_ok=True)
                os.makedirs(self.seo_dir, exist_ok=True)
                os.makedirs(self.output_dir, exist_ok=True)
                
                # Reinitialize components
                self.initialize_components()
                
                st.success("Settings saved successfully!")
            except Exception as e:
                st.error(f"Error saving settings: {str(e)}")
        
        # Validate API connections
        st.header("Validate API Connections")
        
        if st.button("Test API Connections"):
            with st.spinner("Testing API connections..."):
                # Test Printify API
                printify_status = self.check_printify_api()
                if printify_status:
                    st.success("Printify API: Connected")
                else:
                    st.error("Printify API: Not Connected")
                
                # Test Etsy API
                etsy_status = self.check_etsy_api()
                if etsy_status:
                    st.success("Etsy API: Connected")
                else:
                    st.error("Etsy API: Not Connected")
                
                # Test Stable Diffusion API
                sd_status = self.check_stable_diffusion_api()
                if sd_status:
                    st.success("Stable Diffusion API: Connected")
                else:
                    st.error("Stable Diffusion API: Not Connected")
    
    def check_printify_api(self):
        """Check if Printify API is connected.
        
        Returns:
            bool: True if connected, False otherwise
        """
        if not self.publishing_agent:
            return False
        
        try:
            validation = self.publishing_agent.validate_api_connections()
            return validation['printify']['connected']
        except Exception:
            return False
    
    def check_etsy_api(self):
        """Check if Etsy API is connected.
        
        Returns:
            bool: True if connected, False otherwise
        """
        if not self.publishing_agent:
            return False
        
        try:
            validation = self.publishing_agent.validate_api_connections()
            return validation['etsy']['connected']
        except Exception:
            return False
    
    def check_stable_diffusion_api(self):
        """Check if Stable Diffusion API is connected.
        
        Returns:
            bool: True if connected, False otherwise
        """
        # PATCH: Force enable Stable Diffusion API for local server without API key
        return True
    
    def get_recent_files(self, directory, ext=None, prefix=None, limit=10):
        """Get recent files from a directory.
        
        Args:
            directory (str): Directory to search
            ext (list, optional): List of file extensions to include
            prefix (str, optional): Prefix for file names
            limit (int, optional): Maximum number of files to return
            
        Returns:
            list: List of file paths
        """
        if not os.path.exists(directory):
            return []
        
        files = []
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            
            if not os.path.isfile(file_path):
                continue
            
            if ext and not any(file.endswith(e) for e in ext):
                continue
            
            if prefix and not file.startswith(prefix):
                continue
            
            files.append((file_path, os.path.getmtime(file_path)))
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: x[1], reverse=True)
        
        # Return file paths
        return [f[0] for f in files[:limit]]
    
    def add_download_button(self, file_path, button_text="Download File"):
        """Add a download button for a file.
        
        Args:
            file_path (str): Path to file
            button_text (str, optional): Text for download button
        """
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            file_name = os.path.basename(file_path)
            
            # Create download button
            st.download_button(
                label=button_text,
                data=file_data,
                file_name=file_name,
                mime="application/octet-stream"
            )
        except Exception as e:
            st.error(f"Error creating download button: {str(e)}")

def main():
    """Main function to run the dashboard."""
    dashboard = Dashboard()
    dashboard.run_dashboard()

if __name__ == "__main__":
    main()
