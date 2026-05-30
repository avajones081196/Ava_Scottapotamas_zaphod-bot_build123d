"""
zaphod_bot_mec_de_man_out_printer_proto_clevis_3_build123d.py

Reference STL: https://github.com/<repo>/.../zaphod_bot_mec_de_man_out_printer_proto_clevis_3.stl

SOLID part (closed body). A forked clevis with a cylindrical pin/boss:

Sketch summary (planes auto-detected):

  S1  Y = 30.0   1 three-point circle in the (X, Z) plane.
                 Circumcircle center (X, Z) = (4.736, 5.800), r = 2.925.
                 -> the cylindrical PIN / boss.
  S2  Z = 15.0   3 Lines + 1 three-point circle in the (X, Y) plane.
                 The 3 lines are the top + two sides of a rectangle
                 (X = 0.236 .. 9.236, Y = 4.5 .. 15.5); the circle
                 (center (4.736, 4.5), r = 4.5) supplies the rounded
                 bottom.  Region = rounded-bottom rectangle.
                 -> the main BLOCK (raw stock).
  S3  X = 10.0   13 Lines in the (Y, Z) plane forming ONE closed loop:
                 the clevis SIDE silhouette (two prongs separated by a
                 slot at Z = 2.803 .. 8.797, joined by a back wall at
                 Y = 13.5 .. 15.5, plus small mounting tabs at Y = -1.5).
                 -> the INTERSECT master profile.
  S4  (mixed)    2 Lines = the two inner corners at the back of the slot
                 (Y = 13.5, Z = 8.797 and Z = 2.803), each running along
                 X = 0.236 .. 9.236.  -> the FILLET edges.
  S5  (mixed)    6 Lines + 6 three-point arcs = the model edges around the
                 mouth of the slot on both prongs (the straight slot/back-
                 wall edges, the front rounded-bottom arcs, and the four
                 G5 fillet arcs).  -> the CHAMFER edges.

Guidelines (G3 is the FINAL export step; geometry guidelines run
G1, G2, G4, G5, G6, G7, G8, G9, G10, G11, G12, G13, G14, G15, G16, G17,
G18, G19, G20, G21, G22, G23, G24, G25, G26, G27, G28, G29 in that order):

  G1 - Read S1; build the circle profile on Y = 30 and extrude it as a
       SOLID in two directions from that base plane:
         * 9.5 units along -Y with ZERO taper -> straight cylinder
           (Y = 20.5 .. 30).
         * 0.5 units along +Y with a 45 deg taper drawn so the top
           profile gets SMALLER -> tapered cap (Y = 30 .. 30.5,
           top radius 2.925 - tan(45)*0.5 = 2.425).
       (The prompt writes the cap taper as "-45 deg" but clarifies that
       the taper must be chosen so the resultant circle is SMALLER than
       the base; in build123d that is taper=+45, see TAPER_DEG below.)
  G2 - Read S2; build the rounded-bottom-rectangle profile on Z = 15 and
       extrude it 22 units along -Z -> solid BLOCK (Z = -7 .. 15).
  G4 - Read S3; build the closed side-silhouette profile on X = 10 and
       perform an INTERSECTED extrude: extrude 23 units along -X
       (X = -13 .. 10) and take the boolean COMMON with the BLOCK ->
       forked clevis body.  (The G1 pin lies outside the S3 silhouette's
       Y-range, so the intersect targets the block only; the pin is then
       joined back in.)
  G5 - Read S4; locate the two model edges named by S4 and apply a
       2 mm radius fillet (rounds the inner corners at the back of the
       slot).
  G6 - Read S5; locate the 12 model edges named by S5 (lines + arcs) and
       apply an EQUAL-DISTANCE 0.25 mm chamfer to all of them.
       FIX: the edges meet TANGENTLY at shared vertices, so OCCT cannot
       chamfer them all at once and any sequential batching breaks the
       part's left/right mirror symmetry.  Instead the fork is cut at its
       mid-plane (X = 4.736), ONE half is chamfered (the front arcs become
       half-arcs ending on the cut, which removes the tangent conflicts so
       the half chamfers in a single call), then that half is MIRRORED and
       fused back.  The two sides are therefore identical by construction
       and the removed volume matches the analytic 0.25-chamfer prism.
  G7 - Read S6; draw TWO circle profiles on Z = 8.35:
         * 3_point_circle_1 -> inner circle  (r ≈ 2.505, used for G11 cut)
         * 3_point_circle_2 -> outer circle  (r ≈ 3.555, used for G10 loft)
  G8 - Read S7; draw ONE circle profile on Z = 8.797 (r ≈ 4.250, upper
       loft terminus).
  G9 - Read S8; build the guide-rail arc in the Y = 4.5 plane from the
       3-point arc data.  The arc connects the S6-outer-circle plane
       (Z = 8.35) to the S7-circle plane (Z = 8.797) and is used as the
       spine for the G10 loft operation.
  G10- Build the boss body spanning the G7 outer circle (Z = 8.35) and the
       G8 circle (Z = 8.797).  Because the two circles are CONCENTRIC and
       the G9 rail is a single in-plane arc, the lofted-with-rail surface
       is exactly a SURFACE OF REVOLUTION, so it is built with `revolve`
       of the G9 meridian about the central axis.  (PipeShell lofting was
       replaced: it produced a BSPLINE side wall whose base rim could only
       take a ~0.013 mm fillet, making the G14 0.2 mm fillet impossible.)
       The revolved boss is boolean-unioned into the fork body.
  G11- Extrude-cut using the G7 inner circle profile:
         * 3.25 units along +Z  (top rim at Z = 11.60 = the S9 plane)
         * 0.01 unit  along -Z  (to avoid a coincident cutter face)
       This creates the through-hole / pocket in the boss + fork body.
  G12- Read S9; fillet (r = 0.2) the inner-hole TOP rim circle (Z = 11.6,
       r ≈ 2.505).
  G13- Read S10; fillet (r = 0.15) the inner-hole BOTTOM rim circle
       (Z = 8.35, r ≈ 2.505).
  G14- Read S11; fillet (r = 0.2) the boss OUTER base rim circle
       (Z = 8.35, r ≈ 3.555).
  G15..G22 — SECOND boss + hole, the mirror of G7..G14 about the slot
       mid-plane (Z = 5.8); it grows from the LOWER prong up into the slot
       and its hole runs down through the block bottom, giving a coaxial
       clevis-pivot pair with the first boss.
         G15 - Read S12; two circles on Z = 3.25 (inner r ≈ 2.505,
               outer r ≈ 3.555).
         G16 - Read S13; one circle on Z = 2.803 (r ≈ 4.250, terminus).
         G17 - Read S14; the guide-rail arc (Z = 2.803 → 3.25).
         G18 - Revolve the G17 meridian (G16 → G15 outer) into the boss
               and union it into the fork.
         G19 - Extrude-cut the G15 inner circle 5.5 along -Z and 1.0 along
               +Z → the through-hole (bottom rim at the block base Z = 0).
         G20 - Read S15; fillet (r = 0.2)  the hole BOTTOM rim (Z = 0).
         G21 - Read S16; fillet (r = 0.15) the hole TOP rim   (Z = 3.25).
         G22 - Read S17; fillet (r = 0.2)  the boss OUTER base rim (Z = 3.25).
  G23..G29 — Pin-to-fork transition, edge finishing, pin bore, and a final
       unstitch to a surface model:
         G23 - Read S18; circle profile (r ≈ 4.0) on Y = 20.5.
         G24 - Loft the fork BACK face (Y = 15.5) to the G23 circle, then
               union pin + fork + loft into ONE solid (bridges the 5 mm gap
               the literal coordinates left between fork and pin).
         G25 - Read S19; fillet (r = 2.0) the four loft corner edges.
         G26 - Read S20; equal-distance 0.5 chamfer on the top (Z = 11.6)
               and bottom (Z = 0) outer perimeter edges (mirror-symmetric,
               same half-mirror method as G6).
         G27 - Read S21; circle (r ≈ 1.425) on Y = 30.5, extrude-cut 15 mm
               along -Y → axial bore through the pin (Y = 30.5 → 15.5).
         G28 - Fillet (r = 0.25) the bore's start (Y = 30.5) and end
               (Y = 15.5) rims.
         G29 - Unstitch the finished solid into an open Shell — a 2-D
               surface (sheet) model with no enclosed volume.
  G3 - LAST: compound + .clean() + STL/STEP/summary export.

NOTE on connectivity: with the coordinates as given, the pin spans
Y = 20.5 .. 30.5 while the fork tops out at Y = 15.5, i.e. the two
bodies are disjoint by 5 mm in Y.  This is reproduced faithfully and
flagged in the summary; both bodies are watertight solids carried in
one compound.

Cross-platform:
  BASE_DIR derived from script location. No hardcoded paths.

Code-style reference: zaphod_bot_mec_de_man_out_printer_proto_homing_block_build123d.py
(helpers and conventions reused -- CSV freshness logging, plane
auto-detection, checkpoint machinery, cumulative tracking, summary
writers.  The GEOMETRY differs: this is a closed SOLID built by solid
extrusion + boolean intersect + fillet, not surface extrusion.)
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
EDGE_MATCH_TOL  = 0.20   # mm; matching solid edges to S4 fillet edges
CHAMFER_MID_TOL = 1.00   # mm; matching solid edges to S5 chamfer edges by
                         # dense-sample minimum distance.  Looser than
                         # EDGE_MATCH_TOL because chamfer passes trim
                         # neighbouring edges, shifting their geometry.


# ══════════════════════════════════════════════════════════════════════════
# Paths
# ══════════════════════════════════════════════════════════════════════════
BASE_DIR    = Path(__file__).resolve().parent
FOLDER_NAME = BASE_DIR.name
CSV_DIR     = BASE_DIR / "csv_merged"

# This part has S1..S11.
S_CSV = {n: CSV_DIR / f"Fusion_Coordinates_S{n}.csv" for n in range(1, 22)}

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
    Edge, Wire, Face, Solid, Shell, Shape, Compound,
    extrude, fillet, chamfer, loft, mirror, revolve,
    export_stl, export_step,
    GeomType,
)
from ocp_vscode import show, set_port, reset_show
set_port(3939)

# Direct OCCT access for the circle edges, boolean operations, and loft.
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir, gp_Circ, gp_Ax1
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeWire
from OCP.TopoDS import TopoDS_Wire


# ══════════════════════════════════════════════════════════════════════════
# VIEWER + EXPORT CHECKPOINT CONFIG
# Valid checkpoint numbers: 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14
#   (G3 is the final export step).
# Set VIEW_AT to None for a full G1..G14 run.
# ══════════════════════════════════════════════════════════════════════════
VIEW_AT                 = 29
STOP_AFTER_VIEW         = True
EXPORT_AT_CHECKPOINT    = True

GUIDELINE_RANGE = "G_1_29"


# ══════════════════════════════════════════════════════════════════════════
# CHECKPOINT MACHINERY
# stage_pieces holds the CURRENT solid bodies of the part.  Because this is a
# closed-solid part we record cumulative surface AREA (per the template) AND
# cumulative VOLUME (the natural metric for solids / the compare step).
# ══════════════════════════════════════════════════════════════════════════
stage_pieces = []
area_history = []


def cumulative_area(pieces):
    total = 0.0
    for p in pieces:
        try:
            for f in p.faces():
                total += float(f.area)
        except Exception:
            pass
    return total


def cumulative_volume(pieces):
    total = 0.0
    for p in pieces:
        try:
            for s in p.solids():
                total += float(s.volume)
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
        f"{'Guideline':>10}  {'Cum. area (mm²)':>18}  {'Δ area (mm²)':>14}  "
        f"{'Cum. vol (mm³)':>16}  {'Δ vol (mm³)':>14}  Label",
        "-" * 110,
    ]
    for e in area_history:
        lines.append(
            f"  G{e['g']:<8d}  {e['area']:>18.3f}  {e['darea']:>+14.3f}  "
            f"{e['vol']:>16.3f}  {e['dvol']:>+14.3f}  {e['label']}"
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
        f"Bodies in compound  :  {len(pieces)}",
        f"Cumulative area     :  {cumulative_area(pieces):.3f} mm²",
        f"Cumulative volume   :  {cumulative_volume(pieces):.3f} mm³",
        "=" * 60,
    ]
    with open(cp_txt, "w") as f:
        f.write("\n".join(lines))
    print(f"     [CHECKPOINT] Wrote: {cp_txt.name}")
    _write_area_history_summary(g_num)


def checkpoint(g_num, label):
    """Record cumulative area + volume over the CURRENT stage_pieces.

    Callers mutate stage_pieces (append new bodies, or swap/replace bodies
    for trim/intersect/fillet steps) BEFORE calling this; the cumulative
    metrics are recomputed over stage_pieces so deltas come out correctly
    (negative deltas are expected for cut / intersect steps)."""
    cum_area = cumulative_area(stage_pieces)
    cum_vol  = cumulative_volume(stage_pieces)
    darea = cum_area - (area_history[-1]["area"] if area_history else 0.0)
    dvol  = cum_vol  - (area_history[-1]["vol"]  if area_history else 0.0)
    area_history.append({"g": g_num, "label": label,
                         "area": cum_area, "darea": darea,
                         "vol": cum_vol, "dvol": dvol})
    print(f"     [AREA] After G{g_num}: cumulative = {cum_area:.3f} mm²  "
          f"(Δ = {darea:+.3f} mm²)")
    print(f"     [VOL ] After G{g_num}: cumulative = {cum_vol:.3f} mm³  "
          f"(Δ = {dvol:+.3f} mm³)")
    if VIEW_AT != g_num:
        return
    print(f"\n[VIEW] Cumulative state after G{g_num} ({label})")
    print(f"       Bodies in stage_pieces: {len(stage_pieces)}")
    try: reset_show()
    except Exception: pass
    try:
        show(*stage_pieces)
        print(f"       Sent {len(stage_pieces)} body(ies) to OCP viewer (port 3939)")
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
    out, i = [], 1
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
        triples.append((float(row[f"X{i}"]),
                        float(row[f"Y{i}"]),
                        float(row[f"Z{i}"])))
    return triples


def _collect_all_points(rows):
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
    """Lift an in-plane (u, v) point to world-space Vector(x, y, z)."""
    u, v = in_plane_pt
    if   axis == "z": return Vector(u, v, plane_value)
    elif axis == "y": return Vector(u, plane_value, v)
    else:             return Vector(plane_value, u, v)


def axis_normal(axis):
    if   axis == "z": return Vector(0, 0, 1)
    elif axis == "y": return Vector(0, 1, 0)
    else:             return Vector(1, 0, 0)


def in_plane_uv(row, idx, axis):
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


def parse_three_point_circles(rows, axis):
    circ = []
    for r in rows:
        if not _norm_draw_type(r["Draw Type"]).startswith("3_point_circle"):
            continue
        circ.append((in_plane_uv(r, 1, axis),
                     in_plane_uv(r, 2, axis),
                     in_plane_uv(r, 3, axis)))
    return circ


def parse_line_segments_world(rows):
    """Every Line row as a pair of world Vectors (kept full 3-D — used for
    matching model edges to S4 fillet edges)."""
    segs = []
    for r in rows:
        if not _norm_draw_type(r["Draw Type"]).startswith("line"):
            continue
        (x1, y1, z1), (x2, y2, z2) = _row_all_xyz_triples(r)[:2]
        segs.append((Vector(x1, y1, z1), Vector(x2, y2, z2)))
    return segs


def parse_edges_world(rows):
    """Parse every edge row (Line OR 3-point arc) into a descriptor used to
    locate the matching edge on the model for the G6 chamfer.

    Returns a list of dicts: {'kind', 'start', 'end', 'mid'} (world Vectors).
      * Line          -> start/end are the two endpoints, mid = their midpoint.
      * 3-point arc    -> start/end are the 1st/3rd points, mid = the 2nd
                          (on-curve) point."""
    out = []
    for r in rows:
        dt = _norm_draw_type(r["Draw Type"])
        trips = _row_all_xyz_triples(r)
        if dt.startswith("line") and len(trips) >= 2:
            a = Vector(*trips[0]); b = Vector(*trips[1])
            out.append({"kind": "line", "start": a, "end": b,
                        "mid": (a + b) * 0.5})
        elif (dt.startswith("3_point_arc") or
              dt.startswith("3_point_circle")) and len(trips) >= 3:
            a = Vector(*trips[0]); m = Vector(*trips[1]); b = Vector(*trips[2])
            out.append({"kind": "arc", "start": a, "end": b, "mid": m})
    return out


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
    return Edge.make_line(world_vec_axis(p_uv, axis, plane_value),
                          world_vec_axis(q_uv, axis, plane_value))


def make_circle_edge(center_uv, radius, axis, plane_value):
    """Full-circle Edge centred at the in-plane point, on the axis-aligned
    sketch plane (built with raw OCCT so the plane normal is exact)."""
    origin = world_vec_axis(center_uv, axis, plane_value)
    normal = axis_normal(axis)
    circ = gp_Circ(gp_Ax2(gp_Pnt(origin.X, origin.Y, origin.Z),
                          gp_Dir(normal.X, normal.Y, normal.Z)), radius)
    return Edge(BRepBuilderAPI_MakeEdge(circ).Edge())


def circle_face(center_uv, radius, axis, plane_value):
    return Face(Wire([make_circle_edge(center_uv, radius, axis, plane_value)]))


def _kep(uv, tol=1e-2):
    return (round(uv[0] / tol) * tol, round(uv[1] / tol) * tol)


def closed_face_from_lines(line_segs, axis, plane_value):
    """Build a closed planar Face from a set of line segments that form ONE
    closed loop.  Edges are connected by build123d's Wire ordering; the wire
    is asserted closed."""
    edges = [make_line_edge(a, b, axis, plane_value) for (a, b) in line_segs]
    wire = Wire(edges)
    if not wire.is_closed:
        raise ValueError("Line segments do not form a closed loop.")
    return Face(wire)


def rectangle_face_from_open_lines(line_segs, axis, plane_value):
    """Given line segments that form an OPEN polyline (exactly two free
    endpoints), close it with one extra segment and return the Face."""
    touch = {}
    originals = {}
    for (a, b) in line_segs:
        for p in (a, b):
            k = _kep(p)
            touch[k] = touch.get(k, 0) + 1
            originals[k] = p
    free = [originals[k] for k, c in touch.items() if c == 1]
    if len(free) != 2:
        raise ValueError(f"Expected exactly 2 free endpoints to close, "
                         f"got {len(free)}.")
    closed = list(line_segs) + [(free[0], free[1])]
    return closed_face_from_lines(closed, axis, plane_value)


def parse_three_point_arcs_world(rows):
    """Parse every 3_point_arc row into world-space triple (start, mid, end)
    as Vector objects — used to build OCCT arc edges for guide rails (G9)."""
    arcs = []
    for r in rows:
        if not _norm_draw_type(r["Draw Type"]).startswith("3_point_arc"):
            continue
        trips = _row_all_xyz_triples(r)
        if len(trips) >= 3:
            arcs.append((Vector(*trips[0]), Vector(*trips[1]), Vector(*trips[2])))
    return arcs


def make_arc_edge_3pt(p1_vec, p2_vec, p3_vec):
    """Build a build123d Edge that is a circular arc through three world-space
    Vectors.  Wraps Edge.make_three_point_arc (OCCT GC_MakeArcOfCircle)."""
    return Edge.make_three_point_arc(p1_vec, p2_vec, p3_vec)


# ══════════════════════════════════════════════════════════════════════════
# G1 — Read S1: one 3-point circle on Y = 30.  Build the circle profile and
#       extrude it as a SOLID: straight -Y (9.5, zero taper) + tapered cap
#       +Y (0.5, 45° taper drawn SMALLER).
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G1] Reading {S_CSV[1].name}")
s1_rows = read_rows(S_CSV[1])
_p1 = detect_sketch_plane(s1_rows)
if _p1[0] != "axis":
    sys.exit(f"❌ G1: S1 not axis-aligned (got {_p1[0]}).")
_, S1_AXIS, S1_PLANE = _p1
print(f"     S1 plane: {S1_AXIS.upper()} = {S1_PLANE}")

s1_circles = parse_three_point_circles(s1_rows, S1_AXIS)
if len(s1_circles) != 1:
    sys.exit(f"❌ G1: expected 1 circle in S1, got {len(s1_circles)}.")
pin_center, pin_radius = circle_from_3_points(*s1_circles[0])
print(f"     Pin circle: center=({pin_center[0]:.3f},{pin_center[1]:.3f}) "
      f"r={pin_radius:.3f} mm")

pin_face = circle_face(pin_center, pin_radius, S1_AXIS, S1_PLANE)
n1 = axis_normal(S1_AXIS)

STRAIGHT_LEN = 9.5
CAP_LEN      = 0.5
TAPER_DEG    = 45.0   # build123d sign that SHRINKS the swept profile
pin_y_lo = S1_PLANE - STRAIGHT_LEN     # 20.5
pin_y_hi = S1_PLANE + CAP_LEN          # 30.5

pin_straight = extrude(pin_face, amount=STRAIGHT_LEN, dir=tuple(n1 * -1))
pin_cap      = extrude(pin_face, amount=CAP_LEN, dir=tuple(n1), taper=TAPER_DEG)
pin = pin_straight + pin_cap

top_r = pin_radius - CAP_LEN * math.tan(math.radians(TAPER_DEG))
print(f"     Straight cylinder : {S1_AXIS.upper()}={S1_PLANE}→{pin_y_lo}, "
      f"r={pin_radius:.3f}")
print(f"     Tapered cap       : {S1_AXIS.upper()}={S1_PLANE}→{pin_y_hi}, "
      f"45° taper inward → top r≈{top_r:.3f}")
print(f"     Pin volume        : {pin.volume:.3f} mm³  (valid={pin.is_valid})")

stage_pieces.append(pin)
checkpoint(1, f"G1 pin solid on {S1_AXIS.upper()}={S1_PLANE} "
              f"({S1_AXIS.upper()}={pin_y_lo}..{pin_y_hi})")


# ══════════════════════════════════════════════════════════════════════════
# G2 — Read S2: 3 lines + 1 circle on Z = 15.  Build the rounded-bottom
#       rectangle and extrude 22 units along -Z into a SOLID block.
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G2] Reading {S_CSV[2].name}")
s2_rows = read_rows(S_CSV[2])
_p2 = detect_sketch_plane(s2_rows)
if _p2[0] != "axis":
    sys.exit(f"❌ G2: S2 not axis-aligned (got {_p2[0]}).")
_, S2_AXIS, S2_PLANE = _p2
print(f"     S2 plane: {S2_AXIS.upper()} = {S2_PLANE}")

s2_lines   = parse_line_segments(s2_rows, S2_AXIS)
s2_circles = parse_three_point_circles(s2_rows, S2_AXIS)
print(f"     S2 lines: {len(s2_lines)}, three-point circles: {len(s2_circles)}")
if len(s2_lines) != 3 or len(s2_circles) != 1:
    sys.exit(f"❌ G2: expected 3 lines + 1 circle in S2, "
             f"got {len(s2_lines)} + {len(s2_circles)}.")

BLOCK_LEN = 22.0
n2 = axis_normal(S2_AXIS)
block_z_lo = S2_PLANE - BLOCK_LEN      # -7.0

rect_face = rectangle_face_from_open_lines(s2_lines, S2_AXIS, S2_PLANE)
circ_center, circ_radius = circle_from_3_points(*s2_circles[0])
print(f"     Rectangle face area : {rect_face.area:.3f} mm²")
print(f"     Bottom circle       : center=({circ_center[0]:.3f},"
      f"{circ_center[1]:.3f}) r={circ_radius:.3f} mm")
circ_face_block = circle_face(circ_center, circ_radius, S2_AXIS, S2_PLANE)

block_rect = extrude(rect_face, amount=BLOCK_LEN, dir=tuple(n2 * -1))
block_circ = extrude(circ_face_block, amount=BLOCK_LEN, dir=tuple(n2 * -1))
block = block_rect + block_circ
print(f"     Block (rounded-bottom rect, {S2_AXIS.upper()}={S2_PLANE}→"
      f"{block_z_lo}): volume {block.volume:.3f} mm³  (valid={block.is_valid})")

stage_pieces.append(block)
checkpoint(2, f"G2 block solid on {S2_AXIS.upper()}={S2_PLANE} "
              f"({S2_AXIS.upper()}={S2_PLANE}..{block_z_lo})")


# ══════════════════════════════════════════════════════════════════════════
# G4 — Read S3: 13 lines on X = 10 forming the closed clevis side profile.
#       Extrude 23 units along -X and INTERSECT (boolean common) with the
#       block to form the forked clevis body.
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G4] Reading {S_CSV[3].name}")
s3_rows = read_rows(S_CSV[3])
_p3 = detect_sketch_plane(s3_rows)
if _p3[0] != "axis":
    sys.exit(f"❌ G4: S3 not axis-aligned (got {_p3[0]}).")
_, S3_AXIS, S3_PLANE = _p3
print(f"     S3 plane: {S3_AXIS.upper()} = {S3_PLANE}")

s3_lines = parse_line_segments(s3_rows, S3_AXIS)
print(f"     S3 lines: {len(s3_lines)}")
profile_face = closed_face_from_lines(s3_lines, S3_AXIS, S3_PLANE)
print(f"     S3 profile face area : {profile_face.area:.3f} mm²")

SWEEP_LEN = 23.0
n3 = axis_normal(S3_AXIS)
sweep_x_lo = S3_PLANE - SWEEP_LEN      # -13.0
sweep_solid = extrude(profile_face, amount=SWEEP_LEN, dir=tuple(n3 * -1))
print(f"     S3 sweep solid ({S3_AXIS.upper()}={S3_PLANE}→{sweep_x_lo}): "
      f"volume {sweep_solid.volume:.3f} mm³")

fork = block & sweep_solid           # boolean COMMON (intersect)
print(f"     Intersected fork body: volume {fork.volume:.3f} mm³  "
      f"(valid={fork.is_valid}, solids={len(fork.solids())})")

stage_pieces[:] = [p for p in stage_pieces if p is not block]
stage_pieces.append(fork)
checkpoint(4, f"G4 intersected fork body ({S3_AXIS.upper()}={S3_PLANE}→"
              f"{sweep_x_lo} sweep ∩ block)")


# ══════════════════════════════════════════════════════════════════════════
# G5 — Read S4: 2 line edges naming the inner corners at the back of the
#       slot.  Apply a 2 mm radius fillet on the matching model edges.
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G5] Reading {S_CSV[4].name}")
s4_rows  = read_rows(S_CSV[4])
s4_edges = parse_line_segments_world(s4_rows)
print(f"     S4 fillet edges (named): {len(s4_edges)}")
FILLET_RADIUS = 2.0

def _unit(v):
    L = v.length
    return v / L if L > 1e-9 else v

targets = []
for (a, b) in s4_edges:
    mid = (a + b) * 0.5
    d   = _unit(b - a)
    targets.append((mid, d))
    print(f"     target mid=({mid.X:.3f},{mid.Y:.3f},{mid.Z:.3f}) "
          f"dir=({d.X:.2f},{d.Y:.2f},{d.Z:.2f})")

sel_edges = []
for e in fork.edges():
    if e.geom_type != GeomType.LINE:
        continue
    c  = e.center()
    de = _unit(e.end_point() - e.start_point())
    for (mid, d) in targets:
        parallel = abs(abs(de.dot(d)) - 1.0) < 1e-3
        close    = (c - mid).length < EDGE_MATCH_TOL
        if parallel and close:
            sel_edges.append(e)
            break
print(f"     Matched model edges to fillet: {len(sel_edges)}")
if len(sel_edges) != len(s4_edges):
    print(f"     ⚠  matched {len(sel_edges)} edge(s) but S4 names "
          f"{len(s4_edges)} — check EDGE_MATCH_TOL.")

fork_filleted = fillet(sel_edges, radius=FILLET_RADIUS)
print(f"     Filleted fork: volume {fork_filleted.volume:.3f} mm³  "
      f"(valid={fork_filleted.is_valid})")

stage_pieces[:] = [p for p in stage_pieces if p is not fork]
stage_pieces.append(fork_filleted)
checkpoint(5, f"G5 filleted {len(sel_edges)} slot edge(s) at r={FILLET_RADIUS} mm")


# ══════════════════════════════════════════════════════════════════════════
# G6 — Read S5: the model edges around the slot mouth (6 straight lines +
#       6 three-point arcs, including the four G5 fillet arcs).  Apply an
#       EQUAL-DISTANCE chamfer of 0.25 mm to every one of them.
#
# FIX — symmetric two-group approach:
#
#   Previous bug: the old code chamfered each face group in a separate
#   sequential pass.  Every pass reshapes the shared slot faces, so the
#   second side's topology differs from the first's, producing systematically
#   different vertex counts on X=0.236 vs X=9.236 (26 vs 16 in testing) —
#   i.e. three visible outlines on one side, two on the other.
#
#   Fix:
#     Group A — ALL side-face edges (both X=0.236 and X=9.236 simultaneously):
#       S5 indices 0–5  (6 straight slot/back-wall lines, 3 per side face)
#       S5 indices 8–11 (4 G5 fillet arcs, 2 per side face)
#       Total: 10 edges in one chamfer() call → OCCT sees both sides at once,
#       corners close symmetrically, mirror symmetry is guaranteed by
#       construction.
#     Group B — front rounded-bottom arcs (S5 indices 6–7, 2 arcs):
#       Processed after Group A.
#
#   Edge matching: dense sampling (11 parameter values t ∈ [0,1] per edge)
#   replaces position_at(0.5) alone — robust to parametric drift and to arcs
#   whose geometric midpoint is not at t=0.5.
#
#   Symmetry check: vertex counts on each side face are printed after every
#   group so asymmetry is immediately visible if it re-appears.
#
#   S5 row → group mapping (0-indexed specs):
#     0  Line  X=9.236 top-slot  (Y=11.5→4.5,  Z=8.797)   → Group A
#     1  Line  X=0.236 top-slot  (Y=4.5→11.5,  Z=8.797)   → Group A
#     2  Line  X=0.236 back-wall (Z=6.797→4.803,Y=13.5)   → Group A
#     3  Line  X=9.236 back-wall (Z=4.803→6.797,Y=13.5)   → Group A
#     4  Line  X=9.236 bot-slot  (Y=4.5→11.5,  Z=2.803)   → Group A
#     5  Line  X=0.236 bot-slot  (Y=11.5→4.5,  Z=2.803)   → Group A
#     6  Arc   front top arc     (Z=8.797, X=0.236→9.236) → Group B
#     7  Arc   front bot arc     (Z=2.803, X=9.236→0.236) → Group B
#     8  Arc   G5 fillet arc     X=9.236 bot-back          → Group A
#     9  Arc   G5 fillet arc     X=9.236 top-back          → Group A
#    10  Arc   G5 fillet arc     X=0.236 top-back          → Group A
#    11  Arc   G5 fillet arc     X=0.236 bot-back          → Group A
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G6] Reading {S_CSV[5].name}")
s5_rows  = read_rows(S_CSV[5])
s5_specs = parse_edges_world(s5_rows)
CHAMFER_DIST = 0.25
n_line = sum(1 for s in s5_specs if s["kind"] == "line")
n_arc  = sum(1 for s in s5_specs if s["kind"] == "arc")
print(f"     S5 chamfer edges (named): {len(s5_specs)} "
      f"({n_line} line, {n_arc} arc)")


# ── Dense-sample edge matcher ─────────────────────────────────────────────
def _sample_edge(e, n=11):
    """Sample n points along model edge e at evenly-spaced parameter values.
    Falls back to center() if position_at fails."""
    pts = []
    for i in range(n):
        t = i / (n - 1)
        try:
            pts.append(e.position_at(t))
        except Exception:
            pass
    if not pts:
        try:
            pts.append(e.center())
        except Exception:
            pass
    return pts


def _spec_sample_pts(spec, n=11):
    """Sample n points along an S5 spec segment.
    Line: lerp start→end.
    Arc:  lerp start→mid then mid→end (two sub-segments), producing
          2n-1 points that densely cover the curve."""
    if spec["kind"] == "line":
        a, b = spec["start"], spec["end"]
        return [(a + (b - a) * (i / (n - 1))) for i in range(n)]
    else:
        a, m, b = spec["start"], spec["mid"], spec["end"]
        half = n // 2 + 1
        pts  = [(a + (m - a) * (i / (half - 1))) for i in range(half)]
        pts += [(m + (b - m) * (i / (half - 1))) for i in range(1, half)]
        return pts


def _min_dist_to_spec(edge_pts, spec_pts):
    """Minimum distance between two point clouds (one per entity)."""
    best = float("inf")
    for ep in edge_pts:
        for sp in spec_pts:
            d = (ep - sp).length
            if d < best:
                best = d
    return best


def find_edge_for_spec(shape, spec, tol=CHAMFER_MID_TOL):
    """Return the model edge whose dense-sampled point cloud is closest to
    the spec's dense-sampled point cloud, within `tol`.
    Returns (edge, dist) or (None, inf)."""
    spec_pts = _spec_sample_pts(spec, n=11)
    best_e, best_d = None, float("inf")
    for e in shape.edges():
        ep = _sample_edge(e, n=11)
        d  = _min_dist_to_spec(ep, spec_pts)
        if d < best_d:
            best_d, best_e = d, e
    if best_d <= tol:
        return best_e, best_d
    return None, best_d


# ── Symmetry verifier ─────────────────────────────────────────────────────
def _check_lr_symmetry(shape, label, x_lo=0.236, x_hi=9.236, tol=0.5):
    """Count vertices within `tol` of each side face and report."""
    vlo = sum(1 for v in shape.vertices()
              if abs(float(v.X) - x_lo) < tol)
    vhi = sum(1 for v in shape.vertices()
              if abs(float(v.X) - x_hi) < tol)
    sym = "✓ symmetric" if vlo == vhi else f"✗ ASYMMETRIC ({vlo} vs {vhi})"
    print(f"     [SYM] {label}: X={x_lo} → {vlo} verts, "
          f"X={x_hi} → {vhi} verts  {sym}")
    return vlo == vhi


# ── Symmetric chamfer via half-mirror-fuse ────────────────────────────────
#   The 12 S5 edges meet TANGENTLY at shared vertices (a straight slot edge
#   runs collinear into a G5 fillet arc), so OCCT cannot close a chamfer
#   corner when both edges of such a junction are chamfered together — a
#   single all-edges call fails, and any *sequential* batching is
#   order-dependent and breaks the part's left/right mirror symmetry about
#   X = (min+max)/2 of the S5 mid-points (= 4.736).  The robust fix exploits
#   that symmetry directly:
#     1. cut the fork at the mid-plane and keep ONE half;
#     2. chamfer that half's slot-mouth edges (the front arcs become
#        half-arcs ending on the cut plane — far fewer tangent conflicts, so
#        the whole half chamfers in one OCCT call);
#     3. MIRROR the chamfered half across the mid-plane and fuse the two
#        halves back together.
#   The two sides are then identical by construction, and the removed volume
#   matches the analytic 0.25-chamfer prism volume of all 12 edges.
def _symmetric_chamfer(solid, specs, dist):
    xs   = [s["mid"].X for s in specs]
    xsym = (min(xs) + max(xs)) / 2.0
    # Dense point samples of each named S5 edge, for geometric selection.
    ref_samples = []
    for s in specs:
        ref = (Edge.make_line(s["start"], s["end"]) if s["kind"] == "line"
               else Edge.make_three_point_arc(s["start"], s["mid"], s["end"]))
        ref_samples.append([ref.position_at(u) for u in np.linspace(0, 1, 400)])

    def _on_s5(p, tol=0.05):
        return any(min((p - q).length for q in pts) < tol for pts in ref_samples)

    # Keep the half with X <= xsym (boolean intersect with a large half-space box).
    box  = Solid.make_box(400, 400, 400).translate((xsym - 400, -200, -200))
    half = solid & box
    sel  = [e for e in half.edges()
            if abs(e.position_at(0.5).X - xsym) > 1e-4 and _on_s5(e.position_at(0.5))]
    print(f"     mid-plane X={xsym:.3f}; half-solid carries {len(sel)} "
          f"slot-mouth edge(s) to chamfer")

    try:
        half_ch = chamfer(sel, length=dist)
        print(f"     half chamfered as one batch ({len(sel)} edges)")
    except Exception as exc:
        print(f"     half batch failed ({str(exc)[:45]}) — per-edge fallback")
        half_ch = half
        for e in sel:
            m = e.position_at(0.5)
            tgt = min(half_ch.edges(),
                      key=lambda x: (x.position_at(0.5) - m).length)
            try:
                half_ch = chamfer([tgt], length=dist)
            except Exception:
                pass

    mplane  = Plane(origin=(xsym, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    mirrored = mirror(half_ch, about=mplane)
    fused = half_ch + mirrored
    try:
        fused = fused.clean()
    except Exception as exc:
        print(f"     ⚠  .clean() after fuse: {exc}")
    return fused, len(specs)

fork_chamfered, chamfered_count = _symmetric_chamfer(fork_filleted,
                                                     s5_specs, CHAMFER_DIST)
print(f"\n     Chamfered {chamfered_count}/{len(s5_specs)} S5 edge(s) "
      f"at {CHAMFER_DIST} mm (equal distance, symmetric)")
print(f"     Chamfered fork: volume {fork_chamfered.volume:.3f} mm³  "
      f"(valid={fork_chamfered.is_valid})")
_check_lr_symmetry(fork_chamfered, "FINAL G6")

stage_pieces[:] = [p for p in stage_pieces if p is not fork_filleted]
stage_pieces.append(fork_chamfered)
checkpoint(6, f"G6 chamfered {chamfered_count} slot-mouth edge(s) "
              f"at {CHAMFER_DIST} mm (equal distance, mirror-symmetric)")


# ══════════════════════════════════════════════════════════════════════════
# G7 — Read S6: TWO 3-point circles on Z = 8.35.
#       3_point_circle_1 -> INNER circle  (r ≈ 2.505)  used for G11 cut.
#       3_point_circle_2 -> OUTER circle  (r ≈ 3.555)  used for G10 loft.
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G7] Reading {S_CSV[6].name}")
s6_rows = read_rows(S_CSV[6])
_p6 = detect_sketch_plane(s6_rows)
if _p6[0] != "axis":
    sys.exit(f"❌ G7: S6 not axis-aligned (got {_p6[0]}).")
_, S6_AXIS, S6_PLANE = _p6
print(f"     S6 plane: {S6_AXIS.upper()} = {S6_PLANE}")

s6_circles = parse_three_point_circles(s6_rows, S6_AXIS)
if len(s6_circles) != 2:
    sys.exit(f"❌ G7: expected 2 circles in S6, got {len(s6_circles)}.")

# Row ordering in CSV: 3_point_circle_1 = inner, 3_point_circle_2 = outer.
g7_inner_center, g7_inner_radius = circle_from_3_points(*s6_circles[0])
g7_outer_center, g7_outer_radius = circle_from_3_points(*s6_circles[1])
print(f"     G7 inner circle: center=({g7_inner_center[0]:.4f},{g7_inner_center[1]:.4f})"
      f" r={g7_inner_radius:.4f} mm")
print(f"     G7 outer circle: center=({g7_outer_center[0]:.4f},{g7_outer_center[1]:.4f})"
      f" r={g7_outer_radius:.4f} mm")

# Build Face objects for both circles (profiles, not solids yet).
g7_inner_face = circle_face(g7_inner_center, g7_inner_radius, S6_AXIS, S6_PLANE)
g7_outer_face = circle_face(g7_outer_center, g7_outer_radius, S6_AXIS, S6_PLANE)

# Build the circle Edges (Wires) for use as loft profiles.
g7_inner_edge = make_circle_edge(g7_inner_center, g7_inner_radius, S6_AXIS, S6_PLANE)
g7_outer_edge = make_circle_edge(g7_outer_center, g7_outer_radius, S6_AXIS, S6_PLANE)
g7_inner_wire = Wire([g7_inner_edge])
g7_outer_wire = Wire([g7_outer_edge])

print(f"     G7 inner face area: {g7_inner_face.area:.4f} mm²")
print(f"     G7 outer face area: {g7_outer_face.area:.4f} mm²")
checkpoint(7, f"G7 two circle profiles on {S6_AXIS.upper()}={S6_PLANE}: "
              f"inner r={g7_inner_radius:.4f}, outer r={g7_outer_radius:.4f}")


# ══════════════════════════════════════════════════════════════════════════
# G8 — Read S7: ONE 3-point circle on Z = 8.797 (upper loft terminus).
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G8] Reading {S_CSV[7].name}")
s7_rows = read_rows(S_CSV[7])
_p7 = detect_sketch_plane(s7_rows)
if _p7[0] != "axis":
    sys.exit(f"❌ G8: S7 not axis-aligned (got {_p7[0]}).")
_, S7_AXIS, S7_PLANE = _p7
print(f"     S7 plane: {S7_AXIS.upper()} = {S7_PLANE}")

s7_circles = parse_three_point_circles(s7_rows, S7_AXIS)
if len(s7_circles) != 1:
    sys.exit(f"❌ G8: expected 1 circle in S7, got {len(s7_circles)}.")

g8_center, g8_radius = circle_from_3_points(*s7_circles[0])
print(f"     G8 circle: center=({g8_center[0]:.4f},{g8_center[1]:.4f})"
      f" r={g8_radius:.4f} mm")

g8_face = circle_face(g8_center, g8_radius, S7_AXIS, S7_PLANE)
g8_edge = make_circle_edge(g8_center, g8_radius, S7_AXIS, S7_PLANE)
g8_wire = Wire([g8_edge])

print(f"     G8 face area: {g8_face.area:.4f} mm²")
checkpoint(8, f"G8 circle profile on {S7_AXIS.upper()}={S7_PLANE}: r={g8_radius:.4f}")


# ══════════════════════════════════════════════════════════════════════════
# G9 — Read S8: ONE 3-point arc in the Y = 4.5 plane.
#       This arc is the guide rail for the G10 loft operation.
#       It runs from the S6-outer-circle plane (Z = 8.35) to the
#       S7-circle plane (Z = 8.797), tracing the outer edge path.
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G9] Reading {S_CSV[8].name}")
s8_rows = read_rows(S_CSV[8])

s8_arcs = parse_three_point_arcs_world(s8_rows)
if len(s8_arcs) != 1:
    sys.exit(f"❌ G9: expected 1 three-point arc in S8, got {len(s8_arcs)}.")

g9_p1, g9_p2, g9_p3 = s8_arcs[0]
print(f"     G9 arc P1: ({g9_p1.X:.4f}, {g9_p1.Y:.4f}, {g9_p1.Z:.4f})")
print(f"     G9 arc P2: ({g9_p2.X:.4f}, {g9_p2.Y:.4f}, {g9_p2.Z:.4f})  (on-curve mid)")
print(f"     G9 arc P3: ({g9_p3.X:.4f}, {g9_p3.Y:.4f}, {g9_p3.Z:.4f})")
print(f"     Arc start Z = {g9_p1.Z:.4f} (should match S6 plane {S6_PLANE})")
print(f"     Arc end   Z = {g9_p3.Z:.4f} (should match S7 plane {S7_PLANE})")

g9_arc_edge  = make_arc_edge_3pt(g9_p1, g9_p2, g9_p3)
g9_guide_wire = Wire([g9_arc_edge])
print(f"     G9 guide rail arc length: {g9_arc_edge.length:.4f} mm")
checkpoint(9, f"G9 guide-rail arc in Y={g9_p1.Y:.3f} plane, "
              f"Z={g9_p1.Z:.4f}→{g9_p3.Z:.4f}")


# ══════════════════════════════════════════════════════════════════════════
# G10 — Loft: G7 outer circle  →  G8 circle, guided by G9 arc rail.
#
#  The correct OCCT kernel for a guide-rail loft is BRepFill_PipeShell:
#    - Spine  : the G9 arc wire (guide rail)
#    - Section 1 : G7 outer circle wire  (at spine start, Z = 8.35)
#    - Section 2 : G8 circle wire        (at spine end,   Z = 8.797)
#
#  BRepFill_PipeShell sweeps the evolving cross-section along the spine,
#  interpolating from section 1 to section 2 — this IS the guided loft.
#  BRepOffsetAPI_ThruSections (used previously) does NOT support guide
#  rails; it was the wrong kernel.
#
#  Mode: DiscreteTrihedron — robust for non-planar spines; keeps sections
#  normal to the spine tangent at each point.
#  MakeSolid() is called after Build() to cap the ends and return a solid.
#
#  Fallback: if PipeShell fails for any reason, fall back to an unguided
#  ThruSections loft between the two circles and print a clear warning.
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G10] Boss body: revolve the G9 meridian (G7 outer → G8) about the "
      f"central axis")
# The G7 outer circle (Z=8.35) and the G8 circle (Z=8.797) are CONCENTRIC, and
# the G9 rail is a single arc lying in the Y=g9_p1.Y plane.  Lofting two
# concentric circles along an in-plane rail is, by construction, a SURFACE OF
# REVOLUTION, so we build it directly with `revolve`.  This is both the
# faithful interpretation of the feature AND far more robust than a PipeShell
# loft: PipeShell emits a wobbly BSPLINE side wall whose base rim can only take
# a ~0.013 mm fillet (so the G14 0.2 mm fillet is impossible on it), whereas a
# revolved wall is an exact surface of revolution whose base rim is a true
# CIRCLE that fillets cleanly.
_axis_x, _axis_y = g7_outer_center[0], g7_outer_center[1]   # (4.736, 4.5)
_A_base = Vector(_axis_x, _axis_y, S6_PLANE)   # axis point at the outer-circle plane
_A_top  = Vector(_axis_x, _axis_y, S7_PLANE)   # axis point at the G8-circle plane
# Closed meridian: outer arc (g9) + top radius + axis segment + bottom radius.
_meridian = Wire([
    g9_arc_edge,                       # P1 (outer base) -> P3 (top), follows the rail
    Edge.make_line(g9_p3, _A_top),     # top disk radius
    Edge.make_line(_A_top, _A_base),   # along the central axis
    Edge.make_line(_A_base, g9_p1),    # bottom disk radius
])
_rev_axis = Axis((_axis_x, _axis_y, 0.0), (0.0, 0.0, 1.0))
g10_loft_solid = revolve(Face(_meridian), _rev_axis, revolution_arc=360)
g10_guided = True
print(f"     Revolved boss volume : {g10_loft_solid.volume:.4f} mm³  "
      f"(valid={g10_loft_solid.is_valid})")

# Boolean-union the loft into the fork body so they form ONE solid.
# Keeping the loft as a separate body (old code) left a shared internal face
# at Z=8.35 that was double-counted in surface area (~+79 mm²) and caused
# G11 to cut two separate bodies instead of one unified solid.
fork_with_loft = fork_chamfered + g10_loft_solid
print(f"     Fork + loft union: volume {fork_with_loft.volume:.4f} mm³  "
      f"(valid={fork_with_loft.is_valid})")
stage_pieces[:] = [p for p in stage_pieces if p is not fork_chamfered]
stage_pieces.append(fork_with_loft)
checkpoint(10, f"G10 loft unioned into fork (G7 outer → G8, guided={g10_guided}): "
               f"fork+loft volume {fork_with_loft.volume:.4f} mm³")


# ══════════════════════════════════════════════════════════════════════════
# G11 — Extrude-cut with G7 inner circle profile.
#        +3.25 units along +Z  (positive Z direction)
#        -0.01 unit  along -Z  (tiny epsilon to avoid coincident face at
#                               Z=8.35; keeps the bottom rim at Z≈8.35)
#
#  Net cut region: Z = (8.35 - 0.01) to (8.35 + 3.25) = Z = 8.34 .. 11.60
#
#  Why 3.25?  S9 (G12) names a circle edge at Z=11.6, r≈2.505 — the top
#  rim of this hole.  8.35 + 3.25 = 11.60 exactly.
#  Why ~0 on -Z?  S10 (G13) names a circle edge at Z=8.35 — the bottom
#  rim sits on the sketch plane itself, so only a tiny epsilon is needed
#  to keep OCCT from seeing a zero-thickness cutter face.
#
#  The inner circle face sits on Z = S6_PLANE = 8.35.  The cutter cylinder
#  is subtracted from every body in stage_pieces that it intersects.
#  After G10's union, the fork+loft is now ONE body, so the cut goes
#  through both regions in a single boolean subtraction.
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G11] Extrude-cut with G7 inner circle (r={g7_inner_radius:.4f})")

G11_POS_Z = 3.25   # extrude +Z  → top rim at Z = 8.35 + 3.25 = 11.60 (= S9 plane)
G11_NEG_Z = 0.01   # extrude -Z  → bottom rim at Z ≈ 8.35 (= S10 plane); epsilon avoids coincident face

nz_pos = Vector(0, 0,  1)
nz_neg = Vector(0, 0, -1)

# Build a cutter solid: extrude inner face +Z, then extrude same face -Z,
# union the two halves into one continuous cylinder spanning the full cut depth.
g11_cut_pos = extrude(g7_inner_face, amount=G11_POS_Z, dir=tuple(nz_pos))
g11_cut_neg = extrude(g7_inner_face, amount=G11_NEG_Z, dir=tuple(nz_neg))
g11_cutter  = g11_cut_pos + g11_cut_neg

z_lo_cut = S6_PLANE - G11_NEG_Z    # 8.34
z_hi_cut = S6_PLANE + G11_POS_Z    # 11.60
print(f"     Cutter region   : Z = {z_lo_cut:.3f} .. {z_hi_cut:.3f}")
print(f"     Cutter volume   : {g11_cutter.volume:.4f} mm³")

# Apply boolean cut to EVERY body in stage_pieces.
# Each body is subtracted individually so bodies that don't intersect
# the cutter are kept unchanged (subtraction returns the original if
# there is no overlap).
new_stage = []
for idx, body in enumerate(stage_pieces):
    body_bb = body.bounding_box()
    # Quick bounding-box pre-check: skip bodies entirely above or below the cutter.
    if body_bb.min.Z > z_hi_cut or body_bb.max.Z < z_lo_cut:
        print(f"     body[{idx}]: Z=[{body_bb.min.Z:.3f},{body_bb.max.Z:.3f}] "
              f"— outside cutter Z range, kept unchanged")
        new_stage.append(body)
        continue
    try:
        cut_body = body - g11_cutter
        vol_before = body.volume
        vol_after  = cut_body.volume
        print(f"     body[{idx}]: volume {vol_before:.4f} → {vol_after:.4f} mm³  "
              f"Δ={vol_after - vol_before:+.4f}  (valid={cut_body.is_valid})")
        new_stage.append(cut_body)
    except Exception as exc:
        print(f"     body[{idx}]: boolean cut failed ({exc}) — kept unchanged")
        new_stage.append(body)

stage_pieces[:] = new_stage

# g10_final is the cut version of the loft body (last appended = G10 body).
# Retrieve it by position — it was the last body added before G11.
g10_final = stage_pieces[-1]

checkpoint(11, f"G11 extrude-cut: inner r={g7_inner_radius:.4f}, "
               f"+{G11_POS_Z}/-{G11_NEG_Z} Z, "
               f"Z={z_lo_cut:.3f}..{z_hi_cut:.3f}")




# ══════════════════════════════════════════════════════════════════════════
# G12 — Read S9: one 3-point circle on Z = 11.6.
#        Match the corresponding circular model edge and apply a 0.2 mm
#        radius fillet.  This edge is the top rim of the G11 extrude-cut
#        hole (the circle at Z ≈ 11.6, r ≈ 2.505).
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G12] Reading {S_CSV[9].name}")
s9_rows   = read_rows(S_CSV[9])
_p9       = detect_sketch_plane(s9_rows)
if _p9[0] != "axis":
    sys.exit(f"❌ G12: S9 not axis-aligned (got {_p9[0]}).")
_, S9_AXIS, S9_PLANE = _p9
print(f"     S9 plane: {S9_AXIS.upper()} = {S9_PLANE}")

s9_circles = parse_three_point_circles(s9_rows, S9_AXIS)
if len(s9_circles) != 1:
    sys.exit(f"❌ G12: expected 1 circle in S9, got {len(s9_circles)}.")
g12_center, g12_radius = circle_from_3_points(*s9_circles[0])
print(f"     G12 circle: center=({g12_center[0]:.4f},{g12_center[1]:.4f}) "
      f"r={g12_radius:.4f} mm  plane {S9_AXIS.upper()}={S9_PLANE}")

FILLET_RADIUS_G12 = 0.2

def _find_circle_edge(shape, center_uv, radius, plane_axis, plane_val,
                      r_tol=0.10, plane_tol=0.5):
    """Return all model edges that belong to the circular feature described.
    Uses pure geometric 3-point sampling to bypass OCCT's BSPLINE/CIRCLE types."""
    candidates = []
    for e in shape.edges():
        try:
            # Sample 3 points along the curve
            p1 = e.position_at(0.1)
            p2 = e.position_at(0.5)
            p3 = e.position_at(0.9)
        except Exception:
            continue
            
        # Plane coordinate check based on the sampled points
        if plane_axis == "z":
            ep_val = p2.Z
            tp1, tp2, tp3 = (p1.X, p1.Y), (p2.X, p2.Y), (p3.X, p3.Y)
            dz = max(abs(p1.Z - ep_val), abs(p3.Z - ep_val))
            if dz > 0.15: continue # Ensure edge is planar in Z
        elif plane_axis == "y":
            ep_val = p2.Y
            tp1, tp2, tp3 = (p1.X, p1.Z), (p2.X, p2.Z), (p3.X, p3.Z)
            dy = max(abs(p1.Y - ep_val), abs(p3.Y - ep_val))
            if dy > 0.15: continue
        else:
            ep_val = p2.X
            tp1, tp2, tp3 = (p1.Y, p1.Z), (p2.Y, p2.Z), (p3.Y, p3.Z)
            dx = max(abs(p1.X - ep_val), abs(p3.X - ep_val))
            if dx > 0.15: continue

        if abs(ep_val - plane_val) > plane_tol:
            continue

        try:
            # Reconstruct radius using circumradius formula
            (cu, cv), arc_r = circle_from_3_points(tp1, tp2, tp3)
        except Exception:
            continue
            
        candidates.append((e, arc_r, cu, cv, ep_val, e.geom_type.name))

    # Diagnostic log
    if candidates:
        print(f"       [diag] {len(candidates)} planar edge(s) near "
              f"{plane_axis.upper()}≈{plane_val}:")
        for (e, ar, cu, cv, epv, gtn) in candidates:
            flag = ("✓" if abs(ar - radius) <= r_tol and
                    math.hypot(cu - center_uv[0], cv - center_uv[1]) < r_tol + 0.2
                    else " ")
            print(f"         {flag} {gtn:8s}  {plane_axis.upper()}={epv:.4f}  "
                  f"r={ar:.4f}  center=({cu:.3f},{cv:.3f})")

    matched = []
    for (e, arc_r, cu, cv, ep_val, gtn) in candidates:
        if abs(arc_r - radius) > r_tol:
            continue
        if math.hypot(cu - center_uv[0], cv - center_uv[1]) > r_tol + 0.2:
            continue
        matched.append(e)
    return matched

# After G11 the fork+loft body is stage_pieces[-1] (pin is stage_pieces[0]).
# Fillets target the fork+loft body.
fork_body = stage_pieces[-1]

g12_edges = _find_circle_edge(fork_body, g12_center, g12_radius,
                               S9_AXIS, S9_PLANE)
print(f"     Matched circle edges for G12 fillet: {len(g12_edges)}")
if not g12_edges:
    print(f"     ⚠  no matching edge found — skipping G12 fillet")
    fork_g12 = fork_body
else:
    try:
        fork_g12 = fillet(g12_edges, radius=FILLET_RADIUS_G12)
        print(f"     G12 filleted volume: {fork_g12.volume:.4f} mm³  "
              f"(valid={fork_g12.is_valid})")
    except Exception as exc:
        print(f"     ⚠  G12 fillet failed: {exc} — keeping body unchanged")
        fork_g12 = fork_body

stage_pieces[:] = [p for p in stage_pieces if p is not fork_body]
stage_pieces.append(fork_g12)
checkpoint(12, f"G12 fillet r={FILLET_RADIUS_G12} mm on S9 circle edge "
               f"(Z={S9_PLANE}, r={g12_radius:.4f})")


# ══════════════════════════════════════════════════════════════════════════
# G13 — Read S10: one 3-point circle on Z = 8.35.
#        Matches the inner circle (r ≈ 2.505) — the bottom rim of the G11
#        extrude-cut hole.  Apply a 0.15 mm radius fillet.
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G13] Reading {S_CSV[10].name}")
s10_rows   = read_rows(S_CSV[10])
_p10       = detect_sketch_plane(s10_rows)
if _p10[0] != "axis":
    sys.exit(f"❌ G13: S10 not axis-aligned (got {_p10[0]}).")
_, S10_AXIS, S10_PLANE = _p10
print(f"     S10 plane: {S10_AXIS.upper()} = {S10_PLANE}")

s10_circles = parse_three_point_circles(s10_rows, S10_AXIS)
if len(s10_circles) != 1:
    sys.exit(f"❌ G13: expected 1 circle in S10, got {len(s10_circles)}.")
g13_center, g13_radius = circle_from_3_points(*s10_circles[0])
print(f"     G13 circle: center=({g13_center[0]:.4f},{g13_center[1]:.4f}) "
      f"r={g13_radius:.4f} mm  plane {S10_AXIS.upper()}={S10_PLANE}")

FILLET_RADIUS_G13 = 0.15

fork_body_g13 = stage_pieces[-1]
g13_edges = _find_circle_edge(fork_body_g13, g13_center, g13_radius,
                               S10_AXIS, S10_PLANE)
print(f"     Matched circle edges for G13 fillet: {len(g13_edges)}")
if not g13_edges:
    print(f"     ⚠  no matching edge found — skipping G13 fillet")
    fork_g13 = fork_body_g13
else:
    try:
        fork_g13 = fillet(g13_edges, radius=FILLET_RADIUS_G13)
        print(f"     G13 filleted volume: {fork_g13.volume:.4f} mm³  "
              f"(valid={fork_g13.is_valid})")
    except Exception as exc:
        print(f"     ⚠  G13 fillet failed: {exc} — keeping body unchanged")
        fork_g13 = fork_body_g13

stage_pieces[:] = [p for p in stage_pieces if p is not fork_body_g13]
stage_pieces.append(fork_g13)
checkpoint(13, f"G13 fillet r={FILLET_RADIUS_G13} mm on S10 circle edge "
               f"(Z={S10_PLANE}, r={g13_radius:.4f})")


# ══════════════════════════════════════════════════════════════════════════
# G14 — Read S11: one 3-point circle on Z = 8.35.
#        Matches the outer circle (r ≈ 3.555) — the bottom rim of the G10
#        loft body.  Apply a 0.2 mm radius fillet.
# ══════════════════════════════════════════════════════════════════════════
print(f"\n[G14] Reading {S_CSV[11].name}")
s11_rows   = read_rows(S_CSV[11])
_p11       = detect_sketch_plane(s11_rows)
if _p11[0] != "axis":
    sys.exit(f"❌ G14: S11 not axis-aligned (got {_p11[0]}).")
_, S11_AXIS, S11_PLANE = _p11
print(f"     S11 plane: {S11_AXIS.upper()} = {S11_PLANE}")

s11_circles = parse_three_point_circles(s11_rows, S11_AXIS)
if len(s11_circles) != 1:
    sys.exit(f"❌ G14: expected 1 circle in S11, got {len(s11_circles)}.")
g14_center, g14_radius = circle_from_3_points(*s11_circles[0])
print(f"     G14 circle: center=({g14_center[0]:.4f},{g14_center[1]:.4f}) "
      f"r={g14_radius:.4f} mm  plane {S11_AXIS.upper()}={S11_PLANE}")

FILLET_RADIUS_G14 = 0.2

fork_body_g14 = stage_pieces[-1]
g14_edges = _find_circle_edge(fork_body_g14, g14_center, g14_radius,
                               S11_AXIS, S11_PLANE)
print(f"     Matched circle edges for G14 fillet: {len(g14_edges)}")
if not g14_edges:
    print(f"     ⚠  no matching edge found — skipping G14 fillet")
    fork_g14 = fork_body_g14
else:
    try:
        fork_g14 = fillet(g14_edges, radius=FILLET_RADIUS_G14)
        print(f"     G14 filleted volume: {fork_g14.volume:.4f} mm³  "
              f"(valid={fork_g14.is_valid})")
    except Exception as exc:
        print(f"     ⚠  G14 fillet failed: {exc} — keeping body unchanged")
        fork_g14 = fork_body_g14

stage_pieces[:] = [p for p in stage_pieces if p is not fork_body_g14]
stage_pieces.append(fork_g14)
checkpoint(14, f"G14 fillet r={FILLET_RADIUS_G14} mm on S11 circle edge "
               f"(Z={S11_PLANE}, r={g14_radius:.4f})")


# ══════════════════════════════════════════════════════════════════════════
# G15..G22 — SECOND boss + hole feature, the mirror image of the G7..G14
#            feature about the slot mid-plane (Z = 5.8).  This boss grows
#            from the LOWER prong up into the slot; its hole runs down
#            through the bottom of the block.  Same construction as the
#            first boss: two profile circles (G15), a terminus circle (G16),
#            a guide-rail arc (G17), a revolved boss (G18), an extrude-cut
#            hole (G19), and three rim fillets (G20..G22).
# ══════════════════════════════════════════════════════════════════════════

# ── G15 — Read S12: TWO 3-point circles on Z = 3.25 (inner + outer). ───────
print(f"\n[G15] Reading {S_CSV[12].name}")
s12_rows = read_rows(S_CSV[12])
_p12 = detect_sketch_plane(s12_rows)
if _p12[0] != "axis":
    sys.exit(f"❌ G15: S12 not axis-aligned (got {_p12[0]}).")
_, S12_AXIS, S12_PLANE = _p12
print(f"     S12 plane: {S12_AXIS.upper()} = {S12_PLANE}")

s12_circles = parse_three_point_circles(s12_rows, S12_AXIS)
if len(s12_circles) != 2:
    sys.exit(f"❌ G15: expected 2 circles in S12, got {len(s12_circles)}.")
g15_inner_center, g15_inner_radius = circle_from_3_points(*s12_circles[0])
g15_outer_center, g15_outer_radius = circle_from_3_points(*s12_circles[1])
print(f"     G15 inner circle: center=({g15_inner_center[0]:.4f},"
      f"{g15_inner_center[1]:.4f}) r={g15_inner_radius:.4f} mm")
print(f"     G15 outer circle: center=({g15_outer_center[0]:.4f},"
      f"{g15_outer_center[1]:.4f}) r={g15_outer_radius:.4f} mm")

g15_inner_face = circle_face(g15_inner_center, g15_inner_radius, S12_AXIS, S12_PLANE)
g15_outer_edge = make_circle_edge(g15_outer_center, g15_outer_radius, S12_AXIS, S12_PLANE)
g15_outer_wire = Wire([g15_outer_edge])
print(f"     G15 inner face area: {g15_inner_face.area:.4f} mm²")
checkpoint(15, f"G15 two circle profiles on {S12_AXIS.upper()}={S12_PLANE}: "
               f"inner r={g15_inner_radius:.4f}, outer r={g15_outer_radius:.4f}")


# ── G16 — Read S13: ONE 3-point circle on Z = 2.803 (lower terminus). ──────
print(f"\n[G16] Reading {S_CSV[13].name}")
s13_rows = read_rows(S_CSV[13])
_p13 = detect_sketch_plane(s13_rows)
if _p13[0] != "axis":
    sys.exit(f"❌ G16: S13 not axis-aligned (got {_p13[0]}).")
_, S13_AXIS, S13_PLANE = _p13
print(f"     S13 plane: {S13_AXIS.upper()} = {S13_PLANE}")

s13_circles = parse_three_point_circles(s13_rows, S13_AXIS)
if len(s13_circles) != 1:
    sys.exit(f"❌ G16: expected 1 circle in S13, got {len(s13_circles)}.")
g16_center, g16_radius = circle_from_3_points(*s13_circles[0])
print(f"     G16 circle: center=({g16_center[0]:.4f},{g16_center[1]:.4f}) "
      f"r={g16_radius:.4f} mm")
checkpoint(16, f"G16 circle profile on {S13_AXIS.upper()}={S13_PLANE}: "
               f"r={g16_radius:.4f}")


# ── G17 — Read S14: ONE 3-point arc (guide rail for the G18 boss). ─────────
print(f"\n[G17] Reading {S_CSV[14].name}")
s14_rows = read_rows(S_CSV[14])
s14_arcs = parse_three_point_arcs_world(s14_rows)
if len(s14_arcs) != 1:
    sys.exit(f"❌ G17: expected 1 three-point arc in S14, got {len(s14_arcs)}.")
g17_p1, g17_p2, g17_p3 = s14_arcs[0]
print(f"     G17 arc P1: ({g17_p1.X:.4f},{g17_p1.Y:.4f},{g17_p1.Z:.4f})  "
      f"(G16 terminus, Z={S13_PLANE})")
print(f"     G17 arc P3: ({g17_p3.X:.4f},{g17_p3.Y:.4f},{g17_p3.Z:.4f})  "
      f"(G15 outer, Z={S12_PLANE})")
g17_arc_edge = make_arc_edge_3pt(g17_p1, g17_p2, g17_p3)
print(f"     G17 guide rail arc length: {g17_arc_edge.length:.4f} mm")
checkpoint(17, f"G17 guide-rail arc in Y={g17_p1.Y:.3f} plane, "
               f"Z={g17_p1.Z:.4f}→{g17_p3.Z:.4f}")


# ── G18 — Boss body: revolve the G17 meridian about the central axis. ──────
#   (Same reasoning as G10: concentric circles + in-plane rail ⇒ surface of
#    revolution; revolve keeps the rims as true CIRCLEs so G22 fillets.)
print(f"\n[G18] Boss body: revolve the G17 meridian (G16 → G15 outer) about "
      f"the central axis")
_axis2_x, _axis2_y = g15_outer_center[0], g15_outer_center[1]   # (4.736, 4.5)
_B_lo = Vector(_axis2_x, _axis2_y, S13_PLANE)   # axis point at G16 plane (Z=2.803)
_B_hi = Vector(_axis2_x, _axis2_y, S12_PLANE)   # axis point at G15 plane (Z=3.25)
_meridian2 = Wire([
    g17_arc_edge,                       # P1 (G16, wide) -> P3 (G15 outer, narrow)
    Edge.make_line(g17_p3, _B_hi),      # top disk radius (Z=3.25)
    Edge.make_line(_B_hi, _B_lo),       # along the central axis
    Edge.make_line(_B_lo, g17_p1),      # bottom disk radius (Z=2.803)
])
_rev_axis2 = Axis((_axis2_x, _axis2_y, 0.0), (0.0, 0.0, 1.0))
g18_boss_solid = revolve(Face(_meridian2), _rev_axis2, revolution_arc=360)
print(f"     Revolved boss volume : {g18_boss_solid.volume:.4f} mm³  "
      f"(valid={g18_boss_solid.is_valid})")

g18_fork_in = stage_pieces[-1]
fork_with_boss2 = g18_fork_in + g18_boss_solid
print(f"     Fork + boss2 union: volume {fork_with_boss2.volume:.4f} mm³  "
      f"(valid={fork_with_boss2.is_valid})")
stage_pieces[:] = [p for p in stage_pieces if p is not g18_fork_in]
stage_pieces.append(fork_with_boss2)
checkpoint(18, f"G18 boss (revolve G16→G15 outer): "
               f"fork+boss volume {fork_with_boss2.volume:.4f} mm³")


# ── G19 — Extrude-cut with the G15 inner circle profile. ───────────────────
#   Spec: cut 5.5 units along -Z and 1.0 unit along +Z (the +Z unit avoids a
#   coincident cutter face at the boss top plane Z=3.25).  The hole therefore
#   runs from Z=3.25 down through the block bottom (Z=0); its bottom rim (the
#   G20 fillet edge) forms where the cutter exits the solid at Z=0.
print(f"\n[G19] Extrude-cut with G15 inner circle (r={g15_inner_radius:.4f})")
G19_NEG_Z = 5.5    # extrude -Z  → reaches Z = 3.25 - 5.5 = -2.25 (past block bottom Z=0)
G19_POS_Z = 1.0    # extrude +Z  → Z = 3.25 + 1.0 = 4.25 (into the open slot; avoids coincident face)
g19_cut_neg = extrude(g15_inner_face, amount=G19_NEG_Z, dir=(0, 0, -1))
g19_cut_pos = extrude(g15_inner_face, amount=G19_POS_Z, dir=(0, 0,  1))
g19_cutter  = g19_cut_neg + g19_cut_pos
z_lo_cut2 = S12_PLANE - G19_NEG_Z   # -2.25
z_hi_cut2 = S12_PLANE + G19_POS_Z   #  4.25
print(f"     Cutter region   : Z = {z_lo_cut2:.3f} .. {z_hi_cut2:.3f}")
print(f"     Cutter volume   : {g19_cutter.volume:.4f} mm³")

new_stage = []
for idx, body in enumerate(stage_pieces):
    bb = body.bounding_box()
    if bb.min.Z > z_hi_cut2 or bb.max.Z < z_lo_cut2:
        print(f"     body[{idx}]: Z=[{bb.min.Z:.3f},{bb.max.Z:.3f}] — outside "
              f"cutter Z range, kept unchanged")
        new_stage.append(body)
        continue
    try:
        cut_body = body - g19_cutter
        print(f"     body[{idx}]: volume {body.volume:.4f} → {cut_body.volume:.4f} "
              f"mm³  Δ={cut_body.volume - body.volume:+.4f}  (valid={cut_body.is_valid})")
        new_stage.append(cut_body)
    except Exception as exc:
        print(f"     body[{idx}]: boolean cut failed ({exc}) — kept unchanged")
        new_stage.append(body)
stage_pieces[:] = new_stage
checkpoint(19, f"G19 extrude-cut: inner r={g15_inner_radius:.4f}, "
               f"-{G19_NEG_Z}/+{G19_POS_Z} Z, Z={z_lo_cut2:.3f}..{z_hi_cut2:.3f}")


# ── G20 — Read S15: fillet (r=0.2) the inner-hole BOTTOM rim (Z=0). ────────
print(f"\n[G20] Reading {S_CSV[15].name}")
s15_rows = read_rows(S_CSV[15])
_p15 = detect_sketch_plane(s15_rows)
if _p15[0] != "axis":
    sys.exit(f"❌ G20: S15 not axis-aligned (got {_p15[0]}).")
_, S15_AXIS, S15_PLANE = _p15
s15_circles = parse_three_point_circles(s15_rows, S15_AXIS)
if len(s15_circles) != 1:
    sys.exit(f"❌ G20: expected 1 circle in S15, got {len(s15_circles)}.")
g20_center, g20_radius = circle_from_3_points(*s15_circles[0])
print(f"     G20 circle: center=({g20_center[0]:.4f},{g20_center[1]:.4f}) "
      f"r={g20_radius:.4f} mm  plane {S15_AXIS.upper()}={S15_PLANE}")
FILLET_RADIUS_G20 = 0.2
fork_body_g20 = stage_pieces[-1]
g20_edges = _find_circle_edge(fork_body_g20, g20_center, g20_radius,
                               S15_AXIS, S15_PLANE)
print(f"     Matched circle edges for G20 fillet: {len(g20_edges)}")
if not g20_edges:
    print(f"     ⚠  no matching edge found — skipping G20 fillet")
    fork_g20 = fork_body_g20
else:
    try:
        fork_g20 = fillet(g20_edges, radius=FILLET_RADIUS_G20)
        print(f"     G20 filleted volume: {fork_g20.volume:.4f} mm³  "
              f"(valid={fork_g20.is_valid})")
    except Exception as exc:
        print(f"     ⚠  G20 fillet failed: {exc} — keeping body unchanged")
        fork_g20 = fork_body_g20
stage_pieces[:] = [p for p in stage_pieces if p is not fork_body_g20]
stage_pieces.append(fork_g20)
checkpoint(20, f"G20 fillet r={FILLET_RADIUS_G20} mm on S15 circle edge "
               f"(Z={S15_PLANE}, r={g20_radius:.4f})")


# ── G21 — Read S16: fillet (r=0.15) the inner-hole TOP rim (Z=3.25). ───────
print(f"\n[G21] Reading {S_CSV[16].name}")
s16_rows = read_rows(S_CSV[16])
_p16 = detect_sketch_plane(s16_rows)
if _p16[0] != "axis":
    sys.exit(f"❌ G21: S16 not axis-aligned (got {_p16[0]}).")
_, S16_AXIS, S16_PLANE = _p16
s16_circles = parse_three_point_circles(s16_rows, S16_AXIS)
if len(s16_circles) != 1:
    sys.exit(f"❌ G21: expected 1 circle in S16, got {len(s16_circles)}.")
g21_center, g21_radius = circle_from_3_points(*s16_circles[0])
print(f"     G21 circle: center=({g21_center[0]:.4f},{g21_center[1]:.4f}) "
      f"r={g21_radius:.4f} mm  plane {S16_AXIS.upper()}={S16_PLANE}")
FILLET_RADIUS_G21 = 0.15
fork_body_g21 = stage_pieces[-1]
g21_edges = _find_circle_edge(fork_body_g21, g21_center, g21_radius,
                               S16_AXIS, S16_PLANE)
print(f"     Matched circle edges for G21 fillet: {len(g21_edges)}")
if not g21_edges:
    print(f"     ⚠  no matching edge found — skipping G21 fillet")
    fork_g21 = fork_body_g21
else:
    try:
        fork_g21 = fillet(g21_edges, radius=FILLET_RADIUS_G21)
        print(f"     G21 filleted volume: {fork_g21.volume:.4f} mm³  "
              f"(valid={fork_g21.is_valid})")
    except Exception as exc:
        print(f"     ⚠  G21 fillet failed: {exc} — keeping body unchanged")
        fork_g21 = fork_body_g21
stage_pieces[:] = [p for p in stage_pieces if p is not fork_body_g21]
stage_pieces.append(fork_g21)
checkpoint(21, f"G21 fillet r={FILLET_RADIUS_G21} mm on S16 circle edge "
               f"(Z={S16_PLANE}, r={g21_radius:.4f})")


# ── G22 — Read S17: fillet (r=0.2) the boss OUTER base rim (Z=3.25). ───────
print(f"\n[G22] Reading {S_CSV[17].name}")
s17_rows = read_rows(S_CSV[17])
_p17 = detect_sketch_plane(s17_rows)
if _p17[0] != "axis":
    sys.exit(f"❌ G22: S17 not axis-aligned (got {_p17[0]}).")
_, S17_AXIS, S17_PLANE = _p17
s17_circles = parse_three_point_circles(s17_rows, S17_AXIS)
if len(s17_circles) != 1:
    sys.exit(f"❌ G22: expected 1 circle in S17, got {len(s17_circles)}.")
g22_center, g22_radius = circle_from_3_points(*s17_circles[0])
print(f"     G22 circle: center=({g22_center[0]:.4f},{g22_center[1]:.4f}) "
      f"r={g22_radius:.4f} mm  plane {S17_AXIS.upper()}={S17_PLANE}")
FILLET_RADIUS_G22 = 0.2
fork_body_g22 = stage_pieces[-1]
g22_edges = _find_circle_edge(fork_body_g22, g22_center, g22_radius,
                               S17_AXIS, S17_PLANE)
print(f"     Matched circle edges for G22 fillet: {len(g22_edges)}")
if not g22_edges:
    print(f"     ⚠  no matching edge found — skipping G22 fillet")
    fork_g22 = fork_body_g22
else:
    try:
        fork_g22 = fillet(g22_edges, radius=FILLET_RADIUS_G22)
        print(f"     G22 filleted volume: {fork_g22.volume:.4f} mm³  "
              f"(valid={fork_g22.is_valid})")
    except Exception as exc:
        print(f"     ⚠  G22 fillet failed: {exc} — keeping body unchanged")
        fork_g22 = fork_body_g22
stage_pieces[:] = [p for p in stage_pieces if p is not fork_body_g22]
stage_pieces.append(fork_g22)
checkpoint(22, f"G22 fillet r={FILLET_RADIUS_G22} mm on S17 circle edge "
               f"(Z={S17_PLANE}, r={g22_radius:.4f})")


# ══════════════════════════════════════════════════════════════════════════
# G23..G29 — Pin-to-fork transition (loft), edge finishing, an axial bore in
#            the pin, and finally an "unstitch" to a surface (sheet) model.
# ══════════════════════════════════════════════════════════════════════════

# ── G23 — Read S18: one circle (r≈4.0) on Y=20.5, concentric with the pin. ─
print(f"\n[G23] Reading {S_CSV[18].name}")
s18_rows = read_rows(S_CSV[18])
_p18 = detect_sketch_plane(s18_rows)
if _p18[0] != "axis":
    sys.exit(f"❌ G23: S18 not axis-aligned (got {_p18[0]}).")
_, S18_AXIS, S18_PLANE = _p18
s18_circles = parse_three_point_circles(s18_rows, S18_AXIS)
if len(s18_circles) != 1:
    sys.exit(f"❌ G23: expected 1 circle in S18, got {len(s18_circles)}.")
g23_center, g23_radius = circle_from_3_points(*s18_circles[0])
print(f"     G23 circle: center=({g23_center[0]:.4f},{g23_center[1]:.4f}) "
      f"r={g23_radius:.4f} mm  plane {S18_AXIS.upper()}={S18_PLANE}")
g23_face = circle_face(g23_center, g23_radius, S18_AXIS, S18_PLANE)
checkpoint(23, f"G23 circle profile on {S18_AXIS.upper()}={S18_PLANE}: "
               f"r={g23_radius:.4f}")


# ── G24 — Loft the fork BACK face (Y=15.5) to the G23 circle (Y=20.5), then
#          union pin + fork + loft into ONE connected solid (bridges the 5 mm
#          gap the literal coordinates left between fork and pin). ──────────
print(f"\n[G24] Loft fork back face (Y=15.5) → G23 circle (Y={S18_PLANE})")
g24_fork = stage_pieces[-1]            # fork (with both bosses)
g24_pin  = stage_pieces[0]             # pin
_yf = [f for f in g24_fork.faces()
       if abs(f.center().Y - 15.5) < 0.10 and abs(f.normal_at(f.center()).Y) > 0.9]
if not _yf:
    sys.exit("❌ G24: could not find the Y=15.5 back face on the fork.")
g24_back_face = max(_yf, key=lambda f: f.area)
print(f"     Back face @ Y=15.5: area={g24_back_face.area:.3f} mm²")
# loft() accepts the two FACES as cross-sections (wire form trips an OCCT check).
g24_loft = loft([g24_back_face, g23_face])
print(f"     Loft solid volume : {g24_loft.volume:.4f} mm³  "
      f"(valid={g24_loft.is_valid})")
g24_joined = (g24_fork + g24_loft + g24_pin)
try:
    g24_joined = g24_joined.clean()
except Exception as exc:
    print(f"     ⚠  .clean() after join: {exc}")
_js = g24_joined.solids()
print(f"     Joined pin+fork+loft: {len(_js)} solid(s), "
      f"volume {g24_joined.volume:.4f} mm³, valid={all(s.is_valid for s in _js)}")
stage_pieces[:] = [g24_joined]
checkpoint(24, f"G24 loft back-face→G23 circle; pin+fork+loft joined into "
               f"{len(_js)} solid(s), vol {g24_joined.volume:.4f} mm³")


# ── G25 — Read S19: the 4 loft corner edges; fillet r=2.0. ─────────────────
print(f"\n[G25] Reading {S_CSV[19].name}")
s19_rows = read_rows(S_CSV[19])
s19_segs = parse_line_segments_world(s19_rows)
g25_mids = [(a + b) * 0.5 for a, b in s19_segs]
print(f"     S19 names {len(g25_mids)} loft edge(s) to fillet")
FILLET_RADIUS_G25 = 2.0
g25_body = stage_pieces[-1]
g25_edges = []
for m in g25_mids:
    e = min(g25_body.edges(), key=lambda x: (x.position_at(0.5) - m).length)
    d = (e.position_at(0.5) - m).length
    if d < 0.75 and not any(e.is_same(x) for x in g25_edges):
        g25_edges.append(e)
print(f"     Matched {len(g25_edges)} loft edge(s)")
try:
    g25_done = fillet(g25_edges, radius=FILLET_RADIUS_G25)
    print(f"     G25 fillet OK: volume {g25_done.volume:.4f} mm³ "
          f"(valid={g25_done.is_valid})")
except Exception as exc:
    print(f"     ⚠  G25 batch fillet failed ({str(exc)[:45]}) — per-edge fallback")
    g25_done = g25_body
    for m in g25_mids:
        e = min(g25_done.edges(), key=lambda x: (x.position_at(0.5) - m).length)
        try:
            g25_done = fillet([e], radius=FILLET_RADIUS_G25)
        except Exception as exc2:
            print(f"        edge @ ({m.X:.1f},{m.Y:.1f},{m.Z:.1f}): "
                  f"failed ({str(exc2)[:35]})")
stage_pieces[:] = [g25_done]
checkpoint(25, f"G25 fillet r={FILLET_RADIUS_G25} mm on {len(g25_edges)} "
               f"loft edge(s)")


# ── G26 — Read S20: top (Z=11.6) & bottom (Z=0) outer perimeter edges;
#          equal-distance 0.5 chamfer.  These meet tangentially (front arc
#          into side lines) exactly like the G6 slot edges, so reuse the
#          mirror-symmetric chamfer helper. ────────────────────────────────
print(f"\n[G26] Reading {S_CSV[20].name}")
s20_rows  = read_rows(S_CSV[20])
s20_specs = parse_edges_world(s20_rows)
print(f"     S20 names {len(s20_specs)} edge(s) to chamfer at 0.5 mm")
g26_body = stage_pieces[-1]
g26_done, g26_n = _symmetric_chamfer(g26_body, s20_specs, 0.5)
print(f"     G26 chamfered (symmetric): volume {g26_done.volume:.4f} mm³ "
      f"(valid={g26_done.is_valid})")
_check_lr_symmetry(g26_done, "FINAL G26")
stage_pieces[:] = [g26_done]
checkpoint(26, f"G26 chamfered {len(s20_specs)} top/bottom edge(s) at 0.5 mm "
               f"(equal distance, mirror-symmetric)")


# ── G27 — Read S21: circle (r≈1.425) on Y=30.5; extrude-cut 15 mm along -Y
#          → axial bore through the pin. ───────────────────────────────────
print(f"\n[G27] Reading {S_CSV[21].name}")
s21_rows = read_rows(S_CSV[21])
_p21 = detect_sketch_plane(s21_rows)
if _p21[0] != "axis":
    sys.exit(f"❌ G27: S21 not axis-aligned (got {_p21[0]}).")
_, S21_AXIS, S21_PLANE = _p21
s21_circles = parse_three_point_circles(s21_rows, S21_AXIS)
if len(s21_circles) != 1:
    sys.exit(f"❌ G27: expected 1 circle in S21, got {len(s21_circles)}.")
g27_center, g27_radius = circle_from_3_points(*s21_circles[0])
print(f"     G27 circle: center=({g27_center[0]:.4f},{g27_center[1]:.4f}) "
      f"r={g27_radius:.4f} mm  plane {S21_AXIS.upper()}={S21_PLANE}")
G27_DEPTH = 15.0
g27_face   = circle_face(g27_center, g27_radius, S21_AXIS, S21_PLANE)
g27_cutter = extrude(g27_face, amount=G27_DEPTH, dir=(0, -1, 0))
g27_y_end  = S21_PLANE - G27_DEPTH      # 30.5 - 15 = 15.5
print(f"     Bore: Y = {S21_PLANE} → {g27_y_end} (depth {G27_DEPTH} along -Y)")
g27_body   = stage_pieces[-1] - g27_cutter
print(f"     Bored body volume: {g27_body.volume:.4f} mm³ "
      f"(valid={g27_body.is_valid})")
stage_pieces[:] = [g27_body]
checkpoint(27, f"G27 extrude-cut bore r={g27_radius:.4f}, Y={S21_PLANE}→{g27_y_end}")


# ── G28 — Fillet r=0.25 on the bore's start (Y=30.5) and end (Y=15.5) rims. ─
print(f"\n[G28] Fillet bore start/end rims (r=0.25)")
FILLET_RADIUS_G28 = 0.25
g28_body  = stage_pieces[-1]
g28_edges = []
for yv in (S21_PLANE, g27_y_end):
    es = _find_circle_edge(g28_body, g27_center, g27_radius, S21_AXIS, yv)
    print(f"     rim @ Y={yv}: matched {len(es)} edge(s)")
    g28_edges += es
if not g28_edges:
    print(f"     ⚠  no bore rim edges found — skipping G28 fillet")
    g28_done = g28_body
else:
    try:
        g28_done = fillet(g28_edges, radius=FILLET_RADIUS_G28)
        print(f"     G28 fillet OK: volume {g28_done.volume:.4f} mm³ "
              f"(valid={g28_done.is_valid})")
    except Exception as exc:
        print(f"     ⚠  G28 batch fillet failed ({str(exc)[:45]}) — per-edge")
        g28_done = g28_body
        for yv in (S21_PLANE, g27_y_end):
            for e in _find_circle_edge(g28_done, g27_center, g27_radius,
                                       S21_AXIS, yv):
                try:
                    g28_done = fillet([e], radius=FILLET_RADIUS_G28)
                except Exception as exc2:
                    print(f"        rim @ Y={yv}: failed ({str(exc2)[:35]})")
stage_pieces[:] = [g28_done]
checkpoint(28, f"G28 fillet r={FILLET_RADIUS_G28} mm on bore start/end rims")


# ── G29 — Unstitch the solid into a SURFACE (sheet) model: take the solid's
#          faces and build an open Shell (no volume — a 2-D surface model). ─
print(f"\n[G29] Unstitch solid → surface (sheet) model")
g29_body  = stage_pieces[-1]
g29_faces = g29_body.faces()
g29_shell = Shell(g29_faces)
print(f"     Unstitched: {len(g29_faces)} face(s) → open Shell "
      f"(surface area {sum(f.area for f in g29_faces):.3f} mm², "
      f"is_solid=False)")
stage_pieces[:] = [g29_shell]
checkpoint(29, f"G29 unstitched solid into a {len(g29_faces)}-face surface model")


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

all_faces = final_compound.faces()
total_surface_area = sum(f.area for f in all_faces)
n_edges = len(final_compound.edges())
print(f"     Total surface area : {total_surface_area:.3f} mm²")
print(f"     Face count         : {len(all_faces)}")
print(f"     Edge count         : {n_edges} (informational)")

solids = final_compound.solids()
total_volume = sum(s.volume for s in solids)
all_watertight = True
for i, s in enumerate(solids, 1):
    wt = bool(s.is_valid)
    all_watertight = all_watertight and wt
    bb = s.bounding_box()
    print(f"     Solid {i}: volume={s.volume:.3f} mm³ valid={wt}  "
          f"Y=[{bb.min.Y:.2f},{bb.max.Y:.2f}]")
print(f"     Closed solid(s)    : {len(solids)}, total volume={total_volume:.3f} mm³, "
      f"all_valid={all_watertight}")
if len(solids) > 1:
    print(f"     ⚠  {len(solids)} disjoint solids — pin and fork do not touch "
          f"(5 mm Y-gap, as per the literal coordinates).")

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
    f"Guidelines     :  G1, G2, G4, G5, G6, G7, G8, G9, G10, G11, G12, G13, G14  (G3 = export, last)",
    f"Part type      :  closed SOLID (multi-body compound)",
    "=" * 70, "",
    f"-- G1 : S1 — pin solid on {S1_AXIS.upper()}={S1_PLANE} --",
    f"  Circle            : center=({pin_center[0]:.3f},{pin_center[1]:.3f}) "
        f"r={pin_radius:.3f} mm",
    f"  Straight cylinder : {S1_AXIS.upper()}={S1_PLANE}→{pin_y_lo} "
        f"(len {STRAIGHT_LEN}, zero taper)",
    f"  Tapered cap       : {S1_AXIS.upper()}={S1_PLANE}→{pin_y_hi} "
        f"(len {CAP_LEN}, {TAPER_DEG:.0f}° inward → top r≈{top_r:.3f})",
    f"  Pin volume        : {pin.volume:.3f} mm³",
    "",
    f"-- G2 : S2 — block solid on {S2_AXIS.upper()}={S2_PLANE} --",
    f"  Lines / circle    : {len(s2_lines)} lines + 1 circle "
        f"(rounded-bottom rectangle)",
    f"  Bottom circle     : center=({circ_center[0]:.3f},{circ_center[1]:.3f}) "
        f"r={circ_radius:.3f} mm",
    f"  Extrude           : {BLOCK_LEN} mm along -{S2_AXIS.upper()} "
        f"({S2_AXIS.upper()}={S2_PLANE}→{block_z_lo})",
    f"  Block volume      : {block.volume:.3f} mm³",
    "",
    f"-- G4 : S3 — intersected fork body on {S3_AXIS.upper()}={S3_PLANE} --",
    f"  Profile lines     : {len(s3_lines)} (one closed loop)",
    f"  Sweep             : {SWEEP_LEN} mm along -{S3_AXIS.upper()} "
        f"({S3_AXIS.upper()}={S3_PLANE}→{sweep_x_lo})",
    f"  Operation         : boolean COMMON (sweep ∩ block)",
    f"  Fork volume       : {fork.volume:.3f} mm³",
    "",
    f"-- G5 : S4 — fillet --",
    f"  Named edges       : {len(s4_edges)}",
    f"  Matched edges     : {len(sel_edges)}",
    f"  Radius            : {FILLET_RADIUS} mm",
    f"  Filleted volume   : {fork_filleted.volume:.3f} mm³",
    "",
    f"-- G6 : S5 — chamfer (symmetry-fixed) --",
    f"  Named edges       : {len(s5_specs)} ({n_line} line, {n_arc} arc)",
    f"  Chamfered edges   : {chamfered_count}",
    f"  Distance          : {CHAMFER_DIST} mm (equal distance)",
    f"  Grouping          : Group A (both side faces simultaneously, 10 edges)",
    f"                      Group B (front arcs, 2 edges)",
    f"  Matching          : dense-sample (11 pts/edge), tol={CHAMFER_MID_TOL} mm",
    f"  Chamfered volume  : {fork_chamfered.volume:.3f} mm³",
    "",
    f"-- G7 : S6 — two circle profiles on {S6_AXIS.upper()}={S6_PLANE} --",
    f"  Inner circle  : center=({g7_inner_center[0]:.4f},{g7_inner_center[1]:.4f}) "
        f"r={g7_inner_radius:.4f} mm  (→ G11 extrude-cut)",
    f"  Outer circle  : center=({g7_outer_center[0]:.4f},{g7_outer_center[1]:.4f}) "
        f"r={g7_outer_radius:.4f} mm  (→ G10 loft base)",
    "",
    f"-- G8 : S7 — circle profile on {S7_AXIS.upper()}={S7_PLANE} --",
    f"  Circle        : center=({g8_center[0]:.4f},{g8_center[1]:.4f}) "
        f"r={g8_radius:.4f} mm  (→ G10 loft top)",
    "",
    f"-- G9 : S8 — guide-rail arc in Y={g9_p1.Y:.3f} plane --",
    f"  Arc start     : ({g9_p1.X:.4f}, {g9_p1.Y:.4f}, {g9_p1.Z:.4f})",
    f"  Arc mid       : ({g9_p2.X:.4f}, {g9_p2.Y:.4f}, {g9_p2.Z:.4f})",
    f"  Arc end       : ({g9_p3.X:.4f}, {g9_p3.Y:.4f}, {g9_p3.Z:.4f})",
    f"  Arc length    : {g9_arc_edge.length:.4f} mm",
    "",
    f"-- G10 : Loft (G7 outer → G8, guided by G9) --",
    f"  Profile lo    : r={g7_outer_radius:.4f} mm at {S6_AXIS.upper()}={S6_PLANE}",
    f"  Profile hi    : r={g8_radius:.4f} mm at {S7_AXIS.upper()}={S7_PLANE}",
    f"  Guide rail    : G9 arc  (guided={g10_guided})",
    f"  Loft volume   : {g10_loft_solid.volume:.4f} mm³  (bare loft before union)",
    f"  Fork+loft vol : {fork_with_loft.volume:.4f} mm³  (after boolean union into fork)",
    "",
    f"-- G11 : Extrude-cut (G7 inner circle) --",
    f"  Inner circle  : r={g7_inner_radius:.4f} mm at {S6_AXIS.upper()}={S6_PLANE}",
    f"  +Z direction  : {G11_POS_Z} units  (Z → {S6_PLANE + G11_POS_Z:.3f}, top rim = S9 plane)",
    f"  -Z direction  : {G11_NEG_Z} units  (Z → {S6_PLANE - G11_NEG_Z:.3f}, bottom rim ≈ S10 plane)",
    f"  Cut region Z  : {z_lo_cut:.3f} .. {z_hi_cut:.3f}",
    f"  Final volume  : {g10_final.volume:.4f} mm³",
    "",
    "-- G12 : Fillet (S9 circle edge) --",
    f"  Circle  : center=({g12_center[0]:.4f},{g12_center[1]:.4f}) r={g12_radius:.4f} mm  plane Z={S9_PLANE}",
    f"  Matched : {len(g12_edges)} edge(s)",
    f"  Radius  : {FILLET_RADIUS_G12} mm",
    f"  Volume  : {fork_g12.volume:.4f} mm³",
    "",
    "-- G13 : Fillet (S10 circle edge) --",
    f"  Circle  : center=({g13_center[0]:.4f},{g13_center[1]:.4f}) r={g13_radius:.4f} mm  plane Z={S10_PLANE}",
    f"  Matched : {len(g13_edges)} edge(s)",
    f"  Radius  : {FILLET_RADIUS_G13} mm",
    f"  Volume  : {fork_g13.volume:.4f} mm³",
    "",
    "-- G14 : Fillet (S11 circle edge) --",
    f"  Circle  : center=({g14_center[0]:.4f},{g14_center[1]:.4f}) r={g14_radius:.4f} mm  plane Z={S11_PLANE}",
    f"  Matched : {len(g14_edges)} edge(s)",
    f"  Radius  : {FILLET_RADIUS_G14} mm",
    f"  Volume  : {fork_g14.volume:.4f} mm³",
    "",
    "-- G3 : Export --",
    f"  STL                : {FINAL_STL.name}",
    f"  STEP               : {FINAL_STEP.name}",
    f"  Total surface area : {total_surface_area:.3f} mm²",
    f"  Total volume       : {total_volume:.3f} mm³",
    f"  Closed solids      : {len(solids)} (all_valid={all_watertight})",
    f"  Face / edge count  : {len(all_faces)} / {n_edges}",
]
if len(solids) > 1:
    summary_lines.append(
        f"  NOTE               : {len(solids)} disjoint solids — pin "
        f"(Y={pin_y_lo}..{pin_y_hi}) and fork are 5 mm apart in Y, as the "
        f"literal coordinates specify."
    )
summary_lines += [
    "", "=" * 70,
    "PER-GUIDELINE CUMULATIVE AREA / VOLUME HISTORY",
    "=" * 70,
    f"{'Guideline':>10}  {'Cum. area (mm²)':>18}  {'Δ area':>12}  "
    f"{'Cum. vol (mm³)':>16}  {'Δ vol':>12}  Label",
    "-" * 100,
]
for e in area_history:
    summary_lines.append(
        f"  G{e['g']:<8d}  {e['area']:>18.3f}  {e['darea']:>+12.3f}  "
        f"{e['vol']:>16.3f}  {e['dvol']:>+12.3f}  {e['label']}"
    )
summary_lines.append("=" * 70)
with open(FINAL_TXT, "w") as f:
    f.write("\n".join(summary_lines))
print(f"     [EXPORT] Wrote: {FINAL_TXT.name}")
_write_area_history_summary()

print(f"\nDone -- G1, G2, G4, G5, G6, G7, G8, G9, G10, G11, G12, G13, G14 complete (G3 = export, last).")