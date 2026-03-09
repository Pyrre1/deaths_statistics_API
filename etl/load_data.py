import csv
import os
import time
import io

from app.dependencies.connection import get_db_connection
from app.repositories.sexes_repository import SexesRepository
from app.repositories.regions_repository import RegionsRepository
from app.repositories.ages_repository import AgesRepository
from app.repositories.measures_repository import MeasuresRepository
from app.repositories.causes_repository import CausesRepository
# from app.repositories.deaths_repository import DeathsRepository

DATA_DIR = os.getenv("DATA_DIR")

def load_sexes(db):
  sexes_repo = SexesRepository(db)
  with open(f"{DATA_DIR}/dödsorsaker - meta - kön.csv", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file, delimiter=";")
    for row in reader:
      sexes_repo.insert_one(
        sex_code=row['Kön'],
        sex_text=row['Text']
      )

def load_regions(db):
  regions_repo = RegionsRepository(db)
  with open(f"{DATA_DIR}/dödsorsaker - meta - regioner.csv", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file, delimiter=";")
    for row in reader:
      regions_repo.insert_one(
        region_code=row['Region'],
        region_text=row['Text']
      )

def load_ages(db):
  ages_repo = AgesRepository(db)
  with open(f"{DATA_DIR}/dödsorsaker - meta - åldrar.csv", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file, delimiter=";")
    for row in reader:
      ages_repo.insert_one(
        age_code=row['Ålder'],
        age_text=row['Text']
      )

def load_measures(db):
  measures_repo = MeasuresRepository(db)
  with open(f"{DATA_DIR}/dödsorsaker - meta - mått.csv", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file, delimiter=";")
    for row in reader:
      measures_repo.insert_one(
        measure_code=row['Mått'],
        measure_text=row['Text']
      )

def load_causes(db):
  causes_repo = CausesRepository(db)
  with open(f"{DATA_DIR}/dödsorsaker - meta - diagnoser.csv", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file, delimiter=";")
    for row in reader:
      causes_repo.insert_one(
        diagnosis_code=row['Diagnos'],
        diagnosis_text=row['Text']
      )

def load_file(path, measure_code, from_year, to_year, manual_max_rows, batch_size, db):
  print(f"Loading {os.path.basename(path)}...")

  with open(path, encoding="utf-8-sig") as file:
    total_rows = sum(1 for _ in file) - 1 # Räkna totala rader i filen (minus header)

  if manual_max_rows is None:
    max_rows = total_rows
  else:
    max_rows = manual_max_rows

  total_batches_estimate = (max_rows // batch_size) + (1 if max_rows % batch_size > 0 else 0)

  start = time.perf_counter()
  eta_start = None

  # Establish a COPY buffer to be able to read BIG files.
  buffer = io.StringIO()
  cursor = db.cursor()

  checked_rows = 0
  batches_done = 0

  with open(path, encoding="utf-8-sig") as file:
    reader = csv.DictReader(file, delimiter=";")

    for row in reader:
      checked_rows += 1

      if checked_rows >= max_rows:
        break
      
      year = int(row["År"])
      if not (from_year <= year <= to_year):
        continue

      value_raw = row['Värde']
      if value_raw in ('', '..'):
        continue

      buffer.write(
        f"{row['År']},"
        f"{row['Region']},"
        f"{row['Kön']},"
        f"{row['Ålder']},"
        f"{row['Diagnos']},"
        f"{measure_code},"
        f"{value_raw.replace(',', '.')}\n"
      )

      if buffer.tell() >= batch_size * 100: # Approximate size in bytes for batch_size rows (assuming ~100 bytes per row)
        buffer.seek(0)
        cursor.copy("COPY deaths FROM STDIN WITH CSV", buffer)
        buffer = io.StringIO() # Reset buffer for next batch

        batches_done += 1

        progress = checked_rows / max_rows
        bar_length = 30
        filled = int(progress * bar_length)
        bar = f"\033[92m{'#' * filled}\033[91m{'-' * (bar_length - filled)}\033[0m"

        elapsed = time.perf_counter() - eta_start if eta_start else 0
        eta = (elapsed / progress - elapsed ) if progress > 0 else 0

        print(
          f"\r[{bar}] {progress*100:5.1f}% "
          f"Estimated time remaining: {eta:5.1f} seconds "
          f"Checked: {checked_rows}/{max_rows}",
          end=''
        )

    if buffer.tell() > 0: # Load any remaining data in the buffer
      buffer.seek(0)
      cursor.copy("COPY deaths FROM STDIN WITH CSV", buffer)

    db.commit() # Commit all changes after loading the file

    end = time.perf_counter()
    print(f"\nFinished {os.path.basename(path)} in {end - start:.2f} seconds")


def load_deaths_sample(db, manual_max_rows=None, batch_size=2500): # test med första 10000 raderna, batch_size bestämmer hur många rader som ska laddas in i databasen i varje batch
    from_year = 1997
    to_year = 2024

    load_file(f"{DATA_DIR}/dödsorsaker - data - antal döda - 1997-2024.csv", 
        measure_code=1, 
        from_year=from_year, 
        to_year=to_year,
        manual_max_rows=manual_max_rows,
        batch_size=batch_size,
        db=db
    )

    load_file(f"{DATA_DIR}/dödsorsaker - data - antal döda per 100 000 - 1997-2024.csv", 
        measure_code=2,
        from_year=from_year,
        to_year=to_year,
        manual_max_rows=manual_max_rows,
        batch_size=batch_size,
        db=db
    )


def main():
    db_connection = get_db_connection()
    load_sexes(db_connection)
    load_regions(db_connection)
    load_ages(db_connection)
    load_measures(db_connection)
    load_causes(db_connection)
    load_deaths_sample(db_connection)

if __name__ == "__main__": # Om denna fil körs direkt, så kommer main() att köras. Om den importeras som en modul, så kommer main() inte att köras automatiskt.
    main()