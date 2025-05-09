/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type ListingOptimizationResponse = {
    optimized_title?: string;
    optimized_tags?: Array<string>;
    optimized_description?: string;
    seo_score?: number;
    recommendations?: Array<{
        category?: 'title' | 'tags' | 'description';
        score?: number;
        feedback?: string;
    }>;
};

