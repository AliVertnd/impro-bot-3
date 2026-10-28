# Continuation of the same room, after the gallery.
# Frame 1 matches the end of the first turn. Later frames lower to the table,
# turn into the quiet hall, then come back to the case as it closes.
import math
import os
import sys

import bpy
from mathutils import Vector

ROOT = r"C:\Users\Maksim\Projects\clave нейп=ропродакшен"
OUT = os.path.join(ROOT, "site", "media", "journey")
os.makedirs(OUT, exist_ok=True)

scene = bpy.context.scene
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "JPEG"
scene.render.image_settings.quality = 93
scene.render.image_settings.color_mode = "RGB"
ee = scene.eevee
if hasattr(ee, "taa_render_samples"):
    ee.taa_render_samples = 64
if hasattr(ee, "use_raytracing"):
    ee.use_raytracing = True

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
frames = [int(x) for x in argv if x.isdigit()] or list(range(1, 29))

camera = bpy.data.objects["Hall camera"]
if camera.animation_data:
    camera.animation_data_clear()
for constraint in list(camera.constraints):
    camera.constraints.remove(constraint)
camera.rotation_mode = "XYZ"
camera.data.dof.use_dof = False
camera.data.lens = 24

fill = bpy.data.objects.get("Fill")
if fill and fill.type == "LIGHT":
    fill.data.energy = 0

for name in ("Bench seat", "Bench plinth", "Planter", "Tree trunk", "Tree crown", "Tree crown side"):
    obj = bpy.data.objects.get(name)
    if obj:
        obj.hide_render = True

root = bpy.data.objects["CASE world"]
hinge = bpy.data.objects["LID hinge"]


def material_brass():
    mat = bpy.data.materials.get("Passage brass")
    if mat:
        return mat
    mat = bpy.data.materials.new("Passage brass")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        for name, value in (
            ("Base Color", (0.55, 0.36, 0.14, 1)),
            ("Metallic", 1.0),
            ("Roughness", 0.28),
        ):
            sock = bsdf.inputs.get(name)
            if sock is not None:
                sock.default_value = value
    return mat


def material_oak():
    mat = bpy.data.materials.get("Passage oak")
    if mat:
        return mat
    mat = bpy.data.materials.new("Passage oak")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        for name, value in (
            ("Base Color", (0.008, 0.005, 0.004, 1)),
            ("Roughness", 0.55),
        ):
            sock = bsdf.inputs.get(name)
            if sock is not None:
                sock.default_value = value
    return mat


def block(name, loc, dims, mat):
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(scale=True)
    obj.data.materials.append(mat)
    return obj


# A low oak board in the foreground, three brass slips, the key already on the floor nearby.
board = Vector((0.85, -2.35, 0.012))
block("PASS board", board, (0.92, 0.34, 0.02), material_oak())
for index, name in enumerate(("PASS замысел", "PASS мир", "PASS мастер")):
    block(name, (board.x - 0.26 + index * 0.26, board.y, 0.028), (0.2, 0.07, 0.008), material_brass())

lamp = bpy.data.objects.get("PASS lamp")
if lamp is None:
    light = bpy.data.lights.new("PASS lamp", "AREA")
    lamp = bpy.data.objects.new("PASS lamp", light)
    bpy.context.collection.objects.link(lamp)
lamp.data.energy = 18
lamp.data.color = (1.0, 0.72, 0.46)
lamp.data.size = 0.7
lamp.location = (board.x, board.y, 1.15)
lamp.rotation_euler = (Vector((board.x, board.y, 0.03)) - lamp.location).to_track_quat("-Z", "Y").to_euler()

# Same pose as journey frame 24, then the table, the quiet wall, the closing case.
gallery_loc = Vector((-0.55, -3.15, 1.05))
gallery_look = Vector((0.45, 4.15, 1.45))
table_loc = Vector((1.05, -3.2, 0.62))
table_look = Vector((board.x, board.y, 0.04))
hall_loc = Vector((-0.15, 0.15, 1.02))
hall_look = Vector((-5.6, 2.5, 1.45))
lip = root.matrix_world @ Vector((0.0, -0.16, 0.18))
case_loc = root.matrix_world @ Vector((0.22, -1.15, 0.52))
case_look = lip

# (frame, location, look, hinge degrees) across 28 frames.
keys = [
    (1, gallery_loc, gallery_look, -68),
    (8, table_loc, table_look, -68),
    (18, hall_loc, hall_look, -68),
    (28, case_loc, case_look, -22),
]


def pose(frame):
    span = keys[-1][0] - keys[0][0]
    for index in range(len(keys) - 1):
        a = keys[index]
        b = keys[index + 1]
        if frame <= b[0]:
            t = 0 if b[0] == a[0] else (frame - a[0]) / (b[0] - a[0])
            t = t * t * (3 - 2 * t)
            loc = a[1].lerp(b[1], t)
            look = a[2].lerp(b[2], t)
            hinge_deg = a[3] + (b[3] - a[3]) * t
            return loc, look, hinge_deg
    last = keys[-1]
    return last[1], last[2], last[3]


for frame in frames:
    loc, look, hinge_deg = pose(frame)
    camera.location = loc
    camera.rotation_euler = (look - loc).to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = 24
    hinge.rotation_euler.x = math.radians(hinge_deg)
    for light_name, near, far in (("Light left", 90, 6), ("Light center", 110, 6), ("Light right", 100, 6)):
        light = bpy.data.objects.get(light_name)
        if light and light.type == "LIGHT":
            light.data.energy = near if frame < 4 else far
    for extra in ("LIGHT fill", "LIGHT key", "LIGHT rim"):
        extra_light = bpy.data.objects.get(extra)
        if extra_light and extra_light.type == "LIGHT" and frame >= 4:
            extra_light.data.energy = 0
    stone = bpy.data.materials.get("Dark stone floor")
    if stone and stone.node_tree:
        bsdf = stone.node_tree.nodes.get("Principled BSDF")
        sock = bsdf.inputs.get("Roughness") if bsdf else None
        if sock is not None:
            sock.default_value = 0.62 if 5 <= frame <= 16 else 0.16
    bpy.context.view_layer.update()
    scene.render.filepath = os.path.join(OUT, f"frame-{frame + 24:02d}.jpg")
    bpy.ops.render.render(write_still=True)
    print("SHOT", frame + 24)
