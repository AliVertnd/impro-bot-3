# Clave — visual direction v3: Black Gold Gallery

**Active direction.** The owner selected the first site assembly and the dark three-frame gallery reference. Continue from the current `site/` version and refine it in place.

## Brand idea

Clave is a neuroproduction studio that can make any video. Black Gold Gallery is the visual world of the site: a dark cinematic archive where every film has its own world inside one gallery system. The attached reference with three gold-edged black frames is the anchor for the work section.

Brands and advertising agencies are equally important audiences. The site should communicate direction, visual craft and end-to-end production, while keeping formats open. Corporate training is not a featured service.

## Visual system

- **Base:** near-black, charcoal and deep brown, with restrained warm brass/gold edges and amber practical light.
- **Materials:** blackened wood, dark lacquer, glass and a reflective dark floor. Keep metallic accents subtle; no ornate Baroque decoration or bright luxury gold.
- **Frames:** deep black cinematic frames with a narrow warm edge. Keep geometry and spacing consistent across the hall, Work page and project detail pages.
- **Film worlds:** each frame can show a different genre—product/beauty, automotive, architecture/place, or another brief. The gallery is the brand system; the images demonstrate range.
- **Logo:** retain the compact key symbol with CLAVE wordmark. Use it as a small signature, not a decorative motif repeated across the site.
- **Typography:** editorial serif for display headlines; clear neutral sans-serif for body text; small uppercase labels for film type, duration and status.

## Hero and gallery

Keep the first assembly as the working baseline: the existing dark archive case in `site/media/hero.png`, then the gallery reveal in `site/media/hall-render.png`. Preserve this relationship while improving framing, hierarchy, copy and responsive behavior. Do not substitute the cardboard-box camera fly-through.

The selected gallery composition has three vertical frames, warm edge lighting and a reflective floor. On mobile, retain the same three films as readable cards or stacked panels; do not force a desktop WebGL hall into a narrow viewport.

## Pages and content

- **Home:** case/film hero, followed by the gallery reveal, then open-ended capabilities, process and a clear inquiry CTA.
- **Work:** use the first-build three-film set (Veil, Night Road, Above the Clouds) until the owner approves changes. Clearly label visual concepts; never imply client status or outcomes that are not confirmed.
- **Project details:** keep a shared dark frame, film title, type/duration/status, task, idea, Clave's role and deliverables. Use the actual film still or a concept image.
- **Capabilities:** advertising and TV, brand/image films, director-led work, series, and any video task. Do not give corporate training its own highlight or card.
- **Studio/contact:** explain the directing and production process in plain language; the inquiry form should only promise delivery after a real contact endpoint is connected.

## Motion and fallback

- The first build already has a scroll-linked transition into the gallery. Refine its camera feel and timing without scroll-jacking or hiding content.
- Keep links and text usable while WebGL loads; use the static hero and hall images as fallbacks.
- Respect `prefers-reduced-motion`, touch devices, WebGL failure and lower-powered GPUs.
- Any real 3D scene should support the black gallery/frames direction. Do not connect the cardboard-lot scene or its 6-second fly-through to the site.

## Existing assets to preserve as the base

- `site/media/hero.png` — first-screen black archive case.
- `site/media/hall-render.png` — selected three-frame gold-lit gallery reference.
- `site/media/archive-case.glb` — existing dark case model used by the first assembly; inspect before replacing.
- `site/media/art-left.jpg`, `art-mid.jpg`, `art-right.jpg` — three gallery films.
- `blender/clave-hall.blend` and `blender/clave_hall_scene.py` — existing hall scene.

Cardboard/western assets and prototypes in `preview/` and the western Blender scene are archived explorations; keep them for history, but do not use them in the active site.
