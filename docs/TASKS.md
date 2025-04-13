
# ✅ POD Automation System — Integration To-Do List

## 🧠 Foundation-Level Tasks

### 1. Create the Orchestrator “Brain”
- [ ] File: `agents/automation_brain.py`
- [ ] Define `PODAutomationBrain` with `.run_full_cycle()`
- [ ] Sequence: TrendAgent → PromptOptimizerAgent → MockupAgent → PublishingAgent → PerformanceAgent

### 2. Add the Insight Agent (Quasar AI)
- [ ] File: `agents/insight_agent.py`
- [ ] Connect to OpenRouter using `quora/quasar-v1`
- [ ] Methods: `analyze_trends()`, `rewrite_title()`, `extract_tags()`

### 3. Integrate SQLite via MCP
- [ ] Use `sqlite_mcp` to log:
  - Published products
  - Performance metrics
  - A/B test results
- [ ] Table: `insights`

### 4. Implement Save-to-Memory System
- [ ] Use `agents/rule_memory_agent.py`
- [ ] Methods: `save_rule()`, `save_batch()`
- [ ] Track updates in `clinerules.revisions.md`
- [ ] Optional UI: `ui/streamlit_rule_saver.py`

### 5. Standardize `.run()` in All Agents
- [ ] Add `.run()` method to each agent
- [ ] Add basic logging

---

## 🌱 Growth-Level Tasks

### 6. Add Crawlee Trend Scraper
- [ ] Install Crawlee + Playwright
- [ ] Scrape Pinterest → `/data/trends/pinterest_{date}.json`
- [ ] Feed result into `TrendAgent` + `InsightAgent`

### 7. Sync Airtable or Notion
- [ ] Use `pyairtable` or Notion SDK
- [ ] Sync from `PublishingAgent`

### 8. Memo Generator from Performance Logs
- [ ] After `PerformanceAgent`, use `InsightAgent` to analyze KPIs
- [ ] Save memo in `sqlite.insights`
- [ ] Display in dashboard

### 9. Build First Dashboard View
- [ ] File: `dash/main.py`
- [ ] Show mockups, tags, insights
- [ ] Add “Run Full Cycle” button

---

## 🧼 Project Hygiene

- [ ] Write `.run()` tests for all agents
- [ ] Add `install.sh` to clean `Zone.Identifier` files
- [ ] Log all publishes to SQLite
- [ ] Regularly update `clinerules.txt` with rule changes
