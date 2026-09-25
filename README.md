## Tangram Loss Sensitivity Analysis

This repository contains code and notebooks for a systematic sensitivity analysis of the Tangram loss function, based on a PyTorch Lightning reimplementation available at:

[https://github.com/enric-bazz/tangramlit_dev](https://github.com/enric-bazz/tangramlit_dev)

The project focuses on:

* Ablation studies of individual loss terms.
* Experiments driven by predefined training schedules and configuration files.
* Evaluation of configurations obtained via Optuna hyperparameter optimization.

Utilities are provided for:

* Aggregating experiment outputs.
* Inspecting metrics.
* Generating comparative plots across configurations.

---

## Repository Structure

the repo is meant to be run on exact environment specificties with UV and the lock file.

### `src/` ## wrong, it is not a pavkage anymore, just scripts in two folders /ablation_study and optuna_study which build on top of the tangramlit package

Source code for:

* Configurable training pipelines.
* Loss term ablation and extension experiments.
* Integration with Optuna-based hyperparameter optimization.

the optuna_study contains scrpts to run optuna hyperparam studies on one of the datasets 1-5, compute paraemter importance and create fANOVA plots (etc.)

### `notebooks/merfish_whole_mouse_brain_atlas/`

Analysis notebooks for:

* Post hoc evaluation of Tangram experiments.
* Visualization and comparison of loss configurations.
* Sensitivity analysis summaries.

### dataset (this one)

### `notebooks/ablation_study/trainval/`

Notebooks for:

* Model training and validation on the datasets used in the study.
* Reproducible experiment execution with specific schedules and configurations.

### `notebooks/ablation_study/data/`

Full preprocessing pipelines for:

* Spatial transcriptomics datasets.
* Corresponding single-cell RNA-seq references.

---

## Datasets (ablation)

The following dataset pairs were used in the study.

### 1. seqFISH + 10x Chromium

* seqFISH: “SpatialMouseAtlas2020”
  [https://content.cruk.cam.ac.uk/jmlab/SpatialMouseAtlas2020/](https://content.cruk.cam.ac.uk/jmlab/SpatialMouseAtlas2020/)

* 10x Chromium: “Sample 21” in *MouseGastrulationData* (Bioconductor)
  [https://bioconductor.org/packages/MouseGastrulationData/](https://bioconductor.org/packages/MouseGastrulationData/)

---

### 2. seqFISH + 10x Chromium

* seqFISH supplementary data
  [https://ars.els-cdn.com/content/image/1-s2.0-S0896627316307024-mmc6.xlsx](https://ars.els-cdn.com/content/image/1-s2.0-S0896627316307024-mmc6.xlsx)

* 10x Chromium: “HIPP_sc_Rep1_10X” in GEO accession GSE158450
  [https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE158450](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE158450)

---

### 3. MERFISH + 10x Chromium

* MERFISH: Female parent mouse, animal ID 18
  [https://datadryad.org/stash/dataset/doi:10.5061/dryad.8t8s248](https://datadryad.org/stash/dataset/doi:10.5061/dryad.8t8s248)

* 10x Chromium: GEO accession GSE113576
  [https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE113576](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE113576)

---

### 4. MERFISH + 10x Chromium

* MERFISH: “mouse1_slice162”
  [https://caltech.box.com/shared/static/dzqt6ryytmjbgyai356s1z0phtnsbaol.gz](https://caltech.box.com/shared/static/dzqt6ryytmjbgyai356s1z0phtnsbaol.gz)

* 10x Chromium (BICCN, Zeng lab)
  [https://data.nemoarchive.org/biccn/lab/zeng/transcriptome/scell/10x_v3/mouse/processed/analysis/10X_cells_v3_AIBS/](https://data.nemoarchive.org/biccn/lab/zeng/transcriptome/scell/10x_v3/mouse/processed/analysis/10X_cells_v3_AIBS/)

---

### 5. MERFISH + Smart-seq

* MERFISH: “SpaceTx - Spacejam2”
  [https://github.com/spacetx-spacejam/data/](https://github.com/spacetx-spacejam/data/)

* Smart-seq reference
  [https://portal.brain-map.org/](https://portal.brain-map.org/)

---

## Scope and Reproducibility

The repository is designed to:

* Reproduce all ablation and addition experiments from configuration files.
* Support controlled sensitivity analyses of Tangram’s loss terms.
* Compare baseline and Optuna-optimized configurations under identical training conditions.

All preprocessing steps required to regenerate the training-ready datasets are provided in the corresponding notebooks.

---



