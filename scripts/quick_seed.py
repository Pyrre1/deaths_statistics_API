"""
Quick seed script - loads minimal data for fast testing.
Loads ~10k rows from 2024 only.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.dependencies.connection import get_db_connection
from etl.load_data import load_ages, load_causes, load_file, load_measures, load_regions, load_sexes

DATA_DIR: str = os.getenv("DATA_DIR", "./data")

def main():
  print("Quick seed - Loading minimal data (2024 only, ~10k rows)...")

  db = get_db_connection()

  # Load metadata
  print("Loading metadata tables...")
  load_sexes(db)
  load_regions(db)
  load_ages(db)
  load_measures(db)
  load_causes(db)

  # Load minimal deaths data
  print("Loading minimal deaths data (2024 only, 10k rows per measure)...")
  load_file(
    f"{DATA_DIR}/dödsorsaker - data - antal döda - 1997-2024.csv",
      measure_code=1,
      from_year=2024,
      to_year=2024,
      manual_max_rows=10000,  # Only first 10k rows
      batch_size=2500,
      db=db
  )
  load_file(
    f"{DATA_DIR}/dödsorsaker - data - antal döda per 100 000 - 1997-2024.csv",
      measure_code=2,
      from_year=2024,
      to_year=2024,
      manual_max_rows=10000,  # Only first 10k rows
      batch_size=2500,
      db=db
  )

  print("Quick seed complete!")

if __name__ == "__main__":
    main()
