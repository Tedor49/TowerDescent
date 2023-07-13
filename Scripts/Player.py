from Scripts.Weapons import *
from Scripts.Attacks import *
from Scripts.AnimatedSprites import *
from Scripts.TestObjects import Ground


class Player(InteractableObject, Damageable, Persistent):
    sprites = [pygame.image.load("Sprites/playernew.png"), pygame.transform.flip(pygame.image.load("Sprites/playernew.png"), True, False)]
    hp = 10000
    coyote = 0
    x_speed = 1
    jump_height = 1
    prev_jump_pressed = False

    def __init__(self, x, y, sprite, hitbox, dx=0, dy=0, g=0.002):
        InteractableObject.__init__(self, x, y, sprite, hitbox, dx, dy, g)
        self.hitbox.ray_quality = 2
        self.weapon = Weapon(self, FistKit, downtime=350)
        self.base = self.weapon

        self.gui = [WeaponGUI(self)]

    def tick(self):
        if self.hp == 0:
            GameManager.toRemove.append(self)
            return

        keys = pygame.key.get_pressed()
        if pygame.mouse.get_pressed()[0]:
            x, y = pygame.mouse.get_pos()
            self.weapon.attack(x, y)
        if keys[pygame.K_w] and not self.prev_jump_pressed and self.coyote > 0:
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

        for i in self.hitbox.check_intersections(movement):
            if type(i.parent) == Ground:
                movement, dx_mul, dy_mul = i.modify_movement(movement, self.hitbox, mode="slide")
                if dy_mul == 0:
                    self.coyote = 100
                self.dx *= dx_mul
                self.dy *= dy_mul
            if type(i.parent) == Door:
                i.parent.use()
                movement = (movement[0], (self.x, self.y))
                if i.parent.type=='up':
                    movement = (movement[0], (self.x, self.y-30))
        self.x = movement[1][0]
        self.y = movement[1][1]

    def change_weapon(self, new_weapon):
        GameManager.toRemove.append(self.weapon)
        self.weapon = new_weapon
        new_weapon.parent = self
        new_weapon.ammo = random.randint(5, 9)

    def add_to_manager(self):
        GameManager.all_Objects.add(self)
        for i in self.gui:
            GameManager.all_Sprites.add(i)
        if self.weapon:
            self.weapon.add_to_manager()
        if self.hitbox:
            GameManager.all_Hitboxes.add(self.hitbox)
        if self.sprite:
            GameManager.all_Sprites.add(self.sprite)


class WeaponGUI(InteractableObject, Persistent, Sprite):
    def __init__(self, parent):
        InteractableObject.__init__(self, 760, 520, Sprite("Sprites/selectedWeapon.png"), None)
        self.parent = parent
        self.z = 10
        self.font = pygame.font.Font('Sprites/vinque rg.otf', 70)

    def draw(self):
        self.sprite.draw()
        self.parent.weapon.guiIcon.x = 35
        self.parent.weapon.guiIcon.y = 50
        self.parent.weapon.guiIcon.parent = self
        self.parent.weapon.guiIcon.draw()

        if self.parent.weapon.ammo >= 0:
            amount = str(self.parent.weapon.ammo)
        else:
            amount = "∞"

        ammo = self.font.render(amount, True, (255, 215, 0))
        textRect = ammo.get_rect()
        textRect.center = (self.getx() + 145, self.gety() + 135)
        GameManager.screen.blit(ammo, textRect)
