import bpy, math
from mathutils import Vector
from pathlib import Path
O=Path(__file__).parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(name,color,rough=.4):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
 return m
paper=mat('Warm translucent polypropylene',(.80,.75,.57),.36)
edge=mat('Graphite anodized frame',(.038,.032,.021),.3)
lime=mat('Chartreuse test specimen',(.48,.66,.042),.45)
ground=mat('Charcoal cyclorama',(.047,.038,.027),.55)
black=mat('Bore wall',(.38,.33,.24),.55)
def box(name,loc,size,material,bev=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);ob=bpy.context.object;ob.name=name;ob.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.data.materials.append(material)
 if bev: mod=ob.modifiers.new('Rounded edges','BEVEL');mod.width=bev;mod.segments=3;ob.modifiers.new('Normals','WEIGHTED_NORMAL')
 return ob
cols,rows,pitch,depth,OD,ID=18,14,8.05,25,8,7.4
verts=[];faces=[];N=24
for j in range(rows):
 for i in range(cols):
  x=(i-(cols-1)*.5)*pitch;z=(j-(rows-1)*.5)*pitch+63
  b=len(verts)
  for y,r in [(-depth/2,OD/2),(depth/2,OD/2),(-depth/2,ID/2),(depth/2,ID/2)]:
   for k in range(N):
    a=2*math.pi*k/N; verts.append((x+r*math.cos(a),y,z+r*math.sin(a)))
  for k in range(N):
   a=k;b1=(k+1)%N
   for row in [(a,b1,N+b1,N+a),(2*N+a,3*N+a,3*N+b1,2*N+b1),(a,2*N+a,2*N+b1,b1),(N+a,N+b1,3*N+b1,3*N+a)]:
    faces.append(tuple(b+t for t in row))
mesh=bpy.data.meshes.new('252 individually open passages');mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new('18 × 14 straight hollow tubes',mesh)
bpy.context.collection.objects.link(ob);ob.data.materials.append(paper);ob.data.materials.append(black)
for p in mesh.polygons:
 if p.index%4 in (0,1):p.use_smooth=True
 if p.index%4==1:p.material_index=1
ob['Tube depth (mm)']=depth;ob['Declared ID (mm)']=ID;ob['Declared OD (mm)']=OD
w=cols*pitch; h=rows*pitch; mid=63
for y in (-10,10):
 for side in (-1,1):
  box('Frame / vertical clamp rail',(side*(w/2+2.5),y,mid),(5,5,h+10),edge,1)
  box('Frame / horizontal clamp rail',(0,y,mid+side*(h/2+2.5)),(w,5,5),edge,1)
for x in (-60,60):
 box('Foot / chartreuse datum',(x,0,2),(24,40,4),lime,1.5)
for x in (-w/2-2.5,w/2+2.5):
 box('Frame / bridge rail',(x,0,63),(5,16,12),edge,1)
box('Floor',(0,0,-3),(2000,2000,6),ground)
box('Backlit target',(0,75,67),(200,1,132),lime,2)
# A simple lensless reference target; no borrowed portrait.
for i,z in enumerate(range(13,125,12)):
 box('Resolution target / dark line',(0,73,z),(180,2,3 if i%2 else 1),edge)
for x in range(-80,81,16):
 box('Resolution target / vertical line',(x,72,65),(2,1,115),edge)
def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
def lamp(name,xyz,energy,size,col,target):
 bpy.ops.object.light_add(type='AREA',location=xyz);o=bpy.context.object;o.name=name;o.data.energy=energy;o.data.shape='DISK';o.data.size=size;o.data.color=col;aim(o,target)
lamp('Key / warm',(35,-170,260),2.6,160,(1,.86,.60),(0,0,55))
lamp('Fill / window',(-155,-100,105),1.1,140,(.69,.79,1),(0,0,63))
lamp('Rim',(10,105,220),2.4,130,(1,.94,.69),(0,0,63))
lamp('Target illumination',(0,29,95),.55,47,(1,1,.83),(0,75,65))
# Geometry is built in millimeters, then converted to scene meters for physically plausible lighting.
for o in bpy.context.scene.objects:
 o.location*=.001
 if o.type=='MESH': 
  for v in o.data.vertices:v.co*=.001
 for mod in o.modifiers:
  if mod.type=="BEVEL":mod.width*=.001
 if o.type=='LIGHT':o.data.size*=.001;o.data.energy*=.32
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.length_unit='MILLIMETERS';s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=False
s.render.resolution_x=960;s.render.resolution_y=700;s.render.resolution_percentage=100
s.world.color=(.15,.15,.15); s.view_settings.exposure=.65
def camera(name,xyz,point,lens):
 bpy.ops.object.camera_add(location=Vector(xyz)*.001);c=bpy.context.object;c.name=name;c.data.lens=lens;c.data.clip_start=.0001;aim(c,Vector(point)*.001);return c
hero=camera('01 / product three-quarter', (145,-320,166),(0,12,58),57)
axis=camera('02 / optical axis',(0,-330,63),(0,0,63),69)
off=camera('03 / 15° offset',(88,-330,63),(0,0,63),69)
s.camera=hero
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Optical-Channel-Array.blend'))
for c,n in [(hero,'01-panel-hero'),(axis,'02-on-axis'),(off,'03-off-axis')]:
 s.camera=c;s.render.filepath=str(O/(n+'.png'));bpy.ops.render.render(write_still=True)
