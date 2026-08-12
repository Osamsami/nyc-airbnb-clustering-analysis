# Data Directory

This directory contains the CSV datasets used by the clustering notebook
(`notebooks/notebooks_03_clustering.ipynb`) and the Streamlit demo
(`app.py`).

| File | Size | Description | Regenerable? |
|---|---|---|---|
| `airbnb_cleaned.csv` | ~8 MB | Cleaned NYC Airbnb 2019 listings (missing values handled, `log_price` added). This is the notebook's starting point. | No upstream raw source file is checked into this repo — this is the earliest available snapshot. |
| `airbnb_with_clusters.csv` | ~8 MB | `airbnb_cleaned.csv` plus a `cluster` column (0–3) assigned by the K-Means model. | Yes — produced by running `notebooks/notebooks_03_clustering.ipynb` end-to-end (see the final "Final Output" cell, which writes this file). |

## Why these CSVs are committed directly to git (not Git LFS)

Issue #7 flagged that large CSVs shouldn't be committed directly to git.
For this repo, we evaluated the alternatives and are keeping both files
tracked as plain, non-LFS blobs:

- **Size is modest in absolute terms.** Both files are ~8 MB — well under
  GitHub's 50 MB "you should think about this" warning and 100 MB hard
  limit. Git LFS exists to solve problems (huge repos, frequent large
  binary churn) that don't apply here: this is a small, mostly-static
  portfolio-analysis repo, not a monorepo with gigabytes of assets.
- **Introducing Git LFS adds real friction for a project this size** —
  contributors and CI need `git-lfs` installed, LFS has its own storage/
  bandwidth quota on GitHub, and clone/checkout tooling gets more complex —
  for a benefit (repo-size savings) that's marginal at ~16 MB total.
- **`airbnb_with_clusters.csv` is regenerable** by running the notebook,
  but is also kept committed (rather than gitignored) so the Streamlit demo
  (`app.py`) and CI smoke test (`scripts/smoke_test.py`) work immediately
  after `git clone` without requiring a full notebook run first — important
  for a portfolio project where reviewers should be able to try the demo
  in seconds.
- **`airbnb_cleaned.csv` is not regenerable from anything else in the
  repo** (no raw source file is included), so removing it would destroy
  the only copy of the cleaned input data with no way to recreate it.

If this repo's scope grows significantly (e.g. many large raw datasets,
frequent binary updates), Git LFS should be revisited.
