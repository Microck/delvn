# IntelMosaic Roadmap

## Overview

Multi-agent CTI platform that correlates threat feeds into actionable intelligence. Built for Microsoft AI Dev Days Hackathon 2026.

**Timeline:** 5 weeks (Feb 10 - Mar 15, 2026)
**Target Prizes:** Enterprise ($10k), Multi-Agent ($10k)

---

## Phase 1: Foundation

**Goal:** Infrastructure + data model

**Duration:** ~1 week

**Requirements Covered:**
- FOUND-01: Foundry project initialized
- FOUND-02: Azure Cosmos DB for threat storage
- FOUND-03: Azure AI Search for vector embeddings
- FOUND-04: Basic threat data model (CVE, indicator, campaign)

**Success Criteria:**
1. Foundry project running
2. Cosmos DB accessible and configured
3. AI Search index created for embeddings
4. Threat data model defined and validated

**Deliverables:**
- `src/models/threat.py`
- `src/storage/cosmos.py`
- `src/storage/search.py`
- `infra/foundry_config.yaml`

---

## Phase 2: Collection Agents

**Goal:** 3 collector agents pulling from data sources

**Duration:** ~1 week

**Requirements Covered:**
- COLL-01: CVE Agent pulls from NVD API
- COLL-02: CVE Agent parses CVSS scores and descriptions
- COLL-03: Intel Agent pulls from AlienVault OTX
- COLL-04: Intel Agent normalizes threat indicators
- COLL-05: News Agent monitors security RSS feeds
- COLL-06: Data normalization layer for unified format

**Success Criteria:**
1. CVEs retrieved from NVD API
2. CVSS scores and descriptions parsed correctly
3. AlienVault data retrieved successfully
4. Threat indicators normalized to unified format
5. RSS feeds parsed (HackerNews, BleepingComputer)
6. All data in unified threat format

**Deliverables:**
- `src/agents/cve_agent.py`
- `src/agents/intel_agent.py`
- `src/agents/news_agent.py`
- `src/models/unified_threat.py`

---

## Phase 3: Correlation

**Goal:** Embedding-based threat correlation

**Duration:** ~1 week

**Requirements Covered:**
- CORR-01: Correlator Agent generates embeddings for threats
- CORR-02: Correlator Agent finds similar threats via vector search
- CORR-03: Correlator Agent links CVE + exploit + campaign
- CORR-04: Correlation confidence scoring

**Success Criteria:**
1. Embeddings generated for all threats
2. Vector search finds semantically similar threats
3. Links created between related threats
4. Confidence score calculated for correlations

**Deliverables:**
- `src/agents/correlator_agent.py`
- `src/models/correlation.py`

---

## Phase 4: Prioritization & Reporting

**Goal:** User-specific prioritization + executive brief

**Duration:** ~1 week

**Requirements Covered:**
- PRIO-01: User config for tech stack (e.g., Apache, PostgreSQL)
- PRIO-02: Prioritizer Agent matches threats to user stack
- PRIO-03: Relevance scoring (HIGH/MEDIUM/LOW/NONE)
- PRIO-04: Reporter Agent generates executive brief

**Success Criteria:**
1. User can configure their tech stack
2. Threats matched to user's stack
3. Relevance scores assigned correctly
4. Executive brief is readable and actionable

**Deliverables:**
- `src/config/user_stack.yaml`
- `src/agents/prioritizer_agent.py`
- `src/agents/reporter_agent.py`
- `src/models/brief.py`

---

## Phase 5: Demo & Submit

**Goal:** Polished demo and documentation

**Duration:** ~1 week

**Requirements Covered:**
- DEMO-01: Sample user config for demo
- DEMO-02: 2-minute video showing correlation and prioritization
- DEMO-03: README with setup instructions
- DEMO-04: Example executive brief output

**Success Criteria:**
1. Demo config ready (Apache, PostgreSQL, React)
2. Video shows full flow in under 2 minutes
3. README includes setup, architecture, usage
4. Example brief included in repo

**Deliverables:**
- `demo/config.yaml`
- `demo/video.mp4`
- `README.md`
- `docs/example_brief.md`

---

## Coverage Validation

All 22 v1 requirements are mapped:
- Phase 1: FOUND-01 to FOUND-04 (4 requirements)
- Phase 2: COLL-01 to COLL-06 (6 requirements)
- Phase 3: CORR-01 to CORR-04 (4 requirements)
- Phase 4: PRIO-01 to PRIO-04 (4 requirements)
- Phase 5: DEMO-01 to DEMO-04 (4 requirements)

**Total: 22/22 requirements covered (100%)**

---

*Last updated: 2026-02-08*
