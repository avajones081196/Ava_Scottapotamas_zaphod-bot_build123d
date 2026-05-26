# Ava_Scottapotamas_zaphod-bot_build123d

Reverse-engineering the [Scottapotamas/zaphod-bot](https://github.com/Scottapotamas/zaphod-bot)
mechanical parts in [build123d](https://github.com/gumyr/build123d) from
Fusion-extracted CSV coordinates.

Each part follows the same pipeline:

1. Extract coordinates from the reference STL in Fusion → CSVs per sketch.
2. `0_preprocess_csvs.py` cleans the raw CSVs into `csv_merged/`.
3. `<part>_build123d.py` consumes the cleaned CSVs and reconstructs the geometry.
4. `<part>_compare_surfaces.py` measures the build123d output against the reference STL.

---

## Progress  ·  1 / 21

| Part | Status | Time | Δ surface area | Hausdorff (max) | Notes |
|------|:------:|-----:|---------------:|----------------:|-------|
| [`zaphod_bot_mec_fbcoup_3mm_globe`](./zaphod_bot_mec_fbcoup_3mm_globe) | ✅ | ~1 h | +0.18 % | 0.0051 mm | Surface of revolution; 0.1× post-scale needed (CSVs come out 10×) |
| `<next_part>` | ⏳ |  |  |  | |
| `<next_part>` | ⏳ |  |  |  | |
| ... |  |  |  |  | |

---

## Part 1 — `zaphod_bot_mec_fbcoup_3mm_globe`

A 3 mm globe (surface of revolution) from the fibre-coupler assembly.

- **Reference STL:** https://github.com/Scottapotamas/zaphod-bot/blob/master/mechanical/fibre_couplers/manf_outputs/3mm_globe.STL

### Result

| Metric            | Build123d   | Reference   | Δ          | Threshold | Rating |
| ----------------- | ----------: | ----------: | ---------: | --------: | :----: |
| Surface area      | 40.9791 mm² | 40.9073 mm² | +0.18 %    | ≤ 0.5 %   | 🟢     |
| Bbox per axis     | —           | —           | ≤ 0.004 mm | ≤ 0.1 mm  | 🟢     |
| Centroid distance | —           | —           | 0.0009 mm  | ≤ 0.1 mm  | 🟢     |
| Hausdorff (max)   | —           | —           | 0.0051 mm  | ≤ 0.1 mm  | 🟢     |
| Mean distance     | —           | —           | 0.0019 mm  | ≤ 0.01 mm | 🟢     |

### How it was built

Two source sketches, both on the **X = 15.0** plane (auto-detected):

- **S1** — profile: 2 lines + 3 three-point arcs walked into an open
  5-edge chain. The two free endpoints sit on the revolve axis at
  Z = 0 and Z = 5; the on-axis gap is closed by the revolution itself.
- **S2** — construction axis: 1 line at Y ≈ 15 running from Z = 29.142
  to Z = 13.073. The CSV has an ~0.018 mm Y-wobble; the script snaps
  the constant Y component to its mean so the revolve axis is
  perfectly Z-aligned.

Guidelines:

- **G1** — read S1, walk the open profile wire (5 oriented edges).
- **G2** — read S2, build the construction axis line.
- **G3** — final export (always last): `.clean()` then STL + STEP + summary.
- **G4** — revolve the G1 profile about the G2 axis (360°), then scale
  the result by **0.1** about the world origin.

**Why the 0.1× scale:** the Fusion add-in exports CSVs at 10× the
reference part's scale (CSV span ~30 mm vs reference span ~3 mm).
Fastest fix is a single post-revolve scale step in G4. A cleaner
long-term fix would be at the `0_preprocess_csvs.py` stage.

**Revolve solver:** `build123d.revolve()` silently returns an empty
Compound when given an open `Wire`, so the script goes directly to
`OCP.BRepPrimAPI.BRepPrimAPI_MakeRevol`. That produces 5 faces:
2 spherical REVOLUTIONs, 1 TORUS, 1 CYLINDER, 1 CONE — total surface
area ~40.98 mm² after the scale.

### Screenshots

After applying the 0.1 scale, the two parts match — same diameter,
same hole geometry. (Tiny ball = reference; big ball = original
build123d output before the scale fix.)

![Fusion size comparison](./zaphod_bot_mec_fbcoup_3mm_globe/images/fusion_size_comparison.png)

![Finder listing of project outputs](./zaphod_bot_mec_fbcoup_3mm_globe/images/finder_outputs.png)

---

## Acceptance thresholds (FDM-tolerance, CAD-vs-CAD)

Applied by every `<part>_compare_surfaces.py` script.

| Metric            | 🟢 ≤    | 🟡 ≤    | 🟠 ≤   | 🔴 >   |
| ----------------- | ------: | ------: | -----: | -----: |
| Surface area %    | 0.5 %   | 2 %     | 5 %    | 5 %    |
| Bbox per axis     | 0.1 mm  | —       | —      | 0.1 mm |
| Centroid per axis | 0.1 mm  | —       | —      | 0.1 mm |
| Hausdorff (max)   | 0.1 mm  | 0.5 mm  | 1.0 mm | 1.0 mm |
| Mean distance     | 0.01 mm | 0.05 mm | 0.1 mm | 0.1 mm |

---

## Layout

```
Ava_Scottapotamas_zaphod-bot_build123d/
├── README.md                              ← this file (the only one)
├── zaphod_bot_mec_fbcoup_3mm_globe/       ← part 1
│   ├── 0_preprocess_csvs.py
│   ├── <part>_build123d.py
│   ├── <part>_compare_surfaces.py
│   ├── csv_data_<part>/                   ← raw extracted CSVs
│   ├── csv_merged/                        ← cleaned per-sketch CSVs
│   ├── <part>_G_1_N.stl / .step           ← build outputs
│   ├── <part>_summary_G_1_N.txt
│   ├── <part>_area_history_G_1_N.txt
│   ├── <part>_build123d_vs_reference_G_1_N.txt
│   ├── <part>_reference.STL
│   └── images/                            ← screenshots used in this README
└── zaphod_bot_<next_part>/                ← part 2, 3, …
```

---

## Environment

- `build123d`
- `ocp_vscode` (in-VSCode OCP viewer on port 3939)
- `numpy-stl`, `trimesh`, `manifold3d`, `rtree` (compare scripts)
