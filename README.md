# ClearDischarge — Cotiviti Intern Assessment 2026

A fully local, open-source RAG-based agentic AI system for hospital discharge comprehension and post-discharge vital sign monitoring. No cloud, no internet required, no patient data leaves the device.

## Topic
Topic 2: Clinical Decision Making and Pattern Recognition in Health Care — Agentic AI for Treatment, Payment, and Operations

## Deliverables
- 📄 Written Report: `ClearDischarge_Report_Ramyashree.docx`
- 📊 Presentation: `ClearDischarge_Presentation_Ramyashree.pptx`
- 🎥 Video Recording: `Recording_zoom.mp4`
- 💻 POC Code: see folders below

## How It Works

### Module 1 — Discharge Note Explainer
![Main UI](screenshot_main.png)

Paste a hospital discharge note and get a plain-English explanation covering diagnosis, medications, follow-up steps, and warning signs. Two new agentic panels appear:
- **Agentic Router** — shows which sections the system decided to retrieve and why
- **30-Day Readmission Risk** — predicts LOW/MEDIUM/HIGH risk from clinical signals

### Module 2 — VitalPath: Vitals Monitor
![Vitals Monitor](screenshot_vitals.png)

Enter 7 days of post-discharge weight and blood pressure readings. The system runs z-score statistical analysis to detect anomalies and classifies the pattern as STABLE, WARNING, or CRITICAL with a care recommendation.

## Agentic Features (Topic 2 Primitives)
- `classify_intent()` — **Classification**: labels queries as medication/follow_up/warning_sign/diagnosis/general
- `route_query()` — **Agentic Routing & Chain Reasoning**: decides which databases to search based on classification
- `score_readmission_risk()` — **Prediction**: predicts 30-day readmission risk from discharge note signals
- `detect_vitals_anomaly()` — **Time-Series Anomaly Detection**: detects dangerous patterns in 7-day vital sign trends

## Evaluation Results
| Metric | Score |
|--------|-------|
| MRR | 0.576 |
| Recall@5 | 0.55 |
| FK Grade Level | 9.3 |
| Chunks Indexed | 49,423 |

## How to Run
```bash
pip install -r requirements.txt
python scripts/download_open_corpora.py
python scripts/build_indexes.py
python run_app.py
```
- Main app: http://localhost:8080
- Vitals Monitor: http://localhost:8080/static/vitals.html

## Author
Fnu Ramyashree | Cotiviti Intern Assessment | 2026
