/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EtsyListing } from '../models/EtsyListing';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class EtsyService {
    /**
     * Get user's Etsy listings
     * @param status Filter listings by status
     * @param page Page number
     * @param limit Number of items per page
     * @returns any List of Etsy listings
     * @throws ApiError
     */
    public static getEtsyListings(
        status?: 'active' | 'draft' | 'inactive' | 'all',
        page: number = 1,
        limit: number = 20,
    ): CancelablePromise<{
        data?: Array<EtsyListing>;
        pagination?: {
            total?: number;
            page?: number;
            limit?: number;
            pages?: number;
        };
    }> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/etsy/test-listings',
            query: {
                'status': status,
                'page': page,
                'limit': limit,
            },
            errors: {
                401: `Unauthorized`,
            },
        });
    }
}
