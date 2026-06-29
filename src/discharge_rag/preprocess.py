from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

COMMON_ABBREVIATIONS = {
    # Heart / Cardiovascular
    "hfref": "heart failure with reduced ejection fraction",
    "hfpef": "heart failure with preserved ejection fraction",
    "hf": "heart failure",
    "chf": "congestive heart failure",
    "cad": "coronary artery disease",
    "mi": "myocardial infarction",
    "stemi": "ST-elevation myocardial infarction",
    "nstemi": "non-ST-elevation myocardial infarction",
    "afib": "atrial fibrillation",
    "af": "atrial fibrillation",
    "avr": "aortic valve replacement",
    "cabg": "coronary artery bypass graft surgery",
    "ef": "ejection fraction",
    "lvef": "left ventricular ejection fraction",
    "dvt": "deep vein thrombosis",
    "pe": "pulmonary embolism",
    "svt": "supraventricular tachycardia",
    "vt": "ventricular tachycardia",
    "vfib": "ventricular fibrillation",
    # Blood pressure / Metabolic
    "htn": "hypertension",
    "dm": "diabetes mellitus",
    "dm2": "type 2 diabetes",
    "t2dm": "type 2 diabetes",
    "t1dm": "type 1 diabetes",
    "iddm": "insulin-dependent diabetes mellitus",
    "niddm": "non-insulin-dependent diabetes mellitus",
    "hba1c": "hemoglobin A1c (a measure of average blood sugar)",
    "bmi": "body mass index",
    "hyperlipidemia": "high cholesterol",
    "dyslipidemia": "abnormal cholesterol levels",
    "ldl": "low-density lipoprotein (bad cholesterol)",
    "hdl": "high-density lipoprotein (good cholesterol)",
    # Kidney
    "aki": "acute kidney injury",
    "ckd": "chronic kidney disease",
    "esrd": "end-stage renal disease",
    "egfr": "estimated glomerular filtration rate (a measure of kidney function)",
    "cr": "creatinine (a kidney function marker)",
    # Lungs / Breathing
    "copd": "chronic obstructive pulmonary disease",
    "sob": "shortness of breath",
    "doe": "shortness of breath with exertion",
    "pna": "pneumonia",
    "uri": "upper respiratory infection",
    "osa": "obstructive sleep apnea",
    "cpap": "continuous positive airway pressure (a breathing machine used during sleep)",
    "bipap": "bilevel positive airway pressure (a breathing support machine)",
    # Neurology
    "tia": "transient ischemic attack (mini-stroke)",
    "cva": "stroke",
    "ms": "multiple sclerosis",
    "sz": "seizure",
    # GI
    "gerd": "gastroesophageal reflux disease (acid reflux)",
    "ibs": "irritable bowel syndrome",
    "ibd": "inflammatory bowel disease",
    "uc": "ulcerative colitis",
    "gi": "gastrointestinal",
    # Infection / Immune
    "uti": "urinary tract infection",
    "bac": "bacteremia (bacteria in the blood)",
    "sepsis": "severe infection spreading through the blood",
    "hiv": "human immunodeficiency virus",
    "tb": "tuberculosis",
    # General / Vitals
    "hr": "heart rate",
    "bp": "blood pressure",
    "rr": "respiratory rate",
    "temp": "temperature",
    "o2sat": "oxygen saturation",
    "spo2": "blood oxygen level",
    "wbc": "white blood cell count",
    "hgb": "hemoglobin",
    "plt": "platelets",
    "bun": "blood urea nitrogen (kidney marker)",
    "na": "sodium",
    "k": "potassium",
    "hpi": "history of present illness",
    "pmh": "past medical history",
    "prn": "as needed",
    "po": "by mouth (oral)",
    "iv": "intravenous",
    "bid": "twice daily",
    "tid": "three times daily",
    "qid": "four times daily",
    "qd": "once daily",
    "qhs": "at bedtime",
    "npo": "nothing by mouth",
    "dc": "discharge",
    "f/u": "follow-up",
    "w/u": "workup",
    "r/o": "rule out",
    "s/p": "status post (after a procedure or event)",
    "h/o": "history of",
    "c/o": "complaining of",
    "er": "emergency room",
    "ed": "emergency department",
    "icu": "intensive care unit",
    "ccu": "cardiac care unit",
    "loa": "level of alertness",
    "aox3": "alert and oriented to person, place, and time",
    "wdwn": "well-developed, well-nourished",
    "nak": "no abnormality known",
}

SECTION_PATTERNS = {
    "history": [
        r"history of present illness[:\s]",
        r"\bhpi[:\s]",
        r"hospital course[:\s]",
    ],
    "diagnosis": [
        r"discharge diagnosis(?:es)?[:\s]",
        r"diagnosis(?:es)?[:\s]",
        r"assessment(?: and plan)?[:\s]",
    ],
    "medications": [
        r"discharge medications?[:\s]",
        r"medications? on discharge[:\s]",
        r"medications?[:\s]",
    ],
    "follow_up": [
        r"follow[- ]?up(?: instructions)?[:\s]",
        r"follow[- ]?up appointments?[:\s]",
    ],
    "warning_signs": [
        r"return precautions?[:\s]",
        r"warning signs?[:\s]",
        r"when to call(?: your doctor)?[:\s]",
    ],
}

MED_PATTERN = re.compile(
    r"(?P<drug>[A-Z][a-zA-Z0-9\-]+(?: [A-Z]?[a-zA-Z0-9\-]+)?)"
    r"(?:\s+)(?P<dose>\d+(?:\.\d+)?\s?(?:mg|mcg|g|units|mL))?"
    r"(?:.*?)(?P<freq>daily|twice daily|once daily|every \d+ hours|as needed|bid|tid|qid)?",
    re.IGNORECASE,
)

@dataclass
class ProcessedNote:
    raw_text: str
    cleaned_text: str
    sections: Dict[str, str]
    medications: List[Dict[str, str]]
    normalized_terms: List[str]

def clean_text(text: str) -> str:
    text = re.sub(r"_{2,}", " ", text)
    text = re.sub(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", " ", text)
    # Preserve newlines (needed for section parsing) — only collapse horizontal whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def normalize_abbreviations(text: str) -> Tuple[str, List[str]]:
    normalized = []
    out = text
    for k, v in COMMON_ABBREVIATIONS.items():
        pattern = re.compile(rf"\b{re.escape(k)}\b", re.IGNORECASE)
        if pattern.search(out):
            out = pattern.sub(v, out)
            normalized.append(v)
    return out, sorted(set(normalized))

def segment_sections(text: str) -> Dict[str, str]:
    lower = text.lower()
    matches = []
    for section, patterns in SECTION_PATTERNS.items():
        for p in patterns:
            m = re.search(p, lower, flags=re.IGNORECASE)
            if m:
                matches.append((m.start(), section, m.group(0)))
                break
    if not matches:
        return {"general": text}

    matches.sort(key=lambda x: x[0])
    sections: Dict[str, str] = {}
    for i, (start, section, header_text) in enumerate(matches):
        # Skip past the matched header so section content is clean
        content_start = start + len(header_text)
        end = matches[i + 1][0] if i + 1 < len(matches) else len(text)
        chunk = text[content_start:end].strip()
        if chunk:
            sections[section] = chunk
    return sections

def extract_medications(text: str) -> List[Dict[str, str]]:
    meds = []
    for match in MED_PATTERN.finditer(text):
        drug = (match.group("drug") or "").strip()
        if not drug or len(drug) < 3:
            continue
        meds.append({
            "drug": drug,
            "dose": (match.group("dose") or "").strip(),
            "frequency": (match.group("freq") or "").strip(),
        })
    dedup = []
    seen = set()
    for m in meds:
        key = tuple(m.items())
        if key not in seen:
            dedup.append(m)
            seen.add(key)
    return dedup[:25]

def normalize_entities_simple(text: str) -> List[str]:
    # Lightweight hook. Replace with UMLS/SNOMED linker (scispaCy) for production.
    known_conditions = [
        "heart failure", "heart failure with reduced ejection fraction",
        "heart failure with preserved ejection fraction", "congestive heart failure",
        "hypertension", "high blood pressure",
        "type 2 diabetes", "type 1 diabetes", "diabetes mellitus",
        "atrial fibrillation", "arrhythmia",
        "acute kidney injury", "chronic kidney disease", "end-stage renal disease",
        "pneumonia", "upper respiratory infection",
        "chronic obstructive pulmonary disease", "asthma",
        "coronary artery disease", "myocardial infarction", "heart attack",
        "stroke", "transient ischemic attack",
        "deep vein thrombosis", "pulmonary embolism",
        "obstructive sleep apnea",
        "gastroesophageal reflux disease", "acid reflux",
        "urinary tract infection",
        "sepsis", "bacteremia",
        "high cholesterol", "high triglycerides",
        "anemia", "hypothyroidism", "hyperthyroidism",
        "osteoporosis", "arthritis", "gout",
        "depression", "anxiety", "bipolar disorder",
        "seizure", "epilepsy",
        "multiple sclerosis", "parkinson disease",
        "obesity",
    ]
    entities = set()
    for term in known_conditions:
        if re.search(rf"\b{re.escape(term)}\b", text, flags=re.IGNORECASE):
            entities.add(term)
    return sorted(entities)

def preprocess_note(text: str) -> ProcessedNote:
    cleaned = clean_text(text)
    expanded, normalized_abbrevs = normalize_abbreviations(cleaned)
    sections = segment_sections(expanded)
    meds = extract_medications(sections.get("medications", expanded))
    entities = sorted(set(normalized_abbrevs + normalize_entities_simple(expanded)))
    return ProcessedNote(
        raw_text=text,
        cleaned_text=expanded,
        sections=sections,
        medications=meds,
        normalized_terms=entities,
    )
# ── Question Classifier ────────────────────────────────────────────────────────

INTENT_PATTERNS = {
    "medication": [
        r"\b(medication|medicine|drug|pill|dose|dosage|prescription|take|taking|refill|pharmacy)\b",
        r"\b(mg|mcg|tablet|capsule|injection|insulin|inhaler)\b",
        r"\b(side effect|interaction|allergy|allergic)\b",
    ],
    "follow_up": [
        r"\b(appointment|follow.?up|follow up|visit|clinic|doctor|schedule|when do i|next step)\b",
        r"\b(primary care|cardiolog|specialist|referral|outpatient)\b",
    ],
    "warning_sign": [
        r"\b(emergency|er|911|urgent|warning|danger|serious|severe|worsen|worse)\b",
        r"\b(chest pain|shortness of breath|difficulty breathing|fainting|confusion|dizziness)\b",
        r"\b(when should i|when to call|should i go|go to the hospital)\b",
    ],
    "diagnosis": [
        r"\b(diagnosis|condition|disease|disorder|what is|what does|mean|explain|understand)\b",
        r"\b(heart failure|diabetes|hypertension|copd|stroke|cancer|infection|pneumonia)\b",
    ],
}

def classify_intent(text: str) -> dict:
    """
    Classify the intent of a discharge note or patient question.
    Returns the top intent label and confidence scores for all categories.
    
    This replaces the old regex section routing with a scored classifier
    that enables the agentic router to make smarter retrieval decisions.
    """
    text_lower = text.lower()
    scores = {}

    for intent, patterns in INTENT_PATTERNS.items():
        score = 0
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            score += len(matches)
        scores[intent] = score

    # If nothing matched, default to general
    top_intent = max(scores, key=scores.get)
    if scores[top_intent] == 0:
        top_intent = "general"

    return {
        "top_intent": top_intent,
        "scores": scores,
        "is_ambiguous": top_intent != "general" and list(scores.values()).count(scores[top_intent]) > 1,
    }


# ── Readmission Risk Scorer ────────────────────────────────────────────────────

RISK_SIGNALS = {
    "high": [
        r"\b(heart failure|hfref|hfpef|chf)\b",
        r"\b(copd|chronic obstructive)\b",
        r"\b(renal failure|kidney failure|esrd|dialysis)\b",
        r"\b(sepsis|septic)\b",
        r"\b(cancer|oncolog|chemotherapy)\b",
        r"\b(stroke|cva|tia)\b",
    ],
    "medium": [
        r"\b(diabetes|diabetic|dm2|t2dm)\b",
        r"\b(hypertension|htn|high blood pressure)\b",
        r"\b(atrial fibrillation|afib|arrhythmia)\b",
        r"\b(pneumonia|infection|cellulitis)\b",
        r"\b(surgery|procedure|operation|post.?op)\b",
    ],
    "low": [
        r"\b(follow.?up|follow up|appointment)\b",
        r"\b(stable|improving|resolved|recovered)\b",
    ],
}

def score_readmission_risk(text: str) -> dict:
    """
    Predict 30-day readmission risk based on clinical signals
    in the discharge note. Returns Low / Medium / High with reasoning.
    
    This is the Prediction component for Topic 2 (Clinical Decision Making).
    Based on research showing certain comorbidities strongly predict
    30-day readmission (Jencks et al., 2009 — 19.6% Medicare readmission rate).
    """
    text_lower = text.lower()
    matched = {"high": [], "medium": [], "low": []}

    for level, patterns in RISK_SIGNALS.items():
        for pattern in patterns:
            hits = re.findall(pattern, text_lower)
            if hits:
                matched[level].extend(hits)

    high_count = len(matched["high"])
    medium_count = len(matched["medium"])

    if high_count >= 1:
        risk_level = "HIGH"
        explanation = f"High-risk conditions detected: {', '.join(set(matched['high']))}"
    elif medium_count >= 2:
        risk_level = "MEDIUM"
        explanation = f"Multiple moderate-risk factors: {', '.join(set(matched['medium']))}"
    elif medium_count == 1:
        risk_level = "MEDIUM"
        explanation = f"Moderate-risk factor present: {', '.join(set(matched['medium']))}"
    else:
        risk_level = "LOW"
        explanation = "No major readmission risk factors detected."

    return {
        "risk_level": risk_level,
        "explanation": explanation,
        "signals": matched,
        "recommendation": {
            "HIGH": "Prioritise early follow-up within 7 days. Consider care coordination referral.",
            "MEDIUM": "Schedule follow-up within 14 days. Monitor symptoms closely.",
            "LOW": "Standard follow-up within 30 days is appropriate.",
        }[risk_level],
    }

# ── Vital Signs Anomaly Detector ──────────────────────────────────────────────

import statistics

def detect_vitals_anomaly(readings: dict) -> dict:
    """
    Time-series anomaly detection for post-discharge vital signs.
    
    Takes 7 days of weight and blood pressure readings and detects
    anomalies using z-score statistical analysis.
    
    This is the Time-Series Anomaly Detection + Pattern Recognition
    component for Topic 2 (Clinical Decision Making).
    
    Args:
        readings: {
            "weight_kg": [list of daily weights],
            "systolic_bp": [list of daily systolic BP],
            "diastolic_bp": [list of daily diastolic BP]  (optional)
        }
    """
    results = {}
    alerts = []
    pattern = "stable"

    # ── Weight Analysis ───────────────────────────────────────────
    weights = readings.get("weight_kg", [])
    if len(weights) >= 3:
        mean_w = statistics.mean(weights)
        stdev_w = statistics.stdev(weights) if len(weights) > 1 else 0
        daily_changes = [weights[i] - weights[i-1] for i in range(1, len(weights))]
        max_single_day = max(daily_changes) if daily_changes else 0
        total_change = weights[-1] - weights[0]

        weight_alerts = []
        if max_single_day >= 2.0:
            weight_alerts.append(f"Single-day gain of {max_single_day:.1f} kg detected (threshold: 2.0 kg)")
            pattern = "critical"
        elif max_single_day >= 1.0:
            weight_alerts.append(f"Single-day gain of {max_single_day:.1f} kg detected (threshold: 1.0 kg)")
            if pattern == "stable":
                pattern = "warning"

        if total_change >= 2.5:
            weight_alerts.append(f"Total weight gain of {total_change:.1f} kg over {len(weights)} days")
            pattern = "critical"
        elif total_change >= 1.5:
            weight_alerts.append(f"Gradual weight gain of {total_change:.1f} kg over {len(weights)} days")
            if pattern == "stable":
                pattern = "warning"

        # Z-score anomaly detection
        if stdev_w > 0:
            zscores = [(w - mean_w) / stdev_w for w in weights]
            anomaly_days = [i+1 for i, z in enumerate(zscores) if abs(z) > 2.0]
            if anomaly_days:
                weight_alerts.append(f"Statistical anomaly detected on day(s): {anomaly_days}")

        results["weight"] = {
            "readings": weights,
            "mean": round(mean_w, 1),
            "total_change": round(total_change, 1),
            "max_single_day_change": round(max_single_day, 1),
            "alerts": weight_alerts,
        }
        alerts.extend(weight_alerts)

    # ── Blood Pressure Analysis ───────────────────────────────────
    systolic = readings.get("systolic_bp", [])
    if len(systolic) >= 3:
        mean_s = statistics.mean(systolic)
        stdev_s = statistics.stdev(systolic) if len(systolic) > 1 else 0
        bp_alerts = []

        # Check for hypertensive readings
        high_days = [i+1 for i, v in enumerate(systolic) if v >= 180]
        warning_days = [i+1 for i, v in enumerate(systolic) if 140 <= v < 180]

        if high_days:
            bp_alerts.append(f"Hypertensive crisis (>=180 mmHg) on day(s): {high_days}")
            pattern = "critical"
        if warning_days:
            bp_alerts.append(f"Elevated BP (140-179 mmHg) on day(s): {warning_days}")
            if pattern == "stable":
                pattern = "warning"

        # Trend detection
        if len(systolic) >= 3:
            recent_trend = systolic[-1] - systolic[0]
            if recent_trend >= 20:
                bp_alerts.append(f"Rising BP trend: +{recent_trend} mmHg over {len(systolic)} days")
                if pattern == "stable":
                    pattern = "warning"

        # Z-score
        if stdev_s > 0:
            zscores = [(v - mean_s) / stdev_s for v in systolic]
            anomaly_days = [i+1 for i, z in enumerate(zscores) if abs(z) > 2.0]
            if anomaly_days:
                bp_alerts.append(f"BP anomaly on day(s): {anomaly_days}")

        results["blood_pressure"] = {
            "readings": systolic,
            "mean": round(mean_s, 1),
            "alerts": bp_alerts,
        }
        alerts.extend(bp_alerts)

    # ── Pattern Classification + Recommendation ───────────────────
    recommendations = {
        "critical": "URGENT: Contact your doctor or go to the ER today. These readings suggest your condition may be worsening rapidly.",
        "warning": "CAUTION: Contact your doctor within 24 hours. Your readings show early warning signs that need attention.",
        "stable": "Your readings look stable. Continue monitoring daily and attend your scheduled follow-up appointment.",
    }

    return {
        "pattern": pattern,
        "alerts": alerts,
        "results": results,
        "recommendation": recommendations[pattern],
        "days_monitored": max(len(weights), len(systolic)),
        "summary": f"Pattern: {pattern.upper()} — {len(alerts)} alert(s) detected over {max(len(weights), len(systolic))} days of monitoring.",
    }