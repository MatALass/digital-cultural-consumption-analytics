# Digital Cultural Consumption Analytics

Streamlit dashboard on a 2024 French survey about digital cultural consumption (films, series, music, games, books): who consumes what, how much they spend, how they access content (legal, free, paid, illegal) and which groups have room to convert to paid offers.

## Data

| File | Content |
|---|---|
| `data/raw/2024-barometre-consommation.xlsx` | Raw survey export: about 5,040 respondents, 1,518 columns |
| `data/raw/2024-datamap.xlsx` | Questionnaire map: variable codes and labels |
| `data/processed/data.xlsx` | Curated subset: 5,040 rows, 23 readable columns (age, region, spending, legality, VPN use...) |

`data/processed/analytics_dataset_generated.csv` is the output of the pipeline below.

## Method

1. **Curated layer.** `data.xlsx` is the main table. Columns are renamed to English and typed; age is turned into age groups and generations, household and children into a family stage.
2. **Raw enrichment.** Selected raw modules add counts per respondent: paid vs free content categories, device diversity, illicit channels, illicit methods, stream ripping, perceived advantages of legal offers, motivations for legal consumption.
3. **Scores** (all in `src/dashboard/utils/transforms.py`):

   | Score | Formula |
   |---|---|
   | `engagement_score` | 0.45 × internet frequency + 0.35 × cultural frequency + 0.20 × spends something (each part scaled to 0-1) |
   | `monetization_score` | 0.50 × payment orientation + 0.20 × paid access + 0.30 × spends something |
   | `risk_behavior_score` | sum of VPN, DNS settings, illegal download and cracked apps scores |
   | `raw_risk_intensity_score` | illicit channels + illicit methods + stream ripping |
   | `content_depth_score` | 0.45 × content categories + 0.25 × devices + 0.30 × answer coverage |

4. **Value tiers** from monthly spending: non-spender, then low, mid, high and top spender split at the median, Q3 and P90 of spending.
5. **Segments**, rule-based and checked in this order:

   | Segment | Rule |
   |---|---|
   | Premium Legal Users | spending ≥ Q3, legal and paid access, risk score ≤ 1 |
   | Hybrid Monetizers | spending ≥ Q3 and at least one illicit channel |
   | Heavy Free Users | no spending, engagement ≥ 0.65, 3+ content categories |
   | Risk-Oriented Free Users | risk score ≥ 4 and 2+ illicit methods |
   | Casual Value Seekers | some spending, engagement < 0.65 |
   | Low Engagement Users | everyone else |

Rules were preferred to clustering: the segments stay readable and each one maps to a business question (who already pays, who could pay, who is a piracy risk).

## Results

On the full population (5,040 respondents):

- 42.7 % spend something each month; median spending is 0 € and Q3 is 20 €.
- 8.4 % are engaged non-spenders (engagement ≥ 0.65, no spending, 2+ content categories): the clearest conversion target.
- Segments: Heavy Free Users 6.9 %, Hybrid Monetizers 6.4 %, Premium Legal Users 3.5 %, Casual Value Seekers 1.6 %, Risk-Oriented Free Users 1.3 %, Low Engagement Users 80.3 %.

The large "Low Engagement" group is partly an artefact of missing answers: the legality question is empty for 42 % of rows and the free/paid question for 59 %, so many respondents cannot be placed in a more specific segment.

## Dashboard

| Page | Content |
|---|---|
| Executive Overview | KPIs, filtered view vs full population, segment opportunity table, spending distribution |
| Audience & Context | spending by generation, family stage, urbanity, profession |
| Behavior & Access | access style mix, legality, risk radar by segment, VPN / DNS / cracked apps |
| Monetization | conversion funnel, value tiers, access style by value tier |
| Raw Modules | content breadth, devices, illicit methods, legal value perception |
| Segmentation | segment mix, score profiles, risk vs engagement |
| Survey Explorer | missing values, datamap search, raw column preview |
| Methodology | scores, segment rules, limits |

The sidebar filters every page, shows the active filters and exports the filtered table as CSV.

## Run it

```bash
pip install -e ".[dev]"
streamlit run app.py          # or: dcca-dashboard
dcca-build-analytics          # rewrites data/processed/analytics_dataset_generated.csv
```

Checks (also run in CI on Python 3.11 and 3.12):

```bash
ruff check .
pytest -q
```

## Project structure

```text
app.py                        Streamlit entry point
src/dashboard/
  config.py                   paths, column mapping, score maps, pages
  filters.py                  sidebar filters
  sections/                   one module per page
  utils/                      io, transforms (scores, segments), metrics, viz
  cli/build_analytics_dataset.py
tests/                        filters, metrics, transforms, routing, viz
data/raw/, data/processed/
```

## Limits

- The curated file and the raw export share no respondent key. They are aligned on row order, which assumes both files keep the original order. This is not a keyed join.
- Score weights and segment thresholds are set by hand, not estimated.
- The survey is declarative: illegal consumption is probably under-reported.

## License

MIT
