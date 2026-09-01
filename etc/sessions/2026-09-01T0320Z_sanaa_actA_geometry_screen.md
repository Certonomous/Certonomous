# SANAA-DIRECT — Act A geometry screen: real STL + live mesh (2026-09-01, ~03:20Z)

## Sanaa's words, verbatim

> still for act A [SANAA-DIRECT] Act A geometry screen: (1) Regenerate the
> STL from the solved geometry (duct, full-length centerbody with nose and
> tail, heated core section), so the uploaded file IS the solved body; retire
> the floating-motor STL. (2) Mesh it live on screen: the case is
> axisymmetric and meshes in under a minute, so the GUI runs the real mesher
> on the uploaded STL during the demo (zero solver cost), then shows the
> computational mesh, not a tessellation: a 3D view made by revolving the
> wedge mesh around the axis, plus a cross-section zoom with the wall layers
> on the housing, and the mesh facts table (cells per region, cells across
> the 3.5 mm wall, first-cell spacing, quality). Every line drawn is a cell
> edge from the mesh that was solved on.

## Routing (chief)

- (1) STL regeneration from the solved case geometry → heat-transfer (owns
  the solved case and its geometry definition); new file replaces
  motor_in_duct.stl as the Act A upload; old floating-motor STL retired from
  the demo set (kept on disk, nothing deleted from records).
- (2) Live meshing in the GUI + computational-mesh rendering (revolved wedge,
  cross-section zoom with wall layers, mesh facts table) → joint
  heat-transfer (mesher, case knowledge, mesh facts) + cfd (GUI/sdk wiring,
  rendering). Mesh runs live during demo; zero solver cost; every drawn line
  is a real cell edge from the solved mesh spec.
- Binds with 569346b3's item: the uploaded STL IS the solved body — this
  directive is how that statement becomes true.
