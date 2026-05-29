"""
zaphod_bot_mec_de_man_out_printer_proto_bearing_link_3_build123d.py

Reference STL: https://github.com/<repo>/.../bearing_link_3.stl

SOLID part: a bearing link / cross-yoke built from the INTERSECTION of two
perpendicular extruded "link" profiles, pierced by two coaxial bearing
bores (one along Z, one along Y), with rounded outer edges and chamfered
bore mouths, finally UN-STITCHED into a surface body.

Sketch summary (planes auto-detected):

  S1  Z = 15.0   5 Lines + 3 three-point arcs forming a single CLOSED
                 "link" profile in the (X, Y) plane: a rectangular arm on
                 the left (X = -1 .. 11.72, Y = 4.55 .. 9.55) tangent into
                 a disc/eye on the right (centre (X,Y) ≈ (21.12, 7.05),
                 r ≈ 7.025).
  S2  Y = -2.0   7 Lines + 3 three-point arcs forming a CLOSED "link"
                 profile in the (X, Z) plane: a disc/eye on the left
                 (centre (X,Z) ≈ (7.025, 7.025), r ≈ 7.025) tangent into a
                 rectangular tab on the right (around X = 28 .. 29).
  S3  Z = 9.525  1 three-point circle in (X, Y), centre ≈ (21.12, 7.05),
                 r ≈ 5.525 — coaxial with the S1 disc → the Z bore.
  S4  Y = 9.55   1 three-point circle in (X, Z), centre ≈ (7.025, 7.025),
                 r ≈ 5.525 — coaxial with the S2 disc → the Y bore.
  S5  (3D)       16 three-point arcs that are NOT coplanar — they trace the
                 OUTER edges of the finished model in world space. Used only
                 to SELECT which solid edges to fillet (not a sketch plane).

Guidelines (G3 is the FINAL export step; geometry guidelines run
G1, G2, G4, G5, G6, G7 in that order):

  G1 – Read S1; build the CLOSED profile, extrude 16 units along -Z to a
       SOLID (Z = 15 .. -1).
  G2 – Read S2; build the CLOSED profile, extrude 23 units along +Y to a
       SOLID (Y = -2 .. 21), then INTERSECT with the G1 solid. The common
       body is the bearing-link blank.
  G4 – Read S3 and S4; build each circle, extrude it both ways along its own
       plane normal (overshooting the body) and CUT it from the blank to
       make two through holes (Z bore from S3, Y bore from S4).
  G5 – Read S5 (outer-edge reference); SELECT the body edges that lie on the
       S5 curves and FILLET them with radius 0.5.
  G6 – CHAMFER both bore mouths (each bore presents two rim edges where the
       cylindrical wall meets the body surface) with an equal-distance
       chamfer.
  G7 – UN-STITCH the solid into a surface body (its individual faces, no
       solid topology).
  G3 – LAST: compound + .clean() + STL / STEP / summary export.

Cross-platform:
  BASE_DIR derived from script location. No hardcoded paths.

Code-style reference: zaphod_bot_mec_de_man_out_printer_proto_homing_block
_build123d.py (helpers and conventions reused — CSV freshness logging, plane
auto-detection, closed-chain walker, checkpoint machinery and area tracking.
The GEOMETRY is different: this part is a boolean SOLID build — extrude /
intersect / cut / fillet / chamfer — that is only converted to a surface body
at the very end by un-stitching, whereas the reference was surface throughout.)
"""
import csv
import math
import re
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

# ══════════════════════════════════════════════════════════════════════════
# Tolerance / feature named constants
# ══════════════════════════════════════════════════════════════════════════
EPSILON_MM       = 1e-3   # endpoint matching, axis-aligned plane detection
SVD_PLANE_TOL    = 1e-2   # residual threshold for SVD plane fit
STL_TOLERANCE    = 5e-4   # export tolerance for STL

FILLET_RADIUS    = 0.5    # G5 fillet radius (units), per guideline
CHAMFER_MM       = 0.2    # G6 chamfer distance (equal distance). Per revised
                          # guideline: 0.2 units on both holes' edges, each hole
                          # having two cylinder edges. Change this one constant to
                          # re-size both bore chamfers.

# G5 edge selection: a body edge counts as an "outer edge" (i.e. lies on S5)
# when every sampled point along it is within this distance of the S5 curve
# cloud. The reconstructed body deviates from the extracted S5 reference by a
# few tenths of a mm, so this is deliberately looser than EPSILON_MM. There is
# a clean gap in the data (outer edges < ~0.7 mm, everything else > ~1.6 mm),
# so 1.0 mm separates them unambiguously.
FILLET_MATCH_TOL = 1.0
S5_SAMPLES       = 24     # points sampled along each S5 arc for the cloud
EDGE_SAMPLES     = 11     # points sampled along each body edge when matching

HOLE_RADIUS_TOL  = 0.10   # tolerance when recognising a bore rim by radius
HOLE_AXIS_TOL    = 0.20   # max perpendicular offset of a rim centre from axis
HOLE_CUT_LEN     = 60.0   # half-length of each through-cut tool (>> part size)


# ══════════════════════════════════════════════════════════════════════════
# Paths
# ══════════════════════════════════════════════════════════════════════════
BASE_DIR    = Path(__file__).resolve().parent
FOLDER_NAME = BASE_DIR.name
CSV_DIR     = BASE_DIR / "csv_merged"

# This part has S1..S5.
S_CSV = {n: CSV_DIR / f"Fusion_Coordinates_S{n}.csv" for n in range(1, 6)}

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
    Edge, Wire, Face, Shell, Solid, Compound,
    extrude, fillet, chamfer,
    export_stl, export_step,
    GeomType,
)
from ocp_vscode import show, set_port, reset_show
set_port(3939)


# ══════════════════════════════════════════════════════════════════════════
# VIEWER + EXPORT CHECKPOINT CONFIG
# Valid checkpoint numbers: 1, 2, 4, 5, 6, 7  (G3 is the final export step).
# Set VIEW_AT to None for a full G1..G7 run.
# ══════════════════════════════════════════════════════════════════════════
VIEW_AT              = 7
STOP_AFTER_VIEW      = True
EXPORT_AT_CHECKPOINT = True

GUIDELINE_RANGE = "G_1_7"


# ══════════════════════════════════════════════════════════════════════════
# CHECKPOINT / AREA-TRACKING MACHINERY
# ══════════════════════════════════════════════════════════════════════════
area_history = []        # list of {"g","label","area","delta"}
_LAST_SHAPE  = None      # most recent cumulative shape (for the viewer)


def shape_surface_area(shape):
    """Total surface area (mm²) of any solid / shell / compound of faces."""
    try:
        return float(sum(f.area for f in shape.faces()))
    except Exception:
        return 0.0


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
        f"{'Guideline':>10}  {'Cumulative area (mm²)':>22}  "
        f"{'Δ from prev (mm²)':>20}  Label",
        "-" * 96,
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


def write_checkpoint_export(g_num, label, shape):
    cp_range = f"G_1_{g_num}"
    cp_stl   = BASE_DIR / f"{FOLDER_NAME}_{cp_range}.stl"
    cp_step  = BASE_DIR / f"{FOLDER_NAME}_{cp_range}.step"
    cp_txt   = BASE_DIR / f"{FOLDER_NAME}_summary_{cp_range}.txt"
    try:
        try:
            shape = shape.clean()
        except Exception:
            pass
        export_stl(shape, str(cp_stl), tolerance=STL_TOLERANCE)
        export_step(shape, str(cp_step))
        print(f"     [CHECKPOINT] Wrote: {cp_stl.name}")
        print(f"     [CHECKPOINT] Wrote: {cp_step.name}")
    except Exception as exc:
        print(f"     [CHECKPOINT] Export failed: {exc}")
    lines = [
        "=" * 60,
        f"CHECKPOINT SUMMARY  :  {FOLDER_NAME}_summary_{cp_range}.txt",
        f"Time                :  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Guideline reached   :  G{g_num}  ({label})",
        f"Surface area        :  {shape_surface_area(shape):.3f} mm²",
        "=" * 60,
    ]
    with open(cp_txt, "w") as f:
        f.write("\n".join(lines))
    print(f"     [CHECKPOINT] Wrote: {cp_txt.name}")
    _write_area_history_summary(g_num)


def checkpoint(g_num, label, shape):
    """Record cumulative surface area after a guideline, optionally view/export.

    `shape` is the FULL cumulative state after Gn (a Solid for G1, G2, G4, G5,
    G6; the un-stitched Compound for G7). Surface area is reported throughout;
    deltas are negative for trims (cut / fillet / chamfer) and that is expected.
    """
    global _LAST_SHAPE
    _LAST_SHAPE = shape
    area = shape_surface_area(shape)
    delta = area - (area_history[-1]["area"] if area_history else 0.0)
    area_history.append({"g": g_num, "label": label, "area": area, "delta": delta})
    print(f"     [AREA] After G{g_num}: cumulative = {area:.3f} mm²  "
          f"(Δ = {delta:+.3f} mm²)")

    if VIEW_AT != g_num:
        return
    print(f"\n[VIEW] Cumulative state after G{g_num} ({label})")
    try: reset_show()
    except Exception: pass
    try:
        show(shape)
        print(f"       Sent shape to OCP viewer (port 3939)")
    except Exception as e:
        print(f"       OCP viewer call failed: {e}")
    if EXPORT_AT_CHECKPOINT:
        write_checkpoint_export(g_num, label, shape)
    if STOP_AFTER_VIEW:
        print(f"\n[VIEW] STOP_AFTER_VIEW=True — halting after G{g_num}.")
        _write_area_history_summary(g_num)
        sys.exit(0)


# ══════════════════════════════════════════════════════════════════════════
# CSV / GEOMETRY HELPERS  (ported from the reference script)
# ══════════════════════════════════════════════════════════════════════════
def read_rows(csv_path):
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
    triples = []
    for i in _row_present_indices(row):
        triples.append((
            float(row[f"X{i}"]),
            float(row[f"Y{i}"]),
            float(row[f"Z{i}"]),
        ))
    return triples


def _collect_all_points(rows):
    pts = []
    for r in rows:
        pts.extend(_row_all_xyz_triples(r))
    return np.array(pts)


def detect_sketch_plane(rows, tol_axis=EPSILON_MM, tol_plane=SVD_PLANE_TOL):
    """Axis-aligned detection first; SVD fallback for tilted sketches.

    Returns ("axis", axis_letter, plane_value) or
            ("general", origin_tuple, normal_tuple).
    Raises ValueError if the points are not coplanar at all (e.g. S5, which is
    a genuine 3-D edge set rather than a single sketch).
    """
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


def world_vec(row, idx):
    """World-space Vector of the i-th coordinate triple of a CSV row."""
    return Vector(float(row[f"X{idx}"]),
                  float(row[f"Y{idx}"]),
                  float(row[f"Z{idx}"]))


def axis_normal(axis):
    if   axis == "z": return Vector(0, 0, 1)
    elif axis == "y": return Vector(0, 1, 0)
    else:             return Vector(1, 0, 0)


def in_plane_uv(row, idx, axis):
    """Project the i-th coord triple of a CSV row to its in-plane (u, v)."""
    x = float(row[f"X{idx}"]); y = float(row[f"Y{idx}"]); z = float(row[f"Z{idx}"])
    if   axis == "z": return (x, y)
    elif axis == "y": return (x, z)
    else:             return (y, z)


def parse_line_segments(rows, axis):
    segs = []
    for r in rows:
        if not _norm_draw_type(r["Draw Type"]).startswith("line"):
            continue
        segs.append((in_plane_uv(r, 1, axis), in_plane_uv(r, 2, axis)))
    return segs


def parse_three_point_arcs(rows, axis):
    arcs = []
    for r in rows:
        if not _norm_draw_type(r["Draw Type"]).startswith("3_point_arc"):
            continue
        arcs.append((in_plane_uv(r, 1, axis),
                     in_plane_uv(r, 2, axis),
                     in_plane_uv(r, 3, axis)))
    return arcs


def parse_three_point_circles(rows):
    """Return list of (P1, P2, P3) WORLD-space Vector triples for every
    3_point_circle row (three points lying on the circle)."""
    circ = []
    for r in rows:
        if not _norm_draw_type(r["Draw Type"]).startswith("3_point_circle"):
            continue
        circ.append((world_vec(r, 1), world_vec(r, 2), world_vec(r, 3)))
    return circ


def make_line_edge(p_uv, q_uv, axis, plane_value):
    return Edge.make_line(_lift(p_uv, axis, plane_value),
                          _lift(q_uv, axis, plane_value))


def make_3pt_arc_edge(s_uv, m_uv, e_uv, axis, plane_value):
    return Edge.make_three_point_arc(_lift(s_uv, axis, plane_value),
                                     _lift(m_uv, axis, plane_value),
                                     _lift(e_uv, axis, plane_value))


def _lift(uv, axis, plane_value):
    """Lift an in-plane (u, v) back to a world Vector on the axis plane."""
    u, v = uv
    if   axis == "z": return Vector(u, v, plane_value)
    elif axis == "y": return Vector(u, plane_value, v)
    else:             return Vector(plane_value, u, v)


def _kep(p, tol=1e-2):
    return (round(p[0] / tol) * tol, round(p[1] / tol) * tol)


def walk_closed_chain(edges_named):
    """Closed-loop chain walker. Each entry is a dict with keys
    name / start / end / build(reverse)->Edge. Walks them into a connected
    CLOSED chain (every endpoint key shared by exactly two primitives).
    Returns (ordered_edges, loop_start_uv)."""
    from collections import defaultdict
    touch = defaultdict(list)
    for i, e in enumerate(edges_named):
        touch[_kep(e["start"])].append(i)
        touch[_kep(e["end"])].append(i)

    free = [k for k, idxs in touch.items() if len(idxs) == 1]
    if free:
        raise ValueError(f"Closed-chain walker: {len(free)} free endpoint(s): {free}")
    bad = [k for k, idxs in touch.items() if len(idxs) != 2]
    if bad:
        raise ValueError(f"Closed-chain walker: endpoints without exactly 2 "
                         f"neighbours: {bad}")

    used = [False] * len(edges_named)
    first = edges_named[0]
    start_key = _kep(first["start"])
    start_ep  = first["start"]
    ordered = [first["build"](False)]
    used[0] = True
    cur_key = _kep(first["end"])
    for _ in range(len(edges_named) - 1):
        cands = [i for i in touch[cur_key] if not used[i]]
        if not cands:
            raise ValueError(f"Chain broke at {cur_key}: no unused neighbour.")
        i = cands[0]
        e = edges_named[i]
        reverse = _kep(e["start"]) != cur_key
        ordered.append(e["build"](reverse))
        used[i] = True
        cur_key = _kep(e["start"]) if reverse else _kep(e["end"])
    if cur_key != start_key:
        raise ValueError(f"Closed chain didn't return to start {start_key}; "
                         f"ended at {cur_key}.")
    return ordered, start_ep


def build_closed_profile_face(rows, axis, plane_value):
    """Read line + 3-point-arc rows of one axis-aligned sketch, walk them into
    a closed wire, and return (Face, Wire, n_lines, n_arcs)."""
    lines = parse_line_segments(rows, axis)
    arcs  = parse_three_point_arcs(rows, axis)
    named = []
    for i, (a, b) in enumerate(lines, 1):
        named.append({
            "name": f"Line{i}", "start": a, "end": b,
            "build": (lambda a=a, b=b: (
                lambda rev: make_line_edge(b, a, axis, plane_value) if rev
                            else make_line_edge(a, b, axis, plane_value)))(),
        })
    for i, (a, m, b) in enumerate(arcs, 1):
        named.append({
            "name": f"Arc{i}", "start": a, "end": b,
            "build": (lambda a=a, m=m, b=b: (
                lambda rev: make_3pt_arc_edge(b, m, a, axis, plane_value) if rev
                            else make_3pt_arc_edge(a, m, b, axis, plane_value)))(),
        })
    ordered, _ = walk_closed_chain(named)
    wire = Wire(ordered)
    if not wire.is_closed:
        # Fall back to build123d's own edge sorting before giving up.
        wire = Wire([e for e in (named_e["build"](False) for named_e in named)])
    return Face(wire), wire, len(lines), len(arcs)


def circle_from_3_world(p1, p2, p3):
    """Circumcircle of three COPLANAR world points.
    Returns (centre Vector, radius float, unit-normal Vector)."""
    a = np.array(tuple(p1)); b = np.array(tuple(p2)); c = np.array(tuple(p3))
    n = np.cross(b - a, c - a)
    nn = np.linalg.norm(n)
    if nn < 1e-12:
        raise ValueError("Three circle points are collinear.")
    n = n / nn
    A = np.array([b - a, c - a, n])
    rhs = np.array([np.dot(b - a, (a + b) / 2.0),
                    np.dot(c - a, (a + c) / 2.0),
                    np.dot(n, a)])
    centre = np.linalg.solve(A, rhs)
    radius = float(np.linalg.norm(centre - a))
    return Vector(*centre), radius, Vector(*n)


def circle_face_from_rows(rows):
    """Build a planar circular Face from a single 3_point_circle CSV row.
    Returns (Face, centre Vector, radius float, normal Vector)."""
    circles = parse_three_point_circles(rows)
    if len(circles) != 1:
        raise ValueError(f"Expected exactly 1 circle, got {len(circles)}.")
    p1, p2, p3 = circles[0]
    centre, radius, normal = circle_from_3_world(p1, p2, p3)
    edge = Edge.make_circle(radius, Plane(origin=centre, z_dir=normal))
    return Face(Wire([edge])), centre, radius, normal


# ── S5 outer-edge matching helpers ─────────────────────────────────────────
def s5_point_cloud(rows, n=S5_SAMPLES):
    """Sample every S5 3-point arc into world points. Returns (Nx3 array,
    list of (P1,P2,P3) world triples)."""
    cloud, arcs = [], []
    for r in rows:
        if not _norm_draw_type(r["Draw Type"]).startswith("3_point_arc"):
            continue
        p1, p2, p3 = world_vec(r, 1), world_vec(r, 2), world_vec(r, 3)
        arcs.append((p1, p2, p3))
        e = Edge.make_three_point_arc(p1, p2, p3)
        cloud.extend(tuple(e.position_at(i / (n - 1))) for i in range(n))
    return np.array(cloud), arcs


def edge_max_dist_to_cloud(edge, cloud, m=EDGE_SAMPLES):
    """Largest distance from any sampled point on `edge` to the cloud."""
    try:
        pts = [np.array(tuple(edge.position_at(i / (m - 1)))) for i in range(m)]
    except Exception:
        return float("inf")
    return max(float(np.min(np.linalg.norm(cloud - p, axis=1))) for p in pts)


def select_outer_edges(solid, cloud, tol=FILLET_MATCH_TOL):
    """Body edges every sampled point of which lies within `tol` of the S5
    cloud — i.e. the edges that lie on the outer-edge reference."""
    return [e for e in solid.edges()
            if edge_max_dist_to_cloud(e, cloud) < tol]


def select_bore_edges(solid, centre, axis_dir, radius,
                      rtol=HOLE_RADIUS_TOL, atol=HOLE_AXIS_TOL):
    """Circular edges of ~`radius` whose centre lies on the bore axis line
    (through `centre` along `axis_dir`)."""
    axis_dir = axis_dir.normalized()
    out = []
    for e in solid.edges():
        try:
            if e.geom_type != GeomType.CIRCLE:
                continue
            if abs(e.radius - radius) > rtol:
                continue
            ac = e.arc_center
            d = Vector(ac.X - centre.X, ac.Y - centre.Y, ac.Z - centre.Z)
            perp = d - axis_dir * d.dot(axis_dir)
            if perp.length < atol:
                out.append(e)
        except Exception:
            continue
    return out


def safe_fillet(solid, edges, radius):
    """Fillet all edges at once; on OCCT failure, fall back to filleting them
    one at a time (re-selecting the surviving outer edges each pass) so a single
    bad edge cannot abort the whole operation."""
    if not edges:
        print("     ⚠  No edges to fillet.")
        return solid, 0
    try:
        out = fillet(edges, radius)
        return out, len(edges)
    except Exception as exc:
        print(f"     ⚠  Bulk fillet failed ({str(exc)[:70]}); going incremental.")
    cloud, _ = _S5_CLOUD_CACHE
    cur, done = solid, 0
    remaining = len(edges)
    for _ in range(remaining):
        cand = select_outer_edges(cur, cloud)
        if not cand:
            break
        try:
            cur = fillet([cand[0]], radius)
            done += 1
        except Exception:
            # Drop this stubborn edge by nudging the tolerance down a touch.
            cand = cand[1:]
            if not cand:
                break
            try:
                cur = fillet([cand[0]], radius)
                done += 1
            except Exception:
                break
    return cur, done


def safe_chamfer(solid, edges, length):
    """Chamfer all bore edges at once; fall back to per-edge on failure."""
    if not edges:
        print("     ⚠  No edges to chamfer.")
        return solid, 0
    try:
        return chamfer(edges, length), len(edges)
    except Exception as exc:
        print(f"     ⚠  Bulk chamfer failed ({str(exc)[:70]}); going per-edge.")
    cur, done = solid, 0
    for e in edges:
        try:
            cur = chamfer([e], length)
            done += 1
        except Exception:
            pass
    return cur, done


# ══════════════════════════════════════════════════════════════════════════
# G1 — Read S1: closed link profile on Z = 15.0, extrude 16 along -Z to SOLID.
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G1] Reading {S_CSV[1].name}")
s1_rows = read_rows(S_CSV[1])
_p1 = detect_sketch_plane(s1_rows)
if _p1[0] != "axis":
    sys.exit(f"❌ G1: S1 not axis-aligned (got {_p1[0]}).")
_, S1_AXIS, S1_PLANE = _p1
print(f"     S1 plane: {S1_AXIS.upper()} = {S1_PLANE}")

s1_face, s1_wire, s1_nl, s1_na = build_closed_profile_face(s1_rows, S1_AXIS, S1_PLANE)
print(f"     S1 primitives: {s1_nl} lines + {s1_na} arcs")
print(f"     S1 profile wire length: {s1_wire.length:.3f} mm  "
      f"(closed={s1_wire.is_closed}), face area={s1_face.area:.3f} mm²")
if not s1_wire.is_closed:
    sys.exit("❌ G1: S1 profile wire is not closed.")

EXTRUDE_Z = 16.0
g1_dir = -axis_normal(S1_AXIS)                  # -Z
g1_solid = extrude(s1_face, amount=EXTRUDE_Z, dir=g1_dir)
_bb = g1_solid.bounding_box()
print(f"     G1 solid: volume={g1_solid.volume:.3f} mm³, "
      f"extruded {EXTRUDE_Z} along {S1_AXIS.upper()}- "
      f"({S1_AXIS.upper()}={S1_PLANE}→{S1_PLANE - EXTRUDE_Z})")
checkpoint(1, f"G1 S1 profile extruded {EXTRUDE_Z} along -{S1_AXIS.upper()} "
              f"→ solid (vol {g1_solid.volume:.1f} mm³)",
           g1_solid)


# ══════════════════════════════════════════════════════════════════════════
# G2 — Read S2: closed link profile on Y = -2.0, extrude 23 along +Y to SOLID,
#       then INTERSECT with the G1 solid.
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G2] Reading {S_CSV[2].name}")
s2_rows = read_rows(S_CSV[2])
_p2 = detect_sketch_plane(s2_rows)
if _p2[0] != "axis":
    sys.exit(f"❌ G2: S2 not axis-aligned (got {_p2[0]}).")
_, S2_AXIS, S2_PLANE = _p2
print(f"     S2 plane: {S2_AXIS.upper()} = {S2_PLANE}")

s2_face, s2_wire, s2_nl, s2_na = build_closed_profile_face(s2_rows, S2_AXIS, S2_PLANE)
print(f"     S2 primitives: {s2_nl} lines + {s2_na} arcs")
print(f"     S2 profile wire length: {s2_wire.length:.3f} mm  "
      f"(closed={s2_wire.is_closed}), face area={s2_face.area:.3f} mm²")
if not s2_wire.is_closed:
    sys.exit("❌ G2: S2 profile wire is not closed.")

EXTRUDE_Y = 23.0
g2_dir = axis_normal(S2_AXIS)                   # +Y
g2_solid = extrude(s2_face, amount=EXTRUDE_Y, dir=g2_dir)
print(f"     G2 solid: volume={g2_solid.volume:.3f} mm³, "
      f"extruded {EXTRUDE_Y} along {S2_AXIS.upper()}+ "
      f"({S2_AXIS.upper()}={S2_PLANE}→{S2_PLANE + EXTRUDE_Y})")

body = g1_solid & g2_solid                      # boolean intersection
n_solids = len(body.solids())
print(f"     INTERSECT G1 ∩ G2: volume={body.volume:.3f} mm³, "
      f"{n_solids} solid(s)")
if n_solids != 1:
    print(f"     ⚠  Intersection produced {n_solids} solids (expected 1).")
checkpoint(2, f"G2 S2 profile extruded {EXTRUDE_Y} along +{S2_AXIS.upper()} "
              f"then intersected with G1 (vol {body.volume:.1f} mm³)",
           body)


# ══════════════════════════════════════════════════════════════════════════
# G4 — Read S3 and S4: build each circle, extrude through the body and CUT to
#       make two through holes (S3 → Z bore, S4 → Y bore).
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G4] Reading {S_CSV[3].name} and {S_CSV[4].name}")

s3_rows = read_rows(S_CSV[3])
s4_rows = read_rows(S_CSV[4])
_p3 = detect_sketch_plane(s3_rows)
_p4 = detect_sketch_plane(s4_rows)
print(f"     S3 plane: {('%s = %s' % (_p3[1].upper(), _p3[2])) if _p3[0]=='axis' else _p3}")
print(f"     S4 plane: {('%s = %s' % (_p4[1].upper(), _p4[2])) if _p4[0]=='axis' else _p4}")

s3_face, S3_C, S3_R, S3_N = circle_face_from_rows(s3_rows)
s4_face, S4_C, S4_N = None, None, None
s4_face, S4_C, S4_R, S4_N = circle_face_from_rows(s4_rows)
print(f"     S3 bore: centre=({S3_C.X:.3f},{S3_C.Y:.3f},{S3_C.Z:.3f}) "
      f"r={S3_R:.3f} axis={tuple(round(c,2) for c in tuple(S3_N))}")
print(f"     S4 bore: centre=({S4_C.X:.3f},{S4_C.Y:.3f},{S4_C.Z:.3f}) "
      f"r={S4_R:.3f} axis={tuple(round(c,2) for c in tuple(S4_N))}")

# Each cutting tool is the circle swept BOTH ways along its own plane normal,
# overshooting the body so the through hole is unambiguous.
tool_z = extrude(s3_face, amount=HOLE_CUT_LEN, both=True)
tool_y = extrude(s4_face, amount=HOLE_CUT_LEN, both=True)
body_holed = body - tool_z - tool_y
print(f"     After both through-cuts: volume={body_holed.volume:.3f} mm³, "
      f"{len(body_holed.solids())} solid(s)")
checkpoint(4, f"G4 two through bores cut (S3 r={S3_R:.2f} along Z, "
              f"S4 r={S4_R:.2f} along Y) — vol {body_holed.volume:.1f} mm³",
           body_holed)


# ══════════════════════════════════════════════════════════════════════════
# G5 — Read S5 (3-D outer-edge reference). Select the body edges lying on the
#       S5 curves and FILLET them with FILLET_RADIUS.
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G5] Reading {S_CSV[5].name} (outer-edge reference)")
s5_rows = read_rows(S_CSV[5])
try:
    _p5 = detect_sketch_plane(s5_rows)
    print(f"     S5 plane: {_p5[0]} (axis-aligned)")
except ValueError:
    print(f"     S5 is NOT coplanar — treated as a 3-D outer-edge reference.")

s5_cloud, s5_arcs = s5_point_cloud(s5_rows)
_S5_CLOUD_CACHE = (s5_cloud, s5_arcs)           # used by safe_fillet fallback
print(f"     S5 arcs: {len(s5_arcs)}  (cloud points: {len(s5_cloud)})")

outer_edges = select_outer_edges(body_holed, s5_cloud)
print(f"     Outer edges matched on body: {len(outer_edges)} "
      f"of {len(body_holed.edges())} total "
      f"(max-dist < {FILLET_MATCH_TOL} mm)")
for e in outer_edges:
    print(f"        {str(e.geom_type):18s} len={e.length:6.2f}  "
          f"max-dist={edge_max_dist_to_cloud(e, s5_cloud):.3f} mm")

body_filleted, n_fil = safe_fillet(body_holed, outer_edges, FILLET_RADIUS)
print(f"     Filleted {n_fil}/{len(outer_edges)} edge(s) at r={FILLET_RADIUS} — "
      f"volume={body_filleted.volume:.3f} mm³, {len(body_filleted.solids())} solid(s)")
checkpoint(5, f"G5 filleted {n_fil} outer edge(s) at r={FILLET_RADIUS} "
              f"(vol {body_filleted.volume:.1f} mm³)",
           body_filleted)


# ══════════════════════════════════════════════════════════════════════════
# G6 — Equal-distance CHAMFER on both bore mouths. Each bore presents two rim
#       edges (where the cylindrical wall meets the body surface); re-select
#       them on the post-fillet solid, then chamfer.
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G6] Chamfering bore mouths (equal distance = {CHAMFER_MM} mm)")
bore_z_edges = select_bore_edges(body_filleted, S3_C, S3_N, S3_R)
bore_y_edges = select_bore_edges(body_filleted, S4_C, S4_N, S4_R)
print(f"     Z-bore rim edges: {len(bore_z_edges)}, "
      f"Y-bore rim edges: {len(bore_y_edges)}")
all_bore_edges = bore_z_edges + bore_y_edges
body_chamf, n_ch = safe_chamfer(body_filleted, all_bore_edges, CHAMFER_MM)
print(f"     Chamfered {n_ch}/{len(all_bore_edges)} bore edge(s) — "
      f"volume={body_chamf.volume:.3f} mm³, {len(body_chamf.solids())} solid(s)")
checkpoint(6, f"G6 chamfered {n_ch} bore-mouth edge(s) at {CHAMFER_MM} mm "
              f"(vol {body_chamf.volume:.1f} mm³)",
           body_chamf)


# ══════════════════════════════════════════════════════════════════════════
# G7 — UN-STITCH the solid into a surface body (individual faces, no solid
#       topology). The exported part is now an open surface body.
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G7] Un-stitching solid into a surface body")
solid_volume_before_unstitch = float(body_chamf.volume)
unstitched_faces = list(body_chamf.faces())
surface_body = Compound(children=list(unstitched_faces))
print(f"     Un-stitched into {len(unstitched_faces)} face(s), "
      f"total area={shape_surface_area(surface_body):.3f} mm²  "
      f"(solid volume before un-stitch was {solid_volume_before_unstitch:.3f} mm³)")
checkpoint(7, f"G7 un-stitched solid → surface body of {len(unstitched_faces)} "
              f"face(s)",
           surface_body)


# ══════════════════════════════════════════════════════════════════════════
# G3 — FINAL EXPORT (always last)
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G3] Final export")
final_compound = Compound(children=list(unstitched_faces))
try:
    final_compound = final_compound.clean()
    print("     .clean() applied successfully")
except Exception as exc:
    print(f"     ⚠  .clean() failed: {exc}")

# Pre-export checks (surface part: area always; volume only if a closed solid).
all_faces = final_compound.faces()
total_surface_area = float(sum(f.area for f in all_faces))
n_edges = len(final_compound.edges())
print(f"     Total surface area : {total_surface_area:.3f} mm²")
print(f"     Face count         : {len(all_faces)}")
print(f"     Edge count         : {n_edges} (informational)")
try:
    solids = final_compound.solids()
    if solids:
        vol = sum(s.volume for s in solids)
        print(f"     Closed solid(s)    : {len(solids)}, volume={vol:.3f} mm³")
    else:
        print(f"     Surface part (open shell, un-stitched) — "
              f"watertightness/volume skipped")
except Exception:
    print(f"     Surface part (open shell, un-stitched) — "
          f"watertightness/volume skipped")

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


# ── Summary file ────────────────────────────────────────────────────────────
summary_lines = [
    "=" * 70,
    f"BUILD SUMMARY  :  {FOLDER_NAME}",
    f"Time           :  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    f"Range covered  :  {GUIDELINE_RANGE}",
    f"Guidelines     :  G1, G2, G4, G5, G6, G7  (G3 = export, last)",
    "=" * 70, "",
    f"-- G1 : S1 — closed link profile on {S1_AXIS.upper()}={S1_PLANE}, "
        f"extruded to SOLID --",
    f"  Primitives        : {s1_nl} lines + {s1_na} arcs",
    f"  Profile wire len  : {s1_wire.length:.3f} mm  (closed={s1_wire.is_closed})",
    f"  Extrusion         : {EXTRUDE_Z} mm along -{S1_AXIS.upper()} "
        f"({S1_AXIS.upper()}={S1_PLANE}→{S1_PLANE - EXTRUDE_Z})",
    f"  G1 solid volume   : {g1_solid.volume:.3f} mm³",
    "",
    f"-- G2 : S2 — closed link profile on {S2_AXIS.upper()}={S2_PLANE}, "
        f"extruded + intersected --",
    f"  Primitives        : {s2_nl} lines + {s2_na} arcs",
    f"  Profile wire len  : {s2_wire.length:.3f} mm  (closed={s2_wire.is_closed})",
    f"  Extrusion         : {EXTRUDE_Y} mm along +{S2_AXIS.upper()} "
        f"({S2_AXIS.upper()}={S2_PLANE}→{S2_PLANE + EXTRUDE_Y})",
    f"  G2 solid volume   : {g2_solid.volume:.3f} mm³",
    f"  Intersection      : {body.volume:.3f} mm³  ({len(body.solids())} solid)",
    "",
    f"-- G4 : Two through bores cut from S3 and S4 --",
    f"  Z bore (S3)       : centre=({S3_C.X:.3f},{S3_C.Y:.3f},{S3_C.Z:.3f}) "
        f"r={S3_R:.3f} mm",
    f"  Y bore (S4)       : centre=({S4_C.X:.3f},{S4_C.Y:.3f},{S4_C.Z:.3f}) "
        f"r={S4_R:.3f} mm",
    f"  Body after cuts   : {body_holed.volume:.3f} mm³",
    "",
    f"-- G5 : Fillet outer edges (S5 reference) --",
    f"  S5 arcs           : {len(s5_arcs)}  (3-D outer-edge reference)",
    f"  Edges matched     : {len(outer_edges)}  (max-dist < {FILLET_MATCH_TOL} mm)",
    f"  Edges filleted    : {n_fil} at r={FILLET_RADIUS} mm",
    f"  Body after fillet : {body_filleted.volume:.3f} mm³",
    "",
    f"-- G6 : Chamfer bore mouths --",
    f"  Z-bore rim edges  : {len(bore_z_edges)}",
    f"  Y-bore rim edges  : {len(bore_y_edges)}",
    f"  Edges chamfered   : {n_ch} at {CHAMFER_MM} mm (equal distance)",
    f"  Body after chamfer: {body_chamf.volume:.3f} mm³",
    "",
    f"-- G7 : Un-stitch to surface body --",
    f"  Faces             : {len(unstitched_faces)}",
    f"  Solid vol (pre)   : {solid_volume_before_unstitch:.3f} mm³",
    "",
    "-- G3 : Export --",
    f"  STL                : {FINAL_STL.name}",
    f"  STEP               : {FINAL_STEP.name}",
    f"  Total surface area : {total_surface_area:.3f} mm²",
    f"  Face count         : {len(all_faces)}",
    f"  Edge count         : {n_edges}",
    "", "=" * 70,
    "PER-GUIDELINE CUMULATIVE AREA HISTORY",
    "=" * 70,
    f"{'Guideline':>10}  {'Cumulative area (mm²)':>22}  {'Δ (mm²)':>12}  Label",
    "-" * 96,
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

print(f"\nDone -- G1, G2, G4, G5, G6, G7 complete (G3 = export, last).")