# One gallery. The open case sits just outside the final view.
# The camera stays put and only turns, from the case to the three frames.
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

ROOT = r"C:\Users\Maksim\Projects\clave нейп=ропродакшен"
CASE_BLEND = os.path.join(ROOT, "blender", "clave-mixed-case.blend")
OUT = os.path.join(ROOT, "site", "media", "journey")
BLEND = os.path.join(ROOT, "blender", "clave-journey.blend")
os.makedirs(OUT, exist_ok=True)

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 24
scene.render.fps = 24
scene.render.resolution_x = 1600
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "JPEG"
scene.render.image_settings.quality = 86
scene.render.image_settings.color_mode = "RGB"
ee = scene.eevee
if hasattr(ee, "taa_render_samples"):
    ee.taa_render_samples = 32

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
preview = "preview" in argv
frames = [int(x) for x in argv if x.isdigit()] or list(range(1, 25))
if preview:
    scene.render.resolution_percentage = 50
    if hasattr(ee, "taa_render_samples"):
        ee.taa_render_samples = 12

SKIP = {"CAMERA hero", "CAMERA target", "TABLE"}


def purge_old_case():
    doomed = [obj for obj in bpy.data.objects if obj.name.startswith("CASE") or obj.name.startswith("KEY") or obj.name.startswith("LID") or obj.name.startswith("card") or obj.name.startswith("LIGHT ") or obj.name.startswith("HINGE") or obj.name == "TABLE"]
    for obj in doomed:
        bpy.data.objects.remove(obj, do_unlink=True)


purge_old_case()

with bpy.data.libraries.load(CASE_BLEND, link=False) as (src, dst):
    dst.objects = [name for name in src.objects if name not in SKIP]

imported = [obj for obj in dst.objects if obj is not None]
for obj in imported:
    scene.collection.objects.link(obj)

root = bpy.data.objects.new("CASE world", None)
scene.collection.objects.link(root)
for obj in imported:
    if obj.parent is None and obj.type != "CAMERA":
        obj.parent = root
        obj.matrix_parent_inverse = Matrix.Identity(4)

# Lid faces the lens. The case sits to the right of the final gallery view.
root.location = (1.55, -1.7, 0.0)
root.rotation_euler.z = math.radians(-90)
bpy.context.view_layer.update()

camera = bpy.data.objects["Hall camera"]
if camera.animation_data:
    camera.animation_data_clear()
for constraint in list(camera.constraints):
    camera.constraints.remove(constraint)
camera.rotation_mode = "XYZ"
camera.data.dof.use_dof = False
camera.data.lens = 24

# Close on the open case, then settle into the approved hall viewpoint.
start = root.matrix_world @ Vector((0.55, -0.78, 0.48))
end = Vector((-0.55, -3.15, 1.05))
case_look = root.matrix_world @ Vector((-0.28, -0.02, 0.16))
hall_look = Vector((0.45, 4.15, 1.45))


def ease(t):
    return t * t * (3.0 - 2.0 * t)


for frame in range(1, 25):
    t = ease((frame - 1) / 23.0)
    loc = start.lerp(end, t)
    # Look stays on the case while it is still in front of the lens,
    # then settles on the frames. The handoff is what keeps the room continuous.
    look = case_look.lerp(hall_look, ease(max(0.0, (t - 0.18) / 0.82)))
    scene.frame_set(frame)
    camera.location = loc
    camera.rotation_euler = (look - loc).to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = 24
    camera.keyframe_insert("location", frame=frame)
    camera.keyframe_insert("rotation_euler", frame=frame)
    camera.data.keyframe_insert("lens", frame=frame)

action = camera.animation_data.action if camera.animation_data else None
if action is not None:
    curves = getattr(action, "fcurves", None)
    if curves:
        for curve in curves:
            for point in curve.keyframe_points:
                point.interpolation = "LINEAR"

scene.frame_set(1)
print("START", tuple(round(v, 3) for v in start))
print("CASE", tuple(round(v, 3) for v in case_look))
bpy.ops.wm.save_as_mainfile(filepath=BLEND)

for frame in frames:
    scene.frame_set(frame)
    scene.render.filepath = os.path.join(OUT, f"frame-{frame:02d}.jpg")
    bpy.ops.render.render(write_still=True)
    print("FRAME", frame)
