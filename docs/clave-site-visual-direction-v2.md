# Clave — visual direction v2: Cardboard Archive

**Replaces `clave-site-visual-direction-v1.md`.** Use together with the updated `КОНЦЕПТ.md` and the ordered work list in `docs/ПЛАН-РАБОТ-САЙТ.md`.

## Brand idea

Clave is a neuroproduction studio for any video project. The site feels like a working archive from a rough American oilfield loft, circa 1880–1890: a camera glides across the table and discovers an open cardboard case containing films. The box is the site's signature framing device. The films inside can belong to completely different genres and industries.

“Black Gold Gallery” is one archive/case concept, not the studio's service limit. Brands and advertising agencies are equally important audiences. Corporate learning content is not a headline category or a featured service.

## Art direction

- **Materials:** kraft corrugated board, cut folds, tape, letterpress ink, stained wood, worn paper, iron, small aged-brass details, glass lantern, dust and film grain.
- **Color:** smoke/coffee black around the set; tobacco and kraft browns; faded cream; sepia print; muted amber practical highlights. Gold is a material accent only, not the overall luxury cue.
- **Typography:** rugged slab/serif display face, straightforward sans-serif for paragraphs, mono/condensed archive labels for metadata. Headline shapes should feel printed and sturdy, never ornate.
- **Graphic language:** catalogue numbers, stamped words, archive marks, paper frames and imperfect print registration. Preserve reading contrast; distress is texture, not a text filter.
- **Subject matter:** oilfield and frontier items create a memorable set, not a cowboy costume. Props stay secondary to the carton and film imagery.

## Hero motion

1. Begin close to the rough tabletop with a low camera.
2. Travel past a map, iron gear, tool and lantern; maintain a visible sense of table depth.
3. Push toward the open kraft box; let the case silhouette fill the screen.
4. Reveal a film still in the lid and paper story cards inside.
5. Settle on a readable, stable final frame. Avoid abrupt spin, zoom, ornamental floating particles or parallax layers pretending to be real geometry.

The current Blender preview is a six-second camera move (frames 1–144 at 24 fps). Use H.264 MP4 and a poster as the first implementation. Add GLB-driven interactive 3D only if performance, touch and accessibility work are budgeted. For mobile and reduced motion, show a composed poster/crop without autoplay.

## Site composition

- **Header:** compact key mark + CLAVE wordmark; navigation for Work, Capabilities, Studio; RU/EN; one clear inquiry CTA. Key mark should look stamped/engraved and not become a separate luxury ornament.
- **Home:** cardboard-box fly-through, short universal claim, selected archive cards, breadth of formats, three-step process, inquiry CTA.
- **Work archive:** paper/cardboard mounts and catalogue labels. Each card has its own film world; the archive system remains consistent.
- **Project detail:** film frame, concept/client status, brief, creative idea, production approach and verified result/deliverables.
- **Capabilities:** commercial and TV work, brand/image films, director-led film, series and any video brief. Do not foreground corporate training.
- **Studio/contact:** creative direction and end-to-end process; short useful contact form with real submission behavior before launch.

## Image rules

- Keep the user's cardboard-box image as the primary composition reference. Rebuild the scene as 3D geometry; do not use the screenshot itself as the whole-page hero image.
- Use the generated oilfield scene as a replaceable film still, not as a claim that all Clave work looks like the oilfield.
- Use varied concept films in the archive to prove range. Mark them “Concept” until actual clients authorize publication.
- Do not use generated imagery as client proof, invent brand marks, or add unapproved performance claims.

## Interaction rules

- One primary motion effect: the hero camera move. Navigation, text and CTA work if it is disabled or still loading.
- Hover/focus may lift a paper card slightly and reveal its index; keep a visible keyboard focus and a no-hover path on touch.
- No scroll-jacking, long pinned transitions, gold glows, unnecessary 3D flips or interaction that makes text wait for a scene.
- Respect `prefers-reduced-motion`; use poster fallback when WebGL, autoplay or video decoding fails.

## Existing repository assets

- `blender/clave-western-archive.blend` — editable cardboard archive scene.
- `blender/clave-western-archive.glb` — export of the archive geometry.
- `preview/clave-western-archive-camera-flythrough.mp4` — rendered camera animation.
- `preview/clave-western-archive-preview.png` — poster/frame.
- `preview/clave-film-still.jpg` and `preview/clave-card-*.jpg` — film still and archive card imagery.

The GLB and Blender scene are stylized concept assets. Inspect the lid/card intersections and optimize textures/geometry before any interactive production use.
