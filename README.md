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
| 9 | zaphod_bot_mec_de_man_out_printer_proto_clevis_3 | ✅ Complete | 0.137% | 0.0059 | 0.0440 | 8 h |
| ... | | | | | | |
| 21 | — | ⏳ Pending | | | | |

`zaphod_bot_mec_fbcoup_3mm_globe` is the first part. It is a 3 mm globe surface of revolution built from two source sketches (S1 profile + S2 axis). All five aggregate metrics land in the 🟢 EXCELLENT band: surface area to 0.18%, mean point distance 0.0019 mm, Hausdorff worst-case 0.0051 mm, bounding box ≤ 0.004 mm/axis, centroid distance 0.0009 mm. See "Notes on zaphod_bot_mec_fbcoup_3mm_globe" below for the build detail behind it.

`zaphod_bot_mec_fbcoup_5x15mm_1mm_globe_post` is the second part. It is a ~20.8 mm long globe-post — a slender body with cylindrical, conical and toroidal sections terminating in a small 1 mm globe — built as a surface of revolution from the same two-sketch pattern (S1 open profile + S2 axis line). Geometry is more complex than the 3mm_globe: 14 primitives in the source CSV instead of 5, including the first **spline** primitive in the repo and a missing-bridge defect in the source CSV that has to be auto-repaired. All aggregate metrics land in 🟢 EXCELLENT: surface area to 0.14%, mean distance 0.0029 mm, Hausdorff worst-case 0.0092 mm, bounding box ≤ 0.006 mm/axis, centroid distance 0.0020 mm. All seven cross-section slices ✅ PASS. See "Notes on zaphod_bot_mec_fbcoup_5x15mm_1mm_globe_post" below for the detail.

`zaphod_bot_mec_fbcoup_5x15mm_2mm_globe_post` is the third part. It is the slightly-larger sibling of the 1mm-globe-post — a ~21.9 mm long globe-post terminating in a 2 mm globe instead of a 1 mm one — built from the same two-sketch surface-of-revolution pattern (S1 open profile + S2 axis line). Geometry is in the same complexity band as the 1mm-post (15 primitives in S1 vs 14) but structurally cleaner: **10 Lines + 5 three-point arcs and no splines**, and the source CSV is complete (no missing-bridge defect — the 15-primitive chain walks straight through with exactly 2 free endpoints on the revolve axis at `Z = 4.008`). All aggregate metrics land in 🟢 EXCELLENT: surface area to 0.151%, mean distance 0.0032 mm, Hausdorff worst-case 0.0098 mm, bounding box ≤ 0.005 mm/axis, centroid distance 0.0024 mm. All seven cross-section slices ✅ PASS (worst 0.283%). See "Notes on zaphod_bot_mec_fbcoup_5x15mm_2mm_globe_post" below for the detail.

`zaphod_bot_mec_fbcoup_5x15mm_presentation_post` is the fourth part. It is a 20 mm-long fibre-coupler post in the same body-shape family as the two globe-posts but **structurally different on two axes**: the profile is a single **CLOSED** loop (not an open chain terminating on the revolve axis), and the source sketch lies on a **Z-constant plane** (`Z = 4.582`) rather than the X-constant planes used by every previous part. Same two-sketch pattern (S1 profile + S2 axis line); the closed wire revolved 360° about an axis line that sits outside the profile's X-range produces a torus-topology shell that happens to come out **watertight** when tessellated (both the build123d STL and the upstream reference STL register as closed solids in trimesh). All aggregate metrics land in 🟢 EXCELLENT, and this is the tightest run of the project so far on every aggregate: surface area to 0.017% (an order of magnitude better than the three globe-family parts), mean distance 0.0031 mm, Hausdorff worst-case 0.0144 mm, bounding box ≤ 0.0032 mm/axis, centroid distance 0.0026 mm. All seven cross-section slices ✅ PASS (worst 0.178% at Y = 13.0 — the best slice run of the four parts so far). See "Notes on zaphod_bot_mec_fbcoup_5x15mm_presentation_post" below for the detail.

`zaphod_bot_mec_fbcoup_5x25mm_presentation_post` is the fifth part. It is the **longer sibling** of the 5x15mm presentation_post — a 30 mm-long fibre-coupler post (10 mm longer along Y than its 5x15mm counterpart) built from a **structurally identical** source sketch: same closed-loop profile of **8 Lines + 4 three-point arcs = 12 primitives** on a **Z = 4.582 plane**, same revolve-axis at `X = 4.397` on the same plane outside the profile's X-range (~0.4..3.32), same torus-topology shell. The only differences in the source CSVs vs the 5x15mm variant are (a) the profile's Y-range now spans `0.0..30.0` instead of `0.0..20.0`, and (b) the S2 axis-line endpoints move proportionally to `(4.397, 30.0) → (4.397, 27.038)`. The upstream reference STL tessellates watertight as before, but the build123d-side STL on this part comes out as `is_watertight = False` even though the underlying B-rep topology is identical to the 5x15mm sibling — a small tessellation-only gap that doesn't affect any surface-comparison metric (see the part's notes below). All aggregate metrics land in 🟢 EXCELLENT and the part essentially **ties the 5x15mm presentation_post for tightest run of the project**: surface area to 0.020% (vs 0.017% on the 5x15mm — both an order of magnitude better than the globe-family parts), mean distance 0.0033 mm, Hausdorff worst-case 0.0151 mm, bounding box ≤ 0.0032 mm/axis, centroid distance 0.0028 mm. All seven cross-section slices ✅ PASS (worst 0.151% at Y = 19.5 — a region that didn't exist on the shorter 5x15mm part because it sits past that part's Y-extent). This is the first build of the project that was a **near-pure parametric clone** of an already-completed sibling — only the per-CSV-constants and the Y-extent of the profile differ — and the 20-min build time is the lowest of the project so far. See "Notes on zaphod_bot_mec_fbcoup_5x25mm_presentation_post" below for the detail.

`zaphod_bot_mec_fbcoup_fiber_led_coupler` is the sixth part and is **still pending** — it has been allocated a slot in the status table but not yet built. The homing_block (part 7), the bearing_link_3 (part 8) and the clevis_3 (part 9) were all built ahead of it.

`zaphod_bot_mec_de_man_out_printer_proto_homing_block` is the seventh part (built ahead of part 6, `zaphod_bot_mec_fbcoup_fiber_led_coupler`, which remains pending) and the first part in the repo that is **not a surface of revolution**. Where the five fibre-coupler parts were all a single profile revolved about an axis, the homing_block is built by **surface extrusion + capping + Boolean trimming** across **six geometry guidelines (G1, G2, G4, G5, G6, with G3 the final export step)** — the first part to run past G4. It is also the first part on a **Y-constant sketch plane** (`Y = 1.0`, exercising the middle branch of the X→Y→Z plane detector that the X-plane globes and Z-plane presentation_posts never reached), the first to parse **three-point circles** (S2: two `r = 1.7` circles concentric with the stadium's two semicircle centres), and the first to exercise the **trim guidelines** — so its area-history log is the first in the project to show **negative Δ-area** steps. The body is a closed "stadium" profile (2 Lines + 2 three-point arcs) surface-extruded straight down 1 mm (zero taper, `Y = 1→0`) and up 1 mm with a 45° inward taper (`Y = 1→2`, the top profile being the base offset inward by `tan 45° · 1 = 1 mm` via a 2-D offset + ruled loft), capped top and bottom, with both caps pierced by two through-holes and two cylindrical tube walls running `Y = 0→2` through them. All aggregate metrics land in 🟢 EXCELLENT, and because every surface is planar, cylindrical or a ruled loft (no curved surface-of-revolution to tessellate), this part posts the **tightest point-distance run of the project by an order of magnitude**: surface area to **0.011%** (505.5111 mm² vs 505.5651 mm²), Hausdorff worst-case **0.0024 mm**, mean distance **0.0002 mm**, bounding box ≤ 0.0006 mm/axis, centroid distance 0.0000 mm. All seven cross-section slices ✅ PASS (worst **0.014%**) — and because the slices run along Y they directly register the 45° taper, with the section perimeter holding at 81.62 mm through the straight lower half then stepping down to 75.97 mm at Y = 1.9 in the tapered upper half. The build123d STL comes out `is_watertight = False` (open surface) while the upstream reference tessellates watertight — the same incidental tessellation asymmetry seen on the 5x25mm presentation_post, with no effect on any surface-comparison metric. See "Notes on zaphod_bot_mec_de_man_out_printer_proto_homing_block" below for the detail.

`zaphod_bot_mec_de_man_out_printer_proto_bearing_link_3` is the eighth part (built ahead of part 6, `zaphod_bot_mec_fbcoup_fiber_led_coupler`, which remains pending) and the first part in the repo built by **genuine solid Boolean modelling** rather than a surface of revolution or a surface-extrude/cap. Where the homing_block (part 7) extruded a single profile and trimmed it, the bearing_link_3 is a **cross-yoke**: two perpendicular "link" arms — each a closed profile terminating in a bored circular eye — extruded into two separate solids and **intersected** (`G2: G1 ∩ G2`) to form the body. It is the first part to use a body-forming **intersection**, the first with **two perpendicular through-bores** (one along Z, one along Y), the first to **fillet** and **chamfer** real B-rep edges, the first to **un-stitch** a finished solid into a surface body, and the first to run all the way to **G7** (seven geometry guidelines: G1, G2, G4, G5, G6, G7, with G3 the final export step). It is also the first part to **mix sketch-plane orientations within a single part** — S1/S3 are **Z-constant** (`Z = 15.0` / `9.525`) and S2/S4 are **Y-constant** (`Y = −2.0` / `9.55`), so a single part exercises both the Z- and Y-branches of the plane detector — and the first to consume a **non-coplanar CSV**: S5 is not a sketch at all but a 3-D set of 16 three-point arcs tracing the model's outer edges, with an SVD plane-fit residual of ~5.2 mm, sampled into a point cloud and used purely to *select* which body edges to fillet (see notes). Build order is `G1 → G2 → G4 → G5 → G6 → G7`, with G3 (export) last. All aggregate metrics land in 🟢 EXCELLENT: surface area to **0.043%** (936.7036 mm² vs 937.1066 mm²), Hausdorff worst-case **0.0234 mm**, mean distance **0.0008 mm**, bounding box ≤ 0.0014 mm/axis, centroid distance **0.0000 mm**. All seven cross-section slices ✅ PASS (worst **0.042%** at Y = 7.050). Unusually for a surface-exported part, **both** the build123d STL and the upstream reference tessellate **watertight** here (the 5x15mm presentation_post was the only earlier part where the build123d side closed; here both close) — incidental tessellation closure, not a topology guarantee, since the build123d body is un-stitched into 40 free faces at G7. See "Notes on zaphod_bot_mec_de_man_out_printer_proto_bearing_link_3" below for the detail.

`zaphod_bot_mec_de_man_out_printer_proto_clevis_3` is the ninth part (built ahead of part 6, `zaphod_bot_mec_fbcoup_fiber_led_coupler`, which remains pending) and **by a wide margin the most complex part in the repo so far** — it is the clevis/yoke end of the printer prototype: a forked clevis (with a back-slot, two coaxial pivot bosses across the slot, and chamfered/filleted edges) joined through a tapered transition to an axially-bored cylindrical pin. It runs to **G29 — twenty-eight geometry guidelines** (`G1, G2, G4, G5, G6, G7…G22, G23…G29`, with G3 the final export step) across **twenty-one source sketches (S1–S21)** — more than four times the guideline count of any earlier part (the bearing_link_3 topped out at G7). It is the first part to **combine every operation family the repo has developed into a single model**: a two-direction tapered **extrude** (the pin), a surface-extrude **block**, a body-forming **boolean intersect** (the forked clevis), **fillets** and **equal-distance chamfers** on real B-rep edges, **two surfaces-of-revolution as sub-features** (the pivot bosses), **two extrude-cut bores**, a gap-bridging **loft**, and a final **un-stitch** to a surface body. Five firsts are worth calling out: (1) the first **mirror-symmetric chamfer of tangent-connected edges** — the slot-mouth (G6) and top/bottom-perimeter (G26) edges run *tangentially* into their neighbouring fillet/rounded arcs, which defeats a single OCCT chamfer call and makes any sequential batching asymmetric, so the chamfer is done by cutting the body at its `X = 4.736` mirror plane, chamfering one half (the front arcs become half-arcs ending on the cut, which removes the tangent conflicts so the half chamfers in one call), then mirroring and fusing — symmetric by construction; (2) the first time a **revolve builds a sub-feature** rather than the whole part (the two bosses); (3) the first part carrying **two identical mirror-image sub-features** (the pivot bosses, mirrored about the slot mid-plane `Z = 5.8`, verified by matching boss volumes of 20.2258 mm³ and matching cut volumes of −64.05 mm³); (4) the first **loft that joins** two previously-disjoint bodies — G24 lofts the fork's `Y = 15.5` back face to the G23 circle at `Y = 20.5` and the union pin + fork + loft closes the 5 mm gap the literal coordinates left, turning two disjoint solids into one connected body; and (5) the first part to mix **all three** plane-detector branches in one model (Y-constant S1/S18/S21, Z-constant S2/S6…S17, X-constant S3). Despite being the most feature-dense part in the project, all aggregate metrics land in 🟢 EXCELLENT: surface area to **0.137%** (1276.1407 mm² vs 1274.3982 mm²), Hausdorff worst-case **0.0440 mm**, mean distance **0.0059 mm**, RMS 0.0091 mm, 99th-pct 0.0293 mm, bounding box ≤ 0.0003 mm/axis, centroid distance **0.0018 mm**. All seven cross-section slices ✅ PASS (worst **0.334%** at Y = 1.525, the front lip of the clevis where the chamfered rounded nose resolves to a relatively larger percentage of a small perimeter). Like the bearing_link_3 it is **built** as a solid but **un-stitched into a surface body at G29** before export, so it is compared with the **surface** script: the build123d STL is an open surface (`is_watertight = False`, 93 faces) while the upstream reference tessellates watertight — the same harmless asymmetry, with no effect on any metric. See "Notes on zaphod_bot_mec_de_man_out_printer_proto_clevis_3" below for the detail.

---

## Methodology

The reconstruction pipeline is the same for every part. For surface parts (open shells like `zaphod_bot_mec_fbcoup_3mm_globe`) and solid parts (closed bodies) the comparison metrics differ; everything else is identical.

### Step 1 — Coordinate extraction in Fusion 360

The reference STL is imported into Fusion 360. Using a custom Fusion add-in script (not included in this repo), each closed sketch profile is selected, and its line / arc / spline endpoints are written to a CSV with this schema:

```
Steps, Draw Type, X1, Y1, Z1, X2, Y2, Z2, X3, Y3, Z3, …
```

`Draw Type` is one of `Line`, `3_point_arc`, `3_point_circle`, `spline_<N>_points`, `Point`, etc. The X/Y/Z columns hold world-space coordinates in millimetres. Splines extend the row with additional `X_n / Y_n / Z_n` columns for each control point. Each logical sketch is one CSV file (`Fusion_Coordinates_S1.csv`, `Fusion_Coordinates_S2.csv`, …). Splitting by sketch makes loop detection deterministic — adjacent profiles that touch at a corner are kept in separate files so the loop-walker doesn't merge them. Not every CSV is a planar profile, though: the bearing_link_3's S5 is a deliberately **non-coplanar** set of arcs tracing the finished body's outer edges, exported so the build script can *select* edges to fillet rather than build a face (see Step 3). The clevis_3 pushes the per-part CSV count to its highest in the repo — **21 sketches (S1–S21)** — mixing profile circles, rounded-rectangle and silhouette loops, three-point-arc guide rails, and several pure edge-set CSVs (S5/S19/S20) used to *select* edges for chamfer/fillet exactly as the bearing_link_3's S5 was.

### Step 2 — CSV cleaning (`0_preprocess_csvs.py`)

A preprocessor consolidates and validates the raw CSVs:
- Strips trailing whitespace
- Removes duplicate rows
- Validates each row has the right number of fields
- Writes cleaned outputs to `csv_merged/`

### Step 3 — build123d reconstruction (`<part>_build123d.py`)

The main script reads the cleaned CSVs and rebuilds the geometry as a series of numbered guidelines (G1, G2, G3, …). The guideline count scales with part complexity — for the 3mm_globe, 5x15mm_1mm_globe_post, 5x15mm_2mm_globe_post, 5x15mm_presentation_post and 5x25mm_presentation_post G1–G4 is enough (G3 is always the final export step); the homing_block (part 7) is the first to run past G4, using six geometry guidelines (G1, G2, G4, G5, G6); the bearing_link_3 (part 8) is the first to run to G7, using seven geometry guidelines (G1, G2, G4, G5, G6, G7); the clevis_3 (part 9) runs all the way to **G29 — twenty-eight geometry guidelines**, the longest chain in the project so far. For larger parts the count will grow further, following the same pattern proven on the PICSY companion repo (where individual parts run up to G92). The pattern is:

- **Read CSV** guidelines — parse line / arc / spline / circle / point segments, walk endpoints to detect closed loops or open chains.
- **Build profile wires** — assemble parsed primitives into oriented `Wire` objects. Profiles can be left as construction-only (no patched face) when the next step is a sweep / revolve / loft that consumes the wire directly.
- **Surface-revolve / extrude / loft / boolean** — the part-specific geometric operation. For the five fibre-coupler parts (`3mm_globe`, `5x15mm_1mm_globe_post`, `5x15mm_2mm_globe_post`, `5x15mm_presentation_post`, `5x25mm_presentation_post`) this is a 360° revolve of a profile wire about a construction-axis line. The homing_block (part 7) is the first to use the other patterns: a straight `BRepPrimAPI_MakePrism` plus a ruled `BRepOffsetAPI_ThruSections` loft for the tapered walls, `Face(wire)` surface patches for the caps, and `BRepAlgoAPI_Cut` / `BRepAlgoAPI_Common` for the two trim steps. The bearing_link_3 (part 8) adds the remaining solid-modelling patterns: two profiles **extruded into solids** (`extrude(face, amount, dir=…)`; S1 by 16 mm along −Z, S2 by 23 mm along +Y), a body-forming **intersection** (`G1 & G2`) to make the cross-yoke, two through-**cuts** (`−`) for the bores, then `fillet` and `chamfer` on the resulting B-rep edges and a final **un-stitch** of the solid into per-face surfaces. The clevis_3 (part 9) is the first part to use **every one of these patterns at once**, and adds two more: a **`revolve` of a meridian profile** to build a sub-feature (each pivot boss is a surface of revolution, not the whole part), and a **`loft` between two model faces** that *joins* two previously-disjoint bodies into one. For future parts the operation set may grow further, following the extrude / loft / boolean / trim patterns documented in the PICSY companion repo.
- **G3** — always last: apply `.clean()` to remove micro-scars, then export STL + STEP.

Key implementation notes:

- **Cross-platform paths.** `BASE_DIR = Path(__file__).resolve().parent`. No hardcoded absolute paths anywhere.
- **World-coordinate face construction.** All `Edge.make_line(Vector(x, y, z), …)` calls use world coordinates directly. `Plane.XZ.offset()` is avoided because it silently flipped the Z axis in some build123d versions.
- **Plane-detection per CSV (axis-aligned + tilted).** Each CSV sketch's plane is auto-detected per the template's coordinate convention. The detector first tries the axis-aligned case (one of X / Y / Z is constant within tolerance); if no axis is constant, it falls back to a least-squares plane fit via SVD (centroid + smallest-singular-direction normal). For `3mm_globe` both S1 and S2 auto-detect to X = 15.0; for `5x15mm_1mm_globe_post` both auto-detect to X = 3.848; for `5x15mm_2mm_globe_post` both auto-detect to X = 3.847; for `5x15mm_presentation_post` and `5x25mm_presentation_post` S1 auto-detects to **Z = 4.582** and S2 to X = 4.397; for the homing_block both S1 and S2 auto-detect to **Y = 1.0**; for the bearing_link_3 the detector is exercised on **both** axis branches inside a single part (S1/S3 Z-constant, S2/S4 Y-constant) and its S5 is the first CSV that resolves to neither an axis-aligned plane nor an acceptable SVD fit (~5.2 mm residual → treated as a 3-D point set, not a sketch). The clevis_3 is the first part to fire **all three** axis branches in one model: **Y-constant** sketches (S1 the pin circle at `Y = 30`, S18 the transition circle at `Y = 20.5`, S21 the pin-bore circle at `Y = 30.5`), **Z-constant** sketches (S2 the block at `Z = 15`, plus the whole boss family S6…S17 at `Z = 8.35 / 8.797 / 2.803 / 3.25 / 11.6 / 0`), and an **X-constant** sketch (S3 the clevis silhouette at `X = 10`); and like the bearing_link_3's S5 it also carries pure edge-set CSVs (S5/S19/S20) whose points are used to *select* model edges. The detector returns `('axis', letter, value)` or `('general', origin, normal)` and downstream geometry-builders dispatch on that tuple.
- **Open-chain walking for surfaces of revolution from open profiles.** When an open profile is meant to be revolved (rather than patched into a face), the source CSV gives an *open* chain whose two free endpoints sit on the revolve axis — the on-axis gap is closed by the revolution itself, no explicit edge needed. A small walker traverses the parsed primitives by endpoint adjacency. Used for the three globe parts; the same walker generalises to mixed line / arc / spline chains.
- **Closed-loop walking for profiles that become faces or extrudes.** When the source sketch is a fully enclosed loop (every endpoint has exactly two neighbours, zero free endpoints), the closed-loop variant starts from `edges_named[0]` oriented as authored, walks the loop by following unused neighbours, and validates that the walk returns to the starting key. Used for the two presentation_posts (revolved), the homing_block G1 (extruded), the bearing_link_3 G1/G2 (extruded into solids), and across the clevis_3's many closed profiles — the pin circle, the block's rounded-bottom rectangle, the clevis silhouette, and every boss circle. After the walk the script asserts `Wire.is_closed` so any sub-tolerance endpoint mismatch surfaces as a clear error.
- **Three-point arc handling.** The Fusion add-in exports each arc as `(p1, p2, p3) = (start, middle-on-arc, end)`. The build script calls `Edge.make_three_point_arc(start, mid, end)` directly. On the clevis_3 the three-point arc is also the **meridian profile of a revolve** (S8 / S14 — the boss guide rails) and the on-curve middle point is what keeps the revolved wall faithful to the reference cross-section.
- **Three-point circle handling.** The Fusion add-in exports a circle as three points lying on its circumference (`3_point_circle`). `parse_three_point_circles` recovers those triples and `circle_from_3_points` solves the circumcircle (centre + radius) in the sketch's `(u, v)` plane; the edge is built as a full circle on the axis-aligned plane via OCCT `gp_Circ` on a `gp_Ax2`. First used by the homing_block (S2: two `r = 1.7` circles) and the bearing_link_3 (the two `r = 5.525` bore circles); the clevis_3 leans on it harder than any part — **eleven** of its 21 sketches are three-point circles (the pin profile S1, the boss inner/outer/terminus circles across S6/S7/S12/S13, the six fillet-target rim circles S9/S10/S11/S15/S16/S17, the transition circle S18, and the pin-bore circle S21).
- **Non-coplanar CSVs as edge-selection point clouds.** Not every CSV is a sketch. The bearing_link_3's S5 traces the finished body's outer edges in 3-D and is sampled into a point cloud used to *select* which body edges to fillet. The clevis_3 reuses the same idea for three of its edge-finishing steps — S5 (the 12 slot-mouth chamfer edges, 6 Lines + 6 three-point arcs), S19 (the 4 loft-transition edges to fillet), and S20 (the 6 top/bottom perimeter edges to chamfer) — each parsed into world-space segments/arcs and matched against the reconstructed body's edges by mid-point/dense-sample proximity rather than built into a face.
- **Mirror-symmetric chamfer of tangent-connected edges (clevis_3 G6, G26).** The hardest geometry lesson of the part. The slot-mouth edge set (G6, S5) and the top/bottom outer-perimeter set (G26, S20) each contain straight edges that run **tangentially** into a neighbouring arc (a slot side-line into a G5 fillet arc; a block side-line into the front rounded-bottom arc) at their shared vertex. OCCT's chamfer builder cannot close a corner where two chamfered edges are tangent, so a single all-edges `chamfer(...)` call fails ("try a smaller length"), and chamfering the edges in *sequential* batches is order-dependent and silently breaks the part's left/right mirror symmetry about `X = 4.736` (one side ends up with more facets than the other). The robust fix exploits the symmetry directly: intersect the body with a half-space at the mirror plane to keep ONE half, chamfer that half's selected edges (on the half the front arcs are cut into half-arcs that terminate on the cut plane, which removes the tangent conflicts so the whole half chamfers in a single OCCT call), then **mirror the chamfered half across the plane and fuse**. The two sides are then identical by construction, and the removed volume matches the analytic 0.25-/0.5-chamfer prism. A small `_check_lr_symmetry` audit (vertex counts within tolerance of each side face) confirms the result is symmetric (`22 vs 22`, `26 vs 26`) before the build proceeds.
- **Revolve vs guided-loft for an axisymmetric sub-feature (clevis_3 G10, G18) — and why the rim fillet decides it.** Each pivot boss is defined by two *concentric* circles (an outer base circle and a smaller/larger terminus circle) plus a single in-plane three-point-arc "guide rail" — which is, by construction, the meridian of a **surface of revolution**. The natural first instinct is a guided loft (`BRepFill_PipeShell` between the two circles along the rail), and it does produce a closed boss, but its side wall comes out as a wobbly **BSPLINE** surface whose base rim can only accept a **~0.013 mm** fillet — so the guideline's 0.2 mm rim fillet (G14 / G22) is geometrically impossible on it. Rebuilding the boss with `revolve(Face(meridian), axis, 360°)` instead gives an exact surface of revolution whose base rim is a true **CIRCLE** with an effectively unlimited max-fillet, and the 0.2 mm rim fillet then takes cleanly. The lesson: when a feature is axisymmetric, build it with `revolve`, not a loft — the loft's spline rim is both less faithful and unfilletable. The diagnostic tell is in the fillet-target `[diag]` block, where the matched rim prints as `CIRCLE` (revolve) vs `BSPLINE` (loft).
- **A loft that *joins* two disjoint bodies (clevis_3 G24).** The literal source coordinates leave a 5 mm gap in Y between the fork (`Y = 0..15.5`) and the pin (`Y = 20.5..30.5`), so up to G23 the model is two disjoint solids. G24 closes it: extract the fork's planar **back face at `Y = 15.5`**, `loft([back_face, G23_circle])` to the `r = 4.0` circle at `Y = 20.5`, then `fork + loft + pin` unions all three into ONE connected solid. One build123d quirk surfaced here — `loft` only accepted the two **faces** as cross-sections; passing the equivalent **wires** tripped an OCCT "more than one wire is required" check and returned nothing — so the loft is always built face-to-face. After the union a `.clean()` collapses the now-internal shared faces and the body reports a single solid.
- **Fillet / chamfer with an OCCT-robustness fallback.** Bulk fillet/chamfer of all selected edges in a single call occasionally fails on one problematic edge, so the helpers try the whole set at once and, on failure, retry edge-by-edge and skip only the few that won't take. On the bearing_link_3 the bulk path succeeded outright (16/16 fillets, 8/8 chamfers). The clevis_3 fans this out across many small finishing steps — six circular **rim fillets** on the two bosses (G12/G13/G14 = r 0.2/0.15/0.2; G20/G21/G22 mirror them), the four **loft-edge fillets** at r = 2.0 (G25), and the two **bore-rim fillets** at r = 0.25 (G28) — all of which land in the bulk path once each rim is a true circle (see the revolve note) and each fillet radius clears the local max-fillet.
- **Un-stitching a solid into a surface body (bearing_link_3 G7, clevis_3 G29).** After all the solid-modelling steps the part is un-stitched: the finished `Solid`'s faces are collected and rebuilt as an open `Shell` / `Compound` of individual `Face` objects, faithful to the guideline's "un-stitch solid → surface body" step. The bearing_link_3 un-stitches into 40 faces; the clevis_3 into **93 faces**. The exported part is therefore an open shell, and the comparison uses the **surface** script (area / Hausdorff / slices), even though the part was *built* as a solid. The fact that the clevis_3's exported STL is `is_watertight = False` while the reference is watertight is the expected consequence of the un-stitch, not a defect.
- **Spline handling and CSV overflow columns.** Splines exported as `spline_<N>_points` carry all N control points in a single row; `_row_all_xyz_triples` recovers the overflow under `csv.DictReader`'s `None` key. Used by `5x15mm_1mm_globe_post`; not needed by the clevis_3 (its 21 sketches are all lines, three-point arcs and three-point circles).
- **Endpoint precision through the chain walker.** Adjacency matching rounds each `(u, v)` endpoint to 0.01 mm via `_kep`, but the rounded keys never leak into `Edge.make_*` calls — the walker keeps the original unrounded tuples alongside the rounded keys, since a 0.001 mm endpoint mismatch is enough to produce an "Edges are disconnected" error from `Wire(...)`.
- **`build123d.revolve()` / `loft()` edge cases.** `revolve()` quietly returns an empty `Compound` on a bare open `Wire` (the five revolve parts drop to OCCT `BRepPrimAPI_MakeRevol`); on the clevis_3 the boss revolves run on a **closed meridian `Face`**, which `revolve()` handles correctly. `loft()` on the clevis_3 needed **faces, not wires** (wires trip an OCCT multi-wire check). The pattern across the project: build123d's high-level wrappers are convenient but each has a degenerate input class worth knowing — check `len(result.faces())`/`result.volume` before assuming success.
- **Filename guideline-range convention.** Output filenames carry the active guideline range so multiple checkpoint exports coexist — the homing_block uses `G_1_6`, the bearing_link_3 `G_1_7`, and the clevis_3 `G_1_29` (`..._clevis_3_G_1_29.stl`, `..._summary_G_1_29.txt`, `..._area_history_G_1_29.txt`, `..._build123d_vs_reference_G_1_29.txt`).
- **Per-guideline checkpoints.** Three top-of-file flags (`VIEW_AT`, `STOP_AFTER_VIEW`, `EXPORT_AT_CHECKPOINT`) let you halt at any guideline, send the cumulative state to the OCP viewer on port 3939, and optionally export mid-pipeline. For the clevis_3 the valid checkpoint numbers are 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29 (G3 is the final export step).
- **Surface-area tracking.** Every guideline's cumulative surface area is recorded in the summary and a standalone `<part>_area_history_G_1_N.txt`. The sign of each guideline's Δ-area is predictable and is the single most valuable first-run check: extrude / cap / loft / revolve / fuse go **up**; intersect / cut / fillet / chamfer go **down**; un-stitch is **neutral**. The clevis_3's history is the longest audit trail in the project (28 geometry steps): the base pin/block/intersect set the body, G5/G6 take area down (slot fillet then symmetric slot-mouth chamfer), each boss adds a revolve (up) then an extrude-cut bore (down) then three rim fillets (down), G24's loft+join adds the transition (up), G25/G26 fillet+chamfer down, G27 bore down, G28 rim-fillet down, and G29 un-stitch is area-neutral — ending at **1276.14 mm²** across 93 faces. Any step whose delta came out with the wrong sign pointed straight back at the guideline that introduced the wrong geometry.

### A note on `zaphod_bot_mec_fbcoup_3mm_globe` — why it took 1 hour

The 3mm_globe is structurally the simplest possible PICSY-style part: a single open profile revolved about a single axis line, 4 guidelines total (G1, G2, G4, with G3 as the final export step). The hour split roughly as ~20 min on the parser side (`parse_three_point_arcs`, the open-chain walker, plane auto-detect for X-constant sketches), ~15 min isolating and fixing `build123d.revolve()`'s empty-`Compound` silent failure on an open wire (drop to OCCT `BRepPrimAPI_MakeRevol`), ~10 min diagnosing a 10× CSV-vs-reference scale mismatch (single `gp_Trsf.SetScale(origin, 0.1)` at G4; post-scale area 40.988 mm² vs 40.9073 mm², 0.18% off), and ~15 min on a Y-axis-wobble construction line, the `BASE_DIR` plumbing, and the comparison.

Two notes worth recording: `build123d.revolve()` on open wires silently returns an empty Compound (check `len(result.faces())`); CSV-vs-reference unit mismatch is silent and uniform (detect by importing both into Fusion, fix with a post-build scale).

### A note on `zaphod_bot_mec_fbcoup_5x15mm_1mm_globe_post` — why it took 1 h 15 min

Second part, same 4-guideline structure, more complex geometry (14 primitives incl. the repo's first spline) and a missing-bridge CSV defect. ~15 min folder/path setup; ~20 min adding spline support and fixing the `csv.DictReader` overflow-under-`None` bug; ~25 min auto-repairing the missing-bridge defect (the walker saw 4 free endpoints, not 2 — a short Line at Z = 5.084 was missing, reinserted by enumerating off-axis free-endpoint pairs and trial-walking each); ~10 min on a precision-leak bug (rounded keys leaking into `Edge.make_line`); ~5 min on the comparison. Final: 404.55 mm² vs 403.99 mm² (0.14%), Hausdorff 0.0092 mm.

### A note on `zaphod_bot_mec_fbcoup_5x15mm_2mm_globe_post` — why it took 1 hour

Slightly-larger sibling of the 1mm-post; same structure, cleaner source CSV (15 primitives, no splines, no missing bridge). ~10 min setup; ~15 min *removing* the spline/overflow/bridge machinery this part doesn't need; ~10 min on a clean dry run (2 free endpoints at Z = 4.008); ~20 min on G4 + comparison (15 faces, 414.11 mm² vs 413.49 mm², 0.151%); ~5 min cross-checking against the 1mm-post. Two notes: a cleaner CSV genuinely saves time; strip what you don't need.

### A note on `zaphod_bot_mec_fbcoup_5x15mm_presentation_post` — why it took 30 min

First **closed** profile (12 primitives, zero free endpoints) on a **Z-constant** plane. ~5 min setup; ~10 min adding the `walk_closed_chain` variant; ~10 min dry run + G4; ~5 min comparison — 0.017%, Hausdorff 0.0144 mm, the tightest run at the time, both meshes watertight.

### A note on `zaphod_bot_mec_fbcoup_5x25mm_presentation_post` — why it took 20 min

Near-pure parametric clone of the 5x15mm presentation_post — only the Y-extent (30 vs 20 mm) and the S2 axis endpoints differ. ~5 min setup; ~3 min connectivity pre-flight; ~7 min dry run + G4; ~5 min comparison — 0.020%, Hausdorff 0.0151 mm, all slices ≤ 0.151%. The build123d STL came out `is_watertight = False` despite identical topology to the watertight sibling — a tessellation-only artefact. The lowest build time of the project.

### A note on `zaphod_bot_mec_de_man_out_printer_proto_homing_block` — why it took 50 min

First departure from surface-of-revolution: surface-extrude a closed profile both ways, patch the ends, Boolean-trim holes and overshoot, across six guidelines. ~10 min setup (CSV/plane/walker layer carried over; revolve block removed); ~15 min on the tapered upper wall (the one real fight — `BRepOffsetAPI_MakeDraft` tapered the wrong way and under-rose by `cos 45°`, so the taper was built as a 2-D offset + ruled loft); ~10 min on the three-point-circle parser, the two cap patches and the two trim guidelines; ~10 min on the first dry run and the area history (first negative deltas: G5 = −36.31 = `4·π·1.7²`, G6 = −42.72); ~5 min comparison, the tightest of the project (0.011%, Hausdorff 0.0024 mm).

### A note on `zaphod_bot_mec_de_man_out_printer_proto_bearing_link_3` — why it took 2 hr

First genuine solid-Boolean part — two perpendicular link profiles extruded and **intersected** into a cross-yoke, two perpendicular bores cut, outer edges filleted, bore mouths chamfered, then un-stitched into a surface body. First to run to G7. The 2 hr was concentrated in G5 (the S5 edge selection): an EPSILON-tight match selected nothing because the reconstructed outer edges sit ~0.7 mm off the extracted S5 arcs, so the fix was to sample each arc into a cloud and select body edges within `FILLET_MATCH_TOL`, set just below the gap in the per-edge max-distance histogram (≤ 0.703 mm real edges vs ≥ 1.59 mm everything else → `FILLET_MATCH_TOL = 1.0`). Every aggregate metric landed 🟢 EXCELLENT (0.043%, Hausdorff 0.0234 mm). Three notes: a non-coplanar "sketch" CSV is an edge-selection cloud, not a profile; edge-selection tolerance must reflect reconstruction drift, not source precision; a body-forming Boolean (the intersection) can be a negative area delta and the sign is the check.

### A note on `zaphod_bot_mec_de_man_out_printer_proto_clevis_3` — why it took 8 hr

The clevis_3 is the ninth part and by every measure the largest build in the project — 28 geometry guidelines over 21 source sketches, combining every operation family the repo has developed (tapered extrude, surface-extrude, boolean intersect, fillet, chamfer, revolve, loft, extrude-cut bore, un-stitch) into a single clevis/yoke. At 8 hr it is the longest build so far; unlike the bearing_link_3 (where the cost was one guideline), here the time was spread across four genuinely new sub-problems. Build order is `G1, G2, G4, G5, G6` (the forked clevis base) → `G7…G14` (upper pivot boss + bore + rim fillets) → `G15…G22` (lower pivot boss, the mirror of the upper) → `G23…G29` (pin transition, edge finishing, pin bore, un-stitch), with G3 (export) last. The 8 hr split roughly as:

- **~45 min** standing up the folder and the base clevis (`G1, G2, G4, G5`). The CSV / plane / walker / circle-parser / checkpoint / area-tracker layer all carried over from the homing_block and bearing_link_3. The base body is the pin (S1 circle on `Y = 30`, extruded −Y 9.5 straight + +Y 0.5 with a 45° inward taper so the cap profile shrinks), the block (S2 rounded-bottom rectangle on `Z = 15`, surface-extruded −Z 22), and the forked clevis (S3 13-line silhouette on `X = 10`, extruded −X 23 and **intersected** with the block — the pin is deliberately left out of the intersect, since it lies outside the S3 silhouette's Y-range, and rejoined later). G5 fillets the two back-slot corners at r = 2.0. The one recurring gotcha was the pin **taper sign** — the source writes it as "−45°" but means "top circle smaller," which is `taper = +45` in build123d.

- **~1 hr** on **G6**, the slot-mouth chamfer, which is where the symmetric-chamfer technique was worked out. The 12 named edges (6 Lines + 6 three-point arcs, including the four G5 fillet arcs) run tangentially into each other at their shared vertices, so a single `chamfer(all 12, 0.25)` fails outright, and chamfering them in co-facial batches — which *does* complete — comes out **left/right asymmetric** (one side picks up more facets than the other, 26 vs 16 vertices). The resolution was the half-mirror-fuse: cut the fork at its `X = 4.736` mirror plane, chamfer one half (the front arcs become half-arcs ending on the cut, which removes the tangent conflicts), then mirror and fuse. The removed volume then matches the analytic chamfer-prism value, and a vertex-symmetry check (`22 vs 22`) confirms it before proceeding.

- **~1 h 30 min** on the two pivot bosses (`G7…G14` upper, `G15…G22` lower). Each boss is two concentric circles + a three-point-arc guide rail, built into a boss, bored through with an extrude-cut, and finished with three circular rim fillets (r 0.2 / 0.15 / 0.2). The bulk of the time went into the **revolve-vs-loft** decision: a guided `PipeShell` loft between the two circles produces a BSPLINE side wall whose base rim only takes a ~0.013 mm fillet, so the 0.2 mm rim fillet (G14 / G22) is impossible — until the boss is rebuilt with `revolve(Face(meridian), axis, 360°)`, which yields a true-circle rim that fillets cleanly. The lower boss (G15–G22) is the exact mirror of the upper about the slot mid-plane `Z = 5.8`; once the upper was correct the lower was a near-parametric clone, and the matching boss volumes (20.2258 mm³ each) and bore-cut volumes (−64.05 mm³ each) confirmed the symmetry.

- **~1 hr** on **G24**, the loft that joins the fork to the pin. The literal coordinates leave a 5 mm gap in Y, so up to here the model is two disjoint solids; G24 lofts the fork's `Y = 15.5` back face to the G23 `r = 4.0` circle at `Y = 20.5` and unions pin + fork + loft into one connected body. The time went into the build123d `loft` quirk — passing the two **wires** tripped an OCCT "more than one wire is required" check and returned nothing, while passing the two **faces** worked — and into confirming the union closes to a single solid (`.clean()` collapses the shared internal faces).

- **~1 hr** on the remaining finishing steps `G25…G28`: the four loft-transition edges filleted at r = 2.0 (G25, matched from S19), the top (`Z = 11.6`) and bottom (`Z = 0`) outer-perimeter edges chamfered at 0.5 (G26, S20 — the same tangent-edge problem as G6, so the half-mirror chamfer was reused, `26 vs 26` symmetric), the axial pin bore (G27, S21 circle on `Y = 30.5` extrude-cut 15 mm along −Y), and the two bore-rim fillets at r = 0.25 (G28).

- **~30 min** on **G29** (un-stitch the finished solid into a 93-face open Shell — the surface model the comparison consumes) and the final `.clean()` + STL/STEP export.

- **~1 h 15 min** on the comparison run, the area-history sign audit across all 28 steps, and this README entry. Every aggregate metric landed 🟢 EXCELLENT: surface area **0.137%** (1276.1407 mm² vs 1274.3982 mm²), Hausdorff **0.0440 mm**, mean distance **0.0059 mm**, RMS 0.0091 mm, 99th-pct 0.0293 mm, bounding box ≤ 0.0003 mm/axis, centroid distance **0.0018 mm**. All seven Y-slices ✅ PASS (worst **0.334%** at Y = 1.525, the front lip of the clevis nose). The build123d STL is an open surface (`is_watertight = False`, 93 faces) from the G29 un-stitch while the reference tessellates watertight — harmless for surface comparison.

Four notes worth recording for future parts:

- **Symmetric chamfers/fillets of tangent edge-chains: cut, do one half, mirror, fuse.** When a chamfer (or fillet) targets a closed chain of edges that meet *tangentially*, OCCT can't do them all at once and any sequential batching breaks left/right symmetry. If the body has a mirror plane, intersect off one half, finish that half (tangent neighbours that crossed the plane become half-edges terminating on the cut, which OCCT *can* corner), then mirror + fuse. Symmetric by construction, and the removed volume should equal the analytic chamfer/fillet prism — check it.

- **An axisymmetric sub-feature is a `revolve`, not a loft — and the rim fillet proves it.** Two concentric circles plus an in-plane guide arc define a surface of revolution; a guided loft will *look* right but emit a spline side wall whose rim won't fillet (max ~0.013 mm here). Build it with `revolve` so the rim is a true circle. The `[diag]` line that prints the matched rim's `GeomType` (`CIRCLE` vs `BSPLINE`) is the fast tell for which path you're on.

- **`build123d.loft()` wants faces, not wires.** Passing the two cross-section **wires** tripped an OCCT "more than one wire is required" check and silently produced nothing; passing the two **faces** built the loft. Same family of high-level-wrapper degeneracy as `revolve()` on a bare open wire — always sanity-check `.volume`/`.faces()` on the result.

- **A loft can be a *join*, not just a feature.** When the source coordinates leave two bodies disjoint by design, a loft between a face on one and a profile on the other, followed by a union of all three, is the clean way to bridge them into a single solid — and the area-history delta (a clear positive step at the join) confirms it landed.

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

The **cross-section slice comparison** has proven especially valuable on complex parts: it cuts both meshes at multiple Y-plane positions (auto-derived from mesh bounds) and compares the outline perimeter at each cut. Aggregate metrics like Hausdorff or mean-distance can mask a 1–2% feature-level discrepancy because the affected region is small compared to the total surface — the slice test bypasses this by comparing geometry at specific cross-sections. On the eight completed parts every slice has passed comfortably: ≤ 0.24% on the 1mm-post, ≤ 0.283% on the 2mm-post, ≤ 0.178% on the 5x15mm presentation_post, ≤ 0.151% on the 5x25mm presentation_post, ≤ 0.014% on the homing_block, ≤ 0.042% on the bearing_link_3, and ≤ 0.334% on the clevis_3 (worst at Y = 1.525, the front lip of the clevis nose, where a small absolute deviation on the chamfered rounded nose resolves to a relatively larger percentage of a small perimeter). The worst slice on each globe-post lands at the narrow neck just before the globe terminates, for the same small-perimeter reason.

For **solid parts** the original volume + symmetric-volume-difference comparison from the [Thor assembly project](https://github.com/avajones081196/Ava_AngelLM_Thor_Art1_build123d) is used. Note that "solid" here refers to how the part is *built* in build123d, not whether the exported STL happens to tessellate as a watertight closed mesh — and the bearing_link_3 and the clevis_3 are the edge cases that make the distinction concrete: both are **built** by solid Boolean modelling but are **un-stitched into a surface body** (at G7 and G29 respectively) before export, so both are compared with the **surface** script. Surface-built parts may *or may not* register as watertight in mesh tools depending on tessellation luck (the 5x15mm presentation_post and the bearing_link_3 did; the 5x25mm, the homing_block and the clevis_3 did not), but either way they use the surface comparison script.

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

The same layout is used for every part. Output filenames carry the active guideline range so checkpoint exports do not clobber each other — the homing_block uses the `G_1_6` suffix throughout, the bearing_link_3 uses `G_1_7`, and the clevis_3, which runs to G29, uses `G_1_29` (`zaphod_bot_mec_de_man_out_printer_proto_clevis_3_G_1_29.stl`, `..._summary_G_1_29.txt`, `..._area_history_G_1_29.txt`, `..._build123d_vs_reference_G_1_29.txt`). The clevis_3's `csv_merged/` holds all 21 sketch CSVs (S1–S21), including the pure edge-selection CSVs (S5/S19/S20) that are not sketch profiles.

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

Set `VIEW_AT = None` for a clean end-to-end run that only writes the final outputs. For the homing_block the valid `VIEW_AT` checkpoint numbers are 1, 2, 4, 5, 6; for the bearing_link_3 they are 1, 2, 4, 5, 6, 7; for the clevis_3 they are 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29 (G3 is the final export step in every case). The clevis_3 exposes its finishing sizes as single top-of-file constants where the guideline didn't pin them, and reuses the bearing_link_3's `CHAMFER_MM` / `FILLET_MATCH_TOL` pattern for re-sizing and edge-selection tolerance in one place.

---

## Acceptance Criteria — How the Ratings Are Set

For surface parts (every completed part to date — the five fibre-coupler revolves, the homing_block, the bearing_link_3 and the clevis_3), the rating thresholds are aligned with typical FDM 3D-printer manufacturing tolerances rather than CAD-tight micrometre tolerances, since the zaphod-bot parts are designed for FDM printing. A well-tuned consumer FDM printer (Prusa, Bambu, etc.) has roughly 0.1–0.5 mm positional accuracy, with industry rule-of-thumb specs of ±0.5 mm. Anything below that floor is below what the manufacturing process can resolve, so it counts as "indistinguishable from the original" in practice.

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

A part needs to pass **every aggregate metric** (surface area, bounding box, centroid, Hausdorff, mean distance) to earn the ✅ Complete badge. The cross-section slice test is treated as a confirmation test rather than a strict gate: if all aggregate metrics pass AND the Hausdorff worst-case is under the FDM print-tolerance floor of 0.5 mm, then an isolated 🟠 ACCEPTABLE slice (one slice in the 2–5% band) is treated as a known minor variance rather than a failure. The clevis_3 — the most feature-dense part to date — still clears every aggregate comfortably (Hausdorff 0.044 mm, two orders of magnitude under the floor) with all seven slices ≤ 0.334%.

A part is marked ⚠ Review required (rather than ✅ Complete) if any aggregate metric fails, if Hausdorff exceeds 0.5 mm, or if more than one cross-section slice fails — in any of those cases the deviation is print-visible.

Surface-area % thresholds are kept tight since that metric is a unitless ratio and not bounded by print tolerance.

These mirror reverse-engineering / metrology defaults adjusted for FDM manufacturing (vs. machined-tight CAD comparison, where ≤ 0.05 mm thresholds would apply). Per-part the user may adjust thresholds at the top of the comparison script.

---

## Notes on the Reference STLs

The reference STLs come from upstream tessellation by the zaphod-bot repo's authors. Some are not perfectly closed meshes — `is_watertight` may report `False`. This is normal: STL exports often leave non-coincident edges across feature boundaries. For the comparison script this is fine because surface comparison does not require closure. The inverse also happens — the homing_block's and the clevis_3's upstream references tessellate watertight while the build123d-side STLs do not (the clevis_3 because it is un-stitched into 93 free faces at G29). The bearing_link_3 is the opposite-again case: **both** sides tessellate watertight even though the build123d body is un-stitched into 40 free faces at G7. All of these situations are equally harmless for surface comparison, which is why watertightness is never part of the acceptance criteria for a surface part.

---

## License

This repo follows the upstream [zaphod-bot repository's license](https://github.com/Scottapotamas/zaphod-bot). All build123d reconstruction code and comparison utilities are provided as-is for educational and reverse-engineering purposes.
