"""
Enhanced error handling for external data sources in the Trend Forecasting Agent.
"""

import os
import sys
import logging
import json
import time
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Union

# Set up logging
from pod_automation.config.logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

class TrendForecaster:
    """Trend Forecasting Agent for analyzing cat-themed designs and keywords."""
    
    def __init__(self, config=None):
        """Initialize the trend forecaster.
        
        Args:
            config (dict, optional): Configuration dictionary
        """
        self.config = config or {}
        self.data_dir = self.config.get('data_dir', 'data/trends')
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # External data sources
        self.data_sources = {
            'etsy_trends': {
                'url': 'https://openapi.etsy.com/v3/application/trending',
                'method': 'GET',
                'headers': {},
                'params': {'limit': 100},
                'timeout': 30,
                'retry_count': 3,
                'retry_delay': 5,
                'required': False
            },
            'google_trends': {
                'url': 'https://trends.google.com/trends/api/dailytrends',
                'method': 'GET',
                'headers': {},
                'params': {'geo': 'US', 'cat': '5'},
                'timeout': 30,
                'retry_count': 3,
                'retry_delay': 5,
                'required': False
            },
            'pinterest_trends': {
                'url': 'https://api.pinterest.com/v5/trends',
                'method': 'GET',
                'headers': {},
                'params': {'category': 'animals'},
                'timeout': 30,
                'retry_count': 3,
                'retry_delay': 5,
                'required': False
            }
        }
        
        # Initialize cache
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour
    
    def run_trend_analysis(self, keywords=None):
        """Run trend analysis for specified keywords.
        
        Args:
            keywords (list, optional): List of keywords to analyze
            
        Returns:
            str: Path to trend report
        """
        logger.info(f"Running trend analysis for keywords: {keywords}")
        
        try:
            # Get trending keywords if none provided
            if not keywords:
                keywords = self.get_trending_keywords()
            
            # Analyze trends for each keyword
            trend_data = {}
            for keyword in keywords:
                try:
                    keyword_data = self.analyze_keyword(keyword)
                    trend_data[keyword] = keyword_data
                except Exception as e:
                    logger.error(f"Error analyzing keyword '{keyword}': {str(e)}")
                    trend_data[keyword] = {
                        'error': str(e),
                        'status': 'failed',
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
            
            # Generate trend report
            report_path = self.generate_trend_report(trend_data)
            
            return report_path
        
        except Exception as e:
            logger.error(f"Error running trend analysis: {str(e)}")
            # Create error report
            error_report_path = os.path.join(self.data_dir, f"trend_analysis_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
            with open(error_report_path, 'w') as f:
                f.write(f"# Trend Analysis Error Report\n\n")
                f.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**Error:** {str(e)}\n\n")
                f.write(f"**Keywords:** {keywords}\n\n")
                f.write(f"**Stack Trace:**\n\n```\n{sys.exc_info()}\n```\n")
            
            return error_report_path
    
    def get_trending_keywords(self, category="cat"):
        """Get trending keywords for a category.
        
        Args:
            category (str, optional): Category to get trending keywords for
            
        Returns:
            list: List of trending keywords
        """
        logger.info(f"Getting trending keywords for category: {category}")
        
        # Check cache
        cache_key = f"trending_keywords_{category}"
        if cache_key in self.cache:
            cache_time, cache_data = self.cache[cache_key]
            if time.time() - cache_time < self.cache_ttl:
                logger.info(f"Using cached trending keywords for category: {category}")
                return cache_data
        
        # Initialize trending keywords with default fallback values
        trending_keywords = [
            f"{category} lover",
            f"funny {category}",
            f"{category} mom",
            f"{category} dad",
            f"{category} gift"
        ]
        
        # Collect data from external sources
        external_data = {}
        source_errors = {}
        
        for source_name, source_config in self.data_sources.items():
            try:
                source_data = self._fetch_from_external_source(source_name, source_config, category)
                if source_data:
                    external_data[source_name] = source_data
            except Exception as e:
                error_msg = f"Error fetching data from {source_name}: {str(e)}"
                logger.error(error_msg)
                source_errors[source_name] = error_msg
                
                # If this is a required source and it failed, raise exception
                if source_config.get('required', False):
                    raise RuntimeError(f"Required data source {source_name} failed: {str(e)}")
        
        # Extract keywords from external data
        if external_data:
            extracted_keywords = self._extract_keywords_from_external_data(external_data, category)
            if extracted_keywords:
                trending_keywords.extend(extracted_keywords)
                # Remove duplicates and limit to 20 keywords
                trending_keywords = list(dict.fromkeys(trending_keywords))[:20]
        
        # Cache results
        self.cache[cache_key] = (time.time(), trending_keywords)
        
        # Log any source errors
        if source_errors:
            logger.warning(f"Errors occurred with some data sources: {source_errors}")
            # Create a source errors file for reference
            errors_file = os.path.join(self.data_dir, f"source_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(errors_file, 'w') as f:
                json.dump(source_errors, f, indent=2)
        
        return trending_keywords
    
    def _fetch_from_external_source(self, source_name, source_config, category):
        """Fetch data from an external source with enhanced error handling and retries.
        
        Args:
            source_name (str): Name of the source
            source_config (dict): Source configuration
            category (str): Category to fetch data for
            
        Returns:
            dict: Source data
        """
        logger.info(f"Fetching data from {source_name}")
        
        url = source_config['url']
        method = source_config['method']
        headers = source_config.get('headers', {})
        params = source_config.get('params', {})
        timeout = source_config.get('timeout', 30)
        retry_count = source_config.get('retry_count', 3)
        retry_delay = source_config.get('retry_delay', 5)
        
        # Add category to params if applicable
        if 'category' in params:
            params['category'] = category
        
        # Try to fetch data with retries
        for attempt in range(retry_count):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    timeout=timeout
                )
                
                # Check response status
                if response.status_code == 200:
                    try:
                        return response.json()
                    except ValueError:
                        # Not JSON, return text
                        return {'text': response.text}
                elif response.status_code == 404:
                    logger.warning(f"{source_name} returned 404 Not Found")
                    return None
                elif response.status_code == 429:
                    logger.warning(f"{source_name} rate limit exceeded, retrying after delay")
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                    continue
                else:
                    logger.warning(f"{source_name} returned status code {response.status_code}")
                    # Try to parse error response
                    try:
                        error_data = response.json()
                        logger.warning(f"{source_name} error details: {error_data}")
                    except ValueError:
                        logger.warning(f"{source_name} error text: {response.text[:200]}")
                    
                    if attempt < retry_count - 1:
                        time.sleep(retry_delay)
                        continue
                    else:
                        return {'error': f"Status code: {response.status_code}"}
            
            except requests.exceptions.Timeout:
                logger.warning(f"{source_name} request timed out (attempt {attempt + 1}/{retry_count})")
                if attempt < retry_count - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    return {'error': "Request timed out"}
            
            except requests.exceptions.ConnectionError:
                logger.warning(f"{source_name} connection error (attempt {attempt + 1}/{retry_count})")
                if attempt < retry_count - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    return {'error': "Connection error"}
            
            except Exception as e:
                logger.error(f"Unexpected error fetching from {source_name}: {str(e)}")
                if attempt < retry_count - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    return {'error': str(e)}
        
        # If we get here, all retries failed
        logger.error(f"All {retry_count} attempts to fetch from {source_name} failed")
        return {'error': f"All {retry_count} attempts failed"}
    
    def _extract_keywords_from_external_data(self, external_data, category):
        """Extract keywords from external data.
        
        Args:
            external_data (dict): External data by source
            category (str): Category to extract keywords for
            
        Returns:
            list: Extracted keywords
        """
        keywords = []
        
        # Process each source
        for source_name, source_data in external_data.items():
            try:
                if source_name == 'etsy_trends':
                    # Extract from Etsy trends
                    if isinstance(source_data, dict) and 'results' in source_data:
                        for item in source_data['results']:
                            if category.lower() in item.get('title', '').lower():
                                keywords.append(item.get('title'))
                
                elif source_name == 'google_trends':
                    # Extract from Google trends
                    if isinstance(source_data, dict) and 'default' in source_data:
                        for item in source_data['default'].get('trendingSearchesDays', []):
                            for trend in item.get('trendingSearches', []):
                                title = trend.get('title', {}).get('query', '')
                                if category.lower() in title.lower():
                                    keywords.append(title)
                
                elif source_name == 'pinterest_trends':
                    # Extract from Pinterest trends
                    if isinstance(source_data, dict) and 'trends' in source_data:
                        for trend in source_data['trends']:
                            if category.lower() in trend.get('name', '').lower():
                                keywords.append(trend.get('name'))
            
            except Exception as e:
                logger.error(f"Error extracting keywords from {source_name}: {str(e)}")
                # Continue with other sources
        
        # Filter and clean keywords
        filtered_keywords = []
        for keyword in keywords:
            # Basic cleaning
            keyword = keyword.strip()
            if keyword and len(keyword) > 3:
                # Add category if not present
                if category.lower() not in keyword.lower():
                    keyword = f"{category} {keyword}"
                filtered_keywords.append(keyword)
        
        return filtered_keywords
    
    def analyze_keyword(self, keyword):
        """Analyze a keyword for trends.
        
        Args:
            keyword (str): Keyword to analyze
            
        Returns:
            dict: Keyword analysis data
        """
        logger.info(f"Analyzing keyword: {keyword}")
        
        try:
            # Check cache
            cache_key = f"keyword_analysis_{keyword}"
            if cache_key in self.cache:
                cache_time, cache_data = self.cache[cache_key]
                if time.time() - cache_time < self.cache_ttl:
                    logger.info(f"Using cached analysis for keyword: {keyword}")
                    return cache_data
            
            # Simulate keyword analysis
            # In a real implementation, this would use actual data sources
            analysis = {
                'keyword': keyword,
                'popularity': self._simulate_popularity_score(keyword),
                'competition': self._simulate_competition_score(keyword),
                'trend_direction': self._simulate_trend_direction(keyword),
                'related_keywords': self._generate_related_keywords(keyword),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Cache results
            self.cache[cache_key] = (time.time(), analysis)
            
            return analysis
        
        except Exception as e:
            logger.error(f"Error analyzing keyword '{keyword}': {str(e)}")
            return {
                'keyword': keyword,
                'error': str(e),
                'status': 'failed',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def _simulate_popularity_score(self, keyword):
        """Simulate a popularity score for a keyword.
        
        Args:
            keyword (str): Keyword to score
            
        Returns:
            float: Popularity score (0-100)
        """
        # This is a simulation; in a real implementation, this would use actual data
        import random
        base_score = 50
        
        # Adjust score based on keyword characteristics
        if 'cat' in keyword.lower():
            base_score += 20
        if 'funny' in keyword.lower() or 'cute' in keyword.lower():
            base_score += 15
        if 'gift' in keyword.lower():
            base_score += 10
        if 'lover' in keyword.lower() or 'mom' in keyword.lower() or 'dad' in keyword.lower():
            base_score += 5
        
        # Add some randomness
        base_score += random.uniform(-10, 10)
        
        # Ensure score is within bounds
        return max(0, min(100, base_score))
    
    def _simulate_competition_score(self, keyword):
        """Simulate a competition score for a keyword.
        
        Args:
            keyword (str): Keyword to score
            
        Returns:
            float: Competition score (0-100)
        """
        # This is a simulation; in a real implementation, this would use actual data
        import random
        base_score = 40
        
        # Adjust score based on keyword characteristics
        if 'cat' in keyword.lower():
            base_score += 30
        if 'funny' in keyword.lower() or 'cute' in keyword.lower():
            base_score += 20
        if 'gift' in keyword.lower():
            base_score += 15
        if 'lover' in keyword.lower() or 'mom' in keyword.lower() or 'dad' in keyword.lower():
            base_score += 10
        
        # Add some randomness
        base_score += random.uniform(-10, 10)
        
        # Ensure score is within bounds
        return max(0, min(100, base_score))
    
    def _simulate_trend_direction(self, keyword):
        """Simulate a trend direction for a keyword.
        
        Args:
            keyword (str): Keyword to analyze
            
        Returns:
            str: Trend direction (up, down, stable)
        """
        # This is a simulation; in a real implementation, this would use actual data
        import random
        directions = ['up', 'down', 'stable']
        weights = [0.5, 0.2, 0.3]  # More likely to be trending up
        
        # Adjust weights based on keyword characteristics
        if 'cat' in keyword.lower() and ('funny' in keyword.lower() or 'cute' in keyword.lower()):
            weights = [0.7, 0.1, 0.2]  # Even more likely to be trending up
        
        return random.choices(directions, weights=weights)[0]
    
    def _generate_related_keywords(self, keyword):
        """Generate related keywords for a keyword.
        
        Args:
            keyword (str): Base keyword
            
        Returns:
            list: Related keywords
        """
        # This is a simulation; in a real implementation, this would use actual data
        related = []
        
        # Extract main terms
        terms = keyword.lower().split()
        
        # Generate variations
        if 'cat' in terms:
            related.extend(['kitten', 'feline', 'kitty'])
        if 'funny' in terms:
            related.extend(['humorous', 'hilarious', 'amusing'])
        if 'cute' in terms:
            related.extend(['adorable', 'sweet', 'lovely'])
        if 'gift' in terms:
            related.extend(['present', 'gift idea', 'gift for'])
        if 'lover' in terms:
            related.extend(['enthusiast', 'fan', 'owner'])
        
        # Combine terms with base keyword
        base_term = 'cat'
        combined_terms = []
        for term in related:
            if term not in keyword.lower():
                combined_terms.append(f"{base_term} {term}")
        related.extend(combined_terms)
        
        # Remove duplicates and limit to 10
        related = list(dict.fromkeys(related))[:10]
        
        return related
    
    def generate_trend_report(self, trend_data):
        """Generate a trend report from trend data.
        
        Args:
            trend_data (dict): Trend data by keyword
            
        Returns:
            str: Path to trend report
        """
        logger.info("Generating trend report")
        
        try:
            # Create report filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_path = os.path.join(self.data_dir, f"trend_report_{timestamp}.md")
            
            # Generate report content
            with open(report_path, 'w') as f:
                f.write("# Cat-Themed Design Trend Report\n\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Summary section
                f.write("## Summary\n\n")
                f.write("This report analyzes trends for cat-themed designs and keywords to inform design generation.\n\n")
                
                # Add data sources information
                f.write("### Data Sources\n\n")
                for source_name in self.data_sources.keys():
                    f.write(f"- {source_name}\n")
                f.write("\n")
                
                # Keyword analysis section
                f.write("## Keyword Analysis\n\n")
                
                # Sort keywords by popularity (if available)
                sorted_keywords = sorted(
                    trend_data.items(),
                    key=lambda x: x[1].get('popularity', 0) if isinstance(x[1], dict) and 'error' not in x[1] else 0,
                    reverse=True
                )
                
                for keyword, data in sorted_keywords:
                    f.write(f"### {keyword}\n\n")
                    
                    if isinstance(data, dict) and 'error' not in data:
                        # Success case
                        f.write(f"- **Popularity:** {data.get('popularity', 'N/A')}/100\n")
                        f.write(f"- **Competition:** {data.get('competition', 'N/A')}/100\n")
                        f.write(f"- **Trend Direction:** {data.get('trend_direction', 'N/A')}\n")
                        
                        # Related keywords
                        related = data.get('related_keywords', [])
                        if related:
                            f.write("\n**Related Keywords:**\n\n")
                            for rel in related:
                                f.write(f"- {rel}\n")
                    else:
                        # Error case
                        f.write(f"**Error:** {data.get('error', 'Unknown error')}\n")
                    
                    f.write("\n")
                
                # Recommendations section
                f.write("## Design Recommendations\n\n")
                
                # Generate recommendations based on trend data
                recommendations = self._generate_design_recommendations(trend_data)
                for rec in recommendations:
                    f.write(f"- {rec}\n")
            
            logger.info(f"Trend report generated: {report_path}")
            return report_path
        
        except Exception as e:
            logger.error(f"Error generating trend report: {str(e)}")
            # Create error report
            error_report_path = os.path.join(self.data_dir, f"trend_report_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
            with open(error_report_path, 'w') as f:
                f.write(f"# Trend Report Generation Error\n\n")
                f.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**Error:** {str(e)}\n\n")
                f.write(f"**Stack Trace:**\n\n```\n{sys.exc_info()}\n```\n")
            
            return error_report_path
    
    def _generate_design_recommendations(self, trend_data):
        """Generate design recommendations based on trend data.
        
        Args:
            trend_data (dict): Trend data by keyword
            
        Returns:
            list: Design recommendations
        """
        recommendations = []
        
        # Find trending keywords
        trending_up = []
        for keyword, data in trend_data.items():
            if isinstance(data, dict) and 'error' not in data:
                if data.get('trend_direction') == 'up' and data.get('popularity', 0) > 60:
                    trending_up.append((keyword, data))
        
        # Generate recommendations based on trending keywords
        if trending_up:
            recommendations.append("Focus on these trending themes:")
            for keyword, data in trending_up:
                recommendations.append(f"  - {keyword} (Popularity: {data.get('popularity')}/100)")
        
        # Add general recommendations
        recommendations.extend([
            "Use bright, vibrant colors for cat designs to attract attention",
            "Include humorous elements in designs for higher engagement",
            "Create designs that appeal to cat owners' emotional connection with their pets",
            "Consider seasonal themes for cat designs (holidays, seasons, events)",
            "Develop designs that work well on multiple product types (t-shirts, posters, pillows)"
        ])
        
        return recommendations

# For testing
if __name__ == "__main__":
    forecaster = TrendForecaster()
    report_path = forecaster.run_trend_analysis(['cat lover', 'funny cat'])
    print(f"Trend report generated: {report_path}")
