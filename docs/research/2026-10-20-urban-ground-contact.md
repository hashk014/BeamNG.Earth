# Urban building and sidewalk corrections

The player reported floating fragments on a complex building near the blue
school in Les Sables-d'Olonne, dirt gaps behind sidewalks and some houses
projecting into the road. Some real streets legitimately narrow beside a facade.

## Reproduction boundary

The running game was inspected through its local MCP interface. A brief daylight
camera inspection at the main Savary de Mauléon building showed a complete
grounded body. The original camera mode and real-time sky were restored.
The player confirmed that another building or wing was affected. Its exact
location is still requested; that particular floating fragment is not claimed
as reproduced or visually fixed.

The live session's anchor was `46.502571072229, -1.7800668614426`. Two sectors,
`(0, 1)` and `(-1, 2)`, were rebuilt from the real cached source data with
networking disabled, into a separate local output directory. Active session
files were not replaced.

## Confirmed generator problems and changes

- A public road crossing a footprint previously raised the entire building by
  5.5 m. A sufficiently supported crossing now creates a local passage, with
  grounded wings on both sides and the original roof height. Explicit elevated
  geometry stays elevated. Roads inside mapped courtyards do not raise walls.
- Any known-height building part previously replaced the entire parent, even
  when the parts covered only one wing or a small elevated roof structure.
  Uncovered parent areas now retain a body from the ground to the first mapped
  part's support height. Explicit courtyards remain open, and disconnected wings
  are preserved. Related parts share one ground datum on slopes.
- Building foundations previously sampled ungraded terrain while nearby road
  physics used graded terrain. Both near and far generation paths now use the
  same graded ground.
- Pitched roofs previously replaced wall footprints with their bounding
  rectangles. Walls, doors and collision now keep the mapped outline. Guessed
  rectangular pitched roofs are restricted to near-rectangular footprints;
  irregular outlines retain their shape with a flat roof.
- Roof equipment was admitted when only its centre lay over the roof. Its whole
  footprint must now be supported, including at concave corners.
- Intersection cutting dropped sidewalk pieces shorter than three metres, and
  the end joiner excluded gaps below 30 cm. Short sidewalk links and coincident
  or nearby ends are now retained and joined without duplicate vertices.
- Short gaps between an existing sidewalk's back edge and a nearby facing
  facade now receive concrete paving, with the same top geometry in the
  visible mesh, its LOD and collision. Nearby runs are taken before clipping
  at tile borders.

## Evidence

- 243 generator tests pass, including 20 new regressions in
  `server/tests/test_urban_frontages.py`.
- 51 focused maintenance tests pass.
- The two real source-data sectors rebuild 292 building items, 149 concrete
  apron pieces and 13 encoded mesh files. Every stored mesh index is within its
  vertex array. The local warm-cache run took 1.901 seconds; this excludes
  networking, game streaming, collision rebuilds and drawing, and is not an FPS
  claim.
- Local evidence: `dist/urban-proof-final/result.json`,
  `dist/urban-geometry-validation.json`, `dist/urban-quick-validation.json`.

## Limits and next game check

Inferred street passages currently reserve five metres across, require at least
15 m of mapped road inside the solid footprint and retain at least 25% grounded
support area. Ambiguous smaller overlaps retain their mapped building. These
rules cannot establish the real geometry of every underpass from incomplete
map data.

Concrete frontages cover facing gaps up to three metres and reject steep
height differences or the opposite sidewalk. Existing gardens, rural houses
without generated sidewalks and large setbacks are not covered wholesale.
Other sidewalk gaps can remain when connecting them would cross a carriageway
or source geometry is missing.

The corrected sources and local test kit need a fresh server session. Confirm
the exact reported annex, facade-to-sidewalk contact, roof equipment support and
driving/collision behavior in the game. No upstream issue is closed by this pass.
