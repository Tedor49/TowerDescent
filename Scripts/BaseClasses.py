import sys
import time
import random
import pygame


class GameObject:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def tick(self):
        return

    def getx(self):
        return self.x

    def gety(self):
        return self.y

    def add_to_manager(self):
        GameManager.all_Objects.add(self)

    def delete(self):
        if self in GameManager.all_Objects:
            GameManager.all_Objects.remove(self)


class Spawner(GameObject):
    def __init__(self, x, y, enemy, room1):
        super().__init__(x, y)
        self.enemy = enemy
        self.room = room1
        self.room.filling.append(self)
        self.inactive = False

    def spawn(self):
        if not self.inactive:
            self.enemyInstance = self.enemy(self.x, self.y, Sprite('Sprites/playernew.png'), Hitbox(50, 50),
                                            GameManager.player)
            self.room.filling.append(self.enemyInstance)

    def despawn(self):
        if self.enemyInstance.hp <= 0:
            self.inactive = True
        if not self.inactive:
            GameManager.toRemove.append(self)
            self.room.filling.remove(self.enemyInstance)


class Hitbox(GameObject):
    def __init__(self, x_size, y_size, x=0, y=0, parent=None):
        super().__init__(x, y)
        self.parent = parent
        self.x_size = x_size
        self.y_size = y_size
        self.ray_quality = 1
        self.epsilon = 0.000001

    def getx(self):
        return self.parent.getx() + self.x

    def gety(self):
        return self.parent.gety() + self.y

    def intersects(self, other):
        self_x_end = self.getx() + self.x_size
        self_y_end = self.gety() + self.y_size
        other_x_end = other.getx() + other.x_size
        other_y_end = other.gety() + other.y_size
        intersect_x = (self.getx() - other_x_end) * (other.getx() - self_x_end) >= 0
        intersect_y = (self.gety() - other_y_end) * (other.gety() - self_y_end) >= 0
        return intersect_x and intersect_y

    def modify_movement(self, movement, hbox, mode="stop"):
        if mode == "pass":
            return movement

        def vec(p1, p2):
            return p2[0] - p1[0], p2[1] - p1[1]

        def cross(vec1x, vec1y, vec2x, vec2y):
            return vec1x * vec2y - vec1y * vec2x

        def seg_to_line(beg, end):
            return beg[1] - end[1], \
                   end[0] - beg[0], \
                   beg[0] * end[1] - end[0] * beg[1]

        def intersect_lines(a1, b1, c1, a2, b2, c2):
            denominator = (a1 * b2 - a2 * b1)
            return [(b1 * c2 - b2 * c1) / denominator, (a2 * c1 - a1 * c2) / denominator]

        def intersect_segments(seg1, seg2):
            if cross(*vec(seg1[0], seg1[1]), *vec(seg1[0], seg2[0])) * \
                    cross(*vec(seg1[0], seg1[1]), *vec(seg1[0], seg2[1])) > 0 or \
                    cross(*vec(seg2[0], seg2[1]), *vec(seg2[0], seg1[0])) * \
                    cross(*vec(seg2[0], seg2[1]), *vec(seg2[0], seg1[1])) > 0:
                return None
            return intersect_lines(*seg_to_line(*seg1), *seg_to_line(*seg2))

        def pythagoreas(x1, y1, x2, y2):
            return (x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2)

        sides = {"LEFT": (
            (self.getx(), self.gety()), (self.getx(), self.gety() + self.y_size)),
            "TOP":
                ((self.getx() + self.x_size, self.gety()), (self.getx(), self.gety())),
            "RIGHT": (
                (self.getx() + self.x_size, self.gety() + self.y_size), (self.getx() + self.x_size, self.gety())),
            "BOTTOM": (
                (self.getx(), self.gety() + self.y_size), (self.getx() + self.x_size, self.gety() + self.y_size))}

        def ray_intersect(segment):
            intersections = []

            selsides = []
            movvec_x = segment[1][0] - segment[0][0]
            movvec_y = segment[1][1] - segment[0][1]

            if movvec_x > 0:
                selsides.append("LEFT")
            elif movvec_x < 0:
                selsides.append("RIGHT")

            if movvec_y > 0:
                selsides.append("TOP")
            elif movvec_y < 0:
                selsides.append("BOTTOM")

            for s in selsides:
                if intersect_segments(sides[s], segment):
                    intersections.append([s, intersect_segments(sides[s], segment)])
                    if s == "TOP":
                        intersections[-1][1][1] = sides[s][0][1] - self.epsilon
                    elif s == "BOTTOM":
                        intersections[-1][1][1] = sides[s][0][1] + self.epsilon
                    elif s == "LEFT":
                        intersections[-1][1][0] = sides[s][0][0] - self.epsilon
                    else:
                        intersections[-1][1][0] = sides[s][0][0] + self.epsilon

            if not intersections:
                return None
            else:
                return min(intersections, key=lambda x: pythagoreas(*x[1], *segment[0]))

        def ratio_point(p1x, p1y, p2x, p2y, ratio):
            return p1x * ratio + p2x * (1 - ratio), p1y * ratio + p2y * (1 - ratio)

        rays = []

        moving_sides = {"LEFT": (
            (hbox.getx(), hbox.gety()), (hbox.getx(), hbox.gety() + hbox.y_size)),
            "TOP":
                ((hbox.getx() + hbox.x_size, hbox.gety()), (hbox.getx(), hbox.gety())),
            "RIGHT": (
                (hbox.getx() + hbox.x_size, hbox.gety() + hbox.y_size), (hbox.getx() + hbox.x_size, hbox.gety())),
            "BOTTOM": (
                (hbox.getx(), hbox.gety() + hbox.y_size), (hbox.getx() + hbox.x_size, hbox.gety() + hbox.y_size))}

        for side in moving_sides:
            for j in range(hbox.ray_quality):
                ray_start = ratio_point(*moving_sides[side][0], *moving_sides[side][1], j / hbox.ray_quality)
                ray_end = (ray_start[0] + movement[1][0] - movement[0][0],
                           ray_start[1] + movement[1][1] - movement[0][1])
                ray_offset = (hbox.getx() - ray_start[0], hbox.gety() - ray_start[1])
                rays.append(((ray_start, ray_end), ray_offset))

        connected_rays = []

        for i in range(len(rays)):
            intersection = ray_intersect(rays[i][0])
            if intersection:
                connected_rays.append((intersection, rays[i]))

        if not connected_rays:
            return movement, 1, 1

        best_ray = min(connected_rays, key=lambda x: pythagoreas(*x[0][1], *x[1][0][0]))
        best_ray_endpoint = [best_ray[0][1][0] + best_ray[1][1][0], best_ray[0][1][1] + best_ray[1][1][1]]

        if mode == "stop":
            return movement[0], best_ray_endpoint

        if mode == "slide":
            dx_mul = 1
            dy_mul = 1
            if best_ray[0][0] in ["TOP", "BOTTOM"]:
                best_ray_endpoint[0] = movement[1][0]
                dy_mul = 0
            else:
                best_ray_endpoint[1] = movement[1][1]
                dx_mul = 0
            return (movement[0], best_ray_endpoint), dx_mul, dy_mul
        elif mode == "bounce":
            dx_mul = 1
            dy_mul = 1
            if best_ray[0][0] in ["TOP", "BOTTOM"]:
                best_ray_endpoint[0] = movement[1][0]
                best_ray_endpoint[1] += best_ray_endpoint[1] - movement[1][1]
                dy_mul *= -1
            else:
                best_ray_endpoint[1] = movement[1][1]
                best_ray_endpoint[0] += best_ray_endpoint[0] - movement[1][0]
                dx_mul *= -1
            return (movement[0], best_ray_endpoint), dx_mul, dy_mul
        else:
            raise TypeError("Non-existent collision type")

    def check_intersections(self, movement=None):
        intersecting = []
        for i in GameManager.all_Hitboxes:
            if i != self:
                if not movement and self.intersects(i):
                    intersecting.append(i)
                elif movement and i.modify_movement(movement, self)[0] != movement:
                    intersecting.append(i)
        return intersecting

    def show(self):
        sprite = Sprite("Sprites/hitbox.png", z=0)
        sprite.image = pygame.transform.scale(sprite.image, (self.x_size, self.y_size))
        sprite.parent = self
        GameManager.all_Sprites.add(sprite)


class Sprite(GameObject):
    def __init__(self, image, stretch_x=1, stretch_y=1, z=1, x=0, y=0, parent=None):
        super().__init__(x, y)
        self.parent = parent
        self.z = z
        picture = pygame.image.load(image)
        self.image = pygame.transform.scale(picture, (int(picture.get_size()[0] * stretch_x),
                                                      int(picture.get_size()[1] * stretch_y)))

    def getx(self):
        return self.parent.getx() + self.x + GameManager.camera.getx()

    def gety(self):
        return self.parent.gety() + self.y + GameManager.camera.gety()

    def draw(self):
        GameManager.screen.blit(self.image, (self.getx(), self.gety()))


class InteractableObject(GameObject):
    def __init__(self, x, y, sprite=None, hitbox=None, dx=0, dy=0, g=0.002):
        super().__init__(x, y)
        self.dx = dx
        self.dy = dy
        self.g = g
        self.sprite = sprite
        if sprite:
            self.sprite.parent = self
        self.hitbox = hitbox
        if hitbox:
            self.hitbox.parent = self

    def tick(self):
        self.x += self.dx * GameManager.time_elapsed
        self.y += self.dy * GameManager.time_elapsed

    def getdx(self):
        return self.dx

    def getdy(self):
        return self.dy

    def getx(self):
        return self.x

    def gety(self):
        return self.y

    def add_to_manager(self):
        GameManager.all_Objects.add(self)
        if self.hitbox:
            GameManager.all_Hitboxes.add(self.hitbox)
        if self.sprite:
            GameManager.all_Sprites.add(self.sprite)

    def delete(self):
        if self in GameManager.all_Objects:
            GameManager.all_Objects.remove(self)
        if self.hitbox and self.hitbox in GameManager.all_Hitboxes:
            GameManager.all_Hitboxes.remove(self.hitbox)
        if self.sprite and self.sprite in GameManager.all_Sprites:
            GameManager.all_Sprites.remove(self.sprite)


class Attack(InteractableObject):
    def __init__(self, x, y, sprite, hitbox, parent, dx=0, dy=0):
        super().__init__(x, y, sprite, hitbox, dx, dy)
        self.parent = parent
        self.angle = 0
        GameManager.toAdd.append(self)

    def do(self, to_x, to_y):
        pass

    def tick(self):
        pass


class Camera(GameObject):
    def __init__(self, x=0, y=0):
        super().__init__(x, y)

    def tick(self):
        self.x = -GameManager.player.x + 250
        self.y = -GameManager.player.y + 250


class Menu:
    def __init__(self):
        pygame.init()
        size = [700, 700]
        screen = pygame.display.set_mode(size)
        pygame.display.set_caption('Tower Descent menu')
        running = True
        screen.fill(pygame.Color('white'))
        font = pygame.font.SysFont('arial', 50)
        text = font.render('Singleplayer',
                           True, (0, 0, 0))
        text_x = 210
        text_y = 300
        screen.blit(text, (text_x, text_y))
        text = font.render('Multiplayer',
                          True, (0, 0, 0))
        text_x = 230
        text_y = 380
        screen.blit(text, (text_x, text_y))
        while running:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if 210 < x < 410 and 310 < y < 350:
                        pygame.quit()
                        GameManager()
                    elif 230 < x < 430 and 385 < y < 430:
                        print('multiplayer will be available later')
                if event.type == pygame.QUIT:
                    running = False
            pygame.display.flip()


class GameManager:
    toAdd = []
    toRemove = []
    screen = None
    clock = None
    player = None
    camera = None
    time_elapsed = 0
    tps = 120
    currentRoom = None
    all_Hitboxes = set()
    all_Objects = set()
    all_Sprites = set()
    Rooms = []
    counter = 0

    def __init__(self):
        from Scripts.Player import Player
        pygame.init()
        size = [960, 720]
        lev = LevelGenerator()
        GameManager.counter = len(GameManager.Rooms)
        GameManager.player = Player(60, 100, Sprite('Sprites/playernew.png'), Hitbox(50, 50))
        GameManager.screen = pygame.display.set_mode(size)
        pygame.display.set_caption('Tower Descent')
        GameManager.clock = pygame.time.Clock()
        GameManager.currentRoom = GameManager.searchByID(0)
        cam = Camera()
        GameManager.camera = cam
        self.update()
        GameManager.toAdd.append(GameManager.player)
        running = True
        GameManager.currentRoom.enter()
        while running:
            GameManager.clock.tick()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
            GameManager.time_elapsed += GameManager.clock.get_time()
            if GameManager.time_elapsed < 1000 / GameManager.tps:
                continue
            for i in GameManager.all_Objects:
                i.tick()
            for i in sorted(GameManager.all_Sprites, key=lambda x: x.z):
                i.draw()
            pygame.display.flip()
            GameManager.time_elapsed = 0
            self.update()

    @staticmethod
    def update():
        from Scripts.Enemies import Enemy
        for i in GameManager.toAdd:
            i.add_to_manager()
            if i not in GameManager.currentRoom.filling:
                GameManager.currentRoom.filling.append(i)
        GameManager.toAdd = []
        for i in GameManager.toRemove:
            if isinstance(i, Enemy):
                i.delete()
        GameManager.toRemove = []

    @staticmethod
    def searchByID(RoomID):
        for room in GameManager.Rooms:
            if room.id == RoomID:
                return room
        return None


class Room:
    def __init__(self, filling, id):
        self.filling = filling
        self.id = id
        self.leftDoor = None
        self.rightDoor = None
        self.upDoor = None
        self.downDoor = None
        self.checked = False
        self.leftChecked = False
        self.rightChecked = False
        self.upChecked = False
        self.downChecked = False
        self.filling.append(InteractableObject(0, 0, Sprite("Sprites/test_room.png", z=-2)))

    def enter(self, type='left'):
        from Scripts.Player import Player
        coordinates = {
            'up': (450, 40),
            'down':(450, 630),
            'left':(30, 350),
            'right':(880, 350)
        }
        print(type)
        GameManager.player.x = coordinates[type][0]
        GameManager.player.y = coordinates[type][1]
        print(coordinates[type])
        GameManager.currentRoom = self
        self.filling.append(GameManager.player)
        for i in self.filling:
            if isinstance(i, Spawner):
                i.spawn()
            if not isinstance(i, Player):
                GameManager.toAdd.append(i)

    def quit(self):
        from Scripts.Player import Player
        for i in GameManager.all_Objects:
            if isinstance(i, Attack):
                if i in self.filling:
                    self.filling.remove(i)
            if isinstance(i, Spawner):
                i.despawn()
            if not isinstance(i, Player):
                GameManager.toRemove.append(i)


class Door(InteractableObject):
    def __init__(self, x, y, sprite, hitbox, from1, to1, toDoor, dx=0, dy=0, g=5, type=None):
        super().__init__(x, y, sprite, hitbox, dx, dy, g)
        self.type = type
        self.from1 = from1
        self.toDoor = toDoor
        self.to1 = to1

    def use(self):
        self.from1.quit()
        self.to1.enter(self.toDoor.type)
        self.toDoor.timer = time.time()
        self.timer = time.time()


class Damageable:
    hp = 5
    last_attack = 0
    iframes = 0.6

    def hurt(self, proj, value):
        if proj.parent != self and time.time() - self.last_attack > self.iframes:
            self.hp -= value
            self.last_attack = time.time()


class Ground(InteractableObject):
    def __init__(self, x, y, x_size, y_size, sprite=None, dx=0, dy=0, g=5):
        super().__init__(x, y, sprite, Hitbox(x_size, y_size), dx, dy, g)


class LevelGenerator:
    def __init__(self):
        self.id = 0
        self.map = [[None for i in range(7)] for i2 in range(7)]
        random.seed(7)
        self.maxLVL = 10
        self.generateLevel(0, 0)
        for y in range(7):
            for x in range(7):
                if self.map[y][x] != None:
                    self.addWallsAndDoors(x, y)
        for y in range(7):
            for x in range(7):
                if self.map[y][x] != None:
                    self.connect(x, y)

    def generateLevel(self, x, y):
        if 0 <= x <= 6 and 0 <= y <= 6 and self.map[x][y] == None and self.id < self.maxLVL:
            self.map[x][y] = self.id
            self.id += 1
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if random.choice([True, False]) and (i == 0 or j == 0):
                        self.generateLevel(x + i, y + j)

    def combineLeftRight(self, roomL, roomR):
        roomL.rightDoor.toDoor = roomR.leftDoor
        roomR.leftDoor.toDoor = roomL.rightDoor
        roomR.leftDoor.to1 = roomL
        roomL.rightDoor.to1 = roomR

    def combineUpDown(self, roomU, roomD):
        roomU.downDoor.toDoor = roomD.upDoor
        roomD.upDoor.toDoor = roomU.downDoor
        roomU.downDoor.to1 = roomD
        roomD.upDoor.to1 = roomU

    def getRoomID(self, x, y):
        return self.map[y][x]

    def addWallsAndDoors(self, x=0, y=0):
        walls = []
        platforms = [Ground(270, 150, 14 * 30, 30),
                     Ground(270, 450, 14 * 30, 30),
                     Ground(90, 300, 8 * 30, 30),
                     Ground(90, 570, 8 * 30, 30),
                     Ground(620, 300, 8 * 30, 30),
                     Ground(620, 570, 8 * 30, 30)]
        room = Room([], self.getRoomID(x, y))
        import Scripts.Enemies
        Spawner(220, 130, Scripts.Enemies.FlyingGuy, room)
        GameManager.Rooms.append(room)
        if self.checkRoomExistence(x - 1, y):
            walls.append(Ground(0, 0, 30, 305))
            walls.append(Ground(0, 415, 30, 330))
            room.leftDoor = Door(-80, 305, Sprite('Sprites/door.png', z=-1), Hitbox(110, 110), room, None, None,
                                 type='left')
            room.filling.append(room.leftDoor)
            room.leftDoor.hitbox.show()
        else:
            walls.append(Ground(0, 0, 30, 720))

        if self.checkRoomExistence(x + 1, y):
            walls.append(Ground(930, 0, 30, 305))
            walls.append(Ground(930, 415, 30, 330))
            room.rightDoor = Door(930, 305, Sprite('Sprites/door.png', z=-1), Hitbox(110, 110), room, None, None,
                                  type='right')
            room.filling.append(room.rightDoor)
            room.rightDoor.hitbox.show()
        else:
            walls.append(Ground(930, 0, 30, 720))

        if self.checkRoomExistence(x, y - 1):
            walls.append(Ground(0, 0, 425, 30))
            walls.append(Ground(535, 0, 450, 30))
            room.upDoor = Door(425, -80, Sprite('Sprites/door.png', z=-1), Hitbox(110, 110), room, None, None,
                               type='up')
            room.upDoor.upwards = True
            room.filling.append(room.upDoor)
            room.upDoor.hitbox.show()
        else:
            walls.append(Ground(0, 0, 960, 30))

        if self.checkRoomExistence(x, y + 1):
            walls.append(Ground(0, 690, 425, 30))
            walls.append(Ground(535, 690, 450, 30))
            room.downDoor = Door(425, 690, Sprite('Sprites/door.png', z=-1), Hitbox(110, 110), room, None, None,
                                 type='down')
            room.filling.append(room.downDoor)
            room.downDoor.hitbox.show()
        else:
            walls.append(Ground(0, 690, 960, 30))
        for i in walls:
            room.filling.append(i)
        for i in platforms:
            room.filling.append(i)
        return room

    def connect(self, x=0, y=0):
        room = GameManager.searchByID(self.getRoomID(x, y))
        if self.checkRoomExistence(x - 1, y):
            self.combineLeftRight(GameManager.searchByID(self.getRoomID(x - 1, y)), room)
        if self.checkRoomExistence(x + 1, y):
            self.combineLeftRight(room, GameManager.searchByID(self.getRoomID(x + 1, y)))
        if self.checkRoomExistence(x, y - 1):
            self.combineUpDown(GameManager.searchByID(self.getRoomID(x, y - 1)), room)
        if self.checkRoomExistence(x, y + 1):
            self.combineUpDown(room, GameManager.searchByID(self.getRoomID(x, y + 1)))

    def checkRoomExistence(self, x, y):
        if 0 <= x <= 6 and 0 <= y <= 6:
            if self.map[y][x] != None:
                return True
        return False
