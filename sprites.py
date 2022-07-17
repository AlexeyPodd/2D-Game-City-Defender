import pygame
from random import randint as rnd, choice
from time import time
from math import sin, cos, radians

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

bg_color = (204, 204, 255)
BLACK = (0, 0, 0)
DARK_RED = (102, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
SPOTLIGHT_YELLOW = (93, 93, 0)
DARK_YELLOW = (102, 102, 0)
DARK_GREEN = (54, 102, 25)
TEXT_GREEN = (107, 142, 35)
DARK_KHAKI = (60, 67, 53)
VERY_DARK_KHAKI = (50, 56, 45)
TEXT_BLUE = (65, 105, 225)
TEXT_RED = (154, 24, 24)
TEXT_YELLOW = (178, 178, 0)
BLUE = (46, 139, 87)
GREEN = (124, 252, 0)


class Menu(pygame.Surface):
    def __init__(self, size, menu_dislocation, score, game):
        self.game = game

        # Creating menu surface
        super().__init__((size[0] - menu_dislocation, size[1]))

        # Creating info panel and buttons
        self.info = MenuInfoSlot((self.get_width(), 36), score, self.game.level_number)

        buttons_data = [
            ('Homing Sight', 20_000, self.__buy_homing_sight, 1, None),
            ('Night Vision', 5_000, self.__buy_night_vision, 1, None),
            ('NV Battery', 3_000, self.__buy_nv_battery, 1, 1),
            ('Target Recognition', 10_000, self.__buy_target_recognition, 1, None),
            ('Spotlight', 1_000, self.__buy_spotlight, 5, None, [3_000, 5_000, 10_000, 15_000]),
            ('Fighter', 10_000, self.__buy_fighter, 1, None),
            ('Fighter Pilot', 10_000, self.__buy_pilot, 1, 5),
            ('Laser Damage', 7_000, self.__buy_laser_damage_encrease, 3, None, [15_000, 30_000]),
            ('Laser Battery', 7_000, self.__buy_laser_battery, 3, None, [15_000, 30_000])
        ]

        self.buttons = [MenuButton((self.get_width() // 2 - 70, 75 * (i + 1)), menu_dislocation, i, button_data)
                        for i, button_data in enumerate(buttons_data)]
        self.button_indicators = [ButtonIndicator(button) for button in self.buttons]

        # Drawing menu
        self.fill(DARK_KHAKI)
        self.blit(self.info, (0, 0))

        for button in self.buttons:
            self.blit(button.image, button.rect)

        for indicator in self.button_indicators:
            self.blit(indicator.image, indicator.rect)

    def update(self, score):
        # Updating buttons
        for button in self.buttons:
            button.update(score)

        # Updating button's cost indicators
        for indicator in self.button_indicators:
            indicator.update()

        # Updating info panel
        self.info.update(score)

        # Drawing menu on menu surface
        self.fill(DARK_KHAKI)
        self.blit(self.info, (0, 0))
        for button in self.buttons:
            self.blit(button.image, button.rect)
        for indicator in self.button_indicators:
            self.blit(indicator.image, indicator.rect)

    @staticmethod
    def __buy_homing_sight():
        Aim.homing_sight_bought = True

    @staticmethod
    def __buy_night_vision():
        Aim.night_vision_bought = True

    @staticmethod
    def __buy_nv_battery():
        Aim.nv_energy_max += 600

    @staticmethod
    def __buy_target_recognition():
        Aim.target_recognition_bought = True

    def __buy_spotlight(self):
        self.game.spotlights += 1
        self.game.darkness_limit -= SpotLight.power

    def __buy_fighter(self):
        self.game.fighter_bought = True

    def __buy_pilot(self):
        self.game.pilot_bought = True

    @staticmethod
    def __buy_laser_damage_encrease():
        Aim.dmg *= 2
        Aim.laser_sound_indx += 1

    @staticmethod
    def __buy_laser_battery():
        Aim.energy_max *= 2


class MenuInfoSlot(pygame.Surface):
    def __init__(self, size, score, level_number):
        super().__init__(size)
        self.__size = size

        # Setting a timer and score
        self.__start_time = time()
        self.time = 0
        self.score = score
        self.level_number = level_number

        # Drawing score, time and level number
        self.fill(DARK_KHAKI)
        self.__draw_info()

    def update(self, score):
        # Updating time
        self.time = time() - self.__start_time
        self.score = score

        # Drawing score and time
        self.fill(DARK_KHAKI)
        self.__draw_info()

    def reset_timer(self):
        self.__start_time = time()
        self.time = 0

    def __draw_info(self):
        f = pygame.font.SysFont('arial', self.__size[1])

        level_text = f.render('DAY ' + str(self.level_number), True, TEXT_GREEN)
        time_text = f.render(self.__format_time(self.time), True, TEXT_RED)
        score_text = f.render(str(self.score), True, TEXT_BLUE)

        self.blit(level_text, ((self.get_width() - level_text.get_width()) // 2, 0))
        self.blit(time_text, (10, 0))
        self.blit(score_text, (self.get_width() - score_text.get_width() - 10, 0))

    @staticmethod
    def __format_time(t, time_speed=252, time_start=(6 * 3600)):
        t = int(time_start + t * time_speed)
        if t >= 86_400:
            t -= 86_400
        minutes = str(t % 3600 // 60).rjust(2, '0')
        hours = str(t // 3600).rjust(2, '0')
        return f'{hours}:{minutes}'


class MenuButton(pygame.sprite.Sprite):
    w, h = 210, 50
    statuses = []

    font = 'arial'
    font_size = 28

    button_push_sound = pygame.mixer.Sound("sounds/ButtonClicks/Click_push.wav")
    button_unpush_sound = pygame.mixer.Sound("sounds/ButtonClicks/Click_unpush.wav")

    def __init__(self, pos, menu_dislocation, indx, button_data):
        super().__init__()

        name = button_data[0]
        self.indx = indx
        self.cost = button_data[1]
        self.get_goods = button_data[2]
        self.lots = button_data[3]
        self.parent = button_data[4]

        if self.lots > 1:
            self.lots_costs = button_data[5]
        elif self.indx in (5, 6):
            self.lots_costs = [self.cost]
        else:
            self.lots_costs = None

        self.image = pygame.Surface((self.w, self.h))
        self.image.fill(DARK_YELLOW)

        self.rect = self.image.get_rect(center=pos)
        self.rect_game = self.rect.move(menu_dislocation, 0)

        f = pygame.font.SysFont(self.font, self.font_size)
        sc_text = f.render(name, True, TEXT_GREEN)
        pos_text = sc_text.get_rect(center=(self.image.get_width() // 2, self.image.get_height() // 2))
        self.image.blit(sc_text, pos_text)

        self.pushed = False

        self.__status = 'blocked'
        self.statuses.append(self.__status)

    def update(self, score):
        self.__change_status(score)

        if self.__status == 'blocked':
            color = VERY_DARK_KHAKI
        elif self.__status == 'ready':
            color = DARK_GREEN
        elif self.__status == 'bought':
            color = TEXT_YELLOW
        else:
            raise ValueError('invalid button status')

        pygame.draw.rect(self.image, color, (0, 0, self.w, self.h), 7)

    def __change_status(self, score):
        if self.__status != 'bought':
            if score >= self.cost and (self.parent is None or self.statuses[self.parent] == 'bought'):
                self.__status = 'ready'
            else:
                self.__status = 'blocked'

        self.statuses[self.indx] = self.__status

    def push(self):
        if self.__status == 'ready':
            self.pushed = True
            self.button_push_sound.play()
            self.get_goods()
            self.lots -= 1
            self.__status = 'bought'
            return self.cost
        else:
            return 0

    def unpush(self, score):
        self.pushed = False
        if self.lots:
            self.button_unpush_sound.play()
            self.cost = self.lots_costs[0]
            del self.lots_costs[0]
            if score >= self.cost:
                self.__status = 'ready'
            else:
                self.__status = 'blocked'

    def renew(self, score):
        self.button_unpush_sound.play()
        self.lots += 1
        if score >= self.cost:
            self.__status = 'ready'
        else:
            self.__status = 'blocked'


class ButtonIndicator(pygame.sprite.Sprite):
    w, h = MenuButton.w // 2 + 40, MenuButton.h
    font = 'arial'
    font_size = 28

    def __init__(self, button):
        super().__init__()
        self.button = button

        self.image = pygame.Surface((self.w, self.h))
        self.image.fill(DARK_KHAKI)
        self.draw_cost()

        self.rect = self.image.get_rect(x=button.rect.topright[0] + 5, y=button.rect.y)

    def update(self):
        self.image.fill(DARK_KHAKI)
        self.draw_cost()

    def draw_cost(self):
        if self.button.parent is not None and\
                MenuButton.statuses[self.button.parent] != 'bought' and\
                MenuButton.statuses[self.button.indx] != 'bought':
            text = 'not available'
        elif self.button.lots > 0:
            text = str(self.button.cost)
        else:
            text = 'sold'

        f = pygame.font.SysFont(self.font, self.font_size)
        sc_text = f.render(text, True, BLUE)
        pos_text = sc_text.get_rect(center=(self.w // 2, self.h // 2))
        self.image.blit(sc_text, pos_text)


class GamePlace(pygame.Surface):
    def update(self, level):
        self.fill(bg_color)

        self.blit(level.spotlight_surf, (0, 0))
        self.blit(level.nv_surf, (0, 0))

        level.dropped_bombs.draw(self)

        level.game.ground.get_dark(int(level.how_dark))
        self.blit(level.game.ground.image, level.game.ground.rect)

        level.game.city.draw(self)

        level.jets.draw(self)
        level.rockets.draw(self)
        level.alie_jets.draw(self)
        level.pilots.draw(self)
        level.helicopters.draw(self)

        if level.aim.shoted:
            level.aim.draw_laser()

        if pygame.mouse.get_focused() and level.pos[0] < self.get_width():
            level.game.game_place.blit(level.aim.image, level.aim.rect)

        self.blit(level.laser_energy_bar, (0, 0))
        if Aim.night_vision_bought:
            self.blit(level.night_vision_energy_bar, (self.get_width() - level.night_vision_energy_bar.width, 0))


class EnergyBar(pygame.Surface):
    def __init__(self, width, height, color, value, top_value):
        self.width = width
        self.height = height
        self.color = color

        super().__init__((self.width, self.height))

        self.set_colorkey(BLACK)
        pygame.draw.rect(self, self.color,
                         (0, self.height * (1 - value / top_value), self.width, self.height * value / top_value))

    def update(self, value, top_value):
        self.fill(BLACK)
        self.set_colorkey(BLACK)
        pygame.draw.rect(self, self.color,
                         (0, self.height * (1 - value / top_value), self.width, self.height * value / top_value))


class Button(pygame.sprite.Sprite):
    size = (400, 100)
    font = 'arial'
    font_size = 36

    def __init__(self, pos, text):
        super().__init__()

        self.text = text
        self.image = pygame.Surface(self.size)
        self.image.fill(DARK_YELLOW)

        self.rect = self.image.get_rect(center=pos)

        f = pygame.font.SysFont(self.font, self.font_size)
        sc_text = f.render(self.text, True, TEXT_RED)
        pos_text = sc_text.get_rect(center=(self.image.get_width() // 2, self.image.get_height() // 2))
        self.image.blit(sc_text, pos_text)

        self.pushed = False

        self.status = 'ready'

    def update(self):
        if self.status == 'ready':
            color = DARK_GREEN
        elif self.status == 'pushed' or self.status == 'unpushed':
            color = TEXT_YELLOW
        else:
            raise ValueError('invalid button status')

        pygame.draw.rect(self.image, color, (0, 0, self.image.get_width(), self.image.get_height()), 20)

    def push(self):
        if self.status == 'ready':
            MenuButton.button_push_sound.play()
            self.pushed = True
            self.status = 'pushed'

    def unpush(self):
        MenuButton.button_unpush_sound.play()
        self.pushed = False
        self.status = 'unpushed'


class Aim(pygame.sprite.Sprite):
    homing_sight_bought = False
    night_vision_bought = False
    target_recognition_bought = False

    width = 40
    steer_time = 0.6

    dmg = 1
    energy_max = 100
    nv_energy_max = 400

    laser_sounds = [pygame.mixer.Sound("sounds/Buzzing/low_laser.wav"),
                    pygame.mixer.Sound("sounds/Buzzing/medium_laser.wav"),
                    pygame.mixer.Sound("sounds/Buzzing/high_laser.wav"),
                    pygame.mixer.Sound("sounds/Buzzing/very_high_laser.wav")]
    laser_sound_indx = 0

    steer_sound = pygame.mixer.Sound("sounds/Homing/beep.wav")
    homing_sound = pygame.mixer.Sound("sounds/Homing/homing_beep.wav")

    homing_aim_sound = pygame.mixer.Sound("sounds/ButtonClicks/Click_change_to_homing.wav")
    simple_aim_sound = pygame.mixer.Sound("sounds/ButtonClicks/Click_change_to_simple.wav")

    nv_on_sound = pygame.mixer.Sound("sounds/ButtonClicks/Click_nv_on.wav")
    nv_off_sound = pygame.mixer.Sound("sounds/ButtonClicks/Click_nv_off.wav")

    def __init__(self, main_surf, nv_surf):

        super().__init__()
        self.image = self.__draw_simple_aim()
        self.rect = self.image.get_rect(center=(0, 0))

        self.laser_point = self.pos = (0, 0)
        self.main_surf = main_surf
        self.image_laser_point = (self.laser_point[0] - self.rect.x, self.laser_point[1] - self.rect.y)

        self.energy = self.energy_max
        self.ready_to_shoot = True
        self.shoted = False

        self.aim_type = 'simple'
        self.homing_target = None
        self.homing = False
        self.start_homing_time = None
        self.homing_stage = 0

        self.nv_surf = nv_surf
        self.nv_was_on = self.nv_on = False
        self.nv_ready = True

        self.nv_energy = self.nv_energy_max

        self.laser_sound = None

    def update(self, pos, change_mode, *args, **kwargs):
        self.pos = pos
        self.move()
        if self.homing_sight_bought:
            self.__change_aim_image(change_mode)

        if self.aim_type == 'homing':
            self.steer()
        elif self.aim_type == 'simple':
            self.laser_point = self.pos
            self.__clear_aim()
        else:
            raise ValueError('invalid type of aim image')

        if self.night_vision_bought:
            self.use_night_vision()

        self.__play_shooting_sound()

    def __change_aim_image(self, change_mode):
        if change_mode:
            if self.aim_type == 'simple':
                self.image = self.__draw_homing_aim()
                self.aim_type = 'homing'
                self.homing_aim_sound.play()
            elif self.aim_type == 'homing':
                self.image = self.__draw_simple_aim()
                self.aim_type = 'simple'
                self.homing_target = None
                self.simple_aim_sound.play()
            else:
                raise ValueError('invalid type of aim image')

    @classmethod
    def __draw_simple_aim(cls):
        r = cls.width // 2
        image = pygame.Surface((2 * r, 2 * r))
        pygame.draw.rect(image, WHITE, (0, 0, 2 * r, 2 * r))
        image.set_colorkey(WHITE)
        pygame.draw.circle(image, BLACK, (r, r), 5, 1)
        pygame.draw.line(image, BLACK, (r, r + 5), (r, r * 2 - 2))
        pygame.draw.circle(image, DARK_RED, (r, r), r, 2)
        pygame.draw.circle(image, DARK_RED, (r, r), 1, 1)

        return image

    @classmethod
    def __draw_homing_aim(cls):
        width = cls.width
        image = pygame.Surface((width, width))
        pygame.draw.rect(image, WHITE, (0, 0, width, width))
        image.set_colorkey(WHITE)
        pygame.draw.rect(image, DARK_RED, (0, 0, width, width), 1)

        return image

    def move(self):
        self.rect.center = self.pos

    def steer(self):
        if self.homing_target and self.rect.colliderect(self.homing_target.rect) and not self.homing_target.exploded:
            self.laser_point = self.homing_target.rect.clip(self.rect).center
            self.image_laser_point = (self.laser_point[0] - self.rect.x, self.laser_point[1] - self.rect.y)

            if self.homing:
                self.__draw_homing()
            else:
                now = time()
                if now - self.start_homing_time < Aim.steer_time / 3:
                    self.__draw_steering()
                elif now - self.start_homing_time < Aim.steer_time / 3 * 2:
                    if self.homing_stage == 0:
                        self.homing_stage = 1
                        self.steer_sound.play()
                    self.__draw_steering()
                elif now - self.start_homing_time < Aim.steer_time:
                    if self.homing_stage == 1:
                        self.homing_stage = 2
                        self.steer_sound.play()
                    self.__draw_steering()
                else:
                    self.homing = True
                    self.__draw_homing()
                    if self.homing_stage == 2:
                        self.homing_stage = 0
                        self.homing_sound.play()

        else:
            self.laser_point = self.pos
            self.homing = False
            self.homing_target = None
            self.start_homing_time = None
            self.__draw_steering()
            self.homing_stage = 0

    def __clear_aim(self):
        if self.aim_type == 'homing':
            pygame.draw.rect(self.image, WHITE, (1, 1, 38, 38))
        elif self.aim_type == 'simple':
            pygame.draw.circle(self.image, WHITE, (35, 5), 2)
        self.image.set_colorkey(WHITE)

    def __draw_homing(self):
        self.__clear_aim()
        pygame.draw.rect(self.image, DARK_RED, (self.image_laser_point[0]-5, self.image_laser_point[1]-5, 10, 10), 1)

    def __draw_steering(self):
        self.__clear_aim()
        if self.homing_stage == 1:
            pygame.draw.line(self.image, DARK_RED,
                             ((self.image_laser_point[0] - 5) // 3 * 2,
                              (self.image_laser_point[1] - 5) // 3),
                             (40 - (40 - self.image_laser_point[0] - 5) // 3 * 2,
                              (self.image_laser_point[1] - 5) // 3))
            pygame.draw.line(self.image, DARK_RED,
                             (40 - (40 - self.image_laser_point[0] - 5) // 3,
                              (self.image_laser_point[1] - 5) // 3 * 2),
                             (40 - (40 - self.image_laser_point[0] - 5) // 3,
                              40 - (40 - self.image_laser_point[1] - 5) // 3 * 2))
            pygame.draw.line(self.image, DARK_RED,
                             (40 - (40 - self.image_laser_point[0] - 5) // 3 * 2,
                              40 - (40 - self.image_laser_point[1] - 5) // 3),
                             ((self.image_laser_point[0] - 5) // 3 * 2,
                              40 - (40 - self.image_laser_point[1] - 5) // 3))
            pygame.draw.line(self.image, DARK_RED,
                             ((self.image_laser_point[0] - 5) // 3,
                              40 - (40 - self.image_laser_point[1] - 5) // 3 * 2),
                             ((self.image_laser_point[0] - 5) // 3,
                              (self.image_laser_point[1] - 5) // 3 * 2))

        elif self.homing_stage == 2:
            pygame.draw.line(self.image, DARK_RED,
                             (self.image_laser_point[0] - 5,
                              (self.image_laser_point[1] - 5) // 3 * 2),
                             (self.image_laser_point[0] + 5,
                              (self.image_laser_point[1] - 5) // 3 * 2))
            pygame.draw.line(self.image, DARK_RED,
                             (40 - (40 - self.image_laser_point[0] - 5) // 3 * 2,
                              self.image_laser_point[1] - 5),
                             (40 - (40 - self.image_laser_point[0] - 5) // 3 * 2,
                              self.image_laser_point[1] + 5))
            pygame.draw.line(self.image, DARK_RED,
                             (self.image_laser_point[0] - 5,
                              40 - (40 - self.image_laser_point[1] - 5) // 3 * 2),
                             (self.image_laser_point[0] + 5,
                              40 - (40 - self.image_laser_point[1] - 5) // 3 * 2))
            pygame.draw.line(self.image, DARK_RED,
                             ((self.image_laser_point[0] - 5) // 3 * 2,
                              self.image_laser_point[1] + 5),
                             ((self.image_laser_point[0] - 5) // 3 * 2,
                              self.image_laser_point[1] - 5))

    def use_night_vision(self):
        if self.nv_on:
            self.nv_energy -= 1
            if not self.nv_was_on:
                self.nv_on_sound.play()
                self.nv_was_on = True

            if self.nv_energy < 0:
                self.nv_energy = 0

            if self.nv_energy == 0:
                self.nv_ready = False
        else:
            if self.nv_was_on:
                self.nv_off_sound.play()
                self.nv_was_on = False

        self.nv_surf.update(self.nv_on, self.pos, self.image.get_width()//2, self.aim_type)

        if not self.nv_on and self.nv_energy < self.nv_energy_max:
            self.__charge_nv_energy()

    def __charge_nv_energy(self):
        self.nv_energy += 0.5

        if self.nv_energy > self.nv_energy_max:
            self.nv_energy = self.nv_energy_max

        if self.nv_energy >= self.nv_energy_max // 10:
            self.nv_ready = True

    def shoot_laser(self):
        energy = self.energy
        if self.ready_to_shoot:
            self.energy -= self.dmg

        if self.ready_to_shoot and self.energy < 0:
            self.ready_to_shoot = False
            self.energy = 0

        return energy - self.energy

    def charge_laser_energy(self):
        if self.energy < self.energy_max:
            self.energy += self.energy_max // 100
            if self.energy > self.energy_max:
                self.energy = self.energy_max

        if not self.ready_to_shoot and (self.energy >= self.dmg * 70 or self.energy == self.energy_max):
            self.ready_to_shoot = True

    def draw_laser(self):
        w, h = self.main_surf.get_size()
        pygame.draw.polygon(self.main_surf, RED, [self.laser_point, (w // 2 - 3, h * 1.3), (w // 2 + 3, h * 1.3)])

    def __play_shooting_sound(self):
        if self.shoted:
            if self.laser_sound is None:
                self.laser_sound = self.laser_sounds[self.laser_sound_indx]
                self.laser_sound.play()
        elif self.laser_sound is not None:
            self.laser_sound.stop()
            self.laser_sound = None

    def inflict_damage(self, target):
        if self.ready_to_shoot:
            return target.get_damage(self.dmg)
        else:
            return 0

    def recognise(self, target):
        if type(target) == AllieJet or type(target) == Helicopter and target.alie:
            self.__draw_target_mark('alie')
        elif isinstance(target, (Jet, Helicopter)):
            self.__draw_target_mark('enemy')

    def __draw_target_mark(self, target_type):
        if target_type == 'alie':
            color = DARK_GREEN
        elif target_type == 'enemy':
            color = RED
        else:
            raise ValueError('Invalid type of target')

        pygame.draw.circle(self.image, color, (35, 5), 2)


class FlyingObject(pygame.sprite.Sprite):
    def __init__(self, start_pos, hp, speed, expl_rad, points, image, sizex, width, group, del_white=False):
        super().__init__()

        self.strength = self.hp = self.hp_previous = hp
        self.speed = speed
        self.expl_rad = expl_rad
        self.expl_rad_now = 0
        self.points = points
        self.del_white = del_white

        self.image = pygame.image.load(image).convert_alpha()
        sizey = sizex * self.image.get_height() // self.image.get_width()
        self.image = pygame.transform.scale(self.image, (sizex, sizey))
        if self.del_white:
            self.image.set_colorkey(WHITE)

        self.rect = self.image.get_rect(center=start_pos)

        self.direction = 'right'
        if start_pos[0] != 0:
            self.turn_around()

        self.width = width
        self.exploded = False

        self.add(group)

    def update(self, *args, **kwargs):
        if self.hp == 0:
            self.explode()
        self.move()

    def move(self):
        if self.rect.x < self.width and self.rect.topright[0] > 0:
            self.rect.x += self.speed
        else:
            self.kill()

    def get_damage(self, dmg):
        if self.hp > 0:
            self.hp -= dmg
            if self.hp <= 0:
                self.hp = 0
                return self.points
            else:
                return 0
        else:
            self.hp = 0
            return 0

    def explode(self):
        self.speed = 1 if self.direction == 'right' else -1

        if self.expl_rad_now == 0:
            self.exploded = True
            self.image = pygame.Surface((self.expl_rad * 2, self.expl_rad * 2))
            self.image.set_colorkey(BLACK)

            self.rect = self.image.get_rect(center=self.rect.center)

        self.expl_rad_now += 1
        pygame.draw.circle(self.image, RED, (self.expl_rad, self.expl_rad), self.expl_rad_now)
        pygame.draw.circle(self.image, YELLOW, (self.expl_rad, self.expl_rad), self.expl_rad_now // 2)

        if self.expl_rad_now == self.expl_rad:
            self.kill()

    def turn_around(self):
        self.image = pygame.transform.flip(self.image, True, False)
        if self.del_white:
            self.image.set_colorkey(WHITE)

        self.speed = -self.speed
        self.direction = 'left' if self.direction == 'right' else 'right'


class Jet(FlyingObject):
    picture = 'images/jet.png'

    hp = 100
    expl_rad = 50
    points = 200
    sizex = 20

    min_indent = 20
    max_indent = 70

    explode_sounds = [pygame.mixer.Sound("sounds/Explosions/Big_explosion_1.wav"),
                      pygame.mixer.Sound("sounds/Explosions/Big_explosion_1.wav")]

    def __init__(self, start_pos, speed, bomb_dmg, moves, ground_lvl, width, group):
        super().__init__(start_pos=start_pos,
                         hp=self.hp,
                         speed=speed,
                         expl_rad=self.expl_rad,
                         points=self.points,
                         image=self.picture,
                         sizex=self.sizex,
                         width=width,
                         group=group)

        self.moves = moves
        self.bombs = rnd(1, moves // 2)
        self.house_to_bomb = None
        self.bomb_dmg = bomb_dmg
        self.indent = None

        self.ground_lvl = ground_lvl

    def update(self, *args, **kwargs):
        if self.hp == 0:
            if self.expl_rad_now == 0:
                self._act_with_chance(3, self.catapult_pilot, args[2])  # args[2] == pilots
            self.explode()

        self.move()
        self.__bombard(args[0], args[1])

    def move(self):
        self._approach_to_target()
        super().move()

    def _approach_to_target(self):
        if self.indent is None:
            self.indent = rnd(self.min_indent, self.max_indent)

        if self.moves > 1 and (self.rect.x > self.width - self.indent and self.direction == 'right' or
                               self.rect.topright[0] < self.indent and self.direction == 'left'):
            self.turn_around()
            self.moves -= 1
            self.indent = None

    def get_damage(self, dmg):
        points = super().get_damage(dmg)
        if self.hp != 0 and\
                any(map(lambda x: int(self.hp * x) <= self.strength < int(self.hp_previous * x), (1.34, 2, 4))):
            self._act_with_chance(3, self.turn_around)
        self.hp_previous = self.hp
        return points

    def explode(self):
        if self.expl_rad_now == 0:
            self.moves = 0
        super().explode()

    @staticmethod
    def _act_with_chance(chance, act, *args):
        x = rnd(1, chance)
        if x == 1:
            act(*args)
        return x == 1

    def __bombard(self, city, dropped_bombs):
        if self.house_to_bomb is None and self.bombs >= self.moves and len(city):
            self.house_to_bomb = choice([house for house in city])
        if self.house_to_bomb and self.house_to_bomb.rect.x+10 < self.rect.centerx < self.house_to_bomb.rect.right-10:
            self.__drop_bomb(self.house_to_bomb, dropped_bombs)
            self.house_to_bomb = None

    def __drop_bomb(self, target, group):
        Bomb(self.rect.midbottom, target, self.bomb_dmg).add(group)
        self.bombs -= 1

    def _shoot_rocket(self, target, group):
        Rocket(start_pos=self.rect.center,
               start_direction=self.direction,
               target=target,
               width=self.width,
               ground_lvl=self.ground_lvl,
               group=group)

    def catapult_pilot(self, group):
        Pilot(pos=self.rect.center, land_lvl=self.ground_lvl, w8_time=30).add(group)

    def __del__(self):
        if self.exploded:
            self.explode_sounds[rnd(0, 1)].play()


class AllieJet(Jet):
    time_service = 10
    time_out = time() - time_service

    points = -1000

    scream = pygame.mixer.Sound("sounds/PilotScreams/friendly_fire.wav")
    mayday_scream = pygame.mixer.Sound("sounds/PilotScreams/mayday.wav")

    def __init__(self, start_pos, speed, ground_lvl, width, group):
        super().__init__(start_pos=start_pos,
                         speed=speed,
                         bomb_dmg=None,
                         moves=2,
                         ground_lvl=ground_lvl,
                         width=width,
                         group=group)

        self.rockets = 4
        self.armed_missiles = 0
        self.moves = rnd(self.rockets, self.rockets * 3)
        self.shoot_data = self.__choose_place_to_shoot()

        del self.bombs
        del self.house_to_bomb
        del self.bomb_dmg

    def update(self, *args, **kwargs):
        if self.hp == 0:
            if self.expl_rad_now == 0:
                self._act_with_chance(3, self.catapult_pilot, args[3])  # args[3] == pilots
            self.explode()

        if self.rockets == 0:
            self.moves = 1

        self.__arm_missile()
        self.__shoot_rockets(args[0], args[1], args[2])  # args[0] == missiles, args[1] == jets, args[2] == helicopters

        self.move()

    def __shoot_rockets(self, missiles, jets, helicopters):
        targets = set(jets) | set(filter(lambda x: not x.alie, helicopters))
        not_exploded_targets = set(target for target in targets if not target.exploded)
        already_shoted_targets = set(missile.target for missile in missiles)
        free_targets = not_exploded_targets - already_shoted_targets

        if self.armed_missiles and len(free_targets):
            target = choice([target for target in set(targets) - set(missile.target for missile in missiles)])
            Rocket(self.rect.center, self.direction, target, self.width, self.ground_lvl, missiles)
            self.armed_missiles -= 1
            self.rockets -= 1

    def __choose_place_to_shoot(self):
        shoot_place = []
        for i in range(self.rockets):
            move_to_shoot = rnd(1, self.moves)
            x_to_shoot = rnd(self.max_indent, self.width - self.max_indent)
            shoot_place.append((move_to_shoot, x_to_shoot))
        return shoot_place

    def __arm_missile(self):
        if self.rockets:
            for i, data in enumerate(self.shoot_data):
                move_n, x = data
                if self.moves == move_n and (self.rect.x > x and self.direction == 'right' or
                                             self.rect.topright[0] < x and self.direction == 'left'):
                    self.armed_missiles += 1
                    self.shoot_data.pop(i)

    def catapult_pilot(self, group):
        Pilot(pos=self.rect.center, land_lvl=self.ground_lvl, w8_time=30, alie=True).add(group)
        self.scream.stop()
        self.mayday_scream.play()

    def get_damage(self, dmg):
        points = FlyingObject.get_damage(self, dmg)
        if any(map(lambda x: int(self.hp * x) <= self.strength < int(self.hp_previous * x), (1.34, 2, 4))):
            if self._act_with_chance(3, self.turn_around):
                self.scream.stop()
                self.scream.play()

        self.hp_previous = self.hp

        return points

    def __del__(self):
        super().__del__()
        AllieJet.time_out = time()


class Helicopter(FlyingObject):
    hp = 50
    speed = 1
    expl_rad = 30
    points = 100
    picture = 'images/helicopter.png'
    sizex = 20

    explode_sounds = [pygame.mixer.Sound("sounds/Explosions/Medium_explosion_1.wav"),
                      pygame.mixer.Sound("sounds/Explosions/Medium_explosion_2.wav")]

    def __init__(self, pilot, ground_lvl, game_w, group, alie=False):
        self.mission = pilot
        self.fly_height = ground_lvl - 100
        self.ground_lvl = ground_lvl
        self.speedy = 0
        self.going_back = False
        self.pilot_on_board = False
        self.alie = alie

        start_pos = (0 if pilot.rect.centerx < game_w // 2 else game_w, self.fly_height)
        super().__init__(start_pos=start_pos,
                         hp=self.hp,
                         speed=self.speed,
                         expl_rad=self.expl_rad,
                         points=self.points,
                         image=self.picture,
                         sizex=self.sizex,
                         width=game_w,
                         group=group,
                         del_white=True)

        self.image.set_colorkey(WHITE)

        if self.alie:
            self.points = - self.points * 5

    def move(self):
        self.__check_direction()

        # moving
        if self.speedy:
            self.rect.y += self.speedy
        super().move()

    def __check_direction(self):
        if self.expl_rad_now == 0:

            if not self.going_back and self.mission.dead_or_captured:
                self.going_back = True
                if self.speedy:
                    self.__take_off()
                else:
                    self.turn_around()

            if self.speedy == 0 and self.rect.centerx == self.mission.rect.centerx:
                self.__land()

            if self.rect.collidepoint(self.mission.rect.centerx, self.mission.rect.centery):
                self.__pick_pilot()
                self.__take_off()

            if self.speedy and self.going_back and self.rect.centery == self.fly_height:
                self.speedy = 0

    def __land(self):
        self.speed = 0
        self.speedy = 1

    def __pick_pilot(self):
        if self.alie:
            self.points += self.mission.points
        else:
            self.points += abs(self.mission.points) // 2
        self.pilot_on_board = True
        self.mission.picked_up = True
        self.mission.kill()
        self.going_back = True

    def __take_off(self):
        self.speedy = -self.speedy
        self.speed = 1 if self.direction == 'right' else -1
        self.turn_around()

    def __del__(self):
        if self.alie:
            AllieJet.time_out = time()

        if self.exploded:
            self.explode_sounds[rnd(0, 1)].play()


class Rocket(FlyingObject):
    hp = 10
    speed = 5
    expl_rad = 25
    points = -50
    picture = 'images/missile.png'
    sizex = 9

    dmg = 100
    dangle = 4

    def __init__(self, start_pos, start_direction, target, width, ground_lvl, group):
        self.angle = 0
        super().__init__(start_pos=start_pos,
                         hp=self.hp,
                         speed=self.speed,
                         expl_rad=self.expl_rad,
                         points=self.points,
                         image=self.picture,
                         sizex=self.sizex,
                         width=width,
                         group=group)

        self.image = pygame.transform.rotate(self.image, 45)
        self.picture = self.image

        self.ground_lvl = ground_lvl

        self.target = target
        self.armed = True
        self.exploded = False

        self.direction = 'right'
        if self.direction != start_direction:
            self.turn_around()

        self.precision_pos_x, self.precision_pos_y = self.rect.center

    def update(self, *args, **kwargs):
        if self.hp == 0:
            self.exploded = True
            self.armed = False

        if self.exploded:
            self.explode()

        self.rotate()
        self.move()

    def blow_up(self):
        if self.armed and not self.exploded:
            self.armed = False
            self.kill()
            return self.target.get_damage(self.dmg)

    def move(self):
        if self.rect.bottom > self.ground_lvl:
            self.kill()

        self.precision_pos_x -= self.speed * cos(radians(self.angle))
        self.precision_pos_y += self.speed * sin(radians(self.angle))

        self.rect.centerx = int(self.precision_pos_x)
        self.rect.centery = int(self.precision_pos_y)

    def rotate(self):
        if not self.exploded:
            self.__check_rotate_direction()
            self.__check_direction()

            self.angle += self.dangle
            self.image = pygame.transform.rotate(self.picture, self.angle)

    def __check_direction(self):
        self.direction = 'right' if -90 < self.angle < 90 or self.angle < -270 or self.angle > 270 else 'left'

    def __check_rotate_direction(self):
        if self.angle > 360:
            self.angle -= 360
        elif self.angle < -360:
            self.angle += 360

        if (self.target.rect.centerx - self.rect.centerx) * sin(radians(self.angle)) \
                + (self.target.rect.centery - self.rect.centery) * cos(radians(self.angle)) < 0:
            self.dangle = -abs(self.dangle)
        else:
            self.dangle = abs(self.dangle)

    def turn_around(self):
        super().turn_around()
        self.speed = abs(self.speed)
        self.angle += 180

    def explode(self):
        super().explode()
        self.speed = abs(self.speed)

    def __del__(self):
        if self.exploded:
            Bomb.explode_sounds[rnd(0, 1)].play()


class DroppedObject(pygame.sprite.Sprite):
    speed = 1

    def __init__(self, pos, size, image, land_lvl, hp, points):
        super().__init__()

        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect(center=pos)

        self.land = land_lvl

        self.points = points
        self.hp = hp

    def update(self, *args, **kwargs):
        if self.rect.bottom < self.land:
            self.rect.y += self.speed

    def get_damage(self, dmg):
        if self.hp > 0:
            self.hp -= dmg
            if self.hp <= 0:
                self.hp = 0
                return self.points
            else:
                return 0
        else:
            return 0


class Bomb(DroppedObject):
    size = (5, 6)
    picture = 'images/bomb.jpg'
    hp = 10
    points = 50
    expl_rad = 25

    explode_sounds = [pygame.mixer.Sound("sounds/Explosions/Small_explosion_1.wav"),
                      pygame.mixer.Sound("sounds/Explosions/Small_explosion_2.wav")]

    def __init__(self, pos, house, dmg):
        super().__init__(pos=pos,
                         size=self.size,
                         image=self.picture,
                         land_lvl=house.rect.top,
                         hp=self.hp,
                         points=self.points)

        self.dmg = dmg
        self.house = house
        self.crashed = False
        self.expl_rad_now = 0

    def update(self):
        self.rect.y += self.speed
        self.crash()

    def crash(self):
        if self.hp == 0:
            if not self.crashed:
                self.crashed = True
            self.explode()
        if self.expl_rad_now == self.expl_rad:
            self.kill()

    def blow_up(self):
        if self.speed:
            self.speed = 0
        if not self.crashed:
            self.explode()

            if self.expl_rad_now == self.expl_rad:
                self.kill()
                return self.house.get_damage(self.dmg)
            else:
                return 0
        else:
            return 0

    def explode(self):
        if self.expl_rad_now == 0:
            self.image = pygame.Surface((self.expl_rad * 2, self.expl_rad * 2))
            self.image.set_colorkey(BLACK)

            self.rect = self.image.get_rect(center=self.rect.midbottom)

        self.expl_rad_now += 1
        pygame.draw.circle(self.image, RED, (self.expl_rad, self.expl_rad), self.expl_rad_now)
        pygame.draw.circle(self.image, YELLOW, (self.expl_rad, self.expl_rad), self.expl_rad_now // 2)

    def __del__(self):
        self.explode_sounds[rnd(0, 1)].play()


class Pilot(DroppedObject):
    size = (6, 8)
    picture = 'images/paratrooper.png'
    hp = 10
    points = -500

    def __init__(self, pos, land_lvl, w8_time, alie=False):
        super().__init__(pos=pos,
                         size=self.size,
                         image=self.picture,
                         land_lvl=land_lvl,
                         hp=self.hp,
                         points=self.points)

        self.captured_timer = -1
        self.help_signal_timer = -1
        self.w8_time = w8_time
        self.landed = False
        self.dead_or_captured = False
        self.picked_up = False

        self.alie = alie
        if self.alie:
            self.points *= 5

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        if self.hp == 0:
            self.dead_or_captured = True
            self.kill()

        if self.speed > 0 and self.rect.bottom >= self.land:
            self.speed = 0
            self.landed = True
            self.image = pygame.image.load('images/person.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (7, 7))
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
            self.captured_timer = self.w8_time * 60
            self.help_signal_timer = (self.w8_time - rnd(3, self.w8_time - 5)) * 60
            if self.alie:
                self.captured_timer *= 3

        self.captured_timer -= 1
        self.help_signal_timer -= 1

    def get_captured(self):
        self.dead_or_captured = True
        self.kill()
        if self.alie:
            return 0
        else:
            return -self.points

    def __del__(self):
        if self.alie and not self.picked_up:
            AllieJet.time_out = time()


class LandObject(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.dark = None
        self.im = None

    def get_dark(self, how_dark):
        self.dark = pygame.Surface(self.im.get_size())
        self.dark.set_alpha(how_dark)

        self.image = self.im.copy()
        self.image.blit(self.dark, (0, 0))


class Ground(LandObject):
    picture = 'images/ground.jpg'

    def __init__(self, h):
        super().__init__()
        self.im = pygame.image.load(self.picture)
        self.image = self.im.copy()
        if self.dark is not None:
            self.image.blit(self.dark, (0, 0))
        self.rect = self.image.get_rect(x=0, y=h - self.image.get_height())


class HouseBlock(pygame.sprite.Sprite):
    picture = 'images/house_block.jpg'
    size_x = 25
    points = 500

    def __init__(self, flour, strength):
        super().__init__()

        self.strength = strength
        self.image = pygame.image.load(self.picture)

        scale_y = self.size_x * self.image.get_height() // self.image.get_width()
        scale = (self.size_x, scale_y)
        self.image = pygame.transform.scale(self.image, scale)

        self.rect = self.image.get_rect(x=0, y=self.image.get_height() * flour)


class House(LandObject):
    points = 2000

    def __init__(self, x, ground, flours, block_strength, group):
        super().__init__()

        self.blocks = [HouseBlock(flour, block_strength) for flour in range(flours)]
        self.im = pygame.Surface((self.blocks[0].image.get_width(),
                                  self.blocks[0].image.get_height() * flours))
        for block in self.blocks:
            self.im.blit(block.image, block.rect)

        self.image = self.im.copy()
        if self.dark is not None:
            self.image.blit(self.dark, (0, 0))

        self.rect = self.image.get_rect(bottomleft=(x, ground))

        self.damage = 0

        self.add(group)

    def get_damage(self, dmg):
        res = 0
        self.damage += dmg
        while len(self.blocks) and self.damage >= self.blocks[0].strength:
            self.damage -= self.blocks[0].strength
            self.blocks.pop()
            if len(self.blocks) == 0:
                self.kill()
                res -= self.points
            else:
                self.im = pygame.Surface((self.blocks[0].image.get_width(),
                                          self.blocks[0].image.get_height() * len(self.blocks)))
                for block in self.blocks:
                    self.im.blit(block.image, block.rect)
                self.rect = self.im.get_rect(bottomleft=self.rect.bottomleft)
                res -= HouseBlock.points

        return res


class City(pygame.sprite.Group):
    new_blocks = 180
    max_flours = 16
    pos_start = 100
    block_strength = 25

    def __init__(self, ground_lvl, pos_end):
        super().__init__()

        houses = [1] * ((pos_end - self.pos_start) // HouseBlock.size_x)

        while self.new_blocks > 0:
            indx = rnd(0, len(houses) - 1)
            if houses[indx] <= self.max_flours:
                houses[indx] += 1
                self.new_blocks -= 1

        for i, x in enumerate(range(self.pos_start, pos_end, HouseBlock.size_x)):
            House(x, ground_lvl, houses[i], self.block_strength, self)


class SpotLightSurf(pygame.Surface):
    def __init__(self, size, number, ground_lvl, how_dark):
        super().__init__(size)

        self.ground_lvl = ground_lvl
        self.number = number
        self.spots = list(range(size[0] // 6, size[0], size[0] // 6))
        self.spotlights = []
        for i in range(number):
            self.__add_spotlight(self.spots.pop(rnd(0, len(self.spots)-1)), self.ground_lvl)
        for spotlight in self.spotlights:
            self.blit(spotlight.image, spotlight.rect)

        self.set_alpha(how_dark)

    def update(self, number, how_dark, rotate_time):
        self.set_alpha(how_dark)
        self.fill(BLACK)

        if number != self.number:
            for i in range(number - self.number):
                self.__add_spotlight(self.spots.pop(rnd(0, len(self.spots)-1)), self.ground_lvl)

            self.number = number

        for spotlight in self.spotlights:
            spotlight.update(rotate_time)

            self.blit(spotlight.image, spotlight.rect)

    def __add_spotlight(self, x, y):
        self.spotlights.append(SpotLight(x, y))


class SpotLight(pygame.sprite.Sprite):
    power = 6
    light_top_diameter = 30

    def __init__(self, pos_x, y):
        super().__init__()

        self.image = pygame.Surface((y * 2, y))
        self.rect = self.image.get_rect(midbottom=(pos_x, y))

        self.spot = (y, y)

        self.top_left_point = [y - self.light_top_diameter // 2, 0]
        self.top_right_point = [y + self.light_top_diameter // 2, 0]
        self.top_center_point = [y, 0]

        self.positions_x = tuple(range(self.light_top_diameter // 2 + (2 * y - self.light_top_diameter) // 5,
                                       y * 2 - self.light_top_diameter // 2 - (2*y - self.light_top_diameter) // 5 + 1,
                                       (2 * y - self.light_top_diameter) // 5))
        self.destination_x = None

        self.__draw_light()
        self.image.set_colorkey(BLACK)

    def update(self, change_position):
        if change_position and rnd(1, 20) == 1:
            self.destination_x = self.positions_x[rnd(0, 3)]

        if self.destination_x:
            self.image.fill(BLACK)
            self.__rotate_to_position()
            self.__draw_light()
            self.image.set_colorkey(BLACK)

    def __draw_light(self):
        pygame.draw.polygon(self.image, SPOTLIGHT_YELLOW, (self.spot, self.top_left_point, self.top_right_point))

    def __rotate_to_position(self):
        if self.top_center_point[0] != self.destination_x:
            self.__rotate('left' if self.top_center_point[0] > self.destination_x else 'right')
        else:
            self.destination_x = None

    def __rotate(self, direction):
        points = [self.top_left_point, self.top_center_point, self.top_right_point]
        for i in range(len(points)):
            if direction == 'left':
                points[i][0] -= 1
            elif direction == 'right':
                points[i][0] += 1
            else:
                raise ValueError("Invalid rotation direction")


class NightVisionSurface(pygame.Surface):
    def __init__(self, size):
        super().__init__(size)
        self.set_colorkey(BLACK)

    def __draw_nv(self, pos, r, aim_type):
        if aim_type == 'simple':
            pygame.draw.circle(self, WHITE, pos, r)
        elif aim_type == 'homing':
            pygame.draw.rect(self, WHITE, (pos[0]-r, pos[1]-r, r*2, r*2))
        else:
            raise ValueError('Invalid aim type')

    def update(self, nv_on, pos, r, aim_type):
        self.fill(BLACK)
        self.set_colorkey(BLACK)
        if nv_on:
            self.__draw_nv(pos, r, aim_type)
