import pygame
import random as rand

pygame.init()
pygame.mixer.init()

TICK_RATE = 100
DURATION_BONUS = 5 * 1000
WIDTH_HP_BAR, HEIGHT_HP_BAR = 200, 25
SIZE = WIDTH, HEIGHT = 800, 800
TILE_SIZE = 50
screen = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
player1_group = pygame.sprite.Group()
player2_group = pygame.sprite.Group()
tanks_group = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()
bonuses_group = pygame.sprite.Group()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, x, y):
        super().__init__(tiles_group, all_sprites)
        self.tile_type = tile_type
        self.image = load_image(tile_images[tile_type])
        self.rect = self.image.get_rect().move(TILE_SIZE * x, TILE_SIZE * y)


class Bonus(pygame.sprite.Sprite):
    def __init__(self, x, y, title):
        super().__init__(bonuses_group, all_sprites)
        self.x = x
        self.y = y
        self.title = title
        self.image = load_image(bonuses[title])
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect().move(TILE_SIZE * x, TILE_SIZE * y)

    def update(self):
        tank = pygame.sprite.spritecollideany(self, tanks_group)
        if tank != None:
            self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, damage, x, y, angle, tank_number):
        super().__init__()
        self.angle = angle
        self.image = pygame.Surface((10, 10))
        self.image.fill("yellow")
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.tank_number = tank_number
        self.speed = 25
        self.damage = damage

    def update(self):
        global dead
        tank = pygame.sprite.spritecollideany(self, tanks_group)
        if tank != None and tank.number != self.tank_number:
            self.kill()

        tile = pygame.sprite.spritecollideany(self, tiles_group)
        if tile != None and tile.tile_type != 'empty':
            self.kill()
        if self.angle == 0:
            self.rect.x += self.speed
        elif self.angle == 90 or self.angle == -270:
            self.rect.y -= self.speed
        elif self.angle == 180 or self.angle == -180:
            self.rect.x -= self.speed
        elif self.angle == 270 or self.angle == -90:
            self.rect.y += self.speed
        if self.rect.topleft[0] > WIDTH or self.rect.topleft[1] > HEIGHT - 100 or self.rect.bottomright[0] < 0 or \
                self.rect.bottomright[1] < 0:
            self.kill()


class Tank(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, front, back, number, filename):
        super().__init__(tanks_group, all_sprites)
        self.health = 5
        self.max_health = 5
        self.damage = 1
        self.x = x
        self.y = y
        self.number = number
        self.angle = angle
        self.direction_front = front
        self.direction_back = back
        self.image = load_image(filename)
        self.image = pygame.transform.rotate(self.image, angle - 90)
        self.rect = self.image.get_rect().move(TILE_SIZE * x, TILE_SIZE * y)
        self.last_shot = pygame.time.get_ticks()
        self.last_move = pygame.time.get_ticks()
        self.last_bonus = pygame.time.get_ticks()
        self.cooldown_shot = 1 * 1000
        self.cooldown_move = 0.5 * 1000
        self.used_bonus = False

    def update_base(self, x, y):
        time_now = pygame.time.get_ticks()
        if 0 <= x <= 15 and 0 <= y <= 13 and time_now - self.last_move > self.cooldown_move:
            self.rect.move_ip(TILE_SIZE * (x - self.x), TILE_SIZE * (y - self.y))
            self.x = x
            self.y = y
            self.last_move = time_now

    def shoot(self):
        time_now = pygame.time.get_ticks()
        if time_now - self.last_shot > self.cooldown_shot:
            bullet = Bullet(self.damage, self.rect.centerx, self.rect.centery, self.angle, self.number)
            all_sprites.add(bullet)
            bullets_group.add(bullet)
            self.last_shot = time_now

    def draw_hp_bar(self, x, y):
        pygame.draw.rect(screen, 'red', (x, y, WIDTH_HP_BAR, HEIGHT_HP_BAR))
        pygame.draw.rect(screen, 'green', (x, y, WIDTH_HP_BAR // 5 * self.health, HEIGHT_HP_BAR))

    def check_status(self, bonus):
        print(bonus)
        if bonus == 'damage':
            self.damage += 1
            self.used_bonus = True
            self.last_bonus = pygame.time.get_ticks()
        elif bonus == 'speed':
            self.cooldown_move //= 2
            self.used_bonus = True
            self.last_bonus = pygame.time.get_ticks()
        elif bonus == 'recovery':
            self.health += 1
            if self.health > self.max_health:
                self.health = self.max_health

    def reset_status(self):
        self.damage = 1
        self.cooldown_move = 0.5 * 1000
        self.used_bonus = False


class Player1(Tank):
    def __init__(self, *args):
        super().__init__(*args)

    def update(self):
        bonus = pygame.sprite.spritecollideany(self, bonuses_group)
        bullet = pygame.sprite.spritecollideany(self, bullets_group)

        if bonus != None:
            bonuses_group.update()
            self.check_status(bonus.title)

        time_now = pygame.time.get_ticks()
        if self.used_bonus and time_now - self.last_bonus > DURATION_BONUS:
            self.reset_status()

        if bullet != None and bullet.tank_number != self.number:
            play_music(1)
            self.health -= bullet.damage

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            x, y = self.x, self.y
            self.angle %= 360
            if self.x < 15 or self.direction_front != 'right':
                if level[self.y + directions[self.direction_front][0]][
                    self.x + directions[self.direction_front][1]] != "#":
                    if self.angle == 90 or self.angle == -270:
                        y -= 1
                    elif self.angle == 180 or self.angle == -180:
                        x -= 1
                    elif self.angle == 270 or self.angle == -90:
                        y += 1
                    elif self.angle == 0:
                        x += 1
                    self.update_base(x, y)

        if keys[pygame.K_DOWN]:
            x, y = self.x, self.y
            self.angle %= 360
            if self.x < 15 or self.direction_front != 'left':
                if level[self.y + directions[self.direction_back][0]][
                    self.x + directions[self.direction_back][1]] != "#":
                    if self.angle == 90 or self.angle == -270:
                        y += 1
                    elif self.angle == 180 or self.angle == -180:
                        x += 1
                    elif self.angle == 270 or self.angle == -90:
                        y -= 1
                    elif self.angle == 0:
                        x -= 1
                    self.update_base(x, y)

        if keys[pygame.K_LEFT]:
            self.angle += 90
            self.direction_front, self.direction_back = set_direction(self.angle)
            self.image = pygame.transform.rotate(self.image, 90)
            self.rect = self.image.get_rect(center=self.rect.center)

        if keys[pygame.K_RIGHT]:
            self.angle -= 90
            self.direction_front, self.direction_back = set_direction(self.angle)
            self.image = pygame.transform.rotate(self.image, -90)
            self.rect = self.image.get_rect(center=self.rect.center)


class Player2(Tank):
    def __init__(self, *args):
        super().__init__(*args)

    def update(self):
        bonus = pygame.sprite.spritecollideany(self, bonuses_group)
        bullet = pygame.sprite.spritecollideany(self, bullets_group)
        if bonus != None:
            bonuses_group.update()
            self.check_status(bonus.title)

        time_now = pygame.time.get_ticks()
        if self.used_bonus and time_now - self.last_bonus > DURATION_BONUS:
            self.reset_status()

        if bullet != None and bullet.tank_number != self.number:
            play_music(1)
            self.health -= bullet.damage

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            x, y = self.x, self.y
            self.angle %= 360
            if self.x < 15 or self.direction_front != "right":
                if level[self.y + directions[self.direction_front][0]][
                    self.x + directions[self.direction_front][1]] != "#":
                    if self.angle == 90 or self.angle == -270:
                        y -= 1
                    elif player2.angle == 180 or self.angle == -180:
                        x -= 1
                    elif self.angle == 270 or self.angle == -90:
                        y += 1
                    elif self.angle == 0:
                        x += 1
                    self.update_base(x, y)

        if keys[pygame.K_s]:
            x, y = self.x, self.y
            self.angle %= 360
            if self.x < 15 or self.direction_front != 'left':
                if level[self.y + directions[self.direction_back][0]][
                    self.x + directions[self.direction_back][1]] != "#":
                    if self.angle == 90 or self.angle == -270:
                        y += 1
                    elif self.angle == 180 or self.angle == -180:
                        x += 1
                    elif self.angle == 270 or self.angle == -90:
                        y -= 1
                    elif self.angle == 0:
                        x -= 1
                    self.update_base(x, y)

        if keys[pygame.K_a]:
            self.angle += 90
            self.angle %= 360
            self.direction_front, self.direction_back = set_direction(self.angle)
            self.image = pygame.transform.rotate(self.image, 90)
            self.rect = self.image.get_rect(center=self.rect.center)

        if keys[pygame.K_d]:
            self.angle -= 90
            self.angle %= 360
            self.direction_front, self.direction_back = set_direction(self.angle)
            self.image = pygame.transform.rotate(self.image, -90)
            self.rect = self.image.get_rect(center=self.rect.center)


def set_direction(angle):
    angle %= 360
    if angle == 90 or angle == -270:
        return 'top', 'bot'
    elif angle == 180 or angle == -180:
        return 'left', 'right'
    elif angle == 270 or angle == -90:
        return 'bot', 'top'
    elif angle == 0:
        return 'right', 'left'


def pause():
    global paused
    text1 = write_text('arial', 'PAUSED', (200, 0, 70))
    text2 = write_text('arial', 'Чтобы продолжить нажмите ESC', (100, 244, 120))
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                paused = False
        screen.fill((0, 0, 0))
        all_sprites.draw(screen)
        tiles_group.draw(screen)
        tanks_group.draw(screen)
        bullets_group.draw(screen)
        bonuses_group.draw(screen)
        player1_group.draw(screen)
        player2_group.draw(screen)

        screen.blit(text1, (WIDTH // 2 - 30, HEIGHT - 75))
        screen.blit(text2, (WIDTH // 2 - 125, HEIGHT - 50))
        pygame.display.flip()
        pygame.time.delay(30)


def end_game(dead_number):
    global paused, restart
    paused = True
    winner_number = {1: 2, 2: 1}
    text1 = write_text('arial', 'GAME OVER', (200, 0, 70))
    text2 = write_text('arial', f'Player {winner_number[dead_number]} won', (100, 244, 120))
    text3 = write_text('arial', 'Restart', (100, 244, 120), 50)
    text4 = write_text('arial', 'Main menu', (100, 244, 120), 50)
    t3 = text3.get_rect().move(50, 725)
    t4 = text4.get_rect().move(550, 725)
    play_music(2)
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if check_hitbox(t3, event):
                    restart = True
                if check_hitbox(t4, event):
                    restart = True

        if restart:
            paused = False

        screen.fill((0, 0, 0))
        all_sprites.draw(screen)
        tanks_group.draw(screen)
        player1_group.draw(screen)
        player2_group.draw(screen)
        screen.blit(text1, (WIDTH // 2 - 50, HEIGHT - 75))
        screen.blit(text2, (WIDTH // 2 - 50, HEIGHT - 50))
        screen.blit(text3, (WIDTH // 2 - 75, HEIGHT // 4 + 100))
        pygame.display.flip()
        pygame.time.delay(30)


def play_music(type):
    global volume_music
    if type == 1:
        pygame.mixer.music.load("hit_sound.wav")
        pygame.mixer.music.play()
        pygame.mixer.music.set_volume(volume_music)
    if type == 2:
        pygame.mixer.music.load("Game-end-sound-effect.mp3")
        pygame.mixer.music.play()
        pygame.mixer.music.set_volume(volume_music)


def check_hitbox(el, event):
    if el.topleft[0] < event.pos[0] < el.topright[0] and \
            el.topleft[1] < event.pos[1] < el.bottomleft[1] and \
            el.bottomleft[0] < event.pos[0] < el.bottomright[0] and \
            el.bottomleft[1] > event.pos[1]:
        return True
    return False


def main_menu():
    global menu, option, running
    game_title = write_text('arial', 'TANKS', (0, 200, 200), 80)
    start_game = write_text('arial', 'START GAME', (0, 180, 200), 40)
    st = start_game.get_rect().move((WIDTH // 2 - 90, HEIGHT // 4 + 100))
    options = write_text('arial', 'OPTIONS', (0, 180, 200), 40)
    op = options.get_rect().move((WIDTH // 2 - 60, HEIGHT // 4 + 200))
    EXIT = write_text('arial', 'EXIT', (0, 180, 200), 40)
    ex = EXIT.get_rect().move((WIDTH // 2 - 20, HEIGHT // 4 + 300))
    while menu:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if check_hitbox(st, event):
                    running = True
                    return
                elif check_hitbox(op, event):
                    option = True
                    return
                elif check_hitbox(ex, event):
                    pygame.quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()

        screen.fill((0, 0, 0))
        screen.blit(game_title, (WIDTH // 2 - 90, HEIGHT // 8))
        screen.blit(start_game, (WIDTH // 2 - 90, HEIGHT // 4 + 100))
        screen.blit(options, (WIDTH // 2 - 60, HEIGHT // 4 + 200))
        screen.blit(EXIT, (WIDTH // 2 - 20, HEIGHT // 4 + 300))

        pygame.display.flip()


def option_menu():
    global menu, option
    options = write_text('arial', 'OPTIONS', (0, 200, 200), 80)
    volume = write_text('arial', 'VOLUME', (0, 180, 200), 40)
    vol = volume.get_rect().move((WIDTH // 2 - 65, HEIGHT // 8 + 200))
    select_level = write_text('arial', 'SELECT LEVEL', (0, 180, 200), 40)
    sl = select_level.get_rect().move((WIDTH // 2 - 110, HEIGHT // 8 + 300))
    back = write_text('arial', 'BACK', (255, 100, 70), 40)
    bk = back.get_rect().move((0, HEIGHT - 40))
    while option:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if check_hitbox(vol, event):
                    volume_menu()
                elif check_hitbox(sl, event):
                    choose_level()
                elif check_hitbox(bk, event):
                    return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()

        screen.fill((0, 0, 0))
        screen.blit(options, (WIDTH // 2 - 150, HEIGHT // 8))
        screen.blit(volume, (WIDTH // 2 - 65, HEIGHT // 8 + 200))
        screen.blit(select_level, (WIDTH // 2 - 110, HEIGHT // 8 + 300))
        screen.blit(back, (0, HEIGHT - 40))

        pygame.display.flip()


def choose_level():
    global number_level, levels
    main_text = write_text('arial', 'Levels', (0, 200, 200), 80)
    first = write_text('arial', '1', (0, 200, 200), 60)
    first_hb = first.get_rect().move((WIDTH // 2 - 90, HEIGHT // 4 + 100))
    second = write_text('arial', '2', (0, 200, 200), 60)
    second_hb = second.get_rect().move((WIDTH // 2 - 20, HEIGHT // 4 + 100))
    third = write_text('arial', '3', (0, 200, 200), 60)
    third_hb = third.get_rect().move((WIDTH // 2 + 50, HEIGHT // 4 + 100))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if check_hitbox(first_hb, event):
                    number_level = 1
                    return
                if check_hitbox(second_hb, event):
                    number_level = 2
                    return
                if check_hitbox(third_hb, event):
                    number_level = 3
                    return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()

        screen.fill((0, 0, 0))
        screen.blit(main_text, (WIDTH // 2 - 90, HEIGHT // 8))
        screen.blit(first, (WIDTH // 2 - 90, HEIGHT // 4 + 100))
        screen.blit(second, (WIDTH // 2 - 20, HEIGHT // 4 + 100))
        screen.blit(third, (WIDTH // 2 + 50, HEIGHT // 4 + 100))
        pygame.display.flip()


def volume_menu():
    global volume_music
    main_text = write_text('arial', 'Volume', (0, 200, 200), 80)
    zero = write_text('arial', '0%', (0, 200, 200), 60)
    zero_hb = zero.get_rect().move((WIDTH // 2 - 120, HEIGHT // 4 + 100))
    fifty = write_text('arial', '50%', (0, 200, 200), 60)
    fifty_hb = fifty.get_rect().move((WIDTH // 2 - 20, HEIGHT // 4 + 100))
    max = write_text('arial', '100%', (0, 200, 200), 60)
    max_hb = max.get_rect().move((WIDTH // 2 + 80, HEIGHT // 4 + 100))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if check_hitbox(zero_hb, event):
                    volume_music = 0
                    return
                if check_hitbox(fifty_hb, event):
                    volume_music = 0.5
                    return
                if check_hitbox(max_hb, event):
                    volume_music = 1
                    return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
        screen.fill((0, 0, 0))
        screen.blit(main_text, (WIDTH // 2 - 90, HEIGHT // 8))
        screen.blit(zero, (WIDTH // 2 - 120, HEIGHT // 4 + 100))
        screen.blit(fifty, (WIDTH // 2 - 20, HEIGHT // 4 + 100))
        screen.blit(max, (WIDTH // 2 + 80, HEIGHT // 4 + 100))
        pygame.display.flip()


def write_text(filename, text, color: tuple, size=20):
    font = pygame.font.SysFont(filename, size)
    return font.render(text, False, color)


def load_image(filename):
    image = pygame.image.load(filename)
    image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
    return image


def load_level(filename):
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


def generate_level(level):
    player1, player2, x, y = None, None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '-':
                Tile('bg', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                player1 = Player1(x, y, 90, 'top', 'bot', 1, 'tank.png')
                player1_group.add(player1)
            elif level[y][x] == '!':
                Tile('empty', x, y)
                player2 = Player2(x, y, 270, 'bot', 'top', 2, 'tank2.png')
                player2_group.add(player2)
    return player1, player2


def generate_bonus():
    bonus_titles = {0: 'damage',
                    1: 'recovery',
                    2: 'speed'}
    shuffle = True
    while shuffle:
        x, y = rand.randint(0, 15), rand.randint(0, 13)
        if level[y][x] != '#':
            Bonus(x, y, bonus_titles[rand.randint(0, 2)])
            shuffle = False


tile_images = {'empty': 'grass.jpg',
               'wall': 'wall.png',
               'bg': "black.png"}

directions = {'top': (-1, 0),
              'left': (0, -1),
              'bot': (1, 0),
              'right': (0, 1)}

bonuses = {'damage': 'damage.png',
           'recovery': 'recovery.png',
           'speed': 'speed.png'}

levels = {1: 'level_1.txt',
          2: 'level_2.txt',
          3: 'level_3.txt'}

number_level = 1
volume_music = 1

cooldown_bonus = rand.randint(7, 10) * 1000
last_bonus = 0

paused = False
menu = True
option = False
running = False
restart = False
while running == False:
    main_menu()
    option_menu()
    option = False

level = load_level(levels[number_level])
player1, player2 = generate_level(level)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if paused == False:
                    paused = True
            if event.key == pygame.K_SPACE:
                player1.shoot()
            if event.key == pygame.K_f:
                player2.shoot()
    if paused:
        pause()

    time_bonus = pygame.time.get_ticks()
    if time_bonus - last_bonus > cooldown_bonus:
        generate_bonus()
        last_bonus = time_bonus

    if player1.health <= 0:
        player1.kill()
        end_game(1)
    if player2.health <= 0:
        player2.kill()
        end_game(2)

    if restart:
        restart = False
        all_sprites.empty()
        player1_group.empty()
        player2_group.empty()
        bullets_group.empty()
        bonuses_group.empty()
        tanks_group.empty()
        player1, player2 = generate_level(level)

    screen.fill((0, 0, 0))
    tiles_group.draw(screen)
    tanks_group.draw(screen)
    bullets_group.draw(screen)
    bonuses_group.draw(screen)
    player1_group.update()
    player2_group.update()
    bullets_group.update()

    screen.blit(write_text('arial', 'Player 1', (255, 255, 255)), (125, 725))
    screen.blit(write_text('arial', 'Player 2', (255, 255, 255)), (625, 725))
    player1.draw_hp_bar(50, 750)
    player2.draw_hp_bar(550, 750)

    pygame.display.flip()
    pygame.time.delay(TICK_RATE)

pygame.quit()
