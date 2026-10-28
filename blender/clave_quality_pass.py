# Re-render the existing camera turn at the same quality as the continuation.
import bpy

scene = bpy.context.scene
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "JPEG"
scene.render.image_settings.quality = 93
ee = scene.eevee
if hasattr(ee, "taa_render_samples"):
    ee.taa_render_samples = 64
if hasattr(ee, "use_raytracing"):
    ee.use_raytracing = True

out = r"C:\Users\Maksim\Projects\clave нейп=ропродакшен\site\media\journey"
for frame in range(1, 25):
    scene.frame_set(frame)
    scene.render.filepath = out + f"\\frame-{frame:02d}.jpg"
    bpy.ops.render.render(write_still=True)
    print("SHOT", frame)
