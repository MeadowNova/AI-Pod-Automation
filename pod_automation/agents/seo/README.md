# SEO Module for POD Automation

This module provides SEO optimization functionality for Etsy listings.

## Features

- Fetch listings from Etsy
- Import listings to database
- Optimize listing titles and tags
- Approve optimizations
- Update listings on Etsy

## Proof of Concept Workflow

The SEO module includes a proof of concept workflow that demonstrates the complete process from importing listings to updating them on Etsy.

### Prerequisites

- Etsy API credentials configured in `~/.pod_automation_config.json`
- Supabase database configured (optional, but recommended for full functionality)

### Database Setup

If using Supabase, create the following tables:

1. `seo_listings` - Stores listing data
   - `id` (int, primary key)
   - `etsy_listing_id` (int)
   - `title_original` (text)
   - `description_original` (text)
   - `tags_original` (json)
   - `title_optimized` (text)
   - `description_optimized` (text)
   - `tags_optimized` (json)
   - `status` (text) - pending, optimized, approved, rejected, updated
   - `optimization_score` (float)
   - `optimization_date` (timestamp)
   - `approval_date` (timestamp)
   - `user_id` (text)
   - `created_at` (timestamp)
   - `updated_at` (timestamp)

2. `seo_optimization_history` - Stores optimization history
   - `id` (int, primary key)
   - `listing_id` (int, foreign key to seo_listings.id)
   - `optimization_type` (text) - tags, title, description, full
   - `changes_made` (json)
   - `algorithm_version` (text)
   - `performance_metrics` (json)
   - `optimization_date` (timestamp)

3. `seo_keywords` - Stores keyword data
   - `id` (int, primary key)
   - `keyword` (text)
   - `category` (text)
   - `search_volume` (int)
   - `competition` (float)
   - `relevance` (float)
   - `last_updated` (timestamp)

4. `seo_settings` - Stores module settings
   - `id` (int, primary key)
   - `setting_name` (text)
   - `setting_value` (text)
   - `description` (text)
   - `updated_at` (timestamp)

### Running the Proof of Concept

You can run the proof of concept workflow using the following command:

```bash
python -m pod_automation.agents.seo.poc_workflow --listing-count 5 --optimize-count 1 --update-etsy
```

Options:
- `--listing-count`: Number of listings to import (default: 5)
- `--optimize-count`: Number of listings to optimize (default: 1)
- `--update-etsy`: Update listings on Etsy (optional)

### Using the CLI

The SEO module also provides a command-line interface for individual operations:

1. Import listings to database:
```bash
python -m pod_automation.agents.seo.cli import --limit 5
```

2. List database entries:
```bash
python -m pod_automation.agents.seo.cli list
```

3. Optimize a listing (replace LISTING_ID with an actual Etsy listing ID):
```bash
python -m pod_automation.agents.seo.cli optimize LISTING_ID --advanced
```

4. Approve an optimization:
```bash
python -m pod_automation.agents.seo.cli approve LISTING_ID
```

5. Update a listing on Etsy:
```bash
python -m pod_automation.agents.seo.cli update LISTING_ID
```

## Integration with Dashboard

The SEO module is designed to be integrated with the POD Automation dashboard. The database structure supports the following workflow:

1. Import listings from Etsy
2. Display listings in dashboard
3. Optimize listings (individually or in bulk)
4. Review and approve optimizations
5. Update listings on Etsy

## Advanced Tag Optimizer

The SEO module includes an advanced tag optimizer that uses keyword data to generate optimized tags for Etsy listings. The optimizer considers:

- Keyword relevance
- Search volume
- Competition
- Etsy-specific SEO best practices

## Future Enhancements

- Performance tracking for optimized listings
- A/B testing for different optimization strategies
- Integration with other marketplaces (Printify, Shopify, etc.)
- Automated optimization scheduling
