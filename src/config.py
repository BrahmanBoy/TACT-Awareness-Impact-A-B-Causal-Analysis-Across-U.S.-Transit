from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"

RAW_XLSX_CANDIDATES = [
    DATA_RAW / "awareness_survey.xlsx",
    DATA_RAW / "FTA Human Trafficking Before and After Tables 1.10.2025.xlsx",
]
TIDY_CSV = DATA_PROCESSED / "tidy_awareness.csv"

REGIONS = ["Albany", "Alexandria", "Austin", "Chicago", "Portland", "Santa Fe"]

DEFAULT_QUESTION_KEYWORDS = ["hotline", "indicator", "signs", "report", "awareness"]
