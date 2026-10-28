# Clave homepage hero sequence v2: open case -> gallery -> process -> human direction -> open case CTA.
import math
import os
import sys
import bpy
from mathutils import Vector

ROOT = r"C:\Users\Maksim\Projects\clave нейп=ропродакшен"
SRC = os.path.join(ROOT, "blender", "clave-journey.blend")
BLEND = os.path.join(ROOT, "blender", "clave-hero-journey-v2.blend")
OUT = os.path.join(ROOT, "site", "media", "journey-v2")
PREVIEW = os.path.join(ROOT, "preview", "hero-sequence-v2")
os.makedirs(OUT, exist_ok=True)
os.makedirs(PREVIEW, exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=SRC)
scene = bpy.context.scene
camera = scene.camera
root = bpy.data.objects["CASE world"]
hinge = bpy.data.objects["LID hinge"]

# Keep the archival case, turn it slightly toward the viewer and open the lid a little further.
root.rotation_euler.z = math.radians(-82)
hinge.rotation_euler.x = math.radians(-78)
scene.frame_start = 1
scene.frame_end = 52
scene.render.fps = 24
scene.render.resolution_x = 1600
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "JPEG"
scene.render.image_settings.quality = 82
scene.render.image_settings.color_mode = "RGB"
scene.render.filepath = os.path.join(OUT, "frame-")

# Restore readable gallery lighting through the full journey.
for name, energy in (("Light left", 82), ("Light center", 118), ("Light right", 92), ("Fill", 18)):
    obj = bpy.data.objects.get(name)
    if obj and obj.type == "LIGHT":
        obj.data.energy = energy

# Hide incidental seating and foliage while the case and process table are in view.
for name in ("Bench seat", "Bench plinth", "Planter", "Tree trunk", "Tree crown", "Tree crown side"):
    obj = bpy.data.objects.get(name)
    if obj:
        obj.hide_render = True

# Camera stays in the gallery for the story beats, with a small move toward the films.
gallery_loc = Vector((-0.55, -3.15, 1.05))
gallery_look = Vector((0.45, 4.15, 1.45))
gallery_close_loc = Vector((-0.48, -1.95, 1.20))
gallery_close_look = Vector((0.45, 4.15, 1.45))
gallery_detail_loc = Vector((-0.15, -1.75, 1.34))
gallery_detail_look = Vector((0.82, 4.15, 1.50))
scene.frame_set(1)
bpy.context.view_layer.update()
case_loc = camera.matrix_world.translation.copy()
case_look = case_loc + camera.matrix_world.to_3x3() @ Vector((0.0, 0.0, -8.0))
keys = [
    (24, gallery_loc, gallery_look),
    (28, gallery_loc, gallery_look),
    (33, gallery_close_loc, gallery_close_look),
    (37, gallery_close_loc, gallery_close_look),
    (42, gallery_detail_loc, gallery_detail_look),
    (46, gallery_detail_loc, gallery_detail_look),
    (50, case_loc, case_look),
    (52, case_loc, case_look),
]

def smooth(t):
    return t * t * (3.0 - 2.0 * t)

def pose(frame):
    for idx in range(len(keys) - 1):
        a, b = keys[idx], keys[idx + 1]
        if frame <= b[0]:
            t = smooth((frame - a[0]) / (b[0] - a[0])) if b[0] != a[0] else 0
            return a[1].lerp(b[1], t), a[2].lerp(b[2], t)
    return keys[-1][1], keys[-1][2]

camera.data.dof.use_dof = False
camera.data.lens = 24
for frame in range(25, 53):
    loc, look = pose(frame)
    camera.location = loc
    camera.rotation_euler = (look - loc).to_track_quat("-Z", "Y").to_euler()
    camera.keyframe_insert(data_path="location", frame=frame)
    camera.keyframe_insert(data_path="rotation_euler", frame=frame)
    camera.data.keyframe_insert(data_path="lens", frame=frame)

# Keep the case open at the final screen; avoid the previous animation's closing lid.
for frame, degrees in ((1, -78), (24, -78), (33, -78), (42, -78), (50, -78), (52, -78)):
    scene.frame_set(frame)
    hinge.rotation_euler.x = math.radians(degrees)
    hinge.keyframe_insert(data_path="rotation_euler", frame=frame)

scene.frame_set(1)
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=BLEND)

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
preview_mode = "preview" in argv
all_mode = "all" in argv
frames = [1, 12, 24, 33, 42, 52] if preview_mode else (list(range(1, 53)) if all_mode else [1, 24, 33, 42, 52])
if preview_mode:
    scene.render.resolution_percentage = 50
    scene.eevee.taa_render_samples = 16
else:
    scene.render.resolution_percentage = 100
    scene.eevee.taa_render_samples = 48
for frame in frames:
    scene.frame_set(frame)
    if preview_mode:
        scene.render.filepath = os.path.join(PREVIEW, f"hero-{frame:02d}.jpg")
    else:
        scene.render.filepath = os.path.join(OUT, f"frame-{frame:02d}.jpg")
    bpy.ops.render.render(write_still=True)
    print("HERO_FRAME", frame, scene.render.filepath)
