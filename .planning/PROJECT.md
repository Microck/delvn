# Delvn

## What This Is

A multi-agent CTI (Cyber Threat Intelligence) platform that correlates threat feeds into actionable intelligence. Specialized agents collect from CVE databases, threat intel APIs, and security news, then correlate and prioritize threats based on your specific tech stack. Built for the Microsoft AI Dev Days Hackathon 2026.

## Core Value

**Security teams drown in threat data. 6 specialized agents collect, correlate, and prioritize threats — delivering an executive brief of what matters to YOUR infrastructure.**

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] CVE Agent that monitors NVD for new vulnerabilities
- [ ] Intel Agent that pulls from AlienVault OTX
- [ ] News Agent that monitors security news and breach reports
- [ ] Correlator Agent that links related threats using embeddings
- [ ] Prioritizer Agent that ranks by relevance to user's tech stack
- [ ] Reporter Agent that generates executive briefings
- [ ] User config for tech stack (e.g., "I use Apache, PostgreSQL")
- [ ] 2-minute demo video showing correlation and prioritization

### Out of Scope

- Real-time alerting — batch processing for demo
- SIEM integration — standalone demo
- Automated blocking/patching — informational only
- More than 3 data sources — NVD, AlienVault, RSS only
- Historical trend analysis — current threats only

## Context

**Hackathon:** Microsoft AI Dev Days 2026 (Feb 10 - Mar 15, 2026)

**Target Prizes:**
- Primary: Enterprise ($10,000)
- Secondary: Multi-Agent ($10,000)

**Why This Wins:**
- Enterprise pain point: Security teams drown in data
- Multi-agent natural fit: Each source = separate agent
- Correlation is hard: Manual process today, agents automate it

**Data Sources (MVP):**
1. NVD — CVE database (free, reliable)
2. AlienVault OTX — Threat intel (free tier)
3. Security news RSS — HackerNews, BleepingComputer

## Constraints

- **Timeline**: 5 weeks (Feb 10 - Mar 15, 2026)
- **Perfect Tech Stack**:
  - **Language**: Python 3.12+ (ETL + parsing + scoring + embeddings iteration speed)
  - **Runtime/Packaging**: `uv` + `pyproject.toml` + lockfile for reproducibility
  - **Data modeling**: Pydantic v2
  - **HTTP**: httpx
  - **Reliability**: tenacity for retries/backoff
  - **Azure integration**: Cosmos DB (`azure-cosmos`), Azure AI Search (`azure-search-documents`), Entra auth (`azure-identity`)
  - **Testing**: pytest
- **Model Access**: GPT-4o via Foundry
- **Storage**: Azure Cosmos DB (threats), Azure AI Search (embeddings)
- **APIs**: NVD API, AlienVault OTX API
- **Demo**: 2-minute video required

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 3 data sources max | Avoid scope creep, demo quality | — Pending |
| Embedding-based correlation | Semantic matching of threats | — Pending |
| User config for stack | Personalized prioritization | — Pending |
| Executive brief output | Clear business value | — Pending |

---
*Last updated: 2026-02-08 after project initialization*
