import pygame
import os
import random
from pygame import mixer
pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 900, 700
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Invaders of Space 2")

# ICON
icon = pygame.image.load(os.path.join("assets", "icon.png"))
pygame.display.set_icon(icon)

# ESSENTIALS
lives = 8
score = 0
keys = pygame.key.get_pressed()
won = False
lost = False

# MUSIC AND SOUND EFFECTS
mixer.music.load(os.path.join("assets", "gamemusic.mp3"))
mixer.music.play(-1)
hit_sound = mixer.Sound(os.path.join("assets", "laserSound.mp3"))

# SPECIAL CHARACTER
specialCharacter = pygame.image.load(os.path.join("assets", "special_character.png"))

# BACKGROUND
BG = pygame.image.load(os.path.join("assets", "background.png"))

# BULLETS
player_bullet = pygame.image.load(os.path.join("assets", "player_bullet.png"))
enemy_bullet = pygame.image.load(os.path.join("assets", "enemy_laser.png"))

# ENEMIES
enemy_one = pygame.image.load(os.path.join("assets", "enemy_one.png"))
enemy_two = pygame.image.load(os.path.join("assets", "enemy_two.png"))
enemy_three = pygame.image.load(os.path.join("assets", "enemy_three.png"))
enemySpecialImg = pygame.image.load(os.path.join("assets", "special_character.png"))

# PLAYER
main_character = pygame.image.load(os.path.join("assets", "main_character.png"))


# BULLET CLASS
class Bullet:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, playerY_change):
        self.y -= playerY_change

    def off_screen(self, height):
        return not self.y <= height and self.y >= 0

    def collision(self, obj):
        return collide(obj, self)


# SHIP CLASS
class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.bullet_img = None
        self.bullets = []
        self.cooldown_counter = 0

    def cooldown(self):
        if self.cooldown_counter >= self.COOLDOWN:
            self.cooldown_counter = 0
        elif self.cooldown_counter > 0:
            self.cooldown_counter += 0.5

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for bullet in self.bullets:
            bullet.draw(window)

    def shoot(self):
        if self.cooldown_counter == 0:
            bullet = Bullet(self.x, self.y, self.bullet_img)
            self.bullets.append(bullet)
            self.cooldown_counter = 1

    def move_bullets(self, laserY_change, obj):
        self.cooldown()
        for bullet in self.bullets:
            bullet.move(-laserY_change)
            if bullet.off_screen(HEIGHT):
                self.bullets.remove(bullet)
            elif bullet.collision(obj):
                self.bullets.remove(bullet)


# ENEMY CLASS
class Enemy(Ship):
    Color_map = {"gray": (enemy_one, enemy_bullet), "navy": (enemy_two, enemy_bullet), "blue": (enemy_three, enemy_bullet)}

    def __init__(self, x, y, color):
        super().__init__(x, y)
        self.ship_img, self.bullet_img = self.Color_map[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, enemyY_change):
        self.y += enemyY_change

    def move_bullets(self, enemy_laser_change, obj):
        self.cooldown()
        for bullet in self.bullets:
            bullet.move(-enemy_laser_change)
            if bullet.off_screen(HEIGHT):
                self.bullets.remove(bullet)
            elif bullet.collision(obj):
                hit_sound.play()
                obj.health -= 10
                self.bullets.remove(bullet)


# SPECIAL CHARACTER CLASS
class Special(Ship):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.bullet_img = enemy_bullet
        self.ship_img = enemySpecialImg
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, enemySpecialX_change, enemySpecialY_change):
        self.x += enemySpecialX_change

    def move_bullets(self, enemy_laser_change, obj):
        self.cooldown()
        for bullet in self.bullets:
            bullet.move(-enemy_laser_change)
            if bullet.off_screen(HEIGHT):
                self.bullets.remove(bullet)
            elif bullet.collision(obj):
                hit_sound.play()
                self.bullets.remove(bullet)

    def collision(self, obj):
        return collide(obj, self)


class Player(Ship):
    def __init__(self, x, y, max_health=100):
        super().__init__(x, y)
        self.ship_img = main_character
        self.bullet_img = player_bullet
        self.max_health = max_health
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move_bullets(self, laserY_change, objs):
        self.cooldown()
        for bullet in self.bullets:
            bullet.move(laserY_change)
            if bullet.off_screen(HEIGHT):
                self.bullets.remove(bullet)
            else:
                for obj in objs:
                    if bullet.collision(obj):
                        hit_sound.play()
                        objs.remove(obj)
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)

    def special_bullets(self, laserY_change, obj):
        self.cooldown()
        for bullet in self.bullets:
            bullet.move(laserY_change)
            if bullet.off_screen(HEIGHT):
                self.bullets.remove(bullet)
            elif bullet.collision(obj):
                hit_sound.play()
                obj.y = random.randint(-192, -128)
                self.bullets.remove(bullet)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        global lives
        global keys
        global lost
        global won
        pygame.draw.rect(window, (0, 31, 255), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 216, 255), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))
        if self.ship_img.get_width() * (self.health/self.max_health) == 0:
            lives -= lives
        if won:
            pygame.draw.rect(window, (0, 216, 255), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health / self.max_health), 10))


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (int(offset_x), int(offset_y)))


def main():
    FPS = 60
    clock = pygame.time.Clock()
    playerX_change = 7.8
    playerY_change = 7.8
    global lives
    global lost
    global won

    laserY_change = 5
    enemyBulletChange = 9

    enemies = []
    wave_length = 5
    enemyY_change = 1.5

    enemySpecialX_change = 4
    enemySpecialY_change = 64

    level = 0
    player = Player(412, 636)
    special = Special(0, -64)
    attribution = pygame.font.SysFont("comicsans", 40)
    main_font = pygame.font.SysFont("comicsans", 50)
    gameover_font = pygame.font.SysFont("comicsans", 70)
    play_again_font = pygame.font.SysFont("comicsans", 60)
    author_font = pygame.font.SysFont("comicsans", 60)
    congrats_font = pygame.font.SysFont("comicsans", 95)
    running = True

    def redraw_window():
        WIN.blit(BG, (0, 0))
        for enemy in enemies:
            enemy.draw(WIN)
        if lost:
            play_again_text = play_again_font.render("Press P to play again", True, (255, 255, 255))
            WIN.blit(play_again_text, (WIDTH / 2 - play_again_text.get_width() / 2, 399))
            lost_text = gameover_font.render("GAME OVER", True, (255, 255, 255))
            WIN.blit(lost_text, (WIDTH / 2 - lost_text.get_width() / 2, 340))
        if won:
            attribution_text = attribution.render("Icons made by Freepik and icongeek26 from www.flaticon.com", True, (255, 255, 255))
            WIN.blit(attribution_text, (WIDTH / 2 - attribution_text.get_width() / 2, 600))
            play_again_text = play_again_font.render("Press P to play again", True, (255, 255, 255))
            WIN.blit(play_again_text, (WIDTH / 2 - play_again_text.get_width() / 2, 399))
            author_text = author_font.render("Game made by frytat", True, (255, 255, 255))
            WIN.blit(author_text, (WIDTH / 2 - author_text.get_width() / 2, 30))
            congrats_text = congrats_font.render("Congratulations!", True, (255, 255, 255))
            WIN.blit(congrats_text, (WIDTH / 2 - congrats_text.get_width() / 2, 315))
            music_text = author_font.render("Music: snayk - growing on me", True, (255, 255, 255))
            WIN.blit(music_text, (WIDTH / 2 - music_text.get_width() / 2, 500))
        lives_label = main_font.render(f"Lives: {lives}", True, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", True, (255, 255, 255))
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        player.draw(WIN)
        special.draw(WIN)
        pygame.display.update()

    while running:
        clock.tick(FPS)
        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1600, -200), random.choice(["gray", "navy", "blue"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        if level >= 3:
            enemyY_change = 1.7

        special.move(enemySpecialX_change, enemySpecialY_change)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            player.shoot()
        if keys[pygame.K_w] and not keys[pygame.K_UP]:
            player.y -= playerY_change
        if keys[pygame.K_a] and not keys[pygame.K_LEFT]:
            player.x -= playerX_change
        if keys[pygame.K_s] and not keys[pygame.K_DOWN]:
            player.y += playerY_change
        if keys[pygame.K_d] and not keys[pygame.K_RIGHT]:
            player.x += playerX_change
        if keys[pygame.K_UP] and not keys[pygame.K_w]:
            player.y -= playerY_change
        if keys[pygame.K_LEFT] and not keys[pygame.K_a]:
            player.x -= playerX_change
        if keys[pygame.K_DOWN] and not keys[pygame.K_s]:
            player.y += playerY_change
        if keys[pygame.K_RIGHT] and not keys[pygame.K_d]:
            player.x += playerX_change
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemyY_change)
            enemy.move_bullets(enemyBulletChange, player)
            if enemy.y >= 740:
                lives -= 1
                enemies.remove(enemy)
            if lives <= 0:
                lives = 0
                lost = True
            if collide(enemy, player):
                hit_sound.play()
                lives -= 1
                enemy.y = random.randrange(-1400, 100)
            if random.randrange(0, 480) == 1:
                enemy.shoot()
            if lost:
                enemy.y = -2000
                laserY_change = 0
                enemyY_change = 0
                enemyBulletChange = 0
                enemySpecialY_change = 0
                enemySpecialX_change = 0
                special.y = -1000
                player.y = -84
                if keys[pygame.K_p]:
                    lost = False
                    lives += 8
                    main()
            if level >= 6:
                won = True
                enemy.y = -2000
                laserY_change = 0
                enemyY_change = 0
                enemyBulletChange = 0
                enemySpecialY_change = 0
                enemySpecialX_change = 0
                special.y = -1000
                player.y = -84
                if keys[pygame.K_p]:
                    won = False
                    lives += 8 - lives
                    main()

        player.move_bullets(laserY_change, enemies)

        special.move_bullets(enemyBulletChange, player)
        player.special_bullets(laserY_change, special)

        if special.x <= 0:
            enemySpecialX_change = 4
            special.y += enemySpecialY_change
        if special.x >= 836:
            enemySpecialX_change = -4
            special.y += enemySpecialY_change
        if collide(special, player):
            hit_sound.play()
            lives -= 1
            special.y = random.randrange(-192, -128)
        if special.y >= 750:
            lives -= 1
            special.y = random.randrange(-192, -128)
        if random.randrange(0, 480) == 1:
            special.shoot()

        if player.x <= 0:
            player.x = 0
        if player.x >= 836:
            player.x = 836
        if player.y >= 636:
            player.y = 636
        if player.y <= -84:
            player.y = -84

        redraw_window()

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 60)
    instruction_font = pygame.font.SysFont("comicsans", 50)
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title_text = title_font.render("Welcome to Invaders of Space 2!", True, (255, 255, 255))
        WIN.blit(title_text, (WIDTH / 2 - title_text.get_width() / 2, 300))
        instruction_text = instruction_font.render("Click anywhere on the screen to start.", True, (255, 255, 255))
        WIN.blit(instruction_text, (WIDTH / 2 - instruction_text.get_width() / 2, 500))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

main_menu()
