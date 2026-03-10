import pygame
from os.path import join
from random import randint, uniform, choice


class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('poze', 'player.png')).convert_alpha()
        self.rect = self.image.get_rect(center=(window_width / 2, window_height / 2))
        self.direction = pygame.Vector2()
        self.speed = 300
        self.pos = pygame.Vector2(self.rect.center)

        # cooldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_time = 400  # 0.4 secunde

        # mask
        self.mask = pygame.mask.from_surface(self.image)

    def laser_time(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_time:
                self.can_shoot = True

    def update(self, dt):
        global space_pressed

        self.laser_time()

        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])

        if self.direction.length() != 0:
            self.direction = self.direction.normalize()

        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos

        # playerul in ecran
        self.rect.clamp_ip(display_surface.get_rect())
        self.pos = pygame.Vector2(self.rect.center)

        if space_pressed and self.can_shoot:
            Laser((all_sprites, laser_sprites), laser_surf, self.rect.midtop)
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()
            space_pressed = False


class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(
            center=(randint(0, window_width), randint(0, window_height))
        )


class Laser(pygame.sprite.Sprite):
    def __init__(self, groups, surf, pos):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(midbottom=pos)
        self.pos = pygame.Vector2(self.rect.center)

    def update(self, dt):
        self.pos.y -= 400 * dt
        self.rect.center = self.pos

        if self.rect.bottom < 0:
            self.kill()


class Meteor(pygame.sprite.Sprite):
    def __init__(self, groups, surf, pos, scale):
        super().__init__(groups)

        # meteoriti de diferite marimi
        width = int(surf.get_width() * scale)
        height = int(surf.get_height() * scale)
        scaled_surf = pygame.transform.smoothscale(surf, (width, height))

        self.original_surf = scaled_surf
        self.image = self.original_surf
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(self.rect.center)

        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000
        self.direction = pygame.Vector2(uniform(-0.5, 0.5), 1)

        if self.direction.length() != 0:
            self.direction = self.direction.normalize()

    
        # meteoritii mici sunt mai rapizi
        if scale <= 0.8:
            self.speed = randint(260, 340)
        elif scale <= 1.1:
            self.speed = randint(220, 300)
        else:
            self.speed = randint(180, 250)

        self.rotation_speed = randint(40, 80)
        self.rotation = 0

        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos

        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()

        self.rotation += self.rotation_speed * dt
        center_before = self.rect.center
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_rect(center=center_before)
        self.mask = pygame.mask.from_surface(self.image)


class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.image = frames[0]
        self.rect = self.image.get_rect(center=pos)
        self.frames = frames
        self.index_frame = 0

    def update(self, dt):
        self.index_frame += 20 * dt
        if self.index_frame < len(self.frames):
            self.image = self.frames[int(self.index_frame)]
        else:
            self.kill()


def collisions():
    global running, lives, game_over, final_score

    # coliziune player - meteoriti
    collision_sprites = pygame.sprite.spritecollide(
        player, meteor_sprites, True, pygame.sprite.collide_mask
    )

    if collision_sprites:
        lives -= 1

        for meteor in collision_sprites:
            AnimatedExplosion(explosion_frames, meteor.rect.center, all_sprites)
            explosion_sound.play()

        if lives <= 0:
            final_score = pygame.time.get_ticks() // 100
            game_over = True

    # coliziune laser - meteoriti
    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_sprites:
            laser.kill()
            for meteor in collided_sprites:
                AnimatedExplosion(explosion_frames, meteor.rect.center, all_sprites)
            explosion_sound.play()


def display_score():
    current_time = pygame.time.get_ticks() // 100
    text_surf = font.render(str(current_time), True, (240, 240, 240))
    text_rect = text_surf.get_rect(midbottom=(window_width / 2, window_height - 50))
    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(
        display_surface,
        (240, 240, 240),
        text_rect.inflate(20, 10).move(0, -8),
        5,
        10
    )


def display_lives():
    lives_surf = font.render(f"Vieti: {lives}", True, (240, 240, 240))
    lives_rect = lives_surf.get_rect(topleft=(20, 20))
    display_surface.blit(lives_surf, lives_rect)


def display_game_over():
    display_surface.fill("#1C062F")

    game_over_surf = game_over_font.render("GAME OVER", True, (240, 240, 240))
    game_over_rect = game_over_surf.get_rect(center=(window_width / 2, window_height / 2 - 60))
    display_surface.blit(game_over_surf, game_over_rect)

    score_surf = font.render(f"Scor final: {final_score}", True, (240, 240, 240))
    score_rect = score_surf.get_rect(center=(window_width / 2, window_height / 2 + 10))
    display_surface.blit(score_surf, score_rect)

    info_surf = small_font.render("Inchide fereastra pentru a iesi", True, (200, 200, 200))
    info_rect = info_surf.get_rect(center=(window_width / 2, window_height / 2 + 70))
    display_surface.blit(info_surf, info_rect)

    pygame.display.update()


# general setup
pygame.init()
pygame.mixer.init()

window_width, window_height = 800, 600
display_surface = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("My First Game")
running = True
game_over = False
clock = pygame.time.Clock()

lives = 3
final_score = 0

# imports
star_surf = pygame.image.load(join('poze', 'star.png')).convert_alpha()
meteor_surf = pygame.image.load(join('poze', 'meteorit.png')).convert_alpha()
laser_surf = pygame.image.load(join('poze', 'laser_toxic.png')).convert_alpha()
explosion_frames = [
    pygame.image.load(join('poze', 'explosion', f'{i}.png')).convert_alpha()
    for i in range(21)
]

font = pygame.font.Font(join('poze', 'Oxanium-Bold.ttf'), 40)
game_over_font = pygame.font.Font(join('poze', 'Oxanium-Bold.ttf'), 70)
small_font = pygame.font.Font(join('poze', 'Oxanium-Bold.ttf'), 24)

laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
laser_sound.set_volume(0.5)

explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))

game_music = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_music.set_volume(0.4)
game_music.play(loops=-1)

# Sprites
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()

for i in range(20):
    Star(all_sprites, star_surf)

player = Player(all_sprites)

# Custom events
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)
space_pressed = False


meteor_scales = [0.6, 0.8, 1.0, 1.3, 1.6]

# Main game loop
while running:
    dt = clock.tick(60) / 1000

    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if not game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    space_pressed = True

            if event.type == meteor_event:
                x, y = randint(0, window_width), randint(-200, -100)
                scale = choice(meteor_scales)
                Meteor((all_sprites, meteor_sprites), meteor_surf, (x, y), scale)

    if not game_over:
        # update
        all_sprites.update(dt)
        collisions()

        # draw the game
        display_surface.fill("#320A60")
        display_score()
        display_lives()
        all_sprites.draw(display_surface)
        pygame.display.update()
    else:
        display_game_over()

pygame.quit()