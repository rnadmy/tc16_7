import pygame as pg
import random as ran

# Inisialisasi pygame
pg.init()
pg.mixer.init()

# Membuat jendela game
WIDTH, HEIGHT = 800, 600
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption('Space Shooter')

# Tambahkan image sebagai background
image = pg.image.load('space.png')
image = pg.transform.scale(image, (800, 600))

# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Kecepatan Game
FPS = 60
clock = pg.time.Clock()

# Menyimpan highest score dalam variable
highest_score = 0

# Memasukan suara background game
pg.mixer.music.load('bg.wav')
pg.mixer.music.set_volume(0.5)
pg.mixer.music.play(-1)

# Memasukan sound efek ship hit rock
hit_sound = pg.mixer.Sound('game_over.wav')
hit_sound.set_volume(0.5)

# Class untuk Player
class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.image.load('ship.png')
        self.image = pg.transform.scale(self.image, (50, 50))
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 50)
        self.speed = 5

    def update(self):
        keys = pg.key.get_pressed()
        # kondisi jika kita gerakan objek ke atas, bawah, kiri, dan kanan
        if keys[pg.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pg.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if keys[pg.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pg.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed
        
    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)

# Class untuk Bullet
class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.Surface((5, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:  
            self.kill()

# Class untuk Enemies
class Enemies(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.image.load('stone.png')
        self.image = pg.transform.scale(self.image, (50, 50))
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = ran.randint(0, WIDTH - 50)
        self.rect.y = ran.randint(-100, -50)
        self.speed = ran.randint(2, 6)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.x = ran.randint(0, WIDTH - 75)
            self.rect.y = ran.randint(-100, -50)
            self.speed = ran.randint(2, 6)

# Membuat Function menampilkan text
def draw_text(text, font, color, x, y):
    screen_text = font.render(text, True, color)
    screen.blit(screen_text, (x, y))

# Membuat fungsi untuk tombol menu
def draw_button(text, x, y, w, h, inactive_color, active_color, action=None):
    mouse = pg.mouse.get_pos()
    click = pg.mouse.get_pressed()

    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pg.draw.rect(screen, active_color, (x, y, w, h))
        if click[0] == 1 and action is not None:
            action()
    else:
        pg.draw.rect(screen, inactive_color, (x, y, w, h))

    font = pg.font.SysFont(None, 40)
    text_surf = font.render(text, True, WHITE)
    screen.blit(text_surf, (x + (w / 5), y + (h / 5)))

# Membuat function untuk memulai game
def start_game():
    global highest_score  # Mengakses global variable highest score

    # Inisialisasi sprite group
    global all_sprites, bullets  
    all_sprites = pg.sprite.Group()
    enemies = pg.sprite.Group()
    bullets = pg.sprite.Group()  

    # Membuat player
    player = Player()
    all_sprites.add(player)

    # Membuat enemies
    for i in range(5):  # ada 5 musuh di awal
        enemy = Enemies()
        all_sprites.add(enemy)
        enemies.add(enemy)

    # Membuat score dan waktu
    score = 0
    start = pg.time.get_ticks()
    level = 1

    # Loop game
    run = True
    game_over = False
    while run:
        clock.tick(FPS)

        # Menutup game jika tekan 'X'
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:  # Press space to shoot
                    player.shoot()

        # Logik naik level
        if score > 10 * level:
            level += 1
            for i in range(5):
                enemy = Enemies()
                enemy.speed = ran.randint(2 + level, 6 + level)
                all_sprites.add(enemy)
                enemies.add(enemy)

        # Logik game over
        if not game_over:
            # Update semua sprite
            all_sprites.update()

            # Mengecek apakah player hit enemies?
            hits = pg.sprite.spritecollide(player, enemies, False)
            if hits:
                hit_sound.play()
                game_over = True
                game_over_time = (pg.time.get_ticks() - start) // 100  # menghitung skor waktu bertahan hidup

                # Menambahkan logik highest score
                if game_over_time > highest_score:
                    highest_score = game_over_time

            # Mengecek tabrakan antara bullets dan enemies
            bullet_hits = pg.sprite.groupcollide(enemies, bullets, True, True)
            for hit in bullet_hits:
                score += 1  

            # Menghitung skor akhir
            score = (pg.time.get_ticks() - start) // 1000

        # Menampilkan background
        screen.blit(image, (0, 0))

        # Menggambar objek
        all_sprites.draw(screen)  # Menggambar semua sprite

        # Menampilkan score
        font = pg.font.SysFont(None, 30)
        text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(text, (10, 10))

        # Menampilkan level
        font = pg.font.SysFont(None, 30)
        text = font.render(f"Level: {level}", True, WHITE)
        screen.blit(text, (10, 10 + 20))

        # Menampilkan game over
        if game_over:
            over_text = font.render(f"Game Over! Your Best Score: {highest_score}", True, WHITE)
            screen.blit(over_text, (WIDTH // 2 - 150, HEIGHT // 2))

            # Menampilkan tombol restart game
            draw_button("Restart Game", WIDTH // 3, HEIGHT // 3 + 150, 250, 60, BLUE, RED, start_game)

        # Update tampilan layar
        pg.display.flip()

    pg.quit()

# Membuat Function menu utama
def main_menu():
    menu = True
    while menu:
        # Menampilkan background
        screen.blit(image, (0, 0))

        # Menampilkan judul Game
        font = pg.font.SysFont(None, 70)
        draw_text("Space Shooter", font, WHITE, WIDTH // 4, HEIGHT // 4)

        # Menampilkan tombol start
        draw_button("Start Game", WIDTH // 3, HEIGHT // 3, 200, 60, BLUE, RED, start_game)

        # Menutup game jika tekan 'X'
        for event in pg.event.get():
            if event.type == pg.QUIT:
                menu = False

        pg.display.update()
        clock.tick(15)

# Memulai program
if __name__ == '__main__':
    main_menu()
