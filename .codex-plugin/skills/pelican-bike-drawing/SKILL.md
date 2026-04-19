---
name: pelican-bike-drawing
description: This skill should be used when the user asks to "draw a pelican on a bike", "sketch a bird on a bicycle", "use pelican reference photos", "trace a bird reference for Krita", or "improve a rough animal drawing with references".
version: "0.8.8"
---

# Pelican Bike Drawing

Use this skill to turn reference images into a clean Krita illustration of a pelican on a bicycle. Keep the result original, readable, and simple enough to work well in a CLI-driven drawing workflow.

## Core Approach

Start with references before drawing anything.

1. Gather 2 to 4 references that show the subject clearly.
2. Prefer user-provided images, public-domain images, or clearly licensed stock photos.
3. Extract the subject structure before thinking about style.
4. Build the drawing from broad shapes first, then add details.
5. Export a versioned result and review it against the references.

## What To Look For In Pelican References

Identify the parts that matter most for a readable silhouette:

- A large rounded body.
- A high-set head with a small eye.
- A long horizontal beak with a visible pouch.
- A short neck and a smooth body transition.
- Thin legs that can hang below the body.
- Strong contrast between body mass and the narrow beak.

When the subject is on a bike, keep the bicycle clearly separate from the bird:

- Make both wheels obvious.
- Leave enough space for the frame to read as a triangle or bar system.
- Keep the pelican body perched above the frame, not merged into it.
- Use thick, simple frame strokes instead of tiny mechanical detail.

## When Tracing Is Worth Considering

Use tracing only for structure and proportion.

- Trace silhouettes, body masses, and the bike geometry when the goal is accurate placement.
- Trace only from images that are user-owned, user-provided, or clearly open licensed.
- Avoid copying copyrighted artwork or imitating a living artist's style.
- Convert traced structure into a new drawing instead of reproducing the source image.

Treat tracing as an anatomy shortcut, not as a final look.

## Suggested Workflow

1. Collect references and isolate the most useful one or two views.
2. Note the main geometry: body oval, head circle, beak rectangle, wheel circles, frame bars.
3. Draft the composition as simple shapes on a fresh canvas.
4. Check the image at thumbnail size.
5. If the bike is unclear, thicken the frame and simplify the body overlap.
6. If the pelican is unclear, enlarge the beak, raise the head, and separate the neck from the torso.
7. Export the canvas with a versioned filename.
8. Compare the export against the references and decide what to fix next.

## Krita CLI Findings

These are workflow-specific lessons from the actual pelican-on-bike iteration history in this repo.

- The `draw_shape` `line` primitive survives export more reliably than freehand `stroke` for bike frames.
- If the bike must read instantly, spend the command budget on frame clarity before adding extra bird detail.
- The plugin batch limit is 50 commands, so reserve duplicates only for the lines that matter most.
- When a line needs to read thicker, duplicate it with a 1 to 2 pixel offset instead of assuming brush strokes will export cleanly.
- Keep the pelican body high enough that the top tube, seat tube, and down tube are still visible underneath.
- Treat the beak and pouch as separate shape systems: a yellow beak block plus orange pouch lines reads better than one generic orange stroke.
- Test exports often. A composition that seems correct in the command plan can still fail visually in the PNG.
- Once the frame is readable, the next quality gain comes from proportion: compact frame geometry and a believable seat/handlebar relationship look better than simply adding more lines.
- The legs should terminate clearly on pedals; if they overshoot or bend too loosely, the rider pose becomes the weakest part of the image.
- Small asymmetry helps. Even in a minimal drawing, offset pedal heights and slightly different leg paths make the rider read as posed instead of pinned in place.
- After pose, the next improvement is contour hierarchy. A second neck or pouch contour can make the head-to-body transition feel more anatomical without forcing a more detailed style.
- Keep that contour hierarchy simple. A pair of clean long contours reads better than several shorter neck segments once the composition is already working.
- Head scale and beak length need restraint. Once the rider pose is working, slightly smaller head mass and a shorter beak can make the bird feel more unified instead of top-heavy.
- When the proportions are already close, one strategic connector contour at the highest-value join can improve the drawing more than another full silhouette rewrite.
- After the head/body join is working, controlled overlap becomes the next lever. Lowering the upper mass slightly can make the pelican feel seated on the bike instead of floating, but only if the top tube and frame triangle remain readable.
- Once overlap is working, the next gains are often micro-adjustments. Small changes to head attitude and exact foot landing can improve the sense of intention more than any additional contour.
- After micro-adjustments, look for calmness. A slightly lower upper mass and a quieter head position can make the drawing feel more settled without adding any new features.
- After calmness is working, the next lever is character, not structure. Tiny changes to facial proportion or a single tail gesture can add personality without destabilizing the silhouette.
- After character is working, proportion restraint becomes the next lever again. Small reductions in head or beak mass can make the bird feel cleaner and less blunt without changing the pose.
- After restraint, look for elegance rather than reduction for its own sake. Slightly cleaner spacing around the face can make the bird feel more refined without making it smaller in every direction.
- After elegance, look for poise. Tiny shifts in head position and face spacing can change the bird's demeanor without asking the composition to do anything structurally different.
- After poise, look for coherence. Slightly tighter alignment between the head, eye, and beak can make the face feel more unified without changing the perch or bike.

## Failure Review

When a drawing looks bad, diagnose the failure before redrawing:

- If it looks like a blob, the silhouette is too merged.
- If it looks like a bird but not a pelican, the beak is too short or too generic.
- If it looks like a pelican but not a bike, the wheels and frame are too weak.
- If it looks stiff, the pose is too symmetrical.
- If it looks overworked, remove detail and return to larger shapes.

## Version-Specific Lessons

- `version1` / `final`: the bird and bike read as disconnected objects and the bicycle structure is too weak.
- `v3`: stronger body and wheel mass, but the bike frame is still buried under the pelican.
- `v4`: frame geometry exists in the command plan, but the body overlap still prevents fast readability.
- `v5`: better composition separation, but it still relies too much on primitives that do not survive export well enough.
- `v6`: first structurally successful pass because the bike moved to explicit line shapes.
- `v7`: improved `v6` by thickening the most important frame edges and preserving clearer separation between pelican, seat, and frame.
- `v8`: refined the geometry rather than just the thickness, using a tighter frame and cleaner seat/handlebar placement for a more coherent bike.
- `v9`: kept the compact `v8` geometry but improved the riding pose with more asymmetric leg placement.
- `v10`: kept the `v9` pose and added a clearer neck/pouch contour so the pelican reads as a bird with anatomy rather than a body plus a separate head.
- `v11`: simplified the neck/pouch treatment from `v10`, proving that cleaner long contours beat fussier segmented ones for this style.
- `v12`: refined scale rather than structure, showing that a slightly smaller head and shorter beak can improve unity without changing the working composition.
- `v13`: showed that once the body, head, and bike already work, a single deliberate connector contour can improve head-to-body integration better than another large redraw.
- `v14`: showed that a slightly lower, more perched body placement can improve the rider read, provided the bike frame still stays visible underneath.
- `v15`: showed that, after the perch is working, tiny refinements to head attitude and pedal contact can produce a cleaner, more intentional rider read without changing the overall composition.
- `v16`: showed that tiny placement changes can also affect mood; a calmer head and slightly more settled body placement made the rider feel less twitchy while preserving the same simple structure.
- `v17`: showed that, after calmness is established, very small face and tail adjustments can add character while keeping the same stable bike and body arrangement.
- `v18`: showed that character can then be tightened through restraint; a slightly smaller head/beak relationship made the pelican feel cleaner without needing any new detail.
- `v19`: showed that restraint can become elegance; slightly cleaner head and beak spacing made the bird feel more refined without changing the bike or perch.
- `v20`: showed that elegance can then become poise; tiny head-placement changes made the pelican feel more self-possessed while preserving the same stable setup.
- `v21`: showed that poise can be tightened into coherence; a slightly tighter head, eye, and beak relationship made the face feel more unified while preserving the same calm baseline.

## Additional Resources

### Reference Notes

- `references/pelican-anatomy.md` - Pelican shape notes, reference checklist, and license-safe usage guidance.
