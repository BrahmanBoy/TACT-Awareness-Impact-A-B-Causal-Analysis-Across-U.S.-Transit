from pathlib import Path
import pandas as pd
from .logging import get_logger

logger = get_logger(__name__)

def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

def read_excel_any(path_candidates) -> pd.ExcelFile:
    for p in path_candidates:
        if Path(p).exists():
            logger.info(f"Reading Excel: {p}")
            return pd.ExcelFile(p)
    raise FileNotFoundError(f"No Excel found in: {path_candidates}")

def write_csv(df: pd.DataFrame, path: Path) -> None:
    ensure_parent(path)
    df.to_csv(path, index=False)
    logger.info(f"Wrote: {path}  (rows={len(df)})")
