import csv
import os

from app.dependencies.connection import get_db_connection
from app.repositories.sexes_repository import SexesRepository
from app.repositories.regions_repository import RegionsRepository
from app.repositories.ages_repository import AgesRepository
from app.repositories.measures_repository import MeasuresRepository
from app.repositories.causes_repository import CausesRepository
from app.repositories.deaths_repository import DeathsRepository

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

def load_deaths_sample(db, max_rows=10000, batch_size=1000): # test med första 10000 raderna, batch_size bestämmer hur många rader som ska laddas in i databasen i varje batch
  deaths_repo_sample = DeathsRepository(db)
  print("Datasets loaded") # TODO: Ta bort detta, endast för felsökn-ing 
  def load_file(path, measure_code):
    batch = []
    counter = 0

    with open(path, encoding="utf-8-sig") as file:
      reader = csv.DictReader(file, delimiter=";")

      for row in reader:
        year = int(row["År"])

        if counter >= max_rows:
          break

        if not (2024 <= year <=2024):
          continue

        value_raw = row['Värde']
        if value_raw in ('', '..'):
          continue

        batch.append((
          int(row['År']),
          row['Region'],
          int(row['Kön']),
          row['Ålder'],
          row['Diagnos'],
          measure_code,
          float(value_raw.replace(',', '.')) # Convert comma to dot for decimal values
        ))

        if len(batch) >= batch_size:
          for row_values in batch:
            deaths_repo_sample.insert_one(*row_values)
          batch = []

        counter += 1

    if batch:
      for row_values in batch: # Row_values motsvarar "year, region_code, sex_code, age_code, diagnosis_code, measure_code, value"
        deaths_repo_sample.insert_one(*row_values)

  load_file(f"{DATA_DIR}/dödsorsaker - data - antal döda - 1997-2024.csv", measure_code=1)
  load_file(f"{DATA_DIR}/dödsorsaker - data - antal döda per 100 000 - 1997-2024.csv", measure_code=2)

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