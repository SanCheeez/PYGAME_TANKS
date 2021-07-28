import pygame

pygame.init()

WIDTH_HP_BAR, HEIGHT_HP_BAR = 200, 25
SIZE = WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode(SIZE)
tile_size = 50
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
player1_group = pygame.sprite.Group()
player2_group = pygame.sprite.Group()
tanks_group = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, x, y):
        super().__init__(tiles_group, all_sprites)
        self.tile_type = tile_type
        self.image = load_image(tile_images[tile_type])
        self.rect = self.image.get_rect().move(50 * x, 50 * y)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, tank_number):
        pygame.sprite.Sprite.__init__(self)
        self.angle = angle
        self.image = pygame.Surface((10, 10))
        self.image.fill("yellow")
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.tank_number = tank_number
        self.speed = 25

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
        self.x = x
        self.y = y
        self.number = number
        self.angle = angle
        self.direction_front = front
        self.direction_back = back
        self.image = load_image(filename)
        self.image = pygame.transform.rotate(self.image, angle - 90)
        self.rect = self.image.get_rect().move(tile_size * x, tile_size * y)
        self.last_shot = pygame.time.get_ticks()
        self.last_move = pygame.time.get_ticks()
        self.cooldown_shot = 1000
        self.cooldown_move = 500

    def update_base(self, x, y):
        time_now = pygame.time.get_ticks()
        if 0 <= x <= 15 and 0 <= y <= 13 and time_now - self.last_move > self.cooldown_move:
            self.rect.move_ip(tile_size * (x - self.x), tile_size * (y - self.y))
            self.x = x
            self.y = y
            self.last_move = time_now

    # def rotate(self):
    #     self.angle %= 360
    #     self.image = pygame.transform.rotate(self.angle)

    def shoot(self):
        time_now = pygame.time.get_ticks()
        if time_now - self.last_shot > self.cooldown_shot:
            bullet = Bullet(self.rect.centerx, self.rect.centery, self.angle, self.number)
            all_sprites.add(bullet)
            bullets_group.add(bullet)
            self.last_shot = time_now

    def draw_hp_bar(self, x, y):
        pygame.draw.rect(screen, 'red', (x, y, WIDTH_HP_BAR, HEIGHT_HP_BAR))
        pygame.draw.rect(screen, 'green', (x, y, WIDTH_HP_BAR // 5 * self.health, HEIGHT_HP_BAR))


class Player1(Tank):
    def __init__(self, *args):
        super().__init__(*args)

    def update(self):
        bullet = pygame.sprite.spritecollideany(self, bullets_group)
        if bullet != None and bullet.tank_number != self.number:
            self.health -= 1

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            x, y = self.x, self.y
            self.angle %= 360
            if self.x < 15 or self.direction_front != 'right':
                if level[self.y + directions[self.direction_front][0]][self.x + directions[self.direction_front][1]] != "#":
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
                if level[self.y + directions[self.direction_back][0]][self.x + directions[self.direction_back][1]] != "#":
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
        bullet = pygame.sprite.spritecollideany(self, bullets_group)
        if bullet != None and bullet.tank_number != self.number:
            self.health -= 1

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            x, y = self.x, self.y
            self.angle %= 360
            if self.x < 15 or self.direction_front != "right":
                if level[self.y + directions[self.direction_front][0]][self.x + directions[self.direction_front][1]] != "#":
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
                if level[self.y + directions[self.direction_back][0]][self.x + directions[self.direction_back][1]] != "#":
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
        player1_group.draw(screen)
        screen.blit(text1, (WIDTH // 2 - 50, HEIGHT - 75))
        screen.blit(text2, (WIDTH // 2 - 140, HEIGHT - 50))
        pygame.display.flip()
        pygame.time.delay(30)


def end_game(dead_number):
    global paused
    paused = True
    winner_number = {1: 2, 2: 1}
    text1 = write_text('arial', 'GAME OVER', (200, 0, 70))
    text2 = write_text('arial', f'Player {winner_number[dead_number]} won', (100, 244, 120))
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
        screen.fill((0, 0, 0))
        all_sprites.draw(screen)
        tanks_group.draw(screen)
        player1_group.draw(screen)
        player2_group.draw(screen)
        screen.blit(text1, (WIDTH // 2 - 50, HEIGHT - 75))
        screen.blit(text2, (WIDTH // 2 - 50, HEIGHT - 50))
        pygame.display.flip()
        pygame.time.delay(30)


def write_text(filename, text, color: tuple, size=20):
    font = pygame.font.SysFont(filename, size)
    return font.render(text, False, color)


def load_image(filename):
    image = pygame.image.load(filename)
    image = pygame.transform.scale(image, (tile_size, tile_size))
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


tile_images = {'empty': 'grass.jpg',
               'wall': 'wall.png',
               'bg': "black.png"}

directions = {'top': (-1, 0),
              'left': (0, -1),
              'bot': (1, 0),
              'right': (0, 1)}

levels = {1: 'level_1.txt',}

level = load_level(levels[1])
player1, player2 = generate_level(level)

paused = False
running = True
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

    if player1.health == 0:
        player1.kill()
        end_game(1)
    if player2.health == 0:
        player2.kill()
        end_game(2)

    screen.fill((0, 0, 0))
    tiles_group.draw(screen)
    tanks_group.draw(screen)
    bullets_group.draw(screen)
    bullets_group.update()
    player1_group.update()
    player2_group.update()

    screen.blit(write_text('arial', 'Player 1', (255, 255, 255)), (125, 725))
    screen.blit(write_text('arial', 'Player 2', (255, 255, 255)), (625, 725))
    player1.draw_hp_bar(50, 750)
    player2.draw_hp_bar(550, 750)

    pygame.display.flip()
    # pygame.time.delay(100)
    clock.tick(10)

pygame.quit()
