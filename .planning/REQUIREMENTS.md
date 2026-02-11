# Requirements

## v1 Requirements

### Foundation (FOUND)

- [ ] **FOUND-01**: Foundry project initialized
- [ ] **FOUND-02**: Azure Cosmos DB for threat storage
- [ ] **FOUND-03**: Azure AI Search for vector embeddings
- [ ] **FOUND-04**: Basic threat data model (CVE, indicator, campaign)

### Collection (COLL)

- [ ] **COLL-01**: CVE Agent pulls from NVD API
- [ ] **COLL-02**: CVE Agent parses CVSS scores and descriptions
- [ ] **COLL-03**: Intel Agent pulls from AlienVault OTX
- [ ] **COLL-04**: Intel Agent normalizes threat indicators
- [ ] **COLL-05**: News Agent monitors security RSS feeds
- [ ] **COLL-06**: Data normalization layer for unified format

### Correlation (CORR)

- [ ] **CORR-01**: Correlator Agent generates embeddings for threats
- [ ] **CORR-02**: Correlator Agent finds similar threats via vector search
- [ ] **CORR-03**: Correlator Agent links CVE + exploit + campaign
- [ ] **CORR-04**: Correlation confidence scoring

### Prioritization (PRIO)

- [ ] **PRIO-01**: User config for tech stack (e.g., Apache, PostgreSQL)
- [ ] **PRIO-02**: Prioritizer Agent matches threats to user stack
- [ ] **PRIO-03**: Relevance scoring (HIGH/MEDIUM/LOW/NONE)
- [ ] **PRIO-04**: Reporter Agent generates executive brief

### Demo (DEMO)

- [ ] **DEMO-01**: Sample user config for demo
- [ ] **DEMO-02**: 2-minute video showing correlation and prioritization
- [ ] **DEMO-03**: README with setup instructions
- [ ] **DEMO-04**: Example executive brief output

---

## v2 Requirements

### Enhancements

- [ ] Additional data sources (Shodan, VirusTotal)
- [ ] Real-time alerting for critical threats
- [ ] Historical trend analysis
- [ ] SIEM integration (Splunk, Sentinel)

---

## Out of Scope

- **Real-time alerting** — batch processing for demo
- **SIEM integration** — standalone demo
- **Automated blocking/patching** — informational only
- **More than 3 sources** — NVD, AlienVault, RSS only
- **Historical trends** — current threats only

---

## Traceability

| REQ-ID | Phase | Status | Success Criteria |
|--------|-------|--------|------------------|
| FOUND-01 | Phase 1: Foundation | Pending | Foundry project running |
| FOUND-02 | Phase 1: Foundation | Pending | Cosmos DB accessible |
| FOUND-03 | Phase 1: Foundation | Pending | AI Search index created |
| FOUND-04 | Phase 1: Foundation | Pending | Data model defined |
| COLL-01 | Phase 2: Collection | Pending | CVEs retrieved from NVD |
| COLL-02 | Phase 2: Collection | Pending | CVSS parsed correctly |
| COLL-03 | Phase 2: Collection | Pending | AlienVault data retrieved |
| COLL-04 | Phase 2: Collection | Pending | Indicators normalized |
| COLL-05 | Phase 2: Collection | Pending | RSS feeds parsed |
| COLL-06 | Phase 2: Collection | Pending | Unified format works |
| CORR-01 | Phase 3: Correlation | Pending | Embeddings generated |
| CORR-02 | Phase 3: Correlation | Pending | Similar threats found |
| CORR-03 | Phase 3: Correlation | Pending | Links created |
| CORR-04 | Phase 3: Correlation | Pending | Confidence calculated |
| PRIO-01 | Phase 4: Prioritization | Pending | User config works |
| PRIO-02 | Phase 4: Prioritization | Pending | Stack matching works |
| PRIO-03 | Phase 4: Prioritization | Pending | Relevance scored |
| PRIO-04 | Phase 4: Prioritization | Pending | Brief generated |
| DEMO-01 | Phase 5: Demo | Pending | Demo config ready |
| DEMO-02 | Phase 5: Demo | Pending | Video recorded |
| DEMO-03 | Phase 5: Demo | Pending | README complete |
| DEMO-04 | Phase 5: Demo | Pending | Example brief included |

**Coverage:** 22/22 requirements mapped (100%)
