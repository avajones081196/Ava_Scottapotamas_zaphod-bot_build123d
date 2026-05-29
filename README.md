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
| 8 | zaphod_bot_mec_de_man_out_printer_proto_bearing_link_3 | ✅ Complete | 0.043% | 0.0008 | 0.0234 | 2 h |
| ... | | | | | | |
| 21 | — | ⏳ Pending | | | | |

`zaphod_bot_mec_fbcoup_3mm_globe` is the first part. It is a 3 mm globe surface of revolution built from two source sketches (S1 profile + S2 axis). All five aggregate metrics land in the 🟢 EXCELLENT band: surface area to 0.18%, mean point distance 0.0019 mm, Hausdorff worst-case 0.0051 mm, bounding box ≤ 0.004 mm/axis, centroid distance 0.0009 mm. See "Notes on zaphod_bot_mec_fbcoup_3mm_globe" below for the build detail behind it.

`zaphod_bot_mec_fbcoup_5x15mm_1mm_globe_post` is the second part. It is a ~20.8 mm long globe-post — a slender body with cylindrical, conical and toroidal sections terminating in a small 1 mm globe — built as a surface of revolution from the same two-sketch pattern (S1 open profile + S2 axis line). Geometry is more complex than the 3mm_globe: 14 primitives in the source CSV instead of 5, including the first **spline** primitive in the repo and a missing-bridge defect in the source CSV that has to be auto-repaired. All aggregate metrics land in 🟢 EXCELLENT: surface area to 0.14%, mean distance 0.0029 mm, Hausdorff worst-case 0.0092 mm, bounding box ≤ 0.006 mm/axis, centroid distance 0.0020 mm. All seven cross-section slices ✅ PASS. See "Notes on zaphod_bot_mec_fbcoup_5x15mm_1mm_globe_post" below for the detail.

`zaphod_bot_mec_fbcoup_5x15mm_2mm_globe_post` is the third part. It is the slightly-larger sibling of the 1mm-globe-post — a ~21.9 mm long globe-post terminating in a 2 mm globe instead of a 1 mm one — built from the same two-sketch surface-of-revolution pattern (S1 open profile + S2 axis line). Geometry is in the same complexity band as the 1mm-post (15 primitives in S1 vs 14) but structurally cleaner: **10 Lines + 5 three-point arcs and no splines**, and the source CSV is complete (no missing-bridge defect — the 15-primitive chain walks straight through with exactly 2 free endpoints on the revolve axis at `Z = 4.008`). All aggregate metrics land in 🟢 EXCELLENT: surface area to 0.151%, mean distance 0.0032 mm, Hausdorff worst-case 0.0098 mm, bounding box ≤ 0.005 mm/axis, centroid distance 0.0024 mm. All seven cross-section slices ✅ PASS (worst 0.283%). See "Notes on zaphod_bot_mec_fbcoup_5x15mm_2mm_globe_post" below for the detail.

`zaphod_bot_mec_fbcoup_5x15mm_presentation_post` is the fourth part. It is a 20 mm-long fibre-coupler post in the same body-shape family as the two globe-posts but **structurally different on two axes**: the profile is a single **CLOSED** loop (not an open chain terminating on the revolve axis), and the source sketch lies on a **Z-constant plane** (`Z = 4.582`) rather than the X-constant planes used by every previous part. Same two-sketch pattern (S1 profile + S2 axis line); the closed wire revolved 360° about an axis line that sits outside the profile's X-range produces a torus-topology shell that happens to come out **watertight** when tessellated (both the build123d STL and the upstream reference STL register as closed solids in trimesh). All aggregate metrics land in 🟢 EXCELLENT, and this is the tightest run of the project so far on every aggregate: surface area to 0.017% (an order of magnitude better than the three globe-family parts), mean distance 0.0031 mm, Hausdorff worst-case 0.0144 mm, bounding box ≤ 0.0032 mm/axis, centroid distance 0.0026 mm. All seven cross-section slices ✅ PASS (worst 0.178% at Y = 13.0 — the best slice run of the four parts so far). See "Notes on zaphod_bot_mec_fbcoup_5x15mm_presentation_post" below for the detail.

`zaphod_bot_mec_fbcoup_5x25mm_presentation_post` is the fifth part. It is the **longer sibling** of the 5x15mm presentation_post — a 30 mm-long fibre-coupler post (10 mm longer along Y than its 5x15mm counterpart) built from a **structurally identical** source sketch: same closed-loop profile of **8 Lines + 4 three-point arcs = 12 primitives** on a **Z = 4.582 plane**, same revolve-axis at `X = 4.397` on the same plane outside the profile's X-range (~0.4..3.32), same torus-topology shell. The only differences in the source CSVs vs the 5x15mm variant are (a) the profile's Y-range now spans `0.0..30.0` instead of `0.0..20.0`, and (b) the S2 axis-line endpoints move proportionally to `(4.397, 30.0) → (4.397, 27.038)`. The upstream reference STL tessellates watertight as before, but the build123d-side STL on this part comes out as `is_watertight = False` even though the underlying B-rep topology is identical to the 5x15mm sibling — a small tessellation-only gap that doesn't affect any surface-comparison metric (see the part's notes below). All aggregate metrics land in 🟢 EXCELLENT and the part essentially **ties the 5x15mm presentation_post for tightest run of the project**: surface area to 0.020% (vs 0.017% on the 5x15mm — both an order of magnitude better than the globe-family parts), mean distance 0.0033 mm, Hausdorff worst-case 0.0151 mm, bounding box ≤ 0.0032 mm/axis, centroid distance 0.0028 mm. All seven cross-section slices ✅ PASS (worst 0.151% at Y = 19.5 — a region that didn't exist on the shorter 5x15mm part because it sits past that part's Y-extent). This is the first build of the project that was a **near-pure parametric clone** of an already-completed sibling — only the per-CSV-constants and the Y-extent of the profile differ — and the 20-min build time is the lowest of the project so far. See "Notes on zaphod_bot_mec_fbcoup_5x25mm_presentation_post" below for the detail.

`zaphod_bot_mec_fbcoup_fiber_led_coupler` is the sixth part and is **still pending** — it has been allocated a slot in the status table but not yet built. The homing_block (part 7) and the bearing_link_3 (part 8) were both built ahead of it.

`zaphod_bot_mec_de_man_out_printer_proto_homing_block` is the seventh part (built ahead of part 6, `zaphod_bot_mec_fbcoup_fiber_led_coupler`, which remains pending) and the first part in the repo that is **not a surface of revolution**. Where the five fibre-coupler parts were all a single profile revolved about an axis, the homing_block is built by **surface extrusion + capping + Boolean trimming** across **six geometry guidelines (G1, G2, G4, G5, G6, with G3 the final export step)** — the first part to run past G4. It is also the first part on a **Y-constant sketch plane** (`Y = 1.0`, exercising the middle branch of the X→Y→Z plane detector that the X-plane globes and Z-plane presentation_posts never reached), the first to parse **three-point circles** (S2: two `r = 1.7` circles concentric with the stadium's two semicircle centres), and the first to exercise the **trim guidelines** — so its area-history log is the first in the project to show **negative Δ-area** steps. The body is a closed "stadium" profile (2 Lines + 2 three-point arcs) surface-extruded straight down 1 mm (zero taper, `Y = 1→0`) and up 1 mm with a 45° inward taper (`Y = 1→2`, the top profile being the base offset inward by `tan 45° · 1 = 1 mm` via a 2-D offset + ruled loft), capped top and bottom, with both caps pierced by two through-holes and two cylindrical tube walls running `Y = 0→2` through them. All aggregate metrics land in 🟢 EXCELLENT, and because every surface is planar, cylindrical or a ruled loft (no curved surface-of-revolution to tessellate), this part posts the **tightest point-distance run of the project by an order of magnitude**: surface area to **0.011%** (505.5111 mm² vs 505.5651 mm²), Hausdorff worst-case **0.0024 mm**, mean distance **0.0002 mm**, bounding box ≤ 0.0006 mm/axis, centroid distance 0.0000 mm. All seven cross-section slices ✅ PASS (worst **0.014%**) — and because the slices run along Y they directly register the 45° taper, with the section perimeter holding at 81.62 mm through the straight lower half then stepping down to 75.97 mm at Y = 1.9 in the tapered upper half. The build123d STL comes out `is_watertight = False` (open surface) while the upstream reference tessellates watertight — the same incidental tessellation asymmetry seen on the 5x25mm presentation_post, with no effect on any surface-comparison metric. See "Notes on zaphod_bot_mec_de_man_out_printer_proto_homing_block" below for the detail.

`zaphod_bot_mec_de_man_out_printer_proto_bearing_link_3` is the eighth part (built ahead of part 6, `zaphod_bot_mec_fbcoup_fiber_led_coupler`, which remains pending) and the first part in the repo built by **genuine solid Boolean modelling** rather than a surface of revolution or a surface-extrude/cap. Where the homing_block (part 7) extruded a single profile and trimmed it, the bearing_link_3 is a **cross-yoke**: two perpendicular "link" arms — each a closed profile terminating in a bored circular eye — extruded into two separate solids and **intersected** (`G2: G1 ∩ G2`) to form the body. It is the first part to use a body-forming **intersection**, the first with **two perpendicular through-bores** (one along Z, one along Y), the first to **fillet** and **chamfer** real B-rep edges, the first to **un-stitch** a finished solid into a surface body, and the first to run all the way to **G7** (seven geometry guidelines: G1, G2, G4, G5, G6, G7, with G3 the final export step). It is also the first part to **mix sketch-plane orientations within a single part** — S1/S3 are **Z-constant** (`Z = 15.0` / `9.525`) and S2/S4 are **Y-constant** (`Y = −2.0` / `9.55`), so a single part exercises both the Z- and Y-branches of the plane detector — and the first to consume a **non-coplanar CSV**: S5 is not a sketch at all but a 3-D set of 16 three-point arcs tracing the model's outer edges, with an SVD plane-fit residual of ~5.2 mm, sampled into a point cloud and used purely to *select* which body edges to fillet (see notes). Build order is `G1 → G2 → G4 → G5 → G6 → G7`, with G3 (export) last. All aggregate metrics land in 🟢 EXCELLENT: surface area to **0.043%** (936.7036 mm² vs 937.1066 mm²), Hausdorff worst-case **0.0234 mm**, mean distance **0.0008 mm**, bounding box ≤ 0.0014 mm/axis, centroid distance **0.0000 mm**. All seven cross-section slices ✅ PASS (worst **0.042%** at Y = 7.050). Unusually for a surface-exported part, **both** the build123d STL and the upstream reference tessellate **watertight** here (the 5x15mm presentation_post was the only earlier part where the build123d side closed; here both close) — incidental tessellation closure, not a topology guarantee, since the build123d body is un-stitched into 40 free faces at G7. See "Notes on zaphod_bot_mec_de_man_out_printer_proto_bearing_link_3" below for the detail.

---

## Methodology

The reconstruction pipeline is the same for every part. For surface parts (open shells like `zaphod_bot_mec_fbcoup_3mm_globe`) and solid parts (closed bodies) the comparison metrics differ; everything else is identical.

### Step 1 — Coordinate extraction in Fusion 360

The reference STL is imported into Fusion 360. Using a custom Fusion add-in script (not included in this repo), each closed sketch profile is selected, and its line / arc / spline endpoints are written to a CSV with this schema:

```
Steps, Draw Type, X1, Y1, Z1, X2, Y2, Z2, X3, Y3, Z3, …
```

`Draw Type` is one of `Line`, `3_point_arc`, `3_point_circle`, `spline_<N>_points`, `Point`, etc. The X/Y/Z columns hold world-space coordinates in millimetres. Splines extend the row with additional `X_n / Y_n / Z_n` columns for each control point. Each logical sketch is one CSV file (`Fusion_Coordinates_S1.csv`, `Fusion_Coordinates_S2.csv`, …). Splitting by sketch makes loop detection deterministic — adjacent profiles that touch at a corner are kept in separate files so the loop-walker doesn't merge them. Not every CSV is a planar profile, though: the bearing_link_3's S5 is a deliberately **non-coplanar** set of arcs tracing the finished body's outer edges, exported so the build script can *select* edges to fillet rather than build a face (see Step 3).

### Step 2 — CSV cleaning (`0_preprocess_csvs.py`)

A preprocessor consolidates and validates the raw CSVs:
- Strips trailing whitespace
- Removes duplicate rows
- Validates each row has the right number of fields
- Writes cleaned outputs to `csv_merged/`

### Step 3 — build123d reconstruction (`<part>_build123d.py`)

The main script reads the cleaned CSVs and rebuilds the geometry as a series of numbered guidelines (G1, G2, G3, …). The guideline count scales with part complexity — for the 3mm_globe, 5x15mm_1mm_globe_post, 5x15mm_2mm_globe_post, 5x15mm_presentation_post and 5x25mm_presentation_post G1–G4 is enough (G3 is always the final export step); the homing_block (part 7) is the first to run past G4, using six geometry guidelines (G1, G2, G4, G5, G6); the bearing_link_3 (part 8) is the first to run to G7, using seven geometry guidelines (G1, G2, G4, G5, G6, G7). For larger parts the count will grow into the dozens, following the same pattern proven on the PICSY companion repo (where individual parts run up to G92). The pattern is:

- **Read CSV** guidelines — parse line / arc / spline / circle / point segments, walk endpoints to detect closed loops or open chains.
- **Build profile wires** — assemble parsed primitives into oriented `Wire` objects. Profiles can be left as construction-only (no patched face) when the next step is a sweep / revolve / loft that consumes the wire directly.
- **Surface-revolve / extrude / loft / boolean** — the part-specific geometric operation. For the five fibre-coupler parts (`3mm_globe`, `5x15mm_1mm_globe_post`, `5x15mm_2mm_globe_post`, `5x15mm_presentation_post`, `5x25mm_presentation_post`) this is a 360° revolve of a profile wire about a construction-axis line. The homing_block (part 7) is the first to use the other patterns: a straight `BRepPrimAPI_MakePrism` plus a ruled `BRepOffsetAPI_ThruSections` loft for the tapered walls, `Face(wire)` surface patches for the caps, and `BRepAlgoAPI_Cut` / `BRepAlgoAPI_Common` for the two trim steps. The bearing_link_3 (part 8) adds the remaining solid-modelling patterns: two profiles **extruded into solids** (`extrude(face, amount, dir=…)`; S1 by 16 mm along −Z, S2 by 23 mm along +Y), a body-forming **intersection** (`G1 & G2`) to make the cross-yoke, two through-**cuts** (`−`) for the bores, then `fillet` and `chamfer` on the resulting B-rep edges and a final **un-stitch** of the solid into per-face surfaces. For future parts the operation set may grow further, following the extrude / loft / boolean / trim patterns documented in the PICSY companion repo.
- **G3** — always last: apply `.clean()` to remove micro-scars, then export STL + STEP.

Key implementation notes:

- **Cross-platform paths.** `BASE_DIR = Path(__file__).resolve().parent`. No hardcoded absolute paths anywhere.
- **World-coordinate face construction.** All `Edge.make_line(Vector(x, y, z), …)` calls use world coordinates directly. `Plane.XZ.offset()` is avoided because it silently flipped the Z axis in some build123d versions.
- **Plane-detection per CSV (axis-aligned + tilted).** Each CSV sketch's plane is auto-detected per the template's coordinate convention. The detector first tries the axis-aligned case (one of X / Y / Z is constant within tolerance); if no axis is constant, it falls back to a least-squares plane fit via SVD (centroid + smallest-singular-direction normal). For `3mm_globe` both S1 and S2 auto-detect to X = 15.0; for `5x15mm_1mm_globe_post` both auto-detect to X = 3.848; for `5x15mm_2mm_globe_post` both auto-detect to X = 3.847; for `5x15mm_presentation_post` and `5x25mm_presentation_post` S1 auto-detects to **Z = 4.582** (the first Z-constant sketches in the repo) and S2 to X = 4.397; for `zaphod_bot_mec_de_man_out_printer_proto_homing_block` both S1 and S2 auto-detect to **Y = 1.0** — the first Y-constant sketches in the repo, and the first time the detector's middle (Y) branch fires. For `zaphod_bot_mec_de_man_out_printer_proto_bearing_link_3` the detector is exercised on **both** axis branches inside a single part: S1 and S3 auto-detect to **Z-constant** (`Z = 15.0` and `Z = 9.525`) and S2 and S4 to **Y-constant** (`Y = −2.0` and `Y = 9.55`). Its S5 is the first CSV that **does not** resolve to an axis-aligned plane *or* an acceptable SVD fit — the smallest-singular residual is ~5.2 mm, far above `EPSILON_MM` — and the detector returns the `('general', origin, normal)` tuple with a residual large enough that the geometry-builder treats S5 as a 3-D point set rather than a sketch (see the edge-selection note below). The detector returns `('axis', letter, value)` or `('general', origin, normal)` and downstream geometry-builders dispatch on that tuple.
- **Open-chain walking for surfaces of revolution from open profiles.** When an open profile is meant to be revolved (rather than patched into a face), the source CSV gives an *open* chain whose two free endpoints sit on the revolve axis — the on-axis gap is closed by the revolution itself, no explicit edge needed. A small walker traverses the parsed primitives by endpoint adjacency: find the two count-1 endpoints (the chain's free ends), pick one as start, then at each step pick the unused primitive that shares the current "front" endpoint, reversing it if necessary, and continue until the other free end is reached. Used for `3mm_globe` G1 (5 edges), `5x15mm_1mm_globe_post` G1 (15 edges incl. a programmatic bridge — see the part's notes), and `5x15mm_2mm_globe_post` G1 (15 edges, clean source CSV). The same walker generalises to mixed line / arc / spline chains.
- **Closed-loop walking for profiles that become faces or extrudes.** When the source sketch is a fully enclosed loop (every endpoint has exactly two neighbours, zero free endpoints), the open-chain walker can't be used — it asserts exactly two free endpoints. The closed-loop variant starts from `edges_named[0]` oriented as authored, walks the loop by following unused neighbours at each endpoint key, and validates that the walk returns to the starting key after consuming every primitive. Both walkers share the same fuzzy adjacency machinery (`_kep` 0.01 mm rounding for matching, original unrounded coordinates preserved for downstream edge construction); only the start-condition and termination-condition differ. Used for `5x15mm_presentation_post` G1 and `5x25mm_presentation_post` G1 (both 12 edges, revolved), for `zaphod_bot_mec_de_man_out_printer_proto_homing_block` G1 (4 edges — a closed "stadium" loop, the first time the closed-loop walker drives an extrude rather than a revolve), and for `zaphod_bot_mec_de_man_out_printer_proto_bearing_link_3` G1 (8 edges = 5 Lines + 3 three-point arcs, the "arm + eye" link profile on `Z = 15.0`) and G2 (10 edges = 7 Lines + 3 three-point arcs, the second "eye + tab" link profile on `Y = −2.0`) — the first time **two** independent closed profiles are each walked, faced and extruded into solids that are then Booleaned together. After the walk the script also asserts `Wire.is_closed` so that any sub-tolerance endpoint mismatch surfaces as a clear error rather than producing a silently-open wire downstream.
- **Three-point arc handling.** The Fusion add-in exports each arc as `(p1, p2, p3) = (start, middle-on-arc, end)`. The build script calls `Edge.make_three_point_arc(start, mid, end)` directly; the `parse_three_point_arcs` helper keeps the middle point as part of the (start, mid, end) tuple so it survives any reversal during chain walking.
- **Three-point circle handling.** The Fusion add-in exports a circle as three points lying on its circumference (`3_point_circle`, columns `(p1, p2, p3)`). `parse_three_point_circles` recovers those triples and `circle_from_3_points` solves the circumcircle (centre + radius) in the sketch's `(u, v)` plane; the edge is then built as a full circle on the axis-aligned plane via OCCT `gp_Circ` on a `gp_Ax2` whose normal is the plane's constant axis. First used by `zaphod_bot_mec_de_man_out_printer_proto_homing_block` (S2: two `r = 1.7` circles), and again by `zaphod_bot_mec_de_man_out_printer_proto_bearing_link_3` (S3: one `r = 5.525` circle on `Z = 9.525`, coaxial with the S1 eye → the Z bore; S4: one `r = 5.525` circle on `Y = 9.55`, coaxial with the S2 eye → the Y bore). On the bearing_link_3 each circle is extruded into a cutting cylinder and subtracted in G4. None of the five revolve parts had circles in their source CSVs, so this parser is dead code for them and is added only where the `EXPECTED_CIRCLES` block declares it.
- **Non-coplanar CSVs as edge-selection point clouds (bearing_link_3 S5).** Not every CSV is a sketch. The bearing_link_3's S5 is a set of 16 three-point arcs tracing the finished body's outer edges in 3-D; its SVD plane-fit residual (~5.2 mm) is far too large to treat as a planar sketch, and trying to build a wire from it would be meaningless. Instead the build script **samples** each S5 arc into points (24 per arc), unions them into a point cloud, and uses that cloud to *select* which of the reconstructed body's edges to fillet at G5: an edge is selected if every one of its sampled points (11 per edge) lies within `FILLET_MATCH_TOL` of the cloud. This is the first time a CSV drives a *selection* rather than a construction, and the first time the plane detector's large-residual branch is used as a signal ("this is not a sketch") rather than an error.
- **Solid Booleans (bearing_link_3).** The body is formed by intersecting two solids — `body = solidA & solidB` where `solidA` is S1 extruded 16 mm along −Z and `solidB` is S2 extruded 23 mm along +Y. The two through-bores are cut with `body = body - boreZ - boreY`. build123d's `&` / `-` / `+` operators on `Solid` objects map straight onto the OCCT `BRepAlgoAPI_Common` / `_Cut` / `_Fuse` backend; unlike the bare-wire `revolve()` / `MakeDraft` edge cases hit on earlier parts, the solid-on-solid Booleans behaved exactly as documented and needed no lower-level fallback.
- **Fillet / chamfer with an OCCT-robustness fallback (bearing_link_3).** G5 fillets the 16 selected outer edges at `r = 0.5`; G6 chamfers the bore-mouth edges at an equal distance of `CHAMFER_MM` (the per-part constant, currently **0.2 mm** — the guideline calls for an equal-distance chamfer on both holes' edges, each hole contributing two cylinder edges → 8 edges total). Bulk fillet/chamfer of all selected edges in a single call occasionally fails on one problematic edge, so `safe_fillet` / `safe_chamfer` try the whole set at once and, on failure, retry edge-by-edge and skip only the few that won't take. On this part the bulk path succeeded outright: 16/16 fillets and 8/8 chamfers. The bore-mouth edges for G6 are selected by `GeomType.CIRCLE` + `radius ≈ 5.525` + a centre-on-bore-axis test, so the chamfer lands only on the two bores' rims and nowhere else.
- **Un-stitching a solid into a surface body (bearing_link_3 G7).** After all the solid-modelling steps the part is un-stitched: the finished `Solid`'s faces are collected and rebuilt as a `Compound` of 40 individual `Face` objects, faithful to the guideline's "un-stitch solid → surface body" step. The exported part is therefore an open shell, and the comparison uses the **surface** script (area / Hausdorff / slices), even though the part was *built* as a solid. The fact that the exported STL still tessellates watertight on both sides is incidental closure, not a property of the un-stitched topology.
- **Spline handling and CSV overflow columns.** Splines exported as `spline_<N>_points` carry all N control points in a single row, but the CSV header only declares the first 9 coordinate columns (X1..Z3). For N > 3 the extra triples land in `csv.DictReader`'s overflow under the `None` key as a flat list of strings. The `_row_all_xyz_triples` helper recovers them so a 5-point spline is built from all 5 control points. Used by `5x15mm_1mm_globe_post`; not needed by the other parts (including the bearing_link_3), since none of their source CSVs have splines.
- **Tapered walls without `BRepOffsetAPI_MakeDraft`.** A 45° draft "extrude these edges and shrink the profile" is the homing_block's one genuinely new geometric operation; the build script constructs the taper explicitly via a 2-D in-plane offset + a ruled loft rather than the misbehaving `BRepOffsetAPI_MakeDraft`. The bearing_link_3 has no taper, so this path is not exercised there.
- **Endpoint precision through the chain walker.** Adjacency matching for chain walking uses a `_kep` function that rounds each `(u, v)` endpoint to 0.01 mm, but the *rounded* keys must never leak into actual `Edge.make_*` calls — OCCT wire construction expects coincident vertices at floating-point precision, and a 0.001 mm endpoint mismatch is enough to produce a "Edges are disconnected" error from `Wire(...)`. The walker keeps the original unrounded `(u, v)` tuples alongside the rounded keys, and downstream edge construction always uses the originals.
- **Axis-snap for noisy construction lines.** Fusion's add-in sometimes exports a "constant-along-one-axis" construction line with a small wobble; the build script snaps a component to its mean when it varies by less than `AXIS_SNAP_MM = 0.05 mm`. The bearing_link_3 has no construction-axis line (it is not a revolve), so this snap is not exercised there.
- **`build123d.revolve()` quietly fails on bare wires.** The five revolve parts go directly to OCCT's `BRepPrimAPI_MakeRevol(...)` because build123d's high-level `revolve()` returns an empty `Compound` on a bare `Wire` without raising. The bearing_link_3 sidesteps this entirely — it never revolves — and its solid-on-solid Booleans hit none of that class of degeneracy.
- **Boolean trims and Boolean tools that never reach the export.** The homing_block's two trim guidelines each need a cutting body (a solid cylinder for the holes, a slab box for the tube trim) that is pure scaffolding. The same discipline applies to the bearing_link_3's two bore cuts at G4 — the cutting cylinders are built as local variables, fed to the `-` operator, and never added to the exported compound — which keeps the final STL clean and the area-history honest.
- **Post-revolve scale fix for CSV-vs-reference unit mismatch (3mm_globe only).** The 3mm_globe's CSV came out at 10× the reference scale; a single `gp_Trsf.SetScale(origin, 0.1)` step in G4 fixes it. Every other part (including the bearing_link_3) came out at the correct reference scale and needs no post-build scaling.
- **Filename guideline-range convention.** Output filenames carry the active guideline range (e.g. `..._homing_block_G_1_6.stl`, `..._bearing_link_3_G_1_7.stl`) so multiple checkpoint exports coexist without clobbering each other.
- **Per-guideline checkpoints.** Three top-of-file flags (`VIEW_AT`, `STOP_AFTER_VIEW`, `EXPORT_AT_CHECKPOINT`) let you halt at any guideline, send the cumulative state to the OCP viewer on port 3939, and optionally export `<part>_G_1_N.{stl,step,txt}` mid-pipeline. For the homing_block the valid checkpoint numbers are 1, 2, 4, 5, 6; for the bearing_link_3 they are 1, 2, 4, 5, 6, 7 (G3 is the final export step in both).
- **Surface-area tracking.** Every guideline's cumulative surface area is recorded. Both the main summary and a standalone `<part>_area_history_G_1_N.txt` document how area accumulates and — as of the homing_block (part 7) — *decreases*. The homing_block's G5 and G6 were the first negative Δ-area steps in the project (two `r = 1.7` holes per cap; trimming each tube wall from 4 mm to 2 mm). The bearing_link_3 (part 8) is the first part where a **body-forming** Boolean is itself a negative delta: G1 builds the S1 solid (+1652.33 mm²), then **G2 intersects** it with the S2 extrusion and the cumulative area drops to 1023.52 mm² (**Δ = −628.81**), since an intersection of two solids is smaller than either. The subsequent trims continue downward — G4 two through-bores (−35.61), G5 sixteen fillets at r = 0.5 (−35.45), G6 eight bore-mouth chamfers at 0.2 mm (−15.64) — and G7 un-stitch is area-neutral (+0.00), ending at 936.83 mm² across 40 faces. For complex parts this audit trail is the single most valuable debugging tool: the *sign* of each guideline's delta is predictable (extrude/cap/fuse go up; intersect/cut/fillet/chamfer go down), so any delta with the wrong sign or wrong magnitude points straight back at the guideline that introduced the wrong geometry.

### A note on `zaphod_bot_mec_fbcoup_3mm_globe` — why it took 1 hour

The 3mm_globe is structurally the simplest possible PICSY-style part: a single open profile revolved about a single axis line, 4 guidelines total (G1, G2, G4, with G3 as the final export step). The 1 hour was split roughly as:

- **~20 min** on the parser side: writing `parse_three_point_arcs`, the open-chain walker that finds the 2 free endpoints and walks the 5 primitives into a connected oriented chain, and confirming the plane auto-detector handles X-constant sketches the same way it handles Z-constant ones in the PICSY repo.
- **~15 min** running into and fixing the empty-Compound silent failure from `build123d.revolve()` on an open Wire. The fix was straightforward once isolated — drop to OCCT's `BRepPrimAPI_MakeRevol` directly, which produces 5 faces (2 REVOLUTION, 1 TORUS, 1 CYLINDER, 1 CONE) of total area ~4099 mm² (pre-scale).
- **~10 min** diagnosing the 10× scale mismatch when the first build came out as a 30 mm globe next to the 3 mm reference STL in Fusion. The CSV-vs-reference scale ratio was an exact 10×, so a single `gp_Trsf.SetScale(origin, 0.1)` step at the end of G4 closed the gap. Post-scale surface area: 40.988 mm² vs reference 40.9073 mm² — 0.18% off.
- **~15 min** on the 0.018 mm Y-axis-wobble in the S2 construction line, the cross-platform `BASE_DIR` plumbing, and confirming the comparison script lands every metric in 🟢 EXCELLENT.

Two notes worth recording for future parts:

- **`build123d.revolve()` on open wires silently returns an empty Compound.** No exception, no warning — just zero faces in the result. Always check `len(result.faces())` before assuming success, or skip the wrapper and call `BRepPrimAPI_MakeRevol` directly when the profile is a 1-D wire rather than a closed face.
- **CSV-vs-reference unit mismatch is silent and uniform.** Every coordinate is wrong by the same factor, so plane detection still works, loop walking still works, the revolve still completes, and the only symptom is a build that's 10× too big when imported into Fusion next to the reference. Detection: import both into Fusion and visually compare. Quick fix: post-build scale.

### A note on `zaphod_bot_mec_fbcoup_5x15mm_1mm_globe_post` — why it took 1 h 15 min

The 5x15mm_1mm_globe_post is the second part and reuses the same 4-guideline structure as the 3mm_globe. Geometry is more complex: 14 primitives in S1 (8 Lines + 5 three-point arcs + 1 five-point spline) versus 5 in the 3mm_globe, and the source CSV had a real defect that needed programmatic repair. The 1 h 15 min was split roughly as:

- **~15 min** dropping the 3mm_globe script into the new folder, swapping CSV paths via `BASE_DIR`, and confirming the plane auto-detector handles X = 3.848.
- **~20 min** adding spline support: a `parse_splines` helper, a `make_spline_edge` builder wrapping `Edge.make_spline(...)`, and the closure pattern that lets the chain walker reverse a spline. First run showed only 3 of 5 control points because `csv.DictReader` buries overflow under the `None` key; the `_row_all_xyz_triples` helper fixed it.
- **~25 min** on the missing-bridge CSV defect. The walker reported 4 free endpoints instead of 2 — the source CSV was missing one short horizontal Line at Z = 5.084. Auto-repaired at G1 by peeking at S2 for the revolve-axis V coordinate, enumerating free-endpoint pairs whose V matches within `BRIDGE_V_TOL`, excluding on-axis pairs, and trial-walking each candidate. Only the gap-pair survived.
- **~10 min** on a precision-leak bug surfaced by the bridge insertion (rounded keys leaking into `Edge.make_line`), fixed by tracking unrounded coords alongside the rounded `_kep` keys.
- **~5 min** confirming no post-revolve scaling was needed and running the comparison.

Final numbers: surface area 404.55 mm² vs 403.99 mm² (0.14%), Hausdorff 0.0092 mm, mean 0.0029 mm.

Three notes worth recording: CSV-header overflow with splines is silent (read both named columns *and* `row[None]`); programmatic bridge insertion needs the axis context (exclude on-axis pairs); rounded adjacency keys must not leak into geometry.

### A note on `zaphod_bot_mec_fbcoup_5x15mm_2mm_globe_post` — why it took 1 hour

The 2mm_globe_post is the slightly-larger sibling of the 1mm-post — same 4-guideline structure, same complexity band (15 primitives vs 14), but structurally cleaner: 10 Lines + 5 three-point arcs, no splines, complete source CSV. The 1 hour was split roughly as ~10 min folder setup + count swaps; ~15 min *removing* the spline parser, overflow handler and bridge block that this part doesn't need; ~10 min on a clean first dry run (walker found exactly 2 free endpoints on the axis at Z = 4.008, no bridge needed); ~20 min on G4 + the comparison (15 faces, area 414.11 mm² vs 413.49 mm², 0.151%); ~5 min cross-checking against the 1mm-post.

Two notes: a cleaner source CSV genuinely saves time (the bulk of per-part time is CSV-extraction defects, not geometry complexity); strip what you don't need (declare the primitive set in one `EXPECTED_*` block and carry only the parsers it requires).

### A note on `zaphod_bot_mec_fbcoup_5x15mm_presentation_post` — why it took 30 min

The presentation_post exercises two new branches: a single **CLOSED** profile (12 primitives, zero free endpoints) on a **Z-constant plane** (`Z = 4.582`). ~5 min folder setup + count swaps; ~10 min adding the `walk_closed_chain` variant (starts from `edges_named[0]`, follows unused neighbours, validates return to start, asserts `Wire.is_closed`); ~10 min on the dry run + G4 (12 faces, ~524.5 mm²); ~5 min on the comparison — surface area 0.017%, Hausdorff 0.0144 mm, the tightest run of the project at the time, both meshes watertight.

Three notes: a second walker variant is a 10-minute change once the first is in place; the axis-agnostic plane detector paid off (the Z-branch was dead code until here); watertight comparison output is incidental, not engineered.

### A note on `zaphod_bot_mec_fbcoup_5x25mm_presentation_post` — why it took 20 min

The 5x25mm presentation_post is a near-pure parametric clone of the 5x15mm — same 12-primitive closed profile on Z = 4.582, only the Y-extent (30 mm vs 20 mm) and the S2 axis endpoints differ. ~5 min folder setup; ~3 min pre-flight connectivity check (12 distinct keys, all degree-2); ~7 min dry run + G4 (12 faces, ~773.3 mm²); ~5 min comparison — surface area 0.020%, Hausdorff 0.0151 mm, all slices ≤ 0.151%. The build123d STL came out `is_watertight = False` here even though the topology is identical to the watertight 5x15mm sibling — a tessellation-only artefact.

Three notes: a near-pure clone is a 5-minute build; new Y-extent means new slices test new ground; tessellation closure on revolved closed-wire shells is not stable across sibling runs.

### A note on `zaphod_bot_mec_de_man_out_printer_proto_homing_block` — why it took 50 min

The homing_block is the first departure from surface-of-revolution: surface-extrude a closed profile in two directions, patch the ends, Boolean-trim holes and overshoot, across six guidelines (G1, G2, G4, G5, G6). ~10 min folder setup (the whole CSV/plane/walker layer carried over; the G4 revolve block was removed wholesale); ~15 min on the tapered upper wall (the one real fight — `BRepOffsetAPI_MakeDraft` tapered outward regardless of sign and under-rose by `cos 45°`, so the taper was built explicitly as a 2-D offset + ruled loft); ~10 min on the three-point-circle parser, the two cap patches and the two trim guidelines; ~10 min on the first dry run and the area history (first negative deltas: G5 = −36.31 = `4·π·1.7²`, G6 = −42.72); ~5 min on the comparison, the tightest of the project (surface area 0.011%, Hausdorff 0.0024 mm, mean 0.0002 mm).

Three notes: `BRepOffsetAPI_MakeDraft` is the wrong tool for a controlled taper on a bare wire; trim guidelines are where the area-history audit trail earns its keep (the expected delta has a closed-form sign and magnitude); keep Boolean tools out of `stage_pieces`.

### A note on `zaphod_bot_mec_de_man_out_printer_proto_bearing_link_3` — why it took 2 hr

The bearing_link_3 is the eighth part and the first built by genuine solid Boolean modelling — two perpendicular link profiles extruded into solids and **intersected** into a cross-yoke, two perpendicular through-bores cut out, outer edges filleted, bore mouths chamfered, then the solid un-stitched into a surface body. It is the first part to run to G7 (G1, G2, G4, G5, G6, G7; G3 is the final export step), and at 2 hr it is the longest build since the early globe parts — the cost was concentrated almost entirely in one guideline (G5, the S5 edge selection). The 2 hr was split roughly as:

- **~15 min** standing up the folder and deciding what carried over. The CSV / plane / walker layer came across unchanged — CSV reading, `detect_sketch_plane`, `world_vec_axis`/`in_plane_uv`, `parse_line_segments`, `parse_three_point_arcs`, `parse_three_point_circles` (from the homing_block), `walk_closed_chain` (from the presentation_posts), the checkpoint scaffold and area tracker. What did *not* carry over was the homing_block's taper/cap/loft block (no taper here) and all of the revolve machinery. The plane detector landed on **Z = 15.0** for S1 and **Y = −2.0** for S2 first try — the first part to drive both the Z- and Y-branches in a single run.

- **~20 min** on G1 + G2 — the two closed link profiles and the intersection. S1 (5 Lines + 3 three-point arcs, the rectangular arm tangent into a `r ≈ 7.025` eye centred near (21.12, 7.05)) walks closed and faces cleanly; `extrude(face, 16, dir=(0,0,-1))` produces the first solid (vol 3735.3 mm³). S2 (7 Lines + 3 three-point arcs, an eye + rectangular tab) walks closed on `Y = −2.0`; `extrude(face, 23, dir=(0,1,0))` produces the second solid. The body-forming `body = solidA & solidB` was the genuinely new operation, but build123d's `&` mapped straight onto OCCT `BRepAlgoAPI_Common` and produced one clean solid (vol 1584.6 mm³) first try — no degeneracy of the kind the bare-wire `revolve()` and `MakeDraft` calls hit on earlier parts. Most of the 20 min was spent confirming the two extrude *directions and amounts* (−Z by 16, +Y by 23) overlap into the right cross-yoke volume against the reference.

- **~15 min** on G4 — the two perpendicular through-bores. S3 is one `r = 5.525` circle on `Z = 9.525`, coaxial with the S1 eye → extruded into a Z-axis cutting cylinder; S4 is one `r = 5.525` circle on `Y = 9.55`, coaxial with the S2 eye → a Y-axis cutting cylinder. `body = body - boreZ - boreY` (vol 625.3 mm³). The first part with bores on two *different* axes; the time went into confirming each circle is genuinely coaxial with its eye (centre-on-eye-axis check) before cutting, so the bores don't graze the wrong wall.

- **~45 min** on G5 — the fillet edge selection, which was the whole reason this part took 2 hr. S5 is not a sketch: 16 three-point arcs tracing the body's outer edges in 3-D, with an SVD plane-fit residual of ~5.2 mm, so the plane detector correctly refuses to treat it as planar. The first instinct — match each body edge to an S5 arc with an EPSILON-tight tolerance — selected *nothing*, because the reconstructed body's outer edges sit **~0.7 mm** off the extracted S5 arcs (the arcs were sampled from the reference mesh, the body from the CSVs, and the two disagree by sub-millimetre reconstruction drift). The fix was to sample each S5 arc into a point cloud (24 pts/arc) and select any body edge whose 11 sampled points all fall within `FILLET_MATCH_TOL` of the cloud — then widen the tolerance to just below the gap in the per-edge max-distance histogram. Printing that histogram made the gap obvious and the tolerance defensible: the real outer edges sit at ≤ 0.703 mm from the cloud, everything else at ≥ 1.59 mm, so **`FILLET_MATCH_TOL = 1.0 mm`** cleanly isolates exactly the 16 outer edges (4 disc-rim circles, 4 transition splines, 8 blend splines) — matching S5's 16 arcs one-for-one. `safe_fillet` then took all 16 at `r = 0.5` in the bulk path (vol 616.6 mm³).

- **~10 min** on G6 + G7. G6 chamfers the bore mouths at an equal distance of `CHAMFER_MM`; the edges are selected by `GeomType.CIRCLE` + `radius ≈ 5.525` + a centre-on-bore-axis test, which picks up exactly the two bores' rims — 8 edges total (each hole contributes two cylinder edges, split into arcs). The guideline did not pin a chamfer size, so it started at a documented top-of-file constant; it was later set to **0.2 mm** per the revised guideline (`safe_chamfer` took 8/8 in the bulk path, vol 613.8 mm³). G7 un-stitches the finished solid into a `Compound` of 40 individual faces — the first un-stitch in the repo — and the part is exported as an open shell.

- **~15 min** on the comparison run and this README entry. Every aggregate metric landed 🟢 EXCELLENT: surface area **0.043%** (936.7036 mm² vs 937.1066 mm²), Hausdorff **0.0234 mm**, mean distance **0.0008 mm**, RMS 0.0017 mm, 99th-pct 0.0024 mm, bounding box ≤ 0.0014 mm/axis, centroid distance **0.0000 mm**. All seven Y-slices ✅ PASS (worst **0.042%** at Y = 7.050, the central plane where both eyes' bores are open). Both the build123d STL and the upstream reference tessellate watertight on this part — the first time the build123d side closes since the 5x15mm presentation_post, and incidental either way given the G7 un-stitch.

Three notes worth recording for future parts:

- **A non-coplanar "sketch" CSV is an edge-selection cloud, not a profile.** S5's ~5.2 mm plane-fit residual is the signal: this CSV traces the finished body's 3-D edges, it is not a planar sketch. Don't fit a plane or build a wire from it — sample it into a point cloud and use it to *select* which body edges to fillet. Treat a large plane-fit residual from the detector as "this is not a sketch," not as an error to suppress.

- **Edge-selection tolerance must reflect reconstruction drift, not source precision.** The reconstructed outer edges sit ~0.7 mm off the extracted S5 arcs, so an EPSILON-tight match selects nothing. Set the match tolerance just below the gap between "real outer edges" and "everything else" — here 1.0 mm cleanly separates ≤ 0.703 mm from ≥ 1.59 mm. Always print the per-edge max-distance histogram so the gap is visible and the chosen tolerance is auditable rather than magic.

- **A body-forming Boolean can be a negative area delta, and the sign is the check.** The G2 intersection is the first body-forming step in the project that *reduces* cumulative surface area (−628.81 mm²), where every prior part's body-forming steps (revolve, extrude, cap, fuse) only added area. The per-operation sign is predictable — intersect and cut go down, extrude / cap / fuse go up, fillet and chamfer go down, un-stitch is neutral — so building the expected sign into each guideline's print line turns the area-history log into a first-run sanity check for the whole solid-modelling pipeline.

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

The **cross-section slice comparison** has proven especially valuable on complex parts: it cuts both meshes at multiple Y-plane positions (auto-derived from mesh bounds) and compares the outline perimeter at each cut. Aggregate metrics like Hausdorff or mean-distance can mask a 1–2% feature-level discrepancy because the affected region is small compared to the total surface — the slice test bypasses this by comparing geometry at specific cross-sections. On the seven completed parts every slice has passed comfortably: ≤ 0.24% perimeter error on the 1mm-post, ≤ 0.283% on the 2mm-post, ≤ 0.178% on the 5x15mm presentation_post, ≤ 0.151% on the 5x25mm presentation_post, ≤ 0.014% on the homing_block, and ≤ 0.042% on the bearing_link_3 (worst at Y = 7.050, the central plane through both bores). The worst slice on each globe-post lands at the narrow neck just before the globe terminates, where a small absolute deviation resolves to a relatively larger percentage of a small perimeter.

For **solid parts** the original volume + symmetric-volume-difference comparison from the [Thor assembly project](https://github.com/avajones081196/Ava_AngelLM_Thor_Art1_build123d) is used. Note that "solid" here refers to how the part is *built* in build123d, not whether the exported STL happens to tessellate as a watertight closed mesh — and the bearing_link_3 is the edge case that makes the distinction concrete: it is **built** by solid Boolean modelling (intersection + cuts + fillet + chamfer) but is **un-stitched into a surface body at G7** before export, so it is compared with the **surface** script. Surface-built parts may *or may not* register as watertight in mesh tools depending on tessellation luck (the 5x15mm presentation_post and the bearing_link_3 did; the 5x25mm and the homing_block did not), but either way they use the surface comparison script.

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

The same layout is used for every part. Output filenames carry the active guideline range so checkpoint exports do not clobber each other — the homing_block uses the `G_1_6` suffix throughout, and the bearing_link_3, which runs to G7, uses `G_1_7` (`zaphod_bot_mec_de_man_out_printer_proto_bearing_link_3_G_1_7.stl`, `..._summary_G_1_7.txt`, `..._area_history_G_1_7.txt`, `..._build123d_vs_reference_G_1_7.txt`). Its S5 CSV (the edge-selection cloud) lives alongside S1–S4 in `csv_merged/` even though it is not a sketch profile.

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

Set `VIEW_AT = None` for a clean end-to-end run that only writes the final outputs. For the homing_block the valid `VIEW_AT` checkpoint numbers are 1, 2, 4, 5, 6; for the bearing_link_3 they are 1, 2, 4, 5, 6, 7 (G3 is the final export step). The bearing_link_3's chamfer size is exposed as a single top-of-file `CHAMFER_MM` constant (currently `0.2`) so the equal-distance bore chamfer can be re-sized in one place, and `FILLET_MATCH_TOL` (currently `1.0`) controls the S5 edge-selection tolerance.

---

## Acceptance Criteria — How the Ratings Are Set

For surface parts (e.g. `zaphod_bot_mec_fbcoup_3mm_globe`, `zaphod_bot_mec_fbcoup_5x15mm_1mm_globe_post`, `zaphod_bot_mec_fbcoup_5x15mm_2mm_globe_post`, `zaphod_bot_mec_fbcoup_5x15mm_presentation_post`, `zaphod_bot_mec_fbcoup_5x25mm_presentation_post`, `zaphod_bot_mec_de_man_out_printer_proto_homing_block`, `zaphod_bot_mec_de_man_out_printer_proto_bearing_link_3`), the rating thresholds are aligned with typical FDM 3D-printer manufacturing tolerances rather than CAD-tight micrometre tolerances, since the zaphod-bot parts are designed for FDM printing. A well-tuned consumer FDM printer (Prusa, Bambu, etc.) has roughly 0.1–0.5 mm positional accuracy, with industry rule-of-thumb specs of ±0.5 mm. Anything below that floor is below what the manufacturing process can resolve, so it counts as "indistinguishable from the original" in practice.

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

The reference STLs come from upstream tessellation by the zaphod-bot repo's authors. Some are not perfectly closed meshes — `is_watertight` may report `False`. This is normal: STL exports often leave non-coincident edges across feature boundaries. For the comparison script this is fine because surface comparison does not require closure. The inverse also happens — the homing_block's upstream reference tessellates watertight while the build123d-side STL does not. The bearing_link_3 is the opposite-again case: **both** sides tessellate watertight even though the build123d body is un-stitched into 40 free faces at G7. All three situations are equally harmless for surface comparison, which is why watertightness is never part of the acceptance criteria for a surface part.

---

## License

This repo follows the upstream [zaphod-bot repository's license](https://github.com/Scottapotamas/zaphod-bot). All build123d reconstruction code and comparison utilities are provided as-is for educational and reverse-engineering purposes.
