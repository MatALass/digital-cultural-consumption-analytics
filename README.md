# Digital Cultural Consumption Analytics

A portfolio-grade **Streamlit analytics application** built from the real Excel survey files in this repository.

This improved final version is stronger on the points that matter in a serious portfolio review:
- **cleaner decision flow** with filtered-vs-baseline benchmark context
- **better UX utility** through active filter summaries and export of the filtered analytical layer
- **broader behavioral reading** with access-style mix analysis by generation and value tier
- **safer exploration flow** with explicit empty-state handling and a corrected missingness chart
- **stronger maintainability** through clearer sidebar logic, reusable metrics helpers, and additional tests

The application analyzes digital cultural consumption in France through four decision lenses:
- **audience structure**
- **engagement intensity**
- **monetization potential**
- **risk-heavy access behavior**

It combines a curated analytical export with broader raw barometer modules to produce a dashboard that is more useful than a basic descriptive survey app, while staying technically honest about the integration limits.

---

## What is materially better in this final improved version

Compared with the previous delivered zip, this version adds practical improvements that are actually useful:

- **active filter summary in the sidebar** instead of making the user infer the state mentally
- **download button for the filtered analytics dataset** for handoff and validation
- **baseline comparison table** in the executive overview to avoid reading the filtered slice in isolation
- **segment opportunity table** to surface conversion headroom directly
- **generation × access-style share chart** in the behavior section
- **value-tier × access-style share chart** in the monetization section
- **better audience deep-dive** with filtered-share vs full-population-share context
- **correct missingness visualization** in the survey explorer
- **empty-filter safety** so the dashboard fails gracefully instead of silently producing nonsense
- **cleanup of the distributable zip** with no cached test artifacts included

---

## Data sources

Raw inputs used by the project:
- `data/raw/2024-barometre-consommation.xlsx`
- `data/raw/2024-datamap.xlsx`
- `data/processed/data.xlsx`

Generated helper artifacts:
- `data/processed/raw_module_inventory.csv`
- `data/processed/datamap_module_excerpt.csv`
- `data/processed/analytics_dataset_generated.csv`

---

## Analytical approach

### 1. Curated business layer
`data.xlsx` is kept as the primary interpretable layer.

That is the right architectural decision here because it preserves a business-readable subset of the survey and avoids pretending that the project fully reconstructs the entire raw questionnaire semantics.

### 2. Raw module enrichment
The raw barometer is used to derive broader feature blocks from selected modules such as:
- paid vs free content matrix
- device diversity
- illicit access channels
- illicit methods breadth
- stream-ripping behavior
- legal-offer advantages
- legal-consumption motivations

### 3. Interpretable engineered scores
The project builds explainable composite signals such as:
- `engagement_score`
- `monetization_score`
- `risk_behavior_score`
- `content_depth_score`
- `raw_risk_intensity_score`
- `legal_value_perception_score`

### 4. Rule-based segmentation
The final layer turns those signals into interpretable consumer segments:
- Premium Legal Users
- Hybrid Monetizers
- Heavy Free Users
- Risk-Oriented Free Users
- Casual Value Seekers
- Low Engagement Users

This is more defensible than decorative ML on top of a survey structure that does not justify it.

---

## Dashboard sections

### 📌 Executive Overview
- KPI board with quantiles, monetization, engagement, and risk signals
- filtered view vs full population benchmark table
- segment opportunity table for conversion headroom
- spending distribution and engagement progression by spending quintile

### 👥 Audience & Context
- spending dispersion by generation
- generation → family stage → segment composition
- urbanity vs content breadth
- profession concentration
- audience deep-dive with filtered vs full-population share context

### 🛜 Behavior & Access
- access style mix
- legality self-positioning
- segment-level risk radar
- VPN / DNS / cracked-app behavioral intensity
- generation × access-style share

### 💸 Monetization
- conversion funnel
- segment × value-tier structure
- engagement distribution by value tier
- value-tier × access-style share
- spending percentiles by segment

### 🧩 Raw Modules
- content-category breadth
- device diversity
- illicit-method breadth
- legal value perception
- content breadth vs spending

### 🎯 Segmentation
- segment distribution
- generation × segment mix
- average score profile by segment
- risk vs engagement scatter
- segment summary and opportunity prioritization

### 🔎 Survey Explorer
- analytical missingness
- datamap variable search
- text-label search
- raw-column explorer with preview and distribution

### 🧪 Methodology
- feature engineering
- segment logic
- limitations
- pipeline summary

---

## Project structure

```text
.
├── app.py
├── data/
│   ├── raw/
│   └── processed/
├── scripts/
│   └── __init__.py
├── src/
│   └── dashboard/
│       ├── sections/
│       └── utils/
├── tests/
└── .github/workflows/
```

---

## Run locally

```bash
pip install -e ".[dev]"
streamlit run app.py
```

Alternative entry point:

```bash
dcca-dashboard
```

To export the generated analytics table:

```bash
python scripts/build_analytics_dataset.py
```

---

## Quality checks

```bash
ruff check .
pytest -q
```

---

## Technical note on honesty

The project uses conservative row-order alignment between the curated analytical file and the raw barometer because the shared business key is not exposed in the processed export.

That is acceptable for a portfolio project as long as it is stated clearly.
It is **not** equivalent to a production-grade keyed integration.
