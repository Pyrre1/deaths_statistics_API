# Swedish Death Statistics API

## Objective

A REST API serving Swedish death statistics data from SCB (Statistics Sweden), covering 1997–2024. The API allows users to retrieve and manage death records filtered by region, cause, age, sex, and year. It includes JWT authentication for write operations, automated testing via Postman/Newman in a CI/CD pipeline, and is deployed on LNU Cumulus.

The dataset contains over 7.2 million records across three entities: death records (primary CRUD resource), regions (read-only), and causes of death (read-only).

It is possible to create a new death record and update or delete that one or ones in the set. If the assignment where to continue to improve different roles should probably be added so corruption of dataset is protected by only be able to delete your own creations.

## Implementation Type

REST with a SQL database structure

## Links and Testing

| | URL / File |
|---|---|
| **Production API** | `https://cu1034.camp.lnu.se/api` |
| **API Documentation** | `https://cu1034.camp.lnu.se/api/docs` |
| **Postman Collection** | `postman/Deaths_API.postman_collection.json` |
| **Production Environment** | `postman/production.postman_environment.json` |

**Examiner can verify tests in one of the following ways:**

1. **CI/CD pipeline** — check the pipeline output in GitLab for test results (Build → Pipelines → latest run).
2. **Run manually** — no setup needed:
```bash
   npx newman run postman/Deaths_API.postman_collection.json \
      -e postman/production.postman_environment.json \
      --insecure
```

   Note: `--insecure` is required because the server uses the LNU Campus CA certificate.

## Dataset


| Field | Description |
|---|---|
| **Dataset source** | [ Socialstyrelsen - Datafiler för utvecklare ](https://www.socialstyrelsen.se/statistik-och-data/statistik/for-utvecklare/) - Dödsorsaker 1997–2024 |
| **Volume** | 7 million + records across 28 years |
| **Primary resource (CRUD)** | Deaths (records) — year, region, sex, age group, diagnosis, measure type, value  |
| **Secondary resource 1 (read-only)** | Regions — 21 Swedish counties + national aggregate (Riket) |
| **Secondary resource 2 (read-only)** | Causes — allmost 2,000 ICD-10 diagnosis codes with descriptions |

**Key fields:**
- `measure_code` — 1 = absolute death count, 2 = deaths per 100,000 inhabitants
- `age_code` — 1–20 for age **groups** (0–4, 5–9, ... 95+), 99 = total
- `sex_code` — 1 = men, 2 = women, 3 = both
- `region_code` — 0 = national total, 1–25 = individual counties (2, 11, 15 and 16 is missing)

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.12+

### Local Development
```bash
# 1. Clone the repository
git clone 
cd assignment-api-design

# 2. Configure environment
cp .env.example .env
# Edit .env with your database credentials and JWT secret

# 3. Start containers
docker compose up -d --build

# 4. Seed the database, 3 options read more under **Seed Script** below.
docker compose exec app python -m etl.load_data

# 5. Create admin user, for manual testing. Not needed for test suite
docker compose exec app python -m scripts.seed_admin
```

With `PORT=8000`
API will be available at `http://localhost:8000`
Swagger docs at `http://localhost:8000/docs`

### Seed Script

The seed script supports three loading modes controlled by the `DATA_LOAD_MODE` environment variable:

| Mode | Command | Description | Time estimate |
|------|---------|-------------|---------------|
| Quick (default) | `docker compose exec app python -m etl.load_data` | Loads 1997 only (~10k rows) | ca 2 sec|
| Sample | `DATA_LOAD_MODE=sample docker compose exec app python -m etl.load_data` | Loads 2022–2024 data | ca 6 min |
| Full | `DATA_LOAD_MODE=full docker compose exec app python -m etl.load_data` | Loads all 1997–2024 data | Ca 40 min |

> **Note:** The CSV files are large (~3GB total). Each file takes several seconds to open 
> before loading begins — this is expected. 

> The Quick mode is disproportionately affected 
> since most time is spent opening the file rather than inserting rows.

### Running Tests
```bash
# Install Newman
npm install -g newman

# Run against local
newman run postman/Deaths_API.postman_collection.json \
  -e postman/development.postman_environment.json

# Run against production
newman run postman/Deaths_API.postman_collection.json \
  -e postman/production.postman_environment.json \
  --insecure
```
> Note: `--insecure` needed to test against Cumulus

#### Reset database (wipe all data and re-apply schema if needed)
```bash
docker compose down -v
docker compose up -d --build
```


## API Endpoints

### Authentication
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/token` | Login, get JWT tokens | No |
| POST | `/api/auth/refresh` | Refresh access token | No |
| DELETE | `/api/auth/delete` | Delete the current active user | Yes |

### Deaths (Primary Resource)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/deaths` | List deaths with filtering and pagination | No |
| GET | `/api/deaths/{id}` | Get single death record | No |
| POST | `/api/deaths` | Create death record |  Yes |
| PUT | `/api/deaths/{id}` | Update death record |  Yes |
| DELETE | `/api/deaths/{id}` | Delete death record |  Yes |

### Regions (Read-only)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/regions` | List all 22 regions |
| GET | `/api/regions/{id}` | Region with death statistics |

### Causes (Read-only)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/causes` | List all 1,948 causes (paginated) |
| GET | `/api/causes/{code}` | Cause with death statistics |

### Filtering (Deaths)
```
GET /api/deaths?from_year=2022&to_year=2024&region_code=1&sex_code=1&measure_code=1
```

Available filters: `from_year`, `to_year`, `region_code`, `sex_code`, `age_code`, `diagnosis_code`, `measure_code`, `order_by`, `direction`, `limit`, `offset`

## Design Decisions

### Authentication

JWT authentication using HS256 with short-lived access tokens (30 min) and long-lived refresh tokens (7 days). Refresh tokens are stored as SHA-256 hashes in the database and rotated on every use (one-time use pattern) to prevent replay attacks.

Alternative considered: RS256 with public/private key pair — better for multi-service architectures where multiple services need to verify tokens without sharing a secret. HS256 was chosen as this is a single-service API.

### API Design

**HATEOAS** is implemented on all responses via `_links` objects:
- Collection responses include `self`, `next`, `prev` pagination links
- Single resource responses include `self`, related resource links (`region`, `cause`), and `collection`
- Region and cause responses include a `deaths` link pre-filtered to that resource

**URL structure** follows REST conventions with resource-based URLs. The API is mounted at `/api/` via NGINX reverse proxy.

**Design note on nested resources:** The assignment example shows `GET /movies/{id}/ratings`. This API instead uses filtering (`GET /deaths?region_code=1`) which is more flexible — it allows combining multiple filters simultaneously. Region and cause detail endpoints (`/regions/{id}`, `/causes/{code}`) return pre-computed statistics about related deaths, covering the nested resource use case.

**Measure codes:** The dataset contains two measure types per record — absolute death counts (measure_code=1) and deaths per 100,000 inhabitants (measure_code=2). The `/deaths` endpoint defaults to `measure_code=1` for intuitive results, overridable via query parameter.


### Error Handling

All errors return a consistent structured format:
```json
{
  "category": "not_found",
  "status": 404,
  "code": "NOT_FOUND",
  "message": "Death record not found"
}
```
This is a superset of the `{"error": "message"}` format specified in requirements — it includes machine-readable category and code fields in addition to the human-readable message. FastAPI's default 422 validation errors are overridden to return 400 per requirements.

## Core Technologies Used

*List the technologies you chose and briefly explain why:*
| Technology | Purpose | Why |
|-----------|---------|-----|
| FastAPI | Web framework | Auto-generates OpenAPI docs, excellent performance, type safety |
| PostgreSQL 16 | Database | Relational integrity via foreign keys, handles 7M+ rows well |
| psycopg3 | DB driver | Modern async-ready PostgreSQL driver for Python |
| PyJWT | JWT handling | Lightweight, standard-compliant JWT library |
| bcrypt | Password hashing | Industry standard for secure password storage |
| Docker + Compose | Containerization | Consistent environments across dev and production |
| NGINX | Reverse proxy | Routes traffic, enables future multi-app hosting |
| Ruff | Linter | Fast Python linter, enforces consistent code style |


## Reflection

*What was hard? What did you learn? What would you do differently?*
**What was challenging:**
- Loading 7M+ records efficiently required batch inserts and careful memory management, there where some trial and errors..
- The dataset contains aggregate rows (totals by sex, age, region) that needed filtering to avoid double-counting in statistics.
- NGINX path routing with FastAPI's trailing slash behavior required some extra configuration.

**What I learned:**
- Repository pattern provides clean separation that makes testing and refactoring much easier.
- Both Python as a language and SQL as database. I did learn a little a long time ago, but have not used it in written code for soo long that most had to be refreshed and dusted off. 
- Foreign key constraints at the database level are the right place to enforce referential integrity.

**What I'd do differently:**
- Separate the auth database from the data database to reduce blast radius in case of a breach.
- Implement rate limiting from the start, especially for public endpoints.
- Use RS256 instead of HS256 if building for multi-service architecture.
- I have in my own TODO list to migrate the hosting to my Raspberry Pi, and without VPN protection layer, rate limit is needed.
- Implement pooling for better performance instead of create connection per request.

## Security

### Implemented
- Passwords hashed with bcrypt (cost factor 12)
- JWT authentication (HS256) with short-lived access tokens (30min) 
  and rotating refresh tokens
- Refresh tokens stored as SHA-256 hashes, single-use
- All database queries use parameterized statements (psycopg3)
- Input validation via Pydantic on all endpoints
- Error responses never expose stack traces or internal details
- Foreign key constraints enforce referential integrity at DB level

### Known Limitations
- No rate limiting on authentication endpoints — brute force attacks 
  are theoretically possible
- Base Docker image (python:3.12-slim-bookworm) contains 1 known CVE 
  in an upstream Debian package — monitor for updated base images
- Tokens stored client-side (bearer tokens) — httpOnly cookies would 
  be more XSS-resistant for browser clients

### OWASP Coverage
| Risk | Status | Notes |
|------|--------|-------|
| A01 Broken Access Control | ✅ | Auth required for CUD operations |
| A02 Security Misconfiguration | ✅ | NGINX reverse proxy, no debug mode |
| A04 Cryptographic Failures | ✅ | bcrypt + JWT HS256 |
| A05 Injection | ✅ | Parameterized queries throughout |
| A07 Authentication Failures | ⚠️ | No rate limiting on auth endpoints |
| API1 BOLA | ✅ | Public data; user delete scoped to self |
| API2 Broken Authentication | ✅ | Token expiry + rotation implemented |

## Acknowledgements

*Resources, attributions, or shoutouts.*
- Dataset: [ Socialstyrelsen - Datafiler för utvecklare ](https://www.socialstyrelsen.se/statistik-och-data/statistik/for-utvecklare/) - CSV-filer Statistikdatabasen – Dödsorsaker 1997–2024 (7 st, 2,93 GB)
- FastAPI documentation: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)

## Requirements

See [all requirements in Issues](../../issues/). Close issues as you implement them. Create additional issues for any custom functionality. See [TESTING.md](TESTING.md) for detailed testing requirements.

### Functional Requirements — Common

| Requirement | Issue | Status |
|---|---|---|
| Data acquisition — choose and document a dataset (1000+ data points) | [#1](../../issues/1) | ✅ |
| Full CRUD for primary resource, read-only for secondary resources | [#2](../../issues/2) | ✅ |
| JWT authentication for write operations | [#3](../../issues/3) | ✅ |
| Error handling (400, 401, 404 with consistent format) | [#4](../../issues/4) | ✅ |
| Filtering and pagination for large result sets | [#17](../../issues/17) | ✅ |

### Functional Requirements — REST

| Requirement | Issue | Status |
|---|---|---|
| RESTful endpoints with proper HTTP methods and status codes | [#12](../../issues/12) | ✅ |
| HATEOAS (hypermedia links in responses) | [#13](../../issues/13) | ✅ |

### Functional Requirements — GraphQL

| Requirement | Issue | Status |
|---|---|---|
| Queries and mutations via single `/graphql` endpoint | [#14](../../issues/14) | :white_large_square: |
| At least one nested query | [#15](../../issues/15) | :white_large_square: |
| GraphQL Playground available | [#16](../../issues/16) | :white_large_square: |

### Non-Functional Requirements

| Requirement | Issue | Status |
|---|---|---|
| API documentation (Swagger/OpenAPI or Postman) | [#6](../../issues/6) | ✅ |
| Automated Postman tests (20+ test cases, success + failure) | [#7](../../issues/7) | ✅ |
| CI/CD pipeline running tests on every commit/MR | [#8](../../issues/8) | ✅ |
| Seed script for sample data | [#5](../../issues/5) | ✅ |
| Code quality (consistent standard, modular, documented) | [#10](../../issues/10) | ✅ |
| Deployed and publicly accessible | [#9](../../issues/9) | ✅ |
| Peer review reflection submitted on merge request | [#11](../../issues/11) | :white_large_square: |


