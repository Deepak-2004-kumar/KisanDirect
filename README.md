# 🌾 KisanDirect

**AI-powered digital agricultural marketplace connecting farmers directly with retailers, restaurants, food processors, institutional buyers and FPOs — reducing unnecessary intermediary layers while keeping essential supply-chain services (transport, storage, aggregation) transparent and efficient.**

Built for **Smart India Hackathon 2026 — Problem Statement PS 33 (SIH26033)**:
*"Reducing Intermediary Losses that Hurt Farmer Earnings and Raise Consumer Prices."*

> ⚠️ This is a working MVP/prototype. All market prices, order history, and demand figures are **synthetic/demo data**, clearly labeled as such throughout the app and API. No real government or market datasets are used or fabricated.

---

## Table of Contents
1. [How This Solves PS 33](#how-this-solves-ps-33)
2. [Architecture](#architecture)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Installation](#installation)
6. [Running with Docker](#running-with-docker-recommended)
7. [Running Manually](#running-manually-without-docker)
8. [SIH Demo Walkthrough](#sih-demo-walkthrough)
9. [API Documentation](#api-documentation)
10. [How the AI Matching Score Works](#how-the-ai-matching-score-works)
11. [Testing](#testing)
12. [Important Product Principles](#important-product-principles)
13. [Known Limitations & Upgrade Paths](#known-limitations--upgrade-paths)

---

## How This Solves PS 33

**Problem:** Farmers often receive a lower share of the final price while consumers may pay more, because of inefficient supply chains, information asymmetry, and unnecessary intermediary layers. Not all intermediaries are bad — aggregation, storage, and transport are genuinely valuable — but *unnecessary* layers and opacity hurt both ends of the chain.

**Solution:** KisanDirect provides:
- A **direct marketplace** where farmers list produce and buyers discover it directly.
- An **explainable AI matching engine** that ranks buyer-farmer pairs on more than just price — crop fit, quantity, quality, distance, delivery timing, and farmer reliability — so farmers aren't pressured into the highest-sounding but least-practical offer, and buyers get a transparent reason for every recommendation.
- **Price intelligence** so farmers know current, historical, and (labeled-as-estimated) forecasted prices before they negotiate.
- **Demand forecasting** so farmers can plan what to grow/sell and buyers can plan procurement.
- **Logistics estimation** so both sides see real transport costs and delivery times up front, instead of discovering them after the deal.
- **Admin analytics** to track platform health and (clearly labeled as estimated/synthetic) impact metrics.

**Impact (for this prototype's demo data):**
- Better market access for farmers beyond their immediate local mandi/village network
- Transparent price discovery instead of opaque, one-sided offers
- Reduced *unnecessary* intermediary layers — essential logistics/storage/aggregation providers still participate, now with visibility
- Lower logistics inefficiency through upfront cost/route estimation
- Better supply-demand matching via forecasting

---

## Architecture

```
Farmer / Buyer
      |
Frontend (React + Vite + Tailwind)
      |
Backend API (FastAPI, JWT auth, RBAC)
      |
AI Services (modular, independently swappable)
 +--------------+---------------+--------------+
 |  Matching    |   Price AI    |  Demand AI   |  Logistics
 |  Engine      | (baseline +   | (baseline +  | (haversine +
 |  (explainable|  linear reg.  |  linear reg. |  vehicle-tier
 |  weighted    |  trend)       |  trend +     |  cost model,
 |  scoring)    |               |  LOW/MED/HIGH|  OR-Tools path
 |              |               |  classifier) |  documented)
 +--------------+---------------+--------------+
                      |
                 PostgreSQL (+ PostGIS reference schema)
                      |
                   API Response -> UI
```

Each AI service lives in `ml/<module>/` as a **standalone, independently testable Python module** with no FastAPI dependency, then gets a thin wrapper in `backend/app/ai/*_service.py` that the API routers call. This means:
- You can run and unit-test the AI logic completely outside the web stack (see each module's `if __name__ == "__main__":` block).
- Any module (e.g. `price_model.py`) can be swapped for a more advanced model later without touching the API contract.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS, React Router, Recharts, i18next |
| Backend | Python 3.11, FastAPI, Pydantic v2 |
| Database | PostgreSQL 15 (+ PostGIS extension in the reference schema) |
| AI/ML | Pandas, NumPy, scikit-learn (Linear Regression baselines) |
| Auth | JWT (python-jose), bcrypt password hashing (passlib), RBAC |
| Maps (planned UI integration) | OpenStreetMap / Leaflet |
| Optimization (documented upgrade path) | Google OR-Tools for multi-stop VRP |
| Containerization | Docker, docker-compose |

---

## Project Structure

```
kisan-direct/
├── frontend/                  React + Vite + Tailwind SPA
│   └── src/
│       ├── components/        Navbar, MatchCard, etc.
│       ├── pages/              14 pages (Landing, Login, Dashboards, etc.)
│       ├── services/api.js     Axios client + typed API calls
│       ├── hooks/useAuth.js    Auth context (JWT in localStorage)
│       └── i18n/i18n.js        English + Hindi translations
│
├── backend/
│   ├── app/
│   │   ├── api/                One router file per resource
│   │   ├── models/              SQLAlchemy ORM models
│   │   ├── schemas/              Pydantic request/response schemas
│   │   ├── ai/                   Thin wrappers around ml/ modules
│   │   ├── core/                 Config, JWT/security, RBAC dependency
│   │   ├── database/             DB session + schema.sql (PostGIS reference)
│   │   └── main.py               FastAPI app entrypoint
│   ├── seed.py                   Seeds DB from data/synthetic/*.json
│   └── requirements.txt
│
├── ml/                          Standalone, independently runnable AI modules
│   ├── matching/matching_engine.py
│   ├── price_prediction/price_model.py
│   ├── demand_forecasting/demand_model.py
│   └── logistics/logistics_engine.py
│
├── data/synthetic/               Seed data generator + generated fixtures
│   └── seed_data.py
│
├── docker-compose.yml
├── .env.example
└── README.md   (this file)
```

---

## Installation

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+ (with PostGIS extension available, for the reference schema)
- Docker + docker-compose (optional but recommended)

### Clone & configure
```bash
cd kisan-direct
cp .env.example .env
# edit .env — set a real JWT_SECRET_KEY and DB password
```

---

## Running with Docker (recommended)

```bash
docker compose up --build
```

This starts the complete containerized application:
- `db` — PostgreSQL + PostGIS on port 5432
- `backend` — FastAPI on **http://localhost:8000** (auto-seeds demo data on first boot)
- `frontend` — built React app served via Nginx on **http://localhost:5173**

Swagger API docs: **http://localhost:8000/docs**

The compose stack waits for PostgreSQL and the backend health endpoint before serving the frontend. The included `.env.example` contains the configurable database and JWT values; copy it to `.env` before use and replace the demo secrets.

---

## Running Manually (without Docker)

### 1. Database
Create a PostgreSQL database and user matching your `.env`:
```sql
CREATE USER kisandirect WITH PASSWORD 'change_me_strong_password';
CREATE DATABASE kisandirect OWNER kisandirect;
```
The running app uses SQLAlchemy's `create_all()` for the MVP (simple lat/lon columns for portability). `backend/app/database/schema.sql` is provided as the **production-grade reference schema** with PostGIS geography columns, full indexing, and additional tables (warehouses, transporters, deliveries, reviews, notifications) for when you're ready to move beyond the MVP — apply it manually with `psql` if you want the full schema instead of the simplified ORM-generated one.

### 2. Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py                      # creates tables + loads synthetic demo data
uvicorn app.main:app --reload --port 8000
```

### 3. Generate/refresh synthetic data (optional — pre-generated fixtures are already included)
```bash
cd data/synthetic
python seed_data.py
```

### 4. AI modules — run standalone (no server needed)
```bash
cd ml/matching && python matching_engine.py
cd ml/price_prediction && python price_model.py
cd ml/demand_forecasting && python demand_model.py
cd ml/logistics && python logistics_engine.py
```

### 5. Frontend
```bash
cd frontend
npm install
npm run dev
```
Visit **http://localhost:5173**.

---

## SIH Demo Walkthrough

Demo logins (created by `seed.py`):

| Role | Email | Password |
|---|---|---|
| Admin | admin@kisandirect.in | admin123 |
| Farmer (demo scenario) | farmer1@kisandirect.in | farmer123 |
| Buyer | buyer1@kisandirect.in | buyer123 |

**Scripted end-to-end demo:**
1. Log in as **Farmer 1** (Ramesh Kumar, Rohtak). A demo listing is pre-seeded: **Tomato, 500kg, Grade A, ₹25/kg, harvest 15 Sept, Rohtak**.
2. Log in as a **Buyer** (different browser/incognito) → go to Marketplace → search "Tomato".
3. Buyer makes an offer (e.g. ₹26/kg, ~18km away) via **Make Offer**.
4. Back on the Farmer Dashboard, open the listing to see the **AI match score and explanation** for every offer received (e.g. *"94% Match — Same crop and quality, quantity fully satisfied, 18 km distance and acceptable price"*) — and compare against a hypothetical distant buyer offering a higher price but scoring lower overall.
5. Farmer clicks **Accept Offer** → an Order is created.
6. Visit **Logistics** page to see distance, suggested vehicle, and estimated cost for that route.
7. Buyer (or farmer) marks the order **Paid** on the Orders/Payments page → status flips `PENDING → PAID`.
8. Log in as **Admin** → Admin Dashboard shows updated KPIs: active orders, total transaction value, average farmer price, etc. (all labeled Estimated/Synthetic where relevant).

You can reproduce the core matching logic independently of the UI by running:
```bash
cd ml/matching && python matching_engine.py
```
which prints exactly this Buyer A vs Buyer B comparison from the command line.

---

## API Documentation

Interactive Swagger/OpenAPI docs are auto-generated by FastAPI at **`/docs`** once the backend is running.

Key endpoints:
```
POST   /auth/register
POST   /auth/login

GET    /farmers
GET    /farmers/{id}

POST   /crop-listings
GET    /crop-listings              ?crop=&min_price=&max_price=&min_quantity=&quality_grade=
GET    /crop-listings/{id}
PUT    /crop-listings/{id}
DELETE /crop-listings/{id}

POST   /offers                      (auto-computes AI match score)
GET    /offers                      ?listing_id=
POST   /offers/{id}/accept          (creates an Order)

GET    /orders
GET    /orders/{id}
POST   /orders/{id}/pay             (demo payment flow)

GET    /prices                      ?crop=
GET    /prices/trends               ?crop=

GET    /demand/forecast             ?crop=&region=

POST   /ai/match                    (standalone match score, given listing_id + buyer_id)

POST   /logistics/route             (distance, vehicle, cost, ETA)

GET    /admin/analytics             (admin-only)
```

All endpoints use Pydantic schemas for validation and return structured error messages on failure.

---

## How the AI Matching Score Works

Location: `ml/matching/matching_engine.py`

The match score is a **transparent, weighted sum of seven sub-scores**, each 0–100:

| Factor | Weight | What it checks |
|---|---|---|
| Crop compatibility | 20% | Same crop? (mismatch = score of 0, disqualifying) |
| Quantity compatibility | 15% | Does supply meet/exceed the requirement without huge oversupply? |
| Quality compatibility | 10% | Does the listing's grade meet the buyer's minimum? |
| Price compatibility | 20% | Is the offer at/above the farmer's expected price (without penalizing generous offers)? |
| Distance / logistics | 20% | Haversine distance, decaying smoothly past a 50km comfort zone |
| Delivery compatibility | 5% | Can harvest/availability meet the buyer's timeline? |
| Reliability | 10% | Farmer's historical fulfillment reliability score |

**Crucially, the engine never simply picks the highest price** — a distant buyer with a higher offer can score *lower* overall than a nearby buyer with a fair offer, because the distance and logistics-cost penalty outweighs a modest price gain. Every score returns:
- The overall `match_score` (0-100)
- Per-factor `sub_scores`
- A ranked, human-readable `reasons` list (e.g. *"Same crop (Tomato)"*, *"18 km distance (~₹144 est. transport)"*)
- `warnings` for edge cases (crop mismatch, very low price, very large distance)

This is intentionally a **transparent baseline model, not a black-box neural network** — for a two-sided marketplace where farmers must trust *why* a recommendation was made, explainability was prioritized over marginal accuracy gains. The `WEIGHTS` dictionary at the top of the file is the single source of truth for the scoring logic and can be tuned by a domain expert without touching the math. A future iteration could train a learned ranking model (e.g. LightGBM LambdaRank) on accepted-vs-rejected offer outcomes, using these same seven features as inputs, while keeping the reason-generation logic for explainability.

---

## Testing

```bash
# AI modules (no DB/server needed)
cd ml/matching && python matching_engine.py
cd ml/price_prediction && python price_model.py
cd ml/demand_forecasting && python demand_model.py
cd ml/logistics && python logistics_engine.py

# Backend — after installing requirements.txt
cd backend
python -m py_compile app/**/*.py     # syntax check
uvicorn app.main:app --reload        # then exercise /docs manually or with pytest/httpx
```
For CI, add `pytest` + `httpx.AsyncClient` tests against the FastAPI `TestClient` (not included in this MVP pass — flagged as a next step).

---

## Important Product Principles

1. The **farmer remains in control** of accepting or rejecting every offer — the AI never auto-accepts.
2. AI recommendations are **explainable** — every score ships with human-readable reasons.
3. Price predictions are **estimates, not guarantees**, and are labeled as such everywhere they appear.
4. The AI **does not make financial or legal decisions** on behalf of any user.
5. **Essential intermediaries are not automatically bad** — the platform targets unnecessary layers and opacity, not aggregation/transport/storage services themselves.
6. All demo/synthetic data is **clearly labeled** and never presented as real government or market data.

---

## Known Limitations & Upgrade Paths

This is an SIH prototype, not a production system. Documented, intentional simplifications:

- **Distance = haversine, not road distance.** Swap `haversine_km()` in `ml/logistics/logistics_engine.py` for an OSRM/OpenRouteService API call for real road distances.
- **Single farmer → single buyer routing only.** `plan_multi_stop_route()` in the same file documents the Google OR-Tools Capacitated-VRP-with-Time-Windows approach for batching multiple pickups/drop-offs into one vehicle run.
- **Price/demand models are linear-regression baselines** on synthetic data, per the "start simple before adding complexity" instruction. `PricePredictor`/`DemandForecaster` classes are structured so a RandomForest/XGBoost model can be swapped in without changing the API contract.
- **SQLAlchemy `create_all()` is used for the running MVP** instead of the full PostGIS schema in `schema.sql`, to keep local setup friction low. Migrate to Alembic migrations against the PostGIS schema before any production use.
- **No automated test suite included** in this pass — `ml/` modules are runnable/verifiable standalone as shown above, which stands in for unit tests during the hackathon timeline.
- **Frontend map integration (Leaflet/OpenStreetMap) is stubbed** — the Logistics/CropDetails pages currently show numeric route estimates; wiring an actual `<MapContainer>` with farmer/buyer markers is the next visual enhancement (the `leaflet`/`react-leaflet` packages are already in `package.json`).
