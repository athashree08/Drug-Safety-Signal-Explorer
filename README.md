
# Drug Safety Signal Explorer

### Finding the drug–reaction pairs that deserve a second look.

[![Live App](https://img.shields.io/badge/Live%20App-Streamlit-red?style=for-the-badge&logo=streamlit)]([YOUR_STREAMLIT_URL](https://drug-safety-signal-explorer-drgfsqgw3uz6jymgmykata.streamlit.app/))
[![Dashboard](https://img.shields.io/badge/Dashboard-Tableau-blue?style=for-the-badge&logo=tableau)](https://public.tableau.com/app/profile/athashree.badokar/viz/Drugsafetysignal/DrugSafetySignalExplorer)

A Python-based pharmacovigilance analytics project that transforms 10,000 openFDA adverse-event reports into structured drug–reaction data and uses Reporting Odds Ratios to surface potential disproportional-reporting signals for further investigation.
What if you could take thousands of real-world adverse-event reports, turn messy nested JSON into something analyzable, and ask:

> **Which drug–reaction pairs are being reported disproportionately often?**

That is what this project explores.

The **Drug Safety Signal Explorer** is a Python-based data pipeline and analytics application built on the openFDA Adverse Event API. It collects adverse-event reports, transforms nested JSON into a structured dataset, calculates **Reporting Odds Ratios (ROR)**, and surfaces drug–reaction pairs that meet predefined disproportional-reporting criteria.

The project is intentionally designed around one important idea:

> **A statistical signal is a reason to investigate — not proof of causality.**

---

## Why I Built This

Drug safety data looks simple from the outside: a drug, a reaction, and a report.

The actual data is much messier.

The openFDA adverse-event API returns deeply nested JSON containing multiple drugs, reactions, patients, and metadata within individual reports. Before any statistical analysis can happen, the data has to be collected reliably, flattened, cleaned, and transformed into a structure that can actually be analyzed.

So this project focuses on the complete workflow:

**API → Data Engineering → Statistical Analysis → Visualization → Investigation**

rather than simply training a model and reporting an accuracy score.

---

## What the Project Does

The pipeline:

1. Queries the openFDA Adverse Event API
2. Collects a defined sample of **10,000 reports**
3. Handles API pagination and retries
4. Uses local caching to avoid unnecessary repeated requests
5. Extracts drugs and adverse reactions from nested JSON
6. Normalizes the data into a relational/tidy structure
7. Creates drug–reaction reporting pairs
8. Filters candidate pairs with at least 3 reports
9. Calculates Reporting Odds Ratio (ROR)
10. Calculates a 95% confidence interval
11. Identifies potential disproportional-reporting signals
12. Exports the processed results for visualization
13. Provides both a Tableau dashboard and an interactive Streamlit application

---

# The Data

The project uses the public **openFDA Adverse Event API**.

The final analysis contains:

| Metric | Value |
|---|---:|
| Reports analyzed | 10,000 |
| Unique drugs | 5,273 |
| Unique reactions | 2,954 |
| Candidate pairs with ≥3 reports | 3,712 |
| Potential signal pairs | 2,502 |

The dataset is derived from voluntary adverse-event reports, so it should not be interpreted as a controlled clinical dataset.

---

# From Messy JSON to Analyzable Data

One of the main challenges was that a single adverse-event report can contain multiple drugs and multiple reactions.

For example, conceptually:

```text
Report
├── Drug A
├── Drug B
├── Reaction X
└── Reaction Y
````

The analysis transforms this structure into individual drug–reaction observations:

```text
Drug       Reaction
Drug A     Reaction X
Drug A     Reaction Y
Drug B     Reaction X
Drug B     Reaction Y
```

This makes it possible to count how frequently each drug–reaction combination appears across the dataset.

The pipeline also accounts for missing fields and inconsistent nested structures rather than assuming every API response has the same shape.

---

# Measuring Disproportional Reporting

Instead of asking:

> "Did this drug cause this reaction?"

the project asks a narrower statistical question:

> **"Is this drug–reaction pair reported disproportionately compared with the rest of the dataset?"**

For each drug–reaction pair, the project calculates the **Reporting Odds Ratio (ROR)**.

The underlying 2×2 contingency table is:

|                  | Reaction of Interest | Other Reactions |
| ---------------- | -------------------: | --------------: |
| Drug of Interest |                    A |               B |
| Other Drugs      |                    C |               D |

The ROR is:

$$
ROR = \frac{A \times D}{B \times C}
$$

A 95% confidence interval is also calculated using the standard log-ROR formulation.

---

# Signal Definition

A pair is treated as a **potential signal** when:

```text
ROR > 1
AND
Lower 95% CI > 1
AND
Report Count ≥ 3
```

This creates a reproducible rule for surfacing pairs for further investigation.

The threshold is deliberately presented as a **signal-detection rule**, not as a medical safety classification.

---

# What This Does NOT Prove

This is the most important part of the project.

A potential signal **does not establish that a drug caused a reaction**.

Adverse-event reports are voluntary and can be affected by factors such as:

* Reporting bias
* Drug popularity
* How long a drug has been on the market
* Media attention
* Changes in reporting behavior
* Other underlying patient or clinical factors

For example, a sudden increase in reports could reflect increased attention to a drug or reaction rather than an actual increase in risk.

Therefore, the results should be treated as:

> **Drug–reaction pairs worth further human review.**

They should **not** be interpreted as:

* Diagnoses
* Medical advice
* Causal relationships
* Proof that a drug is dangerous
* Recommendations to stop or change medication

---

# Tableau Dashboard

The Tableau dashboard is designed as the **executive analytical view** of the project.

It answers:

> **"What is happening in the data?"**

It includes:

### Top Reported Drug–Reaction Pairs

Ranks the most frequently reported drug–reaction combinations by report count.

### Top Disproportional-Reporting Signals

Highlights pairs with the highest ROR values among the identified potential signals.

### Report Count vs ROR

A scatter plot showing the relationship between reporting frequency and disproportionality.

This helps distinguish pairs that are:

* Frequently reported
* Highly disproportionate
* Both frequent and disproportionate
* Supported by relatively few reports

---

# Streamlit Signal Explorer

The Streamlit application provides a more interactive investigation experience.

While Tableau answers:

> **"What is happening?"**

Streamlit is designed to answer:

> **"Let me investigate it."**

Users can explore the processed signal dataset using:

* Drug selection
* Reaction selection
* Minimum report-count threshold
* Minimum ROR threshold
* Interactive signal tables
* Report-count vs ROR visualization
* Signal-level details

The application uses the processed CSV rather than repeatedly querying the API, keeping exploration fast and separating data collection from analysis.

---

# Project Architecture

```text
                 openFDA API
                      │
                      ▼
             Data Collection
                      │
        ┌─────────────┴─────────────┐
        │                           │
   Pagination                  Retry Logic
        │                           │
        └─────────────┬─────────────┘
                      ▼
                Raw Reports
                      │
                      ▼
             JSON Normalization
                      │
                      ▼
            Drug–Reaction Pairs
                      │
                      ▼
              ROR Calculation
                      │
                      ▼
             Signal Detection
                      │
              ┌───────┴───────┐
              ▼               ▼
           Tableau         Streamlit
          Dashboard       Investigation
```

---

# Tech Stack

### Data Collection

* Python
* Requests
* openFDA API

### Data Processing

* Pandas
* JSON normalization
* Local caching

### Statistical Analysis

* Reporting Odds Ratio
* 95% Confidence Intervals
* 2×2 contingency tables

### Visualization

* Tableau Public
* Plotly

### Application

* Streamlit

### Development

* Jupyter Notebook
* Git
* GitHub

---

# Project Structure

```text
drug-safety-signal-explorer/
│
├── data/
│   └── drug_safety_signals.csv
│
├── notebooks/
│   └── drug_safety_signal.ipynb
│
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Running the Streamlit App

Clone the repository:

```bash
git clone <your-repository-url>
cd drug-safety-signal-explorer
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run app.py
```

The application will open locally in your browser.

---

# Reproducibility

The data collection pipeline was designed to make API-based analysis more reliable by including:

* Pagination
* Retry handling
* Local caching
* Controlled request delays
* Missing-field handling
* A defined report sample

The analysis can therefore be reproduced from the collection stage through to the final signal dataset.

---

# Limitations

This project has several important limitations.

### Voluntary reporting

The underlying reports are not a random sample of all adverse events.

### Reporting bias

Some drugs or reactions may receive more attention or reporting than others.

### No causal inference

ROR identifies disproportional reporting. It does not prove that a drug caused a reaction.

### Sample-based analysis

The project analyzes a defined sample of 10,000 reports rather than the complete universe of adverse-event reports.

### Statistical signals require context

A high ROR can occur even when the absolute number of reports is small.

That is why the analysis includes a minimum report-count threshold and presents the results as candidate signals rather than confirmed findings.

---

# What I Learned

The most useful part of this project wasn't the ROR formula.

It was learning how much work happens **before** a statistical calculation becomes meaningful.

I worked through:

* Working with a real public API
* Handling pagination and unreliable requests
* Working with nested JSON
* Normalizing semi-structured data
* Designing a relational representation of event data
* Building reproducible statistical calculations
* Creating interpretable visualizations
* Separating exploratory analysis from application logic
* Thinking carefully about what a statistical result actually means

Most importantly, the project reinforced a principle that applies far beyond drug safety:

> **Good data analysis is not just finding a pattern. It is understanding whether the pattern deserves to be trusted.**

---

# What I'd Do Next

If this project were extended further, I would explore:

* Larger-scale data collection
* Temporal signal analysis
* Reporting trends over time
* Stratification by demographic or clinical factors
* Comparison with additional pharmacovigilance methods
* Signal ranking that incorporates reporting volume
* More robust statistical validation
* External validation against established safety findings
* Automated monitoring of newly available reports

These extensions would require additional validation before being used for any real-world safety decision.

---

# One-Sentence Summary

**A Python-based pharmacovigilance analytics project that transforms 10,000 openFDA adverse-event reports into structured drug–reaction data and uses Reporting Odds Ratios to surface potential disproportional-reporting signals for further investigation.**

---

## Disclaimer

This project is intended for **educational and analytical purposes only**.

The results are not medical advice, clinical recommendations, or confirmed drug-safety findings. Potential signals represent patterns of disproportionate reporting within the analyzed data and require further investigation and domain expertise.


