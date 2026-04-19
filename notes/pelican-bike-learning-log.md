# Pelican On A Bike Learning Log

Date: 2026-04-19

This note records the actual iteration history for the pelican-on-a-bike drawing work and the concrete lessons from each exported version.

## Version History

| File | Role | Main takeaway |
| --- | --- | --- |
| `pelican.png` | Early pelican-only baseline | Established the broad body/head/beak shape but did not solve the bike problem. |
| `bike_pelican.png` | First explicit bike attempt | Added bike intent, but the result was still structurally weak and unclear. |
| `bike_pelican_v2.png` | Early cleanup pass | Slight geometry improvement, but still not readable enough at thumbnail size. |
| `bike_pelican_final.png` | Early saved alias | Preserved the first milestone, but it should not be treated as a final-quality output. |
| `bike_pelican_version1.png` | User-requested saved bad version | Useful only as a failure baseline: the silhouette and bike integration are poor. |
| `bike_pelican_v3.png` | Stronger massing pass | The pelican silhouette improved, and the wheels were clearer, but the frame was still too soft. |
| `bike_pelican_v4.png` | Composition separation test | Confirmed that simply placing frame geometry under the bird is not enough if the frame disappears visually. |
| `bike_pelican_v5.png` | Rebuilt composition from first principles | The plan was better than `v4`, but the rendering primitive still made key structure vanish in export. |
| `bike_pelican_v6.png` | First structurally successful export | Switching to explicit `line` shapes made the bike readable and gave the drawing a clear rider/bike relationship. |
| `bike_pelican_v7.png` | Strong line-weight pass | Thickened the most important frame edges with duplicated lines and kept the pelican more clearly perched above the frame. |
| `bike_pelican_v8.png` | Compact-geometry pass | Tightened the bike geometry and made the pose a little more coherent without losing the fast readability achieved in `v6` and `v7`. |
| `bike_pelican_v9.png` | Pose-improvement pass | Preserved the compact frame from `v8` and improved the rider read by making the leg placement less symmetrical. |
| `bike_pelican_v10.png` | Contour-hierarchy pass | Preserved the `v9` pose while improving the anatomical read of the pelican through a clearer neck/pouch transition. |
| `bike_pelican_v11.png` | Clean-contour pass | Simplified the pelican contour treatment from `v10`, making the bird read more cleanly without changing the working bike structure. |
| `bike_pelican_v12.png` | Current improved version | Refined the head scale and beak proportion so the pelican feels more unified and less top-heavy while preserving the working bike and pose. |
| `bike_pelican_v13.png` | Connector-contour pass | Kept the `v12` structure but improved head-to-body integration with a closer head placement and one high-value contour, making the bird feel less assembled from separate parts. |
| `bike_pelican_v14.png` | Perched-overlap pass | Lowered the body slightly and kept the bike geometry stable, making the pelican feel more seated on the bicycle rather than floating above it. |
| `bike_pelican_v15.png` | Micro-attitude pass | Kept the `v14` perch and bike structure but improved the sense of intention through a slightly cleaner head attitude and clearer pedal contact. |
| `bike_pelican_v16.png` | Settled-mass pass | Kept the `v15` structure but made the pelican feel calmer and more settled through a slightly lower upper mass and a quieter head position. |
| `bike_pelican_v17.png` | Character-micro pass | Kept the `v16` calm baseline but improved the bird's character with a tighter face placement and a slightly cleaner tail gesture. |
| `bike_pelican_v18.png` | Restraint pass | Kept the `v17` character baseline but tightened the head/beak proportion so the pelican feels a little cleaner and less blunt. |
| `bike_pelican_v19.png` | Elegance pass | Kept the `v18` calm/clean baseline but improved the face spacing so the pelican feels a little more refined and less chunky. |
| `bike_pelican_v20.png` | Poise pass | Kept the `v19` elegant baseline but adjusted the head position and face spacing so the pelican feels a little more poised and self-possessed. |
| `bike_pelican_v21.png` | Coherence pass | Kept the `v20` poised baseline but tightened the head, eye, and beak relationship so the face feels a little more unified and less assembled. |

## Practical Lessons

- The drawing lives or dies on fast readability. If the bike does not read in one glance, the image fails even if the pelican shape is decent.
- A pelican reads best as a broad oval body, small high head, long horizontal beak, and clearly separated pouch line.
- The frame must stay visible below the body. If the torso overlaps too much, the image becomes "bird over wheels" instead of "bird on a bike."
- The Krita CLI `stroke` primitive was a bad fit for this task because it did not survive export consistently enough for structural lines.
- The Krita CLI `draw_shape` `line` primitive is much more dependable for bicycle geometry.
- Because the batch limit is 50 commands, line duplication should be reserved for the edges that most affect readability.
- A better workflow is: rough geometry, export, diagnose the actual PNG, then iterate. Reading the command list alone is not enough.
- After structure is solved, proportion matters more than additional detail. A more compact frame and better seat/handlebar placement improve the result more than another round of decorative lines.
- The rider pose is now the main remaining weakness. Future passes should improve leg placement before adding any extra bird detail.
- The first meaningful pose improvement came from asymmetry, not complexity. One leg reaching differently from the other helps the bird read as seated on pedals rather than hanging in front of them.
- Once pose is working, contour hierarchy matters more than new geometry. Adding a second contour line in the neck/pouch area made the bird feel more anatomical without making the drawing busier overall.
- Cleaner contour hierarchy beats more contour hierarchy. For this minimal drawing style, two long neck/pouch contours read better than several short contour segments.
- After contour cleanup, proportion becomes the next lever. A slightly smaller head and a shorter beak improved the unity of the bird more than another round of line detail would have.
- After proportion is close, the next lever is join quality. One well-placed connector contour at the head/body junction can improve the drawing more than another whole-shape redesign.
- After join quality is working, controlled overlap becomes the next lever. A slightly lower body can improve the perched rider read, but only if the frame remains visible enough to keep the bike legible.
- After overlap is working, the next lever is precision. Tiny adjustments to head angle, eye position, and exact foot placement can improve liveliness without needing another structural pass.
- After precision, the next lever can be calmness rather than energy. Small downward shifts and a quieter head attitude can make the composition feel more settled without adding new detail.
- After calmness is working, the next lever can be character. Tiny facial adjustments and one modest tail gesture can make the drawing feel more intentional without forcing another structural change.
- After character is working, the next lever can be restraint. Slightly reducing head or beak mass can make the bird feel cleaner without asking the composition to do anything new.
- After restraint is working, the next lever can be elegance. Cleaner spacing around the face can make the bird feel more refined without demanding another structural move.
- After elegance is working, the next lever can be poise. Tiny head-placement changes can alter the bird's demeanor without changing the composition.
- After poise is working, the next lever can be coherence. Slightly tighter alignment between the head, eye, and beak can make the face feel more unified without changing the perch or bike.

## Recommended Next Moves

- If doing another pass, keep `v21` as the coherence baseline and only test one tiny accent at a time: a very small tail/wing cue, a minor cockpit relationship adjustment, or one more eye/head micro-shift, but no more broad body moves unless readability clearly improves.
- If using references again, prioritize side-profile pelican images and simple side-view bicycle silhouettes.
- If tracing is used, use it only for silhouette and proportion, then redraw the result as a fresh illustration.
