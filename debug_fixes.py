"""
Debug and fix issues in the POD Automation System.
Addresses issues identified during testing.
"""

import os
import sys
import logging
import json
import time
from datetime import datetime
import traceback

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug_fixes.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import system
from pod_automation.pod_automation_system import PODAutomationSystem
from pod_automation.config import Config

class SystemDebugger:
    """Debugger for POD Automation System."""
    
    def __init__(self, system=None, config_path=None):
        """Initialize debugger.
        
        Args:
            system (PODAutomationSystem, optional): System to debug
            config_path (str, optional): Path to configuration file
        """
        # Initialize system if not provided
        if system is None:
            self.system = PODAutomationSystem(config_path=config_path)
        else:
            self.system = system
        
        # Set up debug directory
        self.debug_dir = os.path.join(self.system.data_dir, 'debug')
        os.makedirs(self.debug_dir, exist_ok=True)
    
    def run_diagnostics(self):
        """Run diagnostics on the system.
        
        Returns:
            dict: Diagnostic results
        """
        logger.info("Running system diagnostics")
        
        # Initialize results
        results = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'system_info': self._get_system_info(),
            'component_status': {},
            'api_connections': {},
            'directory_status': {},
            'issues': [],
            'fixes_applied': []
        }
        
        # Check component initialization
        results['component_status'] = self._check_components()
        
        # Check API connections
        results['api_connections'] = self._check_api_connections()
        
        # Check directories
        results['directory_status'] = self._check_directories()
        
        # Identify issues
        results['issues'] = self._identify_issues(results)
        
        # Save diagnostic results
        self._save_diagnostics(results)
        
        return results
    
    def _get_system_info(self):
        """Get system information.
        
        Returns:
            dict: System information
        """
        return {
            'python_version': sys.version,
            'platform': sys.platform,
            'data_dir': self.system.data_dir,
            'config_file': self.system.config.config_file if hasattr(self.system.config, 'config_file') else None
        }
    
    def _check_components(self):
        """Check if all components are initialized.
        
        Returns:
            dict: Component status
        """
        components = {
            'trend_forecaster': self.system.trend_forecaster is not None,
            'prompt_optimizer': self.system.prompt_optimizer is not None,
            'stable_diffusion': self.system.stable_diffusion is not None,
            'design_pipeline': self.system.design_pipeline is not None,
            'mockup_generator': self.system.mockup_generator is not None,
            'publishing_agent': self.system.publishing_agent is not None,
            'seo_optimizer': self.system.seo_optimizer is not None
        }
        
        return components
    
    def _check_api_connections(self):
        """Check API connections.
        
        Returns:
            dict: API connection status
        """
        try:
            return self.system.validate_api_connections()
        except Exception as e:
            logger.error(f"Error checking API connections: {str(e)}")
            return {
                'printify': False,
                'etsy': False,
                'stable_diffusion': False,
                'error': str(e)
            }
    
    def _check_directories(self):
        """Check if all directories exist and are writable.
        
        Returns:
            dict: Directory status
        """
        directories = {
            'data_dir': self.system.data_dir,
            'designs_dir': self.system.designs_dir,
            'mockups_dir': self.system.mockups_dir,
            'trends_dir': self.system.trends_dir,
            'seo_dir': self.system.seo_dir,
            'output_dir': self.system.output_dir,
            'debug_dir': self.debug_dir
        }
        
        status = {}
        for name, path in directories.items():
            exists = os.path.exists(path)
            writable = os.access(path, os.W_OK) if exists else False
            
            status[name] = {
                'path': path,
                'exists': exists,
                'writable': writable
            }
        
        return status
    
    def _identify_issues(self, diagnostic_results):
        """Identify issues based on diagnostic results.
        
        Args:
            diagnostic_results (dict): Diagnostic results
            
        Returns:
            list: Identified issues
        """
        issues = []
        
        # Check component initialization
        for component, initialized in diagnostic_results['component_status'].items():
            if not initialized:
                issues.append({
                    'type': 'component_initialization',
                    'component': component,
                    'message': f"{component} is not initialized",
                    'severity': 'high',
                    'fixable': True
                })
        
        # Check API connections
        for api, connected in diagnostic_results['api_connections'].items():
            if api != 'error' and not connected:
                issues.append({
                    'type': 'api_connection',
                    'api': api,
                    'message': f"{api} API is not connected",
                    'severity': 'medium',
                    'fixable': False  # Requires user to provide valid API keys
                })
        
        # Check directories
        for name, status in diagnostic_results['directory_status'].items():
            if not status['exists']:
                issues.append({
                    'type': 'directory_missing',
                    'directory': name,
                    'path': status['path'],
                    'message': f"{name} directory does not exist",
                    'severity': 'high',
                    'fixable': True
                })
            elif not status['writable']:
                issues.append({
                    'type': 'directory_not_writable',
                    'directory': name,
                    'path': status['path'],
                    'message': f"{name} directory is not writable",
                    'severity': 'high',
                    'fixable': True
                })
        
        return issues
    
    def _save_diagnostics(self, results):
        """Save diagnostic results to file.
        
        Args:
            results (dict): Diagnostic results
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = os.path.join(self.debug_dir, f"diagnostics_{timestamp}.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Diagnostic results saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving diagnostic results: {str(e)}")
    
    def fix_issues(self, issues=None):
        """Fix identified issues.
        
        Args:
            issues (list, optional): Issues to fix. If None, run diagnostics first.
            
        Returns:
            dict: Fix results
        """
        logger.info("Fixing identified issues")
        
        # Run diagnostics if issues not provided
        if issues is None:
            diagnostic_results = self.run_diagnostics()
            issues = diagnostic_results['issues']
        
        # Initialize results
        results = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'issues_fixed': [],
            'issues_not_fixed': [],
            'errors': []
        }
        
        # Fix each issue
        for issue in issues:
            if issue['fixable']:
                try:
                    fixed = self._fix_issue(issue)
                    
                    if fixed:
                        results['issues_fixed'].append(issue)
                    else:
                        results['issues_not_fixed'].append(issue)
                except Exception as e:
                    logger.error(f"Error fixing issue: {str(e)}")
                    results['errors'].append({
                        'issue': issue,
                        'error': str(e),
                        'traceback': traceback.format_exc()
                    })
            else:
                results['issues_not_fixed'].append(issue)
        
        # Save fix results
        self._save_fix_results(results)
        
        return results
    
    def _fix_issue(self, issue):
        """Fix a specific issue.
        
        Args:
            issue (dict): Issue to fix
            
        Returns:
            bool: True if issue was fixed, False otherwise
        """
        issue_type = issue['type']
        
        if issue_type == 'component_initialization':
            return self._fix_component_initialization(issue['component'])
        
        elif issue_type == 'directory_missing':
            return self._fix_directory_missing(issue['path'])
        
        elif issue_type == 'directory_not_writable':
            return self._fix_directory_not_writable(issue['path'])
        
        else:
            logger.warning(f"Unknown issue type: {issue_type}")
            return False
    
    def _fix_component_initialization(self, component):
        """Fix component initialization issue.
        
        Args:
            component (str): Component name
            
        Returns:
            bool: True if issue was fixed, False otherwise
        """
        logger.info(f"Fixing {component} initialization")
        
        try:
            # Reinitialize all components
            self.system.initialize_components()
            
            # Check if component is now initialized
            if component == 'trend_forecaster':
                return self.system.trend_forecaster is not None
            elif component == 'prompt_optimizer':
                return self.system.prompt_optimizer is not None
            elif component == 'stable_diffusion':
                return self.system.stable_diffusion is not None
            elif component == 'design_pipeline':
                return self.system.design_pipeline is not None
            elif component == 'mockup_generator':
                return self.system.mockup_generator is not None
            elif component == 'publishing_agent':
                return self.system.publishing_agent is not None
            elif component == 'seo_optimizer':
                return self.system.seo_optimizer is not None
            else:
                logger.warning(f"Unknown component: {component}")
                return False
        
        except Exception as e:
            logger.error(f"Error fixing {component} initialization: {str(e)}")
            return False
    
    def _fix_directory_missing(self, directory):
        """Fix missing directory issue.
        
        Args:
            directory (str): Directory path
            
        Returns:
            bool: True if issue was fixed, False otherwise
        """
        logger.info(f"Creating missing directory: {directory}")
        
        try:
            os.makedirs(directory, exist_ok=True)
            return os.path.exists(directory)
        
        except Exception as e:
            logger.error(f"Error creating directory {directory}: {str(e)}")
            return False
    
    def _fix_directory_not_writable(self, directory):
        """Fix non-writable directory issue.
        
        Args:
            directory (str): Directory path
            
        Returns:
            bool: True if issue was fixed, False otherwise
        """
        logger.info(f"Fixing permissions for directory: {directory}")
        
        try:
            # Check if directory exists
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # Try to make directory writable
            os.chmod(directory, 0o755)  # rwxr-xr-x
            
            return os.access(directory, os.W_OK)
        
        except Exception as e:
            logger.error(f"Error fixing permissions for directory {directory}: {str(e)}")
            return False
    
    def _save_fix_results(self, results):
        """Save fix results to file.
        
        Args:
            results (dict): Fix results
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = os.path.join(self.debug_dir, f"fixes_{timestamp}.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Fix results saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving fix results: {str(e)}")
    
    def run_system_check(self):
        """Run a complete system check and fix issues.
        
        Returns:
            dict: Check results
        """
        logger.info("Running complete system check")
        
        # Run diagnostics
        diagnostic_results = self.run_diagnostics()
        
        # Fix issues
        fix_results = self.fix_issues(diagnostic_results['issues'])
        
        # Run diagnostics again to verify fixes
        post_fix_diagnostics = self.run_diagnostics()
        
        # Prepare results
        results = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'initial_diagnostics': diagnostic_results,
            'fix_results': fix_results,
            'post_fix_diagnostics': post_fix_diagnostics,
            'remaining_issues': post_fix_diagnostics['issues']
        }
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = os.path.join(self.debug_dir, f"system_check_{timestamp}.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"System check results saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving system check results: {str(e)}")
        
        return results
    
    def test_component(self, component_name):
        """Test a specific component.
        
        Args:
            component_name (str): Component name
            
        Returns:
            dict: Test results
        """
        logger.info(f"Testing component: {component_name}")
        
        # Initialize results
        results = {
            'component': component_name,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'success': False,
            'error': None,
            'output': None
        }
        
        try:
            # Test trend forecaster
            if component_name == 'trend_forecaster':
                if self.system.trend_forecaster is None:
                    raise ValueError("Trend forecaster is not initialized")
                
                output = self.system.trend_forecaster.run_trend_analysis(['cat lover'])
                results['success'] = output is not None
                results['output'] = output
            
            # Test prompt optimizer
            elif component_name == 'prompt_optimizer':
                if self.system.prompt_optimizer is None:
                    raise ValueError("Prompt optimizer is not initialized")
                
                output = self.system.prompt_optimizer.optimize_prompt("cat lover t-shirt")
                results['success'] = output is not None
                results['output'] = output
            
            # Test stable diffusion
            elif component_name == 'stable_diffusion':
                if self.system.stable_diffusion is None:
                    raise ValueError("Stable diffusion is not initialized")
                
                success, output = self.system.stable_diffusion.generate_image(
                    prompt="cat lover t-shirt",
                    negative_prompt="deformed, blurry, bad anatomy",
                    width=512,
                    height=512,
                    num_inference_steps=30,
                    guidance_scale=7.5
                )
                results['success'] = success
                results['output'] = output
            
            # Test design pipeline
            elif component_name == 'design_pipeline':
                if self.system.design_pipeline is None:
                    raise ValueError("Design pipeline is not initialized")
                
                output = self.system.design_pipeline.run_pipeline(
                    analyze_trends=False,
                    base_keyword="cat lover",
                    num_designs=1
                )
                results['success'] = output is not None and len(output) > 0
                results['output'] = output
            
            # Test mockup generator
            elif component_name == 'mockup_generator':
                if self.system.mockup_generator is None:
                    raise ValueError("Mockup generator is not initialized")
                
                # Create a test design if none exists
                designs = [f for f in os.listdir(self.system.designs_dir) 
                          if f.endswith('.png') or f.endswith('.jpg')]
                
                if not designs:
                    # Create a simple test image
                    from PIL import Image, ImageDraw
                    img = Image.new('RGB', (512, 512), color='white')
                    draw = ImageDraw.Draw(img)
                    draw.rectangle([(100, 100), (400, 400)], fill='black')
                    test_design_path = os.path.join(self.system.designs_dir, 'test_design.png')
                    img.save(test_design_path)
                    design_path = test_design_path
                else:
                    design_path = os.path.join(self.system.designs_dir, designs[0])
                
                output = self.system.mockup_generator.create_mockups_for_design(
                    design_path,
                    product_types=['t-shirt']
                )
                results['success'] = output is not None and len(output) > 0
                results['output'] = output
            
            # Test publishing agent
            elif component_name == 'publishing_agent':
                if self.system.publishing_agent is None:
                    raise ValueError("Publishing agent is not initialized")
                
                output = self.system.publishing_agent.validate_api_connections()
                results['success'] = output is not None
                results['output'] = output
            
            # Test SEO optimizer
            elif component_name == 'seo_optimizer':
                if self.system.seo_optimizer is None:
                    raise ValueError("SEO optimizer is not initialized")
                
                output = self.system.seo_optimizer.optimize_listing("cat lover", "t-shirt")
                results['success'] = output is not None
                results['output'] = output
            
            else:
                raise ValueError(f"Unknown component: {component_name}")
        
        except Exception as e:
            logger.error(f"Error testing {component_name}: {str(e)}")
            results['error'] = str(e)
            results['traceback'] = traceback.format_exc()
        
        # Save test results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = os.path.join(self.debug_dir, f"test_{component_name}_{timestamp}.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Test results saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving test results: {str(e)}")
        
        return results
    
    def test_all_components(self):
        """Test all components.
        
        Returns:
            dict: Test results for all components
        """
        logger.info("Testing all components")
        
        components = [
            'trend_forecaster',
            'prompt_optimizer',
            'seo_optimizer',
            'publishing_agent',
            'mockup_generator'
        ]
        
        # Only test these components if API keys are available
        if self.system.config.get('stable_diffusion.api_key') or os.environ.get('OPENROUTER_API_KEY'):
            components.extend(['stable_diffusion', 'design_pipeline'])
        
        results = {}
        for component in components:
            results[component] = self.test_component(component)
        
        # Save overall results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = os.path.join(self.debug_dir, f"test_all_components_{timestamp}.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"All component test results saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving all component test results: {str(e)}")
        
        return results

def main():
    """Main function for debugging and fixing issues."""
    import argparse
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Debug and fix issues in POD Automation System")
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--diagnostics', action='store_true', help='Run diagnostics')
    parser.add_argument('--fix', action='store_true', help='Fix identified issues')
    parser.add_argument('--check', action='store_true', help='Run complete system check')
    parser.add_argument('--test', type=str, help='Test a specific component')
    parser.add_argument('--test-all', action='store_true', help='Test all components')
    
    args = parser.parse_args()
    
    # Create system and debugger
    system = PODAutomationSystem(config_path=args.config)
    debugger = SystemDebugger(system)
    
    # Process commands
    if args.diagnostics:
        results = debugger.run_diagnostics()
        print("\n=== Diagnostic Results ===")
        print(f"Issues found: {len(results['issues'])}")
        for issue in results['issues']:
            print(f"- {issue['message']} (Severity: {issue['severity']}, Fixable: {issue['fixable']})")
    
    elif args.fix:
        results = debugger.fix_issues()
        print("\n=== Fix Results ===")
        print(f"Issues fixed: {len(results['issues_fixed'])}")
        print(f"Issues not fixed: {len(results['issues_not_fixed'])}")
        print(f"Errors: {len(results['errors'])}")
    
    elif args.check:
        results = debugger.run_system_check()
        print("\n=== System Check Results ===")
        print(f"Initial issues: {len(results['initial_diagnostics']['issues'])}")
        print(f"Issues fixed: {len(results['fix_results']['issues_fixed'])}")
        print(f"Remaining issues: {len(results['remaining_issues'])}")
    
    elif args.test:
        results = debugger.test_component(args.test)
        print(f"\n=== Test Results for {args.test} ===")
        print(f"Success: {results['success']}")
        if results['error']:
            print(f"Error: {results['error']}")
    
    elif args.test_all:
        results = debugger.test_all_components()
        print("\n=== All Component Test Results ===")
        for component, result in results.items():
            print(f"{component}: {'Success' if result['success'] else 'Failed'}")
    
    else:
        # Default to running a complete system check
        results = debugger.run_system_check()
        print("\n=== System Check Results ===")
        print(f"Initial issues: {len(results['initial_diagnostics']['issues'])}")
        print(f"Issues fixed: {len(results['fix_results']['issues_fixed'])}")
        print(f"Remaining issues: {len(results['remaining_issues'])}")

if __name__ == "__main__":
    main()
