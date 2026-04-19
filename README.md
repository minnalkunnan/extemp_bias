# Speaking Order Bias In Extemporaneous Speaking

This project studies whether speaking order is associated with judge-assigned rank in extemporaneous speaking rounds collected from Tabroom ballot pages tied to a Gabrielino-attended tournament set.

## Results

The current analysis suggests a small **primacy bias**: earlier speakers tended to receive slightly better ranks on average. The effect is statistically detectable in the linear model, but the overall explained variance is still small.

### Figure 1. Mean Rank by Raw Speaking Position

![Mean rank by speaking position](figures/mean_rank_by_position.png)

X-axis: raw speaking position within a panel, such as 1st speaker, 2nd speaker, and so on. Y-axis: mean judge-assigned rank, where lower rank is better. This figure shows the average outcome at each exact speaking slot.

### Figure 2. Mean Rank by Normalized Speaking Position

![Mean rank by normalized position](figures/mean_rank_by_normalized_position.png)

X-axis: normalized speaking position from 0 to 1, where 0 is the earliest speaker in a panel and 1 is the latest. Y-axis: mean judge-assigned rank, where lower rank is better. The blue series shows average rank by position band, and the red line is the fitted linear trend.

### Figure 3. Early vs. Middle vs. Late Speaking Positions

![Early middle late comparison](figures/early_middle_late_comparison.png)

X-axis: grouped speaking-order bins: early, middle, and late. Y-axis: mean judge-assigned rank, where lower rank is better. This figure is the clearest grouped comparison of whether earlier or later speaking slots tend to do better.

### Figure 4. Quadratic Model Prediction Curve

![Quadratic model prediction curve](figures/model_prediction_curve.png)

X-axis: normalized speaking position from earliest to latest. Y-axis: predicted rank from the quadratic model, where lower rank is better. This graph shows whether the fitted relationship bends at the edges instead of following only a straight-line trend.

### Figure 5. Panel Size Distribution

![Panel size distribution](figures/panel_size_distribution.png)

X-axis: panel size, meaning the number of competitors in a judge panel. Y-axis: number of observations in the cleaned dataset. This figure shows how much of the analysis comes from smaller versus larger extemp panels.

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
