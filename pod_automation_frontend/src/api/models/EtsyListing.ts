/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type EtsyListing = {
    id: string;
    title: string;
    description?: string;
    tags?: Array<string>;
    price?: number;
    status?: EtsyListing.status;
    thumbnail_url?: string;
    seo_score?: number;
};
export namespace EtsyListing {
    export enum status {
        ACTIVE = 'active',
        DRAFT = 'draft',
        INACTIVE = 'inactive',
    }
}

