# Ava — Scottapotamas zaphod-bot build123d Reconstruction

Reconstruction of the [zaphod-bot project](https://github.com/Scottapotamas/zaphod-bot) STL parts in [build123d](https://github.com/gumyr/build123d), with surface-area / Hausdorff-distance verification against the original GitHub-hosted STLs.

**Reference:** https://github.com/Scottapotamas/zaphod-bot
**This repo:** https://github.com/avajones081196/Ava_Scottapotamas_zaphod-bot_build123d

---

## Project Overview

The zaphod-bot project hosts 21 STL parts (mechanical sub-assemblies, fibre couplers, brackets, etc.). For each part this repo provides:

1. A `<part_name>/` folder containing all working files
2. A build123d Python script that parametrically reconstructs the part
3. A surface-comparison script that validates the reconstruction against the reference STL
4. A summary report and area-history log per stage

Each part is rebuilt **from scratch in build123d** — not converted from the STL — so the result is a clean parametric model that matches the original geometry as closely as the source data allows.

A future `zaphod_bot_assembly/` folder at the project root will combine all 21 finished part STLs into a single `zaphod_bot_assembly_Final.stl` for full-project visualization, following the same pattern used in the [PICSY companion repo](https://github.com/avajones081196/Ava_Jana-Marie_PICSY_build123d).

---

## Status

| # | Part | Status | Surface area err | Mean dist (mm) | Hausdorff (mm) | Time |
|---|------|--------|------------------|----------------|----------------|------|
| 1 | zaphod_bot_mec_fbcoup_3mm_globe | ✅ Complete | 0.18% | 0.0019 | 0.0051 | 1 h |
| 2 | zaphod_bot_mec_fbcoup_5x15mm_1mm_globe_post | ✅ Complete | 0.14% | 0.0029 | 0.0092 | 1 h 15 min |
| 3 | — | ⏳ Pending | | | | |
| ... | | | | | | |
| 21 | — | ⏳ Pending | | | | |

`zaphod_bot_mec_fbcoup_3mm_globe` is the first part. It is a 3 mm globe surface of revolution built from two source sketches (S1 profile + S2 axis). All five aggregate metrics land in the 🟢 EXCELLENT band: surface area to 0.18%, mean point distance 0.0019 mm, Hausdorff worst-case 0.0051 mm, bounding box ≤ 0.004 mm/axis, centroid distance 0.0009 mm. See "Notes on zaphod_bot_mec_fbcoup_3mm_globe" below for the build detail behind it.

`zaphod_bot_mec_fbcoup_5x15mm_1mm_globe_post` is the second part. It is a ~20.8 mm long globe-post — a slender body with cylindrical, conical and toroidal sections terminating in a small 1 mm globe — built as a surface of revolution from the same two-sketch pattern (S1 open profile + S2 axis line). Geometry is more complex than the 3mm_globe: 14 primitives in the source CSV instead of 5, including the first **spline** primitive in the repo and a missing-bridge defect in the source CSV that has to be auto-repaired. All aggregate metrics land in 🟢 EXCELLENT: surface area to 0.14%, mean distance 0.0029 mm, Hausdorff worst-case 0.0092 mm, bounding box ≤ 0.006 mm/axis, centroid distance 0.0020 mm. All seven cross-section slices ✅ PASS. See "Notes on zaphod_bot_mec_fbcoup_5x15mm_1mm_globe_post" below for the detail.

---

## Methodology

The reconstruction pipeline is the same for every part. For surface parts (open shells like `zaphod_bot_mec_fbcoup_3mm_globe`) and solid parts (closed bodies) the comparison metrics differ; everything else is identical.

### Step 1 — Coordinate extraction in Fusion 360

The reference STL is imported into Fusion 360. Using a custom Fusion add-in script (not included in this repo), each closed sketch profile is selected, and its line / arc / spline endpoints are written to a CSV with this schema:

```
Steps, Draw Type, X1, Y1, Z1, X2, Y2, Z2, X3, Y3, Z3, …
```

`Draw Type` is one of `Line`, `3_point_arc`, `3_point_circle`, `spline_<N>_points`, `Point`, etc. The X/Y/Z columns hold world-space coordinates in millimetres. Splines extend the row with additional `X_n / Y_n / Z_n` columns for each control point. Each logical sketch is one CSV file (`Fusion_Coordinates_S1.csv`, `Fusion_Coordinates_S2.csv`, …). Splitting by sketch makes loop detection deterministic — adjacent profiles that touch at a corner are kept in separate files so the loop-walker doesn't merge them.

### Step 2 — CSV cleaning (`0_preprocess_csvs.py`)

A preprocessor consolidates and validates the raw CSVs:
- Strips trailing whitespace
- Removes duplicate rows
- Validates each row has the right number of fields
- Writes cleaned outputs to `csv_merged/`

### Step 3 — build123d reconstruction (`<part>_build123d.py`)

The main script reads the cleaned CSVs and rebuilds the geometry as a series of numbered guidelines (G1, G2, G3, …). The guideline count scales with part complexity — for the 3mm_globe and 5x15mm_1mm_globe_post G1–G4 is enough (G3 is always the final export step). For larger parts the count will grow into the dozens, following the same pattern proven on the PICSY companion repo (where individual parts run up to G92). The pattern is:

- **Read CSV** guidelines — parse line / arc / spline / point segments, walk endpoints to detect closed loops or open chains.
- **Build profile wires** — assemble parsed primitives into oriented `Wire` objects. Profiles can be left as construction-only (no patched face) when the next step is a sweep / revolve / loft that consumes the wire directly.
- **Surface-revolve / extrude / loft** — the part-specific geometric operation. For `3mm_globe` and `5x15mm_1mm_globe_post` this is a 360° revolve of an open profile wire about a construction-axis line. For future parts it may include any of the extrude / loft / boolean / trim patterns documented in the PICSY companion repo.
- **G3** — always last: apply `.clean()` to remove micro-scars, then export STL + STEP.

Key implementation notes:

- **Cross-platform paths.** `BASE_DIR = Path(__file__).resolve().parent`. No hardcoded absolute paths anywhere.
- **World-coordinate face construction.** All `Edge.make_line(Vector(x, y, z), …)` calls use world coordinates directly. `Plane.XZ.offset()` is avoided because it silently flipped the Z axis in some build123d versions.
- **Plane-detection per CSV (axis-aligned + tilted).** Each CSV sketch's plane is auto-detected per the template's coordinate convention. The detector first tries the axis-aligned case (one of X / Y / Z is constant within tolerance); if no axis is constant, it falls back to a least-squares plane fit via SVD (centroid + smallest-singular-direction normal). For `3mm_globe` both S1 and S2 auto-detect to X = 15.0; for `5x15mm_1mm_globe_post` both auto-detect to X = 3.848. The detector returns `('axis', letter, value)` or `('general', origin, normal)` and downstream geometry-builders dispatch on that tuple.
- **Open-chain walking for surfaces of revolution.** When a profile is meant to be revolved (rather than patched into a face), the source CSV gives an *open* chain whose two free endpoints sit on the revolve axis — the on-axis gap is closed by the revolution itself, no explicit edge needed. A small walker traverses the parsed primitives by endpoint adjacency: find the two count-1 endpoints (the chain's free ends), pick one as start, then at each step pick the unused primitive that shares the current "front" endpoint, reversing it if necessary, and continue until the other free end is reached. Used for `3mm_globe` G1 (5 edges: 2 Lines + 3 three-point arcs) and `5x15mm_1mm_globe_post` G1 (15 edges: 8 Lines + 5 three-point arcs + 1 five-point spline + 1 programmatic bridge line — see the part's notes below). The same walker generalises to mixed line / arc / spline chains.
- **Three-point arc handling.** The Fusion add-in exports each arc as `(p1, p2, p3) = (start, middle-on-arc, end)`. The build script calls `Edge.make_three_point_arc(start, mid, end)` directly; the `parse_three_point_arcs` helper keeps the middle point as part of the (start, mid, end) tuple so it survives any reversal during chain walking.
- **Spline handling and CSV overflow columns.** Splines exported as `spline_<N>_points` carry all N control points in a single row, but the CSV header only declares the first 9 coordinate columns (X1..Z3). For N > 3 the extra triples land in `csv.DictReader`'s overflow under the `None` key as a flat list of strings. The `_row_all_xyz_triples` helper recovers them so a 5-point spline is built from all 5 control points, not just 3. The edge itself is built with `Edge.make_spline([Vector(x, y, z), …])`, which produces a C2 B-spline through all control points.
- **Endpoint precision through the chain walker.** Adjacency matching for chain walking uses a `_kep` function that rounds each `(u, v)` endpoint to 0.01 mm, so primitives that meet "near enough" join up despite small floating-point drift in the source CSV. But the *rounded* keys must not leak into actual `Edge.make_*` calls — OCCT-level wire construction is much stricter than the rounded match (it expects coincident vertices at floating-point precision), and a 0.001 mm endpoint mismatch is enough to produce a "Edges are disconnected" error from `Wire(...)`. The walker keeps the original unrounded `(u, v)` tuples alongside the rounded keys, and downstream edge construction always uses the originals. The same rule applies to any programmatic bridge insertion: bridge endpoints must reuse the *exact* unrounded `(u, v)` of the matching existing primitive, not the rounded adjacency key.
- **Axis-snap for noisy construction lines.** Fusion's add-in sometimes exports a "constant-along-one-axis" construction line with a small wobble in that axis (the `3mm_globe` S2 axis has a 0.018 mm Y-wobble; `5x15mm_1mm_globe_post` S2 is clean). The build script detects when a component varies by less than `AXIS_SNAP_MM = 0.05 mm` and snaps that component to its mean, so the revolve axis is perfectly axis-aligned and the resulting surface of revolution has no tilt. Without this snap a 0.018 mm Y-drift would translate proportionally through the revolve.
- **`build123d.revolve()` quietly fails on open wires.** Given an open `Wire`, build123d's high-level `revolve()` returns an empty `Compound` without raising. The script goes directly to OCCT's `BRepPrimAPI.BRepPrimAPI_MakeRevol(wire, gp_Ax1, angle, copy=True)` as the primary path, with per-edge revolve as a fallback and build123d's `revolve()` as a last-resort fallback. The primary path produces one face per profile primitive (5 faces for the 3mm_globe, 15 faces for the 5x15mm_1mm_globe_post).
- **Post-revolve scale fix for CSV-vs-reference unit mismatch (3mm_globe only).** The Fusion add-in's CSV export for `3mm_globe` came out at 10× the reference part's scale (CSV span ~30 mm vs reference span ~3 mm). The fastest fix is a single post-revolve scale step in G4: build the surface at the CSV's native scale, then apply `gp_Trsf.SetScale(origin, 0.1)` via `BRepBuilderAPI_Transform` to every face. The `5x15mm_1mm_globe_post` CSVs came out at the correct reference scale and need no post-revolve scaling. A cleaner long-term fix would live in `0_preprocess_csvs.py`; the post-revolve scale is recorded here in case other parts hit the same export idiosyncrasy.
- **Filename guideline-range convention.** Output filenames carry the active guideline range (e.g. `zaphod_bot_mec_fbcoup_3mm_globe_G_1_4.stl`) so multiple checkpoint exports coexist without clobbering each other.
- **Per-guideline checkpoints.** Three top-of-file flags (`VIEW_AT`, `STOP_AFTER_VIEW`, `EXPORT_AT_CHECKPOINT`) let you halt at any guideline, send the cumulative state to the OCP viewer on port 3939, and optionally export `<part>_G_1_N.{stl,step,txt}` mid-pipeline for inspection.
- **Surface-area tracking.** Every guideline's cumulative surface area is recorded. Both the main summary and a standalone `<part>_area_history_G_1_N.txt` document how area accumulates and (for trim guidelines, when they arrive in later parts) decreases. For complex parts this audit trail is the single most valuable debugging tool — any unexpected Δ-area at a downstream guideline points straight back to the upstream guideline that introduced the wrong geometry.

### A note on `zaphod_bot_mec_fbcoup_3mm_globe` — why it took 1 hour

The 3mm_globe is structurally the simplest possible PICSY-style part: a single open profile revolved about a single axis line, 4 guidelines total (G1, G2, G4, with G3 as the final export step). The 1 hour was split roughly as:

- **~20 min** on the parser side: writing `parse_three_point_arcs`, the open-chain walker that finds the 2 free endpoints and walks the 5 primitives into a connected oriented chain, and confirming the plane auto-detector handles X-constant sketches the same way it handles Z-constant ones in the PICSY repo.
- **~15 min** running into and fixing the empty-Compound silent failure from `build123d.revolve()` on an open Wire. The fix was straightforward once isolated — drop to OCCT's `BRepPrimAPI_MakeRevol` directly, which produces 5 faces (2 REVOLUTION, 1 TORUS, 1 CYLINDER, 1 CONE) of total area ~4099 mm² (pre-scale).
- **~10 min** diagnosing the 10× scale mismatch when the first build came out as a 30 mm globe next to the 3 mm reference STL in Fusion. The CSV-vs-reference scale ratio was an exact 10×, so a single `gp_Trsf.SetScale(origin, 0.1)` step at the end of G4 closed the gap. Post-scale surface area: 40.988 mm² vs reference 40.9073 mm² — 0.18% off.
- **~15 min** on the 0.018 mm Y-axis-wobble in the S2 construction line, the cross-platform `BASE_DIR` plumbing, and confirming the comparison script lands every metric in 🟢 EXCELLENT.

Two notes worth recording for future parts:

- **`build123d.revolve()` on open wires silently returns an empty Compound.** No exception, no warning — just zero faces in the result. Always check `len(result.faces())` before assuming success, or skip the wrapper and call `BRepPrimAPI_MakeRevol` directly when the profile is a 1-D wire rather than a closed face. The same defensive check pattern will apply to any other high-level build123d operation whose OCCT backend can degenerate on edge-case inputs.
- **CSV-vs-reference unit mismatch is silent and uniform.** It does not announce itself as a single bad coordinate — every coordinate is wrong by the same factor, so plane detection still works, loop walking still works, the revolve still completes, and the only symptom is a build that's 10× too big when imported into Fusion next to the reference. Detection method: import both into Fusion and visually compare. Quick fix: post-build scale. Longer fix: catch it at the preprocess stage and emit a scale factor with the cleaned CSV.

### A note on `zaphod_bot_mec_fbcoup_5x15mm_1mm_globe_post` — why it took 1 h 15 min

The 5x15mm_1mm_globe_post is the second part and reuses the same 4-guideline structure as the 3mm_globe (G1 = S1 open profile, G2 = S2 axis line, G4 = surface-revolve, G3 = final export). Geometry is more complex though: 14 primitives in S1 (8 Lines + 5 three-point arcs + 1 five-point spline) versus 5 in the 3mm_globe (2 Lines + 3 three-point arcs), and the source CSV had a real defect that needed programmatic repair. The 1 h 15 min was split roughly as:

- **~15 min** dropping the existing 3mm_globe script into the new folder, swapping the CSV paths via `BASE_DIR`, and confirming the plane auto-detector handles X = 3.848 the same way it handled X = 15.0. Most of the helper infrastructure (CSV reading, plane detection, axis-aligned `world_vec_axis`/`in_plane_uv`, `parse_line_segments`, `parse_three_point_arcs`, `walk_open_chain`, the checkpoint scaffold) came across unchanged.
- **~20 min** adding spline support: a `parse_splines` helper, a `make_spline_edge` builder that wraps `Edge.make_spline([Vector(x, y, z), …])`, and the closure pattern that lets the chain walker reverse a spline by flipping its control-point sequence. First run printed `Spline1: 3 pts, …` — wrong; the CSV row had 5 control points but only 3 showed up because the CSV header only declares X1..Z3 and `csv.DictReader` was burying the overflow under the `None` key as a flat list of strings. Fix: a new `_row_all_xyz_triples` helper that recovers both the named columns *and* the overflow, used by both the spline parser and the plane detector. After the fix `Spline1: 5 pts, (0.241, 5.375) → (8.591, 5.084)` — correct.
- **~25 min** on the missing-bridge CSV defect. With all 14 primitives parsed correctly the chain walker reported **4 free endpoints instead of 2**: the two expected on-axis points `(20.8, 4.008)` and `(17.0, 4.008)`, plus two unexpected off-axis points `(8.591, 5.084)` and `(13.0, 5.084)`. The off-axis pair shared their Z value to four decimal places, which made it obvious the source CSV was missing one short horizontal Line between them — a clean horizontal at Z = 5.084 from Y = 8.591 to Y = 13.0. I auto-repair the chain at G1 by:
  - (a) peeking at S2 at G1 time to learn the revolve-axis V coordinate (4.008),
  - (b) enumerating every pair of free endpoints whose V coordinates match within `BRIDGE_V_TOL = 0.01 mm`,
  - (c) excluding pairs where either endpoint sits on the revolve axis (those endpoints must remain free — they're closed by the revolution itself, and bridging two on-axis points would create a degenerate edge on the axis),
  - (d) trial-walking each surviving candidate and accepting the one that lets the walker visit every primitive exactly once.

  Only one candidate survives: the gap-pair at Z = 5.084. A programmatic Line is inserted with the exact unrounded `(u, v)` of each existing endpoint, and the chain walks all 15 edges cleanly. The summary records `Bridge added: yes — ((13.0, 5.084), (8.591, 5.084))` so the repair is auditable. The build script also confirms after walking that the two remaining free endpoints belong to Step 1 (the arc) and Step 14 (the final Line) — bails out with a clear error if not.
- **~10 min** on a precision-leak bug surfaced by the bridge insertion. The walker was storing rounded adjacency keys (`(17.0, 4.01)`) in places where the original unrounded coords (`(17.0, 4.008)`) were needed — and feeding rounded coords to `Edge.make_line` produced bridge endpoints that *almost* matched the adjacent primitive but missed by ~4 µm. `Wire(ordered_edges)` then raised `ValueError: Edges are disconnected`. Fix: `walk_open_chain` and `_find_free_endpoints` now both track the original unrounded `(u, v)` alongside the rounded `_kep(...)` key, and downstream edge construction uses the originals throughout.
- **~5 min** confirming no post-revolve scaling was needed (the source CSVs were already at the reference part's scale — Y span ~20.8 mm matches the reference exactly), running the comparison script, and confirming every aggregate metric lands in 🟢 EXCELLENT.

Final numbers vs reference: surface area 404.55 mm² vs 403.99 mm² (0.14% off), bounding box ≤ 0.006 mm/axis, centroid distance 0.0020 mm, Hausdorff worst-case 0.0092 mm, mean distance 0.0029 mm, all seven cross-section slices ≤ 0.24% perimeter error.

Three notes worth recording for future parts:

- **CSV-header overflow with splines is silent.** `csv.DictReader` does not error or warn when a row has more cells than the header declares — it parks the extras under the `None` key as a flat list of strings, which is easy to miss. Any parser that supports multi-point primitives needs to read both the named X1..Zn columns *and* `row[None]`, splitting that overflow into triples. The `_row_all_xyz_triples` helper handles both paths uniformly and should be reused unchanged for any future spline / multi-point primitive.
- **Programmatic bridge insertion needs the axis context.** A naïve "join the two closest free endpoints" rule would have bridged the on-axis pair and produced a degenerate revolve. The bridge selector must know which V (or U) coordinate is the revolve axis so it can exclude on-axis pairs from the candidate pool. Peeking at S2 from inside G1 is fine and keeps the G1/G2/G4 ordering clean — the alternative (running G2 first then back-patching G1) would invert the natural read order.
- **Rounded adjacency keys must not leak into geometry.** Fuzzy adjacency matching (rounding to 0.01 mm) is needed because source CSVs have small floating-point drift across files. But OCCT's wire builder is much stricter — it wants vertex coincidence to floating-point precision. The walker carries both representations side-by-side: rounded keys for adjacency lookup, unrounded coordinates for every `Edge.make_*` call. The same discipline applies to any programmatic edge insertion (bridges, axis snaps, etc.): build the edge from the original unrounded source coordinates, never from the rounded keys.

### Step 4 — Surface comparison (`<part>_compare_surfaces.py`)

For **surface parts**, the volume + symmetric-volume-difference approach used for solids does not apply. Instead the comparison script reports six complementary metrics:

| Metric | What it catches |
|---|---|
| Surface area %     | Wrong size, missing/extra faces |
| Bounding box       | Scale or placement errors |
| Tessellation density | Informational; different tessellators differ |
| Centroid alignment | Translation drift |
| **Hausdorff distance** | **THE primary metric — point-by-point worst-case deviation** |
| Cross-section slices | Feature-level errors at specific Y depths |

The Hausdorff section samples 50,000 random points on each surface, finds the nearest point on the other surface, and reports max / mean / RMS / 95th / 99th percentile distances. For surfaces these collectively prove "the two surfaces occupy the same locations in space," which is the surface analogue of "same volume + zero symmetric difference."

The **cross-section slice comparison** has proven especially valuable on complex parts: it cuts both meshes at multiple Y-plane positions (auto-derived from mesh bounds) and compares the outline perimeter at each cut. Aggregate metrics like Hausdorff or mean-distance can mask a 1–2% feature-level discrepancy because the affected region is small compared to the total surface — the slice test bypasses this by comparing geometry at specific cross-sections. On the 5x15mm_1mm_globe_post all seven slices passed under 0.24% perimeter error, which gave high confidence that no localized feature had been silently lost or distorted by the bridge-insertion repair.

For **solid parts** the original volume + symmetric-volume-difference comparison from the [Thor assembly project](https://github.com/avajones081196/Ava_AngelLM_Thor_Art1_build123d) is used.

---

## Per-part Folder Layout

```
zaphod_bot_mec_fbcoup_3mm_globe/
├── zaphod_bot_mec_fbcoup_3mm_globe_build123d.py            # main reconstruction script
├── zaphod_bot_mec_fbcoup_3mm_globe_compare_surfaces.py     # comparison vs reference
├── 0_preprocess_csvs.py                                    # CSV cleaner
├── 0_preprocess_csvs_summary.txt                           # preprocess log
├── csv_data_zaphod_bot_mec_fbcoup_3mm_globe/               # raw extracted CSVs
├── csv_merged/                                             # cleaned CSVs (input to build script)
│   ├── Fusion_Coordinates_S1.csv
│   └── Fusion_Coordinates_S2.csv
├── zaphod_bot_mec_fbcoup_3mm_globe_reference.STL           # downloaded from upstream zaphod-bot repo
├── zaphod_bot_mec_fbcoup_3mm_globe_G_1_4.stl               # build123d output (final)
├── zaphod_bot_mec_fbcoup_3mm_globe_G_1_4.step              # parametric format
├── zaphod_bot_mec_fbcoup_3mm_globe_summary_G_1_4.txt       # per-guideline summary
├── zaphod_bot_mec_fbcoup_3mm_globe_area_history_G_1_4.txt  # cumulative area per guideline
└── zaphod_bot_mec_fbcoup_3mm_globe_build123d_vs_reference_G_1_4.txt  # comparison report
```

The same layout will be used for every part. Output filenames carry the active guideline range (e.g. `zaphod_bot_mec_fbcoup_3mm_globe_G_1_4.stl`) so checkpoint exports do not clobber each other.

---

## Environment

```
build123d
ocp_vscode
trimesh
numpy-stl
manifold3d
rtree            # required for Hausdorff distance computation
```

OCP viewer is reached via:

```python
from ocp_vscode import show, set_port
set_port(3939)
```

Tested on macOS (Python 3.11). Scripts are written cross-platform; should run unchanged on Windows and Linux.

---

## Running the Scripts

From inside any part folder:

```bash
# Build the part
python <part_name>_build123d.py

# Compare the build123d output to the reference STL
python <part_name>_compare_surfaces.py
```

To inspect intermediate stages, edit the top of the build script:

```python
VIEW_AT              = 4     # show state after guideline 4
STOP_AFTER_VIEW      = True  # halt after that checkpoint
EXPORT_AT_CHECKPOINT = True  # also write G_1_4.stl/.step
```

Set `VIEW_AT = None` for a clean end-to-end run that only writes the final outputs.

---

## Acceptance Criteria — How the Ratings Are Set

For surface parts (e.g. `zaphod_bot_mec_fbcoup_3mm_globe`, `zaphod_bot_mec_fbcoup_5x15mm_1mm_globe_post`), the rating thresholds are aligned with typical FDM 3D-printer manufacturing tolerances rather than CAD-tight micrometre tolerances, since the zaphod-bot parts are designed for FDM printing. A well-tuned consumer FDM printer (Prusa, Bambu, etc.) has roughly 0.1–0.5 mm positional accuracy, with industry rule-of-thumb specs of ±0.5 mm. Anything below that floor is below what the manufacturing process can resolve, so it counts as "indistinguishable from the original" in practice.

| Metric | 🟢 Excellent | 🟡 Good | 🟠 Acceptable | 🔴 Poor |
|---|---|---|---|---|
| Surface area % | ≤ 0.5% | ≤ 2% | ≤ 5% | > 5% |
| Bounding box | ≤ 0.1 mm/axis | — | — | > 0.1 mm |
| Centroid | ≤ 0.1 mm/axis | — | — | > 0.1 mm |
| Hausdorff | ≤ 0.1 mm | ≤ 0.5 mm | ≤ 1.0 mm | > 1.0 mm |
| Mean distance | ≤ 0.01 mm | ≤ 0.05 mm | ≤ 0.1 mm | > 0.1 mm |
| Cross-section slices | all pass (≤ 0.5% per slice) | one slice 0.5–2% | one slice 2–5% | multiple fail or > 5% |

Rationale for the Hausdorff / mean-distance thresholds:

- **🟢 Excellent (≤ 0.1 mm)** — Indistinguishable from the original CAD even on a precision (e.g. SLA / industrial) printer.
- **🟡 Good (≤ 0.5 mm)** — Below typical FDM positional accuracy; deviations of this size are lost in print noise.
- **🟠 Acceptable (≤ 1.0 mm)** — Within loose FDM tolerance; the printed part will function correctly but small features may be slightly off.
- **🔴 Poor (> 1.0 mm)** — Print-visible defect; the deviation is larger than what the printer would have introduced anyway, so the reconstruction needs review.

A part needs to pass **every aggregate metric** (surface area, bounding box, centroid, Hausdorff, mean distance) to earn the ✅ Complete badge. The cross-section slice test is treated as a confirmation test rather than a strict gate: if all aggregate metrics pass AND the Hausdorff worst-case is under the FDM print-tolerance floor of 0.5 mm, then an isolated 🟠 ACCEPTABLE slice (one slice in the 2–5% band) is treated as a known minor variance rather than a failure — because the deviation, however large in *perimeter percentage*, is by definition smaller than what the FDM process can resolve.

A part is marked ⚠ Review required (rather than ✅ Complete) if any aggregate metric fails, if Hausdorff exceeds 0.5 mm, or if more than one cross-section slice fails — in any of those cases the deviation is print-visible.

Surface-area % thresholds are kept tight since that metric is a unitless ratio and not bounded by print tolerance.

These mirror reverse-engineering / metrology defaults adjusted for FDM manufacturing (vs. machined-tight CAD comparison, where ≤ 0.05 mm thresholds would apply). Per-part the user may adjust thresholds at the top of the comparison script.

---

## Notes on the Reference STLs

The reference STLs come from upstream tessellation by the zaphod-bot repo's authors. Some are not perfectly closed meshes — `is_watertight` may report `False`. This is normal: STL exports often leave non-coincident edges across feature boundaries. For the comparison script this is fine because surface comparison does not require closure.

---

## License

This repo follows the upstream [zaphod-bot repository's license](https://github.com/Scottapotamas/zaphod-bot). All build123d reconstruction code and comparison utilities are provided as-is for educational and reverse-engineering purposes.
