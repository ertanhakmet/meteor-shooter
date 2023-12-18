import pygame as py
from sys import exit
import random

# PYGAME SETUP
py.init()
py.mixer.init()
py.font.init()

# VARIABLES
game_font = py.font.Font('Assets/Font/pixelade.TTF', 50)

# colours
red = (255, 0, 0)
white = (255, 255, 255)
yellow = (255, 255, 0)
green = (0, 255, 0)

score = 0
game_over = False

# screen
screen_width = 800
screen_height = 600
fps = 100
bg_music = py.mixer.Sound('Assets/Sound/music_bg.mp3')
bg_music.set_volume(0.3)
bg_music.play(-1)
icon = py.image.load('Assets/Graphics/icon.png')
screen_img = py.image.load('Assets/Graphics/space_bg.jpg')
screen = py.display.set_mode((screen_width, screen_height))
py.display.set_caption("Meteor Shooter")
py.display.set_icon(icon)
# player
player_vel = 5
player_width, player_height = 60, 90
health = 10
# lasers
laser_vel = 6
laser_sound = py.mixer.Sound('Assets/Sound/laser.mp3')
laser_sound.set_volume(0.3)
# meteor
meteor_width, meteor_height = 97, 97
meteor_vel = 2
meteor_timer = 0
meteor_number = 6
explosion_sound = py.mixer.Sound('Assets/Sound/explosion.mp3')
explosion_sound.set_volume(0.8)


# TEXT
class Text(py.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # score
        self.x_offset = 10
        self.y_offset = 5

    def display_score(self):
        self.score_surf = game_font.render(f"Score: {score}", True, white)
        self.score_rect = self.score_surf.get_rect()
        self.score_rect.topleft = (self.x_offset, self.y_offset)
        screen.blit(self.score_surf, self.score_rect.topleft)

    def update(self):
        self.display_score()


# LASER
class Laser(py.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.laser_img = py.Surface((5, 15))
        self.laser_img.fill(red)
        self.rect = self.laser_img.get_rect(center=(x, y))

    def move(self):
        self.rect.y -= laser_vel
        if self.rect.bottom < 30:
            self.kill()

    def update(self):
        self.move()
        screen.blit(self.laser_img, self.rect)


# PLAYER CLASS
class Player(py.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # player
        self.player_img = py.transform.scale(py.image.load('Assets/Graphics/player.png'),
                                             (player_width, player_height)).convert_alpha()
        self.rect = self.player_img.get_rect(center=(screen_width / 2, 500))
        self.firing = False

    def player_input(self):
        keys = py.key.get_pressed()
        if keys[py.K_a] and (self.rect.left - player_vel >= 0):  # left
            self.rect.x -= player_vel
        if keys[py.K_d] and (self.rect.right + player_vel <= screen_width):  # right
            self.rect.x += player_vel
        if keys[py.K_w] and (self.rect.top - player_vel >= 0):  # up
            self.rect.y -= player_vel
        if keys[py.K_s] and (self.rect.bottom - player_vel <= screen_height):  # down
            self.rect.y += player_vel
        # space button
        if keys[py.K_SPACE] and not self.firing:  # space
            laser = Laser(self.rect.centerx, self.rect.top)
            laser_group.add(laser)
            laser_sound.play()
            self.firing = True
        if not keys[py.K_SPACE]:
            player.sprite.firing = False

    def update(self):
        self.player_input()
        screen.blit(self.player_img, self.rect)


# METEOR CLASS
class Meteors(py.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.meteor_img = py.transform.scale(py.image.load('Assets/Graphics/meteor.png'), (meteor_width, meteor_height))
        self.rect = self.meteor_img.get_rect()
        self.rect.x = random.randint(0, screen_width - meteor_width)
        self.rect.y = random.randint(-800, -10)

    def move(self, vel):
        self.rect.y += vel

    def update(self):
        self.move(meteor_vel)
        screen.blit(self.meteor_img, self.rect)


# HEALTH BAR
class HealthBar(py.sprite.Sprite):
    def __init__(self, x, y, width, height, health):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.health = health
        self.max_health = health
        self.colour = green

    def update(self, health):
        self.health = health
        if self.health < self.max_health / 2:
            self.colour = yellow
        if self.health < self.max_health / 4:
            self.colour = red
        py.draw.rect(screen, self.colour,
                     (self.x, self.y, self.width * (self.health / self.max_health), self.height))

    def draw(self, surface):
        # Draw the outline of the health bar
        py.draw.rect(surface, white, (self.x, self.y, self.width, self.height), 2)

        # Draw the filled in portion of the health bar
        fill_width = int((self.health / self.max_health) * (self.width - 4))
        fill_rect = py.Rect(self.x + 2, self.y + 2, fill_width, self.height - 4)
        py.draw.rect(surface, self.colour, fill_rect)

        # Draw the text label for the health bar
        health_font = py.font.Font('Assets/Font/pixelade.TTF', 25)
        text = health_font.render(f"Health: {self.health}/{self.max_health}", True, white)
        text_rect = text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        surface.blit(text, text_rect)


# Restarting game
def restart_game():
    global score, health, game_over, meteor_vel, meteor_timer, meteor_number

    score = 0
    health = 10
    game_over = False
    meteor_vel = 2
    meteor_timer = 0
    meteor_number = 5

    # Reset player
    player.sprite.rect.center = (screen_width / 2, 500)

    # Remove all meteors and lasers
    meteor_group.empty()
    laser_group.empty()

    # Create new meteors
    spawn_meteors()

    # Make health bar green and update its values
    health_bar.colour = green
    health_bar.max_health = health
    health_bar.health = health


def spawn_meteors():
    for i in range(meteor_number):
        meteor = Meteors()

        while py.sprite.spritecollide(meteor, meteor_group, False):
            meteor.rect.x = random.randint(0, screen_width - meteor_width)
            meteor.rect.y = random.randint(-800, -30)

        meteor_group.add(meteor)


# GROUPS
# player
player = py.sprite.GroupSingle()
player.add(Player())

# meteor
meteor_group = py.sprite.Group()

# health bar
health_bar = HealthBar(640, 15, 150, 30, health)

spawn_meteors()

# laser
laser_group = py.sprite.Group()

# text
text_group = py.sprite.Group()
text_group.add(Text())

clock = py.time.Clock()
game_active = True

while True:
    py.display.update()
    clock.tick(fps)

    for event in py.event.get():
        if event.type == py.QUIT:
            py.quit
            exit()

    delta_time = clock.tick(fps) / 250.0
    meteor_timer += delta_time

    if meteor_timer > 2.0:
        meteor_timer = 0
        new_meteor = Meteors()
        meteor_group.add(new_meteor)

    # update screen, meteor, player, laser and text
    screen.blit(screen_img, (0, 0))
    meteor_group.update()
    player.update()
    laser_group.update()
    health_bar.draw(screen)
    text_group.update()

    # collision for player and laser
    player_meteor_collisions = py.sprite.groupcollide(player, meteor_group, False, True)
    for player_sprite, meteors in player_meteor_collisions.items():
        score += 1
        health -= 1
        health_bar.update(health)
        explosion_sound.play()
        if health <= 0:
            game_active = False

    laser_meteor_collisions = py.sprite.groupcollide(laser_group, meteor_group, True, True)
    for laser, meteors in laser_meteor_collisions.items():
        score += 1
        explosion_sound.play()

    # Check if a meteor passed the player and went off-screen
    for meteor in meteor_group:
        if meteor.rect.top > screen_height:
            health -= 1
            health_bar.update(health)
            meteor.kill()
            if health <= 0:
                game_active = False

    if not game_active:
        # game over text
        game_over_text = game_font.render("GAME OVER", True, white)
        game_over_rect = game_over_text.get_rect(center=(screen_width / 2, screen_height / 2 - 80))
        screen.blit(game_over_text, game_over_rect)
        # restarts in 5 seconds
        restart_text = game_font.render("Restarts in 5 seconds...", True, yellow)
        restart_text_rect = restart_text.get_rect(center=(screen_width / 2, screen_height / 2 + 10))
        screen.blit(restart_text, restart_text_rect)

        py.display.update()
        py.time.wait(5000)
        restart_game()
        game_active = True
