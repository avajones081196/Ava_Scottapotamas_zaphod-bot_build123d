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
| 3 | zaphod_bot_mec_fbcoup_5x15mm_2mm_globe_post | ✅ Complete | 0.15% | 0.0032 | 0.0098 | 1 h |
| 4 | zaphod_bot_mec_fbcoup_5x15mm_presentation_post | ✅ Complete | 0.017% | 0.0031 | 0.0144 | 30 min |
| 5 | zaphod_bot_mec_fbcoup_5x25mm_presentation_post | ✅ Complete | 0.020% | 0.0033 | 0.0151 | 20 min |
| 6 | zaphod_bot_mec_fbcoup_fiber_led_coupler | ⏳ Pending | | | | |
| 7 | zaphod_bot_mec_de_man_out_printer_proto_homing_block | ✅ Complete | 0.011% | 0.0002 | 0.0024 | 50 min |
| 8 | — | ⏳ Pending | | | | |
| ... | | | | | | |
| 21 | — | ⏳ Pending | | | | |

`zaphod_bot_mec_fbcoup_3mm_globe` is the first part. It is a 3 mm globe surface of revolution built from two source sketches (S1 profile + S2 axis). All five aggregate metrics land in the 🟢 EXCELLENT band: surface area to 0.18%, mean point distance 0.0019 mm, Hausdorff worst-case 0.0051 mm, bounding box ≤ 0.004 mm/axis, centroid distance 0.0009 mm. See "Notes on zaphod_bot_mec_fbcoup_3mm_globe" below for the build detail behind it.

`zaphod_bot_mec_fbcoup_5x15mm_1mm_globe_post` is the second part. It is a ~20.8 mm long globe-post — a slender body with cylindrical, conical and toroidal sections terminating in a small 1 mm globe — built as a surface of revolution from the same two-sketch pattern (S1 open profile + S2 axis line). Geometry is more complex than the 3mm_globe: 14 primitives in the source CSV instead of 5, including the first **spline** primitive in the repo and a missing-bridge defect in the source CSV that has to be auto-repaired. All aggregate metrics land in 🟢 EXCELLENT: surface area to 0.14%, mean distance 0.0029 mm, Hausdorff worst-case 0.0092 mm, bounding box ≤ 0.006 mm/axis, centroid distance 0.0020 mm. All seven cross-section slices ✅ PASS. See "Notes on zaphod_bot_mec_fbcoup_5x15mm_1mm_globe_post" below for the detail.

`zaphod_bot_mec_fbcoup_5x15mm_2mm_globe_post` is the third part. It is the slightly-larger sibling of the 1mm-globe-post — a ~21.9 mm long globe-post terminating in a 2 mm globe instead of a 1 mm one — built from the same two-sketch surface-of-revolution pattern (S1 open profile + S2 axis line). Geometry is in the same complexity band as the 1mm-post (15 primitives in S1 vs 14) but structurally cleaner: **10 Lines + 5 three-point arcs and no splines**, and the source CSV is complete (no missing-bridge defect — the 15-primitive chain walks straight through with exactly 2 free endpoints on the revolve axis at `Z = 4.008`). All aggregate metrics land in 🟢 EXCELLENT: surface area to 0.151%, mean distance 0.0032 mm, Hausdorff worst-case 0.0098 mm, bounding box ≤ 0.005 mm/axis, centroid distance 0.0024 mm. All seven cross-section slices ✅ PASS (worst 0.283%). See "Notes on zaphod_bot_mec_fbcoup_5x15mm_2mm_globe_post" below for the detail.

`zaphod_bot_mec_fbcoup_5x15mm_presentation_post` is the fourth part. It is a 20 mm-long fibre-coupler post in the same body-shape family as the two globe-posts but **structurally different on two axes**: the profile is a single **CLOSED** loop (not an open chain terminating on the revolve axis), and the source sketch lies on a **Z-constant plane** (`Z = 4.582`) rather than the X-constant planes used by every previous part. Same two-sketch pattern (S1 profile + S2 axis line); the closed wire revolved 360° about an axis line that sits outside the profile's X-range produces a torus-topology shell that happens to come out **watertight** when tessellated (both the build123d STL and the upstream reference STL register as closed solids in trimesh). All aggregate metrics land in 🟢 EXCELLENT, and this is the tightest run of the project so far on every aggregate: surface area to 0.017% (an order of magnitude better than the three globe-family parts), mean distance 0.0031 mm, Hausdorff worst-case 0.0144 mm, bounding box ≤ 0.0032 mm/axis, centroid distance 0.0026 mm. All seven cross-section slices ✅ PASS (worst 0.178% at Y = 13.0 — the best slice run of the four parts so far). See "Notes on zaphod_bot_mec_fbcoup_5x15mm_presentation_post" below for the detail.

`zaphod_bot_mec_fbcoup_5x25mm_presentation_post` is the fifth part. It is the **longer sibling** of the 5x15mm presentation_post — a 30 mm-long fibre-coupler post (10 mm longer along Y than its 5x15mm counterpart) built from a **structurally identical** source sketch: same closed-loop profile of **8 Lines + 4 three-point arcs = 12 primitives** on a **Z = 4.582 plane**, same revolve-axis at `X = 4.397` on the same plane outside the profile's X-range (~0.4..3.32), same torus-topology shell. The only differences in the source CSVs vs the 5x15mm variant are (a) the profile's Y-range now spans `0.0..30.0` instead of `0.0..20.0`, and (b) the S2 axis-line endpoints move proportionally to `(4.397, 30.0) → (4.397, 27.038)`. The upstream reference STL tessellates watertight as before, but the build123d-side STL on this part comes out as `is_watertight = False` even though the underlying B-rep topology is identical to the 5x15mm sibling — a small tessellation-only gap that doesn't affect any surface-comparison metric (see the part's notes below). All aggregate metrics land in 🟢 EXCELLENT and the part essentially **ties the 5x15mm presentation_post for tightest run of the project**: surface area to 0.020% (vs 0.017% on the 5x15mm — both an order of magnitude better than the globe-family parts), mean distance 0.0033 mm, Hausdorff worst-case 0.0151 mm, bounding box ≤ 0.0032 mm/axis, centroid distance 0.0028 mm. All seven cross-section slices ✅ PASS (worst 0.151% at Y = 19.5 — a region that didn't exist on the shorter 5x15mm part because it sits past that part's Y-extent). This is the first build of the project that was a **near-pure parametric clone** of an already-completed sibling — only the per-CSV-constants and the Y-extent of the profile differ — and the 20-min build time is the lowest of the project so far. See "Notes on zaphod_bot_mec_fbcoup_5x25mm_presentation_post" below for the detail.

`zaphod_bot_mec_fbcoup_fiber_led_coupler` is the sixth part and is **still pending** — it has been allocated a slot in the status table but not yet built. The homing_block (part 7) was built ahead of it.

`zaphod_bot_mec_de_man_out_printer_proto_homing_block` is the seventh part (built ahead of part 6, `zaphod_bot_mec_fbcoup_fiber_led_coupler`, which remains pending) and the first part in the repo that is **not a surface of revolution**. Where the five fibre-coupler parts were all a single profile revolved about an axis, the homing_block is built by **surface extrusion + capping + Boolean trimming** across **six geometry guidelines (G1, G2, G4, G5, G6, with G3 the final export step)** — the first part to run past G4. It is also the first part on a **Y-constant sketch plane** (`Y = 1.0`, exercising the middle branch of the X→Y→Z plane detector that the X-plane globes and Z-plane presentation_posts never reached), the first to parse **three-point circles** (S2: two `r = 1.7` circles concentric with the stadium's two semicircle centres), and the first to exercise the **trim guidelines** — so its area-history log is the first in the project to show **negative Δ-area** steps. The body is a closed "stadium" profile (2 Lines + 2 three-point arcs) surface-extruded straight down 1 mm (zero taper, `Y = 1→0`) and up 1 mm with a 45° inward taper (`Y = 1→2`, the top profile being the base offset inward by `tan 45° · 1 = 1 mm` via a 2-D offset + ruled loft), capped top and bottom, with both caps pierced by two through-holes and two cylindrical tube walls running `Y = 0→2` through them. All aggregate metrics land in 🟢 EXCELLENT, and because every surface is planar, cylindrical or a ruled loft (no curved surface-of-revolution to tessellate), this part posts the **tightest point-distance run of the project by an order of magnitude**: surface area to **0.011%** (505.5111 mm² vs 505.5651 mm²), Hausdorff worst-case **0.0024 mm**, mean distance **0.0002 mm**, bounding box ≤ 0.0006 mm/axis, centroid distance 0.0000 mm. All seven cross-section slices ✅ PASS (worst **0.014%**) — and because the slices run along Y they directly register the 45° taper, with the section perimeter holding at 81.62 mm through the straight lower half then stepping down to 75.97 mm at Y = 1.9 in the tapered upper half. The build123d STL comes out `is_watertight = False` (open surface) while the upstream reference tessellates watertight — the same incidental tessellation asymmetry seen on the 5x25mm presentation_post, with no effect on any surface-comparison metric. See "Notes on zaphod_bot_mec_de_man_out_printer_proto_homing_block" below for the detail.

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

The main script reads the cleaned CSVs and rebuilds the geometry as a series of numbered guidelines (G1, G2, G3, …). The guideline count scales with part complexity — for the 3mm_globe, 5x15mm_1mm_globe_post, 5x15mm_2mm_globe_post, 5x15mm_presentation_post and 5x25mm_presentation_post G1–G4 is enough (G3 is always the final export step); the homing_block (part 7) is the first to run past G4, using six geometry guidelines (G1, G2, G4, G5, G6). For larger parts the count will grow into the dozens, following the same pattern proven on the PICSY companion repo (where individual parts run up to G92). The pattern is:

- **Read CSV** guidelines — parse line / arc / spline / circle / point segments, walk endpoints to detect closed loops or open chains.
- **Build profile wires** — assemble parsed primitives into oriented `Wire` objects. Profiles can be left as construction-only (no patched face) when the next step is a sweep / revolve / loft that consumes the wire directly.
- **Surface-revolve / extrude / loft** — the part-specific geometric operation. For the five fibre-coupler parts (`3mm_globe`, `5x15mm_1mm_globe_post`, `5x15mm_2mm_globe_post`, `5x15mm_presentation_post`, `5x25mm_presentation_post`) this is a 360° revolve of a profile wire about a construction-axis line. The homing_block (part 7) is the first to use the other patterns instead: a straight `BRepPrimAPI_MakePrism` plus a ruled `BRepOffsetAPI_ThruSections` loft for the tapered walls, `Face(wire)` surface patches for the caps, and `BRepAlgoAPI_Cut` / `BRepAlgoAPI_Common` for the two trim steps. For future parts the operation set may grow further, following the extrude / loft / boolean / trim patterns documented in the PICSY companion repo.
- **G3** — always last: apply `.clean()` to remove micro-scars, then export STL + STEP.

Key implementation notes:

- **Cross-platform paths.** `BASE_DIR = Path(__file__).resolve().parent`. No hardcoded absolute paths anywhere.
- **World-coordinate face construction.** All `Edge.make_line(Vector(x, y, z), …)` calls use world coordinates directly. `Plane.XZ.offset()` is avoided because it silently flipped the Z axis in some build123d versions.
- **Plane-detection per CSV (axis-aligned + tilted).** Each CSV sketch's plane is auto-detected per the template's coordinate convention. The detector first tries the axis-aligned case (one of X / Y / Z is constant within tolerance); if no axis is constant, it falls back to a least-squares plane fit via SVD (centroid + smallest-singular-direction normal). For `3mm_globe` both S1 and S2 auto-detect to X = 15.0; for `5x15mm_1mm_globe_post` both auto-detect to X = 3.848; for `5x15mm_2mm_globe_post` both auto-detect to X = 3.847; for `5x15mm_presentation_post` and `5x25mm_presentation_post` S1 auto-detects to **Z = 4.582** (the first Z-constant sketches in the repo) and S2 to X = 4.397 (the S2 line is degenerate enough that both X and Z are constant, and the detector picks the first-found constant axis; the lifted world-space axis line is identical either way). For `zaphod_bot_mec_de_man_out_printer_proto_homing_block` both S1 and S2 auto-detect to **Y = 1.0** — the first Y-constant sketches in the repo, and the first time the detector's middle (Y) branch actually fires; the globes were all X-constant and the presentation_posts Z-constant, so the Y branch had been dead code for the first five parts exactly as the Z branch had been before the 5x15mm presentation_post. The detector returns `('axis', letter, value)` or `('general', origin, normal)` and downstream geometry-builders dispatch on that tuple.
- **Open-chain walking for surfaces of revolution from open profiles.** When an open profile is meant to be revolved (rather than patched into a face), the source CSV gives an *open* chain whose two free endpoints sit on the revolve axis — the on-axis gap is closed by the revolution itself, no explicit edge needed. A small walker traverses the parsed primitives by endpoint adjacency: find the two count-1 endpoints (the chain's free ends), pick one as start, then at each step pick the unused primitive that shares the current "front" endpoint, reversing it if necessary, and continue until the other free end is reached. Used for `3mm_globe` G1 (5 edges: 2 Lines + 3 three-point arcs), `5x15mm_1mm_globe_post` G1 (15 edges: 8 Lines + 5 three-point arcs + 1 five-point spline + 1 programmatic bridge line — see the part's notes below), and `5x15mm_2mm_globe_post` G1 (15 edges: 10 Lines + 5 three-point arcs, clean source CSV). The same walker generalises to mixed line / arc / spline chains.
- **Closed-loop walking for surfaces of revolution from closed profiles.** When the source sketch is a fully enclosed loop (every endpoint has exactly two neighbours, zero free endpoints), the open-chain walker can't be used — it asserts exactly two free endpoints. The closed-loop variant starts from `edges_named[0]` oriented as authored, walks the loop by following unused neighbours at each endpoint key, and validates that the walk returns to the starting key after consuming every primitive. Both walkers share the same fuzzy adjacency machinery (`_kep` 0.01 mm rounding for matching, original unrounded coordinates preserved for downstream edge construction); only the start-condition and termination-condition differ. Used for `5x15mm_presentation_post` G1 and `5x25mm_presentation_post` G1 (both: 12 edges = 8 Lines + 4 three-point arcs, zero free endpoints), and for `zaphod_bot_mec_de_man_out_printer_proto_homing_block` G1 (4 edges = 2 Lines + 2 three-point arcs — a closed "stadium" loop, the shortest closed profile in the repo, and the first time the closed-loop walker drives an extrude rather than a revolve). After the walk the script also asserts `Wire.is_closed` so that any sub-tolerance endpoint mismatch surfaces as a clear error rather than producing a silently-open wire downstream.
- **Three-point arc handling.** The Fusion add-in exports each arc as `(p1, p2, p3) = (start, middle-on-arc, end)`. The build script calls `Edge.make_three_point_arc(start, mid, end)` directly; the `parse_three_point_arcs` helper keeps the middle point as part of the (start, mid, end) tuple so it survives any reversal during chain walking.
- **Three-point circle handling.** The Fusion add-in exports a circle as three points lying on its circumference (`3_point_circle`, columns `(p1, p2, p3)`). The homing_block's `parse_three_point_circles` helper recovers those triples and `circle_from_3_points` solves the circumcircle (centre + radius) in the sketch's `(u, v)` plane; the edge is then built as a full circle on the axis-aligned plane via OCCT `gp_Circ` on a `gp_Ax2` whose normal is the plane's constant axis. First used by `zaphod_bot_mec_de_man_out_printer_proto_homing_block` (S2: two `r = 1.7` circles centred at the stadium's two semicircle centres); none of the five revolve parts had circles in their source CSVs, so this parser is dead code for them and is added only where the `EXPECTED_CIRCLES` block declares it.
- **Spline handling and CSV overflow columns.** Splines exported as `spline_<N>_points` carry all N control points in a single row, but the CSV header only declares the first 9 coordinate columns (X1..Z3). For N > 3 the extra triples land in `csv.DictReader`'s overflow under the `None` key as a flat list of strings. The `_row_all_xyz_triples` helper recovers them so a 5-point spline is built from all 5 control points, not just 3. The edge itself is built with `Edge.make_spline([Vector(x, y, z), …])`, which produces a C2 B-spline through all control points. Used by `5x15mm_1mm_globe_post`; not needed by `3mm_globe`, `5x15mm_2mm_globe_post`, `5x15mm_presentation_post`, `5x25mm_presentation_post` or `homing_block` since none of these parts have splines in their source CSVs — those scripts can skip the spline parser and overflow handler entirely, keeping the G1 section noticeably simpler.
- **Tapered walls without `BRepOffsetAPI_MakeDraft`.** A 45° draft "extrude these edges and shrink the profile" is the homing_block's one genuinely new geometric operation, and OCCT's `BRepOffsetAPI_MakeDraft` turned out to be the wrong tool for it on a bare wire (it tapers *outward* regardless of angle sign, and its `Perform(length)` measures along the slanted draft surface so a 45° draft only rises `length · cos 45°` along the pull axis). The build script instead constructs the taper explicitly: a 2-D in-plane offset of the base profile by `−tan(angle) · height` (`BRepOffsetAPI_MakeOffset`; for the homing_block, `−1.0 mm`), lifted to the end plane, then a ruled loft (`BRepOffsetAPI_ThruSections` with `isSolid = False, ruled = True`) between the base wire and the offset wire. The straight (zero-taper) wall is a plain `BRepPrimAPI_MakePrism`. This gives exact control over both taper direction (offset sign) and wall height (lift distance). See the part's notes below.
- **Endpoint precision through the chain walker.** Adjacency matching for chain walking uses a `_kep` function that rounds each `(u, v)` endpoint to 0.01 mm, so primitives that meet "near enough" join up despite small floating-point drift in the source CSV. But the *rounded* keys must not leak into actual `Edge.make_*` calls — OCCT-level wire construction is much stricter than the rounded match (it expects coincident vertices at floating-point precision), and a 0.001 mm endpoint mismatch is enough to produce a "Edges are disconnected" error from `Wire(...)`. The walker keeps the original unrounded `(u, v)` tuples alongside the rounded keys, and downstream edge construction always uses the originals. The same rule applies to any programmatic bridge insertion: bridge endpoints must reuse the *exact* unrounded `(u, v)` of the matching existing primitive, not the rounded adjacency key.
- **Axis-snap for noisy construction lines.** Fusion's add-in sometimes exports a "constant-along-one-axis" construction line with a small wobble in that axis (the `3mm_globe` S2 axis has a 0.018 mm Y-wobble; the four later revolve parts' S2 lines are clean). The build script detects when a component varies by less than `AXIS_SNAP_MM = 0.05 mm` and snaps that component to its mean, so the revolve axis is perfectly axis-aligned and the resulting surface of revolution has no tilt. The homing_block has no construction-axis line at all (it is not a revolve), so this snap is not exercised there.
- **`build123d.revolve()` quietly fails on bare wires.** Given a bare `Wire` (open or closed), build123d's high-level `revolve()` returns an empty `Compound` without raising. The five revolve parts go directly to OCCT's `BRepPrimAPI.BRepPrimAPI_MakeRevol(wire, gp_Ax1, angle, copy=True)` as the primary path, with per-edge revolve as a fallback and build123d's `revolve()` as a last-resort fallback. The primary path produces one face per profile primitive (5 faces for the 3mm_globe, 15 faces for both globe-posts, 12 faces for both presentation_posts). The homing_block sidesteps this entirely — it never revolves — but it hit the *same class* of "the high-level wrapper degenerates on a bare 1-D input" problem with `BRepOffsetAPI_MakeDraft` (see the tapered-walls note above), and resolved it the same way: drop to an explicit lower-level construction with full control over the inputs.
- **Boolean trims use helper tools that never reach the export.** The homing_block's two trim guidelines (G5 cap-holes, G6 tube-height) each need a cutting body — a solid cylinder for the holes, a large `Y = 0..2` slab box for the tube trim. Those tools are pure scaffolding: they are built as local variables, fed to `BRepAlgoAPI_Cut` / `BRepAlgoAPI_Common`, and only the resulting trimmed faces are collected back into `stage_pieces`. The tools are never added to the compound and never exported, which keeps the final STL clean and the area-history honest.
- **Post-revolve scale fix for CSV-vs-reference unit mismatch (3mm_globe only).** The Fusion add-in's CSV export for `3mm_globe` came out at 10× the reference part's scale (CSV span ~30 mm vs reference span ~3 mm). The fastest fix is a single post-revolve scale step in G4: build the surface at the CSV's native scale, then apply `gp_Trsf.SetScale(origin, 0.1)` via `BRepBuilderAPI_Transform` to every face. Every other part so far came out at the correct reference scale and needs no post-build scaling.
- **Filename guideline-range convention.** Output filenames carry the active guideline range (e.g. `zaphod_bot_mec_fbcoup_3mm_globe_G_1_4.stl`, `zaphod_bot_mec_de_man_out_printer_proto_homing_block_G_1_6.stl`) so multiple checkpoint exports coexist without clobbering each other.
- **Per-guideline checkpoints.** Three top-of-file flags (`VIEW_AT`, `STOP_AFTER_VIEW`, `EXPORT_AT_CHECKPOINT`) let you halt at any guideline, send the cumulative state to the OCP viewer on port 3939, and optionally export `<part>_G_1_N.{stl,step,txt}` mid-pipeline for inspection. For the homing_block the valid checkpoint numbers are 1, 2, 4, 5, 6 (G3 is the final export step).
- **Surface-area tracking.** Every guideline's cumulative surface area is recorded. Both the main summary and a standalone `<part>_area_history_G_1_N.txt` document how area accumulates and — as of the homing_block (part 7), the first part with trim guidelines — *decreases*. The homing_block's G5 and G6 are the first negative Δ-area steps in the project: G5 = −36.31 mm² (two `r = 1.7` holes per cap, both caps = `4 · π · 1.7²`) and G6 = −42.72 mm² (trimming each tube wall from 4 mm to 2 mm of height). For complex parts this audit trail is the single most valuable debugging tool — any unexpected Δ-area at a downstream guideline points straight back to the upstream guideline that introduced the wrong geometry, and on a trim step the expected delta has a closed-form sign and magnitude you can check against on the first run.

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

### A note on `zaphod_bot_mec_fbcoup_5x15mm_2mm_globe_post` — why it took 1 hour

The 5x15mm_2mm_globe_post is the third part and is the slightly-larger sibling of the 1mm_globe_post — same 4-guideline structure (G1 = S1 open profile, G2 = S2 axis line, G4 = surface-revolve, G3 = final export), same complexity band in the source CSV (15 primitives versus the 1mm-post's 14), but **structurally cleaner**: 10 Lines + 5 three-point arcs and no splines, and the source CSV is complete (no missing-bridge defect). The 1 hour was split roughly as:

- **~10 min** dropping the existing 1mm_globe_post script into the new folder, swapping the CSV paths via `BASE_DIR`, swapping the expected-primitive counts (`EXPECTED_LINES = 10`, `EXPECTED_ARCS = 5`, no spline count), and confirming the plane auto-detector handles X = 3.847 the same way it handled X = 3.848. The helper infrastructure that *did* survive — CSV reading, plane detection, `world_vec_axis`/`in_plane_uv`, `parse_line_segments`, `parse_three_point_arcs`, `walk_open_chain`, the checkpoint scaffold, the G4 OCCT revolve path — came across unchanged.
- **~15 min** deciding what to *remove* from the 1mm-post script before running. The 1mm-post script carries three pieces of machinery that this part does not need: (a) the spline parser (`parse_splines`), (b) the `_row_all_xyz_triples` overflow handler for spline rows with > 3 control points, and (c) the entire bridge-insertion block. All of that is dead code for a clean 15-primitive open chain, and leaving it in would have made the file ~120 lines longer for no benefit. Removed everything not used. The 2mm-post script ends up shorter than the 1mm-post script despite covering one more primitive — which is the right outcome when the source CSV is cleaner.
- **~10 min** on the first dry run. CSV freshness banner printed the two CSVs at 907 B and 97 B. Plane detector landed on `X = 3.847` for both sketches as expected. Parser counted 10 lines + 5 arcs in S1 and 1 line in S2 — passed the `EXPECTED_*` guard. Walker found exactly 2 free endpoints at `(Y=17.0, Z=4.008)` from Step 15's line and `(Y=21.916, Z=4.008)` from Step 1's arc — both on the revolve axis at Z=4.008. No bridge needed, no precision-leak path exercised, chain walked all 15 edges first try.
- **~20 min** on G4 and the comparison run. The OCCT `BRepPrimAPI_MakeRevol(wire, …)` path produced 15 faces in one shot at total area 414.11 mm² — close to the reference STL's 413.49 mm². `.clean()` ran without warning, the STL+STEP exports landed without issue, and the comparison script reported every aggregate metric in the 🟢 EXCELLENT band: surface area 0.151%, mean distance 0.0032 mm, Hausdorff 0.0098 mm, bounding box ≤ 0.005 mm/axis, centroid distance 0.0024 mm. All seven cross-section slices passed under 0.283% perimeter error (worst slice at Y = 17.533, the narrow neck just before the globe terminates).
- **~5 min** cross-checking the result against the 1mm-post numbers to confirm the difference is just the globe diameter and not a regression somewhere.

Two notes worth recording for future parts:

- **A cleaner source CSV genuinely saves time.** The 1mm-post took 1 h 15 min and ~45 min of that was the spline parser + the bridge insertion + the rounded-key precision-leak debug. The 2mm-post had neither feature, ran on the first dry pass, and finished in 1 hour even though it has *more* primitives in S1. The bulk of the template's per-part time is spent on CSV-extraction defects, not on geometry complexity.
- **Strip what you don't need.** Each part script should declare its primitive set in a single `EXPECTED_*` block near G1 and carry only the parsers / repairers that block requires. The 2mm-post script's G1 section is ~80 lines vs the 1mm-post's ~200, and you can see the geometry rules at a glance.

### A note on `zaphod_bot_mec_fbcoup_5x15mm_presentation_post` — why it took 30 min

The 5x15mm_presentation_post is the fourth part and was the fastest build of the project at the time it landed. Same 4-guideline structure as the previous three globe-family parts (G1 = S1 profile, G2 = S2 axis line, G4 = surface-revolve, G3 = final export), but the source CSV exercises two new branches of the template that earlier parts never reached: the profile is a single **CLOSED loop** (12 primitives — 8 Lines + 4 three-point arcs — every endpoint with degree 2, zero free endpoints) and the sketch plane is **Z-constant** (`Z = 4.582`). Both are first-of-their-kind in the repo. The 30 min was split roughly as:

- **~5 min** dropping the existing 2mm-post script into the new folder, swapping CSV paths via `BASE_DIR`, swapping the expected-primitive counts (`EXPECTED_LINES = 8`, `EXPECTED_ARCS = 4`), and updating the header docstring. The plane-detection branch for Z-constant sketches was already present and tested in the PICSY companion repo, so no detector change was needed.
- **~10 min** adding the closed-loop walker variant. The existing `walk_open_chain` requires exactly 2 free endpoints; this part has 0, so a parallel `walk_closed_chain` was added that starts from `edges_named[0]` as authored, follows unused neighbours at each endpoint key, and validates the walk returns to the starting key after consuming every primitive. After the walk, the script also asserts `Wire.is_closed`.
- **~10 min** on the first dry run and the G4 / comparison run. CSV freshness banner printed the two CSVs at 727 B and 95 B. Plane detector landed on `Z = 4.582` for S1 and `X = 4.397` for S2. Closed-loop walker visited all 12 edges first try, returned to the start key, and `Wire.is_closed` confirmed True. G4 produced 12 faces via `BRepPrimAPI_MakeRevol(wire, …)` at total area ~524.5 mm². `.clean()` ran without warning, STL+STEP exports landed cleanly.
- **~5 min** on the comparison run. Every aggregate metric landed in 🟢 EXCELLENT and this part posted the tightest aggregate numbers of the project at the time: surface area 524.5266 mm² vs reference 524.4362 mm² (**0.017%** error), Hausdorff 0.0144 mm, mean distance 0.0031 mm, bounding box ≤ 0.0032 mm/axis, centroid distance 0.0026 mm. All seven cross-section slices ≤ 0.178% perimeter error (worst at Y = 13.0). Both meshes register as watertight closed solids in trimesh.

Three notes worth recording for future parts:

- **A second walker variant is a 10-minute change once the first one is in place.** The open-chain walker did the heavy lifting; the closed-loop variant reuses every piece of it and only differs in the start condition and termination condition. The next walker variant should be in the same shape: share `_kep`, share the closure-based oriented-edge builders, share the unrounded-coords discipline, and only specialise the start/terminate logic.
- **The plane auto-detector being axis-agnostic paid off here.** Every prior part lived on an X-constant plane, so the Y- and Z- branches of `detect_sketch_plane` were dead code paths for the first three runs. They turned out to be correct anyway because the detector was written generically (iterate X → Y → Z, first one constant within `EPSILON_MM` wins). The same generic discipline later paid off again on the homing_block, whose Y-constant plane was the first to hit the middle branch.
- **Watertight comparison output is incidental, not engineered.** The build123d intermediate is a `Compound` of `Face` objects, not a `Solid`. The fact that the exported STL happens to register as watertight in trimesh is a property of the *tessellated mesh*, not of the build123d topology. For comparison purposes the surface-vs-surface metrics (area, Hausdorff, slices) apply unchanged.

### A note on `zaphod_bot_mec_fbcoup_5x25mm_presentation_post` — why it took 20 min

The 5x25mm_presentation_post is the fifth part and was the fastest build of the project to that point. It is the longer sibling of the 5x15mm_presentation_post — 30 mm long along Y instead of 20 mm — built from a **structurally identical source sketch**: same closed-loop profile of 8 Lines + 4 three-point arcs = 12 primitives on the same Z = 4.582 plane, same revolve axis at X = 4.397 outside the profile's X-range, same torus-topology shell. The only differences in the source CSVs are (a) the profile's Y-range now spans 0.0..30.0 instead of 0.0..20.0, and (b) the S2 axis-line endpoints move proportionally to `(4.397, 30.0)→(4.397, 27.038)`. The 20 min was split roughly as:

- **~5 min** dropping the existing 5x15mm_presentation_post script into the new folder, swapping the CSV paths via `BASE_DIR`, and updating the header docstring. The expected-primitive counts carry across unchanged because S1's topology is bit-for-bit identical to the 5x15mm sibling. The entire helper infrastructure came across without a single character changed.
- **~3 min** on a pre-flight connectivity check: tabulating the 12 primitive endpoints by `_kep` rounded key showed exactly 12 distinct keys, each shared by exactly 2 primitives, zero free endpoints — the same degree-2 closed-loop signature as the 5x15mm variant.
- **~7 min** on the first dry run and the G4 / comparison run. CSV freshness banner printed the two CSVs at 731 B and 97 B. Plane detector landed on `Z = 4.582` for S1 and `X = 4.397` for S2. Closed-loop walker visited all 12 edges first try. G4 produced 12 faces via `BRepPrimAPI_MakeRevol(wire, …)` at total area ~773.3 mm². `.clean()` ran without warning, STL+STEP exports landed cleanly.
- **~5 min** on the comparison run. Every aggregate metric landed in 🟢 EXCELLENT: surface area 773.2635 mm² vs reference 773.1088 mm² (**0.020%** error), Hausdorff 0.0151 mm, mean distance 0.0033 mm, bounding box ≤ 0.0032 mm/axis, centroid distance 0.0028 mm. All seven cross-section slices ≤ 0.151% perimeter error (worst at Y = 19.5 — a region that didn't exist on the shorter 5x15mm part). One asymmetry vs the 5x15mm sibling: the upstream reference STL registers as watertight in trimesh, but the build123d-side STL comes out as `is_watertight = False` — a tessellation artefact, not a geometry difference, with no effect on any surface-comparison metric.

Three notes worth recording for future parts:

- **A near-pure parametric clone of a sibling is a 5-minute build.** The 5x25mm_presentation_post differs from the 5x15mm in two CSV constants and nothing else. The build-side budget for variant parts whose differences boil down to source-CSV constants should be ~10–20 minutes total, dominated by running the comparison script and writing the README entry.
- **When a sibling part adds Y-extent, the new cross-section slices test new ground.** The slice runner picks 7 Y-planes from each mesh's own bounds, so three of the 5x25mm slices sit entirely past the 5x15mm sibling's 20 mm Y-extent — genuinely new geometry being validated against the upstream STL for the first time.
- **Tessellation closure on revolved closed-wire shells is not stable across sibling runs.** Same code, same operation, slightly different mesh outcome (5x15mm watertight, 5x25mm not). Watertightness of the *tessellated mesh* is incidental and shouldn't be part of the acceptance criteria for a surface part.

### A note on `zaphod_bot_mec_de_man_out_printer_proto_homing_block` — why it took 50 min

The homing_block is the seventh part and the first real departure from the surface-of-revolution template that carried the first five parts. There is no revolve here at all: the part is built by surface-extruding a closed profile in two directions, patching the open ends, and Boolean-trimming holes and overshoot. It is also the first part to run past G4 — six geometry guidelines (G1, G2, G4, G5, G6; G3 stays the final export step). The 50 min was split roughly as:

- **~10 min** standing up the new folder and deciding how much of the presentation_post script survived. The whole CSV / plane / walker layer came across unchanged — CSV reading, `detect_sketch_plane`, `world_vec_axis`/`in_plane_uv`, `parse_line_segments`, `parse_three_point_arcs`, `walk_closed_chain`, the checkpoint scaffold and area tracker. The closed-loop walker that the presentation_posts introduced handles this part's 4-primitive stadium (2 Lines + 2 three-point arcs) without modification. The plane detector landed on `Y = 1.0` for both S1 and S2 — the first Y-constant sketches in the repo, and the first time the middle branch of the X→Y→Z fall-through actually fires (the globes were X-constant, the presentation_posts Z-constant). What did *not* carry across was the entire G4 revolve block — `BRepPrimAPI_MakeRevol`, the per-edge and `build123d.revolve()` fallbacks, the axis-snap — none of it applies to an extrude/cap/trim part, so it was removed wholesale and replaced with the new operations below.

- **~15 min** on the tapered upper wall, which was the one genuine fight. The obvious tool for "extrude these edges with a 45° taper" is OCCT's `BRepOffsetAPI_MakeDraft` on the profile wire — but on a bare closed wire it misbehaved twice over: it tapered *outward* (the bbox grew) regardless of whether the draft angle was +45° or −45°, and `Perform(1.0)` produced only a 0.707 mm vertical rise instead of 1.0 mm, because its length argument is measured along the slanted draft direction, not along the pull axis. Rather than fight the draft API's sign-and-length conventions, I built the taper explicitly: take a 2-D in-plane offset of the base profile by −1.0 mm (`BRepOffsetAPI_MakeOffset`; `tan 45° · 1 mm = 1 mm` inward, so the top stadium is radius 3.5 with straight runs at Z = 1 and Z = 8), lift that offset wire to Y = 2, and `BRepOffsetAPI_ThruSections` (isSolid = False, ruled = True) a ruled loft between the base wire at Y = 1 and the shrunk wire at Y = 2. The straight lower wall is a plain `BRepPrimAPI_MakePrism` of the base wire by −1 mm in Y. Exact direction and height control, and the two wall shells meet cleanly at the Y = 1 base profile.

- **~10 min** on the other first-of-their-kind pieces: a three-point-circle parser (circumcircle from the three S2 points → centres (4.5, 4.5) and (20.5, 4.5), r = 1.7, built as full-circle edges on the Y-plane), the two cap patches (`Face(wire)` at Y = 0 and Y = 2), and the two trim guidelines. Cap holes (G5) are a Boolean cut of each cap face against solid cylinder *tools*; the tube-wall trim (G6) is a `BRepAlgoAPI_Common` of each full-length tube wall against a large Y = 0..2 slab box. The cut tools and the slab box are helpers only — never added to `stage_pieces`, never exported.

- **~10 min** on the first dry run and the area history. This is the first part whose area log goes *down*: G1 +141.07 (8 wall faces — 4 straight + 4 tapered), G2 +358.10 (two caps), G4 +85.44 (two full-length tube walls), then **G5 −36.31** (two `r = 1.7` holes per cap = `4 · π · 1.7²`) and **G6 −42.72** (trimming each tube from 4 mm to 2 mm of height). Seeing the two negative deltas come out at exactly the expected magnitudes was the fastest possible confirmation that the trims removed the right geometry and nothing else. Final surface area 505.59 mm² across 12 faces.

- **~5 min** on the comparison run, which came back as the tightest of the project: surface area 0.011%, Hausdorff 0.0024 mm, mean distance 0.0002 mm — an order of magnitude inside the revolve parts' 0.005–0.015 mm Hausdorff band. The reason is geometric: every surface on this part is planar, cylindrical or a ruled loft, all of which tessellate almost identically between the build123d export and the upstream reference, whereas a surface of revolution carries curvature that the two tessellators approximate slightly differently. All seven Y-slices passed at ≤ 0.014%, and because they run along the taper axis they double as a direct check on the 45° draft — the section perimeter holds at 81.62 mm through the straight lower half and steps down to 75.97 mm at Y = 1.9. As on the 5x25mm presentation_post, the build123d STL comes out `is_watertight = False` while the upstream reference tessellates watertight; it has no effect on any metric.

Three notes worth recording for future parts:

- **`BRepOffsetAPI_MakeDraft` is the wrong tool for a controlled taper on a bare wire.** It tapers outward irrespective of angle sign (the direction is governed by the wire's planar orientation, not the sign you pass), and its `Perform(length)` measures along the slanted draft surface, so a 45° draft only rises `length · cos 45°` along the pull axis. For a predictable tapered wall, skip the draft API: compute the end profile directly as a 2-D in-plane offset of the start profile by `tan(angle) · height`, lift it to the end plane, and ruled-loft between the two wires. You get exact control over both the taper direction (offset sign) and the wall height (lift distance), and the result is a clean ruled shell.

- **Trim guidelines are where the area-history audit trail finally earns its keep.** For the first five revolve parts the cumulative-area log only ever increased, so a wrong Δ was easy to spot but rare. The moment trims arrive, the expected delta has a *sign and a magnitude* you can predict in closed form — a hole cut is `−π r²` per hole, a height trim is `−(removed length · perimeter)` — so any trim that bites the wrong region or the wrong amount shows up instantly as a delta that doesn't match the arithmetic. On this part G5 = −36.31 mm² (= `4 · π · 1.7²`) and G6 = −42.72 mm² matched prediction to the third decimal on the first run. Build the predicted delta into the guideline's print line for any future trim step.

- **Keep Boolean tools out of `stage_pieces`.** A trim needs a cutting body (a solid cylinder, a slab box) that is pure scaffolding — it must not survive into the exported compound or the area history. The discipline that keeps the final STL clean and the area log honest is to construct tools as local variables, apply the Boolean, collect only the resulting faces back into `stage_pieces`, and let the tools fall out of scope. The same rule will apply to every future extrude / loft / boolean / trim part: the only shapes that reach the export are the ones that are actually part of the model surface.

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

The **cross-section slice comparison** has proven especially valuable on complex parts: it cuts both meshes at multiple Y-plane positions (auto-derived from mesh bounds) and compares the outline perimeter at each cut. Aggregate metrics like Hausdorff or mean-distance can mask a 1–2% feature-level discrepancy because the affected region is small compared to the total surface — the slice test bypasses this by comparing geometry at specific cross-sections. On the six completed parts every slice has passed comfortably: ≤ 0.24% perimeter error on the 1mm-post, ≤ 0.283% on the 2mm-post, ≤ 0.178% on the 5x15mm presentation_post, ≤ 0.151% on the 5x25mm presentation_post, and ≤ 0.014% on the homing_block — now the tightest slice run in the project by a wide margin, since its cross-sections are simple planar / cylindrical outlines rather than revolved curves (and, running along the taper axis, they also confirm the 45° draft, with the perimeter stepping down from 81.62 mm to 75.97 mm across the tapered upper half). The worst slice on each globe-post lands at the narrow neck just before the globe terminates, where a small absolute deviation resolves to a relatively larger percentage of a small perimeter.

For **solid parts** the original volume + symmetric-volume-difference comparison from the [Thor assembly project](https://github.com/avajones081196/Ava_AngelLM_Thor_Art1_build123d) is used. Note that "solid" here refers to how the part is *built* in build123d (a `Solid` object or a face that revolves/extrudes into one), not whether the exported STL happens to tessellate as a watertight closed mesh — surface-built parts may *or may not* register as watertight in mesh tools depending on tessellation luck (the 5x15mm presentation_post did; the 5x25mm and the homing_block did not), but either way they are still surface-built and use the surface comparison script.

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

The same layout is used for every part. Output filenames carry the active guideline range so checkpoint exports do not clobber each other — the homing_block, which runs to G6, uses the `G_1_6` suffix throughout (`zaphod_bot_mec_de_man_out_printer_proto_homing_block_G_1_6.stl`, `..._summary_G_1_6.txt`, `..._area_history_G_1_6.txt`, `..._build123d_vs_reference_G_1_6.txt`).

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

Set `VIEW_AT = None` for a clean end-to-end run that only writes the final outputs. For the homing_block the valid `VIEW_AT` checkpoint numbers are 1, 2, 4, 5, 6 (G3 is the final export step).

---

## Acceptance Criteria — How the Ratings Are Set

For surface parts (e.g. `zaphod_bot_mec_fbcoup_3mm_globe`, `zaphod_bot_mec_fbcoup_5x15mm_1mm_globe_post`, `zaphod_bot_mec_fbcoup_5x15mm_2mm_globe_post`, `zaphod_bot_mec_fbcoup_5x15mm_presentation_post`, `zaphod_bot_mec_fbcoup_5x25mm_presentation_post`, `zaphod_bot_mec_de_man_out_printer_proto_homing_block`), the rating thresholds are aligned with typical FDM 3D-printer manufacturing tolerances rather than CAD-tight micrometre tolerances, since the zaphod-bot parts are designed for FDM printing. A well-tuned consumer FDM printer (Prusa, Bambu, etc.) has roughly 0.1–0.5 mm positional accuracy, with industry rule-of-thumb specs of ±0.5 mm. Anything below that floor is below what the manufacturing process can resolve, so it counts as "indistinguishable from the original" in practice.

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

A part needs to pass **every aggregate metric** (surface area, bounding box, centroid, Hausdorff, mean distance) to earn the ✅ Complete badge. The cross-section slice test is treated as a confirmation test rather than a strict gate: if all aggregate metrics pass AND the Hausdorff worst-case is under the FDM print-tolerance floor of 0.5 mm, then an isolated 🟠 ACCEPTABLE slice (one slice in the 2–5% band) is treated as a known minor variance rather than a failure.

A part is marked ⚠ Review required (rather than ✅ Complete) if any aggregate metric fails, if Hausdorff exceeds 0.5 mm, or if more than one cross-section slice fails — in any of those cases the deviation is print-visible.

Surface-area % thresholds are kept tight since that metric is a unitless ratio and not bounded by print tolerance.

These mirror reverse-engineering / metrology defaults adjusted for FDM manufacturing (vs. machined-tight CAD comparison, where ≤ 0.05 mm thresholds would apply). Per-part the user may adjust thresholds at the top of the comparison script.

---

## Notes on the Reference STLs

The reference STLs come from upstream tessellation by the zaphod-bot repo's authors. Some are not perfectly closed meshes — `is_watertight` may report `False`. This is normal: STL exports often leave non-coincident edges across feature boundaries. For the comparison script this is fine because surface comparison does not require closure. The inverse also happens — the homing_block's upstream reference tessellates watertight while the build123d-side STL does not — and is equally harmless for surface comparison.

---

## License

This repo follows the upstream [zaphod-bot repository's license](https://github.com/Scottapotamas/zaphod-bot). All build123d reconstruction code and comparison utilities are provided as-is for educational and reverse-engineering purposes.
