from pathlib import Path
import pandas as pd

def read_csv(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path)

def list_source_files(directory: str | Path) -> list[Path]:
    return sorted(Path(directory).glob("*.csv"))