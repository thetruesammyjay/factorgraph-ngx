from pathlib import Path
from app.data.ingestion import list_source_files

def main():
    raw = Path("../../data/raw")
    files = list_source_files(raw)
    print(f"Found {len(files)} raw CSV file(s) in {raw.resolve()}")
    for path in files: print(f" - {path.name}")

if __name__ == "__main__": main()