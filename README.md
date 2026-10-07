# GEO Datasets Recommendation System: An Integrated Database Approach

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Database: SQLite3](https://img.shields.io/badge/Database-SQLite3-lightgrey.svg)](https://www.sqlite.org/)

---

## Table of Contents
- [Overview](#overview)
- [Authors & Contact](#authors--contact)

---

## Overview

Finding relevant genomic datasets within public repositories like NCBI GEO often requires manual, keyword-based queries that overlook latent semantic relationships between studies. This framework formulates dataset retrieval as a recommendation problem:

- **Entity Integration:** Disambiguates author entities across GEO and PubMed records using contact email mapping, affiliation parsing, and SVM classifiers.
- **Multi-Field Content Filtering:** Calculates item-item similarity vectors using text metadata combinations (Title, Summary, Overall Design, Experiment Type, and Organism).
- **Metric Aggregation:** Evaluates Min, Max, and Average pooling aggregation functions over 3-field and 5-field configurations to score candidate datasets against historical author profiles.

---


## Workflow & Execution

Follow these three sequential steps to build the database, populate all tables, and generate author recommendations.

### Step 1: Initialize the Empty Database
Run `database_construction.py` to create `sample.db` and initialize the relational schema (`author`, `series`, `author_series`, etc.):

### Step 2: Import Data Tables
Import all processed table files from the `data/` directory into the initialized SQLite database:

### Step 3: Run the Recommendation Pipeline
Execute `recommendation.py` to compute multi-feature similarities and export the candidate recommendation results:


## Author & Contact
- **Yu Bin (Gary) Chen**  
  - The University of Texas Health Science Center at Houston (UTHealth)  
  - Email: [yu.bin.chen@uth.tmc.edu](mailto:yu.bin.chen@uth.tmc.edu)  
  - GitHub: [@ychen45edu](https://github.com/your-username)

- **Tru Cao**  
  - The University of Texas Health Science Center at Houston (UTHealth)  
  - Email: [tru.cao@uth.tmc.edu](mailto:tru.cao@uth.tmc.edu)  

For questions regarding database schemas, scripts, or reproducibility requests, please open an issue in this repository or contact the author directly.
