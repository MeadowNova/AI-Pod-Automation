import { SeoService as SeoApiService } from '../api/services/SeoService';
import { ListingOptimizationRequest } from '../api/models/ListingOptimizationRequest';
import { ListingOptimizationResponse } from '../api/models/ListingOptimizationResponse';
import { ApiError } from '../api/core/ApiError';

/**
 * Optimize an Etsy listing with fallback to mock data
 */
export async function optimizeListing(request: ListingOptimizationRequest) {
  try {
    // Try to get real data from API
    console.log('Calling SEO API service to optimize listing:', request);
    const response = await SeoApiService.optimizeListing(request);
    console.log('Received response from SEO API:', response);
    return { data: response, isMockData: false };
  } catch (error) {
    console.warn('Error optimizing listing from API, falling back to mock data:', error);
    
    // Generate mock optimization response
    const mockResponse: ListingOptimizationResponse = {
      listing_id: request.listing_id,
      optimized_title: request.current_title 
        ? `Improved ${request.current_title.split(' ').slice(0, 3).join(' ')} - SEO Enhanced Version with Keywords`
        : "Optimized Title Example",
      optimized_tags: request.current_tags 
        ? [...request.current_tags, "additional tag", "seo keyword"] 
        : ["tag1", "tag2", "seo keyword"],
      optimized_description: request.current_description
        ? `Enhanced version of: ${request.current_description?.substring(0, 50)}...\n\nWith additional SEO-friendly content that helps buyers find this product more easily.`
        : "Optimized description example with SEO-friendly content.",
      seo_score: 85,
      recommendations: [
        {
          category: "title",
          score: 80,
          feedback: "Title has good keywords but could be more specific."
        },
        {
          category: "tags",
          score: 90,
          feedback: "Good use of tags, consider adding more long-tail keywords."
        },
        {
          category: "description",
          score: 85,
          feedback: "Description is detailed but could include more product specifications."
        }
      ]
    };
    
    return { data: mockResponse, isMockData: true };
  }
}

/**
 * Optimize multiple Etsy listings in batch with fallback to mock data
 */
export async function optimizeListingsBatch(
  listings: Array<{
    id: string;
    title?: string;
    tags?: string[];
    description?: string;
  }>,
  maxListings?: number
) {
  try {
    // In a real implementation, this would call the API service
    // For now, we'll just return mock data
    console.log(`Would optimize ${listings.length} listings in batch`);
    
    // Generate mock batch optimization response
    const mockResults: ListingOptimizationResponse[] = listings.slice(0, maxListings || listings.length).map(listing => ({
      listing_id: listing.id,
      optimized_title: listing.title 
        ? `Improved ${listing.title.split(' ').slice(0, 3).join(' ')} - SEO Enhanced Version`
        : "Optimized Title Example",
      optimized_tags: listing.tags 
        ? [...listing.tags, "additional tag", "seo keyword"] 
        : ["tag1", "tag2", "seo keyword"],
      optimized_description: listing.description
        ? `Enhanced version of: ${listing.description.substring(0, 50)}...\n\nWith additional SEO-friendly content.`
        : "Optimized description example with SEO-friendly content.",
      seo_score: 75 + Math.floor(Math.random() * 20),
      recommendations: [
        {
          category: "title",
          score: 70 + Math.floor(Math.random() * 30),
          feedback: "Title has good keywords but could be more specific."
        },
        {
          category: "tags",
          score: 80 + Math.floor(Math.random() * 20),
          feedback: "Good use of tags, consider adding more long-tail keywords."
        }
      ]
    }));
    
    return {
      results: mockResults,
      processed_count: mockResults.length,
      total_count: listings.length,
      cache_stats: {
        hits: 5,
        misses: mockResults.length,
        size: 20,
        evictions: 0
      },
      isMockData: true
    };
  } catch (error) {
    throw new ApiError({
      name: 'Service Error',
      message: 'Failed to optimize listings in batch',
      status: 500,
      body: { detail: 'Internal service error' }
    });
  }
}

/**
 * Get SEO dashboard data with fallback to mock data
 */
export async function getSEODashboard() {
  try {
    // In a real implementation, this would call the API service
    // For now, we'll just return mock data
    console.log('Would fetch SEO dashboard data');
    
    return {
      data: {
        overall_seo_score: 72,
        listings_optimized: 15,
        total_listings: 25,
        recent_listings: [
          {
            id: "12345",
            title: "Vintage Sunset T-Shirt - Retro 80s Style Graphic Tee",
            seo_score: 85,
            thumbnail_url: "https://example.com/images/vintage-sunset-tee.jpg"
          },
          {
            id: "67890",
            title: "Funny Cat Mug - \"I Need More Coffee\" - Cute Pet Lover Gift",
            seo_score: 65,
            thumbnail_url: "https://example.com/images/cat-coffee-mug.jpg"
          },
          {
            id: "24680",
            title: "Minimalist Line Art Print - Abstract Face Poster",
            seo_score: 78,
            thumbnail_url: "https://example.com/images/line-art-print.jpg"
          }
        ],
        optimization_recommendations: [
          "Use all 13 available tags for each listing",
          "Ensure titles are 120-140 characters long",
          "Include relevant keywords in the first 40 characters of titles"
        ]
      },
      isMockData: true
    };
  } catch (error) {
    throw new ApiError({
      name: 'Service Error',
      message: 'Failed to fetch SEO dashboard data',
      status: 500,
      body: { detail: 'Internal service error' }
    });
  }
}