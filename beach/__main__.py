import math
import os
import pygame
import random
from vec2d import Vec2d

ASSET_DIR = "data"
FPS = 60
SCREEN_X = 640
SCREEN_Y = 480
TIDE_LIMIT_Y = SCREEN_Y * .80
MAX_POWERUPS = 20

def load_sound(name, is_free=True):
  class NoneSound:
    def play(self): pass
  if not pygame.mixer or not pygame.mixer.get_init():
    return NoneSound()
  if is_free:
    fullname = os.path.join(ASSET_DIR, name)
  else:
    fullname = os.path.join(ASSET_DIR, "non-free", name)
  try:
    sound = pygame.mixer.Sound(fullname)
  except pygame.error, message:
    print 'Cannot load sound:', fullname
    raise SystemExit, message
  return sound

class Player(pygame.sprite.Sprite):
  def __init__(self, position=Vec2d(0, 0), vector=Vec2d(0, 0), speed=0):
    pygame.sprite.Sprite.__init__(self, self.containers)

    self._layer = 10
    self.image = pygame.image.load(
                 os.path.join(ASSET_DIR, "player.png")
                 ).convert_alpha()
    self.rect = self.image.get_rect()

    self.__position = position
    self.rect.center = self.__position
    self.__vector = vector.normalized()
    self.__speed = speed
    self.__powerups = []

  def update(self, dt):
    self.__position += self.__speed * self.__vector * float(dt) / float(FPS)
    self.rect.center = self.__position
    self.rect = self.image.get_rect(center=self.rect.center)
    lead_position = self.__position
    for powerup in self.__powerups:
      lead_position = powerup.move(self.__position)

  def move(self, new_pos):
    delta = new_pos - self.__position
    self.__vector = delta.normalized()
    max_speed = MAX_POWERUPS + 4 - len(self.__powerups)
    self.__speed = min(max_speed, delta.get_length() / 4)

  def add_powerups(self, powerups):
    self.__powerups.extend(powerups)

  def score_powerups(self):
    score = 0
    multiplier = len(self.__powerups)
    for powerup in self.__powerups:
      score += powerup.get_score()
      powerup.move(Vec2d(-1, SCREEN_Y + 1))
    self.__powerups = []
    return score * multiplier

  def in_water(self, y):
    return self.rect.bottom < y

class Powerup(pygame.sprite.Sprite):
  NORMAL = 0
  SPECIAL = 1
  AMAZING = 2
  MORE_AMAZING = 3
  CATHERINE = 4

  FILENAMES = {
    NORMAL: 'gem-blue',
    SPECIAL: 'gem-green',
    AMAZING: 'gem-orange',
    MORE_AMAZING: 'star',
    CATHERINE: 'catherine',
  }

  SCORES = {
    NORMAL: 1,
    SPECIAL: 3,
    AMAZING: 5,
    MORE_AMAZING: 20,
    CATHERINE: 50,
  }

  def __init__(self, type, position):
    pygame.sprite.Sprite.__init__(self, self.containers)

    self._layer = 9
    self.image = pygame.image.load(
                 os.path.join("data", "%s.png" % self.FILENAMES[type])
                 ).convert_alpha()
    self.rect = self.image.get_rect()

    self.__score = self.SCORES[type]

    self.__position = position
    self.rect.center = self.__position
    self.__vector = Vec2d(0, 0)
    self.__speed = 0

    self.rect = self.image.get_rect(center=self.rect.center)

  def get_score(self):
    return self.__score

  def update(self, dt):
    self.__position += self.__speed * self.__vector * float(dt) / float(FPS)
    self.rect.center = self.__position
    self.rect = self.image.get_rect(center=self.rect.center)
    if self.__position[0] < 0 or self.__position[1] >= SCREEN_Y:
      self.kill()

  def halt(self):
    self.__speed = 0

  def move(self, new_pos):
    delta = new_pos - self.__position
    self.__vector = delta.normalized()
    self.__speed = delta.get_length() / 4
    return self.__position

class TreasureChest(pygame.sprite.Sprite):
  def __init__(self, position):
    pygame.sprite.Sprite.__init__(self, self.containers)

    self._layer = 8
    self.image = pygame.image.load(
                 os.path.join("data", "treasure_chest.png")
                 ).convert_alpha()
    self.rect = self.image.get_rect()
    self.rect.center = position
    self.rect = self.image.get_rect(center=self.rect.center)

  def update(self, dt):
    pass

class Dashboard(pygame.sprite.Sprite):
  BACKGROUND_COLOR = (64, 64, 64)
  COLOR = (255, 255, 0)

  def __init__(self, position, game, font, line_count):
    self._layer = 10
    pygame.sprite.Sprite.__init__(self, self.containers)
    self.game = game
    self.font = font
    self.line_count = line_count
    self.line_height = self.font.get_height()
    self.image = pygame.Surface((80, self.line_height *
                                 self.line_count)).convert()
    self.rect = self.image.get_rect()
    self.rect.left = position[0]
    self.rect.bottom = position[1]

  def update(self, dt):
    cursor = (4, 0)

    self.image.fill(Dashboard.BACKGROUND_COLOR)

    str = 'Score: %d' % self.game.get_score()
    text = self.font.render(str, 1, Dashboard.COLOR)
    textpos = text.get_rect()
    textpos.topleft = cursor
    text.set_alpha(128)
    self.image.blit(text, textpos)
    cursor = (cursor[0], cursor[1] + self.line_height)

    str = 'Items: %d' % (self.game.get_carrying_count())
    text = self.font.render(str, 1, Dashboard.COLOR)
    textpos = text.get_rect()
    textpos.topleft = cursor
    text.set_alpha(128)
    self.image.blit(text, textpos)
    cursor = (cursor[0], cursor[1] + self.line_height)

def get_font(size):
  return pygame.font.Font(os.path.join(ASSET_DIR, 'surface_medium.otf'), size)

class Game:
  BACKGROUND = (128, 128, 128)

  def __init__(self):
    self.__screen = pygame.display.set_mode([SCREEN_X, SCREEN_Y])
    self.__small_font = get_font(14)

    self.__sound_waves = []
    for i in range(0, 3):
      self.__sound_waves.append(load_sound('wave_crash_%d.wav' % i))
    self.__powerup_sound = load_sound('congrats.wav')
    self.__score_sound = load_sound('marvelous_moment03.wav', False)
    self.__sad_sound = load_sound('powerup_40.wav', False)

    self.__background = pygame.image.load(os.path.join(ASSET_DIR,
                                                       'background.png'))
    self.__screen.blit(self.__background, self.__background.get_rect())
    pygame.display.update()

    self.__ocean = pygame.image.load(os.path.join(ASSET_DIR, 'ocean.png'))
    self.__ocean_start_y = - SCREEN_Y * 2
    self.__ocean_end_y = self.__ocean_start_y
    self.set_ocean_target()

    self.__all_sprites = pygame.sprite.LayeredUpdates()
    self.__powerup_sprites = pygame.sprite.RenderUpdates()
    self.__treasure_chest_sprites = pygame.sprite.RenderUpdates()
    self.__captured_powerup_sprites = pygame.sprite.RenderUpdates()
    self.__foreground_sprites = pygame.sprite.RenderUpdates()

    Dashboard.containers = self.__foreground_sprites, self.__all_sprites
    Player.containers = self.__all_sprites
    Powerup.containers = self.__all_sprites, self.__powerup_sprites
    TreasureChest.containers = self.__all_sprites, self.__treasure_chest_sprites

    self.__dashboard = Dashboard((SCREEN_X - 80 - 5, SCREEN_Y),
                       self, self.__small_font, 2)

    for x in range(32, SCREEN_X - 32, 30):
      y = random.randint(16, TIDE_LIMIT_Y)
      type = self.type_for_y(y)
      Powerup(type, Vec2d(x, y))

    self.__player = Player(Vec2d(SCREEN_X / 2, SCREEN_Y))
    self.__treasure_chest = TreasureChest(Vec2d(32, SCREEN_Y - 77 / 2))

    pygame.mouse.set_pos(self.__player.rect.centerx,
                         self.__player.rect.centery - 50)

    self.__score = 0

    self.__clock = pygame.time.Clock()

  def get_score(self):
    return self.__score

  def get_carrying_count(self):
    return len(self.__captured_powerup_sprites)

  def type_for_y(self, y):
    normalized = float(SCREEN_Y - y) / float(SCREEN_Y)
    value = random.uniform(0, normalized)
    if value < 0.25:
      return Powerup.NORMAL
    if value < 0.40:
      return Powerup.SPECIAL
    if value < 0.65:
      return Powerup.AMAZING
    if value < 0.90:
      return Powerup.MORE_AMAZING
    return Powerup.CATHERINE

  def handle_events(self):
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        return True
      elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
          return True
    return False

  def set_ocean_target(self):
    self.__played_wave_sound = False
    self.__ocean_start_y = self.__ocean_end_y
    if self.__ocean_start_y < 0:
      self.__ocean_end_y = random.randint(SCREEN_Y * .15, TIDE_LIMIT_Y)
      self.__ocean_flow = True
    else:
      self.__ocean_end_y = random.randint(-SCREEN_Y * 2, -SCREEN_Y * 0.25)
      self.__ocean_flow = False
    self.__ocean_step = 0
    self.__ocean_tide_rate = float(random.randint(3000, 5000))

  def smoothstep(self, min, max, input):
    r = (float(input) - float(min)) / (float(max) - float(min))
    return r * r * (3.0 - 2.0 * r)

  def move_ocean(self, dt):
    smooth_step = self.smoothstep(0.0, 1.0, self.__ocean_step)
    self.__ocean_y = self.__ocean_start_y + float(self.__ocean_end_y -
                      self.__ocean_start_y) * smooth_step
    self.__ocean_step += dt / self.__ocean_tide_rate
    if self.__ocean_y >= 0 and self.__ocean_flow and not self.__played_wave_sound:
      self.__played_wave_sound = True
      sound_num = random.randint(0, len(self.__sound_waves) - 1)
      self.__sound_waves[sound_num].play()
    if self.__ocean_step >= 1:
      self.set_ocean_target()

  def wash_up_powerups(self):
    if self.__ocean_step == 0.0:
      return
    if self.__ocean_flow:
      return
    if self.__ocean_y <= 0:
      return
    if len(self.__powerup_sprites.sprites()) >= MAX_POWERUPS:
      return
    while True:
      x = random.randint(32, SCREEN_X - 64)
      y = random.randint(0, max(32, int(self.__ocean_y)) - 31)
      type = self.type_for_y(y)
      powerup = Powerup(type, Vec2d(x, y))
      powerup_collisions = pygame.sprite.spritecollide(powerup,
                                                       self.__powerup_sprites, False)
      if len(powerup_collisions) > 1:
        powerup.kill()
      else:
        break

  def check_for_drowning(self):
    if self.__player.in_water(self.__ocean_y):
      self.__sad_sound.play()
      return True
    return False

  def handle_powerups(self):
    powerup_collisions = pygame.sprite.spritecollide(self.__player,
                         self.__powerup_sprites, False)
    if powerup_collisions:
      self.__powerup_sound.play()
      self.__captured_powerup_sprites.add(powerup_collisions)
      for powerup in powerup_collisions:
        self.__powerup_sprites.remove(powerup)
      self.__player.add_powerups(powerup_collisions)

    treasure_chest_collisions = pygame.sprite.spritecollide(self.__player,
                                self.__treasure_chest_sprites, False)
    if treasure_chest_collisions:
      self.__score_sound.play()
      self.__score += self.__player.score_powerups()

    if self.__ocean_flow and self.__ocean_y >= 0:
      for sprite in self.__powerup_sprites:
        if sprite.rect.bottom < self.__ocean_y:
          sprite.kill()

  def run(self):
    done = False
    player_dead = False

    while not done:
      elapsed = self.__clock.tick(FPS)

      done = self.handle_events()
      if done:
        continue
      if not player_dead:
        (x_mouse, y_mouse) = pygame.mouse.get_pos()
        self.__player.move(Vec2d(x_mouse, y_mouse))

      self.__all_sprites.update(elapsed)
      self.move_ocean(elapsed)
      self.wash_up_powerups()
      self.handle_powerups()
      if not player_dead:
        player_dead = self.check_for_drowning()
        if player_dead:
          self.__player.kill()
          for sprite in self.__captured_powerup_sprites:
            sprite.halt()
            self.__powerup_sprites.add(sprite)
          self.__captured_powerup_sprites.empty()

      self.__screen.blit(self.__background, self.__background.get_rect())

      self.__all_sprites.clear(self.__screen, self.__background)
      dirty = self.__all_sprites.draw(self.__screen)

      self.__screen.blit(self.__ocean,
                         pygame.Rect(0, self.__ocean_y - 480, 640, 480))

      pygame.display.update(dirty)

def main():
  pygame.mixer.pre_init(frequency=22050, size=-16, channels=1, buffer=8192)
  pygame.init()

  game = Game()
  game.run()

  pygame.quit()
