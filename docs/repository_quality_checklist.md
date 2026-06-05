# Repository Quality Checklist

This checklist is used to keep the repository suitable for public portfolio review.

## Data and Security

- Synthetic data only
- No real customer data
- No real transaction data
- No real alerts or confidential financial crime intelligence
- No credentials, private keys, service account files, or secrets
- No live GCP resources required

## Local Reproducibility

- Local setup documented
- End-to-end commands documented
- `scripts/run_all_local.sh` available for full demo workflow
- `scripts/final_project_check.py` available for readiness checks
- Generated sample outputs present
- Generated markdown reports present

## Code Quality

- Ruff passing
- Pytest passing
- CLI commands available for major workflows
- Lightweight dependencies only
- No cloud SDKs required
- No heavy ML, LLM, or dashboard dependencies introduced

## Documentation Completeness

- README is public-facing and professional
- Documentation index present
- End-to-end walkthrough present
- Architecture narrative present
- GCP reference architecture present
- Deployment blueprint present
- Distributed systems design present
- Security and governance mapping present
- Operations runbook present
- Sample output guide present

## Governance Evidence

- Data validation report present
- Feature summary present
- Model metrics present
- Model card present
- Monitoring report present
- Governance control checklist present
- Model risk assessment present
- Evidence inventory present
- Audit log present
- Lifecycle traceability present
- Governance evidence pack present

## Required Caveats

- Synthetic data caveat present
- Non-production caveat present
- Human review caveat present
- No autonomous final decisioning caveat present

## GCP Blueprint

- GCP service mapping present
- Mermaid architecture diagrams present
- Deployment blueprint documents phases and controls
- Architecture docs explain that no live infrastructure is deployed

## Final Review

Run:

```bash
python3 -m ruff check .
python3 -m pytest
python3 scripts/final_project_check.py
```

The repository is portfolio-ready when these checks pass and generated outputs are present.
