"""
zaphod_bot_mec_fbcoup_5x15mm_2mm_globe_post_compare_surfaces.py
====================================

Compares two STL files where one or both are SURFACE models (open shells)
rather than closed solids. For solids you'd compare volume + symmetric
volume difference; for surfaces those metrics are not meaningful.

This script reports six complementary metrics, each catching a different
class of geometric mismatch:

  1. Surface area               -> fast scalar sanity check
  2. Bounding box per axis      -> catches scale / placement errors
  3. Triangle count, edge len   -> catches tessellation density mismatch
                                   (informational, not a defect)
  4. Centroid alignment         -> catches translation / rotation drift
  5. Hausdorff & mean distance  -> THE strongest single metric for surfaces:
                                   measures how far each surface deviates
                                   from the other, point by point
  6. Sliced-section comparison  -> cuts both meshes at multiple Y planes
                                   and compares the resulting cross-section
                                   outlines (catches feature-level errors
                                   that area + Hausdorff might miss)

Output:
  - Terminal report
  - Text file:  <folder>_build123d_vs_reference_<range>.txt
                (same naming pattern as the previous compare script)

Cross-platform support:
  - Works on macOS, Windows, and Linux without changes.
  - BASE_DIR is derived from the script's own location at runtime
    (Path(__file__).resolve().parent), so the script can be run from
    any working directory.
  - Auto-discovers the build123d STL by scanning for files matching
    <folder>_G_1_*.stl and picking the most recent guideline range.
    You can override with explicit paths in the configuration block.
  - Console output uses ASCII fallbacks when running on a terminal that
    can't render Unicode (e.g. Windows cmd.exe with cp1252 codepage).
  - Report file is always written as UTF-8 regardless of platform.

Required libraries:
  - trimesh
  - numpy
  - rtree              (used by trimesh for fast nearest-point lookup)
  - shapely (optional) (improves cross-section accuracy if present)

Usage:
  python zaphod_bot_mec_fbcoup_5x15mm_2mm_globe_post_compare_surfaces.py
"""

import os
import sys
import math
from pathlib import Path
from datetime import datetime

# ── Numpy + trimesh imports with helpful error messages ─────────────────────
try:
    import numpy as np
except ImportError:
    print("ERROR: numpy not installed. Run: pip install numpy")
    sys.exit(1)

try:
    import trimesh
except ImportError:
    print("ERROR: trimesh not installed. Run: pip install trimesh")
    sys.exit(1)

# rtree is required by trimesh.proximity.closest_point. We don't import it
# directly but we check availability so we can fail with a helpful message
# instead of a deep traceback later.
try:
    import rtree as _rtree_check  # noqa: F401
    _HAS_RTREE = True
except ImportError:
    _HAS_RTREE = False


# ─────────────────────────────────────────────────────────────────────────────
#  Configuration
#
#  All paths are derived from BASE_DIR so the script is location-independent.
#  Override BUILD123D_STL_OVERRIDE / REFERENCE_STL_OVERRIDE below if your
#  files are named differently from the auto-discovery defaults.
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent

def _infer_folder_name(base_dir):
    """
    Derive FOLDER_NAME from the STL files present rather than from the
    directory name. This makes the script robust when it is placed in a
    folder whose name does not match the project (e.g. ~/scripts/).

    Strategy:
      1. Look for any <name>_reference.stl  -> name is everything before _reference
      2. Look for any <name>_G_1_*.stl      -> name is everything before _G_1_
      3. Fall back to BASE_DIR.name (original behaviour)
    """
    # Priority 1: reference STL pattern
    for p in base_dir.glob("*_reference.stl"):
        stem = p.stem  # e.g. "PICSY_trigger_button_r_reference"
        if stem.endswith("_reference"):
            return stem[: -len("_reference")]

    # Priority 2: build123d STL pattern
    for p in base_dir.glob("*_G_1_*.stl"):
        parts = p.stem.rsplit("_G_1_", 1)
        if len(parts) == 2:
            return parts[0]

    # Fallback: directory name (original behaviour)
    return base_dir.name

FOLDER_NAME = _infer_folder_name(BASE_DIR)


def auto_discover_build123d_stl(base_dir, folder_name):
    """
    Scan base_dir for files matching <folder_name>_G_1_*.stl and pick the
    one with the highest guideline number. Returns (Path, range_str) or
    (None, None) if no match is found.

    Examples:
      PICSY_trigger_button_r_G_1_18.stl    -> range "G_1_18"
      PICSY_trigger_button_r_G_1_5.stl     -> range "G_1_5"
    """
    pattern = f"{folder_name}_G_1_*.stl"
    candidates = sorted(base_dir.glob(pattern))
    if not candidates:
        return None, None

    def trailing_num(p):
        stem = p.stem  # filename without extension
        try:
            return int(stem.rsplit("_", 1)[-1])
        except ValueError:
            return -1

    best = max(candidates, key=trailing_num)
    n = trailing_num(best)
    return best, f"G_1_{n}"


# Auto-discover the build123d output. Set BUILD123D_STL_OVERRIDE explicitly
# if you have a non-standard filename.
BUILD123D_STL_OVERRIDE = None     # e.g. BASE_DIR / "my_custom_build.stl"
REFERENCE_STL_OVERRIDE = None     # e.g. BASE_DIR / "my_reference.stl"

if BUILD123D_STL_OVERRIDE is not None:
    BUILD123D_STL = Path(BUILD123D_STL_OVERRIDE)
    GUIDELINE_RANGE = BUILD123D_STL.stem.rsplit("_", 2)[-2:]  # last two parts
    GUIDELINE_RANGE = "_".join(GUIDELINE_RANGE)
else:
    BUILD123D_STL, GUIDELINE_RANGE = auto_discover_build123d_stl(BASE_DIR, FOLDER_NAME)
    if BUILD123D_STL is None:
        # Fall back to the default name; main() will report a helpful error.
        GUIDELINE_RANGE = "G_1_18"
        BUILD123D_STL = BASE_DIR / f"{FOLDER_NAME}_{GUIDELINE_RANGE}.stl"

if REFERENCE_STL_OVERRIDE is not None:
    REFERENCE_STL = Path(REFERENCE_STL_OVERRIDE)
else:
    REFERENCE_STL = BASE_DIR / f"{FOLDER_NAME}_reference.stl"

REPORT_TXT = BASE_DIR / f"{FOLDER_NAME}_build123d_vs_reference_{GUIDELINE_RANGE}.txt"


# How many random surface samples to use for Hausdorff / mean-distance.
# 50,000 is a good balance: noise is averaged out, runtime ~5-10 sec.
HAUSDORFF_N_SAMPLES = 50_000

# Tolerances for grading. These are aligned with typical FDM 3D-printer
# manufacturing tolerances rather than CAD-tight micrometre tolerances,
# since the PICSY parts are designed for FDM printing. A well-tuned
# consumer FDM printer (Prusa, Bambu, etc.) has ~0.1-0.5 mm positional
# accuracy; industry rule-of-thumb is ±0.5 mm. Deviations below those
# floors are below what the manufacturing process can resolve, so they
# count as "indistinguishable from the original" in practice.
#
# Rationale per band (Hausdorff / mean distance):
#   EXCELLENT  : indistinguishable even on a precision (SLA/industrial) printer
#   GOOD       : below typical FDM positional accuracy (lost in print noise)
#   ACCEPTABLE : within loose FDM tolerance (functional, minor feature drift)
#   POOR       : print-visible defect; larger than what the printer would
#                have introduced on its own
#
# Surface-area % thresholds are kept tight since that metric is a unitless
# ratio and not bounded by print tolerance.
AREA_PCT_EXCELLENT      = 0.5      # %
AREA_PCT_GOOD           = 2.0
AREA_PCT_ACCEPTABLE     = 5.0

BBOX_TOL_MM             = 0.1      # mm per axis (FDM-aligned)
CENTROID_TOL_MM         = 0.1      # mm

HAUSDORFF_EXCELLENT_MM  = 0.1      # precision-printer floor
HAUSDORFF_GOOD_MM       = 0.5      # typical FDM positional accuracy
HAUSDORFF_ACCEPTABLE_MM = 1.0      # loose FDM tolerance

MEAN_DIST_EXCELLENT_MM  = 0.01     # roughly 1/10 of Hausdorff bands
MEAN_DIST_GOOD_MM       = 0.05
MEAN_DIST_ACCEPTABLE_MM = 0.1

# Cross-section Y-planes for slice comparison.
# Auto-computed inside compare_sections() from the meshes' actual Y bounds
# so no manual tuning is needed.  This list is the FALLBACK used only if
# mesh loading fails before the function is called.
SECTION_Y_PLANES = [-14.0, -10.0, -5.0, 0.0, 5.0, 10.0, 14.0]


# ─────────────────────────────────────────────────────────────────────────────
#  Unicode-safe output: detect whether the active stdout can render the
#  symbols we'd like to use. If it can, use the rich Unicode versions;
#  otherwise fall back to plain ASCII so the script doesn't crash on
#  Windows cmd.exe with cp1252 codepage.
# ─────────────────────────────────────────────────────────────────────────────
def _stdout_supports_unicode():
    """Return True if sys.stdout encoding can encode common emoji."""
    enc = (getattr(sys.stdout, "encoding", None) or "").lower()
    if enc.startswith("utf"):
        return True
    try:
        "\U0001F7E2".encode(enc or "ascii")  # green circle
        return True
    except (UnicodeEncodeError, LookupError):
        return False


_USE_UNICODE = _stdout_supports_unicode()


def _sym(rich, plain):
    return rich if _USE_UNICODE else plain


SYM_GREEN  = _sym("\U0001F7E2", "[OK]   ")
SYM_YELLOW = _sym("\U0001F7E1", "[GOOD] ")
SYM_ORANGE = _sym("\U0001F7E0", "[FAIR] ")
SYM_RED    = _sym("\U0001F534", "[POOR] ")
SYM_PASS   = _sym("\u2705",     "[PASS]")
SYM_FAIL   = _sym("\u274C",     "[FAIL]")
SYM_NEUT   = _sym("\u2796",     "[--]  ")
SYM_WARN   = _sym("\u26A0 ",    "[WARN]")
SYM_BLOCK  = _sym("\u2588",     "#")


# ─────────────────────────────────────────────────────────────────────────────
#  Tee output: write to stdout AND a UTF-8 file simultaneously.
#  The file is ALWAYS UTF-8 so it preserves emoji and special characters
#  regardless of the platform's default encoding.
# ─────────────────────────────────────────────────────────────────────────────
class Tee:
    def __init__(self, filepath):
        self.terminal = sys.stdout
        # Always write report file as UTF-8 (works on Windows + macOS + Linux).
        self.log = open(filepath, "w", encoding="utf-8")

    def write(self, msg):
        # Try to write to terminal; if its encoding can't handle a character,
        # fall back to a safe encoding rather than crashing.
        try:
            self.terminal.write(msg)
        except UnicodeEncodeError:
            enc = getattr(self.terminal, "encoding", None) or "ascii"
            safe = msg.encode(enc, errors="replace").decode(enc, errors="replace")
            self.terminal.write(safe)
        # File always gets the full UTF-8 message.
        self.log.write(msg)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def close(self):
        self.log.close()


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────
def pct_err(diff, reference):
    if reference == 0:
        return float("inf")
    return abs(diff) / abs(reference) * 100.0


def grade(value, exc, good, acc):
    if value <= exc:  return f"{SYM_GREEN} EXCELLENT"
    if value <= good: return f"{SYM_YELLOW} GOOD"
    if value <= acc:  return f"{SYM_ORANGE} ACCEPTABLE"
    return            f"{SYM_RED} POOR"


def grade_pass_fail(passed):
    return f"{SYM_PASS} PASS" if passed else f"{SYM_FAIL} FAIL"


def sep(c="=", length=70):
    print(f"\n  {c * length}")


# ─────────────────────────────────────────────────────────────────────────────
#  PART 1 - Mesh inspection
# ─────────────────────────────────────────────────────────────────────────────
def load_and_inspect(filepath, label):
    """Load an STL, print basic geometric info, return the trimesh object."""
    p = Path(filepath)
    if not p.exists():
        raise FileNotFoundError(f"STL not found: {p}")
    m = trimesh.load(str(p), force="mesh")
    # trimesh.load() may return a Scene when the STL has disjoint bodies.
    # force="mesh" coerces it, but as a belt-and-braces fallback we also
    # concatenate a Scene manually.
    if isinstance(m, trimesh.Scene):
        meshes = [g for g in m.geometry.values()
                  if isinstance(g, trimesh.Trimesh)]
        if not meshes:
            raise ValueError(f"No Trimesh geometry found in {p.name}")
        m = trimesh.util.concatenate(meshes)
        print(f"  [Note: Scene with {len(meshes)} body/bodies merged into one mesh]")
    sep()
    print(f"  {label}")
    sep()
    print(f"  File              : {p.name}")
    print(f"  Triangles         : {len(m.faces):,}")
    print(f"  Vertices          : {len(m.vertices):,}")
    print(f"  Watertight        : {m.is_watertight}  "
          f"({'closed solid' if m.is_watertight else 'open surface'})")
    print(f"  Surface area      : {m.area:.4f} mm^2")
    print(f"  Bbox X            : {m.bounds[0,0]:>10.4f} -> {m.bounds[1,0]:.4f} mm "
          f"(span {m.bounds[1,0] - m.bounds[0,0]:.4f})")
    print(f"  Bbox Y            : {m.bounds[0,1]:>10.4f} -> {m.bounds[1,1]:.4f} mm "
          f"(span {m.bounds[1,1] - m.bounds[0,1]:.4f})")
    print(f"  Bbox Z            : {m.bounds[0,2]:>10.4f} -> {m.bounds[1,2]:.4f} mm "
          f"(span {m.bounds[1,2] - m.bounds[0,2]:.4f})")
    c = m.centroid
    print(f"  Centroid          : ({c[0]:.4f}, {c[1]:.4f}, {c[2]:.4f}) mm")
    return m


# ─────────────────────────────────────────────────────────────────────────────
#  PART 2 - Surface area comparison
# ─────────────────────────────────────────────────────────────────────────────
def compare_surface_area(b123_mesh, ref_mesh):
    sep()
    print(f"  SURFACE AREA COMPARISON")
    sep()
    a_b = b123_mesh.area
    a_r = ref_mesh.area
    diff = a_b - a_r
    p = pct_err(diff, a_r)
    rating = grade(p, AREA_PCT_EXCELLENT, AREA_PCT_GOOD, AREA_PCT_ACCEPTABLE)

    print(f"  {'Metric':<35}{'Value':>15}  Unit")
    print(f"  {'-' * 65}")
    print(f"  {'Build123d surface area':<35}{a_b:>15.4f}  mm^2")
    print(f"  {'Reference surface area':<35}{a_r:>15.4f}  mm^2")
    print(f"  {'Absolute difference':<35}{diff:>+15.4f}  mm^2  "
          f"({'build123d larger' if diff > 0 else 'build123d smaller'})")
    print(f"  {'% error vs reference':<35}{p:>15.4f}  %")
    print(f"  {'Rating':<35}{rating:>15}")
    return p


# ─────────────────────────────────────────────────────────────────────────────
#  PART 3 - Bounding box comparison
# ─────────────────────────────────────────────────────────────────────────────
def compare_bounding_box(b123_mesh, ref_mesh):
    sep()
    print(f"  BOUNDING BOX COMPARISON  (tolerance +/-{BBOX_TOL_MM} mm per axis)")
    sep()

    ba = b123_mesh.bounds
    br = ref_mesh.bounds

    print(f"  {'Axis':<8}{'Build123d':>14}{'Reference':>14}"
          f"{'D (mm)':>10}{'% err':>9}  Status")
    print(f"  {'-' * 65}")

    axes = ["X min", "X max", "Y min", "Y max", "Z min", "Z max"]
    vals_b = [ba[0, 0], ba[1, 0], ba[0, 1], ba[1, 1], ba[0, 2], ba[1, 2]]
    vals_r = [br[0, 0], br[1, 0], br[0, 1], br[1, 1], br[0, 2], br[1, 2]]
    spans = [
        br[1, 0] - br[0, 0], br[1, 0] - br[0, 0],
        br[1, 1] - br[0, 1], br[1, 1] - br[0, 1],
        br[1, 2] - br[0, 2], br[1, 2] - br[0, 2],
    ]

    all_pass = True
    for axis, vb, vr, span in zip(axes, vals_b, vals_r, spans):
        diff = vb - vr
        p = pct_err(diff, span) if span != 0 else 0.0
        passes = abs(diff) <= BBOX_TOL_MM
        all_pass = all_pass and passes
        icon = SYM_PASS if passes else SYM_FAIL
        print(f"  {axis:<8}{vb:>14.4f}{vr:>14.4f}{diff:>+10.4f}{p:>8.3f}%  {icon}")

    print(f"\n  Overall bounding box : {grade_pass_fail(all_pass)}")
    return all_pass


# ─────────────────────────────────────────────────────────────────────────────
#  PART 4 - Tessellation density (informational)
# ─────────────────────────────────────────────────────────────────────────────
def compare_tessellation(b123_mesh, ref_mesh):
    sep()
    print(f"  TESSELLATION DENSITY  (informational - different tessellators")
    print(f"                         can produce different triangle counts")
    print(f"                         for the same underlying surface)")
    sep()

    tb_n = len(b123_mesh.faces)
    tr_n = len(ref_mesh.faces)
    vb_n = len(b123_mesh.vertices)
    vr_n = len(ref_mesh.vertices)
    eb_n = b123_mesh.edges_unique.shape[0]
    er_n = ref_mesh.edges_unique.shape[0]

    print(f"  {'Metric':<35}{'Build123d':>14}{'Reference':>14}{'Delta':>10}")
    print(f"  {'-' * 65}")
    print(f"  {'Triangles':<35}{tb_n:>14,}{tr_n:>14,}{tb_n - tr_n:>+10,}")
    print(f"  {'Vertices':<35}{vb_n:>14,}{vr_n:>14,}{vb_n - vr_n:>+10,}")
    print(f"  {'Unique edges':<35}{eb_n:>14,}{er_n:>14,}{eb_n - er_n:>+10,}")

    avg_edge_b = float(b123_mesh.edges_unique_length.mean())
    avg_edge_r = float(ref_mesh.edges_unique_length.mean())
    print(f"  {'Avg edge length (mm)':<35}{avg_edge_b:>14.4f}"
          f"{avg_edge_r:>14.4f}{avg_edge_b - avg_edge_r:>+10.4f}")

    print(f"\n  Note: small differences in triangle / edge counts are expected.")
    print(f"        What matters is that the SURFACES match, not the meshes.")


# ─────────────────────────────────────────────────────────────────────────────
#  PART 5 - Centroid alignment
# ─────────────────────────────────────────────────────────────────────────────
def compare_centroid(b123_mesh, ref_mesh):
    sep()
    print(f"  CENTROID ALIGNMENT  (tolerance +/-{CENTROID_TOL_MM} mm per axis)")
    sep()
    cb = b123_mesh.centroid
    cr = ref_mesh.centroid
    diff = cb - cr
    dist = float(np.linalg.norm(diff))

    print(f"  {'Axis':<8}{'Build123d':>14}{'Reference':>14}"
          f"{'D (mm)':>10}  Status")
    print(f"  {'-' * 65}")
    all_pass = True
    for axis_name, b, r, d in [
        ("X", cb[0], cr[0], diff[0]),
        ("Y", cb[1], cr[1], diff[1]),
        ("Z", cb[2], cr[2], diff[2]),
    ]:
        passes = abs(d) <= CENTROID_TOL_MM
        all_pass = all_pass and passes
        icon = SYM_PASS if passes else SYM_FAIL
        print(f"  {axis_name:<8}{b:>14.4f}{r:>14.4f}{d:>+10.4f}  {icon}")

    print(f"\n  Centroid distance : {dist:.4f} mm")
    print(f"  Overall centroid  : {grade_pass_fail(all_pass)}")
    return all_pass, dist


# ─────────────────────────────────────────────────────────────────────────────
#  PART 6 - Hausdorff / mean / RMS distance
# ─────────────────────────────────────────────────────────────────────────────
def compare_hausdorff(b123_mesh, ref_mesh, n_samples=HAUSDORFF_N_SAMPLES):
    """
    Sample N random points on each surface, then for each point measure
    distance to the nearest point on the OTHER surface. Reports:
      - Hausdorff (max worst-case distance)
      - Mean distance
      - RMS distance
      - 95th and 99th percentiles

    Requires rtree for trimesh.proximity.closest_point. If not installed,
    skip this section gracefully and tell the user how to fix it.
    """
    sep()
    print(f"  HAUSDORFF / NEAREST-POINT DISTANCE  (n_samples = {n_samples:,})")
    print(f"  THE primary metric for surface-vs-surface equivalence:")
    print(f"  measures how far each surface deviates from the other.")
    sep()

    if not _HAS_RTREE:
        print(f"  {SYM_WARN} Skipping this section: 'rtree' Python package not installed.")
        print(f"     trimesh.proximity.closest_point requires rtree for fast lookups.")
        print(f"     Install with: pip install rtree")
        print(f"     (Works on Windows, macOS, and Linux. The pip wheel includes")
        print(f"      the underlying spatial-index library on all platforms.)")
        return None, None, None

    # Sample dense point clouds from both surfaces.
    pts_b, _ = trimesh.sample.sample_surface(b123_mesh, n_samples)
    pts_r, _ = trimesh.sample.sample_surface(ref_mesh, n_samples)

    _, d_b_to_r, _ = trimesh.proximity.closest_point(ref_mesh, pts_b)
    _, d_r_to_b, _ = trimesh.proximity.closest_point(b123_mesh, pts_r)

    all_d = np.concatenate([d_b_to_r, d_r_to_b])

    haus = float(max(d_b_to_r.max(), d_r_to_b.max()))
    mean = float(all_d.mean())
    rms = float(np.sqrt((all_d ** 2).mean()))
    p95 = float(np.percentile(all_d, 95))
    p99 = float(np.percentile(all_d, 99))

    haus_rating = grade(haus, HAUSDORFF_EXCELLENT_MM, HAUSDORFF_GOOD_MM,
                        HAUSDORFF_ACCEPTABLE_MM)
    mean_rating = grade(mean, MEAN_DIST_EXCELLENT_MM, MEAN_DIST_GOOD_MM,
                        MEAN_DIST_ACCEPTABLE_MM)

    print(f"  {'Metric':<40}{'Value (mm)':>14}  Rating")
    print(f"  {'-' * 65}")
    print(f"  {'Hausdorff (max)':<40}{haus:>14.6f}  {haus_rating}")
    print(f"  {'Mean distance':<40}{mean:>14.6f}  {mean_rating}")
    print(f"  {'RMS distance':<40}{rms:>14.6f}")
    print(f"  {'95th percentile':<40}{p95:>14.6f}")
    print(f"  {'99th percentile':<40}{p99:>14.6f}")

    print(f"\n  Interpretation:")
    print(f"   - Mean distance much less than 1 mesh-edge length means")
    print(f"     surfaces are coincident in the bulk, with only mesh noise.")
    print(f"   - Hausdorff much larger than mean -> a small region where")
    print(f"     the surfaces diverge significantly (a missing or misplaced")
    print(f"     feature), even though most of the area aligns.")

    return haus, mean, rms


# ─────────────────────────────────────────────────────────────────────────────
#  PART 7 - Cross-section slice comparison
# ─────────────────────────────────────────────────────────────────────────────
def compare_sections(b123_mesh, ref_mesh, y_planes=None):
    """
    Slice both meshes at each Y plane in y_planes (planes parallel to XZ).
    Compare the resulting cross-section: total length and bounding box.
    Y planes are auto-derived from the mesh bounds if not supplied.
    """
    if y_planes is None:
        # Auto-derive 7 evenly-spaced cuts from the union of both Y ranges,
        # keeping 5% margin from each end so edge cuts don't produce empty slices.
        y_min = max(b123_mesh.bounds[0, 1], ref_mesh.bounds[0, 1])
        y_max = min(b123_mesh.bounds[1, 1], ref_mesh.bounds[1, 1])
        margin = (y_max - y_min) * 0.05
        y_min += margin
        y_max -= margin
        import numpy as _np2
        y_planes = [round(float(v), 3) for v in _np2.linspace(y_min, y_max, 7)]
    sep()
    print(f"  CROSS-SECTION SLICE COMPARISON  ({len(y_planes)} cuts at Y planes)")
    print(f"  Y planes (auto-derived from mesh bounds): {y_planes}")
    print(f"  Cuts both meshes at each Y plane and compares the outline.")
    sep()
    print(f"  {'Y':>8}  {'B123d len':>11}  {'Ref len':>11}"
          f"  {'D len':>10}  {'D %':>8}  Status")
    print(f"  {'-' * 65}")

    overall_pass = True
    for y in y_planes:
        plane_origin = [0.0, y, 0.0]
        plane_normal = [0.0, 1.0, 0.0]

        try:
            sec_b = b123_mesh.section(plane_origin=plane_origin, plane_normal=plane_normal)
            sec_r = ref_mesh.section(plane_origin=plane_origin, plane_normal=plane_normal)
        except Exception as e:
            print(f"  {y:>8.3f}  section error: {type(e).__name__}: {e}")
            continue

        if sec_b is None and sec_r is None:
            print(f"  {y:>8.3f}  {'(empty)':>11}  {'(empty)':>11}"
                  f"  {'-':>10}  {'-':>8}  {SYM_NEUT}")
            continue
        if sec_b is None or sec_r is None:
            present = "B123d" if sec_b is not None else "Ref"
            print(f"  {y:>8.3f}  "
                  f"{(sec_b.length if sec_b else 0):>11.4f}  "
                  f"{(sec_r.length if sec_r else 0):>11.4f}"
                  f"  {'-':>10}  {'-':>8}  {SYM_FAIL} only-{present}")
            overall_pass = False
            continue

        len_b = float(sec_b.length)
        len_r = float(sec_r.length)
        diff = len_b - len_r
        p = pct_err(diff, len_r) if len_r > 0 else 0.0
        passes = p <= 2.0
        overall_pass = overall_pass and passes
        icon = SYM_PASS if passes else SYM_FAIL
        print(f"  {y:>8.3f}  {len_b:>11.4f}  {len_r:>11.4f}"
              f"  {diff:>+10.4f}  {p:>7.3f}%  {icon}")

    print(f"\n  Overall section comparison: {grade_pass_fail(overall_pass)}")
    return overall_pass


# ─────────────────────────────────────────────────────────────────────────────
#  PART 8 - Summary scorecard
# ─────────────────────────────────────────────────────────────────────────────
def print_summary(area_p, bbox_pass, centroid_pass, centroid_dist,
                  haus, mean, sections_pass):
    sep(SYM_BLOCK)
    print(f"  SUMMARY SCORECARD")
    sep(SYM_BLOCK)
    print(f"  {'Check':<40}{'Score':>15}  Rating")
    print(f"  {'-' * 65}")
    print(f"  {'Surface area % error':<40}{area_p:>14.3f}%  "
          f"{grade(area_p, AREA_PCT_EXCELLENT, AREA_PCT_GOOD, AREA_PCT_ACCEPTABLE)}")
    print(f"  {'Bounding box':<40}{grade_pass_fail(bbox_pass):>15}")
    print(f"  {'Centroid alignment':<40}{grade_pass_fail(centroid_pass):>15}  "
          f"(dist: {centroid_dist:.4f} mm)")
    if haus is not None:
        print(f"  {'Hausdorff distance (mm)':<40}{haus:>15.6f}  "
              f"{grade(haus, HAUSDORFF_EXCELLENT_MM, HAUSDORFF_GOOD_MM, HAUSDORFF_ACCEPTABLE_MM)}")
        print(f"  {'Mean distance (mm)':<40}{mean:>15.6f}  "
              f"{grade(mean, MEAN_DIST_EXCELLENT_MM, MEAN_DIST_GOOD_MM, MEAN_DIST_ACCEPTABLE_MM)}")
    else:
        print(f"  {'Hausdorff distance (mm)':<40}{'(skipped)':>15}  "
              f"(rtree not installed)")
        print(f"  {'Mean distance (mm)':<40}{'(skipped)':>15}")
    print(f"  {'Cross-section slices':<40}{grade_pass_fail(sections_pass):>15}")
    sep(SYM_BLOCK)

    overall = (
        area_p <= AREA_PCT_GOOD and
        bbox_pass and
        centroid_pass and
        (haus is None or haus <= HAUSDORFF_GOOD_MM) and
        (mean is None or mean <= MEAN_DIST_GOOD_MM) and
        sections_pass
    )
    if overall:
        print(f"\n  OVERALL VERDICT : {SYM_GREEN} SURFACES MATCH")
    else:
        print(f"\n  OVERALL VERDICT : {SYM_WARN} REVIEW REQUIRED")


# ─────────────────────────────────────────────────────────────────────────────
#  Helpful diagnostics when files are missing
# ─────────────────────────────────────────────────────────────────────────────
def list_stl_files_in_base():
    return sorted(BASE_DIR.glob("*.stl"))


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Pre-flight: do the input files exist?
    missing = []
    if not BUILD123D_STL.exists():
        missing.append(("Build123d STL", BUILD123D_STL))
    if not REFERENCE_STL.exists():
        missing.append(("Reference STL", REFERENCE_STL))

    if missing:
        print("ERROR: One or more required input files were not found.\n")
        for label, p in missing:
            print(f"  {label:<20}: {p}")
        print()
        existing = list_stl_files_in_base()
        if existing:
            print(f"STL files present in {BASE_DIR}:")
            for p in existing:
                print(f"  {p.name}")
        else:
            print(f"No STL files were found in {BASE_DIR}.")
        print()
        print("Fix options:")
        print("  1. Make sure both files exist with the expected names:")
        print(f"     - {FOLDER_NAME}_G_1_<n>.stl   (build123d output)")
        print(f"     - {FOLDER_NAME}_reference.stl (downloaded reference)")
        print("  2. Or set BUILD123D_STL_OVERRIDE / REFERENCE_STL_OVERRIDE")
        print("     near the top of this script to point to your filenames.")
        sys.exit(1)

    tee = Tee(REPORT_TXT)
    sys.stdout = tee

    try:
        print("\n" + SYM_BLOCK * 70)
        print(f"  SURFACE COMPARISON: Build123d vs Reference STL")
        print(f"  Run time   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Platform   : {sys.platform} (Python {sys.version.split()[0]})")
        print(f"  Project    : {BASE_DIR}")
        print(f"  Folder     : {FOLDER_NAME}")
        print(SYM_BLOCK * 70)
        print(f"  Build123d  : {BUILD123D_STL.name}")
        print(f"  Reference  : {REFERENCE_STL.name}")
        print(f"  Report     : {REPORT_TXT.name}")

        b123_mesh = load_and_inspect(BUILD123D_STL, "Build123d STL")
        ref_mesh  = load_and_inspect(REFERENCE_STL, "Reference STL")

        area_p = compare_surface_area(b123_mesh, ref_mesh)
        compare_tessellation(b123_mesh, ref_mesh)
        bbox_pass = compare_bounding_box(b123_mesh, ref_mesh)
        centroid_pass, centroid_dist = compare_centroid(b123_mesh, ref_mesh)
        haus, mean, rms = compare_hausdorff(b123_mesh, ref_mesh)
        sections_pass = compare_sections(b123_mesh, ref_mesh)

        print_summary(area_p, bbox_pass, centroid_pass, centroid_dist,
                      haus, mean, sections_pass)

        print(f"\n  Report saved -> {REPORT_TXT}\n")

    except Exception as _exc:
        import traceback as _tb
        print(f"\n  ERROR during comparison:")
        print(f"  {type(_exc).__name__}: {_exc}")
        print()
        _tb.print_exc(file=sys.stdout)
        sys.stdout.flush()
        raise
    finally:
        sys.stdout = tee.terminal
        tee.close()

    print(f"Report written -> {REPORT_TXT}")