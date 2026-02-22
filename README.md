# Australian Road Fatalities Analysis

Analysis of fatal road crashes in Australia using the Australian Road Deaths Database (ARDD), covering 1989–2025. The project explores demographic, geographic, and temporal risk factors across three notebooks, with a portfolio overview page that highlights key findings.

**Live site:** [julian-chung.github.io/ardd-road-safety-analysis](https://julian-chung.github.io/ardd-road-safety-analysis)

---

## Project Structure

```
ardd-road-safety-analysis/
├── data/                          # ARDD crash data and motorcycle licence data
├── notebooks/
│   ├── 0-eda-australian-road-fatalities.ipynb   # National overview: trends by state, year, age, gender
│   ├── 1-vulnerable-road-users.ipynb            # Sub-analysis: child pedestrians and cyclists
│   └── 2-motorcyclists.ipynb                    # Sub-analysis: motorcyclist and pillion fatalities
├── scripts/
│   └── data_cleaning.py           # Shared data cleaning pipeline
├── index.qmd                      # Portfolio overview page (key findings + links to notebooks)
├── _quarto.yml                    # Quarto website configuration
└── requirements.txt
```

---

## Notebooks

**0 — Main EDA**
National overview of road fatalities: yearly trends, state comparisons, age and gender distributions, and day/time crash patterns.

**1 — Vulnerable Road Users**
Focused analysis of child pedestrians and cyclists (under 16): trends by year, state, season, and gender.

**2 — Motorcyclists**
Analysis of rider and pillion passenger fatalities including age/gender breakdowns, day/time crash patterns, and risk normalised against licensing data (deaths per 10,000 licences).

---

## Setup

```bash
git clone https://github.com/julian-chung/ardd-road-safety-analysis.git
cd ardd-road-safety-analysis

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Data: download the ARDD dataset from [BITRE](https://www.bitre.gov.au/statistics/safety/fatal_road_crash_database) and place CSV files in `data/`.

To render the site locally:
```bash
QUARTO_PYTHON=.venv/bin/python3 quarto render
```

---

## Author

**Julian Chung** — Clinical Trials & Public Health Analyst
[github.com/julian-chung](https://github.com/julian-chung)
