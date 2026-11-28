# GEO Datasets Recommendation System: An Integrated Database Approach

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Database: SQLite3](https://img.shields.io/badge/Database-SQLite3-lightgrey.svg)](https://www.sqlite.org/)

---

## Table of Contents
- [Overview](#overview)
- [Workflow & Execution](#workflow--execution)
- [Author & Contact](#author--contact)

---

## Overview

Finding relevant genomic datasets within public repositories like NCBI GEO often requires manual, keyword-based queries that overlook latent semantic relationships between studies. This framework formulates dataset retrieval as a recommendation problem:

- **Entity Integration:** Disambiguates author entities across GEO and PubMed records using contact email mapping, affiliation parsing, and SVM classifiers.
- **Multi-Field Content Filtering:** Calculates item-item similarity vectors using text metadata combinations (Title, Summary, Overall Design, Experiment Type, and Organism).
- **Metric Aggregation:** Evaluates Min, Max, and Average pooling aggregation functions over 3-field and 5-field configurations to score candidate datasets against historical author profiles.

---

### Prerequisites & Environment Requirements

Before running the pipeline, ensure your environment meets the following software version requirements:

- **Python:** `>= 3.8` 
- **R:** `4.2.2` 

Then install requirements:
```
pip install -r requirements.txt
```
```
Rscript ./src/install.R
```


## Workflow & Execution

Follow these four sequential steps to build the database, populate all tables, generate author recommendations, and export the evaluation figures.




### Step 1: Initialize the Empty Database

Run `database_construction.py` to create the SQLite database (`../test/sample.db`) and initialize its relational schema across eight tables (`series`, `publication`, `author`, `affiliation`, `publication_series`, `author_affiliation`, `author_publication`, and `author_series`):

```
python database_construction.py
```

### Step 2: Populate the Database

Run `import_table.py` to import the corresponding table CSV files from `../data/` into `../test/sample.db`:

```
python import_table.py
```

### Step 3: Compute Dataset Feature Similarities

Run `compute_similarity.py` to retrieve series metadata from `../test/sample.db` alongside the pre-defined author-level dataset splits in `../data/train_test/`, where `historical_set.csv` specifies the fixed historical dataset IDs and `test_set.csv` specifies the fixed candidate test set for evaluation. For each author, the script calculates pairwise field-level and aggregated (5-feature and 3-feature min, max, and average) similarity scores between every candidate test dataset and historical dataset, exporting per-author score tables (`{author_id}.csv`) to `../test/`:

```
python compute_similarity.py
```

### Step 4: Evaluate Results & Produce Performance Figures

Run `performance_curve.R` to aggregate the per-author similarity tables in `../test/`, evaluate Precision, Recall, and F1​ scores across similarity thresholds (`0.00` to `1.00` in steps of `0.05`), export metric tables and 3x3 performance curve PDFs (`5f_performance_vectorVersion.pdf` and `3f_performance_vectorVersion.pdf`) to `../test/evaluation/5features` and `../test/evaluation/3features` :

```
Rscript performance_curve.R
```


## Author & Contact
- **Yu Bin (Gary) Chen**  
  - The University of Texas Health Science Center at Houston (UTHealth)  
  - Email: [yu.bin.chen@uth.tmc.edu](mailto:yu.bin.chen@uth.tmc.edu)  
  - GitHub: [@ychen45edu](https://github.com/your-username)

- **Tru Cao**  
  - The University of Texas Health Science Center at Houston (UTHealth)  
  - Email: [tru.cao@uth.tmc.edu](mailto:tru.cao@uth.tmc.edu)  

For questions regarding database schemas, scripts, or reproducibility requests, please open an issue in this repository or contact the author directly.
