import csv
import os
import time

from app.dependencies.connection import get_db_connection
from app.repositories.ages_repository import AgesRepository
from app.repositories.causes_repository import CausesRepository
from app.repositories.measures_repository import MeasuresRepository
from app.repositories.regions_repository import RegionsRepository
from app.repositories.sexes_repository import SexesRepository

# from app.repositories.deaths_repository import DeathsRepository

DATA_DIR = os.getenv("DATA_DIR")


def load_sexes(db):
    sexes_repo = SexesRepository(db)
    with open(f"{DATA_DIR}/dödsorsaker - meta - kön.csv", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file, delimiter=";")
        for row in reader:
            sexes_repo.insert_one(sex_code=row["Kön"], sex_text=row["Text"])


def load_regions(db):
    regions_repo = RegionsRepository(db)
    with open(f"{DATA_DIR}/dödsorsaker - meta - regioner.csv", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file, delimiter=";")
        for row in reader:
            regions_repo.insert_one(region_code=row["Region"], region_text=row["Text"])


def load_ages(db):
    ages_repo = AgesRepository(db)
    with open(f"{DATA_DIR}/dödsorsaker - meta - åldrar.csv", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file, delimiter=";")
        for row in reader:
            ages_repo.insert_one(age_code=row["Ålder"], age_text=row["Text"])


def load_measures(db):
    measures_repo = MeasuresRepository(db)
    with open(f"{DATA_DIR}/dödsorsaker - meta - mått.csv", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file, delimiter=";")
        for row in reader:
            measures_repo.insert_one(measure_code=row["Mått"], measure_text=row["Text"])


def load_causes(db):
    causes_repo = CausesRepository(db)
    with open(f"{DATA_DIR}/dödsorsaker - meta - diagnoser.csv", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file, delimiter=";")
        for row in reader:
            causes_repo.insert_one(diagnosis_code=row["Diagnos"], diagnosis_text=row["Text"])


def load_file(path, measure_code, from_year, to_year, manual_max_rows, batch_size, db):
    print(f"Loading {os.path.basename(path)} (years {from_year}-{to_year})...")

    with open(path, encoding="utf-8-sig") as file:
        total_rows = sum(1 for _ in file) - 1  # Räkna totala rader i filen (minus header)

    if manual_max_rows is None:
        max_rows = total_rows
    else:
        max_rows = manual_max_rows

    # total_batches_estimate = (max_rows // batch_size) + (1 if max_rows % batch_size > 0 else 0)

    start = time.perf_counter()
    eta_start = start

    # Establish a COPY buffer to be able to read BIG files.
    # buffer = io.StringIO()
    cursor = db.cursor()

    checked_rows = 0
    loaded_rows = 0
    batches_done = 0
    batch_data = []

    with open(path, encoding="utf-8-sig") as file:
        reader = csv.DictReader(file, delimiter=";")

        for row in reader:
            checked_rows += 1

            year = int(row["År"])
            if not (from_year <= year <= to_year):
                continue

            # if checked_rows >= max_rows:
            #   break

            value_raw = row["Värde"]
            if value_raw in ("", ".."):
                continue

            loaded_rows += 1

            if manual_max_rows and loaded_rows > max_rows:
                break

            batch_data.append(
                (
                    int(row["År"]),
                    int(row["Region"]),
                    int(row["Kön"]),
                    int(row["Ålder"]),
                    row["Diagnos"],
                    measure_code,
                    float(value_raw.replace(",", ".")),
                )
            )

            if len(batch_data) >= batch_size:
                cursor.executemany(
                    """
          INSERT INTO deaths (year, region_code, sex_code, age_code, diagnosis_code, measure_code, value)
          VALUES (%s, %s, %s, %s, %s, %s, %s)
          """,
                    batch_data,
                )
                db.commit()  # Commit after each batch
                batch_data = []  # Clear batch data for next batch

                batches_done += 1

                progress = checked_rows / total_rows
                bar_length = 30
                filled = int(progress * bar_length)
                bar = f"\033[92m{'#' * filled}\033[91m{'-' * (bar_length - filled)}\033[0m"

                elapsed = time.perf_counter() - eta_start
                eta = (elapsed / progress - elapsed) if progress > 0 else 0

                print(
                    f"\r[{bar}] {progress * 100:5.1f}% "
                    f"Estimated time remaining: {eta:5.1f} seconds "
                    f" | Loaded: {loaded_rows:,} | Checked: {checked_rows}/{total_rows}",
                    end="",
                )

        # Insert any remaining data after the loop
        if batch_data:
            cursor.executemany(
                """
        INSERT INTO deaths (year, region_code, sex_code, age_code, diagnosis_code, measure_code, value)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
                batch_data,
            )
            db.commit()

        end = time.perf_counter()
        print(f"\nFinished {os.path.basename(path)} in {end - start:.2f} seconds")
        print(f"Total checked: {checked_rows:,} | Loaded: {loaded_rows:,}")


def load_deaths_sample(db, manual_max_rows=None, batch_size=2500, from_year=1997, to_year=2024):
    load_file(
        f"{DATA_DIR}/dödsorsaker - data - antal döda - 1997-2024.csv",
        measure_code=1,
        from_year=from_year,
        to_year=to_year,
        manual_max_rows=manual_max_rows,
        batch_size=batch_size,
        db=db,
    )

    load_file(
        f"{DATA_DIR}/dödsorsaker - data - antal döda per 100 000 - 1997-2024.csv",
        measure_code=2,
        from_year=from_year,
        to_year=to_year,
        manual_max_rows=manual_max_rows,
        batch_size=batch_size,
        db=db,
    )


def main():
    db_connection = get_db_connection()
    load_sexes(db_connection)
    load_regions(db_connection)
    load_ages(db_connection)
    load_measures(db_connection)
    load_causes(db_connection)

    load_mode = os.getenv("DATA_LOAD_MODE", "").lower()

    if load_mode == "full":
        print("Starting FULL load of death records (1997-2024).")
        load_deaths_sample(db_connection)
    elif load_mode == "sample":
        print(
            "Starting SAMPLE load of death records (2022-2024). Set FULL_DATA_LOAD=true to load all years."
        )
        load_deaths_sample(db_connection, from_year=2022, to_year=2024)
    else:
        print("Starting QUICK load (Only: 1997, 10k rows).")
        load_deaths_sample(db_connection, manual_max_rows=10000, from_year=1997, to_year=1997)


if (
    __name__ == "__main__"
):  # Om denna fil körs direkt, så kommer main() att köras. Om den importeras som en modul, så kommer main() inte att köras automatiskt.
    main()
