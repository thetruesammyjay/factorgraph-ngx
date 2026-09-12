"""Import price observations after running the data audit."""
from pathlib import Path
from app.data.ingestion import list_source_files

def main(): print(f"Experiment import scaffold ready for {len(list_source_files(Path('../../data/raw')))} file(s).")
if __name__ == "__main__": main()