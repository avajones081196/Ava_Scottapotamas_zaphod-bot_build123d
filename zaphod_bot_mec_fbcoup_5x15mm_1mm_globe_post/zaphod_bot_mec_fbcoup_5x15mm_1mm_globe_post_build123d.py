"""
zaphod_bot_mec_fbcoup_5x15mm_1mm_globe_post_build123d.py

Reference STL: https://github.com/Scottapotamas/zaphod-bot/blob/master/mechanical/fibre_couplers/manf_outputs/5x15mm_1mm_globe_post.STL


Surface part (open shell, surface of revolution).

Sketch summary (planes auto-detected; both axis-aligned to X = 3.848):

  S1  X = 3.848  8 Lines + 5 three-point arcs + 1 five-point spline —
                 open profile chain. The two on-axis free endpoints sit on
                 the S2 axis line (Z=4.008) at Y=17.0 and Y=20.8 — the
                 on-axis gap is closed by the revolve itself.
                 NOTE: the source CSV is missing one bridging line between
                       the spline end (Y=8.591, Z=5.084) and Line11 end
                       (Y=13.0, Z=5.084). Z values match exactly, so we
                       insert this bridge programmatically (see template
                       §7 item 5 — CSV typo / programmatic correction).
  S2  X = 3.848  1 Line from (3.848, 17.0, 4.008) to (3.848, -3.0, 4.008)
                 — construction axis for the revolve (the Y-direction line
                 at Z=4.008 inside the X=3.848 plane).

Guidelines:

  G1 – Read S1; build the open profile wire (8 lines + 5 arcs + 1 spline
       + 1 programmatic bridge line = 15 edges total) on X = 3.848.
  G2 – Read S2; build the construction axis line. No surface
       contribution — used by G4 only.
  G3 – LAST: compound + .clean() + STL/STEP/summary export.
  G4 – Surface-revolve the G1 profile wire about the G2 axis line →
       1 surface-of-revolution shell (the globe-post).

Cross-platform:
  BASE_DIR derived from script location. No hardcoded paths.

Code-style reference: zaphod_bot_mec_fbcoup_3mm_globe_build123d.py
(used for helpers and patterns only — geometry rules differ here:
new primitive type `spline_5_points` and different plane offsets).
"""
import csv
import math
import re
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

# ══════════════════════════════════════════════════════════════════════════
# Tolerance named constants
# ══════════════════════════════════════════════════════════════════════════
EPSILON_MM      = 1e-3   # endpoint matching, axis-aligned plane detection
SVD_PLANE_TOL   = 1e-2   # residual threshold for SVD plane fit
STL_TOLERANCE   = 5e-4   # export tolerance for STL
AXIS_SNAP_MM    = 5e-2   # axis component snap tolerance
BRIDGE_V_TOL    = 1e-2   # tolerance for "same V coordinate" when inserting
                         # a programmatic bridge between two free endpoints


# ══════════════════════════════════════════════════════════════════════════
# Paths
# ══════════════════════════════════════════════════════════════════════════
BASE_DIR    = Path(__file__).resolve().parent
FOLDER_NAME = BASE_DIR.name
CSV_DIR     = BASE_DIR / "csv_merged"

# This part has S1..S2.
S_CSV = {n: CSV_DIR / f"Fusion_Coordinates_S{n}.csv" for n in range(1, 3)}

if not CSV_DIR.exists():
    sys.exit(f"❌ csv_merged folder not found at: {CSV_DIR}")
for n, p in S_CSV.items():
    if not p.exists():
        sys.exit(f"❌ Required CSV missing: {p}")

# Log every CSV path + size on first read so re-uploads are visible.
print("=" * 70)
print(f"[CSV FRESHNESS]  CSV_DIR = {CSV_DIR}")
for n in sorted(S_CSV):
    p = S_CSV[n]
    st = p.stat()
    print(f"  S{n}: {p.name}  size={st.st_size} B  mtime={st.st_mtime:.0f}")
print("=" * 70)


# ══════════════════════════════════════════════════════════════════════════
# build123d + OCP imports
# ══════════════════════════════════════════════════════════════════════════
from build123d import (
    Vector, Plane, Axis,
    Edge, Wire, Face, Shape, Compound,
    revolve,
    export_stl, export_step,
    GeomType,
)
from ocp_vscode import show, set_port, reset_show
set_port(3939)


# ══════════════════════════════════════════════════════════════════════════
# VIEWER + EXPORT CHECKPOINT CONFIG
# Valid checkpoint numbers: 1, 2, 4  (G3 is the final export step).
# Set VIEW_AT to None for a full G1..G4 run.
# ══════════════════════════════════════════════════════════════════════════
VIEW_AT                 = 4
STOP_AFTER_VIEW         = True
EXPORT_AT_CHECKPOINT    = True

GUIDELINE_RANGE = "G_1_4"


# ══════════════════════════════════════════════════════════════════════════
# CHECKPOINT MACHINERY
# ══════════════════════════════════════════════════════════════════════════
stage_pieces = []
area_history = []


def cumulative_area(pieces):
    total = 0.0
    for p in pieces:
        try:
            a = p.area
            if a is not None:
                total += float(a)
        except Exception:
            pass
    return total


def _write_area_history_summary(stop_g_num=None):
    if not area_history:
        return
    last_g = stop_g_num if stop_g_num is not None else area_history[-1]["g"]
    name = f"{FOLDER_NAME}_area_history_G_1_{last_g}.txt"
    path = BASE_DIR / name
    lines = [
        "=" * 60,
        f"AREA HISTORY  :  {name}",
        f"Time          :  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 60, "",
        f"{'Guideline':>10}  {'Cumulative area (mm²)':>22}  {'Δ from prev (mm²)':>20}  Label",
        "-" * 90,
    ]
    for entry in area_history:
        lines.append(
            f"  G{entry['g']:<8d}  {entry['area']:>22.3f}  "
            f"{entry['delta']:>+20.3f}  {entry['label']}"
        )
    lines.append("=" * 60)
    with open(path, "w") as f:
        f.write("\n".join(lines))
    print(f"     [AREA] History saved to: {path}")


def write_checkpoint_export(g_num, label, pieces):
    cp_range = f"G_1_{g_num}"
    cp_stl   = BASE_DIR / f"{FOLDER_NAME}_{cp_range}.stl"
    cp_step  = BASE_DIR / f"{FOLDER_NAME}_{cp_range}.step"
    cp_txt   = BASE_DIR / f"{FOLDER_NAME}_summary_{cp_range}.txt"
    try:
        compound = Compound(children=list(pieces))
        try:
            compound = compound.clean()
        except Exception:
            pass
        export_stl(compound, str(cp_stl), tolerance=STL_TOLERANCE)
        export_step(compound, str(cp_step))
        print(f"     [CHECKPOINT] Wrote: {cp_stl.name}")
        print(f"     [CHECKPOINT] Wrote: {cp_step.name}")
    except Exception as exc:
        print(f"     [CHECKPOINT] Export failed: {exc}")
    lines = [
        "=" * 60,
        f"CHECKPOINT SUMMARY  :  {FOLDER_NAME}_summary_{cp_range}.txt",
        f"Time                :  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Guideline reached   :  G{g_num}  ({label})",
        f"Pieces in compound  :  {len(pieces)}",
        f"Cumulative area     :  {cumulative_area(pieces):.3f} mm²",
        "=" * 60,
    ]
    with open(cp_txt, "w") as f:
        f.write("\n".join(lines))
    print(f"     [CHECKPOINT] Wrote: {cp_txt.name}")
    _write_area_history_summary(g_num)


def checkpoint(g_num, label, *new_pieces):
    stage_pieces.extend(new_pieces)
    cum_area = cumulative_area(stage_pieces)
    delta = cum_area - (area_history[-1]["area"] if area_history else 0.0)
    area_history.append({"g": g_num, "label": label,
                         "area": cum_area, "delta": delta})
    print(f"     [AREA] After G{g_num}: cumulative = {cum_area:.3f} mm²  "
          f"(Δ = {delta:+.3f} mm²)")
    if VIEW_AT != g_num:
        return
    print(f"\n[VIEW] Cumulative state after G{g_num} ({label})")
    print(f"       Pieces in stage_pieces: {len(stage_pieces)}")
    try: reset_show()
    except Exception: pass
    try:
        show(*stage_pieces)
        print(f"       Sent {len(stage_pieces)} shape(s) to OCP viewer (port 3939)")
    except Exception as e:
        print(f"       OCP viewer call failed: {e}")
    if EXPORT_AT_CHECKPOINT:
        write_checkpoint_export(g_num, label, stage_pieces)
    if STOP_AFTER_VIEW:
        print(f"\n[VIEW] STOP_AFTER_VIEW=True — halting after G{g_num}.")
        _write_area_history_summary(g_num)
        sys.exit(0)


# ══════════════════════════════════════════════════════════════════════════
# CSV / GEOMETRY HELPERS
# ══════════════════════════════════════════════════════════════════════════
def read_rows(csv_path):
    """Plain DictReader read; OK for short rows (lines / arcs / splines)."""
    with open(csv_path, "r") as f:
        return list(csv.DictReader(f))


def _is_missing(cell):
    if cell is None:
        return True
    s = cell.strip()
    return s == "" or s.upper() == "NA"


def _norm_draw_type(raw):
    return re.sub(r'_\d+$', '', raw.strip().lower()).rstrip('_')


def _collect_all_points(rows):
    """Pull every non-missing (Xi,Yi,Zi) triple out of the row, for plane
    detection. Splines contribute up to 5 points; lines 2; arcs 3.
    Overflow columns (the Fusion add-in writes more points than the CSV
    header declares for splines) are included via _row_all_xyz_triples."""
    pts = []
    for r in rows:
        # _row_all_xyz_triples handles both named X1..Z3 cells and the
        # overflow-via-None-key that csv.DictReader produces for spline
        # rows with >3 points.
        pts.extend(_row_all_xyz_triples(r))
    return np.array(pts)


def detect_sketch_plane(rows, tol_axis=EPSILON_MM, tol_plane=SVD_PLANE_TOL):
    """Axis-aligned detection first; SVD fallback for tilted sketches."""
    pts = _collect_all_points(rows)
    for axis_idx, axis_letter in ((0, "x"), (1, "y"), (2, "z")):
        col = pts[:, axis_idx]
        if col.max() - col.min() < tol_axis:
            return ("axis", axis_letter, float(col.mean()))
    centroid = pts.mean(axis=0)
    centred  = pts - centroid
    _, _, vh = np.linalg.svd(centred, full_matrices=False)
    normal = vh[-1] / np.linalg.norm(vh[-1])
    if abs((centred @ normal)).max() > tol_plane:
        raise ValueError("Sketch points are not coplanar.")
    return ("general", tuple(centroid), tuple(normal))


def world_vec_axis(in_plane_pt, axis, plane_value):
    """Lift a (u, v) in-plane point to world-space Vector(x, y, z)."""
    u, v = in_plane_pt
    if   axis == "z": return Vector(u, v, plane_value)
    elif axis == "y": return Vector(u, plane_value, v)
    else:             return Vector(plane_value, u, v)


def in_plane_uv(row, idx, axis):
    """Project the i-th coord triple of a CSV row down to its in-plane (u, v)."""
    x = float(row[f"X{idx}"])
    y = float(row[f"Y{idx}"])
    z = float(row[f"Z{idx}"])
    if   axis == "z": return (x, y)
    elif axis == "y": return (x, z)
    else:             return (y, z)


def _row_present_indices(row):
    """Return the sorted list of i such that (Xi,Yi,Zi) is fully populated."""
    out = []
    i = 1
    while True:
        xk = f"X{i}"
        if xk not in row:
            break
        if not _is_missing(row[xk]):
            out.append(i)
        i += 1
    return out


def _row_all_xyz_triples(row):
    """Return ALL (x, y, z) float triples from a row, INCLUDING any overflow
    columns the standard header (X1..Z3) doesn't cover.

    The Fusion add-in writes each primitive on one line with a variable
    number of (X, Y, Z) triples, but the CSV header only declares 9
    coordinate columns (X1..Z3). When a spline row carries more than 3
    points, csv.DictReader collects the overflow strings under the key
    None as a flat list (e.g. ['3.848', '6.503', '5.156', ...] for a
    5-point spline). We append those overflow triples in order so a
    5-point spline returns 5 points, a 7-point spline returns 7, etc."""
    triples = []
    # First, named columns X1/Y1/Z1, X2/Y2/Z2, ...
    for i in _row_present_indices(row):
        triples.append((
            float(row[f"X{i}"]),
            float(row[f"Y{i}"]),
            float(row[f"Z{i}"]),
        ))
    # Then any overflow stored under the None key. DictReader puts these
    # as a list-of-strings when the row has more cells than the header.
    extra = row.get(None)
    if extra:
        # Defensive: DictReader may also produce a single string for the
        # overflow on some Python versions; normalise to a list.
        if isinstance(extra, str):
            extra = [s.strip() for s in extra.split(",")]
        clean = [s for s in extra if not _is_missing(s)]
        if len(clean) % 3 != 0:
            raise ValueError(
                f"Overflow cells in row are not a multiple of 3: {extra}"
            )
        for k in range(0, len(clean), 3):
            triples.append((float(clean[k]),
                            float(clean[k + 1]),
                            float(clean[k + 2])))
    return triples


def _project_uv(xyz, axis):
    """Project a world (x, y, z) triple onto the (u, v) plane axes."""
    x, y, z = xyz
    if   axis == "z": return (x, y)
    elif axis == "y": return (x, z)
    else:             return (y, z)


def parse_line_segments(rows, axis):
    """Return list of ((u1,v1), (u2,v2)) for every Line row."""
    segs = []
    for r in rows:
        if not _norm_draw_type(r["Draw Type"]).startswith("line"):
            continue
        segs.append((in_plane_uv(r, 1, axis), in_plane_uv(r, 2, axis)))
    return segs


def parse_three_point_arcs(rows, axis):
    """Return list of (start, mid, end) tuples in in-plane (u,v) for every
    3_point_arc row. Fusion convention: (X1,Y1,Z1)=start, (X2,Y2,Z2)=middle
    on the arc, (X3,Y3,Z3)=end."""
    arcs = []
    for r in rows:
        if not _norm_draw_type(r["Draw Type"]).startswith("3_point_arc"):
            continue
        arcs.append((
            in_plane_uv(r, 1, axis),
            in_plane_uv(r, 2, axis),
            in_plane_uv(r, 3, axis),
        ))
    return arcs


def parse_splines(rows, axis):
    """Return list of point-tuples in in-plane (u,v) for every spline row.
    Each spline carries all of its control points in (X1,Y1,Z1)..(XN,YN,ZN).
    The Fusion add-in uses the type prefix `spline_<N>_points` (e.g.
    `spline_5_points_1`).

    NOTE: when a spline row has more than 3 points (the CSV header only
    declares X1..Z3), the extra triples sit in the row's overflow under
    csv.DictReader's None key. `_row_all_xyz_triples` recovers them."""
    splines = []
    for r in rows:
        dtype = _norm_draw_type(r["Draw Type"])
        if not dtype.startswith("spline"):
            continue
        triples = _row_all_xyz_triples(r)
        if len(triples) < 2:
            raise ValueError(
                f"Spline row has fewer than 2 populated points: {r}"
            )
        pts = [_project_uv(t, axis) for t in triples]
        splines.append(tuple(pts))
    return splines


def make_line_edge(p_uv, q_uv, axis, plane_value):
    return Edge.make_line(
        world_vec_axis(p_uv, axis, plane_value),
        world_vec_axis(q_uv, axis, plane_value),
    )


def make_3pt_arc_edge(start_uv, mid_uv, end_uv, axis, plane_value):
    return Edge.make_three_point_arc(
        world_vec_axis(start_uv, axis, plane_value),
        world_vec_axis(mid_uv,   axis, plane_value),
        world_vec_axis(end_uv,   axis, plane_value),
    )


def make_spline_edge(pts_uv, axis, plane_value):
    """Build an interpolating spline Edge through the given in-plane points
    in order. build123d's Edge.make_spline takes a sequence of Vector
    waypoints and produces a C2 B-spline that passes through each one."""
    world_pts = [world_vec_axis(p, axis, plane_value) for p in pts_uv]
    return Edge.make_spline(world_pts)


def _kep(p, tol=1e-2):
    """Endpoint key for fuzzy matching (in-plane u, v)."""
    return (round(p[0] / tol) * tol, round(p[1] / tol) * tol)


def walk_open_chain(edges_named):
    """
    P-04-style walker: given a list of (name, start_uv, end_uv, build_fn)
    entries — where each entry knows how to build its own oriented edge —
    walk them into a connected open chain. Returns a list of oriented
    edges in order, plus the in-plane chain endpoints (returned as the
    ORIGINAL unrounded (u, v) tuples, not the rounded adjacency keys).
    """
    from collections import defaultdict

    touch     = defaultdict(list)   # rounded key → list of edge indices
    originals = defaultdict(list)   # rounded key → list of original (u,v)
    for i, e in enumerate(edges_named):
        touch[_kep(e["start"])].append(i)
        touch[_kep(e["end"])].append(i)
        originals[_kep(e["start"])].append(e["start"])
        originals[_kep(e["end"])].append(e["end"])

    free_keys = [k for k, idxs in touch.items() if len(idxs) == 1]
    if len(free_keys) != 2:
        raise ValueError(
            f"Open-chain walker expected exactly 2 free endpoints; "
            f"got {len(free_keys)}: {free_keys}"
        )

    start_key = free_keys[0]
    end_key   = free_keys[1]
    start_ep  = originals[start_key][0]   # unrounded
    end_ep    = originals[end_key][0]     # unrounded

    used = [False] * len(edges_named)
    ordered = []
    cur_key = start_key
    for _ in range(len(edges_named)):
        candidates = [i for i in touch[cur_key] if not used[i]]
        if not candidates:
            raise ValueError(f"Chain broke at {cur_key}: no unused neighbor.")
        i = candidates[0]
        e = edges_named[i]
        reverse = _kep(e["start"]) != cur_key
        ordered.append(e["build"](reverse))
        used[i] = True
        cur_key = _kep(e["start"]) if reverse else _kep(e["end"])

    if cur_key != end_key:
        raise ValueError(
            f"Chain didn't terminate at expected free end "
            f"{end_key}; got {cur_key}."
        )
    return ordered, start_ep, end_ep


def _find_free_endpoints(edges_named):
    """Return the list of free (count==1) endpoints in the named-edges set.

    Returns the ORIGINAL (unrounded) endpoints — not the rounded keys —
    so that downstream code (e.g. the bridge-insertion logic) can
    construct edges whose endpoints exactly match the existing primitives
    at OCCT precision. The rounding is used only for adjacency keys."""
    from collections import defaultdict
    # Map from rounded key → list of (count_increment, original_endpoint).
    keyed = defaultdict(list)
    for e in edges_named:
        keyed[_kep(e["start"])].append(e["start"])
        keyed[_kep(e["end"])].append(e["end"])
    out = []
    for k, originals in keyed.items():
        if len(originals) == 1:
            out.append(originals[0])
    return out


# ══════════════════════════════════════════════════════════════════════════
# G1 — Read S1: 8 lines + 5 three-point arcs + 1 five-point spline on
#       X = 3.848. Build the open profile wire.
#
# We also peek at S2 NOW (full reading happens in G2) to learn the axis
# coordinate, so the bridge-selection step below can correctly EXCLUDE
# on-axis free endpoints from the candidate pool. Those on-axis ends are
# closed by the revolve itself and must remain free in the profile wire.
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G1] Reading {S_CSV[1].name}")
s1_rows = read_rows(S_CSV[1])
_pinfo1 = detect_sketch_plane(s1_rows)
if _pinfo1[0] != "axis":
    sys.exit(f"❌ G1: S1 not axis-aligned.")
_, S1_AXIS, S1_PLANE = _pinfo1
print(f"     S1 plane: {S1_AXIS.upper()} = {S1_PLANE}")

# Peek at S2 just to learn the revolve-axis V coordinate (in S1's in-plane
# (u,v) frame). Used solely by the bridge filter below.
print(f"     [Peek] Reading {S_CSV[2].name} early to learn the revolve axis")
_s2_rows_peek = read_rows(S_CSV[2])
_pinfo2_peek  = detect_sketch_plane(_s2_rows_peek)
if _pinfo2_peek[0] != "axis":
    sys.exit(f"❌ G1-peek: S2 not axis-aligned.")
_, _S2_AXIS_PEEK, _S2_PLANE_PEEK = _pinfo2_peek
_s2_lines_peek = parse_line_segments(_s2_rows_peek, _S2_AXIS_PEEK)
if len(_s2_lines_peek) != 1:
    sys.exit(f"❌ G1-peek: S2 must have exactly 1 line.")
_a_peek, _b_peek = _s2_lines_peek[0]
# In the S2 in-plane (u,v) frame, the axis runs along one component.
# Find the component that is essentially constant — that is the V value
# the bridge filter cares about (assuming S1 and S2 share an axis
# convention, which is true for the parts in this template).
if abs(_a_peek[1] - _b_peek[1]) < AXIS_SNAP_MM:
    AXIS_V_IN_S1_FRAME = 0.5 * (_a_peek[1] + _b_peek[1])
    print(f"     [Peek] Revolve axis V (S1 frame) ≈ {AXIS_V_IN_S1_FRAME:.4f}")
elif abs(_a_peek[0] - _b_peek[0]) < AXIS_SNAP_MM:
    # If U is constant in S2's frame, then "on-axis" S1 endpoints share
    # that U value. We still use V terminology below but on the U index.
    AXIS_V_IN_S1_FRAME = None
    AXIS_U_IN_S1_FRAME = 0.5 * (_a_peek[0] + _b_peek[0])
    print(f"     [Peek] Revolve axis U (S1 frame) ≈ {AXIS_U_IN_S1_FRAME:.4f}")
else:
    AXIS_V_IN_S1_FRAME = None
    AXIS_U_IN_S1_FRAME = None
    print(f"     [Peek] Revolve axis is not axis-aligned in S2 frame; "
          f"bridge filter will not exclude on-axis endpoints")


def _is_on_axis(pt, tol=AXIS_SNAP_MM):
    """Return True if the in-plane (u, v) point lies on the revolve axis."""
    u, v = pt
    if AXIS_V_IN_S1_FRAME is not None:
        return abs(v - AXIS_V_IN_S1_FRAME) < tol
    try:
        return abs(u - AXIS_U_IN_S1_FRAME) < tol
    except (NameError, TypeError):
        return False


s1_lines   = parse_line_segments(s1_rows, S1_AXIS)
s1_arcs    = parse_three_point_arcs(s1_rows, S1_AXIS)
s1_splines = parse_splines(s1_rows, S1_AXIS)
print(f"     S1 lines: {len(s1_lines)}, "
      f"three-point arcs: {len(s1_arcs)}, "
      f"splines: {len(s1_splines)}")

# Expected: 8 lines + 5 arcs + 1 spline = 14 primitives.
EXPECTED_LINES, EXPECTED_ARCS, EXPECTED_SPLINES = 8, 5, 1
if (len(s1_lines), len(s1_arcs), len(s1_splines)) != (
        EXPECTED_LINES, EXPECTED_ARCS, EXPECTED_SPLINES):
    sys.exit(
        f"❌ G1: expected {EXPECTED_LINES} lines + {EXPECTED_ARCS} arcs + "
        f"{EXPECTED_SPLINES} spline(s) in S1, got "
        f"{len(s1_lines)} + {len(s1_arcs)} + {len(s1_splines)}."
    )

for i, (a, b) in enumerate(s1_lines, 1):
    print(f"     Line{i}: ({a[0]:.3f},{a[1]:.3f}) → ({b[0]:.3f},{b[1]:.3f})")
for i, (a, m, b) in enumerate(s1_arcs, 1):
    print(f"     Arc{i}: ({a[0]:.3f},{a[1]:.3f}) via ({m[0]:.3f},{m[1]:.3f}) "
          f"→ ({b[0]:.3f},{b[1]:.3f})")
for i, pts in enumerate(s1_splines, 1):
    print(f"     Spline{i}: {len(pts)} pts, "
          f"({pts[0][0]:.3f},{pts[0][1]:.3f}) → "
          f"({pts[-1][0]:.3f},{pts[-1][1]:.3f})")

# Package every primitive with a closure that builds the oriented Edge.
named_edges = []

# Lines (oriented by chain walker)
for i, (a, b) in enumerate(s1_lines, 1):
    named_edges.append({
        "name": f"Line{i}",
        "start": a, "end": b,
        "build": (lambda a=a, b=b: (
            lambda rev: make_line_edge(b, a, S1_AXIS, S1_PLANE)
                       if rev else make_line_edge(a, b, S1_AXIS, S1_PLANE)
        ))(),
    })

# 3-point arcs
for i, (a, m, b) in enumerate(s1_arcs, 1):
    named_edges.append({
        "name": f"Arc{i}",
        "start": a, "end": b,
        "build": (lambda a=a, m=m, b=b: (
            lambda rev: make_3pt_arc_edge(b, m, a, S1_AXIS, S1_PLANE)
                       if rev else make_3pt_arc_edge(a, m, b, S1_AXIS, S1_PLANE)
        ))(),
    })

# Splines — use first and last interpolated point as the chain endpoints.
# Reversal flips the entire control-point sequence.
for i, pts in enumerate(s1_splines, 1):
    named_edges.append({
        "name": f"Spline{i}",
        "start": pts[0], "end": pts[-1],
        "build": (lambda pts=pts: (
            lambda rev: make_spline_edge(tuple(reversed(pts)), S1_AXIS, S1_PLANE)
                       if rev else make_spline_edge(pts, S1_AXIS, S1_PLANE)
        ))(),
    })

# ── Programmatic chain-bridge correction (template §7 item 5) ────────────
# This S1 CSV is missing one short Line connecting the spline's free end
# (Y≈8.591, Z≈5.084) to Line11's free end (Y≈13.0, Z≈5.084). With it
# missing we observe 4 free endpoints (2 on-axis at Z=4.008, plus the 2
# unconnected ends at Z=5.084) and the open-chain walker would refuse to
# proceed. Z values match exactly, so the bridge is a clean horizontal
# segment in the (Y, Z) plane.
#
# Selection criteria:
#   1. Both endpoints share a V coordinate within BRIDGE_V_TOL.
#   2. NEITHER endpoint sits on the revolve axis (those endpoints are
#      closed by the revolve itself and must remain free in the profile
#      wire — bridging them would create a degenerate edge on the axis).
#   3. The resulting chain walks all primitives exactly once.
bridge_inserted = None
free_eps = _find_free_endpoints(named_edges)
if len(free_eps) > 2:
    print(f"     ⚠  CSV has {len(free_eps)} free endpoints (expected 2). "
          f"Trialling bridge pairs ...")
    pair_candidates = []
    for i in range(len(free_eps)):
        for j in range(i + 1, len(free_eps)):
            p, q = free_eps[i], free_eps[j]
            if abs(p[1] - q[1]) >= BRIDGE_V_TOL:
                continue
            if _is_on_axis(p) or _is_on_axis(q):
                print(f"       skip ({p[0]:.3f},{p[1]:.3f}) → "
                      f"({q[0]:.3f},{q[1]:.3f}) : at least one endpoint "
                      f"is on the revolve axis")
                continue
            pair_candidates.append((p, q))
    if not pair_candidates:
        sys.exit(
            f"❌ G1: no off-axis pair of free endpoints shares a V coord "
            f"within {BRIDGE_V_TOL} mm: {free_eps}"
        )

    successful = []
    for (p, q) in pair_candidates:
        trial = list(named_edges) + [{
            "name": "TrialBridge", "start": p, "end": q,
            "build": (lambda p=p, q=q: (
                lambda rev: make_line_edge(q, p, S1_AXIS, S1_PLANE)
                           if rev else make_line_edge(p, q, S1_AXIS, S1_PLANE)
            ))(),
        }]
        try:
            oe, su, eu = walk_open_chain(trial)
        except ValueError as exc:
            print(f"       reject ({p[0]:.3f},{p[1]:.3f}) → "
                  f"({q[0]:.3f},{q[1]:.3f}) : {exc}")
            continue
        if len(oe) != len(trial):
            print(f"       reject ({p[0]:.3f},{p[1]:.3f}) → "
                  f"({q[0]:.3f},{q[1]:.3f}) : walker visited {len(oe)} "
                  f"of {len(trial)} edges")
            continue
        print(f"       accept ({p[0]:.3f},{p[1]:.3f}) → "
              f"({q[0]:.3f},{q[1]:.3f}) : walker visited all "
              f"{len(oe)} edges")
        successful.append(((p, q), oe, su, eu))

    if not successful:
        sys.exit(
            f"❌ G1: no candidate bridge produced a complete walker chain. "
            f"Off-axis free endpoints: "
            f"{[ep for ep in free_eps if not _is_on_axis(ep)]}"
        )
    if len(successful) > 1:
        # Shouldn't happen for these parts, but: prefer the shortest.
        successful.sort(key=lambda s: abs(s[0][0][0] - s[0][1][0]))
        print(f"     ⚠  {len(successful)} bridges produced valid walks; "
              f"picking shortest.")
    chosen_pair, _, _, _ = successful[0]
    bp, bq = chosen_pair
    print(f"     Chosen bridge: ({bp[0]:.3f},{bp[1]:.3f}) → "
          f"({bq[0]:.3f},{bq[1]:.3f})  length={abs(bp[0]-bq[0]):.3f} mm")
    bridge_inserted = (bp, bq)
    named_edges.append({
        "name": "BridgeLine",
        "start": bp, "end": bq,
        "build": (lambda bp=bp, bq=bq: (
            lambda rev: make_line_edge(bq, bp, S1_AXIS, S1_PLANE)
                       if rev else make_line_edge(bp, bq, S1_AXIS, S1_PLANE)
        ))(),
    })

ordered_edges, start_uv, end_uv = walk_open_chain(named_edges)
print(f"     Chain ordered: {len(ordered_edges)} edges")
print(f"     Free endpoint 1 (in-plane u,v): "
      f"({start_uv[0]:.3f}, {start_uv[1]:.3f})")
print(f"     Free endpoint 2 (in-plane u,v): "
      f"({end_uv[0]:.3f}, {end_uv[1]:.3f})")

# Spec check: the two free endpoints must correspond to Step 1 (the first
# row of S1, a 3-point arc) and Step 14 (the last row, a Line). Read
# those rows directly out of S1 and confirm one of their (u,v) endpoints
# matches each free end.
step1_row  = s1_rows[0]
step14_row = s1_rows[-1]
if _norm_draw_type(step1_row["Draw Type"]) != "3_point_arc":
    sys.exit(f"❌ G1: Step 1 row is not a 3-point arc: {step1_row['Draw Type']}")
if _norm_draw_type(step14_row["Draw Type"]) != "line":
    sys.exit(f"❌ G1: Step 14 row is not a Line: {step14_row['Draw Type']}")

step1_endpoints  = (in_plane_uv(step1_row,  1, S1_AXIS),
                    in_plane_uv(step1_row,  3, S1_AXIS))
step14_endpoints = (in_plane_uv(step14_row, 1, S1_AXIS),
                    in_plane_uv(step14_row, 2, S1_AXIS))

def _owner_of(free_pt):
    """Return 'Step1' or 'Step14' if free_pt matches one of their endpoints."""
    fk = _kep(free_pt)
    for ep in step1_endpoints:
        if _kep(ep) == fk:
            return "Step1 (3pt arc)"
    for ep in step14_endpoints:
        if _kep(ep) == fk:
            return "Step14 (Line)"
    return None

owner_start = _owner_of(start_uv)
owner_end   = _owner_of(end_uv)
print(f"       free 1 owner : {owner_start}")
print(f"       free 2 owner : {owner_end}")
if owner_start is None or owner_end is None or owner_start == owner_end:
    sys.exit(
        f"❌ G1: free endpoints must come from Step 1 (arc) and Step 14 "
        f"(line). Got owners: {owner_start}, {owner_end}"
    )

profile_wire = Wire(ordered_edges)
print(f"     Profile wire length: {profile_wire.length:.3f} mm  "
      f"(closed={profile_wire.is_closed})")

# A profile wire has no surface area on its own. Show it as construction.
checkpoint(1, f"G1 S1 profile wire (open, {len(ordered_edges)} edges) on "
              f"{S1_AXIS.upper()}={S1_PLANE}"
              + (" [+1 programmatic bridge]" if bridge_inserted else ""),
           profile_wire)


# ══════════════════════════════════════════════════════════════════════════
# G2 — Read S2: 1 line construction axis on X = 3.848.
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G2] Reading {S_CSV[2].name}")
s2_rows = read_rows(S_CSV[2])
_pinfo2 = detect_sketch_plane(s2_rows)
if _pinfo2[0] != "axis":
    sys.exit(f"❌ G2: S2 not axis-aligned.")
_, S2_AXIS, S2_PLANE = _pinfo2
print(f"     S2 plane: {S2_AXIS.upper()} = {S2_PLANE}")

s2_lines = parse_line_segments(s2_rows, S2_AXIS)
if len(s2_lines) != 1:
    sys.exit(f"❌ G2: expected 1 axis line in S2, got {len(s2_lines)}.")

(a, b) = s2_lines[0]
print(f"     S2 axis: ({a[0]:.3f},{a[1]:.3f}) → ({b[0]:.3f},{b[1]:.3f})")

# Snap any near-constant in-plane component to its mean so the revolve
# axis is perfectly axis-aligned (defends against the few-micron Fusion
# wobble seen in source CSVs).
u_const = abs(a[0] - b[0]) < AXIS_SNAP_MM
v_const = abs(a[1] - b[1]) < AXIS_SNAP_MM
if u_const and not v_const:
    u_snap = 0.5 * (a[0] + b[0])
    a_snap = (u_snap, a[1])
    b_snap = (u_snap, b[1])
    print(f"     Snapped axis U-coord to constant {u_snap:.4f}")
elif v_const and not u_const:
    v_snap = 0.5 * (a[1] + b[1])
    a_snap = (a[0], v_snap)
    b_snap = (b[0], v_snap)
    print(f"     Snapped axis V-coord to constant {v_snap:.4f}")
else:
    a_snap, b_snap = a, b
    print(f"     Axis kept as-is (neither component constant within "
          f"{AXIS_SNAP_MM} mm)")

axis_p1 = world_vec_axis(a_snap, S2_AXIS, S2_PLANE)
axis_p2 = world_vec_axis(b_snap, S2_AXIS, S2_PLANE)
print(f"     World axis endpoints: "
      f"({axis_p1.X:.3f},{axis_p1.Y:.3f},{axis_p1.Z:.3f}) → "
      f"({axis_p2.X:.3f},{axis_p2.Y:.3f},{axis_p2.Z:.3f})")

# Edge used for visualization only; the revolve uses an Axis object.
axis_edge_construction = Edge.make_line(axis_p1, axis_p2)
axis_dir = axis_p2 - axis_p1
revolve_axis = Axis(origin=axis_p1, direction=axis_dir)
print(f"     Revolve axis direction: "
      f"({axis_dir.X:.4f}, {axis_dir.Y:.4f}, {axis_dir.Z:.4f})")

checkpoint(2, "G2 S2 construction axis line",
           axis_edge_construction)


# ══════════════════════════════════════════════════════════════════════════
# G4 — Surface-revolve the G1 profile wire about the G2 axis line.
#       (G3 is the FINAL export step, run after G4.)
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G4] Revolving G1 profile about G2 axis (360°)")

# Surface of revolution from an OPEN 1-D profile.
#
# build123d.revolve() targets the solid/face path and silently returns an
# empty Compound when given an open Wire on its own, so we go through
# OCCT directly. BRepPrimAPI_MakeRevol on a TopoDS_Wire produces one Face
# per edge in the wire (a Shell), which is exactly the surface shell we
# want for this open shell.
from OCP.BRepPrimAPI import BRepPrimAPI_MakeRevol
from OCP.gp import gp_Ax1, gp_Pnt, gp_Dir
from OCP.TopAbs import TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS

_ax1 = gp_Ax1(
    gp_Pnt(axis_p1.X, axis_p1.Y, axis_p1.Z),
    gp_Dir(axis_dir.X, axis_dir.Y, axis_dir.Z),
)


def _revolve_collect_faces(shape):
    out = []
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        out.append(Face(TopoDS.Face_s(exp.Current())))
        exp.Next()
    return out


g4_faces = []
g4_via   = None

# Primary path: revolve the whole wire in one go (matches Fusion's semantics).
mk = BRepPrimAPI_MakeRevol(profile_wire.wrapped, _ax1, math.radians(360.0), True)
mk.Build()
if mk.IsDone():
    g4_faces = _revolve_collect_faces(mk.Shape())
    g4_via   = "BRepPrimAPI_MakeRevol(wire)"

# Fallback: revolve each edge separately, then merge the faces.
if not g4_faces:
    print(f"     Whole-wire revolve produced 0 faces; falling back to "
          f"per-edge revolve")
    per_edge = []
    for i, e in enumerate(ordered_edges, 1):
        mk = BRepPrimAPI_MakeRevol(e.wrapped, _ax1, math.radians(360.0), True)
        mk.Build()
        if not mk.IsDone():
            sys.exit(f"❌ G4: per-edge revolve failed at edge {i}.")
        per_edge.extend(_revolve_collect_faces(mk.Shape()))
    g4_faces = per_edge
    g4_via   = "BRepPrimAPI_MakeRevol(edge×N)"

# Last-chance fallback: try build123d's wrapper too (rarely useful here).
if not g4_faces:
    print(f"     Per-edge revolve also empty; trying build123d.revolve()")
    try:
        revolved = revolve(profile_wire, axis=revolve_axis,
                           revolution_arc=360.0)
        g4_faces = list(revolved.faces())
        g4_via   = "build123d.revolve()"
    except Exception as exc:
        print(f"     build123d.revolve() failed: {exc}")

if not g4_faces:
    sys.exit("❌ G4: all revolve paths produced 0 faces.")

g4_total_area = sum(f.area for f in g4_faces)
print(f"     G4 produced {len(g4_faces)} face(s) via {g4_via}, "
      f"total area = {g4_total_area:.3f} mm²")
for i, f in enumerate(g4_faces, 1):
    print(f"       face {i}: area={f.area:.3f} mm²  geom={f.geom_type}")

# The construction-only axis edge contributes no surface area; remove it
# from stage_pieces so the final compound is just the revolved surface.
stage_pieces[:] = [p for p in stage_pieces if p is not axis_edge_construction
                                              and p is not profile_wire]

checkpoint(4, f"G4 revolve of profile about axis (360°) — "
              f"{len(g4_faces)} face(s)",
           *g4_faces)


# ══════════════════════════════════════════════════════════════════════════
# G3 — FINAL EXPORT (always last)
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G3] Final export")
final_compound = Compound(children=list(stage_pieces))
try:
    final_compound = final_compound.clean()
    print("     .clean() applied successfully")
except Exception as exc:
    print(f"     ⚠  .clean() failed: {exc}")

total_surface_area = sum(f.area for f in final_compound.faces())
n_edges = len(final_compound.edges())
print(f"     Total surface area : {total_surface_area:.3f} mm²")
print(f"     Edge count         : {n_edges}")

FINAL_STL  = BASE_DIR / f"{FOLDER_NAME}_{GUIDELINE_RANGE}.stl"
FINAL_STEP = BASE_DIR / f"{FOLDER_NAME}_{GUIDELINE_RANGE}.step"
FINAL_TXT  = BASE_DIR / f"{FOLDER_NAME}_summary_{GUIDELINE_RANGE}.txt"

try:
    export_stl(final_compound, str(FINAL_STL), tolerance=STL_TOLERANCE)
    print(f"     [EXPORT] Wrote: {FINAL_STL.name}")
except Exception as exc:
    print(f"     [EXPORT] STL failed: {exc}")
try:
    export_step(final_compound, str(FINAL_STEP))
    print(f"     [EXPORT] Wrote: {FINAL_STEP.name}")
except Exception as exc:
    print(f"     [EXPORT] STEP failed: {exc}")


# ── Summary file ──────────────────────────────────────────────────────────
summary_lines = [
    "=" * 70,
    f"BUILD SUMMARY  :  {FOLDER_NAME}",
    f"Time           :  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    f"Range covered  :  {GUIDELINE_RANGE}",
    f"Guidelines     :  G1, G2, G4  (G3 = export, last)",
    "=" * 70, "",
    f"-- G1 : S1 — open profile wire on {S1_AXIS.upper()}={S1_PLANE} --",
    f"  Primitives    : {len(s1_lines)} lines + {len(s1_arcs)} arcs "
        f"+ {len(s1_splines)} spline(s)",
    f"  Bridge added  : {'yes — ' + repr(bridge_inserted) if bridge_inserted else 'no'}",
    f"  Chain edges   : {len(ordered_edges)}",
    f"  Free end 1    : ({start_uv[0]:.3f}, {start_uv[1]:.3f})  "
        f"[{owner_start}]",
    f"  Free end 2    : ({end_uv[0]:.3f}, {end_uv[1]:.3f})  "
        f"[{owner_end}]",
    f"  Wire length   : {profile_wire.length:.3f} mm  "
        f"(closed={profile_wire.is_closed})",
    "",
    f"-- G2 : S2 — construction axis line on {S2_AXIS.upper()}={S2_PLANE} --",
    f"  Axis endpoints (world):",
    f"    P1 : ({axis_p1.X:.3f}, {axis_p1.Y:.3f}, {axis_p1.Z:.3f})",
    f"    P2 : ({axis_p2.X:.3f}, {axis_p2.Y:.3f}, {axis_p2.Z:.3f})",
    f"  Direction     : ({axis_dir.X:.4f}, {axis_dir.Y:.4f}, {axis_dir.Z:.4f})",
    "",
    f"-- G4 : Surface revolve of G1 profile about G2 axis (360°) --",
    f"  Solver        : {g4_via}",
    f"  Faces         : {len(g4_faces)}",
    f"  Total area    : {g4_total_area:.3f} mm²",
    "",
    "-- G3 : Export --",
    f"  STL                : {FINAL_STL.name}",
    f"  STEP               : {FINAL_STEP.name}",
    f"  Total surface area : {total_surface_area:.3f} mm²",
    f"  Edge count         : {n_edges}",
    "", "=" * 70,
    "PER-GUIDELINE CUMULATIVE AREA HISTORY",
    "=" * 70,
    f"{'Guideline':>10}  {'Cumulative area (mm²)':>22}  {'Δ (mm²)':>12}  Label",
    "-" * 90,
]
for entry in area_history:
    summary_lines.append(
        f"  G{entry['g']:<8d}  {entry['area']:>22.3f}  "
        f"{entry['delta']:>+12.3f}  {entry['label']}"
    )
summary_lines.append("=" * 70)
with open(FINAL_TXT, "w") as f:
    f.write("\n".join(summary_lines))
print(f"     [EXPORT] Wrote: {FINAL_TXT.name}")
_write_area_history_summary()

print(f"\nDone -- G1, G2, G4 complete (G3 = export, last).")