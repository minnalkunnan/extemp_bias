# Speaking Order Bias In Extemporaneous Speaking

This project studies whether speaking order is associated with judge-assigned rank in extemporaneous speaking rounds collected from Tabroom ballot pages. The main version of the analysis now uses a standardized California championship-path sample across six seasons, built from CHSSA state championships, CHSSA state qualifiers, and NSDA district national-qualifier tournaments.

## Results

The current standardized analysis finds **no clear speaking-order bias**. Later speakers do not show a statistically reliable advantage, earlier speakers do not show a statistically reliable advantage, and the quadratic model does not reach conventional significance for edge effects.

Hypothesis test framing:
- Null hypothesis (`H0`): speaking order is not associated with judge-assigned rank in this sample.
- Alternative hypothesis (`H1`): speaking order is associated with judge-assigned rank in this sample.
- Linear test result: the normalized-position coefficient is `-0.0632` with `p = 0.2294`, so at conventional significance thresholds we **fail to reject the null hypothesis** for a linear primacy or recency effect.
- Quadratic test result: the normalized-position-squared coefficient is `-0.3352` with `p = 0.0635`, so we also **fail to reject the null hypothesis** for a curved or edge-effect pattern at the 0.05 level.
- Interpretation: average ranks vary across exact speaking slots, but the overall early-to-late pattern is not statistically reliable in the standardized sample.

Model evidence:
- Linear normalized-position slope: `-0.0632` with `p = 0.2294`
- Quadratic normalized-position-squared term: `-0.3352` with `p = 0.0635`
- Linear model `R^2 = 0.0001`
- Quadratic model `R^2 = 0.0004`

Key sample stats:
- 8 tournaments
- 1,773 unique judge panels
- 1,247 judges
- 11,327 competitor-by-judge observations

### Figure 1. Mean Rank by Raw Speaking Position

![Figure 1. Mean rank by raw speaking position](figures/mean_rank_by_position.png)

X-axis: exact speaking slot within a panel, such as 1st speaker, 2nd speaker, and so on. Y-axis: mean judge-assigned rank, where lower rank is better. This shows the average result at each literal speaking position.

### Figure 2. Mean Rank by Normalized Speaking Position

![Figure 2. Mean rank by normalized speaking position](figures/mean_rank_by_normalized_position.png)

X-axis: normalized speaking position from 0 to 1, where 0 is the earliest speaker in a panel and 1 is the latest. Y-axis: mean judge-assigned rank, where lower rank is better. Blue points trace the binned averages, and the red line is the fitted linear trend.

### Figure 3. Early, Middle, and Late Speaking Positions

![Figure 3. Early, middle, and late speaking positions](figures/early_middle_late_comparison.png)

X-axis: grouped speaking-order bins. `early` means normalized position `0.00-0.33`, `middle` means `0.33-0.66`, and `late` means `0.66-1.00`. Y-axis: mean judge-assigned rank, where lower rank is better. This gives a simple grouped comparison instead of exact slot-by-slot averages.

### Figure 4. Quadratic Model Prediction Curve

![Figure 4. Quadratic model prediction curve](figures/model_prediction_curve.png)

X-axis: normalized speaking position from earliest to latest. Y-axis: predicted rank from the quadratic model, where lower rank is better. In plain terms, this asks whether the first or last speakers look unusually advantaged or disadvantaged relative to the middle, rather than assuming the pattern is a straight line.

### Figure 5. Panel Size Distribution

![Figure 5. Panel size distribution](figures/panel_size_distribution.png)

X-axis: panel size, meaning the number of competitors in a judge panel. Y-axis: observation count in the cleaned dataset. This shows how much of the analysis comes from 4-speaker, 5-speaker, 6-speaker, 7-speaker, and 8-speaker panels.

## Methods

Each observation is a competitor-by-judge row from a Tabroom round-results ballot page. Panels were kept only when speaking positions were numeric, started at 1, were complete within the panel, and had no duplicate competitors inside the same `tournament + event + round_id + judge` panel.

Interpretation rules:
- Lower rank = better
- Negative slope on normalized position suggests recency bias
- Positive slope suggests primacy bias
- A meaningful quadratic term suggests edge effects

Current model summary:
- Linear slope on normalized position: `-0.0632`, `p = 0.2294`
- Quadratic term on normalized position squared: `-0.3352`, `p = 0.0635`

## Files

- `01_candidate_pages.md`: standardized extemp round-results pages included in the search frame
- `03_cleaned_data.csv`: cleaned analysis dataset
- `03_model_results.csv`: regression outputs
- `03_analysis_summary.md`: concise results summary
- `figures/`: analysis figures used in the README and site
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
git add .
git commit -m "Update project to standardized extemp sample"
git push -u origin main
```

Then enable GitHub Pages in the repository settings and set the source to deploy from the `main` branch, `/site` folder.

## Tournaments Surveyed

These are the tournaments that actually contributed usable round-level extemp data to the standardized analysis.

### 2025-26

- `state_qual`: SCDL State Quals SPEECH. Rounds retained: Finals, Semis, Round 1, Round 2, Round 3.
- `nat_qual`: Southern California District Tournament. Rounds retained: Finals, Semifinals, Round 1, Round 2, Round 3.
- `nat_qual`: East Los Angeles District Tournament. Rounds retained: Final, SemisB, RD1B, RD2B, RD3B.

### 2024-25

- `state`: California High School Speech Association State Championship. Rounds retained: Finals, Semis, Round 1, Round 2, Round 3.
- `state_qual`: GGSA State Quals. Rounds retained: Semi-Finals, Round 1, Round 2, Round 3.
- `state_qual`: CHSSA CVFL Speech Quals Mira Loma. Rounds retained: Finals, Round 1, Round 2, Round 3.
- `nat_qual`: Southern California District Tournament. Rounds retained: Finals, Semifinals, Round 1, Round 2, Round 3.
- `nat_qual`: East Los Angeles District Tournament. Rounds retained: FINAL, SEMI, RD1, RD2, RD3.

### 2023-24

- `state`: California High School Speech Association State Championship. Rounds retained: Finals, Semis, Round 1, Round 2, Round 3.
- `state_qual`: GGSA State Quals. Rounds retained: Semi-Finals, Round 1, Round 2, Round 3.
- `state_qual`: CFL Speech CHSSA State Quals. Rounds retained: Finals, Round 1, Round 2, Round 3.
- `state_qual`: CVFL CHSSA Speech Qualifier Ponderosa. Rounds retained: Finals, Round 1, Round 2, Round 3.
- `nat_qual`: Southern California District Tournament. Rounds retained: Final or Finals, Semifinals, Round 1, Round 2, Round 3.
- `nat_qual`: East Los Angeles District Tournament. Rounds retained: Final, Semis, RD 1, RD 2, RD 3.

### 2022-23

- `state`: California High School Speech Association State Championship. Rounds retained: Finals, Semis, Round 1, Round 2, Round 3.
- `state_qual`: GGSA State Quals. Rounds retained: Semi-Finals, Round 1, Round 2, Round 3.
- `nat_qual`: Southern California District Tournament. Rounds retained: Finals, Round 1, Round 2, Round 3.
- `nat_qual`: East Los Angeles District Tournament. Rounds retained: Finals, SEMI B, RD 1B, RD 2B, RD 3B.

### 2021-22

- `state`: California High School Speech Association State Championship. Rounds retained: Finals, Semis, Round 1, Round 2, Round 3, Round 4.
- `state_qual`: GGSA State Quals. Rounds retained: Semi-Finals, Round 1, Round 2, Round 3.
- `nat_qual`: Southern California District Tournament. Rounds retained: Finals, Semifinals, Round 1, Round 2, Round 3.

### 2020-21

- `state`: California High School Speech Association State Championship. Rounds retained: Finals, Semis, Round 1, Round 2, Round 3, Round 4.
- `nat_qual`: Southern California District Tournament. Rounds retained: Finals, Semi Final or Semis, Round 1, Round 2, Round 3.

Search universe but not retained in the final cleaned sample:
- `2025-26 state`: California High School Speech Association State Championship was in the search universe, but the extemp results pages available in this pass did not yield usable posted `round_results` links.
- `2019-20 nat_qual`: Southern California District Tournament appeared in the search universe, but its extemp events did not produce usable posted `round_results` links in this pass.
- `2019-20 nat_qual`: East Los Angeles District Tournament appeared in the search universe, but its extemp events did not produce usable posted `round_results` links in this pass.
- `2020-21 nat_qual`: East Los Angeles District Tournament appeared in the search universe, but its extemp events did not produce usable posted `round_results` links in this pass.
- `2021-22 nat_qual`: East Los Angeles District Tournament appeared in the search universe, but its extemp events did not produce usable posted `round_results` links in this pass.
