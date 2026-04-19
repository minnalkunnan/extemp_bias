# Analysis Summary

Key result: **primacy bias**.

Lower rank is better throughout this analysis.

## Descriptive Statistics

- Tournaments: 7
- Unique panels: 435
- Judges: 360
- Total observations: 2589
- Panel size distribution:
  - 3: 9
  - 4: 44
  - 5: 355
  - 6: 1614
  - 7: 567
- Counts by season and tournament:
  - 2022-23 | Jack Howe Memorial Tournament: 361
  - 2022-23 | La Reina Invitational: 69
  - 2024-25 | 39th Annual Stanford Invitational: 706
  - 2024-25 | East Los Angeles NSDA 2025 Nat Quals Speech: 288
  - 2024-25 | Gabrielino Screamin Eagles GAB GAB GAB Speech Invitational: 195
  - 2024-25 | Jack Howe Memorial Tournament: 244
  - 2025-26 | East Los Angeles NSDA 2026 Nat Quals Speech: 282
  - 2025-26 | Gabrielino Screamin Eagles GAB GAB GAB Speech Invitational: 195
  - 2025-26 | SCDL State Quals SPEECH: 249

## Mean Rank Patterns

- Mean rank by speaking position:
  - Position 1: mean rank 3.441 across 435 observations
  - Position 2: mean rank 3.216 across 435 observations
  - Position 3: mean rank 3.430 across 435 observations
  - Position 4: mean rank 3.664 across 432 observations
  - Position 5: mean rank 3.546 across 421 observations
  - Position 6: mean rank 3.677 across 350 observations
  - Position 7: mean rank 4.432 across 81 observations
- Mean rank by early/middle/late bins:
  - early: mean rank 3.346 across 856 observations
  - late: mean rank 3.632 across 948 observations
  - middle: mean rank 3.571 across 785 observations

## Models

- Linear model `rank ~ normalized_position`: slope = 0.3000, p ≈ 0.0030, R² = 0.0034
- Quadratic model `rank ~ normalized_position + normalized_position^2`: linear term = 0.1823, quadratic term = 0.1177, quadratic p ≈ 0.7333, R² = 0.0034

## Interpretation

Earlier speakers tend to receive better ranks on average, which is consistent with primacy bias.

## Limitations

- Judge heterogeneity remains substantial, and the optional mixed-effects model was not fit in this environment.
- Speaking order may not be randomly assigned.
- The tournament sample is restricted to the Gabrielino-attended set already collected.
