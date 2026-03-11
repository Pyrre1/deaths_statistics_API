from app.repositories.base_repository import BaseRepository

class DeathsRepository(BaseRepository):
    ALLOWED_ORDER_COLUMNS = {
      'id',
      'year',
      'region_code',
      'sex_code',
      'age_code',
      'diagnosis_code',
      'measure_code',
      'value'
    }

    def insert_one(
      self,
      year,
      region_code,
      sex_code,
      age_code,
      diagnosis_code,
      measure_code,
      value
    ):
      self.execute(
        """
        INSERT INTO deaths (
          year,
          region_code,
          sex_code,
          age_code,
          diagnosis_code,
          measure_code,
          value
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
          year,
          region_code,
          sex_code,
          age_code,
          diagnosis_code,
          measure_code,
          value
        )
      )

    def get_by_id(self, death_id):
      return self.fetch_one(
        "SELECT * FROM deaths WHERE id = %s;",
        (death_id,)
      )

    def get_all(self, limit=100, offset=0):
      rows = self.fetch_all(
        "SELECT * FROM deaths ORDER BY id LIMIT %s OFFSET %s;",
        (limit, offset)
      )

      total = self.fetch_one(
        "SELECT COUNT(*) AS total FROM deaths"
        )["total"]

      return {
        "total": total,
        "items": rows
      }
    
    def find(
      self,
      year=None,
      region_code=None,
      sex_code=None,
      age_code=None,
      diagnosis_code=None,
      measure_code=None,
      limit=100,
      offset=0,
      order_by='year',
      direction='asc'
    ):

      if order_by not in self.ALLOWED_ORDER_COLUMNS:
        raise ValueError(f"Invalid order_by column: {order_by}")

      if direction.lower() not in ['asc', 'desc']:
        raise ValueError(f"Invalid direction: {direction}")

      filters = []
      params = []

      if year is not None:
        filters.append("year = %s")
        params.append(year)

      if region_code is not None:
        filters.append("region_code = %s")
        params.append(region_code)

      if sex_code is not None:
        filters.append("sex_code = %s")
        params.append(sex_code)

      if age_code is not None:
        filters.append("age_code = %s")
        params.append(age_code)

      if diagnosis_code is not None:
        filters.append("diagnosis_code = %s")
        params.append(diagnosis_code)

      if measure_code is not None:
        filters.append("measure_code = %s")
        params.append(measure_code)

      where_clause = ""
      if filters:
        where_clause = "WHERE " + " AND ".join(filters)

      query = f"""
        SELECT * FROM deaths
        {where_clause}
        ORDER BY {order_by} {direction}
        LIMIT %s OFFSET %s
      """

      params_with_pagination = params + [limit, offset]

      rows = self.fetch_all(query, params_with_pagination)

      count_query = f"""
        SELECT COUNT(*) AS total FROM deaths
        {where_clause}
      """
      total = self.fetch_one(count_query, params)["total"]

      return {
        "total": total,
        "items": rows,
        "limit": limit,
        "offset": offset,
        "order_by": order_by,
        "direction": direction
      }

    def count_by_region(self, region_code):
      result = self.fetch_one(
        """
        SELECT COUNT(*) AS total FROM deaths
        WHERE region_code = %s
          AND age_code != 99
        """,
        (region_code,)
      )
      return result["total"]if result else 0

    def average_age_by_region(self, region_code):
      """Calculates the average age_code for region and returns the range text"""
      result = self.fetch_one(
        """
        SELECT AVG(age_code) AS avg_age_code
        FROM deaths
        WHERE region_code = %s
          AND age_code != 99
      """, (region_code,))

      if not result or result["avg_age_code"] is None:
        return "Unknown"

      # Round to nearest integer.
      avg_code = round(result["avg_age_code"])

      # Get the age range text for the average code.
      age_range = self.fetch_one(
        """
        SELECT age_text 
        FROM ages
        WHERE age_code = %s
        """, (avg_code,))

      return age_range["age_text"] if age_range else "Unknown"

    def get_year_range_by_region(self, region_code):
      """Get min and max year for a region"""
      filter_clause = self._build_non_aggregate_filter()

      result = self.fetch_one(
        f"""
        SELECT 
        MIN(year) AS min_year, 
        MAX(year) AS max_year
        FROM deaths
        WHERE region_code = %s
          AND {filter_clause}
        """,
        (region_code,)
      )
      return result if result else {"min_year": None, "max_year": None}