#Universidad del Valle de Guatemala
#Proyecto 2 Raycaster
#20/11/2021
#Creación de Raytracer

from cube import Cube
from lib import *
from math import pi, tan
from random import random
from sphere import Sphere
from envmap import Envmap

BLACK = color(0, 0, 0)
WHITE = color(255, 255, 255)
GREY = color(150, 150, 150)
MAX_RECURSION_DEPTH = 3

#La calse de raytracer
class Raytracer(object):
  def __init__(self, width, height):
    self.width = width
    self.height = height
    self.clear()
    self.background_color = BLACK

  def clear(self):
    self.pixels = [
      [BLACK for x in range(self.width)]
      for y in range(self.height)
    ]

  def write(self, filename):
    writebmp(filename, self.width, self.height, self.pixels)

  def point(self, x, y, col):
    self.pixels[y][x] = col

  def cast_ray(self, origin, direction, recursion = 0):
    material, intersect = self.scene_intersect(origin, direction)
    if material is None or recursion >= MAX_RECURSION_DEPTH:
      if self.envmap: return self.envmap.get_color(direction)
      return self.background_color

    light_dir = norm(sub(self.light.position, intersect.point))
    light_distance = length(sub(self.light.position, intersect.point))

    offset_normal = mul(intersect.normal, 0.1)
    shadow_origin = sum(intersect.point, offset_normal) if dot(intersect.normal, light_dir) > 0 else sub(intersect.point, offset_normal)
    shadow_material, shadow_intersect = self.scene_intersect(shadow_origin, light_dir)
    if shadow_material is None or length(sub(shadow_intersect.point, shadow_origin)) > light_distance: shadow_intensity = 0
    else: shadow_intensity = 0.6

    if material.albedo[2] > 0:
      reverse_direction = mul(direction, -1)
      reflect_direction = reflect(reverse_direction, intersect.normal)
      reflect_origin = sub(intersect.point, offset_normal) if dot(reflect_direction, intersect.normal) < 0 else sum(intersect.point, offset_normal)
      reflect_color = self.cast_ray(reflect_origin, reflect_direction, recursion + 1)
    else:
      reflect_color = BLACK

    if material.albedo[3] > 0:
      refract_direction = refract(direction, intersect.normal, material.refractive_index)
      if refract_direction is None:
        refract_color = BLACK
      else:
        refract_origin = sub(intersect.point, offset_normal) if dot(refract_direction, intersect.normal) < 0 else sum(intersect.point, offset_normal)
        refract_color = self.cast_ray(refract_origin, refract_direction, recursion + 1)
    else:
      refract_color = BLACK

    intensity = self.light.intensity * max(0, dot(light_dir, intersect.normal)) * (1 - shadow_intensity)
    if material.texture:
      if intersect.normal.z != 0:
        tx = intersect.point.x - int(intersect.point.x) 
        ty = intersect.point.y - int(intersect.point.y)
      elif intersect.normal.y != 0:
        tx = intersect.point.x - int(intersect.point.x) 
        ty = intersect.point.z - int(intersect.point.z)
      else:
        ty = intersect.point.y - int(intersect.point.y)
        tx = intersect.point.z - int(intersect.point.z)
      if material.top_texture and intersect.normal.y != 0:
        diffuse = material.top_texture.get_color(tx, ty) * (intensity * material.albedo[0])
      else:
        diffuse = material.texture.get_color(tx, ty) * (intensity * material.albedo[0])
    else:
      diffuse = material.diffuse * (intensity * material.albedo[0])

    specular_reflection = reflect(light_dir, intersect.normal)
    specular_intensity = self.light.intensity * max(0, -dot(specular_reflection, direction))**material.spec if shadow_intensity == 0 else 0
    specular = self.light.color * specular_intensity * material.albedo[1]
    reflection = reflect_color * material.albedo[2]
    refraction = refract_color * material.albedo[3]
    c = diffuse + specular + reflection + refraction
    return c

#Intersectos la escena
  def scene_intersect(self, origin, direction):
    zbuffer = float('inf')
    material = None
    retintersect = None
    for obj in self.scene:
      intersect = obj.ray_intersect(origin, direction)
      if intersect:
        if intersect.distance < zbuffer:
          zbuffer = intersect.distance
          material = obj.material
          retintersect = intersect
    return material, retintersect

  def render(self):
    fov = pi/2
    ar = self.width / self.height
    c1 = tan(fov/2)

    for y in range(self.height):
      for x in range(self.width):
        if random() > 0:
          i = ((2 * x + 1) / self.width - 1) * c1 * ar
          j = (1 - (2 * y + 1) / self.height) * c1
          direction = norm(sum(V3(i, -j, 0), self.orientation))
          col = self.cast_ray(self.camera, direction)
          self.point(x, y, col)

r = Raytracer(1920, 1100)

r.camera = V3(5, 5, 4)
r.orientation = V3(0, -0.70, -1)

r.light = Light(
  position = V3(20, 20, 20),
  intensity = 2,
  color = color(255, 255, 200)
)
def setCubes(pos, size, material):
  cubes = []
  for x in range(size.x):
    for y in range(size.y):
      for z in range(size.z):
        cubes.append(Cube(V3(pos.x + x, pos.y + y, pos.z - z), material))
  return cubes

#Materiales
water = Material(diffuse=color(35, 177, 209), albedo=[0.2, 0.3, 0.8, 0], spec=60 )
piso = Material(diffuse=color(0, 0, 0), albedo=[0.9, 0.1, 0, 0], spec=10, texture='./textures/piso.bmp', top_texture='./textures/gramita.bmp')
madera = Material(diffuse=color(0, 0, 0), albedo=[0.9, 0.1, 0, 0], spec=10, texture='./textures/madera.bmp')
ladrillo = Material(diffuse=color(0, 0, 0), albedo=[0.9, 0.1, 0, 0], spec=10, texture='./textures/piso.bmp')
aldeano = Material(diffuse=color(0, 0, 0), albedo=[0.9, 0.1, 0, 0], spec=10, texture='./textures/madera.bmp')
aldeano2 = Material(diffuse=color(0, 0, 0), albedo=[0.9, 0.1, 0, 0], spec=10, texture='./textures/aldeano.bmp')
hojitas = Material(diffuse=color(0, 0, 0), albedo=[0.9, 0.1, 0, 0], spec=10, texture='./textures/hojitas.bmp')
cuerpo = Material(diffuse=color(0, 0, 0), albedo=[0.9, 0.1, 0, 0], spec=10, texture='./textures/hojitas.bmp') 

r.scene = [
  Cube(V3(9, 3, -1), hojitas),
  Cube(V3(8, 3, -1.5), hojitas),
  Cube(V3(7, 3, -2), hojitas),
  Cube(V3(7.5, 3, -1), hojitas),
  Cube(V3(8.5, 4, -2), hojitas),
  Cube(V3(8.5, 1, -2), madera),
  Cube(V3(8.5, 2, -2),  madera),
  Cube(V3(8.5, 3, -2),  madera),
  #ladrillos
  Cube(V3(-1, 1, -2),  ladrillo),
  Cube(V3(2, 1, -2),  ladrillo),
  Cube(V3(0, 2, -1.5),  ladrillo),
  Cube(V3(1, 1, -1),  ladrillo),
  Cube(V3(1, 2, -1.5),  ladrillo),
  Cube(V3(0, 1, -1),  ladrillo),
  Cube(V3(1, 1.5, -2.5),  ladrillo),
  #AGUA
  Cube(V3(4, 0, -2), water),
  Cube(V3(5, 0, -2), water),
  Cube(V3(6, 0, -2), water),
  Cube(V3(7, 0, -2), water),
  Cube(V3(6, 0, -1), water),
  Cube(V3(6, 0, -2.5), water),
  Cube(V3(7, 0, -1), water), 
  Cube(V3(7, 0, -2.5), water),
  #ALDEANO
  Cube(V3(4, 1, -3), cuerpo),
  Cube(V3(4, 2, -3), cuerpo),
  Cube(V3(4, 3, -3), aldeano2),
 
]

#Piso de la escena
r.scene.extend(setCubes(V3(0, 0, 0), V3(4, 1, 4), piso))
r.scene.extend(setCubes(V3(4, 0, 0), V3(6, 1, 4), piso))

r.envmap = Envmap('./textures/fondo.bmp')

r.render()
r.write('a.bmp') 
