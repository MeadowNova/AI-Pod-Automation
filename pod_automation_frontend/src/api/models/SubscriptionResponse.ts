/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SubscriptionPlan } from './SubscriptionPlan';
export type SubscriptionResponse = {
    id: string;
    status: SubscriptionResponse.status;
    plan: SubscriptionPlan;
    current_period_end?: string;
    cancel_at_period_end?: boolean;
};
export namespace SubscriptionResponse {
    export enum status {
        ACTIVE = 'active',
        CANCELED = 'canceled',
        PAST_DUE = 'past_due',
        TRIALING = 'trialing',
    }
}

