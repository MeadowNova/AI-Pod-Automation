import { EtsyService as EtsyApiService } from '../api/services/EtsyService';
import { EtsyListing } from '../api/models/EtsyListing';
import { ApiError } from '../api/core/ApiError';

// Mock data for development when API is not available
const MOCK_LISTINGS: EtsyListing[] = [
  {
    id: "12345",
    title: "Vintage Sunset T-Shirt - Retro 80s Style Graphic Tee",
    description: "A super soft vintage-style t-shirt featuring a stunning retro sunset graphic. Perfect for 80s enthusiasts and lovers of unique graphic tees. Made from 100% cotton for maximum comfort.",
    tags: ["vintage t-shirt", "retro shirt", "80s graphics", "sunset tee", "graphic tee"],
    price: 24.99,
    status: EtsyListing.status.ACTIVE,
    thumbnail_url: "https://example.com/images/vintage-sunset-tee.jpg",
    seo_score: 75
  },
  {
    id: "67890",
    title: "Funny Cat Mug - \"I Need More Coffee\" - Cute Pet Lover Gift",
    description: "Start your day with a smile with this hilarious cat mug! Features a cute cat illustration and the relatable phrase \"I Need More Coffee\". A great gift for any cat owner or coffee addict.",
    tags: ["cat mug", "funny coffee mug", "pet lover gift", "cute cat", "coffee lover"],
    price: 15.99,
    status: EtsyListing.status.ACTIVE,
    thumbnail_url: "https://example.com/images/cat-coffee-mug.jpg",
    seo_score: 60
  },
  {
    id: "24680",
    title: "Minimalist Line Art Print - Abstract Face Poster, Modern Wall Decor",
    description: "Add a touch of modern elegance to your home with this minimalist line art print. Featuring an abstract face design, this poster is perfect for contemporary interiors. High-quality print on premium paper.",
    tags: ["line art", "abstract print", "minimalist decor", "modern wall art", "face poster"],
    price: 18.50,
    status: EtsyListing.status.DRAFT,
    thumbnail_url: "https://example.com/images/line-art-print.jpg",
    seo_score: 85
  }
];

/**
 * Get Etsy listings with fallback to mock data
 */
export async function getEtsyListings(
  status?: 'active' | 'draft' | 'inactive' | 'all',
  page: number = 1,
  limit: number = 20
) {
  try {
    // Try to get real data from API
    console.log('Calling Etsy API service to get listings');
    const response = await EtsyApiService.getEtsyListings(status, page, limit);
    console.log('Received response from Etsy API:', response);
    return { data: response.data, pagination: response.pagination, isMockData: false };
  } catch (error) {
    console.warn('Error fetching Etsy listings from API, falling back to mock data:', error);
    
    // Filter mock data by status if provided
    let filteredListings = [...MOCK_LISTINGS];
    if (status && status !== 'all') {
      filteredListings = MOCK_LISTINGS.filter(listing => listing.status === status);
    }
    
    // Create pagination info
    const total = filteredListings.length;
    const pages = Math.ceil(total / limit);
    const startIdx = (page - 1) * limit;
    const endIdx = Math.min(startIdx + limit, total);
    const paginatedListings = filteredListings.slice(startIdx, endIdx);
    
    return {
      data: paginatedListings,
      pagination: {
        total: total,
        page: page,
        limit: limit,
        pages: pages
      },
      isMockData: true
    };
  }
}

/**
 * Get a specific Etsy listing with fallback to mock data
 */
export async function getEtsyListing(listingId: string) {
  try {
    // In a real implementation, this would call the API service
    // For now, we'll just use mock data
    const listing = MOCK_LISTINGS.find(l => l.id === listingId);
    
    if (!listing) {
      throw new ApiError({
        name: 'Not Found',
        message: `Listing with ID ${listingId} not found`,
        status: 404,
        body: { detail: `Listing with ID ${listingId} not found` }
      });
    }
    
    return { data: listing, isMockData: true };
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    
    throw new ApiError({
      name: 'Service Error',
      message: 'Failed to fetch Etsy listing',
      status: 500,
      body: { detail: 'Internal service error' }
    });
  }
}

/**
 * Update an Etsy listing
 */
export async function updateEtsyListing(
  listingId: string, 
  data: {
    title?: string;
    description?: string;
    tags?: string[];
  }
) {
  try {
    // In a real implementation, this would call the API service
    // For now, we'll just return a success message
    console.log(`Would update Etsy listing ${listingId} with data:`, data);
    
    return {
      success: true,
      message: 'Listing updated successfully',
      isMockData: true
    };
  } catch (error) {
    throw new ApiError({
      name: 'Service Error',
      message: 'Failed to update Etsy listing',
      status: 500,
      body: { detail: 'Internal service error' }
    });
  }
}