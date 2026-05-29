"""
zaphod_bot_mec_de_man_out_printer_proto_homing_block_build123d.py

Reference STL: https://github.com/<repo>/.../homing_block.stl

Surface part (open shell): a tapered stadium-shaped wall with top and
bottom cap patches, each pierced by two circular holes, and two
cylindrical tube walls passing through those holes.

Sketch summary (planes auto-detected; both axis-aligned to Y = 1.0):

  S1  Y = 1.0   2 Lines + 2 three-point arcs = 4 primitives forming a
                single CLOSED "stadium" (discorectangle) profile in the
                (X, Z) plane.  Straight top/bottom segments at Z = 9 and
                Z = 0 span X = 4.5 .. 20.5; the two ends are semicircles
                of radius 4.5 centred at (X,Z) = (4.5, 4.5) and
                (20.5, 4.5).  Profile X-range 0 .. 25, Z-range 0 .. 9.
                Every endpoint has exactly two neighbours (zero free
                endpoints) so the walker traverses a closed loop.
  S2  Y = 1.0   2 three-point circles in the (X, Z) plane, each of
                radius 1.7, centred at (4.5, 4.5) and (20.5, 4.5) — i.e.
                concentric with the two stadium semicircle centres.
                These become the two cylindrical tube walls.

Guidelines (G3 is the FINAL export step; geometry guidelines run
G1, G2, G4, G5, G6 in that order):

  G1 – Read S1; build the CLOSED profile wire on Y = 1.0, then SURFACE-
       EXTRUDE its edges in two directions from that base plane:
         * 1 unit along -Y with ZERO taper  -> straight lower walls
           (Y = 1 .. 0).
         * 1 unit along +Y with a 45 deg taper drawn INWARD so the
           extruded profile gets SMALLER -> tapered upper walls
           (Y = 1 .. 2).  tan(45 deg) = 1, so the top profile is the
           base profile offset inward by 1 mm.
  G2 – Apply surface patches (cap faces) on the two open extruded
       profiles at Y = 0 (full stadium) and Y = 2 (shrunk stadium).
  G4 – Read S2; build the two circles, then surface-extrude their edges
       symmetrically to a TOTAL length of 4 units (Y = -1 .. 3),
       deliberately overshooting the Y = 0 .. 2 body so the tubes are
       easy to trim later.
  G5 – Trim the G2 cap patches (Y = 0 and Y = 2): remove the portions
       that lie INSIDE the G4 cylindrical walls -> two circular holes
       per cap.
  G6 – Trim the G4 cylindrical walls so they span only Y = 0 .. 2
       (discard the overshoot established in G4).
  G3 – LAST: compound + .clean() + STL/STEP/summary export.

Cross-platform:
  BASE_DIR derived from script location. No hardcoded paths.

Code-style reference: zaphod_bot_mec_fbcoup_5x25mm_presentation_post_build123d.py
(helpers and conventions reused — CSV freshness logging, plane
auto-detection, closed-chain walker, checkpoint machinery and area
tracking. The GEOMETRY is different: this part is built by surface
extrusion + capping + boolean trims, not by revolution.)
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
TRIM_PAD_MM     = 60.0   # half-extent of the Y-range trim box (>> part size)


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
    export_stl, export_step,
    GeomType,
)
from ocp_vscode import show, set_port, reset_show
set_port(3939)

# Direct OCCT access for the surface operations build123d does not expose
# cleanly on bare wires/edges.
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir, gp_Vec, gp_Circ
from OCP.BRepPrimAPI import (
    BRepPrimAPI_MakePrism, BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder,
)
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCP.BRepOffsetAPI import (
    BRepOffsetAPI_MakeOffset, BRepOffsetAPI_ThruSections,
)
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Common
from OCP.GeomAbs import GeomAbs_Arc
from OCP.TopAbs import TopAbs_FACE, TopAbs_WIRE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS


# ══════════════════════════════════════════════════════════════════════════
# VIEWER + EXPORT CHECKPOINT CONFIG
# Valid checkpoint numbers: 1, 2, 4, 5, 6  (G3 is the final export step).
# Set VIEW_AT to None for a full G1..G6 run.
# ══════════════════════════════════════════════════════════════════════════
VIEW_AT                 = 6
STOP_AFTER_VIEW         = True
EXPORT_AT_CHECKPOINT    = True

GUIDELINE_RANGE = "G_1_6"


# ══════════════════════════════════════════════════════════════════════════
# CHECKPOINT MACHINERY
# ══════════════════════════════════════════════════════════════════════════
stage_pieces = []
area_history = []


def faces_of(topods_shape):
    """Collect every TopoDS_Face inside an OCCT shape as build123d Faces."""
    out = []
    exp = TopExp_Explorer(topods_shape, TopAbs_FACE)
    while exp.More():
        out.append(Face(TopoDS.Face_s(exp.Current())))
        exp.Next()
    return out


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
    """Record cumulative surface area after a guideline.

    new_pieces are appended to stage_pieces. For guidelines that MODIFY
    or TRIM existing geometry, mutate stage_pieces[:] in place first and
    call this with no new_pieces — the cumulative area is recomputed over
    the current stage_pieces, so the delta correctly comes out negative.
    """
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
# CSV / GEOMETRY HELPERS  (reused from the reference script)
# ══════════════════════════════════════════════════════════════════════════
def read_rows(csv_path):
    """Plain DictReader read; OK for short rows (lines / arcs / circles)."""
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
    """Return ALL (x, y, z) float triples from a row (named X1..Z3 columns)."""
    triples = []
    for i in _row_present_indices(row):
        triples.append((
            float(row[f"X{i}"]),
            float(row[f"Y{i}"]),
            float(row[f"Z{i}"]),
        ))
    return triples


def _collect_all_points(rows):
    """Pull every non-missing (Xi,Yi,Zi) triple out of the rows, for plane
    detection. Lines contribute 2; arcs/circles contribute 3."""
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


def axis_normal(axis):
    """World-space unit normal of an axis-aligned sketch plane."""
    if   axis == "z": return Vector(0, 0, 1)
    elif axis == "y": return Vector(0, 1, 0)
    else:             return Vector(1, 0, 0)


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


def parse_three_point_circles(rows, axis):
    """Return list of (p1, p2, p3) in-plane (u,v) triples for every
    3_point_circle row (three points lying on the circle)."""
    circ = []
    for r in rows:
        if not _norm_draw_type(r["Draw Type"]).startswith("3_point_circle"):
            continue
        circ.append((
            in_plane_uv(r, 1, axis),
            in_plane_uv(r, 2, axis),
            in_plane_uv(r, 3, axis),
        ))
    return circ


def circle_from_3_points(p1, p2, p3):
    """Circumcircle of three in-plane (u,v) points -> ((cu,cv), radius)."""
    (ax, ay), (bx, by), (cx, cy) = p1, p2, p3
    d = 2.0 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-12:
        raise ValueError("Three circle points are collinear.")
    a2, b2, c2 = ax*ax + ay*ay, bx*bx + by*by, cx*cx + cy*cy
    cu = (a2 * (by - cy) + b2 * (cy - ay) + c2 * (ay - by)) / d
    cv = (a2 * (cx - bx) + b2 * (ax - cx) + c2 * (bx - ax)) / d
    r = math.hypot(ax - cu, ay - cv)
    return (cu, cv), r


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


def make_circle_edge(center_uv, radius, axis, plane_value):
    """Full-circle Edge centred at the in-plane point, lying on the
    axis-aligned sketch plane."""
    origin = world_vec_axis(center_uv, axis, plane_value)
    normal = axis_normal(axis)
    circ = gp_Circ(
        gp_Ax2(gp_Pnt(origin.X, origin.Y, origin.Z),
               gp_Dir(normal.X, normal.Y, normal.Z)),
        radius,
    )
    return Edge(BRepBuilderAPI_MakeEdge(circ).Edge())


def _kep(p, tol=1e-2):
    """Endpoint key for fuzzy matching (in-plane u, v)."""
    return (round(p[0] / tol) * tol, round(p[1] / tol) * tol)


def walk_closed_chain(edges_named):
    """
    Closed-loop chain walker. Given a list of (name, start_uv, end_uv,
    build_fn) entries — where each entry knows how to build its own
    oriented edge — walk them into a connected CLOSED chain (every
    endpoint key shared by exactly two primitives, so zero free
    endpoints).

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


def inward_offset_wire(wire, distance):
    """2-D in-plane offset of a closed planar wire by `distance`
    (negative shrinks). Returns the offset Wire."""
    mk = BRepOffsetAPI_MakeOffset(wire.wrapped, GeomAbs_Arc)
    mk.Perform(distance)
    exp = TopExp_Explorer(mk.Shape(), TopAbs_WIRE)
    if not exp.More():
        raise RuntimeError("Offset produced no wire.")
    return Wire(TopoDS.Wire_s(exp.Current()))


def surface_prism(wire_or_edge, vec):
    """Linear sweep (straight extrude) of a 1-D wire/edge into a SHELL of
    lateral faces — one face per edge, no caps. Returns list[Face]."""
    pr = BRepPrimAPI_MakePrism(wire_or_edge.wrapped, gp_Vec(vec.X, vec.Y, vec.Z))
    return faces_of(pr.Shape())


def ruled_loft_faces(wire_a, wire_b):
    """Ruled (straight-line) surface between two compatible closed wires —
    no end caps. Returns list[Face]. Used for the tapered upper walls."""
    ts = BRepOffsetAPI_ThruSections(False, True)   # isSolid=False, ruled=True
    ts.AddWire(wire_a.wrapped)
    ts.AddWire(wire_b.wrapped)
    ts.Build()
    return faces_of(ts.Shape())


def solid_cylinder_tool(center_uv, radius, axis, y_lo, y_hi):
    """Solid cylinder used purely as a boolean CUTTING tool (not part of
    the exported surface). Built tall enough to fully pierce the caps."""
    origin = world_vec_axis(center_uv, axis, y_lo)
    normal = axis_normal(axis)
    ax = gp_Ax2(gp_Pnt(origin.X, origin.Y, origin.Z),
                gp_Dir(normal.X, normal.Y, normal.Z))
    return BRepPrimAPI_MakeCylinder(ax, radius, (y_hi - y_lo)).Shape()


def cut_face_with_tools(face, tools):
    """Subtract solid tools from a face -> face(s) with holes. list[Face]."""
    shp = face.wrapped
    for t in tools:
        shp = BRepAlgoAPI_Cut(shp, t).Shape()
    return faces_of(shp)


def trim_faces_to_y(faces, y_lo, y_hi, pad=TRIM_PAD_MM):
    """Keep only the portion of each face inside the slab y_lo <= Y <= y_hi
    by intersecting with a large box. Returns list[Face]."""
    box = BRepPrimAPI_MakeBox(
        gp_Pnt(-pad, y_lo, -pad), gp_Pnt(pad, y_hi, pad)
    ).Shape()
    out = []
    for f in faces:
        common = BRepAlgoAPI_Common(f.wrapped, box).Shape()
        out.extend(faces_of(common))
    return out


# ══════════════════════════════════════════════════════════════════════════
# G1 — Read S1: 2 lines + 2 three-point arcs on Y = 1.0. Build the CLOSED
#       profile wire, then surface-extrude into lower (straight) + upper
#       (45° tapered, inward) walls.
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G1] Reading {S_CSV[1].name}")
s1_rows = read_rows(S_CSV[1])
_pinfo1 = detect_sketch_plane(s1_rows)
if _pinfo1[0] != "axis":
    sys.exit(f"❌ G1: S1 not axis-aligned (got {_pinfo1[0]}).")
_, S1_AXIS, S1_PLANE = _pinfo1
print(f"     S1 plane: {S1_AXIS.upper()} = {S1_PLANE}")

s1_lines = parse_line_segments(s1_rows, S1_AXIS)
s1_arcs  = parse_three_point_arcs(s1_rows, S1_AXIS)
print(f"     S1 lines: {len(s1_lines)}, three-point arcs: {len(s1_arcs)}")

EXPECTED_LINES, EXPECTED_ARCS = 2, 2
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
for i, (a, b) in enumerate(s1_lines, 1):
    named_edges.append({
        "name": f"Line{i}",
        "start": a, "end": b,
        "build": (lambda a=a, b=b: (
            lambda rev: make_line_edge(b, a, S1_AXIS, S1_PLANE)
                       if rev else make_line_edge(a, b, S1_AXIS, S1_PLANE)
        ))(),
    })
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

base_wire = Wire(ordered_edges)
print(f"     Base profile wire length: {base_wire.length:.3f} mm  "
      f"(closed={base_wire.is_closed})")
if not base_wire.is_closed:
    sys.exit(
        "❌ G1: closed-chain walk completed but Wire.is_closed is False — "
        "endpoint snapping likely off (check EPSILON_MM / arc precision)."
    )

# --- Surface extrude: lower (straight, -Y, 1 unit, zero taper) -------------
EXTRUDE_LEN = 1.0
n = axis_normal(S1_AXIS)
y_base = S1_PLANE
y_low  = y_base - EXTRUDE_LEN          # 0.0
y_high = y_base + EXTRUDE_LEN          # 2.0

lower_walls = surface_prism(base_wire, n * (-EXTRUDE_LEN))
print(f"     Lower walls (straight, {S1_AXIS.upper()}={y_base}→{y_low}): "
      f"{len(lower_walls)} face(s), area={sum(f.area for f in lower_walls):.3f} mm²")

# --- Surface extrude: upper (45° taper INWARD, +Y, 1 unit) -----------------
# tan(45°) = 1, so a 1-unit rise shrinks the profile by 1 mm in-plane.
TAPER_DEG = 45.0
inset = EXTRUDE_LEN * math.tan(math.radians(TAPER_DEG))   # = 1.0 mm
top_wire_inplane = inward_offset_wire(base_wire, -inset)  # negative = shrink
top_wire = top_wire_inplane.translate(n * EXTRUDE_LEN)    # lift to Y=2
print(f"     Top profile: base offset inward {inset:.3f} mm "
      f"(45° taper), length={top_wire.length:.3f} mm, "
      f"lifted to {S1_AXIS.upper()}={y_high}")

upper_walls = ruled_loft_faces(base_wire, top_wire)
print(f"     Upper walls (tapered, {S1_AXIS.upper()}={y_base}→{y_high}): "
      f"{len(upper_walls)} face(s), area={sum(f.area for f in upper_walls):.3f} mm²")

g1_faces = lower_walls + upper_walls
checkpoint(1, f"G1 surface-extruded walls — {len(lower_walls)} straight + "
              f"{len(upper_walls)} tapered face(s) on "
              f"{S1_AXIS.upper()}={y_low}..{y_high}",
           *g1_faces)


# ══════════════════════════════════════════════════════════════════════════
# G2 — Surface patches (cap faces) on the open profiles at Y = 0 and Y = 2.
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G2] Cap patches on the open profiles")

# Bottom profile (Y=0) is the base profile translated straight down by 1.
bottom_wire = base_wire.translate(n * (-EXTRUDE_LEN))
cap_bottom = Face(bottom_wire)
# Top profile (Y=2) is the already-built shrunk top_wire.
cap_top = Face(top_wire)
print(f"     Cap bottom ({S1_AXIS.upper()}={y_low}): area={cap_bottom.area:.3f} mm²")
print(f"     Cap top    ({S1_AXIS.upper()}={y_high}): area={cap_top.area:.3f} mm²")

checkpoint(2, f"G2 cap patches at {S1_AXIS.upper()}={y_low} and "
              f"{S1_AXIS.upper()}={y_high}",
           cap_bottom, cap_top)


# ══════════════════════════════════════════════════════════════════════════
# G4 — Read S2: 2 three-point circles on Y = 1.0. Surface-extrude the circle
#       edges symmetrically to a TOTAL length of 4 units (overshooting the
#       Y=0..2 body so they trim cleanly in G6).
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G4] Reading {S_CSV[2].name}")
s2_rows = read_rows(S_CSV[2])
_pinfo2 = detect_sketch_plane(s2_rows)
if _pinfo2[0] != "axis":
    sys.exit(f"❌ G4: S2 not axis-aligned (got {_pinfo2[0]}).")
_, S2_AXIS, S2_PLANE = _pinfo2
print(f"     S2 plane: {S2_AXIS.upper()} = {S2_PLANE}")
if S2_AXIS != S1_AXIS or abs(S2_PLANE - S1_PLANE) > EPSILON_MM:
    print(f"     ⚠  S2 plane differs from S1 — proceeding with S2's own plane.")

s2_circles_pts = parse_three_point_circles(s2_rows, S2_AXIS)
print(f"     S2 three-point circles: {len(s2_circles_pts)}")
EXPECTED_CIRCLES = 2
if len(s2_circles_pts) != EXPECTED_CIRCLES:
    sys.exit(f"❌ G4: expected {EXPECTED_CIRCLES} circles in S2, "
             f"got {len(s2_circles_pts)}.")

n2 = axis_normal(S2_AXIS)
CYL_TOTAL_LEN = 4.0
half = CYL_TOTAL_LEN / 2.0
cyl_y_lo = S2_PLANE - half     # -1.0
cyl_y_hi = S2_PLANE + half     #  3.0

circle_specs = []   # (center_uv, radius)
for i, (p1, p2, p3) in enumerate(s2_circles_pts, 1):
    center, radius = circle_from_3_points(p1, p2, p3)
    circle_specs.append((center, radius))
    print(f"     Circle{i}: center=({center[0]:.3f},{center[1]:.3f}) "
          f"r={radius:.3f} mm")

# Build the full-length tube walls (one cylindrical face per circle), placed
# at the lower extreme then swept the full 4 units along +normal.
cyl_walls_full = []
for i, (center, radius) in enumerate(circle_specs, 1):
    circ_edge_lo = make_circle_edge(center, radius, S2_AXIS, cyl_y_lo)
    wall = surface_prism(circ_edge_lo, n2 * CYL_TOTAL_LEN)
    cyl_walls_full.extend(wall)
    print(f"     Tube{i} wall (full, {S2_AXIS.upper()}={cyl_y_lo}..{cyl_y_hi}): "
          f"{len(wall)} face(s), area={sum(f.area for f in wall):.3f} mm²")

checkpoint(4, f"G4 cylindrical tube walls (full length {CYL_TOTAL_LEN}) — "
              f"{len(cyl_walls_full)} face(s) on "
              f"{S2_AXIS.upper()}={cyl_y_lo}..{cyl_y_hi}",
           *cyl_walls_full)


# ══════════════════════════════════════════════════════════════════════════
# G5 — Trim the G2 cap patches: remove the regions inside the G4 cylindrical
#       walls (two circular holes per cap).
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G5] Trimming cap holes inside the cylindrical walls")

# Solid cylinder tools (helpers only — never exported). Made taller than the
# caps so the Boolean cut is unambiguous.
tool_lo = min(y_low, cyl_y_lo) - 1.0
tool_hi = max(y_high, cyl_y_hi) + 1.0
cut_tools = [
    solid_cylinder_tool(center, radius, S2_AXIS, tool_lo, tool_hi)
    for (center, radius) in circle_specs
]

cap_bottom_holed = cut_face_with_tools(cap_bottom, cut_tools)
cap_top_holed    = cut_face_with_tools(cap_top,    cut_tools)
print(f"     Cap bottom: {len(cap_bottom_holed)} face(s) after cut, "
      f"area={sum(f.area for f in cap_bottom_holed):.3f} mm²")
print(f"     Cap top   : {len(cap_top_holed)} face(s) after cut, "
      f"area={sum(f.area for f in cap_top_holed):.3f} mm²")

# Swap the un-holed caps in stage_pieces for the holed versions (identity).
stage_pieces[:] = [p for p in stage_pieces
                   if p is not cap_bottom and p is not cap_top]
stage_pieces.extend(cap_bottom_holed)
stage_pieces.extend(cap_top_holed)
checkpoint(5, f"G5 trimmed cap holes inside {len(cut_tools)} tube footprints")


# ══════════════════════════════════════════════════════════════════════════
# G6 — Trim the G4 cylindrical walls to span only Y = 0 .. 2 (discard the
#       overshoot built in G4).
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G6] Trimming cylindrical walls to "
      f"{S2_AXIS.upper()}={y_low}..{y_high}")

cyl_walls_trimmed = trim_faces_to_y(cyl_walls_full, y_low, y_high)
print(f"     Tube walls: {len(cyl_walls_trimmed)} face(s) after trim, "
      f"area={sum(f.area for f in cyl_walls_trimmed):.3f} mm²")

# Swap full-length walls for the trimmed walls (identity match).
full_wall_ids = {id(f) for f in cyl_walls_full}
stage_pieces[:] = [p for p in stage_pieces if id(p) not in full_wall_ids]
stage_pieces.extend(cyl_walls_trimmed)
checkpoint(6, f"G6 trimmed tube walls to {S2_AXIS.upper()}={y_low}..{y_high} — "
              f"{len(cyl_walls_trimmed)} face(s)")


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

# Pre-export checks (surface part: area always; volume only if closed solid).
all_faces = final_compound.faces()
total_surface_area = sum(f.area for f in all_faces)
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
        print(f"     Surface part (open shell) — watertightness/volume skipped")
except Exception:
    print(f"     Surface part (open shell) — watertightness/volume skipped")

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
    f"Guidelines     :  G1, G2, G4, G5, G6  (G3 = export, last)",
    "=" * 70, "",
    f"-- G1 : S1 — CLOSED stadium profile + surface-extruded walls "
        f"on {S1_AXIS.upper()}={S1_PLANE} --",
    f"  Primitives        : {len(s1_lines)} lines + {len(s1_arcs)} arcs",
    f"  Base wire length  : {base_wire.length:.3f} mm  (closed={base_wire.is_closed})",
    f"  Lower walls       : straight extrude {S1_AXIS.upper()}={y_base}→{y_low}, "
        f"{len(lower_walls)} face(s)",
    f"  Upper walls       : {TAPER_DEG:.0f}° taper inward (inset {inset:.3f} mm), "
        f"{S1_AXIS.upper()}={y_base}→{y_high}, {len(upper_walls)} face(s)",
    "",
    f"-- G2 : Cap patches --",
    f"  Bottom cap        : {S1_AXIS.upper()}={y_low}, area {cap_bottom.area:.3f} mm²",
    f"  Top cap           : {S1_AXIS.upper()}={y_high}, area {cap_top.area:.3f} mm²",
    "",
    f"-- G4 : S2 — cylindrical tube walls on {S2_AXIS.upper()}={S2_PLANE} --",
    f"  Circles           : {len(circle_specs)}",
]
for i, (center, radius) in enumerate(circle_specs, 1):
    summary_lines.append(
        f"    Tube{i}           : center=({center[0]:.3f},{center[1]:.3f}) "
        f"r={radius:.3f} mm"
    )
summary_lines += [
    f"  Full sweep        : {S2_AXIS.upper()}={cyl_y_lo}..{cyl_y_hi} "
        f"(total {CYL_TOTAL_LEN} mm, symmetric)",
    "",
    f"-- G5 : Trim cap holes inside tube footprints --",
    f"  Bottom cap        : {len(cap_bottom_holed)} face(s), "
        f"area {sum(f.area for f in cap_bottom_holed):.3f} mm²",
    f"  Top cap           : {len(cap_top_holed)} face(s), "
        f"area {sum(f.area for f in cap_top_holed):.3f} mm²",
    "",
    f"-- G6 : Trim tube walls to {S2_AXIS.upper()}={y_low}..{y_high} --",
    f"  Trimmed walls     : {len(cyl_walls_trimmed)} face(s), "
        f"area {sum(f.area for f in cyl_walls_trimmed):.3f} mm²",
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

print(f"\nDone -- G1, G2, G4, G5, G6 complete (G3 = export, last).")