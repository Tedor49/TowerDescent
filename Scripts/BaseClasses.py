import sys
import time
import random
import pygame
import json


class GameObject:
    """Default interface for Game Object"""

    def __init__(self, x=0, y=0):
        """
        Initialization of a Game Object
        :param x: coordinate on the x_axis
        :param y: coordinate on the y_axis
        """
        self.x = x
        self.y = y

    def tick(self):
        """
        Default function for ticking an object
        :return: None
        """
        return

    def get_x(self):
        """
        Getter for the x coordinate
        :return: x coordinate
        """
        return self.x

    def get_y(self):
        """
        Getter for the y coordinate
        :return: y coordinate
        """
        return self.y

    def add_to_manager(self):
        """
        Method that adds object instance to the Game Manager
        """
        GameManager.all_Objects.add(self)

    def delete(self):
        """
        Method that adds removes object from the Game Manager
        """
        if self in GameManager.all_Objects:
            GameManager.all_Objects.remove(self)


class Spawner(GameObject):
    """Spawner that creates enemy instances in rooms"""

    def __init__(self, x, y, enemy, room1):
        """
        The initialization method for Spawner
        :param x: x coordinate
        :param y: y coordinate
        :param room1: room, in which Spawner is located
        """
        super().__init__(x, y)
        self.enemy = enemy
        self.room = room1
        self.room.filling.append(self)
        self.inactive = False
        self.enemyInstance = None

    def spawn(self):
        """
        Spawner function that spawns an enemy instance
        """
        from Scripts.Enemies import Movement
        movement = Movement()
        if not self.inactive:
            if self.enemyInstance is None:
                self.enemyInstance = self.enemy(self.x, self.y, Sprite('Sprites/playernew.png'), Hitbox(50, 50),
                                                GameManager.player, move=movement.get_random_movement())
            self.room.filling.append(self.enemyInstance)

    def despawn(self):
        """
        Function that despawns an enemy instance and checks if its hp > 0
        """
        if self.enemyInstance.hp <= 0:
            self.inactive = True
            GameManager.to_remove.append(self)
            self.room.filling.remove(self)
        else:
            self.enemyInstance.x = self.x
            self.enemyInstance.y = self.y
            GameManager.to_remove.append(self.enemyInstance)
            self.room.filling.remove(self.enemyInstance)


class InfiniteSpawner(GameObject):
    """Infinite Spawner that spawns an infinite number of enemy instances"""

    def __init__(self, x, y):
        """
        The initialization method for an Infinite Spawner
        :param x: x coordinate
        :param y: y coordinate
        """

        super().__init__(x, y)
        GameManager.to_add.append(self)
        self.cooldown = 3000

    def tick(self):
        """Actions that Infinite Spawner conducts each tick"""
        from Scripts.Enemies import Movement, BaseEnemy
        if self.cooldown > 0:
            self.cooldown -= GameManager.time_elapsed
        else:
            enemy = BaseEnemy(self.x, self.y, Sprite('Sprites/playernew.png'), Hitbox(50, 50),
                              GameManager.player, move=Movement.follow_flying_move)
            GameManager.to_add.append(enemy)
            self.cooldown = random.randint(5000, 10000)


class Hitbox(GameObject):
    """Hitbox that is used to check intersections and interactions of different objects"""

    def __init__(self, x_size, y_size, x=0, y=0, parent=None):
        """
        The initialization method for Hitbox
        :param x_size: size on the x axis
        :param y_size: size on the y axis
        :param x: x coordinate relative to the object that owns this hitbox
        :param y: y coordinate relative to the object that owns this hitbox
        :param parent: Object which owns this Hitbox
        """
        super().__init__(x, y)
        self.parent = parent
        self.x_size = x_size
        self.y_size = y_size
        self.ray_quality = 1
        self.epsilon = 0.000001

    def get_x(self):
        """
        Get the x coordinate of the Hitbox
        :return: x coordinate of the Hitbox
        """
        return self.parent.get_x() + self.x

    def get_y(self):
        """
        Get the x coordinate of the Hitbox
        :return: x coordinate of the Hitbox
        """
        return self.parent.get_y() + self.y

    def intersects(self, other):
        """
        Method that checks if one hitbox intersects other
        :param other: hitbox with which we check intersections
        :return: x and y coordinate of intersection
        """
        self_x_end = self.get_x() + self.x_size
        self_y_end = self.get_y() + self.y_size
        other_x_end = other.get_x() + other.x_size
        other_y_end = other.get_y() + other.y_size
        intersect_x = (self.get_x() - other_x_end) * (other.get_x() - self_x_end) >= 0
        intersect_y = (self.get_y() - other_y_end) * (other.get_y() - self_y_end) >= 0
        return intersect_x and intersect_y

    def modify_movement(self, movement, hbox, mode="stop"):
        """Method that modifies the movement in regard to another hitbox"""
        if mode == "pass":
            return movement

        def vec(p1, p2):
            """
            function that returns the vector between two points
            :param p1: first point
            :param p2: second point
            :return: vector from one point to another
            """
            return p2[0] - p1[0], p2[1] - p1[1]

        def cross(vec1x, vec1y, vec2x, vec2y):
            """
            Function that calculates cross product of two vectors
            :param vec1x: x coordinate of the first vector
            :param vec1y: y coordinate of the first vector
            :param vec2x: x coordinate of the second vector
            :param vec2y: y coordinate of the second vector
            :return: the cross product
            """
            return vec1x * vec2y - vec1y * vec2x

        def seg_to_line(beg, end):
            """
            Function that creates a line from a segment of two points
            :param beg: first point
            :param end: second point
            :return: coefficients of the line equation
            """
            return beg[1] - end[1], end[0] - beg[0], beg[0] * end[1] - end[0] * beg[1]

        def intersect_lines(a1, b1, c1, a2, b2, c2):
            """
            Function that computes the point of intersection of line
            :param a1: a coefficient of the first line
            :param b1: b coefficient of the first line
            :param c1: c coefficient of the first line
            :param a2: a coefficient of the second line
            :param b2: b coefficient of the second line
            :param c2: c coefficient of the second line
            :return: point of intersection of two lines
            """
            denominator = (a1 * b2 - a2 * b1)
            return [(b1 * c2 - b2 * c1) / denominator, (a2 * c1 - a1 * c2) / denominator]

        def intersect_segments(seg1, seg2):
            """
            Function that computes the point of intersection of two segments
            :param seg1: first line segment
            :param seg2: second line segment
            :return: the point of intersection or None
            """
            if cross(*vec(seg1[0], seg1[1]), *vec(seg1[0], seg2[0])) * \
                    cross(*vec(seg1[0], seg1[1]), *vec(seg1[0], seg2[1])) > 0 or \
                    cross(*vec(seg2[0], seg2[1]), *vec(seg2[0], seg1[0])) * \
                    cross(*vec(seg2[0], seg2[1]), *vec(seg2[0], seg1[1])) > 0:
                return None
            return intersect_lines(*seg_to_line(*seg1), *seg_to_line(*seg2))

        def pythagoreas(x1, y1, x2, y2):
            """
            Function that computes pythagorean length of the line segment
            :param x1: x coordinate for the first point
            :param y1: y coordinate for the first point
            :param x2: x coordinate for the second point
            :param y2: y coordinate for the second point
            :return: pythagorean length of the line segment
            """
            return (x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2)

        sides = {"LEFT": (
            (self.get_x(), self.get_y()), (self.get_x(), self.get_y() + self.y_size)),
            "TOP":
                ((self.get_x() + self.x_size, self.get_y()), (self.get_x(), self.get_y())),
            "RIGHT": (
                (self.get_x() + self.x_size, self.get_y() + self.y_size), (self.get_x() + self.x_size, self.get_y())),
            "BOTTOM": (
                (self.get_x(), self.get_y() + self.y_size), (self.get_x() + self.x_size, self.get_y() + self.y_size))}

        def ray_intersect(segment):
            """
            Calculates the ray intersection with the hitbox
            :param segment: line segment
            :return: information about the intersection
            """
            intersections = []

            selected_sides = []
            movement_vector_x = segment[1][0] - segment[0][0]
            movement_vector_y = segment[1][1] - segment[0][1]

            if movement_vector_x > 0:
                selected_sides.append("LEFT")
            elif movement_vector_x < 0:
                selected_sides.append("RIGHT")

            if movement_vector_y > 0:
                selected_sides.append("TOP")
            elif movement_vector_y < 0:
                selected_sides.append("BOTTOM")

            for hitbox_side in selected_sides:
                if intersect_segments(sides[hitbox_side], segment):
                    intersections.append([hitbox_side, intersect_segments(sides[hitbox_side], segment)])
                    if hitbox_side == "TOP":
                        intersections[-1][1][1] = sides[hitbox_side][0][1] - self.epsilon
                    elif hitbox_side == "BOTTOM":
                        intersections[-1][1][1] = sides[hitbox_side][0][1] + self.epsilon
                    elif hitbox_side == "LEFT":
                        intersections[-1][1][0] = sides[hitbox_side][0][0] - self.epsilon
                    else:
                        intersections[-1][1][0] = sides[hitbox_side][0][0] + self.epsilon

            if not intersections:
                return None
            else:
                return min(intersections, key=lambda x: pythagoreas(*x[1], *segment[0]))

        def ratio_point(x1, y1, x2, y2, ratio):
            """
            Calculates a point that lies at a specific ratio between 2 points
            :param x1: x coordinate of the first point
            :param y1: y coordinate of the first point
            :param x2: x coordinate of the second point
            :param y2: y coordinate of the first point
            :param ratio: ratio
            """
            return x1 * ratio + x2 * (1 - ratio), y1 * ratio + y2 * (1 - ratio)

        rays = []

        moving_sides = {"LEFT": (
            (hbox.get_x(), hbox.get_y()), (hbox.get_x(), hbox.get_y() + hbox.y_size)),
            "TOP":
                ((hbox.get_x() + hbox.x_size, hbox.get_y()), (hbox.get_x(), hbox.get_y())),
            "RIGHT": (
                (hbox.get_x() + hbox.x_size, hbox.get_y() + hbox.y_size), (hbox.get_x() + hbox.x_size, hbox.get_y())),
            "BOTTOM": (
                (hbox.get_x(), hbox.get_y() + hbox.y_size), (hbox.get_x() + hbox.x_size, hbox.get_y() + hbox.y_size))}

        for side in moving_sides:
            for j in range(hbox.ray_quality):
                ray_start = ratio_point(*moving_sides[side][0], *moving_sides[side][1], j / hbox.ray_quality)
                ray_end = (ray_start[0] + movement[1][0] - movement[0][0],
                           ray_start[1] + movement[1][1] - movement[0][1])
                ray_offset = (hbox.get_x() - ray_start[0], hbox.get_y() - ray_start[1])
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
        """
        Method that checks hitboxes with which there is an intersection
        :param movement: movement flag
        :return: array of hitboxes, with which there is an intersection
        """
        intersecting = []
        for hitbox in GameManager.all_Hitboxes:
            if hitbox != self:
                if not movement and self.intersects(hitbox):
                    intersecting.append(hitbox)
                elif movement and hitbox.modify_movement(movement, self)[0] != movement:
                    intersecting.append(hitbox)
        return intersecting

    def show(self):
        """
        Method that shows the Hitbox using Sprite
        """
        sprite = Sprite("Sprites/hitbox.png", z=0)
        sprite.image = pygame.transform.scale(sprite.image, (self.x_size, self.y_size))
        sprite.parent = self
        GameManager.all_Sprites.add(sprite)


class Sprite(GameObject):
    """Class that represents the visible part of the object"""
    active = True

    def __init__(self, image, stretch_x=1, stretch_y=1, z=1, x=0, y=0, parent=None):
        """
        The initialization method for Sprite
        :param image: image for a Sprite
        :param stretch_x: scale on the x coordinate
        :param stretch_y: scale on the y coordinate
        :param z: z coordinate
        :param x: x coordinate relative to the object that owns this hitbox
        :param y: y coordinate relative to the object that owns this hitbox
        :param parent: Object that owns this sprite
        """
        super().__init__(x, y)
        self.parent = parent
        self.z = z
        self.optimized = False
        picture = pygame.image.load(image)
        self.image = pygame.transform.scale(picture, (int(picture.get_size()[0] * stretch_x),
                                                      int(picture.get_size()[1] * stretch_y)))

    def get_x(self):
        """
        Method that gets x coordinate of the sprite
        :return: x coordinate of the sprite
        """
        return self.parent.get_x() + self.x

    def get_y(self):
        """
        Method, that gets y coordinate of the Sprite
        :return: y coordinate of the sprite
        """
        return self.parent.get_y() + self.y

    def draw(self):
        """
        Method that is used to draw the Sprite
        """
        if self.active:
            GameManager.screen.blit(self.image, (self.get_x(), self.get_y()))

    def optimize(self):
        """Method that optimizes the Sprite image"""
        if not self.optimized:
            self.optimized = True
            self.image = self.image.convert_alpha()


class InteractableObject(GameObject):
    """Class that represents an object that can have a hitbox and/or a sprite and, thus, can be interacted with"""

    def __init__(self, x, y, sprite=None, hitbox=None, dx=0, dy=0, g=0.002):
        """
        Initialization of an Interactable Object
        :param x: coordinate on the x axis
        :param y: coordinate on the y axis
        :param sprite: Sprite instance that is owned by this Interactable Object
        :param hitbox: Hitbox instance that is owned by this Interactable Object
        :param dx:  motion over the x axis
        :param dy: motion over the y axis
        :param g: acceleration of gravity
        """
        GameObject.__init__(self, x, y)
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
        """Tick function of an Interactable Object"""
        self.x += self.dx * GameManager.time_elapsed
        self.y += self.dy * GameManager.time_elapsed

    def getdx(self):
        """
        Method that gets dx
        :return: dx
        """

        return self.dx

    def getdy(self):
        """
        Method that gets dy
        :return: dy
        """
        return self.dy

    def get_x(self):
        """
        Method that gets coordinate on the x axis
        :return: x coordinate
        """
        return self.x

    def get_y(self):
        """
        Method that gets coordinate on the y axis
        :return: y coordinate
        """
        return self.y

    def add_to_manager(self):
        """Method that adds InteractableObject to GameManager"""
        GameManager.all_Objects.add(self)
        if self.hitbox:
            GameManager.all_Hitboxes.add(self.hitbox)
        if self.sprite:
            GameManager.all_Sprites.add(self.sprite)

    def delete(self):
        """Method that removes Interactable Object from GameManager"""
        if self in GameManager.all_Objects:
            GameManager.all_Objects.remove(self)
        if self.hitbox and self.hitbox in GameManager.all_Hitboxes:
            GameManager.all_Hitboxes.remove(self.hitbox)
        if self.sprite and self.sprite in GameManager.all_Sprites:
            GameManager.all_Sprites.remove(self.sprite)


class Attack(InteractableObject):
    """Class that represents different attacks"""

    def __init__(self, x, y, sprite, hitbox, parent, dx=0, dy=0):
        """
        The initialization method for Attack class
        :param x: coordinate on the x axis
        :param y: coordinate on the y axis
        :param sprite: Sprite instance that is owned by this Attack
        :param hitbox: Hitbox instance that is owned by this Attack
        :param parent: Object, which owns this Attack
        :param dx:  motion over the x axis
        :param dy: motion over the y axis
        """
        super().__init__(x, y, sprite, hitbox, dx, dy)
        self.parent = parent
        self.angle = 0
        GameManager.to_add.append(self)

    def do(self, to_x, to_y):
        """Method, that represent what Attack will do when triggered"""
        pass

    def tick(self):
        """Tick for the Attack object"""
        pass


class Menu:
    """Class that represents Menu"""

    def __init__(self):
        """Initialization of the Menu, where main pygame cycle for a Menu page occurs"""
        pygame.init()
        size = [960, 720]
        screen = pygame.display.set_mode(size)
        pygame.display.set_caption('Madness Descent menu')
        running = True
        screen.fill(pygame.Color('white'))
        font = pygame.font.SysFont('arial', 50)
        text = font.render('Start',
                           True, (0, 0, 0))
        text_x = 440
        text_y = 330
        screen.blit(text, (text_x, text_y))
        screen.blit(pygame.image.load("Sprites/logo.png"), (220, 60))
        while running:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if 440 < x < 540 and 330 < y < 370:
                        pygame.quit()
                        GameManager()
                if event.type == pygame.QUIT:
                    running = False
            pygame.display.flip()


class GameManager:
    """Class that manages all events in the game"""
    power_ups = None
    to_add = []
    to_remove = []
    screen = None
    clock = None
    player = None
    time_elapsed = 0
    tps = 120
    current_room = None
    all_Hitboxes = set()
    all_Objects = set()
    all_Sprites = set()
    Rooms = []
    not_cleared_rooms = 0
    lvl_number = 0
    interdimensional_room = None
    background = None
    elevator_broken = False
    running = True
    level = None

    def __init__(self):
        """Initialization of a GameManager object, where the main cycle occurs"""
        import Scripts.Powerups
        GameManager.power_ups = [
            ('Sprites\\Powerups\\doubleJump.png', Scripts.Powerups.DoubleJump),
            ('Sprites\\Powerups\\doubleDamage.png', Scripts.Powerups.DoubleDamage),
            ('Sprites\\Powerups\\bouncyBullets.png', Scripts.Powerups.BouncyBullets),
            ('Sprites\\Powerups\\discardWeapon.png', Scripts.Powerups.DiscardWeapon),
            ('Sprites\\Powerups\\infiniteAmmo.png', Scripts.Powerups.InfiniteAmmo),
            ('Sprites\\PowerUps\\swordReflect.png', Scripts.Powerups.SwordReflect),
            ('Sprites\\PowerUps\\lowGrav.png', Scripts.Powerups.LowGravity),
            ('Sprites\\PowerUps\\lowerCooldown.png', Scripts.Powerups.LowerCooldown),
            ('Sprites\\PowerUps\\berserker.png', Scripts.Powerups.FistPowerUp)
        ]
        from Scripts.Player import Player
        pygame.init()
        size = [960, 720]
        GameManager.level = LevelGenerator(GameManager.lvl_number + 7)
        GameManager.player = Player(455, 100, Sprite('Sprites/playernew.png'), Hitbox(50, 50))
        GameManager.screen = pygame.display.set_mode(size)
        GameManager.not_cleared_rooms = len(GameManager.Rooms)
        pygame.display.set_caption('Madness Descent')
        GameManager.clock = pygame.time.Clock()
        GameManager.current_room = GameManager.search_by_id(0)
        pygame.display.set_icon(pygame.image.load("Sprites/playernew.png"))
        self.update()
        GameManager.to_add.append(GameManager.player)
        GameManager.current_room.enter(enter_type="up")
        GameManager.running = True

        while GameManager.running:
            GameManager.clock.tick()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
            GameManager.time_elapsed += GameManager.clock.get_time()
            if GameManager.time_elapsed < 1000 / GameManager.tps:
                continue
            for game_object in GameManager.all_Objects:
                game_object.tick()
            GameManager.screen.fill((255, 255, 255))
            for sprite in sorted(GameManager.all_Sprites, key=lambda x: x.z):
                sprite.optimize()
                sprite.draw()
            pygame.display.flip()
            GameManager.time_elapsed = 0
            self.update()
        sys.exit()

    @staticmethod
    def update():
        """Method that adds and deletes Objects that are scheduled to be so"""
        for game_object in GameManager.to_add:
            game_object.add_to_manager()
        GameManager.to_add = []
        for game_object in set(GameManager.to_remove):
            game_object.delete()
        GameManager.to_remove = []

    @staticmethod
    def search_by_id(room_id):
        """
        Method that returns room by using its id
        :param room_id: id of a room
        :return: room with the required id
        """
        for room in GameManager.Rooms:
            if room.id == room_id:
                return room
        return None

    @staticmethod
    def new_level():
        """
        Method that creates new level
        """
        from Scripts.AnimatedSprites import AnimatedEntryElevator
        GameManager.lvl_number += 1
        GameManager.to_add = []
        GameManager.to_remove = []
        GameManager.current_room = None
        GameManager.all_Hitboxes = set()
        GameManager.all_Objects = set()
        GameManager.all_Sprites = set()
        GameManager.Rooms = []
        GameManager.level = LevelGenerator()
        GameManager.not_cleared_rooms = len(GameManager.Rooms)
        GameManager.current_room = GameManager.search_by_id(0)
        GameManager.to_add.append(GameManager.player)
        GameManager.current_room.enter()
        GameManager.player.x, GameManager.player.y = 455, 400
        GameManager.player.dx, GameManager.player.dy = 0, 0
        entry_elevator = AnimatedEntryElevator()
        GameManager.all_Sprites.add(entry_elevator)
        GameManager.all_Objects.add(entry_elevator)


class Room:
    """Class that represents Room on the level"""

    def __init__(self, filling, room_id):
        """
        Initialization for a Room class
        :param filling: filling of the room
        :param room_id: id of the room
        """
        self.filling = filling
        self.id = room_id
        self.left_door = None
        self.right_door = None
        self.up_door = None
        self.down_door = None
        self.checked = False
        self.left_checked = False
        self.right_checked = False
        self.up_checked = False
        self.down_checked = False
        self.cleaned = False
        self.type = ''

    def enter(self, enter_type='left'):
        """
        Method that add filling of the room to the GameManager
        :param enter_type: direction from which the player enters
        """
        from Scripts.Player import Player
        coordinates = {
            'up': (450, 40),
            'down': (450, 630),
            'left': (30, 350),
            'right': (880, 350)
        }
        GameManager.player.x = coordinates[enter_type][0]
        GameManager.player.y = coordinates[enter_type][1]
        GameManager.current_room = self
        for game_object in self.filling:
            if isinstance(game_object, Spawner):
                game_object.spawn()
            if not isinstance(game_object, Player):
                GameManager.to_add.append(game_object)

    def quit(self):
        """
        Method that will quit from the room and add changes to GameManager
        """
        for game_object in GameManager.all_Objects:
            if isinstance(game_object, Attack):
                if game_object in self.filling:
                    self.filling.remove(game_object)
            if isinstance(game_object, Spawner):
                game_object.despawn()
            if not isinstance(game_object, Persistent):
                GameManager.to_remove.append(game_object)

    def check_cleaned(self):
        """
        Method that checks if the room is cleared from enemies
        :return: True or False, depending on the filling of the room
        """
        for game_object in self.filling:
            if isinstance(game_object, Spawner):
                return False
        self.cleaned = True
        return True


class InterDimensionalRoom(Room):
    """Class that represents room between levels"""

    def __init__(self):
        """Initialization for an InterDimensionalRoom class, where filling and sprites are specified"""

        super().__init__([], -1)

        if not GameManager.elevator_broken:
            cur_sprite = "Sprites/elevator.png"
        else:
            cur_sprite = "Sprites/elevator_broken_player.png"

        self.filling += [Elevator(450, -500, Sprite(cur_sprite, z=-2), Hitbox(60, 110)),
                         InteractableObject(0, 0, Sprite("Sprites/Levels/background_elevator.png", z=-4))]
        self.power_ups = []

    def enter(self, enter_type='elevator'):
        """
        Method that add filling of the room to the GameManager
        :param enter_type: direction from which the player enters
        """

        for element_of_interface in GameManager.player.gui:
            element_of_interface.active = False
        GameManager.player.x = 480
        GameManager.player.y = -120
        self.get_power_ups()
        GameManager.current_room = self
        for game_object in self.filling:
            GameManager.to_add.append(game_object)

    def quit(self):
        """
        Method that will quit from the InterDimensionalRoom and create a new level for a GameManager
        """

        for elements_of_interface in GameManager.player.gui:
            elements_of_interface.active = True
        GameManager.new_level()

    def get_power_ups(self):
        """Method that creates objects representing power_ups in InterDimensionalRoom"""

        while len(self.power_ups) != 3:
            power_up = random.choice(GameManager.power_ups)
            if power_up in self.power_ups:
                continue
            else:
                self.power_ups.append(power_up)
                GameManager.power_ups.remove(power_up)
        for i in range(len(self.power_ups)):
            self.filling.append(InteractableObject(150 * (i + 1) + 120 * i, 540,
                                                   Sprite(self.power_ups[i][0], z=-2), None))


class DeathPlane(InteractableObject):
    """Class that represents death plane"""

    def __init__(self, x, y, x_size, y_size):
        """
        The initialization method of DeathPlane
        :param x: coordinate on the x axis
        :param y: coordinate on the y axis
        :param x_size: size on the x axis
        :param y_size: size on the y axis
        """
        super().__init__(x, y, None, Hitbox(x_size, y_size))


class FakeInterDimensionalRoom(Room):
    """Class that represents room which will be used for the third boss fight"""

    def __init__(self):
        """Initialization for FakeInterDimensionalRoom class, where the filling of the room is specified"""

        from Scripts.AnimatedSprites import AnimatedTop
        super().__init__([], -1)
        self.cap = InteractableObject(450, 370, AnimatedTop())

        self.filling += [InteractableObject(0, 0, Sprite("Sprites/Levels/background_elevator.png", z=-4)),
                         InteractableObject(450, 420, Sprite("Sprites/elevatorBottom.png", z=4)),
                         self.cap,
                         InteractableObject(450, -340, Sprite("Sprites/rope.png", z=-2)),
                         DeathPlane(-10000, 690, 20960, 30),
                         Ground(450, 450, 60, 30)]

    def enter(self, enter_type='elevator'):
        """
        Method that add filling of the room to the GameManager
        :param enter_type: direction from which the player enters
        """

        for element_of_interface in GameManager.player.gui:
            element_of_interface.active = False
        GameManager.player.x = 440
        GameManager.player.y = 400
        GameManager.current_room = self
        for game_object in self.filling:
            GameManager.to_add.append(game_object)


class Door(InteractableObject):
    """Class that represents doors between the rooms"""

    def __init__(self, x, y, sprite, hitbox, from_room, to_room, to_door, enter_type=None, usable=True):
        """
        The initialization method of door
        :param x: coordinate on the x axis
        :param y: coordinate on the y axis
        :param sprite: Sprite which will be used by the Door instance
        :param hitbox: Hitbox which will be used by the Door instance
        :param from_room: from which room the door transports
        :param to_room: to which room the door transports
        :param to_door: door that works between both room but in the opposite way
        :param enter_type: the direction of the door
        :param usable: If the door can be passed through
        """
        super().__init__(x, y, sprite, hitbox)
        self.type = enter_type
        self.from_room = from_room
        self.to_door = to_door
        self.to_room = to_room
        self.usable = usable

    def use(self):
        """ Method that causes enter funtion in the next room and quit function in the currens, so the GameManager will
        change itself accordingly"""
        self.from_room.quit()
        if self.from_room.cleaned is False:
            print(1, self.from_room.check_cleaned())
            if self.from_room.check_cleaned():
                GameManager.not_cleared_rooms -= 1
                print(GameManager.not_cleared_rooms)
                if GameManager.not_cleared_rooms == 1:
                    GameManager.search_by_id(0).left_door.usable = True
                    GameManager.level.boss_wall.image.fill((255, 255, 255, 0), ((0, 300), (30, 120)))
        self.to_room.enter(self.to_door.type)
        self.to_door.timer = time.time()


class Damageable:
    """Class that represents damageable objects"""
    hp = 5
    last_attack = 0
    iframes = 0.4

    def hurt(self, proj, value):
        """Method that is used when Damageable object is damaged by other object"""

        if proj.parent != self and time.time() - self.last_attack > self.iframes:
            self.hp -= value
            self.last_attack = time.time()


class Ground(InteractableObject):
    """Class that represents ground"""

    def __init__(self, x, y, x_size, y_size, sprite=None):
        """
        The initialization method of Ground
        :param x: coordinate on the x axis
        :param y: coordinate on the y axis
        :param x_size: size on the x axis
        :param y_size: size on the y axis
        :param sprite: Sprite which will be used by the Ground instance
        """
        super().__init__(x, y, sprite, Hitbox(x_size, y_size))


class LevelGenerator:
    """Class that is used to generate random level"""

    def __init__(self, rooms_minimum=7):
        """
        Initialization for a LevelGenerator class, which creates level and adds it to the GameManager
        :param rooms_minimum: minimum rooms on this level
        """
        self.id = 0
        self.map = [[None]*6 for i in range(7)]
        self.rooms_maximum = rooms_minimum + 2
        self.rooms_minimum = rooms_minimum
        self.generate_level(0, 1)
        self.boss_wall = None
        self.dim_room = InterDimensionalRoom()
        while not self.id >= rooms_minimum:
            self.id = 0
            self.map = [[None]*6 for i2 in range(7)]
            self.generate_level(0, 1)
        for y in range(len(self.map)):
            for x in range(len(self.map[0])):
                if self.map[y][x] is not None:
                    self.add_walls_and_doors(x, y)
        for y in range(len(self.map)):
            for x in range(len(self.map[0])):
                if self.map[y][x] is not None:
                    self.connect(x, y)

    def generate_level(self, y, x):
        """
        Method, where the matrix for a level is generated
        :param y: y coordinate in the matrix
        :param x: x coordinate in the matrix
        :return:
        """
        forbidden = [(0, 1), (1, 1)]
        if 0 <= x <= len(self.map[0]) - 1 and 0 <= y <= len(self.map) - 1\
                and self.map[y][x] is None and self.id < self.rooms_maximum:
            self.map[y][x] = self.id
            self.id += 1
            if x == 1 and y == 0:
                self.generate_level(y, x - 1)
                self.generate_level(y, x + 1)
            for i in range(0, 2):
                for j in range(-1, 2):
                    if random.choice([True, False, True]) and (i == 0 or j == 0) and (x + j, y + i) not in forbidden:
                        self.generate_level(y + i, x + j)

    def combine_left_right(self, room_left, room_right):
        """
        Method that connects two rooms on the x axis
        :param room_left: Door in the left room
        :param room_right: Door in the right room
        :return:
        """
        room_left.right_door.to_door = room_right.left_door
        room_right.left_door.to_door = room_left.right_door
        room_right.left_door.to_room = room_left
        room_left.right_door.to_room = room_right

    def combine_up_down(self, room_up, room_down):
        """
        Method that connects two rooms on the y axis
        :param room_up: Door in the upper room
        :param room_down: Door in the lower room
        :return:
        """
        room_up.down_door.to_door = room_down.up_door
        room_down.up_door.to_door = room_up.down_door
        room_up.down_door.to_room = room_down
        room_down.up_door.to_room = room_up

    def get_room_id(self, x, y):
        """
        Method that returns id of the room depending on coordinates
        :param x: coordinate on the x axis
        :param y: coordinate on the y axis
        :return: id of the room
        """
        return self.map[y][x]

    def add_walls_and_doors(self, x=0, y=0):
        """
        Method that creates room where walls, doors, and sprites are specified
        :param x: coordinate of the room on the x axis
        :param y: coordinate of the room on the y axis
        :return: generated room
        """
        import Scripts.Enemies
        from Scripts.AnimatedSprites import AnimatedExitElevator

        room = Room([], self.get_room_id(x, y))

        if x == 0 and y == 0:
            room_type = 'boss_' + str(GameManager.lvl_number % 4)

            exit_elevator = Elevator(450, -120, AnimatedExitElevator(), Hitbox(60, 110), usable=False, direction='to')
            if room_type == "boss_0":
                room.filling.append(Scripts.Enemies.Boss0(GameManager.player, exit_elevator))
                room.filling.append(Scripts.Enemies.GunArm(GameManager.player))
                room.filling.append(exit_elevator)
            elif room_type == "boss_1":
                room.filling.append(Scripts.Enemies.Boss1(GameManager.player, exit_elevator))
                room.filling.append(exit_elevator)
            elif room_type == "boss_2":
                room.filling.append(exit_elevator)
                exit_elevator.spawn(310)
            elif room_type == "boss_3":
                room.filling.append(FinalManager())
            else:
                room.filling.append(Scripts.Enemies.Boss0(GameManager.player, exit_elevator))
                room.filling.append(exit_elevator)
        elif x == 1 and y == 0:
            room_type = 'start'
        else:
            room_type = 'map_' + str(random.randint(0, 4))
        tags = {
            0: '_BW.png',
            1: '_CL.png',
            2: '_RL.png',
            3: '_FL.png'
        }
        walls = []
        map_data = json.load(open('Sprites\Levels\map_data.json', 'r'))
        room.type = room_type
        room_sprite = Sprite("Sprites/Levels/" + room.type + tags[GameManager.lvl_number % 4], z=-3)
        room.filling.append(InteractableObject(0, 0, room_sprite))
        room.filling.append(InteractableObject(0, 0,
                                               Sprite("Sprites/Levels/background" +
                                                      tags[GameManager.lvl_number % 4], z=-4)
                                               ))
        GameManager.background = InteractableObject(0, 0,
                                                    Sprite("Sprites/Levels/background" +
                                                           tags[GameManager.lvl_number % 4], z=-4)
                                                    )
        for platform_info in map_data[room_type]['platforms']:
            room.filling.append(Ground(platform_info['x'], platform_info['y'],
                                       platform_info['x_size'] * 30, platform_info['y_size'] * 30))
        for spawner_info in map_data[room_type]['spawners']:
            Spawner(spawner_info['x'], spawner_info['y'], Scripts.Enemies.BaseEnemy, room)
        GameManager.Rooms.append(room)
        if self.check_room_existence(x - 1, y):
            walls.append(Ground(0, 0, 30, 300))
            walls.append(Ground(0, 420, 30, 330))
            room.left_door = Door(-90, 300, None, Hitbox(120, 120), room, None, None,
                                  enter_type='left')
            if x - 1 == 0 and y == 0:
                room.left_door.usable = False
                self.boss_wall = room_sprite
            else:
                room_sprite.image.fill((255, 255, 255, 0), ((0, 300), (30, 120)))
            room.filling.append(room.left_door)
        else:
            walls.append(Ground(0, 0, 30, 720))

        if self.check_room_existence(x + 1, y):
            walls.append(Ground(930, 0, 30, 300))
            walls.append(Ground(930, 420, 30, 330))
            room.right_door = Door(930, 300, None, Hitbox(120, 120), room, None, None,
                                   enter_type='right')
            if x == 0 and y == 0 and GameManager.lvl_number % 4 == 3:
                room.right_door.usable = False
            else:
                room_sprite.image.fill((255, 255, 255, 0), ((930, 300), (30, 120)))
            room.filling.append(room.right_door)
        else:
            walls.append(Ground(930, 0, 30, 720))

        if self.check_room_existence(x, y - 1):
            walls.append(Ground(0, 0, 420, 30))
            walls.append(Ground(540, 0, 450, 30))
            room_sprite.image.fill((255, 255, 255, 0), ((420, 0), (120, 30)))
            room.up_door = Door(420, -80, None, Hitbox(110, 110), room, None, None,
                                enter_type='up')
            room.up_door.upwards = True
            room.filling.append(room.up_door)
        else:
            walls.append(Ground(0, 0, 960, 30))

        if self.check_room_existence(x, y + 1):
            walls.append(Ground(0, 690, 420, 30))
            walls.append(Ground(540, 690, 450, 30))
            room_sprite.image.fill((255, 255, 255, 0), ((420, 690), (120, 30)))
            room.down_door = Door(420, 690, None, Hitbox(110, 110), room, None, None,
                                  enter_type='down')
            room.filling.append(room.down_door)
        else:
            walls.append(Ground(0, 690, 960, 30))
        for wall in walls:
            room.filling.append(wall)
        return room

    def connect(self, x=0, y=0):
        """
        Room that connects all the rooms which are neighbours to the room specified by coordinates
        :param x: coordinate of the room on the x axis
        :param y: coordinate of the room on the y axis
        """
        room = GameManager.search_by_id(self.get_room_id(x, y))
        if self.check_room_existence(x - 1, y):
            self.combine_left_right(GameManager.search_by_id(self.get_room_id(x - 1, y)), room)
        if self.check_room_existence(x + 1, y):
            self.combine_left_right(room, GameManager.search_by_id(self.get_room_id(x + 1, y)))
        if self.check_room_existence(x, y - 1):
            self.combine_up_down(GameManager.search_by_id(self.get_room_id(x, y - 1)), room)
        if self.check_room_existence(x, y + 1):
            self.combine_up_down(room, GameManager.search_by_id(self.get_room_id(x, y + 1)))

    def check_room_existence(self, x, y):
        """
        Method that checks if the room exist at specified coordinates
        :param x: coordinate on the x axis
        :param y: coordinate on the y axis
        :return: boolean depending on the result
        """
        if 0 <= x <= len(self.map[0]) - 1 and 0 <= y <= len(self.map) - 1:
            if self.map[y][x] is not None:
                return True
        return False


class FinalManager(GameObject):
    """Class that changes the final room depending on the ending"""

    def add_to_manager(self):
        """Method that adds FinalManager Instance to the GameManager"""
        if GameManager.player.hp >= 70:
            from Scripts.AnimatedSprites import AnimatedEnding
            GameManager.to_add.append(InteractableObject(0, 0, AnimatedEnding()))
            GameManager.to_add.append(InteractableObject(0, 0, Sprite("Sprites/Levels/foreground_true_final.png", z=3)))
        else:
            from Scripts.Enemies import Boss3
            GameManager.to_add.append(InteractableObject(0, 0, Sprite("Sprites/Levels/foreground_final.png", z=3)))
            GameManager.to_add.append(InfiniteSpawner(480, 360))
            GameManager.to_add.append(Boss3(GameManager.player))


class Elevator(InteractableObject):
    """Class that represents elevator which takes player to another level"""

    def __init__(self, x, y, sprite, hitbox, dx=0, dy=0, g=5, direction='to', usable=True):
        """
        Initialization for an Elevator class
        :param x: coordinate on the x axis
        :param y: coordinate on the y axis
        :param sprite: Sprite which will be used by an Elevator instance
        :param hitbox: Hitbox which will be used by an Elevator instance
        :param dx: change on the x axis
        :param dy: change on the y axis
        :param g: acceleration of gravity
        :param direction: direction in which elevator works
        :param usable: flag which shows if the elevator can be used
        """
        super().__init__(x, y, sprite, hitbox, dx, dy, g)
        self.direction = direction
        self.usable = usable

    def use(self):
        """Method which is called when we need this elevator to work"""

        if self.usable and self.direction == 'to':
            GameManager.player.deactivate()
            self.sprite.play(750)

    def spawn(self, y):
        """Method that is called when we need elevator to play animated sprite"""

        self.sprite.play(y)


class Persistent:
    """Class that represents persistent objects, which are not removed when there is a room transition"""
    pass
