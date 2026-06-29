# ClearDischarge — Cotiviti Intern Assessment 2026

A fully local, open-source RAG-based agentic AI system for hospital discharge comprehension and post-discharge vital sign monitoring. No cloud, no internet required, no patient data leaves the device.

## Topic
Topic 2: Clinical Decision Making and Pattern Recognition in Health Care — Agentic AI for Treatment, Payment, and Operations

## Deliverables
- 📄 Written Report: `ClearDischarge_Report_Ramyashree.docx`
- 📊 Presentation: `ClearDischarge_Presentation_Ramyashree.pptx`
- 🎥 Video Recording: `Recording_zoom.mp4`
- 💻 POC Code: see folders below

## Key Features
- **classify_intent()** — classifies patient queries (Classification)
- **route_query()** — agentic router selects retrieval sections (Agentic AI)
- **score_readmission_risk()** — predicts 30-day readmission risk (Prediction)
- **detect_vitals_anomaly()** — time-series anomaly detection on 7-day vitals (Pattern Recognition)

## How to Run
```bash
pip install -r requirements.txt
python scripts/download_open_corpora.py
python scripts/build_indexes.py
python run_app.py
```
Open http://localhost:8080

For Vitals Monitor: http://localhost:8080/static/vitals.html

## Author
Fnu Ramyashree
