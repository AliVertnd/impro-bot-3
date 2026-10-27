# Clave hall: three brass frames in a dark gallery, matching the reference photograph.
import math
import os

import bpy

ROOT = r"C:\Users\Maksim\Projects\clave нейп=ропродакшен"
MEDIA = os.path.join(ROOT, "site", "media")
OUT = os.path.join(MEDIA, "hall-render.png")
BLEND = os.path.join(ROOT, "blender", "clave-hall.blend")

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.filepath = OUT
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.view_settings.view_transform = "AgX"
scene.view_settings.exposure = -0.15
ee = scene.eevee
if hasattr(ee, "taa_render_samples"):
    ee.taa_render_samples = 96
if hasattr(ee, "use_raytracing"):
    ee.use_raytracing = True

world = bpy.data.worlds.new("Hall")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.012, 0.009, 0.007, 1)
bg.inputs["Strength"].default_value = 0.04


def set_in(node, name, value):
    sock = node.inputs.get(name)
    if sock is not None:
        sock.default_value = value


def material(name, color, rough=0.5, metal=0.0, emit=0.0, coat=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    set_in(bsdf, "Base Color", (*color, 1))
    set_in(bsdf, "Roughness", rough)
    set_in(bsdf, "Metallic", metal)
    set_in(bsdf, "Coat Weight", coat)
    set_in(bsdf, "Coat Roughness", 0.25)
    set_in(bsdf, "Emission Color", (*color, 1))
    set_in(bsdf, "Emission Strength", emit)
    return mat


def stone(name, dark, light, rough):
    mat = material(name, dark, rough, 0.04, 0.0, 0.08)
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    coord = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (1.6, 1.6, 1.6)
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 3.2
    noise.inputs["Detail"].default_value = 6.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.38
    ramp.color_ramp.elements[0].color = (*dark, 1)
    ramp.color_ramp.elements[1].position = 0.78
    ramp.color_ramp.elements[1].color = (*light, 1)
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.12
    nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def cube(name, loc, dims, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("Edge", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    return obj


def image_plane(name, path, loc, w, h):
    image = bpy.data.images.load(path, check_existing=True)
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = image
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    if "Emission Color" in bsdf.inputs:
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
    set_in(bsdf, "Emission Strength", 1.35)
    set_in(bsdf, "Roughness", 0.45)
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(
        [(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)],
        [],
        [(0, 1, 2, 3)],
    )
    uv = mesh.uv_layers.new(name="UVMap")
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            co = mesh.vertices[mesh.loops[li].vertex_index].co
            uv.data[li].uv = ((co.x / w) + 0.5, (co.z / h) + 0.5)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    obj.data.materials.append(mat)
    return obj


floor_mat = stone("Dark stone floor", (0.012, 0.01, 0.009), (0.045, 0.032, 0.022), 0.16)
wall_mat = stone("Dark stone wall", (0.008, 0.007, 0.006), (0.03, 0.022, 0.016), 0.62)
brass = material("Aged brass", (0.62, 0.42, 0.16), 0.28, 1.0, 0.0, 0.15)
ink = material("Black frame", (0.006, 0.005, 0.004), 0.42, 0.0, 0.0, 0.04)
cloth = material("Black upholstery", (0.01, 0.009, 0.008), 0.72)
leaf = material("Dark foliage", (0.015, 0.02, 0.012), 0.7)
planter = material("Planter", (0.02, 0.016, 0.013), 0.55)

# Room. Camera looks toward +Y.
cube("Floor", (0, 2.2, -0.04), (16, 14, 0.08), floor_mat)
cube("Back wall", (0, 6.15, 2.4), (16, 0.18, 4.8), wall_mat)
cube("Left wall", (-6.2, 2.2, 2.4), (0.18, 14, 4.8), wall_mat)
cube("Right wall", (6.2, 2.2, 2.4), (0.18, 14, 4.8), wall_mat)
cube("Ceiling", (0, 2.2, 4.85), (16, 14, 0.12), wall_mat)

# Warm vertical light on the left wall, as in the reference.
glow = material("Wall light", (1.0, 0.72, 0.38), 0.4, 0.0, 8.0)
cube("Left light strip", (-6.05, 2.6, 2.3), (0.02, 0.08, 2.4), glow, 0)


def gallery_frame(name, x, width, height, bottom, image_name):
    y = 4.15
    cz = bottom + height / 2
    outer = 0.09
    brass_w = 0.018
    depth = 0.11
    cube(name + " back", (x, y + 0.04, cz), (width, 0.03, height), ink)
    cube(name + " top", (x, y, cz + height / 2), (width + outer, depth, outer), ink, 0.004)
    cube(name + " bottom", (x, y, cz - height / 2), (width + outer, depth, outer), ink, 0.004)
    cube(name + " left", (x - width / 2, y, cz), (outer, depth, height), ink, 0.004)
    cube(name + " right", (x + width / 2, y, cz), (outer, depth, height), ink, 0.004)
    inset = outer * 0.42
    cube(name + " brass top", (x, y - 0.03, cz + height / 2 - inset), (width - 0.04, 0.025, brass_w), brass, 0.002)
    cube(name + " brass bottom", (x, y - 0.03, cz - height / 2 + inset), (width - 0.04, 0.025, brass_w), brass, 0.002)
    cube(name + " brass left", (x - width / 2 + inset, y - 0.03, cz), (brass_w, 0.025, height - inset * 2), brass, 0.002)
    cube(name + " brass right", (x + width / 2 - inset, y - 0.03, cz), (brass_w, 0.025, height - inset * 2), brass, 0.002)
    image_plane(
        name + " picture",
        os.path.join(MEDIA, image_name),
        (x, y - 0.045, cz),
        width - 0.16,
        height - 0.16,
    )
    strip = material(name + " wash", (1.0, 0.75, 0.42), 0.3, 0.0, 4.0)
    cube(name + " side light", (x + width / 2 + 0.16, y + 0.05, cz), (0.015, 0.02, height * 0.72), strip)


gallery_frame("Left", -2.35, 2.05, 2.85, 0.02, "art-left.jpg")
gallery_frame("Center", 0.2, 2.35, 3.05, 0.02, "art-mid.jpg")
gallery_frame("Right", 2.85, 2.15, 3.15, 0.02, "art-right.jpg")

cube("Bench seat", (-2.9, 0.35, 0.42), (1.7, 0.58, 0.16), cloth, 0.012)
cube("Bench plinth", (-2.9, 0.35, 0.14), (1.35, 0.46, 0.2), brass, 0.004)
cube("Planter", (-4.55, 2.15, 0.22), (0.7, 0.42, 0.44), planter, 0.008)
bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.025, depth=0.55, location=(-4.55, 2.15, 0.62))
trunk = bpy.context.object
trunk.name = "Tree trunk"
trunk.data.materials.append(leaf)
bpy.ops.mesh.primitive_ico_sphere_add(radius=0.22, location=(-4.7, 2.15, 0.95), subdivisions=2)
crown = bpy.context.object
crown.name = "Tree crown"
crown.scale = (1.6, 0.9, 0.85)
bpy.ops.object.transform_apply(scale=True)
crown.data.materials.append(leaf)
bpy.ops.mesh.primitive_ico_sphere_add(radius=0.14, location=(-4.35, 2.2, 1.05), subdivisions=1)
crown2 = bpy.context.object
crown2.name = "Tree crown side"
crown2.data.materials.append(leaf)


def area(name, loc, energy, color, size, target):
    bpy.ops.object.light_add(type="AREA", location=loc)
    lamp = bpy.context.object
    lamp.name = name
    lamp.data.energy = energy
    lamp.data.color = color
    lamp.data.shape = "RECTANGLE"
    lamp.data.size = size
    lamp.data.size_y = size * 0.45
    direction = __import__("mathutils").Vector(target) - lamp.location
    lamp.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    return lamp


area("Light left", (-2.35, 1.6, 4.15), 90, (1.0, 0.72, 0.42), 0.9, (-2.35, 4.1, 1.7))
area("Light center", (0.2, 1.4, 4.25), 110, (1.0, 0.7, 0.4), 1.05, (0.2, 4.1, 1.8))
area("Light right", (2.85, 1.5, 4.2), 100, (1.0, 0.66, 0.36), 1.0, (2.85, 4.1, 1.9))
area("Fill", (0.2, -0.4, 1.8), 12, (0.7, 0.74, 0.85), 2.4, (0.2, 4, 1.5))

bpy.ops.object.camera_add(location=(-0.55, -3.15, 1.05))
camera = bpy.context.object
camera.name = "Hall camera"
camera.data.lens = 24
camera.data.dof.use_dof = True
camera.data.dof.focus_distance = 7.4
camera.data.dof.aperture_fstop = 5.6
scene.camera = camera
aim = bpy.data.objects.new("Aim", None)
bpy.context.collection.objects.link(aim)
aim.location = (0.45, 4.15, 1.45)
track = camera.constraints.new("TRACK_TO")
track.target = aim
track.track_axis = "TRACK_NEGATIVE_Z"
track.up_axis = "UP_Y"

bpy.ops.wm.save_as_mainfile(filepath=BLEND)
bpy.ops.render.render(write_still=True)
print("HALL", OUT)
