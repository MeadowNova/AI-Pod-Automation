/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type SubscriptionPlan = {
    id: string;
    name: string;
    description?: string;
    price: number;
    interval?: SubscriptionPlan.interval;
    features?: Array<string>;
};
export namespace SubscriptionPlan {
    export enum interval {
        MONTH = 'month',
        YEAR = 'year',
    }
}

