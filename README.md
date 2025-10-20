# Australia Migration Intelligence (Snowflake + Cortex AI-ready)

This repo builds an **internal migration intelligence mart for Australia** using:
- **Snowflake Marketplace** data (AusPost Movers + ABS geography),
- A simple **REF → SILVER → GOLD** medallion model, and
- A **Cortex Analyst** semantic model (YAML) ready for AI Q&A (region availability permitting).

> If Cortex Analyst isn’t enabled in your region yet, you can still run all SQL and use the YAML once it’s available.

## Architecture
![Uploading Australia Migration Intelligence Platform — Simple Overview (Snowflake + Cortex AI).png…]()



**Layers**
- **REF** – reference view mapping **POA (postcode areas)** to region/state from ABS geography.
- **SILVER** – cleans & enriches AusPost Movers with human-readable regions/states.
- **GOLD** – business views:
  - `STATE_MONTHLY_FLOWS` (monthly moves by state pair),
  - `STATE_OD_MATRIX` (state origin–destination matrix),
  - `TOP_SUBURB_OD` (top postcode flows).

## Prereqs

- Snowflake account (role with CREATE DB/SCHEMA/VIEW privileges).
- You’ve **added these Marketplace shares**:
  - `AUSTRALIA_POST_MOVERS_STATISTICS` (from Data Army / PropTrak)
  - `GEOGRAPHY__BOUNDARIES__INSIGHTS__AUSTRALIA` (ABS/GA compiled boundaries)
- A small **warehouse** (e.g., `COMPUTE_WH` XS) is enough.

## Quickstart

1. Open **Worksheets** and run the files in this order from `/sql`:

   - `00_init_snowflake.sql`
   - `10_ref_region_mapping.sql`
   - `20_silver_movers_enriched.sql`
   - `30_gold_state_monthly_flows.sql`
   - `31_gold_state_od_matrix.sql`
   - `32_gold_top_suburb_od.sql`
   - `40_grants_and_cortex_stage.sql` (creates stage for semantic YAML)

2. (Optional but recommended) Upload `cortex/MIGRATION_ANALYST.yaml` to the stage:
   - UI → Databases → `RIPPAA_MIGRATION.GOLD` → Stage `CORTEX_STAGE` → **Upload** `MIGRATION_ANALYST.yaml`
   - Or use SnowSQL `PUT` (see comments in `40_grants_and_cortex_stage.sql`).

3. **Test**:
   ```sql
   -- Top inbound states for 2020
   SELECT TO_STATE, SUM(MOVES) AS TOTAL_MOVES
   FROM RIPPAA_MIGRATION.GOLD.STATE_MONTHLY_FLOWS
   WHERE STAT_MONTH LIKE '2020-%'
   GROUP BY TO_STATE
   ORDER BY TOTAL_MOVES DESC;
