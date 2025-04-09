"""
SEO Optimization Tools for POD Automation System.
Enhances Etsy listings with optimized tags, titles, and descriptions for improved visibility.
"""

import os
import sys
import logging
import json
import time
from datetime import datetime
from pathlib import Path
import random
import re
import requests
from collections import Counter

# Set up logging
from pod_automation.config.logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

class SEOOptimizer:
    """Optimizer for enhancing Etsy listings with SEO."""
    
    def __init__(self, config=None):
        """Initialize SEO optimizer.
        
        Args:
            config (dict, optional): Configuration dictionary
        """
        self.config = config or {}
        
        # Set up directories
        self.data_dir = self.config.get('data_dir', 'data/seo')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load keyword data
        self.keywords = self._load_keywords()
        self.long_tail_keywords = self._load_long_tail_keywords()
        
        # Load templates
        self.title_templates = self._load_templates('title_templates')
        self.description_templates = self._load_templates('description_templates')
    
    def _load_keywords(self):
        """Load keyword data from file or use default.
        
        Returns:
            dict: Dictionary of keywords with search volume and competition
        """
        # Check if keywords file exists
        keywords_file = os.path.join(self.data_dir, 'keywords.json')
        
        if os.path.exists(keywords_file):
            try:
                with open(keywords_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading keywords from file: {str(e)}")
        
        # Use default keywords if file doesn't exist or loading fails
        default_keywords = {
            'cat': {'search_volume': 9500, 'competition': 8.5},
            'cat t-shirt': {'search_volume': 5200, 'competition': 7.2},
            'cat lover': {'search_volume': 4800, 'competition': 6.8},
            'cat gift': {'search_volume': 4500, 'competition': 7.5},
            'funny cat': {'search_volume': 4200, 'competition': 6.5},
            'cute cat': {'search_volume': 3900, 'competition': 6.2},
            'cat mom': {'search_volume': 3600, 'competition': 5.8},
            'cat dad': {'search_volume': 3300, 'competition': 5.5},
            'cat lover gift': {'search_volume': 3000, 'competition': 7.0},
            'cat shirt': {'search_volume': 2800, 'competition': 6.8},
            'cat tee': {'search_volume': 2500, 'competition': 6.5},
            'cat tshirt': {'search_volume': 2300, 'competition': 6.3},
            'cat design': {'search_volume': 2100, 'competition': 5.9},
            'cat illustration': {'search_volume': 1900, 'competition': 5.5},
            'cat art': {'search_volume': 1700, 'competition': 6.2},
            'cat poster': {'search_volume': 1500, 'competition': 5.8},
            'cat wall art': {'search_volume': 1300, 'competition': 5.5},
            'cat pillow': {'search_volume': 1100, 'competition': 5.2},
            'cat home decor': {'search_volume': 900, 'competition': 5.0},
            'cat decor': {'search_volume': 800, 'competition': 4.8}
        }
        
        # Save default keywords to file
        try:
            with open(keywords_file, 'w') as f:
                json.dump(default_keywords, f, indent=2)
            logger.info(f"Saved default keywords to {keywords_file}")
        except Exception as e:
            logger.error(f"Error saving default keywords to file: {str(e)}")
        
        return default_keywords
    
    def _load_long_tail_keywords(self):
        """Load long-tail keyword data from file or use default.
        
        Returns:
            dict: Dictionary of long-tail keywords with search volume and competition
        """
        # Check if long-tail keywords file exists
        long_tail_file = os.path.join(self.data_dir, 'long_tail_keywords.json')
        
        if os.path.exists(long_tail_file):
            try:
                with open(long_tail_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading long-tail keywords from file: {str(e)}")
        
        # Use default long-tail keywords if file doesn't exist or loading fails
        default_long_tail = {
            'cat lover birthday gift': {'search_volume': 850, 'competition': 4.5},
            'funny cat t-shirt for women': {'search_volume': 780, 'competition': 4.2},
            'cute cat shirt for girls': {'search_volume': 720, 'competition': 4.0},
            'black cat halloween shirt': {'search_volume': 680, 'competition': 3.8},
            'cat mom shirt gift': {'search_volume': 650, 'competition': 3.7},
            'cat dad fathers day gift': {'search_volume': 620, 'competition': 3.5},
            'cat lover christmas gift': {'search_volume': 600, 'competition': 4.8},
            'cat themed home decor': {'search_volume': 580, 'competition': 3.2},
            'minimalist cat wall art': {'search_volume': 550, 'competition': 3.0},
            'watercolor cat illustration': {'search_volume': 520, 'competition': 2.8},
            'geometric cat design': {'search_volume': 500, 'competition': 2.7},
            'cat silhouette poster': {'search_volume': 480, 'competition': 2.5},
            'cat quote t-shirt': {'search_volume': 450, 'competition': 3.8},
            'cat pun shirt': {'search_volume': 420, 'competition': 3.5},
            'cat face illustration': {'search_volume': 400, 'competition': 3.2},
            'cat lover throw pillow': {'search_volume': 380, 'competition': 3.0},
            'cat pattern design': {'search_volume': 350, 'competition': 2.8},
            'cat mom and cat dad matching shirts': {'search_volume': 320, 'competition': 2.5},
            'cat with glasses t-shirt': {'search_volume': 300, 'competition': 2.3},
            'cat with bow tie illustration': {'search_volume': 280, 'competition': 2.0}
        }
        
        # Save default long-tail keywords to file
        try:
            with open(long_tail_file, 'w') as f:
                json.dump(default_long_tail, f, indent=2)
            logger.info(f"Saved default long-tail keywords to {long_tail_file}")
        except Exception as e:
            logger.error(f"Error saving default long-tail keywords to file: {str(e)}")
        
        return default_long_tail
    
    def _load_templates(self, template_type):
        """Load templates from file or use default.
        
        Args:
            template_type (str): Type of templates to load
            
        Returns:
            list: List of templates
        """
        # Check if templates file exists
        templates_file = os.path.join(self.data_dir, f'{template_type}.json')
        
        if os.path.exists(templates_file):
            try:
                with open(templates_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading {template_type} from file: {str(e)}")
        
        # Use default templates if file doesn't exist or loading fails
        if template_type == 'title_templates':
            default_templates = [
                "{keyword} - {product_type} for Cat Lovers",
                "Cute {keyword} {product_type} - Perfect Gift for Cat Lovers",
                "{keyword} {product_type} - Unique Cat Design",
                "Funny {keyword} {product_type} - Cat Lover Gift",
                "{keyword} {product_type} - Cat Mom Gift",
                "{keyword} {product_type} - Cat Dad Gift",
                "Adorable {keyword} {product_type} - Cat Themed Gift",
                "{keyword} {product_type} - Unique Cat Lover Present",
                "Stylish {keyword} {product_type} - Cat Design",
                "{keyword} {product_type} - Perfect for Cat People"
            ]
        elif template_type == 'description_templates':
            default_templates = [
                "Show your love for cats with this adorable {keyword} {product_type}! Perfect for cat lovers, this {product_type} features a unique design that will make you stand out.\n\n"
                "🐱 PRODUCT DETAILS 🐱\n"
                "• High-quality {product_type}\n"
                "• Unique cat design\n"
                "• Makes a perfect gift for cat lovers\n"
                "• Available in multiple sizes\n\n"
                "🎁 PERFECT GIFT 🎁\n"
                "This {keyword} {product_type} makes a wonderful gift for cat moms, cat dads, or anyone who loves cats. Surprise your cat-loving friends and family with this unique present!\n\n"
                "📦 SHIPPING 📦\n"
                "• Made to order just for you\n"
                "• Ships within 1-3 business days\n"
                "• Carefully packaged to ensure safe delivery\n\n"
                "❤️ WHY CUSTOMERS LOVE US ❤️\n"
                "• High-quality products\n"
                "• Unique designs\n"
                "• Fast shipping\n"
                "• Excellent customer service\n\n"
                "Order your {keyword} {product_type} today and show your cat love in style!",
                
                "Calling all cat lovers! This {keyword} {product_type} is purr-fect for showing your love for feline friends. Each {product_type} features a unique cat design that's sure to make you smile.\n\n"
                "🐱 ABOUT THIS {product_type_upper} 🐱\n"
                "• Premium quality materials\n"
                "• Durable and long-lasting\n"
                "• Unique cat-themed design\n"
                "• Makes a great conversation starter\n\n"
                "🎁 GIFT IDEAS 🎁\n"
                "This {keyword} {product_type} is perfect for:\n"
                "• Birthday gifts for cat lovers\n"
                "• Christmas presents\n"
                "• Mother's Day or Father's Day\n"
                "• Just because gifts for cat people\n\n"
                "📦 SHIPPING & HANDLING 📦\n"
                "• Each {product_type} is made to order with care\n"
                "• Processing time: 1-3 business days\n"
                "• Packaged securely for safe delivery\n\n"
                "❓ QUESTIONS? ❓\n"
                "Feel free to message us with any questions about this {keyword} {product_type}. We're happy to help!\n\n"
                "Add this purr-fect {keyword} {product_type} to your cart today!"
            ]
        else:
            default_templates = []
        
        # Save default templates to file
        try:
            with open(templates_file, 'w') as f:
                json.dump(default_templates, f, indent=2)
            logger.info(f"Saved default {template_type} to {templates_file}")
        except Exception as e:
            logger.error(f"Error saving default {template_type} to file: {str(e)}")
        
        return default_templates
    
    def update_keywords_from_etsy(self, query="cat", limit=20):
        """Update keywords based on Etsy search suggestions.
        
        Args:
            query (str, optional): Base query for search suggestions
            limit (int, optional): Maximum number of keywords to fetch
            
        Returns:
            bool: True if keywords were updated, False otherwise
        """
        logger.info(f"Updating keywords from Etsy search suggestions for query: {query}")
        
        try:
            # In a real implementation, we would use Etsy's API or scrape search suggestions
            # For this demonstration, we'll simulate the API call
            
            # Simulate API call delay
            time.sleep(1)
            
            # Generate simulated search suggestions
            suggestions = [
                f"{query} t-shirt",
                f"{query} lover gift",
                f"{query} art print",
                f"{query} wall art",
                f"{query} poster",
                f"{query} pillow",
                f"{query} mug",
                f"{query} tote bag",
                f"{query} hoodie",
                f"{query} sweatshirt",
                f"funny {query} shirt",
                f"cute {query} design",
                f"{query} lover",
                f"{query} mom gift",
                f"{query} dad gift",
                f"{query} themed gift",
                f"{query} illustration",
                f"{query} artwork",
                f"{query} home decor",
                f"{query} accessories"
            ]
            
            # Limit suggestions
            suggestions = suggestions[:limit]
            
            # Generate simulated search volume and competition
            new_keywords = {}
            for suggestion in suggestions:
                # Generate random search volume (100-10000) and competition (1-10)
                search_volume = random.randint(100, 10000)
                competition = round(random.uniform(1, 10), 1)
                
                new_keywords[suggestion] = {
                    'search_volume': search_volume,
                    'competition': competition
                }
            
            # Update keywords
            self.keywords.update(new_keywords)
            
            # Save updated keywords to file
            keywords_file = os.path.join(self.data_dir, 'keywords.json')
            with open(keywords_file, 'w') as f:
                json.dump(self.keywords, f, indent=2)
            
            logger.info(f"Updated keywords from Etsy search suggestions. Added {len(new_keywords)} keywords.")
            
            return True
        
        except Exception as e:
            logger.error(f"Error updating keywords from Etsy: {str(e)}")
            return False
    
    def generate_long_tail_keywords(self, base_keywords=None, count=20):
        """Generate long-tail keywords from base keywords.
        
        Args:
            base_keywords (list, optional): List of base keywords
            count (int, optional): Number of long-tail keywords to generate
            
        Returns:
            dict: Dictionary of generated long-tail keywords
        """
        logger.info("Generating long-tail keywords")
        
        # Use provided base keywords or top keywords from self.keywords
        if base_keywords is None:
            # Sort keywords by search volume and get top 5
            sorted_keywords = sorted(
                self.keywords.items(),
                key=lambda x: x[1]['search_volume'],
                reverse=True
            )
            base_keywords = [k for k, _ in sorted_keywords[:5]]
        
        # Modifiers to create long-tail keywords
        modifiers = {
            'prefix': [
                'cute', 'funny', 'adorable', 'unique', 'custom', 'personalized',
                'handmade', 'vintage', 'retro', 'modern', 'minimalist', 'colorful',
                'black', 'white', 'gray', 'pink', 'blue', 'green', 'purple', 'red'
            ],
            'suffix': [
                'for women', 'for men', 'for girls', 'for boys', 'for kids',
                'gift', 'present', 'birthday gift', 'christmas gift', 'holiday gift',
                'design', 'art', 'illustration', 'artwork', 'print',
                'lover gift', 'themed gift', 'inspired gift'
            ],
            'product': [
                't-shirt', 'shirt', 'tee', 'top', 'sweatshirt', 'hoodie',
                'poster', 'print', 'wall art', 'canvas', 'pillow', 'cushion',
                'mug', 'cup', 'tote bag', 'bag', 'accessory', 'decor', 'decoration'
            ]
        }
        
        # Generate long-tail keywords
        long_tail = {}
        for _ in range(count):
            # Select random base keyword
            base = random.choice(base_keywords)
            
            # Select random modifiers
            prefix = random.choice(modifiers['prefix']) if random.random() > 0.3 else ''
            suffix = random.choice(modifiers['suffix']) if random.random() > 0.3 else ''
            product = random.choice(modifiers['product']) if random.random() > 0.3 else ''
            
            # Combine to create long-tail keyword
            components = [c for c in [prefix, base, product, suffix] if c]
            long_tail_keyword = ' '.join(components)
            
            # Generate random search volume (50-1000) and competition (1-5)
            search_volume = random.randint(50, 1000)
            competition = round(random.uniform(1, 5), 1)
            
            long_tail[long_tail_keyword] = {
                'search_volume': search_volume,
                'competition': competition
            }
        
        # Update long-tail keywords
        self.long_tail_keywords.update(long_tail)
        
        # Save updated long-tail keywords to file
        long_tail_file = os.path.join(self.data_dir, 'long_tail_keywords.json')
        with open(long_tail_file, 'w') as f:
            json.dump(self.long_tail_keywords, f, indent=2)
        
        logger.info(f"Generated {len(long_tail)} long-tail keywords")
        
        return long_tail
    
    def optimize_tags(self, base_keyword, product_type, count=13):
        """Optimize tags for an Etsy listing.
        
        Args:
            base_keyword (str): Base keyword for the listing
            product_type (str): Type of product
            count (int, optional): Number of tags to generate (max 13 for Etsy)
            
        Returns:
            list: List of optimized tags
        """
        logger.info(f"Optimizing tags for {base_keyword} {product_type}")
        
        # Combine keywords and long-tail keywords
        all_keywords = {**self.keywords, **self.long_tail_keywords}
        
        # Filter keywords related to base_keyword and product_type
        related_keywords = {}
        for keyword, data in all_keywords.items():
            if base_keyword.lower() in keyword.lower() or product_type.lower() in keyword.lower():
                related_keywords[keyword] = data
        
        # If not enough related keywords, add some general cat keywords
        if len(related_keywords) < count:
            for keyword, data in all_keywords.items():
                if keyword not in related_keywords:
                    related_keywords[keyword] = data
                    if len(related_keywords) >= count * 2:  # Get more than needed for sorting
                        break
        
        # Sort keywords by search volume / competition ratio (higher is better)
        sorted_keywords = sorted(
            related_keywords.items(),
            key=lambda x: x[1]['search_volume'] / max(x[1]['competition'], 0.1),
            reverse=True
        )
        
        # Select top keywords
        selected_keywords = [k for k, _ in sorted_keywords[:count]]
        
        # Ensure base_keyword and product_type are included
        if base_keyword not in selected_keywords:
            selected_keywords[-1] = base_keyword
        
        if product_type not in selected_keywords and len(selected_keywords) > 1:
            selected_keywords[-2] = product_type
        
        logger.info(f"Generated {len(selected_keywords)} optimized tags")
        
        return selected_keywords
    
    def optimize_title(self, base_keyword, product_type, tags=None):
        """Optimize title for an Etsy listing.
        
        Args:
            base_keyword (str): Base keyword for the listing
            product_type (str): Type of product
            tags (list, optional): List of tags to incorporate
            
        Returns:
            str: Optimized title
        """
        logger.info(f"Optimizing title for {base_keyword} {product_type}")
        
        # Select a random title template
        template = random.choice(self.title_templates)
        
        # Replace placeholders
        title = template.replace('{keyword}', base_keyword).replace('{product_type}', product_type)
        
        # Ensure title is not too long (Etsy limit is 140 characters)
        if len(title) > 140:
            title = title[:137] + '...'
        
        logger.info(f"Generated optimized title: {title}")
        
        return title
    
    def optimize_description(self, base_keyword, product_type, tags=None):
        """Optimize description for an Etsy listing.
        
        Args:
            base_keyword (str): Base keyword for the listing
            product_type (str): Type of product
            tags (list, optional): List of tags to incorporate
            
        Returns:
            str: Optimized description
        """
        logger.info(f"Optimizing description for {base_keyword} {product_type}")
        
        # Select a random description template
        template = random.choice(self.description_templates)
        
        # Replace placeholders
        description = template.replace('{keyword}', base_keyword).replace('{product_type}', product_type)
        
        # Replace product_type_upper with uppercase product_type
        description = description.replace('{product_type_upper}', product_type.upper())
        
        # Add tags as keywords at the end if provided
        if tags:
            description += "\n\n🔍 KEYWORDS: " + ", ".join(tags)
        
        logger.info(f"Generated optimized description (length: {len(description)})")
        
        return description
    
    def optimize_listing(self, base_keyword, product_type):
        """Optimize an Etsy listing with tags, title, and description.
        
        Args:
            base_keyword (str): Base keyword for the listing
            product_type (str): Type of product
            
        Returns:
            dict: Optimized listing data
        """
        logger.info(f"Optimizing listing for {base_keyword} {product_type}")
        
        # Optimize tags
        tags = self.optimize_tags(base_keyword, product_type)
        
        # Optimize title
        title = self.optimize_title(base_keyword, product_type, tags)
        
        # Optimize description
        description = self.optimize_description(base_keyword, product_type, tags)
        
        # Prepare optimized listing data
        optimized_listing = {
            'base_keyword': base_keyword,
            'product_type': product_type,
            'tags': tags,
            'title': title,
            'description': description,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Save optimized listing
        timestamp = int(time.time())
        safe_keyword = re.sub(r'[^\w\s]', '', base_keyword).replace(' ', '_')
        listing_path = os.path.join(self.data_dir, f"optimized_listing_{safe_keyword}_{timestamp}.json")
        
        with open(listing_path, 'w') as f:
            json.dump(optimized_listing, f, indent=2)
        
        logger.info(f"Optimized listing saved to: {listing_path}")
        
        return optimized_listing
    
    def analyze_competitor_listings(self, keyword, limit=10):
        """Analyze competitor listings for a keyword.
        
        Args:
            keyword (str): Keyword to analyze
            limit (int, optional): Maximum number of listings to analyze
            
        Returns:
            dict: Analysis results
        """
        logger.info(f"Analyzing competitor listings for keyword: {keyword}")
        
        try:
            # In a real implementation, we would use Etsy's API or scrape listings
            # For this demonstration, we'll simulate the API call
            
            # Simulate API call delay
            time.sleep(1)
            
            # Generate simulated listings
            listings = []
            for i in range(limit):
                listings.append({
                    'title': f"Simulated {keyword} listing {i+1}",
                    'description': f"This is a simulated description for a {keyword} listing.",
                    'tags': [f"tag{j}" for j in range(1, 14)],
                    'price': random.randint(1500, 5000) / 100,  # $15.00 - $50.00
                    'views': random.randint(100, 10000),
                    'favorites': random.randint(10, 1000),
                    'sales': random.randint(1, 100)
                })
            
            # Analyze titles
            title_words = []
            for listing in listings:
                words = re.findall(r'\b\w+\b', listing['title'].lower())
                title_words.extend(words)
            
            title_word_counts = Counter(title_words)
            top_title_words = title_word_counts.most_common(20)
            
            # Analyze tags
            all_tags = []
            for listing in listings:
                all_tags.extend(listing['tags'])
            
            tag_counts = Counter(all_tags)
            top_tags = tag_counts.most_common(20)
            
            # Analyze prices
            prices = [listing['price'] for listing in listings]
            avg_price = sum(prices) / len(prices) if prices else 0
            min_price = min(prices) if prices else 0
            max_price = max(prices) if prices else 0
            
            # Prepare analysis results
            analysis = {
                'keyword': keyword,
                'listings_analyzed': len(listings),
                'top_title_words': top_title_words,
                'top_tags': top_tags,
                'price_analysis': {
                    'average': round(avg_price, 2),
                    'minimum': round(min_price, 2),
                    'maximum': round(max_price, 2)
                },
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Save analysis results
            timestamp = int(time.time())
            safe_keyword = re.sub(r'[^\w\s]', '', keyword).replace(' ', '_')
            analysis_path = os.path.join(self.data_dir, f"competitor_analysis_{safe_keyword}_{timestamp}.json")
            
            with open(analysis_path, 'w') as f:
                json.dump(analysis, f, indent=2)
            
            logger.info(f"Competitor analysis saved to: {analysis_path}")
            
            return analysis
        
        except Exception as e:
            logger.error(f"Error analyzing competitor listings: {str(e)}")
            return None
    
    def generate_seo_report(self, keyword, product_type):
        """Generate an SEO report for a keyword and product type.
        
        Args:
            keyword (str): Keyword to analyze
            product_type (str): Type of product
            
        Returns:
            str: SEO report
        """
        logger.info(f"Generating SEO report for {keyword} {product_type}")
        
        try:
            # Get keyword data
            keyword_data = self.keywords.get(keyword, {'search_volume': 0, 'competition': 0})
            search_volume = keyword_data['search_volume']
            competition = keyword_data['competition']
            
            # Analyze competitor listings
            competitor_analysis = self.analyze_competitor_listings(keyword)
            
            # Optimize listing
            optimized_listing = self.optimize_listing(keyword, product_type)
            
            # Generate report
            report = []
            report.append(f"# SEO Report for {keyword} {product_type}")
            report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            # Keyword analysis section
            report.append("## Keyword Analysis")
            report.append(f"- **Primary Keyword**: {keyword}")
            report.append(f"- **Search Volume**: {search_volume}")
            report.append(f"- **Competition Level**: {competition}/10")
            
            if competition > 7:
                competition_level = "High"
                recommendation = "Consider targeting more specific long-tail keywords"
            elif competition > 4:
                competition_level = "Medium"
                recommendation = "Good balance of search volume and competition"
            else:
                competition_level = "Low"
                recommendation = "Great opportunity, but may have lower search volume"
            
            report.append(f"- **Competition Assessment**: {competition_level}")
            report.append(f"- **Recommendation**: {recommendation}\n")
            
            # Competitor analysis section
            if competitor_analysis:
                report.append("## Competitor Analysis")
                report.append(f"- **Listings Analyzed**: {competitor_analysis['listings_analyzed']}")
                
                report.append("\n### Top Title Words")
                for word, count in competitor_analysis['top_title_words'][:10]:
                    report.append(f"- {word}: {count} occurrences")
                
                report.append("\n### Top Tags")
                for tag, count in competitor_analysis['top_tags'][:10]:
                    report.append(f"- {tag}: {count} occurrences")
                
                report.append("\n### Price Analysis")
                price_analysis = competitor_analysis['price_analysis']
                report.append(f"- **Average Price**: ${price_analysis['average']}")
                report.append(f"- **Price Range**: ${price_analysis['minimum']} - ${price_analysis['maximum']}")
                
                # Price recommendation
                recommended_price = round(price_analysis['average'] * 0.9, 2)  # Slightly lower than average
                report.append(f"- **Recommended Price**: ${recommended_price} (slightly below average to attract buyers)\n")
            
            # Optimized listing section
            report.append("## Optimized Listing")
            report.append(f"- **Title**: {optimized_listing['title']}")
            report.append("\n### Optimized Tags")
            for tag in optimized_listing['tags']:
                report.append(f"- {tag}")
            
            report.append("\n### Optimized Description")
            report.append("```")
            report.append(optimized_listing['description'][:500] + "..." if len(optimized_listing['description']) > 500 else optimized_listing['description'])
            report.append("```\n")
            
            # Recommendations section
            report.append("## SEO Recommendations")
            report.append("1. **Use all 13 tags** allowed by Etsy to maximize visibility")
            report.append("2. **Include keywords in your title, description, and tags** for better search ranking")
            report.append("3. **Use long-tail keywords** to target specific customer searches")
            report.append("4. **Update your listings regularly** to keep them fresh in search results")
            report.append("5. **Monitor performance** and adjust your SEO strategy based on what works")
            
            # Save report
            timestamp = int(time.time())
            safe_keyword = re.sub(r'[^\w\s]', '', keyword).replace(' ', '_')
            report_path = os.path.join(self.data_dir, f"seo_report_{safe_keyword}_{timestamp}.md")
            
            with open(report_path, 'w') as f:
                f.write('\n'.join(report))
            
            logger.info(f"SEO report saved to: {report_path}")
            
            return '\n'.join(report)
        
        except Exception as e:
            logger.error(f"Error generating SEO report: {str(e)}")
            return f"Error generating SEO report: {str(e)}"

def main():
    """Main function to test SEO optimizer."""
    logger.info("Testing SEO Optimizer")
    
    # Create SEO optimizer
    optimizer = SEOOptimizer()
    
    # Update keywords from Etsy
    optimizer.update_keywords_from_etsy()
    
    # Generate long-tail keywords
    optimizer.generate_long_tail_keywords()
    
    # Test optimizing a listing
    optimized_listing = optimizer.optimize_listing("cat lover", "t-shirt")
    
    # Generate SEO report
    report = optimizer.generate_seo_report("cat lover", "t-shirt")
    
    print("SEO Optimization test completed successfully.")
    print(f"Optimized title: {optimized_listing['title']}")
    print(f"Number of optimized tags: {len(optimized_listing['tags'])}")
    print(f"SEO report length: {len(report)} characters")

if __name__ == "__main__":
    main()
