# Speaking Order Bias In Extemporaneous Speaking

This project studies whether speaking order is associated with judge-assigned rank in extemporaneous speaking rounds collected from Tabroom ballot pages tied to a Gabrielino-attended tournament set.

## Data Source

The source data comes from Tabroom round-results ballot pages that include competitor names, judges, speaking order, and ranks.

## What Was Measured

- Speaking position within a judge panel
- Judge-assigned rank, where lower rank is better
- Normalized speaking position and early / middle / late bins

## How To Interpret Results

- Negative slope on normalized position suggests recency bias
- Positive slope suggests primacy bias
- A meaningful quadratic term suggests edge effects

Current high-level result: **primacy bias**.

## Files

- `02_gabrielino_raw_round_data.csv`: extracted raw competitor-by-judge rows
- `03_cleaned_data.csv`: cleaned analysis dataset
- `03_model_results.csv`: regression outputs
- `03_analysis_summary.md`: concise results summary
- `figures/`: analysis figures
- `site/`: GitHub Pages-ready static site

## View The Site Locally

```bash
cd /Users/minnalkunnan/Desktop/research/extemp_analysis
python -m http.server 8000
```

Then open `http://localhost:8000/site/`.

## Publish With GitHub Pages

```bash
cd /Users/minnalkunnan/Desktop/research/extemp_analysis
git init
git add .
git commit -m "Add speaking-order bias analysis site"
git branch -M main
git remote add origin <YOUR_REPO_URL>
git push -u origin main
```

Then enable GitHub Pages in the repository settings and set the source to deploy from the `main` branch, `/site` folder if using a Pages action or the root branch if you publish the built site as configured in your repo workflow.
