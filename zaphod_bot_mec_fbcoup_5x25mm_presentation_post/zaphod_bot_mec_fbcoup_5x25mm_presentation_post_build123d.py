"""
zaphod_bot_mec_fbcoup_5x25mm_presentation_post_build123d.py

Reference STL: https://github.com/Scottapotamas/zaphod-bot/blob/master/mechanical/fibre_couplers/manf_outputs/5x25mm_presentation_post.STL

Surface part (open shell, surface of revolution from a CLOSED profile).

Sketch summary (planes auto-detected; both axis-aligned to Z = 4.582):

  S1  Z = 4.582  8 Lines + 4 three-point arcs = 12 primitives forming a
                  single CLOSED (enclosed) profile in the (X, Y) plane.
                  Every endpoint has exactly two neighbours — zero free
                  endpoints — so the walker must traverse a closed loop,
                  not an open chain. Profile X-range ≈ 0.4..3.32,
                  Y-range 0.0..30.0 (the 25 mm length variant — 10 mm
                  longer than the 5x15mm post on the Y axis).
  S2  Z = 4.582  1 Line from (4.397, 30.0, 4.582) to (4.397, 27.038, 4.582)
                  — construction axis for the revolve (a Y-direction
                  line at X=4.397 inside the Z=4.582 plane). The axis
                  lies OUTSIDE the profile's X-range (~0.4..3.32), so
                  revolving the closed wire about it produces a torus-
                  topology shell (closed surface with a central hole).

Guidelines:

  G1 – Read S1; build the CLOSED profile wire (8 lines + 4 arcs = 12
       edges) on Z = 4.582. Walked as a closed loop.
  G2 – Read S2; build the construction axis line. No surface
       contribution — used by G4 only.
  G3 – LAST: compound + .clean() + STL/STEP/summary export.
  G4 – Surface-revolve the G1 profile wire about the G2 axis line →
       closed-shell surface of revolution.

Cross-platform:
  BASE_DIR derived from script location. No hardcoded paths.

Code-style reference: zaphod_bot_mec_fbcoup_5x15mm_presentation_post_build123d.py
(used for helpers and patterns only — geometry is the same TOPOLOGY
here as in the 5x15mm variant: profile is CLOSED, 8+4=12 primitives on
Z=4.582 with the axis on the same plane. Only the Y-extent of the
profile and the S2 axis-line endpoints differ — the post is 10 mm
longer along Y).
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
    """Plain DictReader read; OK for short rows (lines / arcs)."""
    with open(csv_path, "r") as f:
        return list(csv.DictReader(f))


def _is_missing(cell):
    if cell is None:
        return True
    s = cell.strip()
    return s == "" or s.upper() == "NA"


def _norm_draw_type(raw):
    return re.sub(r'_\d+$', '', raw.strip().lower()).rstrip('_')


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
    """Return ALL (x, y, z) float triples from a row (only the named X1..Z3
    columns — this part has no splines so no overflow handling needed)."""
    triples = []
    for i in _row_present_indices(row):
        triples.append((
            float(row[f"X{i}"]),
            float(row[f"Y{i}"]),
            float(row[f"Z{i}"]),
        ))
    return triples


def _collect_all_points(rows):
    """Pull every non-missing (Xi,Yi,Zi) triple out of the row, for plane
    detection. Lines contribute 2; arcs 3."""
    pts = []
    for r in rows:
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


def _kep(p, tol=1e-2):
    """Endpoint key for fuzzy matching (in-plane u, v)."""
    return (round(p[0] / tol) * tol, round(p[1] / tol) * tol)


def walk_closed_chain(edges_named):
    """
    Closed-loop variant of the chain walker. Given a list of
    (name, start_uv, end_uv, build_fn) entries — where each entry knows
    how to build its own oriented edge — walk them into a connected
    CLOSED chain (every endpoint key shared by exactly two primitives,
    so zero free endpoints).

    The starting primitive is edges_named[0] oriented as given; from
    there the loop is walked by following unused neighbours at each
    endpoint key until every primitive is consumed, and the final
    endpoint must equal the chosen start key.

    Returns a list of oriented edges in walk order, plus the chosen
    start key (as the ORIGINAL unrounded (u, v)) for logging.
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
    if len(free_keys) != 0:
        raise ValueError(
            f"Closed-chain walker expected zero free endpoints; "
            f"got {len(free_keys)}: {free_keys}"
        )
    bad_keys = [k for k, idxs in touch.items() if len(idxs) != 2]
    if bad_keys:
        raise ValueError(
            f"Closed-chain walker expected exactly 2 neighbours at every "
            f"endpoint; got bad keys: {bad_keys}"
        )

    # Start with edges_named[0] oriented as authored.
    used = [False] * len(edges_named)
    first = edges_named[0]
    start_key = _kep(first["start"])
    start_ep  = first["start"]  # unrounded

    ordered = [first["build"](False)]   # reverse=False: as authored
    used[0] = True
    cur_key = _kep(first["end"])

    for _ in range(len(edges_named) - 1):
        candidates = [i for i in touch[cur_key] if not used[i]]
        if not candidates:
            raise ValueError(f"Chain broke at {cur_key}: no unused neighbour.")
        i = candidates[0]
        e = edges_named[i]
        reverse = _kep(e["start"]) != cur_key
        ordered.append(e["build"](reverse))
        used[i] = True
        cur_key = _kep(e["start"]) if reverse else _kep(e["end"])

    if cur_key != start_key:
        raise ValueError(
            f"Closed chain didn't return to start {start_key}; "
            f"ended at {cur_key}."
        )
    return ordered, start_ep


# ══════════════════════════════════════════════════════════════════════════
# G1 — Read S1: 8 lines + 4 three-point arcs on Z = 4.582. Build the CLOSED
#       profile wire.
#
# Same topology as the 5x15mm variant: every endpoint has exactly two
# neighbours, so the chain walker is the closed-loop variant and there is
# no Step-1/Step-N free-endpoint ownership check.
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G1] Reading {S_CSV[1].name}")
s1_rows = read_rows(S_CSV[1])
_pinfo1 = detect_sketch_plane(s1_rows)
if _pinfo1[0] != "axis":
    sys.exit(f"❌ G1: S1 not axis-aligned.")
_, S1_AXIS, S1_PLANE = _pinfo1
print(f"     S1 plane: {S1_AXIS.upper()} = {S1_PLANE}")

s1_lines = parse_line_segments(s1_rows, S1_AXIS)
s1_arcs  = parse_three_point_arcs(s1_rows, S1_AXIS)
print(f"     S1 lines: {len(s1_lines)}, three-point arcs: {len(s1_arcs)}")

# Expected: 8 lines + 4 arcs = 12 primitives.
EXPECTED_LINES, EXPECTED_ARCS = 8, 4
if (len(s1_lines), len(s1_arcs)) != (EXPECTED_LINES, EXPECTED_ARCS):
    sys.exit(
        f"❌ G1: expected {EXPECTED_LINES} lines + {EXPECTED_ARCS} arcs "
        f"in S1, got {len(s1_lines)} + {len(s1_arcs)}."
    )

for i, (a, b) in enumerate(s1_lines, 1):
    print(f"     Line{i}: ({a[0]:.3f},{a[1]:.3f}) → ({b[0]:.3f},{b[1]:.3f})")
for i, (a, m, b) in enumerate(s1_arcs, 1):
    print(f"     Arc{i}: ({a[0]:.3f},{a[1]:.3f}) via ({m[0]:.3f},{m[1]:.3f}) "
          f"→ ({b[0]:.3f},{b[1]:.3f})")

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

ordered_edges, loop_start_uv = walk_closed_chain(named_edges)
print(f"     Closed chain ordered: {len(ordered_edges)} edges")
print(f"     Loop start (in-plane u,v): "
      f"({loop_start_uv[0]:.3f}, {loop_start_uv[1]:.3f})")

profile_wire = Wire(ordered_edges)
print(f"     Profile wire length: {profile_wire.length:.3f} mm  "
      f"(closed={profile_wire.is_closed})")
if not profile_wire.is_closed:
    sys.exit(
        "❌ G1: closed-chain walk completed but Wire.is_closed is False — "
        "endpoint snapping likely off (check EPSILON_MM / arc precision)."
    )

# A profile wire has no surface area on its own. Show it as construction.
checkpoint(1, f"G1 S1 closed profile wire ({len(ordered_edges)} edges) on "
              f"{S1_AXIS.upper()}={S1_PLANE}",
           profile_wire)


# ══════════════════════════════════════════════════════════════════════════
# G2 — Read S2: 1 line construction axis on Z = 4.582.
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
# G4 — Surface-revolve the G1 closed profile wire about the G2 axis line.
#       (G3 is the FINAL export step, run after G4.)
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G4] Revolving G1 closed profile about G2 axis (360°)")

# Surface of revolution from a CLOSED 1-D profile wire about an axis that
# lies OUTSIDE the profile's footprint.
#
# build123d.revolve() targets the solid/face path and silently returns an
# empty Compound when given a bare Wire, so we go through OCCT directly.
# BRepPrimAPI_MakeRevol on a TopoDS_Wire produces one Face per edge in
# the wire (a Shell). Because the profile is closed and the axis is
# external, the resulting shell has torus topology (a closed surface
# with a central hole).
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
# Same for the profile wire — it was a construction artefact for G4.
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
    f"-- G1 : S1 — CLOSED profile wire on {S1_AXIS.upper()}={S1_PLANE} --",
    f"  Primitives    : {len(s1_lines)} lines + {len(s1_arcs)} arcs",
    f"  Chain edges   : {len(ordered_edges)}",
    f"  Loop start    : ({loop_start_uv[0]:.3f}, {loop_start_uv[1]:.3f})",
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