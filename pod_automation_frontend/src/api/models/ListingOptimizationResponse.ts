/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type ListingOptimizationResponse = {
    listing_id?: string;
    original_title?: string;
    original_tags?: Array<string>;
    original_description?: string;
    optimized_title?: string;
    optimized_tags?: Array<string>;
    optimized_description?: string;
    seo_score?: number;
    original_seo_score?: number;
    improvement_percentage?: number;
    processing_time_ms?: number;
    recommendations?: Array<{
        category?: 'title' | 'tags' | 'description';
        score?: number;
        feedback?: string;
    }>;
};

