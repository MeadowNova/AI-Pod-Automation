"""
AI-enhanced SEO optimizer for Etsy listings.

This module extends the base SEO optimizer with AI capabilities using Ollama and RAG.
"""

import os
import json
import logging
from datetime import datetime
import time
from typing import Dict, List, Any, Optional

import torch
from pod_automation.agents.seo.seo_optimizer import SEOOptimizer
from pod_automation.agents.seo.db import seo_db
from pod_automation.agents.seo.ai.ollama_client import OllamaClient
from pod_automation.agents.seo.ai.rag_system import RAGSystem
from pod_automation.agents.seo.ai.batch_processor import BatchProcessor
from pod_automation.utils.gpu_utils import get_device, gpu_memory_stats, clear_gpu_memory, optimize_for_inference

logger = logging.getLogger(__name__)

class AISEOOptimizer(SEOOptimizer):
    """AI-enhanced SEO optimizer for Etsy listings."""

    def __init__(self, config=None, generation_model="mistral:latest", embedding_model="nomic-embed-text", device_id=None, use_gpu=True):
        """Initialize AI SEO optimizer.

        Args:
            config (dict, optional): Configuration dictionary
            generation_model (str): Ollama model to use for text generation
            embedding_model (str): Ollama model to use for embeddings
            device_id (int, optional): Specific GPU device ID to use
            use_gpu (bool): Whether to use GPU acceleration if available
        """
        super().__init__(config)

        # Initialize device
        self.device = None
        if use_gpu:
            try:
                self.device = get_device(device_id)
                if self.device.type == 'cuda':
                    logger.info(f"Using GPU for AI SEO optimization: {torch.cuda.get_device_name(self.device)}")
                    # Optimize PyTorch for inference
                    optimize_for_inference()
                    # Log GPU memory stats
                    memory_stats = gpu_memory_stats()
                    logger.info(f"GPU memory stats: {memory_stats}")
                else:
                    logger.info("GPU not available, using CPU for AI SEO optimization")
            except Exception as e:
                logger.warning(f"Error initializing GPU: {str(e)}. Falling back to CPU.")
                self.device = torch.device("cpu")
        else:
            logger.info("GPU usage disabled, using CPU for AI SEO optimization")
            self.device = torch.device("cpu")

        # Initialize Ollama client with separate models for generation and embeddings
        self.ollama = OllamaClient(
            generation_model=generation_model,
            embedding_model=embedding_model
        )

        logger.info(f"Using generation model: {self.ollama.generation_model}")
        logger.info(f"Using embedding model: {self.ollama.embedding_model}")

        # Initialize RAG system with the selected device
        self.rag = RAGSystem(seo_db, self.ollama, device=self.device)

        # Initialize batch processor
        self.batch_processor = BatchProcessor(self.ollama, seo_db, max_workers=4)

        # Index data
        try:
            self.rag.index_keywords()
            self.rag.index_listings(limit=50)  # Limit to 50 listings for performance
        except Exception as e:
            logger.error(f"Error indexing data: {str(e)}")

    def optimize_listing_ai(self, etsy_listing_id=None, listing_data=None):
        """Optimize a listing using AI.

        Args:
            etsy_listing_id (int, optional): Etsy listing ID
            listing_data (dict, optional): Listing data (if not provided, will be fetched from database)

        Returns:
            dict: Optimized listing data
        """
        logger.info(f"Optimizing listing with AI: {etsy_listing_id}")

        # Get listing data if not provided
        if listing_data is None and etsy_listing_id is not None:
            listing_data = seo_db.get_listing(etsy_listing_id)

        if listing_data is None:
            logger.error("No listing data provided or found")
            return None

        # Extract base keyword and product type
        base_keyword = listing_data.get("base_keyword", "")
        product_type = listing_data.get("product_type", "")

        # If base_keyword or product_type not available, try to extract from title
        if not base_keyword or not product_type:
            title = listing_data.get("title_original", "")
            extracted_data = self.extract_keyword_and_product(title)

            if not base_keyword:
                base_keyword = extracted_data.get("base_keyword", "")

            if not product_type:
                product_type = extracted_data.get("product_type", "")

        # Retrieve market data
        query = f"{base_keyword} {product_type}"
        market_data = self.rag.retrieve_market_data(query)

        # Optimize title
        optimized_title = self.optimize_title_ai(listing_data, market_data)

        # Optimize tags
        optimized_tags = self.optimize_tags_ai(listing_data, market_data)

        # Optimize description
        optimized_description = self.optimize_description_ai(listing_data, market_data)

        # Analyze optimization
        analysis = self.analyze_listing(listing_data)

        # Prepare optimized listing data
        optimized_listing = {
            'etsy_listing_id': listing_data.get('etsy_listing_id'),
            'title_original': listing_data.get('title_original', ''),
            'title_optimized': optimized_title,
            'tags_original': listing_data.get('tags_original', []),
            'tags_optimized': optimized_tags,
            'description_original': listing_data.get('description_original', ''),
            'description_optimized': optimized_description,
            'base_keyword': base_keyword,
            'product_type': product_type,
            'status': 'optimized',
            'optimization_date': datetime.now().isoformat(),
            'optimization_score': analysis.get('score', 0),
            'notes': json.dumps(analysis.get('notes', {})),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        # Save to database if etsy_listing_id is provided
        if etsy_listing_id is not None:
            saved_listing = seo_db.create_or_update_listing(etsy_listing_id, optimized_listing)

            # Add optimization history
            if saved_listing and 'id' in saved_listing:
                changes_made = {
                    'title': {
                        'original': listing_data.get('title_original', ''),
                        'optimized': optimized_title
                    },
                    'tags': {
                        'original': listing_data.get('tags_original', []),
                        'optimized': optimized_tags
                    },
                    'description': {
                        'original_length': len(listing_data.get('description_original', '')),
                        'optimized_length': len(optimized_description)
                    }
                }

                seo_db.add_optimization_history(
                    saved_listing['id'],
                    'full_ai',
                    changes_made,
                    'ai_seo_optimizer_v1',
                    {'score': analysis.get('score', 0)}
                )

        # Clear GPU memory if using CUDA
        if hasattr(self, 'device') and self.device.type == 'cuda':
            clear_gpu_memory()

        return optimized_listing

    def check_gpu_status(self):
        """Check GPU status and memory usage.

        Returns:
            dict: GPU status information
        """
        if not hasattr(self, 'device') or self.device.type != 'cuda':
            return {"status": "CPU mode", "gpu_available": False}

        try:
            memory_stats = gpu_memory_stats()
            status = {
                "status": "GPU mode active",
                "gpu_available": True,
                "device_name": torch.cuda.get_device_name(self.device),
                "memory_stats": memory_stats
            }
            return status
        except Exception as e:
            logger.error(f"Error checking GPU status: {str(e)}")
            return {"status": "Error checking GPU", "error": str(e)}

    def extract_keyword_and_product(self, title):
        """Extract base keyword and product type from title.

        Args:
            title (str): Listing title

        Returns:
            dict: Extracted data
        """
        # Prepare prompt
        system_prompt = """You are an expert at analyzing Etsy product titles. Your task is to extract the base keyword and product type from a title."""

        prompt = f"""Extract the base keyword and product type from this Etsy listing title:

Title: {title}

Return your answer as a JSON object with two fields:
1. base_keyword: The main keyword that describes the product theme (e.g., "cat lover", "mountain landscape", "birthday gift")
2. product_type: The type of product being sold (e.g., "t-shirt", "wall art", "mug")

JSON:"""

        # Generate response
        response = self.ollama.generate(prompt, system_prompt)

        # Extract JSON from response
        try:
            # Find JSON object in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1

            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                extracted_data = json.loads(json_str)
                return extracted_data
            else:
                logger.error("Could not find JSON object in response")

                # Fallback: use simple heuristics
                words = title.lower().split()

                # Try to identify product type from common product words
                product_types = ["shirt", "t-shirt", "tshirt", "tee", "hoodie", "sweatshirt",
                                "print", "poster", "art", "mug", "pillow", "cushion", "bag", "tote"]

                product_type = next((word for word in words if word in product_types), "")

                # Use first 2-3 words as base keyword
                base_keyword = " ".join(words[:3])

                return {
                    "base_keyword": base_keyword,
                    "product_type": product_type
                }
        except Exception as e:
            logger.error(f"Error parsing extracted data: {str(e)}")
            return {
                "base_keyword": "",
                "product_type": ""
            }

    def optimize_title_ai(self, listing_data, market_data=None):
        """Generate optimized title using AI.

        Args:
            listing_data (dict): Listing data
            market_data (dict, optional): Market data

        Returns:
            str: Optimized title
        """
        logger.info("Optimizing title with AI")

        # Extract data
        original_title = listing_data.get("title_original", "")
        base_keyword = listing_data.get("base_keyword", "")
        product_type = listing_data.get("product_type", "")
        tags = listing_data.get("tags_original", [])

        # Prepare context
        context = ""
        if market_data:
            context = self.rag.format_context(
                market_data.get("keywords", []),
                market_data.get("listings", [])
            )

        # Prepare prompt
        system_prompt = """You are an expert Etsy SEO specialist. Your task is to optimize product titles for maximum visibility and conversion.
Follow these guidelines:
1. Titles should be 120-140 characters long
2. Include high-value keywords near the beginning
3. Use pipe symbols (|) to separate sections
4. Include product type, style, and occasion where relevant
5. Maintain readability while maximizing SEO value
6. Follow this format: [High Value Keyword] | [Design Theme] [Product Type] | [Style/Mood] | [Occasion] Gift | [Recipient]"""

        prompt = f"""Please optimize this Etsy listing title:

Original Title: {original_title}

Product Type: {product_type}
Primary Keyword: {base_keyword}
Tags: {', '.join(tags)}

{context}

Create an optimized title that follows Etsy SEO best practices. The title should be between 120-140 characters and use pipe symbols (|) to separate sections.

Optimized Title:"""

        # Generate optimized title
        optimized_title = self.ollama.generate(prompt, system_prompt)

        # Clean up the response (remove any explanations, just get the title)
        if ":" in optimized_title:
            optimized_title = optimized_title.split(":", 1)[1].strip()

        # Ensure title is not too long
        if len(optimized_title) > 140:
            optimized_title = optimized_title[:137] + "..."

        logger.info(f"Generated AI-optimized title: {optimized_title}")

        return optimized_title

    def optimize_tags_ai(self, listing_data, market_data=None):
        """Generate optimized tags using AI.

        Args:
            listing_data (dict): Listing data
            market_data (dict, optional): Market data

        Returns:
            list: Optimized tags
        """
        logger.info("Optimizing tags with AI")

        # Extract data
        original_title = listing_data.get("title_original", "")
        original_tags = listing_data.get("tags_original", [])
        base_keyword = listing_data.get("base_keyword", "")
        product_type = listing_data.get("product_type", "")

        # Prepare context
        context = ""
        if market_data:
            context = self.rag.format_context(
                market_data.get("keywords", []),
                market_data.get("listings", [])
            )

        # Prepare prompt
        system_prompt = """You are an expert Etsy SEO specialist. Your task is to optimize product tags for maximum visibility.
Follow these guidelines:
1. Generate exactly 13 tags (the maximum allowed by Etsy)
2. Each tag must be 20 characters or less
3. Include a mix of short-tail and long-tail keywords
4. Ensure all tags are relevant to the product
5. Include the primary keyword and product type
6. Format as a JSON array of strings"""

        prompt = f"""Please optimize these Etsy listing tags:

Original Title: {original_title}
Original Tags: {', '.join(original_tags)}

Product Type: {product_type}
Primary Keyword: {base_keyword}

{context}

Create 13 optimized tags that follow Etsy SEO best practices. Each tag must be 20 characters or less.
Return the tags as a JSON array of strings.

Optimized Tags:"""

        # Generate optimized tags
        response = self.ollama.generate(prompt, system_prompt)

        # Extract JSON array from response
        try:
            # Find JSON array in the response
            start_idx = response.find('[')
            end_idx = response.rfind(']') + 1

            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                optimized_tags = json.loads(json_str)

                # Ensure we have exactly 13 tags
                if len(optimized_tags) > 13:
                    optimized_tags = optimized_tags[:13]
                elif len(optimized_tags) < 13:
                    # Fill with original tags if we don't have enough
                    for tag in original_tags:
                        if tag not in optimized_tags and len(optimized_tags) < 13:
                            optimized_tags.append(tag)

                # Ensure all tags are 20 characters or less
                optimized_tags = [tag[:20] for tag in optimized_tags]

                logger.info(f"Generated {len(optimized_tags)} AI-optimized tags")
                return optimized_tags
            else:
                logger.error("Could not find JSON array in response")
                return original_tags
        except Exception as e:
            logger.error(f"Error parsing AI-generated tags: {str(e)}")
            return original_tags

    def optimize_description_ai(self, listing_data, market_data=None):
        """Generate optimized description using AI.

        Args:
            listing_data (dict): Listing data
            market_data (dict, optional): Market data

        Returns:
            str: Optimized description
        """
        logger.info("Optimizing description with AI")

        # Extract data
        original_title = listing_data.get("title_original", "")
        original_description = listing_data.get("description_original", "")
        base_keyword = listing_data.get("base_keyword", "")
        product_type = listing_data.get("product_type", "")
        tags = listing_data.get("tags_original", [])

        # Only optimize the intro paragraph to preserve the template structure
        intro_end = original_description.find("\n\n")
        if intro_end > 0:
            original_intro = original_description[:intro_end].strip()
            template_body = original_description[intro_end:].strip()
        else:
            # If we can't find a clear intro, use the first 200 characters
            original_intro = original_description[:200].strip()
            template_body = original_description[200:].strip()

        # Prepare context
        context = ""
        if market_data:
            context = self.rag.format_context(
                market_data.get("keywords", []),
                market_data.get("listings", [])
            )

        # Prepare prompt
        system_prompt = """You are an expert Etsy SEO specialist. Your task is to optimize product descriptions for maximum visibility and conversion.
Follow these guidelines:
1. Create an engaging, SEO-rich introduction paragraph
2. Include primary keywords naturally in the text
3. Highlight key product features and benefits
4. Use emotive language to connect with potential buyers
5. Keep the tone consistent with the brand voice"""

        prompt = f"""Please optimize the introduction paragraph for this Etsy listing description:

Original Title: {original_title}
Original Intro: {original_intro}

Product Type: {product_type}
Primary Keyword: {base_keyword}
Tags: {', '.join(tags)}

{context}

Create an optimized introduction paragraph that follows Etsy SEO best practices. The rest of the description template will be preserved.

Optimized Introduction:"""

        # Generate optimized intro
        optimized_intro = self.ollama.generate(prompt, system_prompt)

        # Combine optimized intro with existing template body
        optimized_description = f"{optimized_intro.strip()}\n\n{template_body}"

        logger.info(f"Generated AI-optimized description intro ({len(optimized_intro)} chars)")

        return optimized_description

    def analyze_listing(self, listing_data):
        """Analyze listing strengths and weaknesses.

        Args:
            listing_data (dict): Listing data

        Returns:
            dict: Analysis results
        """
        logger.info("Analyzing listing")

        # Extract data
        title = listing_data.get("title_original", "")
        tags = listing_data.get("tags_original", [])
        description = listing_data.get("description_original", "")

        # Prepare prompt
        system_prompt = """You are an expert Etsy SEO analyst. Your task is to analyze a listing and identify its strengths and weaknesses."""

        prompt = f"""Please analyze this Etsy listing:

Title: {title}

Tags: {', '.join(tags)}

Description (excerpt): {description[:500]}...

Analyze the listing's SEO strengths and weaknesses. Return your analysis as a JSON object with these fields:
1. score: A number from 0-100 representing the overall SEO quality
2. notes: An object with "strengths" and "weaknesses" arrays
3. recommendations: An array of specific recommendations for improvement

JSON:"""

        # Generate analysis
        response = self.ollama.generate(prompt, system_prompt)

        # Extract JSON from response
        try:
            # Find JSON object in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1

            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                analysis = json.loads(json_str)
                return analysis
            else:
                logger.error("Could not find JSON object in response")
                return {
                    "score": 50,
                    "notes": {
                        "strengths": ["Could not analyze strengths"],
                        "weaknesses": ["Could not analyze weaknesses"]
                    },
                    "recommendations": ["Could not generate recommendations"]
                }
        except Exception as e:
            logger.error(f"Error parsing analysis: {str(e)}")
            return {
                "score": 50,
                "notes": {
                    "strengths": ["Error analyzing strengths"],
                    "weaknesses": ["Error analyzing weaknesses"]
                },
                "recommendations": ["Error generating recommendations"]
            }

    def optimize_listings_batch(self, listings, max_listings=None):
        """Optimize multiple listings in a batch.

        Args:
            listings (list): List of listings to optimize
            max_listings (int, optional): Maximum number of listings to process

        Returns:
            list: Optimized listings
        """
        logger.info(f"Optimizing {len(listings)} listings in batch")

        # Limit the number of listings if specified
        if max_listings and len(listings) > max_listings:
            listings = listings[:max_listings]
            logger.info(f"Limited batch to {max_listings} listings")

        # Use the batch processor to optimize listings
        optimized_listings = self.batch_processor.optimize_listings(listings, self)

        # Log cache statistics
        cache_stats = self.ollama.get_cache_stats()
        logger.info(f"Embedding cache stats: {cache_stats}")

        return optimized_listings

    def explain_optimization(self, original, optimized):
        """Explain optimization changes.

        Args:
            original (dict): Original listing data
            optimized (dict): Optimized listing data

        Returns:
            str: Explanation of changes
        """
        logger.info("Generating optimization explanation")

        # Prepare prompt
        system_prompt = """You are an expert Etsy SEO specialist. Your task is to explain the changes made during optimization in a clear, educational way."""

        prompt = f"""Please explain the changes made during optimization:

Original Title: {original.get('title_original', '')}
Optimized Title: {optimized.get('title_optimized', '')}

Original Tags: {', '.join(original.get('tags_original', []))}
Optimized Tags: {', '.join(optimized.get('tags_optimized', []))}

Explain the key changes made and why they improve the listing's SEO. Focus on:
1. Title structure and keyword placement
2. Tag selection and relevance
3. Overall SEO impact

Explanation:"""

        # Generate explanation
        explanation = self.ollama.generate(prompt, system_prompt)

        return explanation