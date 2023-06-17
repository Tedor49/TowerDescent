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


class Hitbox(GameObject):
    def __init__(self, parent, x_size, y_size, x=0, y=0):
        super().__init__(x, y)
        self.x_size = x_size
        self.y_size = y_size
        self.parent = parent

    def getx(self):
        return self.parent.getx() + self.x

    def gety(self):
        return self.parent.gety() + self.y

    def intersects(self, other):
        self_x_end = self.getx() + self.x_size
        self_y_end = self.gety() + self.y_size
        other_x_end = other.getx() + other.x_size
        other_y_end = other.gety() + other.y_size
        intersect_x = (self.getx() - other_x_end) * (other.getx() - self_x_end) > 0
        intersect_y = (self.gety() - other_y_end) * (other.gety() - self_y_end) > 0
        return intersect_x and intersect_y

    def check_intersections(self):
        intersecting = []
        for i in GameManager.all_Hitboxes:
            if i != self:
                if self.intersects(i):
                    intersecting.append(i)
        return intersecting


class Sprite(GameObject):
    def __init__(self, image, stretch_x=1, stretch_y = 1, x=0, y=0, parent=None):
        super().__init__(x, y)
        self.parent = parent
        picture = pygame.image.load(image)
        self.image = pygame.transform.scale(picture, (int(picture.get_size()[0] * stretch_x), int(picture.get_size()[1] * stretch_y)))

    def getx(self):
        return self.parent.getx() + self.x

    def gety(self):
        return self.parent.gety() + self.y

    def draw(self):
        GameManager.screen.blit(self.image, (self.getx(), self.gety()))


class InteractableObject(GameObject):
    def __init__(self, x, y, sprite, dx=0, dy=0, g=5):
        super().__init__(x, y)
        self.dx = dx
        self.dy = dy
        self.g = g
        self.sprite = sprite
        sprite.parent = self
        self.hitbox = None
        GameManager.toAdd.append(self)

    def tick(self):
        self.x += self.dx * GameManager.time_elapsed
        self.y += self.dy * GameManager.time_elapsed

    def getdx(self):
        return self.dx

    def getdy(self):
        return self.dy

    def getx(self):
        return GameManager.camera.getx() + self.x

    def gety(self):
        return GameManager.camera.gety() + self.y

    def delete(self):
        GameManager.all_Objects.remove(self)
        GameManager.all_Sprites.remove(self.sprite)
        GameManager.all_Hitboxes.remove(self.hitbox)


class Camera(GameObject):
    def __init__(self, x=0, y=0):
        super().__init__(x, y)

    def tick(self):
        self.x = -GameManager.player.x + 250
        self.y = -GameManager.player.y + 250


class GameManager:
    toAdd = []
    toRemove = []
    all_Hitboxes = set()
    all_Objects = set()
    all_Sprites = set()
    screen = None
    clock = None
    player = None
    camera = None
    time_elapsed = 0
    tps = 400

    def __init__(self):
        pygame.init()
        size = [700, 700]
        GameManager.screen = pygame.display.set_mode(size)
        GameManager.clock = pygame.time.Clock()

        self.update()

        running = True
        while running:
            GameManager.clock.tick()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            GameManager.time_elapsed += GameManager.clock.get_time()
            if GameManager.time_elapsed < 1000 / GameManager.tps:
                continue
            GameManager.screen.fill((255, 255, 255))

            for i in GameManager.all_Objects:
                i.tick()
            for i in GameManager.all_Sprites:
                i.draw()
            pygame.display.flip()
            GameManager.time_elapsed = 0
            self.update()


    def update(self):
        for i in GameManager.toAdd:
            GameManager.all_Sprites.add(i.sprite)
            GameManager.all_Hitboxes.add(i.hitbox)
            GameManager.all_Objects.add(i)
        for i in GameManager.toRemove:
            if i in GameManager.all_Objects:
                i.delete()
