# 🚗 Australian Road Fatalities Analysis

This project investigates patterns in fatal road transport accidents across Australia using the Australian Road Deaths Database (ARDD). The analysis spans over three decades (1989–2022) and identifies demographic, geographic, and temporal risk factors contributing to road deaths.

In addition to a comprehensive exploratory data analysis (EDA), this repository includes targeted sub-analyses on vulnerable road users such as child pedestrians, cyclists, and motorcyclists.

---

## 📂 Project Structure

```bash
ardd-road-safety-analysis/
├── data/                          # Raw data files (e.g. ARDD CSVs, license data)
├── notebooks/
│   ├── 0-eda-australian-road-fatalities.ipynb       # Main EDA: trends by state, year, age, gender
│   ├── 1-vulnerable-road-users.ipynb                # Sub-analysis: child pedestrians and cyclists
│   └── 2-motorcyclists.ipynb                        # Sub-analysis: motorcyclist and pillion deaths
├── scripts/
│   └── data_cleaning.py           # Modular pipeline for data cleaning and preparation
├── └── fetch_and_clean.py         # Script to fetch and clean ARDD data - WIP
├── requirements.txt
└── README.md
```

---

## 🔍 Key Features

### 📊 Exploratory Data Analysis
- Fatalities by **state**, **age**, **gender**, **day of week**, and **time of day**
- Temporal trends in **overall and subgroup-specific deaths**
- Seasonal and daily crash risk patterns

### 👶 Vulnerable Road User Analysis
- Child fatalities involving **pedestrians** and **cyclists**
- Trends by **year**, **state**, **time**, and **gender**
- Evidence of school holiday and weekend risk periods

### 🏍️ Motorcyclist Sub-Study *(NEW)*
- Analysis of rider and pillion passenger fatalities
- Risk stratification by **age**, **gender**, **day/time**, and **season**
- Integration of **motorcycle licensing data** to normalize risk (deaths per 10,000 licenses)

---

## 🧰 How to Use

1. **Clone the repository**
   ```bash
   git clone https://github.com/julian-chung/ardd-road-safety-analysis.git
   cd ardd-road-safety-analysis
   ```

2. **Set up your Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Download and place data**
   - Get the ARDD dataset from the [Australian Road Deaths Database (BITRE)](https://www.bitre.gov.au/statistics/safety/fatal_road_crash_database)
   - Place the relevant CSV files in the `data/` directory.
   - Optional: Add motorcycle licensing data (used in `2-motorcyclists.ipynb`).

4. **Run the notebooks**
   ```bash
   jupyter notebook
   ```
   - Start with `0-eda-australian-road-fatalities.ipynb` for a general overview.
   - Use the other notebooks for deep dives into specific road user groups.

---

## 📌 Project Goals

This analysis aims to:
- Support **evidence-based policymaking** for road safety
- Demonstrate **data storytelling and visualization** skills
- Serve as a **public health portfolio project** showcasing epidemiological analysis and modular Python/R workflows

---

🛠️ Project Status: Ongoing
This project is a live and evolving piece. It was last updated in May 2025. Minor tweaks and updates are planned over time.

---

## 👨‍💻 Author

**Julian Chung**  
Clinical Trials & Public Health Analyst  
[GitHub: julian-chung](https://github.com/julian-chung)

---
