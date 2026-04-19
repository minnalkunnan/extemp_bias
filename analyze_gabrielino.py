from __future__ import annotations

import csv
import math
import os
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean

import numpy as np


BASE = Path("/Users/minnalkunnan/Desktop/research/extemp_analysis")
RAW_CSV = BASE / "02_gabrielino_raw_round_data.csv"
CLEAN_CSV = BASE / "03_cleaned_data.csv"
MODEL_CSV = BASE / "03_model_results.csv"
SUMMARY_MD = BASE / "03_analysis_summary.md"
FIG_DIR = BASE / "figures"
SITE_DIR = BASE / "site"
README = BASE / "README.md"


@dataclass
class OLSResult:
    name: str
    terms: list[str]
    coefficients: list[float]
    std_errors: list[float]
    t_stats: list[float]
    p_values: list[float]
    r_squared: float
    n: int
    df_resid: int
    sigma2: float


def normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def parse_float(value: str) -> float | None:
    try:
        return float(value)
    except Exception:
        return None


def load_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with RAW_CSV.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            rank = parse_float(row["rank"])
            speaking_position = parse_float(row["speaking_position"])
            if rank is None or speaking_position is None:
                continue
            row["rank"] = rank
            row["speaking_position"] = speaking_position
            rows.append(row)
    return rows


def clean_data(rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], dict[str, object]]:
    panels: dict[tuple[str, str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        panel = (
            str(row["tournament"]),
            str(row["event"]),
            str(row["round_id"]),
            str(row["judge"]),
        )
        panels[panel].append(row)

    cleaned: list[dict[str, object]] = []
    excluded_panels: list[tuple[tuple[str, str, str, str], str]] = []

    for panel_key, panel_rows in panels.items():
        positions = [int(r["speaking_position"]) for r in panel_rows]
        uniq_positions = sorted(set(positions))
        names = [str(r["competitor_name"]).strip() for r in panel_rows]

        if len(set(names)) != len(names):
            excluded_panels.append((panel_key, "duplicate competitor_name within panel"))
            continue

        if uniq_positions != list(range(1, len(uniq_positions) + 1)):
            excluded_panels.append((panel_key, "speaking positions not complete from 1"))
            continue

        if len(panel_rows) != len(uniq_positions):
            excluded_panels.append((panel_key, "row count does not match unique speaking positions"))
            continue

        panel_size = len(panel_rows)
        for row in sorted(panel_rows, key=lambda r: int(r["speaking_position"])):
            row = dict(row)
            row["rank"] = float(row["rank"])
            row["speaking_position"] = int(row["speaking_position"])
            row["panel_size"] = panel_size
            if panel_size > 1:
                normalized = (row["speaking_position"] - 1) / (panel_size - 1)
            else:
                normalized = 0.0
            row["normalized_position"] = normalized
            if normalized <= 0.33:
                pos_bin = "early"
            elif normalized <= 0.66:
                pos_bin = "middle"
            else:
                pos_bin = "late"
            row["position_bin"] = pos_bin
            cleaned.append(row)

    stats = {
        "raw_rows": len(rows),
        "clean_rows": len(cleaned),
        "raw_panels": len(panels),
        "clean_panels": len({(r["tournament"], r["event"], r["round_id"], r["judge"]) for r in cleaned}),
        "excluded_panels": excluded_panels,
    }
    return cleaned, stats


def save_cleaned(rows: list[dict[str, object]]) -> None:
    fieldnames = [
        "season_year",
        "tournament",
        "event",
        "round",
        "round_id",
        "judge",
        "section_or_room",
        "competitor_name",
        "school",
        "speaking_position",
        "rank",
        "source_url",
        "position_source",
        "panel_size",
        "normalized_position",
        "position_bin",
    ]
    with CLEAN_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            out = dict(row)
            out["normalized_position"] = f"{float(out['normalized_position']):.6f}"
            out["rank"] = f"{float(out['rank']):.6f}"
            writer.writerow(out)


def ols_fit(name: str, y: np.ndarray, x_cols: list[np.ndarray], terms: list[str]) -> OLSResult:
    X = np.column_stack([np.ones(len(y))] + x_cols)
    beta, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    fitted = X @ beta
    resid = y - fitted
    n = len(y)
    p = X.shape[1]
    df_resid = n - p
    sse = float(np.sum(resid ** 2))
    sst = float(np.sum((y - np.mean(y)) ** 2))
    sigma2 = sse / df_resid if df_resid > 0 else float("nan")
    xtx_inv = np.linalg.inv(X.T @ X)
    cov = sigma2 * xtx_inv if math.isfinite(sigma2) else np.full_like(xtx_inv, np.nan)
    se = np.sqrt(np.diag(cov))
    t_stats = beta / se
    p_values = [2 * (1 - normal_cdf(abs(float(t)))) for t in t_stats]
    r2 = 1 - sse / sst if sst else float("nan")
    return OLSResult(
        name=name,
        terms=["intercept"] + terms,
        coefficients=[float(x) for x in beta],
        std_errors=[float(x) for x in se],
        t_stats=[float(x) for x in t_stats],
        p_values=[float(x) for x in p_values],
        r_squared=float(r2),
        n=n,
        df_resid=df_resid,
        sigma2=float(sigma2),
    )


def save_model_results(results: list[OLSResult]) -> None:
    with MODEL_CSV.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["model", "term", "coefficient", "std_error", "t_stat", "p_value", "r_squared", "n", "df_resid"]
        )
        for res in results:
            for i, term in enumerate(res.terms):
                writer.writerow(
                    [
                        res.name,
                        term,
                        f"{res.coefficients[i]:.8f}",
                        f"{res.std_errors[i]:.8f}",
                        f"{res.t_stats[i]:.8f}",
                        f"{res.p_values[i]:.8f}",
                        f"{res.r_squared:.8f}",
                        res.n,
                        res.df_resid,
                    ]
                )


def aggregate_mean(rows: list[dict[str, object]], key_fn) -> list[tuple[object, float, int]]:
    buckets: dict[object, list[float]] = defaultdict(list)
    for row in rows:
        buckets[key_fn(row)].append(float(row["rank"]))
    out = []
    for key in sorted(buckets, key=lambda x: (x if not isinstance(x, tuple) else x[0])):
        vals = buckets[key]
        out.append((key, mean(vals), len(vals)))
    return out


def write_ppm(path: Path, width: int, height: int, pixels: list[list[tuple[int, int, int]]]) -> None:
    with path.open("wb") as f:
        f.write(f"P6\n{width} {height}\n255\n".encode("ascii"))
        for row in pixels:
            for r, g, b in row:
                f.write(bytes((r, g, b)))


def blank_canvas(width: int, height: int, color=(255, 255, 255)):
    return [[color for _ in range(width)] for _ in range(height)]


FONT = {
    "0": ["111", "101", "101", "101", "111"],
    "1": ["010", "110", "010", "010", "111"],
    "2": ["111", "001", "111", "100", "111"],
    "3": ["111", "001", "111", "001", "111"],
    "4": ["101", "101", "111", "001", "001"],
    "5": ["111", "100", "111", "001", "111"],
    "6": ["111", "100", "111", "101", "111"],
    "7": ["111", "001", "010", "010", "010"],
    "8": ["111", "101", "111", "101", "111"],
    "9": ["111", "101", "111", "001", "111"],
    ".": ["000", "000", "000", "000", "010"],
    "-": ["000", "000", "111", "000", "000"],
    "(": ["001", "010", "010", "010", "001"],
    ")": ["100", "010", "010", "010", "100"],
    "=": ["000", "111", "000", "111", "000"],
    ":": ["000", "010", "000", "010", "000"],
    "/": ["001", "001", "010", "100", "100"],
    ",": ["000", "000", "000", "010", "100"],
    " ": ["000", "000", "000", "000", "000"],
}


def draw_rect(pix, x0, y0, x1, y1, color):
    h = len(pix)
    w = len(pix[0])
    for y in range(max(0, y0), min(h, y1)):
        row = pix[y]
        for x in range(max(0, x0), min(w, x1)):
            row[x] = color


def draw_line(pix, x0, y0, x1, y1, color, thickness=1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        draw_rect(pix, x0 - thickness, y0 - thickness, x0 + thickness + 1, y0 + thickness + 1, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def draw_char(pix, x, y, ch, color=(0, 0, 0), scale=2):
    pat = FONT.get(ch.upper())
    if pat is None:
        pat = FONT[" "]
    for ry, row in enumerate(pat):
        for rx, bit in enumerate(row):
            if bit == "1":
                draw_rect(pix, x + rx * scale, y + ry * scale, x + (rx + 1) * scale, y + (ry + 1) * scale, color)


def draw_text(pix, x, y, text, color=(0, 0, 0), scale=2):
    cx = x
    for ch in text:
        draw_char(pix, cx, y, ch, color=color, scale=scale)
        cx += 4 * scale


def ppm_to_png(ppm_path: Path, png_path: Path) -> None:
    subprocess.run(["/usr/bin/sips", "-s", "format", "png", str(ppm_path), "--out", str(png_path)], check=True, capture_output=True)
    ppm_path.unlink(missing_ok=True)


def save_chart(path: Path, title: str, subtitle: str, x_label: str, y_label: str, x_vals, y_vals, kind="line", y_fit=None):
    FIG_DIR.mkdir(exist_ok=True)
    width, height = 1000, 700
    pix = blank_canvas(width, height)
    left, right, top, bottom = 110, 40, 90, 110
    plot_w = width - left - right
    plot_h = height - top - bottom
    draw_text(pix, 20, 20, title[:60], scale=3)
    draw_text(pix, 20, 55, subtitle[:90], scale=2)
    draw_line(pix, left, height - bottom, width - right, height - bottom, (0, 0, 0), thickness=1)
    draw_line(pix, left, top, left, height - bottom, (0, 0, 0), thickness=1)

    x_min = min(x_vals)
    x_max = max(x_vals)
    if x_min == x_max:
        x_min -= 0.5
        x_max += 0.5
    y_min = min(y_vals if y_fit is None else list(y_vals) + list(y_fit))
    y_max = max(y_vals if y_fit is None else list(y_vals) + list(y_fit))
    pad = (y_max - y_min) * 0.1 if y_max > y_min else 1.0
    y_min -= pad
    y_max += pad

    def map_x(x):
        return int(left + (x - x_min) / (x_max - x_min) * plot_w)

    def map_y(y):
        return int(height - bottom - (y - y_min) / (y_max - y_min) * plot_h)

    for frac in [0.0, 0.25, 0.5, 0.75, 1.0]:
        yv = y_min + frac * (y_max - y_min)
        yp = map_y(yv)
        draw_line(pix, left, yp, width - right, yp, (225, 225, 225))
        draw_text(pix, 10, yp - 6, f"{yv:.2f}"[:8], scale=2)

    if kind == "bar":
        n = len(x_vals)
        for i, (xv, yv) in enumerate(zip(x_vals, y_vals)):
            x0 = left + int((i + 0.15) / n * plot_w)
            x1 = left + int((i + 0.85) / n * plot_w)
            y0 = map_y(yv)
            draw_rect(pix, x0, y0, x1, height - bottom, (79, 129, 189))
            draw_text(pix, x0 + 10, height - bottom + 15, str(xv)[:10], scale=2)
    else:
        pts = [(map_x(x), map_y(y)) for x, y in zip(x_vals, y_vals)]
        for i, (xp, yp) in enumerate(pts):
            draw_rect(pix, xp - 4, yp - 4, xp + 5, yp + 5, (79, 129, 189))
            if i > 0:
                draw_line(pix, pts[i - 1][0], pts[i - 1][1], xp, yp, (79, 129, 189), thickness=1)
        if y_fit is not None:
            fit_pts = [(map_x(x), map_y(y)) for x, y in zip(x_vals, y_fit)]
            for i in range(1, len(fit_pts)):
                draw_line(pix, fit_pts[i - 1][0], fit_pts[i - 1][1], fit_pts[i][0], fit_pts[i][1], (196, 78, 82), thickness=1)
        for xv in x_vals:
            xp = map_x(xv)
            draw_text(pix, xp - 10, height - bottom + 15, f"{xv:.2f}"[:4], scale=2)

    draw_text(pix, width // 2 - 100, height - 40, x_label[:45], scale=2)
    draw_text(pix, 10, top - 25, y_label[:45], scale=2)
    ppm = path.with_suffix(".ppm")
    write_ppm(ppm, width, height, pix)
    ppm_to_png(ppm, path)


def dataset_stats(rows: list[dict[str, object]]) -> dict[str, object]:
    tournaments = sorted({str(r["tournament"]) for r in rows})
    panels = {(str(r["tournament"]), str(r["event"]), str(r["round_id"]), str(r["judge"])) for r in rows}
    judges = sorted({str(r["judge"]) for r in rows})
    panel_sizes = Counter(int(r["panel_size"]) for r in rows)
    by_tourn = Counter(str(r["tournament"]) for r in rows)
    by_season = Counter(str(r["season_year"]) for r in rows)
    counts_by_ts = Counter((str(r["season_year"]), str(r["tournament"])) for r in rows)
    return {
        "n_tournaments": len(tournaments),
        "n_panels": len(panels),
        "n_judges": len(judges),
        "n_obs": len(rows),
        "panel_sizes": panel_sizes,
        "by_tournament": by_tourn,
        "by_season": by_season,
        "counts_by_tournament_season": counts_by_ts,
    }


def interpret_result(linear: OLSResult, quadratic: OLSResult) -> str:
    slope = linear.coefficients[1]
    p = linear.p_values[1]
    quad = quadratic.coefficients[2]
    quad_p = quadratic.p_values[2]
    if quad_p < 0.05:
        return "edge effects"
    if p < 0.05 and slope < 0:
        return "recency bias"
    if p < 0.05 and slope > 0:
        return "primacy bias"
    return "no clear speaking-order bias"


def write_summary(rows: list[dict[str, object]], stats: dict[str, object], linear: OLSResult, quadratic: OLSResult) -> str:
    mean_by_pos = aggregate_mean(rows, lambda r: int(r["speaking_position"]))
    mean_by_bin = aggregate_mean(rows, lambda r: str(r["position_bin"]))
    key_result = interpret_result(linear, quadratic)
    with SUMMARY_MD.open("w") as f:
        f.write("# Analysis Summary\n\n")
        f.write(f"Key result: **{key_result}**.\n\n")
        f.write("Lower rank is better throughout this analysis.\n\n")
        f.write("## Descriptive Statistics\n\n")
        f.write(f"- Tournaments: {stats['n_tournaments']}\n")
        f.write(f"- Unique panels: {stats['n_panels']}\n")
        f.write(f"- Judges: {stats['n_judges']}\n")
        f.write(f"- Total observations: {stats['n_obs']}\n")
        f.write("- Panel size distribution:\n")
        for size, count in sorted(stats["panel_sizes"].items()):
            f.write(f"  - {size}: {count}\n")
        f.write("- Counts by season and tournament:\n")
        for (season, tourn), count in sorted(stats["counts_by_tournament_season"].items()):
            f.write(f"  - {season} | {tourn}: {count}\n")
        f.write("\n## Mean Rank Patterns\n\n")
        f.write("- Mean rank by speaking position:\n")
        for pos, avg, n in mean_by_pos:
            f.write(f"  - Position {pos}: mean rank {avg:.3f} across {n} observations\n")
        f.write("- Mean rank by early/middle/late bins:\n")
        for pos_bin, avg, n in mean_by_bin:
            f.write(f"  - {pos_bin}: mean rank {avg:.3f} across {n} observations\n")
        f.write("\n## Models\n\n")
        f.write(f"- Linear model `rank ~ normalized_position`: slope = {linear.coefficients[1]:.4f}, p ≈ {linear.p_values[1]:.4f}, R² = {linear.r_squared:.4f}\n")
        f.write(f"- Quadratic model `rank ~ normalized_position + normalized_position^2`: linear term = {quadratic.coefficients[1]:.4f}, quadratic term = {quadratic.coefficients[2]:.4f}, quadratic p ≈ {quadratic.p_values[2]:.4f}, R² = {quadratic.r_squared:.4f}\n")
        f.write("\n## Interpretation\n\n")
        if key_result == "edge effects":
            f.write("The quadratic term is the clearest signal, suggesting performance differs at the edges of the speaking order rather than following a simple primacy or recency trend.\n")
        elif key_result == "recency bias":
            f.write("Later speakers tend to receive better ranks on average, which is consistent with recency bias.\n")
        elif key_result == "primacy bias":
            f.write("Earlier speakers tend to receive better ranks on average, which is consistent with primacy bias.\n")
        else:
            f.write("The cleaned dataset does not show a strong, clean monotonic speaking-order pattern in judge ranks.\n")
        f.write("\n## Limitations\n\n")
        f.write("- Judge heterogeneity remains substantial, and the optional mixed-effects model was not fit in this environment.\n")
        f.write("- Speaking order may not be randomly assigned.\n")
        f.write("- The tournament sample is restricted to the Gabrielino-attended set already collected.\n")
    return key_result


def generate_figures(rows: list[dict[str, object]], linear: OLSResult, quadratic: OLSResult) -> None:
    FIG_DIR.mkdir(exist_ok=True)

    mean_by_pos = aggregate_mean(rows, lambda r: int(r["speaking_position"]))
    x_pos = [float(k) for k, _, _ in mean_by_pos]
    y_pos = [v for _, v, _ in mean_by_pos]
    save_chart(
        FIG_DIR / "mean_rank_by_position.png",
        "Mean Rank By Speaking Position",
        "Lower rank = better",
        "Speaking position",
        "Mean rank",
        x_pos,
        y_pos,
        kind="line",
    )

    bins = np.linspace(0, 1, 11)
    centers = []
    means = []
    for i in range(len(bins) - 1):
        lo, hi = bins[i], bins[i + 1]
        vals = [float(r["rank"]) for r in rows if (float(r["normalized_position"]) >= lo and (float(r["normalized_position"]) < hi or (i == len(bins) - 2 and float(r["normalized_position"]) <= hi)))]
        if vals:
            centers.append((lo + hi) / 2)
            means.append(mean(vals))
    y_fit = [linear.coefficients[0] + linear.coefficients[1] * x for x in centers]
    save_chart(
        FIG_DIR / "mean_rank_by_normalized_position.png",
        "Mean Rank By Normalized Position",
        "Lower rank = better; red line = linear fit",
        "Normalized speaking position",
        "Mean rank",
        centers,
        means,
        kind="line",
        y_fit=y_fit,
    )

    mean_by_bin_map = {k: (v, n) for k, v, n in aggregate_mean(rows, lambda r: str(r["position_bin"]))}
    x_bins = [0, 1, 2]
    y_bins = [mean_by_bin_map[label][0] for label in ["early", "middle", "late"]]
    save_chart(
        FIG_DIR / "early_middle_late_comparison.png",
        "Mean Rank By Early / Middle / Late Position",
        "Lower rank = better",
        "Bin (0=early, 1=middle, 2=late)",
        "Mean rank",
        x_bins,
        y_bins,
        kind="bar",
    )

    xs = np.linspace(0, 1, 50)
    ys = [quadratic.coefficients[0] + quadratic.coefficients[1] * x + quadratic.coefficients[2] * (x ** 2) for x in xs]
    save_chart(
        FIG_DIR / "model_prediction_curve.png",
        "Quadratic Model Prediction Curve",
        "Lower rank = better",
        "Normalized speaking position",
        "Predicted rank",
        list(xs),
        list(ys),
        kind="line",
    )

    panel_sizes = Counter(int(r["panel_size"]) for r in rows)
    x_ps = list(sorted(panel_sizes))
    y_ps = [panel_sizes[x] for x in x_ps]
    save_chart(
        FIG_DIR / "panel_size_distribution.png",
        "Panel Size Distribution",
        "Counts of observations by panel size",
        "Panel size",
        "Observation count",
        x_ps,
        y_ps,
        kind="bar",
    )


def write_site(stats: dict[str, object], key_result: str) -> None:
    SITE_DIR.mkdir(exist_ok=True)
    css = """body{font-family:Helvetica,Arial,sans-serif;max-width:980px;margin:40px auto;padding:0 20px;line-height:1.5;color:#1f2937}h1,h2{color:#111827}img{max-width:100%;height:auto;border:1px solid #d1d5db;margin:18px 0}figure{margin:24px 0}figcaption{font-size:.95rem;color:#4b5563}.grid{display:grid;grid-template-columns:1fr 1fr;gap:24px}.card{background:#f9fafb;border:1px solid #e5e7eb;padding:16px;border-radius:8px}code{background:#f3f4f6;padding:2px 5px;border-radius:4px}@media (max-width: 800px){.grid{grid-template-columns:1fr}}"""
    (SITE_DIR / "styles.css").write_text(css)
    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Speaking Order Bias in Extemporaneous Speaking</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <h1>Speaking Order Bias in Extemporaneous Speaking</h1>
  <p>This site summarizes a ballot-level analysis of speaking order and judge-assigned rank in extemporaneous speaking rounds drawn from a Gabrielino-attended Tabroom tournament set. Lower rank is better.</p>

  <h2>Methods</h2>
  <p>Each observation is a competitor-by-judge row from a round-results ballot. Panels were cleaned so speaking positions start at 1, run contiguously, and contain no duplicate competitors within the same tournament + event + round_id + judge panel.</p>

  <h2>Key Dataset Stats</h2>
  <div class="grid">
    <div class="card"><strong>Tournaments</strong><br>{stats['n_tournaments']}</div>
    <div class="card"><strong>Panels</strong><br>{stats['n_panels']}</div>
    <div class="card"><strong>Judges</strong><br>{stats['n_judges']}</div>
    <div class="card"><strong>Observations</strong><br>{stats['n_obs']}</div>
  </div>

  <h2>Results</h2>
  <p>The clearest overall result is: <strong>{key_result}</strong>.</p>
  <p>This interpretation is based on cleaned ballot data, descriptive means, and linear / quadratic models where lower rank indicates a better outcome.</p>

  <figure>
    <img src="../figures/mean_rank_by_position.png" alt="Mean rank by speaking position">
    <figcaption>Mean rank by raw speaking position.</figcaption>
  </figure>
  <figure>
    <img src="../figures/mean_rank_by_normalized_position.png" alt="Mean rank by normalized position">
    <figcaption>Mean rank by normalized position with linear fit.</figcaption>
  </figure>
  <figure>
    <img src="../figures/early_middle_late_comparison.png" alt="Early middle late comparison">
    <figcaption>Average rank in early, middle, and late speaking slots.</figcaption>
  </figure>
  <figure>
    <img src="../figures/model_prediction_curve.png" alt="Quadratic model prediction curve">
    <figcaption>Quadratic model prediction curve.</figcaption>
  </figure>
  <figure>
    <img src="../figures/panel_size_distribution.png" alt="Panel size distribution">
    <figcaption>Panel size distribution in the cleaned dataset.</figcaption>
  </figure>

  <h2>Limitations</h2>
  <ul>
    <li>Judge heterogeneity can still influence ranks.</li>
    <li>Speaking order may not be randomly assigned.</li>
    <li>The dataset is limited to tournaments where Gabrielino attended and the relevant Tabroom ballot pages were available.</li>
  </ul>
</body>
</html>
"""
    (SITE_DIR / "index.html").write_text(html_text)


def write_readme(key_result: str) -> None:
    readme = f"""# Speaking Order Bias In Extemporaneous Speaking

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

Current high-level result: **{key_result}**.

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
"""
    README.write_text(readme)


def main():
    rows = load_rows()
    cleaned, clean_stats = clean_data(rows)
    save_cleaned(cleaned)

    y = np.array([float(r["rank"]) for r in cleaned], dtype=float)
    x = np.array([float(r["normalized_position"]) for r in cleaned], dtype=float)
    linear = ols_fit("linear", y, [x], ["normalized_position"])
    quadratic = ols_fit("quadratic", y, [x, x ** 2], ["normalized_position", "normalized_position_sq"])
    save_model_results([linear, quadratic])

    stats = dataset_stats(cleaned)
    key_result = write_summary(cleaned, stats, linear, quadratic)
    generate_figures(cleaned, linear, quadratic)
    write_site(stats, key_result)
    write_readme(key_result)

    print("key_result", key_result)
    print("created_files")
    for path in [
        CLEAN_CSV,
        MODEL_CSV,
        SUMMARY_MD,
        FIG_DIR / "mean_rank_by_position.png",
        FIG_DIR / "mean_rank_by_normalized_position.png",
        FIG_DIR / "early_middle_late_comparison.png",
        FIG_DIR / "model_prediction_curve.png",
        FIG_DIR / "panel_size_distribution.png",
        SITE_DIR / "index.html",
        SITE_DIR / "styles.css",
        README,
    ]:
        print(path)


if __name__ == "__main__":
    main()
