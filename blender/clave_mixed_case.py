# Clave mixed hero: black oak case (premium frame) with an oilfield film
# and archival cards inside (authored stories). No camera animation.
import math
import os

import bpy
from mathutils import Matrix, Vector

TEX = r"C:\Users\Maksim\Documents\Codex\2026-10-23\nt\work\tex"
OUT = r"C:\Users\Maksim\Documents\Codex\2026-10-23\nt\outputs"
BLEND = os.path.join(OUT, "clave-mixed-case.blend")
PNG = os.path.join(OUT, "clave-mixed-case-preview.png")

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1600
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.film_transparent = False
scene.render.filepath = PNG
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.view_settings.view_transform = "AgX"
scene.view_settings.exposure = 0.15
ee = scene.eevee
if hasattr(ee, "taa_render_samples"):
    ee.taa_render_samples = 64
if hasattr(ee, "use_raytracing"):
    ee.use_raytracing = True

world = bpy.data.worlds.new("DarkRoom")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.008, 0.006, 0.005, 1)
bg.inputs["Strength"].default_value = 0.08


def set_in(node, name, value):
    sock = node.inputs.get(name)
    if sock is not None:
        sock.default_value = value


def finish(obj, mat, bevel=0.0015):
    if mat is not None:
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
    if bevel and obj.type == "MESH":
        mod = obj.modifiers.new("Wear", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = "ANGLE"
    return obj


def cube(name, loc, dims, mat, bevel=0.0015):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(scale=True)
    return finish(obj, mat, bevel)


def cylinder(name, loc, radius, depth, mat, rot=(0, 0, 0), verts=24, bevel=0.0008):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=verts, radius=radius, depth=depth, location=loc, rotation=rot
    )
    obj = bpy.context.object
    obj.name = name
    return finish(obj, mat, bevel)


def adopt(obj, parent):
    matrix = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = matrix
    return obj


def wood(name, dark, light, scale_y, rough, coat):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    set_in(bsdf, "Roughness", rough)
    set_in(bsdf, "Metallic", 0.0)
    set_in(bsdf, "Coat Weight", coat)
    set_in(bsdf, "Coat Roughness", 0.42)
    coord = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (1.4, scale_y, 0.6)
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 4.0
    noise.inputs["Detail"].default_value = 7.0
    noise.inputs["Roughness"].default_value = 0.62
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.32
    ramp.color_ramp.elements[0].color = (*dark, 1)
    ramp.color_ramp.elements[1].position = 0.78
    ramp.color_ramp.elements[1].color = (*light, 1)
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.16
    bump.inputs["Distance"].default_value = 0.02
    nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def metal(name, color, rough):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    set_in(bsdf, "Base Color", (*color, 1))
    set_in(bsdf, "Metallic", 1.0)
    set_in(bsdf, "Roughness", rough)
    return mat


def flat(name, color, rough):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    set_in(bsdf, "Base Color", (*color, 1))
    set_in(bsdf, "Roughness", rough)
    set_in(bsdf, "Metallic", 0.0)
    return mat


def image_mat(name, path, glow):
    image = bpy.data.images.load(path, check_existing=True)
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = image
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    set_in(bsdf, "Roughness", 0.55)
    set_in(bsdf, "Emission Color", (1, 1, 1, 1))
    set_in(bsdf, "Emission Strength", glow)
    if "Emission Color" in bsdf.inputs:
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
    return mat, image


def image_plane(name, path, loc, max_w, max_h, glow, rot=(0, 0, 0)):
    mat, image = image_mat(name + " print", path, glow)
    aspect = image.size[0] / image.size[1]
    if max_w / max_h > aspect:
        height = max_h
        width = height * aspect
    else:
        width = max_w
        height = width / aspect
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(
        [(-width / 2, -height / 2, 0), (width / 2, -height / 2, 0), (width / 2, height / 2, 0), (-width / 2, height / 2, 0)],
        [],
        [(0, 1, 2, 3)],
    )
    uv = mesh.uv_layers.new(name="UVMap")
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            vertex = mesh.vertices[mesh.loops[li].vertex_index].co
            uv.data[li].uv = ((vertex.x / width) + 0.5, (vertex.y / height) + 0.5)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = rot
    obj.data.materials.append(mat)
    return obj, width, height


oak = wood("Black oak case", (0.003, 0.002, 0.0015), (0.020, 0.012, 0.007), 11.0, 0.62, 0.06)
table_wood = wood("Dark table", (0.006, 0.004, 0.003), (0.028, 0.016, 0.009), 16.0, 0.72, 0.03)
brass = metal("Aged brass", (0.38, 0.26, 0.09), 0.38)
ink = flat("Black recess", (0.012, 0.009, 0.008), 0.86)
kraft = flat("Archival kraft", (0.34, 0.24, 0.14), 0.84)

# Table fills the lower frame. Top surface is z = 0.
cube("TABLE", (0, 0.02, -0.045), (3.4, 2.4, 0.09), table_wood, 0.004)

# Hollow case. The cavity stays open so the cards sit on a dark floor, not inside the wood.
cube("CASE bottom", (0, 0, 0.028), (0.74, 0.48, 0.056), oak, 0.0022)
cube("CASE inner floor", (0, 0, 0.060), (0.684, 0.424, 0.006), ink, 0.0004)
for x in (-0.351, 0.351):
    cube("CASE side wall", (x, 0, 0.086), (0.022, 0.424, 0.048), oak, 0.0008)
cube("CASE front wall", (0, -0.229, 0.086), (0.74, 0.022, 0.048), oak, 0.0008)
cube("CASE back wall", (0, 0.229, 0.082), (0.74, 0.022, 0.040), oak, 0.0008)

cube("LATCH plate", (0, -0.252, 0.055), (0.046, 0.008, 0.026), brass, 0.0006)
cylinder("KEYHOLE", (0, -0.257, 0.052), 0.0042, 0.006, ink, rot=(math.pi / 2, 0, 0), verts=16, bevel=0)
for x in (-0.22, 0.22):
    cylinder("HINGE barrel", (x, 0.242, 0.104), 0.007, 0.034, brass, rot=(0, math.pi / 2, 0), verts=16)

bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0.240, 0.104))
hinge = bpy.context.object
hinge.name = "LID hinge"
lid = cube("LID panel", (0, 0.005, 0.120), (0.74, 0.47, 0.024), oak, 0.002)
adopt(lid, hinge)
screen, screen_w, screen_h = image_plane(
    "LID film",
    os.path.join(TEX, "film-oil.jpg"),
    (0, 0, 0),
    0.60,
    0.32,
    glow=0.18,
)
screen.parent = lid
screen.matrix_parent_inverse = Matrix.Identity(4)
screen.location = (0, 0, -0.020)
screen.rotation_euler = (math.pi, 0, 0)
screen.scale = (1, 1, 1)

def local_bar(name, loc, dims, mat):
    bar = cube(name, (0, 0, 0), dims, mat, 0.0003)
    bar.parent = screen
    bar.matrix_parent_inverse = Matrix.Identity(4)
    bar.location = loc
    bar.rotation_euler = (0, 0, 0)
    bar.scale = (1, 1, 1)
    return bar

local_bar("screen mat", (0, 0, -0.003), (screen_w + 0.05, screen_h + 0.04, 0.002), ink)
local_bar("frame top", (0, screen_h / 2 + 0.006, 0.0016), (screen_w + 0.028, 0.009, 0.003), brass)
local_bar("frame bottom", (0, -screen_h / 2 - 0.006, 0.0016), (screen_w + 0.028, 0.009, 0.003), brass)
local_bar("frame left", (-screen_w / 2 - 0.006, 0, 0.0016), (0.009, screen_h + 0.028, 0.003), brass)
local_bar("frame right", (screen_w / 2 + 0.006, 0, 0.0016), (0.009, screen_h + 0.028, 0.003), brass)

hinge.rotation_euler.x = math.radians(-68)

cards = [
    ("card sketch", "card-sketch.jpg", -0.20, 1.2),
    ("card field", "card-field.jpg", 0.0, -0.8),
    ("card other", "card-car.jpg", 0.20, 0.7),
]
for name, filename, x, twist in cards:
    mount = cube(name + " mount", (x, -0.02, 0.070), (0.178, 0.124, 0.005), kraft, 0.0008)
    mount.rotation_euler.z = math.radians(twist)
    photo, _, _ = image_plane(
        name,
        os.path.join(TEX, filename),
        (x, -0.02, 0.074),
        0.152,
        0.098,
        glow=0.04,
    )
    photo.rotation_euler.z = math.radians(twist)

# One key, lying on the table. The mark of the studio, not a repeating pattern.
bpy.ops.mesh.primitive_torus_add(
    major_radius=0.016,
    minor_radius=0.0036,
    major_segments=32,
    minor_segments=10,
    location=(-0.50, -0.30, 0.004),
)
bow = bpy.context.object
bow.name = "KEY bow"
finish(bow, brass, 0.0004)
cylinder("KEY shaft", (-0.455, -0.30, 0.004), 0.0032, 0.055, brass, rot=(0, math.pi / 2, 0), verts=12)
cube("KEY bit", (-0.424, -0.292, 0.004), (0.010, 0.012, 0.003), brass, 0.0003)
for obj in (bow, bpy.data.objects["KEY shaft"], bpy.data.objects["KEY bit"]):
    obj.rotation_euler.z += math.radians(-18)

# Warm practical light, as if a lamp sits just outside the frame.
def area(name, loc, energy, color, size, target):
    bpy.ops.object.light_add(type="AREA", location=loc)
    lamp = bpy.context.object
    lamp.name = name
    lamp.data.energy = energy
    lamp.data.color = color
    lamp.data.shape = "DISK"
    lamp.data.size = size
    direction = Vector(target) - lamp.location
    lamp.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    return lamp

area("LIGHT key", (0.55, -0.70, 1.15), 55, (1.0, 0.72, 0.48), 0.85, (0.0, 0.02, 0.16))
area("LIGHT rim", (-0.65, 0.55, 0.72), 22, (1.0, 0.55, 0.28), 0.45, (0.0, 0.05, 0.2))
area("LIGHT fill", (-0.35, -0.85, 0.55), 8, (0.78, 0.82, 0.92), 1.1, (0.0, 0.0, 0.12))
# A little of the film's warmth falls onto the cards.
area("LIGHT screen bounce", (0.0, 0.02, 0.28), 3.5, (1.0, 0.55, 0.28), 0.28, (0.0, -0.02, 0.07))

bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0.0, 0.02, 0.24))
target = bpy.context.object
target.name = "CAMERA target"
bpy.ops.object.camera_add(location=(0.58, -1.42, 0.82))
camera = bpy.context.object
camera.name = "CAMERA hero"
camera.data.lens = 48
camera.data.dof.use_dof = True
camera.data.dof.focus_object = target
camera.data.dof.aperture_fstop = 5.6
scene.camera = camera
track = camera.constraints.new("TRACK_TO")
track.target = target
track.track_axis = "TRACK_NEGATIVE_Z"
track.up_axis = "UP_Y"

bpy.ops.wm.save_as_mainfile(filepath=BLEND)
bpy.ops.render.render(write_still=True)
print("MIXED STILL", PNG)
