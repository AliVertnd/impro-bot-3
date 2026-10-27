import bpy, math, os
from mathutils import Vector

OUT = r'C:\Users\Maksim\Documents\Codex\2026-10-23\nt\outputs'
FILM = os.path.join(OUT, 'clave-film-still.jpg')
BLEND = os.path.join(OUT, 'clave-western-archive.blend')
GLB = os.path.join(OUT, 'clave-western-archive.glb')
PNG = os.path.join(OUT, 'clave-western-archive-preview.png')
MP4 = os.path.join(OUT, 'clave-western-archive-camera-flythrough.mp4')

# Clear and configure a portable, named production scene.
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1600; scene.render.resolution_y = 1000; scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'; scene.render.image_settings.color_mode = 'RGBA'
scene.render.film_transparent = False; scene.view_settings.view_transform = 'AgX'
scene.world.color = (0.018, 0.014, 0.010)
scene.world.use_nodes = True
scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(0.008,0.006,0.004,1)
scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.18
scene.frame_start = 1; scene.frame_end = 144; scene.render.fps = 24
scene.render.filepath = PNG

def material(name, color, rough=0.7, metallic=0.0):
    m = bpy.data.materials.new(name); m.diffuse_color = (*color,1); m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value = (*color,1)
    p.inputs['Roughness'].default_value = rough; p.inputs['Metallic'].default_value = metallic
    return m

def noise_mat(name, a, b, scale=5, bump=0.18, rough=0.8):
    m=material(name,a,rough); n=m.node_tree.nodes; l=m.node_tree.links; p=n.get('Principled BSDF')
    tex=n.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=scale; tex.inputs['Detail'].default_value=3
    ramp=n.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=0.24; ramp.color_ramp.elements[0].color=(*a,1)
    ramp.color_ramp.elements[1].position=0.78; ramp.color_ramp.elements[1].color=(*b,1)
    bumpn=n.new('ShaderNodeBump'); bumpn.inputs['Strength'].default_value=bump; bumpn.inputs['Distance'].default_value=0.09
    l.new(tex.outputs['Fac'],ramp.inputs['Fac']); l.new(ramp.outputs['Color'],p.inputs['Base Color']); l.new(tex.outputs['Fac'],bumpn.inputs['Height']); l.new(bumpn.outputs['Normal'],p.inputs['Normal'])
    return m

cardboard=noise_mat('Kraft · mottled recycled board',(0.17,0.085,0.035),(0.42,0.25,0.105),9,0.22)
cardboard_edge=material('Kraft cut edge',(0.22,0.12,0.052),0.88)
wood=noise_mat('Table · rough oil-stained pine',(0.045,0.023,0.012),(0.20,0.095,0.034),3.2,0.28)
paper=noise_mat('Uncoated archival stock',(0.34,0.24,0.12),(0.63,0.48,0.29),7,0.08)
ink=material('Black letterpress ink',(0.035,0.019,0.010),0.82)
iron=material('Forged black iron',(0.045,0.038,0.029),0.32,0.72)
brass=material('Dull aged brass',(0.34,0.20,0.065),0.36,0.72)
glass=material('Lantern glass',(0.35,0.21,0.08),0.18,0.15)

def cube(name, loc, dims, mat, bevel=0.025, rot=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if rot: o.rotation_euler=rot
    if mat: o.data.materials.append(mat)
    if bevel:
        be=o.modifiers.new('Worn softened board edges','BEVEL'); be.width=bevel; be.segments=2
        o.modifiers.new('Board edge normals','WEIGHTED_NORMAL')
    return o

def cylinder(name, loc, radius, depth, mat, rot=None, vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rot or (0,0,0))
    o=bpy.context.object; o.name=name
    if mat:o.data.materials.append(mat)
    be=o.modifiers.new('Edge wear','BEVEL'); be.width=min(radius*.12,.025); be.segments=2
    o.modifiers.new('Normals','WEIGHTED_NORMAL'); return o

def text_obj(body, name, loc, size, mat, rot=(0,0,0), extrude=.001):
    c=bpy.data.curves.new(name,'FONT'); c.body=body; c.size=size; c.extrude=extrude; c.bevel_depth=.0007
    o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.location=loc; o.rotation_euler=rot; o.data.materials.append(mat); return o

def image_plane(name,path,loc,w,h,rot=(0,0,0)):
    im=bpy.data.images.load(path,check_existing=True); m=bpy.data.materials.new(name+' · printed image'); m.use_nodes=True
    n=m.node_tree.nodes; n.clear(); out=n.new('ShaderNodeOutputMaterial'); em=n.new('ShaderNodeEmission'); tx=n.new('ShaderNodeTexImage'); tx.image=im
    m.node_tree.links.new(tx.outputs['Color'],em.inputs['Color']); m.node_tree.links.new(em.outputs[0],out.inputs['Surface'])
    me=bpy.data.meshes.new(name+' plane'); me.from_pydata([(-w/2,-h/2,0),(w/2,-h/2,0),(w/2,h/2,0),(-w/2,h/2,0)],[],[(0,1,2,3)])
    uv=me.uv_layers.new(name='UVMap')
    for poly in me.polygons:
        for li in poly.loop_indices:
            v=me.vertices[me.loops[li].vertex_index].co; uv.data[li].uv=((v.x/w)+.5,(v.y/h)+.5)
    o=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(o); o.location=loc; o.rotation_euler=rot; o.data.materials.append(m); return o

# A broad, visibly rough plank table; seams and cross grain read as a loft workbench.
cube('TABLE · six-foot work surface',(0,0,-.28),(12,8,.55),wood,.08)
for i in range(9):
    y=-3.55+i*.88
    cube(f'TABLE · plank seam {i+1}',(0,y,.002),(11.94,.018,.009),ink,.003)
for x in (-4.8,-1.6,1.6,4.8):
    cube('Table · iron nail',(x,-3.4,.012),(.055,.055,.016),iron,.02)

# Open clamshell archival gallery box: real kraft panels, layered corrugated edge ribs.
BX=-.45; BY=.18
cube('BOX · lower corrugated base',(BX,BY,.31),(5.6,3.25,.55),cardboard,.07)
cube('BOX · interior floor',(BX,BY,.60),(5.36,3.02,.06),paper,.025)
for x in (BX-2.71,BX+2.71): cube('BOX · side wall',(x,BY,.77),(.18,3.12,.42),cardboard,.025)
cube('BOX · front wall',(BX,BY-1.53,.76),(5.48,.16,.40),cardboard,.025)
cube('BOX · rear hinge lip',(BX,BY+1.52,.77),(5.48,.16,.40),cardboard,.025)
# Corrugated fluting on cut front edge.
for x in [BX-2.58+i*.12 for i in range(44)]:
    cylinder('BOX · corrugated flute',(x,BY-1.615,.76),.014,.35,cardboard_edge,vertices=12)
# Box lid folded open, angled back to create the illustrated upright panel.
lid=cube('BOX · upright hinged lid',(BX,BY+1.98,2.14),(5.6,.26,3.08),cardboard,.07,rot=(math.radians(-10),0,0))
# Insert / video panel on the upright inner face.
cube('LID · printed screen frame',(BX,BY+1.78,2.19),(4.92,.09,2.30),ink,.045,rot=(math.radians(-10),0,0))
cube('LID · paper mat behind screen',(BX,BY+2.12,2.19),(4.70,.045,2.08),paper,.025,rot=(math.radians(-10),0,0))
image_plane('LID · replaceable hero film still',FILM,(BX,BY+1.38,2.19),4.48,1.97,rot=(math.pi/2,0,0))
text_obj('REAL STORIES  ·  FROM A ROUGHER AMERICA','LID · headline',(BX-1.38,BY+1.71,3.43),.16,ink,rot=(math.radians(80),0,0))
text_obj('A CLAVE MOVING-IMAGE ARCHIVE','LID · subline',(BX-1.04,BY+1.70,3.26),.105,ink,rot=(math.radians(80),0,0))
# Rough board's taped corners and faux folded hinge strips.
for x in (BX-2.53,BX+2.53):
    cube('LID · kraft corner tape',(x,BY+1.68,3.48),(.22,.035,.32),paper,.015,rot=(math.radians(-10),0,math.radians(-8 if x<BX else 8)))
for x in (BX-1.65,BX,BX+1.65):
    cylinder('BOX · paper hinge roll',(x,BY+1.56,.83),.075,.42,cardboard_edge,rot=(0,math.pi/2,0))

# Replaceable archival cards with image print, rough stock frames, and stamped titles.
labels=['FIELDS','PEOPLE','MACHINES','TOWNS']
for i,label in enumerate(labels):
    x=BX-1.89+i*1.26; y=BY-.64
    cube(f'CARD {i+1} · worn paper mount',(x,y,.66),(1.13,1.36,.055),paper,.035,rot=(0,0,math.radians((i%2-.5)*2)))
    # Same reference crop is intentionally treated as a contact-sheet base; crop UV per card isn't necessary for near-scale scene.
    image_plane(f'CARD {i+1} · {label} photo',os.path.join(OUT,f'clave-card-{label.lower()}.jpg'),(x,y,.696),.99,.72)
    text_obj(label,f'CARD {i+1} · letterpress title',(x-.34,y-.55,.71),.115,ink)
    text_obj(f'PLATE 0{i+1}',f'CARD {i+1} · plate number',(x-.29,y-.67,.71),.065,ink)

# A distinct standing shipping carton to the left, printed with a two-colour oil-derrick mark.
carton=cube('STANDING CARTON · BLACK GOLD GALLERY',(-4.35,.22,.92),(2.2,1.55,2.0),cardboard,.06,rot=(0,0,math.radians(-7)))
cube('Carton · front print panel',(-4.35,-.565,1.00),(1.92,.028,1.52),paper,.01,rot=(0,0,math.radians(-7)))
text_obj('BLACK GOLD','Carton · wordmark',(-5.11,-.59,1.47),.34,ink,rot=(math.radians(90),0,math.radians(-7)))
text_obj('GALLERY','Carton · descriptor',(-4.82,-.60,1.18),.13,ink,rot=(math.radians(90),0,math.radians(-7)))
text_obj('PEOPLE · PLACES · MACHINES', 'Carton · categories',(-5.16,-.60,.50),.074,ink,rot=(math.radians(90),0,math.radians(-7)))
# Geometric derrick illustration stamped on carton; no decorative baroque ornament.
for dx in (-.35,0,.35):
    cylinder('Carton print · derrick mast',(-4.35+dx,-.60,.82+(.48 if dx==0 else 0)),.012,.92 if dx==0 else .46,ink,vertices=8)
for z in (.62,.78,.94,1.10): cube('Carton print · derrick crossbar',(-4.35,-.602,z),(.68,.018,.018),ink,.004)
for i in range(5): cube('Carton print · derrick brace',(-4.35+(-.24+i*.12),-.61,.66+i*.09),(.018,.018,.18),ink,.003,rot=(0,math.radians(30),0))
text_obj('1880 — 1890','Carton · archive years',(-4.84,-.603,.31),.11,ink,rot=(math.radians(90),0,math.radians(-7)))

# Period tabletop props: kerosene lantern, folded map, revolver silhouette, gear, tools and paper.
# Lantern body and protective wire cage.
lx,ly=3.65,-1.58
cylinder('LANTERN · fuel tank',(lx,ly,.28),.30,.25,iron)
cylinder('LANTERN · brass tank rim',(lx,ly,.43),.31,.045,brass)
cylinder('LANTERN · glass chimney',(lx,ly,.86),.19,.68,glass)
cylinder('LANTERN · burner',(lx,ly,.54),.075,.10,brass)
bpy.ops.mesh.primitive_torus_add(major_radius=.22,minor_radius=.035,major_segments=32,minor_segments=8,location=(lx,ly,1.25)); bpy.context.object.name='LANTERN · top guard'; bpy.context.object.data.materials.append(iron)
cylinder('LANTERN · top cap',(lx,ly,1.29),.26,.12,iron)
for a in range(4):
    ang=a*math.pi/2
    cylinder('LANTERN · guard rod',(lx+.21*math.cos(ang),ly+.21*math.sin(ang),.84),.018,.78,brass)
for z in (.49,1.18):
    bpy.ops.mesh.primitive_torus_add(major_radius=.22,minor_radius=.018,major_segments=32,minor_segments=8,location=(lx,ly,z)); bpy.context.object.name='LANTERN · glass cage ring'; bpy.context.object.data.materials.append(brass)
bpy.ops.object.light_add(type='POINT',location=(lx,ly,.84)); flame=bpy.context.object; flame.name='LANTERN · warm practical glow'; flame.data.energy=85; flame.data.color=(1.0,.46,.13); flame.data.shadow_soft_size=.55

# Folded map as overlapping paper panels with a hand-drawn route.
cube('MAP · folded sheet',(2.03,-2.55,.045),(1.65,1.12,.035),paper,.01,rot=(0,0,math.radians(9)))
for x in (1.50,2.04,2.57): cube('MAP · fold crease',(x,-2.55,.066),(.012,1.07,.008),cardboard_edge,.002,rot=(0,0,math.radians(9)))
text_obj('OIL CREEK','MAP · printed location',(1.55,-2.45,.07),.09,ink)
for i in range(5): cube('MAP · route mark',(1.65+i*.14,-2.72+math.sin(i*.7)*.09,.073),(.18,.016,.006),ink,.002,rot=(0,0,.2))

# Non-violent historical prop: an unloaded decorative revolver, laid flat as set dressing.
cube('REVOLVER · walnut grip',(2.0,-1.20,.09),(.22,.56,.14),wood,.06,rot=(0,0,math.radians(-23)))
cube('REVOLVER · frame',(2.18,-.96,.13),(.28,.43,.15),iron,.07,rot=(0,0,math.radians(18)))
cylinder('REVOLVER · short barrel',(2.35,-.70,.13),.07,.46,iron,rot=(math.pi/2,0,math.radians(-12)))
bpy.ops.mesh.primitive_torus_add(major_radius=.13,minor_radius=.035,major_segments=32,minor_segments=8,location=(2.18,-1.04,.15)); bpy.context.object.name='REVOLVER · empty cylinder'; bpy.context.object.data.materials.append(brass)

# Gear, oilfield wrench and loose brass key.
bpy.ops.mesh.primitive_torus_add(major_radius=.37,minor_radius=.07,major_segments=12,minor_segments=6,location=(-3.25,-2.35,.09)); gear=bpy.context.object; gear.name='GEAR · cast iron ring'; gear.data.materials.append(iron)
cylinder('GEAR · hub',(-3.25,-2.35,.10),.14,.10,brass)
cube('WRENCH · handle',(-2.46,-2.30,.08),(.12,.90,.10),iron,.04,rot=(0,0,math.radians(37)))
bpy.ops.mesh.primitive_torus_add(major_radius=.13,minor_radius=.035,major_segments=24,minor_segments=8,location=(-2.24,-1.98,.09)); bpy.context.object.name='WRENCH · jaw loop'; bpy.context.object.data.materials.append(iron)
bpy.ops.mesh.primitive_torus_add(major_radius=.19,minor_radius=.045,major_segments=32,minor_segments=8,location=(-3.8,-1.65,.08)); bpy.context.object.name='KEY · bow'; bpy.context.object.data.materials.append(brass)
cylinder('KEY · shaft',(-3.36,-1.65,.08),.04,.8,brass,rot=(0,math.pi/2,0))
cube('KEY · tooth',(-3.03,-1.65,.13),(.09,.18,.08),brass,.01)

# Oil-stained photo scraps and handwritten archival tag.
cube('PHOTO · loose print',(-2.75,-.55,.06),(1.10,.72,.025),paper,.015,rot=(0,0,math.radians(-12)))
image_plane('PHOTO · derrick print',FILM,(-2.75,-.55,.078),.98,.52)
cube('TAG · archive card',(4.0,.25,.05),(.92,.60,.025),paper,.012,rot=(0,0,math.radians(-5)))
text_obj('FIELD NOTE','TAG · heading',(3.65,.34,.07),.095,ink)
text_obj('WELL 07 / 1888','TAG · index',(3.60,.18,.07),.075,ink)

# Camera animation: tabletop glide, push into the box, settle on the screen and story cards.
bpy.ops.object.empty_add(type='PLAIN_AXES',location=(BX,BY,1.55)); target=bpy.context.object; target.name='CAMERA TARGET · archive reveal'
bpy.ops.object.camera_add(location=(-7.8,-8.8,3.35)); cam=bpy.context.object; cam.name='CAMERA · 6s tabletop-to-box dolly'; cam.data.lens=32; scene.camera=cam
track=cam.constraints.new('TRACK_TO'); track.target=target; track.track_axis='TRACK_NEGATIVE_Z'; track.up_axis='UP_Y'
keys=[(1,(-9.8,-14.0,6.2),(-1.7,-.8,.7)),(50,(-7.0,-12.0,5.6),(-.8,-.1,1.0)),(105,(-4.0,-11.3,5.5),(-.45,.42,1.65)),(144,(-3.8,-11.0,5.3),(-.45,.42,1.65))]
for frame,loc,tgt in keys:
    cam.location=loc; cam.keyframe_insert(data_path='location',frame=frame)
    target.location=tgt; target.keyframe_insert(data_path='location',frame=frame)
# Blender 5 uses layered action storage; keyframe insertion defaults to bezier interpolation.
for fr,label in ((1,'TABLETOP FLYOVER'),(50,'APPROACH THE BOX'),(105,'ARCHIVE REVEAL'),(144,'HERO HOLD')):
    scene.timeline_markers.new(label,frame=fr)

def area(name,loc,power,color,size,targetpos):
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.name=name; o.data.energy=power; o.data.color=color; o.data.shape='DISK'; o.data.size=size
    o.rotation_euler=(Vector(targetpos)-o.location).to_track_quat('-Z','Y').to_euler(); return o
area('LIGHT · warm loft window',(1,-4,7),1400,(1.0,.66,.37),6,(-.2,0,1))
area('LIGHT · amber rim',(-5,2.5,4.5),1800,(1.0,.42,.16),4,(-.4,.5,1.2))
area('LIGHT · soft fill',(4,3,5),1100,(.82,.72,.55),5,(0,0,1))

# Camera/render defaults and deliverables.
scene.camera.data.dof.use_dof=True; scene.camera.data.dof.focus_object=target; scene.camera.data.dof.aperture_fstop=5.6
scene.frame_set(144); scene.render.filepath=PNG; scene.render.image_settings.file_format='PNG'; scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
bpy.ops.render.render(write_still=True)
# Export selected mesh assets and the camera animation as GLB for web iteration.
bpy.ops.object.select_all(action='DESELECT')
for o in scene.objects:
    if o.type in {'MESH','CAMERA','EMPTY'}: o.select_set(True)
bpy.context.view_layer.objects.active=cam
try: bpy.ops.export_scene.gltf(filepath=GLB,export_format='GLB',use_selection=True,export_animations=True)
except Exception as e: print('GLB export issue:',repr(e))
# Render a compact H.264 preview to prove the camera animation is present and playable.
scene.render.filepath=MP4; scene.render.image_settings.media_type='VIDEO'; scene.render.image_settings.file_format='FFMPEG'; scene.render.ffmpeg.format='MPEG4'; scene.render.ffmpeg.codec='H264'; scene.render.ffmpeg.constant_rate_factor='MEDIUM'
scene.render.resolution_percentage=55; scene.frame_start=1; scene.frame_end=144; scene.render.fps=24
bpy.ops.render.render(animation=True)
print('DELIVERABLES',BLEND,GLB,PNG,MP4)
