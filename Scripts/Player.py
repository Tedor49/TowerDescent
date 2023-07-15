from Scripts.Weapons import *
from Scripts.AnimatedSprites import *
from Scripts.TestObjects import Ground


class Player(InteractableObject, Damageable, Persistent):
    """Class that represents Player"""
    sprites = [pygame.image.load("Sprites/playernew.png"),
               pygame.transform.flip(pygame.image.load("Sprites/playernew.png"), True, False)]
    hp = 100
    coyote = 0
    x_speed = 1
    jump_height = 1
    max_extra_jumps = 0
    extra_jumps = 0
    prev_jump_pressed = False
    active = True
    bullets_bounce = False
    sword_reflect = False
    only_fists = False
    colliding = True

    def __init__(self, x, y, sprite, hitbox, dx=0, dy=0, g=0.002):
        """
        The initialization method for Player
        :param x: x coordinate of the Player
        :param y: y coordinate of the Player
        :param sprite: Sprite of the Player
        :param hitbox: Hitbox of the Player
        :param dx: change on the x-axis
        :param dy: change on the y-axis
        :param g: acceleration of gravity
        """
        InteractableObject.__init__(self, x, y, sprite, hitbox, dx, dy, g)
        self.hitbox.ray_quality = 2
        self.weapon = Weapon(self, FistKit, downtime=350)
        self.base = self.weapon

        self.gui = [WeaponGUI(self), HealthGUI(self), MapGUI(self)]

    def tick(self):
        """Actions that Player do each tick"""
        keys = pygame.key.get_pressed()
        if not self.active:
            if keys[pygame.K_1] and isinstance(GameManager.current_room, InterDimensionalRoom):
                GameManager.current_room.power_ups[0][1].apply()
                GameManager.current_room.quit()
            elif keys[pygame.K_2] and isinstance(GameManager.current_room, InterDimensionalRoom):
                GameManager.current_room.power_ups[1][1].apply()
                GameManager.current_room.quit()
            elif keys[pygame.K_3] and isinstance(GameManager.current_room, InterDimensionalRoom):
                GameManager.current_room.power_ups[2][1].apply()
                GameManager.current_room.quit()
            return
        if self.hp <= 0:
            GameManager.to_remove.append(self)
            GameManager.to_add.append(InteractableObject(0, 0, AnimatedGameOver()))
            return

        keys = pygame.key.get_pressed()
        if pygame.mouse.get_pressed()[0]:
            x, y = pygame.mouse.get_pos()
            self.weapon.attack(x, y)

        if self.coyote > 0:
            self.extra_jumps = self.max_extra_jumps

        if self.colliding:
            if keys[pygame.K_w] and not self.prev_jump_pressed:
                if self.coyote > 0:
                    self.dy = -0.8 * self.jump_height
                    self.coyote = 0
                elif self.extra_jumps > 0:
                    self.extra_jumps -= 1
                    self.dy = -0.8 * self.jump_height
            else:
                self.dy += self.g * GameManager.time_elapsed

        if keys[pygame.K_w]:
            self.prev_jump_pressed = True
        else:
            self.prev_jump_pressed = False

        self.coyote -= GameManager.time_elapsed

        if (keys[pygame.K_d] - keys[pygame.K_a]) == -1:
            self.sprite.image = self.sprites[1]
        elif (keys[pygame.K_d] - keys[pygame.K_a]) == 1:
            self.sprite.image = self.sprites[0]

        movement = [[self.x, self.y],
                    [self.x + self.x_speed * (keys[pygame.K_d] - keys[pygame.K_a]) * GameManager.time_elapsed,
                     self.y + self.dy * GameManager.time_elapsed]]
        if self.colliding:
            for i in self.hitbox.check_intersections(movement):
                if type(i.parent) == Ground or (type(i.parent) == Door and i.parent.usable is False):
                    movement, dx_mul, dy_mul = i.modify_movement(movement, self.hitbox, mode="slide")
                    if dy_mul == 0:
                        self.coyote = 100
                    self.dx *= dx_mul
                    self.dy *= dy_mul
                elif type(i.parent) == Door and i.parent.usable:
                    i.parent.use()
                    movement = (movement[0], (self.x, self.y))
                    if i.parent.type == 'up':
                        movement = (movement[0], (self.x, self.y - 30))
                elif isinstance(i.parent, DeathPlane):
                    self.x = 440
                    self.y = 400
                    self.hp -= 5
                    return
            for i in self.hitbox.check_intersections():
                if type(i.parent) == Elevator:
                    if keys[pygame.K_w]:
                        i.parent.use()
        self.x = movement[1][0]
        self.y = movement[1][1]

        if self.y < -100:
            sys.exit()

    def change_weapon(self, new_weapon):
        """
        Method that occurs when player wants to change weapon
        :param new_weapon: new weapon
        """
        GameManager.to_remove.append(self.weapon)
        self.weapon = new_weapon
        new_weapon.parent = self
        new_weapon.ammo = random.randint(5, 9)

    def add_to_manager(self):
        """Method that adds Player instance in GameManager"""
        GameManager.all_Objects.add(self)
        for element_of_interface in self.gui:
            GameManager.all_Sprites.add(element_of_interface)
        if self.weapon:
            self.weapon.add_to_manager()
        if self.hitbox:
            GameManager.all_Hitboxes.add(self.hitbox)
        if self.sprite:
            GameManager.all_Sprites.add(self.sprite)

    def deactivate(self):
        """Method that deactivates Player"""
        self.active = False
        self.sprite.active = False
        self.weapon.sprite.active = False

    def activate(self):
        """Method that activates Player"""
        self.active = True
        self.sprite.active = True
        self.weapon.sprite.active = True


class WeaponGUI(Sprite, Persistent):
    """Class that provides Weapon GUI"""

    def __init__(self, parent):
        """
        The initialization method for weapon GUI
        :param parent: Owner of the GUI
        """
        Sprite.__init__(self, "Sprites/selectedWeapon.png", z=5)
        self.x = 760
        self.y = 520
        self.parent = parent
        self.z = 10
        self.font = pygame.font.Font('Sprites/vinque rg.otf', 70)

    def draw(self):
        """
        Method that draws weapons GUI
        :return: None
        """
        if not self.active:
            return

        Sprite.draw(self)
        self.parent.weapon.gui_icon.x = 35
        self.parent.weapon.gui_icon.y = 50
        self.parent.weapon.gui_icon.parent = self
        self.parent.weapon.gui_icon.draw()

        if self.parent.weapon.ammo >= 0:
            amount = str(self.parent.weapon.ammo)
        else:
            amount = "∞"

        ammo = self.font.render(amount, True, (0, 0, 0))
        text_position = ammo.get_rect()
        text_position.center = (self.x + 145, self.y + 135)
        GameManager.screen.blit(ammo, text_position)

    def get_x(self):
        """
        Method that returns x coordinate
        :return: x coordinate
        """
        return self.x

    def get_y(self):
        """
        Method that returns y coordinate
        :return: y coordinate
        """
        return self.y


class HealthGUI(Sprite, Persistent):
    """Class that provides Health GUI"""

    def __init__(self, parent):
        """
        The initialization method for health GUI
        :param parent: Owner of the GUI
        """
        Sprite.__init__(self, "Sprites/heart.png", z=5)
        self.baseImage = pygame.image.load("Sprites/heart.png")
        self.x = 50
        self.y = 50
        self.parent = parent
        self.z = 10
        self.time = 0
        self.font = pygame.font.Font('Sprites/vinque rg.otf', 20)

    def draw(self):
        """
        Method that draws health GUI
        :return: None
        """
        if not self.active:
            return

        self.time += GameManager.time_elapsed
        size_fraction = math.sin(10 * ((self.time / 200) % 5)) * math.e ** (4 * (1 - (self.time / 200 % 5))) / 100 + 0.9
        hp_fraction = (self.parent.hp + 100) / 200
        size_fraction *= hp_fraction

        base_size = self.baseImage.get_size()
        new_size = (base_size[0] * size_fraction, base_size[1] * size_fraction)
        self.image = pygame.transform.scale(self.baseImage, new_size)

        brown = (139, 69, 19)

        hp_fraction = 1 - hp_fraction
        self.image.fill(tuple([255 - int((255 - i) * hp_fraction) for i in brown]),
                        special_flags=pygame.BLEND_MULT)
        self.x = 75 - new_size[0] // 2
        self.y = 75 - new_size[1] // 2

        Sprite.draw(self)

        ammo = self.font.render(str(self.parent.hp), True, (255, 0, 0))
        text_position = ammo.get_rect()
        text_position.center = (self.x + 70, self.y + 80)
        GameManager.screen.blit(ammo, text_position)

    def get_x(self):
        """
        Method that returns x coordinate
        :return: x coordinate
        """
        return self.x

    def get_y(self):
        """
        Method that returns y coordinate
        :return: y coordinate
        """
        return self.y


class MapGUI(Sprite, Persistent):
    """Class that provides Map GUI"""

    def __init__(self, parent):
        """
        The initialization method for Map GUI
        :param parent: Owner of the GUI
        """
        self.parent = parent
        Sprite.__init__(self, "Sprites/hitbox.png", z=5)

    def draw(self):
        """
        Method that draws Map GUI
        :return: None
        """
        if not self.active:
            return

        pygame.draw.rect(GameManager.screen, (255, 255, 255), pygame.Rect(845, 0, 115, 110))
        pygame.draw.rect(GameManager.screen, (0, 0, 0), pygame.Rect(845, 0, 115, 110), 2)
        for y in range(7):
            for x in range(7):
                if GameManager.level.map[y][x] is not None:
                    if GameManager.current_room.id == GameManager.level.map[y][x]:
                        pygame.draw.rect(GameManager.screen, (255, 0, 0), pygame.Rect(855 + x * 15, 10 + y * 15,
                                                                                      15, 15))
                    elif GameManager.search_by_id(GameManager.level.map[y][x]).cleaned:
                        pygame.draw.rect(GameManager.screen, (55, 253, 18), pygame.Rect(855 + x * 15, 10 + y * 15,
                                                                                        15, 15))
                    pygame.draw.rect(GameManager.screen, (0, 0, 0), pygame.Rect(855 + x * 15, 10 + y * 15,
                                                                                15, 15), 2)
