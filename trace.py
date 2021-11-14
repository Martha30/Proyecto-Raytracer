#Universidad del Valle de Guatemala
#04/10/2021
#Main

from lib import *
from sphere import *
from math import pi, tan
from random import random

BLACK = color(0, 0, 0)
pi = 3.14159265359

class Raytracer(object):
    def __init__(self, width, height):
      self.width = width
      self.height = height
      self.background_color = BLACK
      self.light = None
      self.clear()

    def clear(self):
      self.framebuffer = [
        [black for _ in range(self.width)]
        for _ in range(self.height)
      ]

    def write(self, filename):
      writeBMP(filename, self.width, self.height, self.framebuffer)


    def glColor(self, r, g, b):
        '''Change the color glVertex() works with. The parameters must 
        be numbers in the range of 0 to 1.'''

        try:
            self.rv = round(r)
            self.gv = round(g)
            self.bv = round(b)
            self.vertex_color = color(self.rv,self.gv,self.bv)
        except ValueError:
                print('\nERROR: Please enter a number between 1 and 0\n')


    def glClearColor(self, r, g, b):
        '''Can change the color of glClear(), parameters must be numbers in the 
        range of 0 to 1.'''

        try:
            self.rc = round(r)
            self.gc = round(g)
            self.bc = round(b)
            self.clear_color = color(self.rc, self.gc, self.bc)
        except ValueError:
            print('\nERROR: Please enter a number between 1 and 0\n')
    
    def point(self, x, y, col):
      self.framebuffer[y][x] = col
    #Siempre nos regresa un color
    def cast_ray(self, origin, direction):
      #LOS RAYOS VAN A VER ALGUNA COSA DE LA ESCENA PARA RETORNAR
      material, intersect = self.scene_intersect(origin, direction)
      
      if material is None:
        return self.background_color
      
      print(material, intersect)


      light_dir = sub(self.light.position, intersect.point)
      intensity = self.light.intensity * max(0, dot(light_dir, intersect.normal))

      #Color diffuso depende del material por la intensity
      diffuse = material.diffuse * intensity

      c = diffuse
      return c

      
    #Rayo único que trata de golpear a todos los objetos de la escena
    def scene_intersect(self, origin, direction):
      zbuffer = float('inf')
      material = None
      intersect = None

      for obj in self.scene:
        r_intersect = obj.ray_intersect(origin, direction)

        if r_intersect:
          if r_ intersect.distance < zbuffer:
            zbuffer = r_intersect.distance#donde golpeo el rayo
            material = obj.material
            intersect = r_intersect

      return material, intersect

    def render(self): 
      fov = pi/2
      ar = self.width/self.height

      for y in range(self.height):
        for x in range(self.width):
        #Corrección para el aspect ratio
          if random() > 0:
            i = (2 * ((x + 0.5) / self.width) - 1) * ar * tan(fov/2)
            j = 1 - 2 * ((y + 0.5) / self.height) * tan(fov/2)

            direction = norm(V3(i, j, -1))
            col = self.cast_ray(V3(0, 0, 0), direction )
            self.point(x, y, col)

r = Raytracer(1000, 1000)

r.light = Light(
  position=V3(10, 10, 10),
  intensity=1,
)

ivory = Material(diffuse=color(100, 100, 80 ))
rubber = Material(diffuse=color(80, 0, 0))
r.scene = [
  Sphere(V3(0, -1.5, -10), 1.5, ivory), #con radio 1.5
  Sphere(V3(-2, 1, -12), 2, rubber), #con radio 2
  Sphere(V3(1, 1, -8), 1.7, rubber), #con radio 1.7
  Sphere(V3(0, 5, -20), 5, ivory), #con radio 5
]

r.render()
r.write('b.bmp')

