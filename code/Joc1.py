import pygame
from os.path import join
from random import randint, uniform

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('poze', 'player.png')).convert_alpha()
        self.rect = self.image.get_rect(center = (window_width/2, window_height/2))
        self.direction = pygame.Vector2()
        self.speed = 300

        #cooldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_time = 400  # 0.4 secunde

        #mask
        self.mask = pygame.mask.from_surface(self.image)

    def laser_time (self):
        if not self.can_shoot :
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_time :
                self.can_shoot = True

    def update (self, dt):
        global space_pressed
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt

        if space_pressed and self.can_shoot:
            Laser((all_sprites,laser_sprites), laser_surf,self.rect.midtop)
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()
            space_pressed = False

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf #pentru a nu importa imaginea de 20 ori
        self.rect =self.image.get_rect(center = (randint(0, window_width), randint(0, window_height)))

class Laser(pygame.sprite.Sprite):
    def __init__(self, groups, surf, pos):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(midbottom=pos)
    def update (self, dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, groups, surf, pos):
        super().__init__(groups)
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_rect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000
        self.direction = pygame.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(200, 300)
        self.rotation_speed = randint(40, 80)
        self.rotation = 0

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_rect(center=self.rect.center)

class AnimatedExplosion (pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.image = frames [0]
        self.rect = self.image.get_rect(center = pos)
        self.frames = frames
        self.index_frame = 0

    def update (self, dt):
        self.index_frame += 20 * dt
        if self.index_frame < len(self.frames) :
            self.image = self.frames[int(self.index_frame)]
        else:
            self.kill()

def collisions ():
    global running
    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites :
        running = False
    for laser in laser_sprites :
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_sprites:
            laser.kill()
            AnimatedExplosion( explosion_frames, laser.rect.midtop, all_sprites)
            explosion_sound.play()

def display_score():
    current_time = pygame.time.get_ticks() // 100
    text_surf = font.render(str(current_time), True, (240,240,240))
    text_rect = text_surf.get_rect(midbottom = (window_width / 2, window_height - 50))
    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(display_surface, (240,240,240), text_rect.inflate(20,10).move(0,-8), 5, 10)

#general setup
pygame.init()
window_width, window_height = 800, 600
display_surface = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("My First Game")
running = True
clock = pygame.time.Clock()

#imports
star_surf = pygame.image.load(join('poze', 'star.png')).convert_alpha()
meteor_surf = pygame.image.load(join('poze', 'meteor.png')).convert_alpha()
laser_surf = pygame.image.load(join('poze', 'laser.png')).convert_alpha()
explosion_frames = [pygame.image.load(join('poze', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]
font = pygame.font.Font(join('poze', 'Oxanium-Bold.ttf'), 40)
laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
game_music = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_music.set_volume(0.4)
game_music.play(loops= -1)

#Sprites
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
for i in range (20) :
    Star (all_sprites, star_surf)
player = Player (all_sprites)

#Custom events
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)
space_pressed = False

# Main game loop
while running:
    dt = clock.tick() / 1000
    #event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                space_pressed = True
        if event.type == meteor_event:
            x, y = randint(0, window_width), randint(-200, -100) # negative ca sa iasa din joc
            Meteor((all_sprites, meteor_sprites), meteor_surf, (x, y))
    # update
    all_sprites.update(dt)
    collisions()

    # draw the game
    display_surface.fill('#3a2e3f')
    display_score()
    all_sprites.draw(display_surface)
    pygame.display.update()

pygame.quit()

