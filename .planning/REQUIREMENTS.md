# Requirements

## v1 Requirements

### Foundation (FOUND)

- [x] **FOUND-01**: Foundry project initialized
- [x] **FOUND-02**: Azure Cosmos DB for threat storage
- [x] **FOUND-03**: Azure AI Search for vector embeddings
- [x] **FOUND-04**: Basic threat data model (CVE, indicator, campaign)

### Collection (COLL)

- [x] **COLL-01**: CVE Agent pulls from NVD API
- [x] **COLL-02**: CVE Agent parses CVSS scores and descriptions
- [x] **COLL-03**: Intel Agent pulls from AlienVault OTX
- [x] **COLL-04**: Intel Agent normalizes threat indicators
- [x] **COLL-05**: News Agent monitors security RSS feeds
- [x] **COLL-06**: Data normalization layer for unified format

### Correlation (CORR)

- [x] **CORR-01**: Correlator Agent generates embeddings for threats
- [x] **CORR-02**: Correlator Agent finds similar threats via vector search
- [x] **CORR-03**: Correlator Agent links CVE + exploit + campaign
- [x] **CORR-04**: Correlation confidence scoring

### Prioritization (PRIO)

- [x] **PRIO-01**: User config for tech stack (e.g., Apache, PostgreSQL)
- [x] **PRIO-02**: Prioritizer Agent matches threats to user stack
- [x] **PRIO-03**: Relevance scoring (HIGH/MEDIUM/LOW/NONE)
- [x] **PRIO-04**: Reporter Agent generates executive brief

### Demo (DEMO)

- [x] **DEMO-01**: Sample user config for demo
- [ ] **DEMO-02**: 2-minute video showing correlation and prioritization
- [x] **DEMO-03**: README with setup instructions
- [x] **DEMO-04**: Example executive brief output

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
| FOUND-01 | Phase 1: Foundation | Complete | Foundry project running |
| FOUND-02 | Phase 1: Foundation | Complete | Cosmos DB accessible |
| FOUND-03 | Phase 1: Foundation | Complete | AI Search index created |
| FOUND-04 | Phase 1: Foundation | Complete | Data model defined |
| COLL-01 | Phase 2: Collection | Complete | CVEs retrieved from NVD |
| COLL-02 | Phase 2: Collection | Complete | CVSS parsed correctly |
| COLL-03 | Phase 2: Collection | Complete | AlienVault data retrieved |
| COLL-04 | Phase 2: Collection | Complete | Indicators normalized |
| COLL-05 | Phase 2: Collection | Complete | RSS feeds parsed |
| COLL-06 | Phase 2: Collection | Complete | Unified format works |
| CORR-01 | Phase 3: Correlation | Complete | Embeddings generated |
| CORR-02 | Phase 3: Correlation | Complete | Similar threats found |
| CORR-03 | Phase 3: Correlation | Complete | Links created |
| CORR-04 | Phase 3: Correlation | Complete | Confidence calculated |
| PRIO-01 | Phase 4: Prioritization | Complete | User config works |
| PRIO-02 | Phase 4: Prioritization | Complete | Stack matching works |
| PRIO-03 | Phase 4: Prioritization | Complete | Relevance scored |
| PRIO-04 | Phase 4: Prioritization | Complete | Brief generated |
| DEMO-01 | Phase 5: Demo | Complete | Demo config ready |
| DEMO-02 | Phase 5: Demo | Pending | Video recorded |
| DEMO-03 | Phase 5: Demo | Complete | README complete |
| DEMO-04 | Phase 5: Demo | Complete | Example brief included |

**Coverage:** 22/22 requirements mapped (100%)
