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


## Workflow & Execution

Follow these four sequential steps to build the database, populate all tables, generate author recommendations, and export the evaluation figures.

### Step 1: Data Download & Preparation
Because the raw NCBI GEO (`gse_html/`) and PubMed (`pub_html/`) HTML datasets exceed GitHub's single-file size limits, they are hosted as split `tar.gz` archives under the [**`v1.0-data` Release**](https://github.com/ychen45edu/GEO-Datasets-Recommendation-System/releases/tag/v1.0-data).

1. **Download all archive assets** (`gse_html.tar.gz.part_aa`, `pub_html.tar.gz.part_aa`, and `pub_html.tar.gz.part_ab`) from the [`v1.0-data` Release page](https://github.com/ychen45edu/GEO-Datasets-Recommendation-System/releases/tag/v1.0-data).

3. **Reassemble and extract** both archives directly into the repository's `data/` directory:

```bash
# Extract into ./GEO-Datasets-Recommendation-System/data/gse_html/
cat gse_html.tar.gz.part_* | tar -xzvf - -C ./GEO-Datasets-Recommendation-System/data/gse_html

# Extract into ./GEO-Datasets-Recommendation-System/data/pub_html/
cat pub_html.tar.gz.part_* | tar -xzvf - -C ./GEO-Datasets-Recommendation-System/data/pub_html
```


### Step 2: Initialize the Empty Database
Run `database_construction.py` to create `sample.db` and initialize the relational schema (`author`, `series`, `author_series`, etc.):

```bash
python database_construction.py
```

### Step 3: Import Data Tables
Run `import_table.py` to import all processed table files from the `data/` directory into the initialized SQLite database:

```bash
python import_table.py
```

### Step 4: Run the Recommendation Pipeline
Execute `recommendation.py` to compute multi-feature similarities and export the candidate recommendation results:

```bash
python recommendation.py
```

### Step 5: Evaluate Results & Export Figures
Run `evaluation.R` to evaluate model performance and export the publication figures:

```bash
Rscript evaluation.R
```

This script exports the following figures:
- **Figure 1:** A histogram of the number of GEO datasets used by an author.
- **Figure 2:** Performance diagrams using five data fields; $\alpha$ is the similarity threshold for which $F_1$ is maximal, with the corresponding recall $R$ and precision $P$.
- **Figure 3:** Performance diagrams using three data fields; $\alpha$ is the similarity threshold for which $F_1$ is maximal, with the corresponding recall $R$ and precision $P$.


## Author & Contact
- **Yu Bin (Gary) Chen**  
  - The University of Texas Health Science Center at Houston (UTHealth)  
  - Email: [yu.bin.chen@uth.tmc.edu](mailto:yu.bin.chen@uth.tmc.edu)  
  - GitHub: [@ychen45edu](https://github.com/your-username)

- **Tru Cao**  
  - The University of Texas Health Science Center at Houston (UTHealth)  
  - Email: [tru.cao@uth.tmc.edu](mailto:tru.cao@uth.tmc.edu)  

For questions regarding database schemas, scripts, or reproducibility requests, please open an issue in this repository or contact the author directly.
