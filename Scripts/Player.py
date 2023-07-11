from Scripts.Weapons import *
from Scripts.Attacks import *
from Scripts.AnimatedSprites import *
from Scripts.TestObjects import Ground


class Player(InteractableObject, Damageable):
    sprites = [pygame.image.load("Sprites/playernew.png"), pygame.transform.flip(pygame.image.load("Sprites/playernew.png"), True, False)]
    hp = 10000
    coyote = 0
    x_speed = 1
    jump_height = 1
    prev_jump_pressed = False

    def __init__(self, x, y, sprite, hitbox, dx=0, dy=0, g=0.002):
        super().__init__(x, y, sprite, hitbox, dx, dy, g)
        self.hitbox.ray_quality = 2
        self.weapon = Weapon(self, Fist, AnimatedFist(), downtime=350)
        self.base = self.weapon

    def tick(self):
        if self.hp == 0:
            GameManager.toRemove.append(self)
            return

        keys = pygame.key.get_pressed()
        print(GameManager.currentRoom.id)
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
                if i.parent.use():
                    movement = (movement[0], (self.x, self.y))
                    break

        self.x = movement[1][0]
        self.y = movement[1][1]

    def change_weapon(self, new_weapon):
        GameManager.toRemove.append(self.weapon)
        self.weapon = new_weapon
        new_weapon.parent = self
        new_weapon.ammo = random.randint(5, 10)

    def add_to_manager(self):
        GameManager.all_Objects.add(self)
        self.weapon.add_to_manager()
        if self.hitbox:
            GameManager.all_Hitboxes.add(self.hitbox)
        if self.sprite:
            GameManager.all_Sprites.add(self.sprite)
