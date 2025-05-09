/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ListingOptimizationRequest } from '../models/ListingOptimizationRequest';
import type { ListingOptimizationResponse } from '../models/ListingOptimizationResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class SeoService {
    /**
     * Optimize an Etsy listing's SEO
     * @param requestBody
     * @returns ListingOptimizationResponse Optimized listing data
     * @throws ApiError
     */
    public static optimizeListing(
        requestBody: ListingOptimizationRequest,
    ): CancelablePromise<ListingOptimizationResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/seo/optimize-listing',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                401: `Unauthorized`,
                404: `Listing not found`,
            },
        });
    }
}
