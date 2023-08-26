import pygame, random, math
import pygame.gfxdraw

# PYGAME ====================

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption('Asteroids')

clock = pygame.time.Clock()

# GAME ====================

font = pygame.font.SysFont('calibri', 60, bold=True)

keys = [False, False, False, False]


def draw_poly(surface, points, color, width):
   for i in range(len(points) - 1):
       pygame.draw.line(surface, color, points[i], points[i + 1], width)


def lineCircle(a, b, c, r):
   if c[1] + r < min(a[1], b[1]) or c[1] - r > max(a[1], b[1]) or \
           c[0] + r < min(a[0], b[0]) or c[0] - r > max(a[0], b[0]):
       return False

   # compute the triangle area times 2(area=area2 / 2)
   area2 = abs((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1]))

   # compute the AB segment length
   LAB = math.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)

   # compute the triangle height
   h = 0 if LAB == 0 else area2 / LAB

   return h < r


def rectCircle(c, r, rect):
   cdistx = abs(c[0] - rect[0])
   cdisty = abs(c[1] - rect[1])

   if cdistx > (rect.width / 2 + r) or cdisty > (rect.height / 2 + r):
       return False

   if cdistx <= (rect.width / 2) or cdisty <= (rect.height / 2):
       return True

   cornerDistance_sq = (cdistx - rect.width / 2) ** 2 + (cdisty - rect.height / 2) ** 2
   return cornerDistance_sq <= r ** 2


class Ship:
   def __init__(self, x, y, r, lives, width=16):
       self.x, self.y, self.r, self.width = x, y, r, width

       self.velx = self.vely = self.rvel = 0

       self.maxvel = 4
       self.thrust = 0.2

       self.forward = False

       self.shape = [(8, 0), (16, 16), (8, 12), (0, 16)]

       self.lives = lives

   def draw(self, surface, color):
       o = (self.x + self.width / 2, self.y + self.width / 2)
       # print(o)

       rot_shape = self.shape.copy()
       for i in range(len(rot_shape)):
           rot_shape[i] = (rot_shape[i][0] + self.x, rot_shape[i][1] + self.y)
           p = rot_shape[i]

           rx = math.cos(math.radians(self.r)) * (p[0] - o[0]) - math.sin(math.radians(self.r)) * (p[1] - o[1]) + o[0]
           ry = math.sin(math.radians(self.r)) * (p[0] - o[0]) + math.cos(math.radians(self.r)) * (p[1] - o[1]) + o[1]
           rot_shape[i] = (rx, ry)

       pygame.gfxdraw.polygon(surface, rot_shape, color)  # self.shape

   def update(self):
       speed = math.sqrt(self.velx ** 2 + self.vely ** 2)
       f_velx = self.velx + self.thrust * math.sin(math.radians(self.r))
       f_vely = self.vely - self.thrust * math.cos(math.radians(self.r))
       f_speed = math.sqrt(f_velx ** 2 + f_vely ** 2)

       if self.forward:
           if f_speed < self.maxvel:
               self.velx = f_velx
               self.vely = f_vely
           else:
               self.velx = self.maxvel * math.sin(math.radians(self.r))
               self.vely = -self.maxvel * math.cos(math.radians(self.r))

       self.x += self.velx
       self.y += self.vely

       self.r += self.rvel
       self.rvel *= 0.94
       if abs(self.rvel) > 2:
           self.rvel = 2 if self.rvel > 0 else -2

       if self.x > SCREEN_WIDTH:
           self.x = 0 - self.width
       elif self.x < 0 - self.width:
           self.x = SCREEN_WIDTH

       if self.y > SCREEN_HEIGHT:
           self.y = 0 - self.width
       elif self.y < 0 - self.width:
           self.y = SCREEN_HEIGHT

   def shoot(self):
       pewpews.append(PewPew(self.x + self.width / 2, self.y + self.width / 2, self.r))

   def rect(self):
       return pygame.Rect((self.x, self.y), (self.width, self.width))

   def die(self, x, y, r, width=16):
       self.lives -= 1

       self.x, self.y, self.r, self.width = x, y, r, width

       self.velx = self.vely = self.rvel = 0

       self.maxvel = 4
       self.thrust = 0.2

       self.forward = False


class PewPew:

   def __init__(self, x, y, r, length=16, width=1):
       self.x, self.y, self.r, self.width, self.length = x, y, r, width, length

       self.vel = 10

       self.steps = 0

   def draw(self, surface, color):
       rx = math.cos(math.radians(self.r)) * ((self.x + self.width) - self.x) - math.sin(math.radians(self.r)) * (
               (self.y + self.length) - self.y) + self.x
       ry = math.sin(math.radians(self.r)) * ((self.x + self.width) - self.x) + math.cos(math.radians(self.r)) * (
               (self.y + self.length) - self.y) + self.y

       pygame.draw.line(surface, color, (self.x, self.y), (rx, ry), 1)

   def update(self):

       self.x += self.vel * math.sin(math.radians(self.r))
       self.y -= self.vel * math.cos(math.radians(self.r))

       if self.x > SCREEN_WIDTH:
           self.x = 0 - self.width
       elif self.x < 0 - self.width:
           self.x = SCREEN_WIDTH

       if self.y > SCREEN_HEIGHT:
           self.y = 0 - self.width
       elif self.y < 0 - self.width:
           self.y = SCREEN_HEIGHT

       self.steps += 1
       if self.steps >= 40:
           self.vel *= 0.9

       if self.vel <= 1:
           self.die()

   def die(self):
       pewpews.remove(self)
       del self

   def end(self):
       rx = math.cos(math.radians(self.r)) * ((self.x + self.width) - self.x) - math.sin(math.radians(self.r)) * (
               (self.y + self.length) - self.y) + self.x
       ry = math.sin(math.radians(self.r)) * ((self.x + self.width) - self.x) + math.cos(math.radians(self.r)) * (
               (self.y + self.length) - self.y) + self.y

       return (rx, ry)


small = 60
medium = 80
big = 100

asteroid_min = 40

score = 0

class Asteroid:

   def __init__(self, x, y, r, width):
       self.x, self.y, self.r, self.width = x, y, r, width
       self.rect = (x, y, width, width)

       if width < asteroid_min:
           self.explode()

       self.vel = 2
       self.velx = self.vel * math.sin(math.radians(self.r))
       self.vely = -self.vel * math.cos(math.radians(self.r))
       self.rvel = 2

       angle = 0
       # self.shape = [(width/2, 0), (width, width), (width/2, width/4*3), (0, width)]
       o = (self.width / 2, self.width / 2)

       self.radius = width / 2
       self.bump = int(self.radius / 4)
       verts = int(width / 6)
       if verts <= 3:
           verts = 4

       self.shape = []
       for i in range(verts):
           self.shape.append(
               (o[0] + self.radius * math.cos(math.radians(angle)) + random.randint(-self.bump, self.bump),
                o[1] + self.radius * math.sin(math.radians(angle)) + random.randint(-self.bump, self.bump)))
           angle += 360 / verts

   def draw(self, surface, color):
       o = (self.x + self.width / 2, self.y + self.width / 2)
       # print(o)

       rot_shape = self.shape.copy()
       for i in range(len(rot_shape)):
           rot_shape[i] = (rot_shape[i][0] + self.x, rot_shape[i][1] + self.y)
           p = rot_shape[i]

           rx = math.cos(math.radians(self.r)) * (p[0] - o[0]) - math.sin(math.radians(self.r)) * (p[1] - o[1]) + o[0]
           ry = math.sin(math.radians(self.r)) * (p[0] - o[0]) + math.cos(math.radians(self.r)) * (p[1] - o[1]) + o[1]
           rot_shape[i] = (rx, ry)

       pygame.gfxdraw.polygon(surface, rot_shape, color)  # self.shape

   def update(self):

       self.x += self.velx
       self.y -= self.vely
       self.r += self.rvel

       if self.x > SCREEN_WIDTH:
           self.x = 0 - self.width
       elif self.x < 0 - self.width:
           self.x = SCREEN_WIDTH

       if self.y > SCREEN_HEIGHT:
           self.y = 0 - self.width
       elif self.y < 0 - self.width:
           self.y = SCREEN_HEIGHT

   def explode(self):

       if self.width < small:
           size = 0
       elif self.width < medium:
           size = small
       else:
           size = medium

       if self.width > small:
           for i in range(random.randint(2, 4)):
               asteroids.append(
                   Asteroid(self.x + random.randint(0, self.width), self.y + random.randint(0, self.width),
                            random.randint(0, 360), size + random.randint(-20, 0)))

       if self in asteroids: asteroids.remove(self)
       del self

   def center(self):
       return (self.x + self.width / 2, self.y + self.width / 2)


player = Ship(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 0, 5)

shoot_delay = 20
clicking = 0

pewpews = []
asteroids = []

def random_ast():
   asteroids.append(Asteroid(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), random.randint(0, 360),
                             big + random.randint(-20, 0)))

def rand_edge_ast():
   width = random.randint(60, 100)
   x = 0-width if bool(random.getrandbits(1)) else SCREEN_WIDTH
   y = 0-width if bool(random.getrandbits(1)) else SCREEN_HEIGHT

   asteroids.append(Asteroid(x, y, random.randint(0, 360), width))

wave = 1

for i in range(4+wave):
   random_ast()

# COLORS ====================

black = (0, 0, 0)
white = (255, 255, 255)

while True:

   for event in pygame.event.get():
       if event.type == pygame.QUIT:
           pygame.quit()
           quit()
       mouse_down = pygame.mouse.get_pressed()[0]

       if event.type == pygame.KEYDOWN:
           if event.key == pygame.K_w: keys[0] = True
           if event.key == pygame.K_a: keys[1] = True
           if event.key == pygame.K_d: keys[2] = True
           if event.key == pygame.K_SPACE: keys[3] = True

       if event.type == pygame.KEYUP:
           if event.key == pygame.K_w: keys[0] = False
           if event.key == pygame.K_a: keys[1] = False
           if event.key == pygame.K_d: keys[2] = False
           if event.key == pygame.K_SPACE: keys[3] = False

   if keys[0]:
       player.forward = True
   else:
       player.forward = False
   if keys[1]:
       player.rvel -= 2
   if keys[2]:
       player.rvel += 2
   if keys[3]:
       if clicking <= 0:
           player.shoot()
           clicking = shoot_delay
   clicking -= 1

   for pewpew in pewpews:
       pewpew.update()

       if pewpew in pewpews:
           for asteroid in asteroids:
               if lineCircle((pewpew.x, pewpew.y), pewpew.end(), asteroid.center(), asteroid.radius + asteroid.bump):
                   # scoring

                   if asteroid.width < small:
                       score += 100
                   elif asteroid.width < medium:
                       score += 50
                   else:
                       score += 20

                   asteroid.explode()
                   pewpew.die()
                   break

   for asteroid in asteroids:
       asteroid.update()

       if rectCircle(asteroid.center(), asteroid.radius-asteroid.bump, player.rect()):
           asteroid.explode()
           player.die(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 0, 5)

   # New Wave

   if not asteroids:
       wave += 1
       for i in range(4+wave):
           rand_edge_ast()

   player.update()

   screen.fill(black)

   player.draw(screen, white)

   for pewpew in pewpews:
       pewpew.draw(screen, white)

   for asteroid in asteroids:
       asteroid.draw(screen, white)



   pygame.display.update()

   clock.tick(60)

