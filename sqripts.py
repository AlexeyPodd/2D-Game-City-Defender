from sprites import *
from sys import exit


class Game:
    # Screen settings
    W, H = 1280, 720
    FPS = 60
    clock = pygame.time.Clock()

    instructions_1 = [
        'Greetings. So you are that "experienced operator of futuristic stuff", huh?',
        "",
        'Your task is to prevent the destruction of the city.'
        ' Shoot down enemy jets and bombs they drop.',
        "",
        "Keep in mind, sometimes pilots will have time to eject before the plane explodes."
        " Don't kill them, the government will allocate",
        "additional funding to our project for their capturing."
        " It's our job to catch them, your job is to make sure those bastards stay in town.",
        "But if one of this sons of bitches did manage to get into the evacuation transport,"
        " you'd better shoot it down.",
        "",
        'The more efficiently you work, the more money will be allocated to our project.'
        ' And the more money we have, the more',
        'expensive toys we can provide you. I will leave you a table of how much money we were promised'
        ' to allocate for what purposes',
        "and instructions for the equipment.",
        "",
        "But there is also a downside - we have pledged to ensure the complete safety of the city,"
        " so we will compensate",
        "for any damage from our budget.",
        "",
        "We will be in the city all the time, there may not be a connection with you -"
        " so I will give you advice now. If it gets really hard,",
        "focus on protecting the city, don't try to get more money."
        " Because if there is nothing left of the city, our project ",
        "will be shut down, and it is unlikely that anyone will ever see us."
        " But if we manage, most likely all debts will be written off to us.",
        ""
    ]

    instructions_2 = [
        "Sure thing!",
        "...",
        "I'm sorry, I seem to have lost them.",
        "Well, there is nothing complicated. Aim and press LMB to shoot."
        " Switching the sight to homing - Q. Turn off the music - M.",
        "Well, night vision mode - RMB. But I would advise you to just buy more spotlights.",
        "Laser charge indicator on the left, night vision (if you buy it) - on the right.",
        "",
        "As for payment - we were promised to pay 200 for each plane,"
        " a helicopter - half as much. For a captured pilot they give 500,",
        "the field of how we catch him, of course. If we don’t make it in time,"
        " and a helicopter takes him away, they will give another 250 ",
        "to the usual 100 for shooting this helicopter down. But if you kill the pilot when "
        "it is possible to take him prisoner, you will have",
        "to pay a fine of -500. Downing of an allied aircraft -1000. Allied pilot kill"
        " -2500, building damage -500, total demolition -2000.",
        "",
        "Looks like I didn't forget anything.",
        "",
        "Don't let us down - we're all counting on you!",
        "Well, a city dwellers too."
]

    def __init__(self):
        # Creating game window
        self.sc = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption("city_defender")
        pygame.display.set_icon(pygame.image.load("icon.ico"))

        self.ground = Ground(self.H)
        self.game_w = self.ground.image.get_width()
        self.ground_lvl = self.H - self.ground.image.get_height()

        # Number of current level
        self.level_number = 1

        # Game score
        self.score = 0

        # Events
        self.jet_event = pygame.USEREVENT
        self.jet_periodicity = 10_000
        self.spotlight_rotate_event = pygame.USEREVENT + 1
        self.spotlight_rotate_periodicity = 2_000

        # Stuff for buying
        self.spotlights = 0
        self.fighter_bought = False
        self.pilot_bought = False

        # How dark will be at night
        self.darkness_limit = 230 - self.spotlights * SpotLight.power

        # Creating game and menu areas
        self.game_place = GamePlace((self.game_w, self.H))
        self.menu = Menu((self.W, self.H), self.game_w, self.score, self)

        # Building city
        self.city = City(ground_lvl=self.H - self.ground.image.get_height(),
                         pos_end=self.game_w - 100)

    def run_level(self):
        level = Level(self)

        pygame.mouse.set_visible(False)

        # Cycle of game level
        while self.menu.info.time < 300 and len(self.city):
            level.process_events()
            level.process_interactions()

            # Drawing stuff on places
            self.menu.update(self.score)
            self.game_place.update(level)

            self.__draw_all_surfaces()

            pygame.display.update()

            self.clock.tick(self.FPS)

        else:
            self.level_number += 1
            self.jet_periodicity //= 1.15

    def show_transit_screen(self):
        pygame.mouse.set_visible(True)

        if self.level_number < 11:
            # update level number in menu info
            self.menu.info.level_number = self.level_number

            # Timers of events
            pygame.time.set_timer(self.jet_event, rnd(self.jet_periodicity // 2, self.jet_periodicity))
            pygame.time.set_timer(self.spotlight_rotate_event, self.spotlight_rotate_periodicity)

        f = pygame.font.SysFont('arial', 48)
        text1 = ('You won!' if len(self.city) else 'You lose') if self.level_number == 11 or not len(self.city) else \
            'Day ' + str(self.level_number)
        sc_text_1 = f.render(text1, True, TEXT_GREEN)
        sc_text_2 = f.render('Score: ' + str(self.score), True, TEXT_BLUE)
        pos1 = sc_text_1.get_rect(center=(self.W // 2, self.H // 2 - 60))
        pos2 = sc_text_2.get_rect(center=(self.W // 2, self.H // 2 + 60))

        button = Button((self.W // 2, self.H - self.H // 4),
                        'Exit' if self.level_number == 11 or not len(self.city) else 'Start this day')
        while button.status != 'unpushed':
            pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

                if button.rect.collidepoint(pos) and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    button.push()
                if button.pushed and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    button.unpush()

            button.update()

            self.sc.fill(DARK_KHAKI)
            self.sc.blit(sc_text_1, pos1)
            self.sc.blit(sc_text_2, pos2)
            self.sc.blit(button.image, button.rect)

            pygame.display.update()
            self.clock.tick(self.FPS)

    def instruct_player(self):
        self.__show_instruction_screen(self.instructions_1, 'Can i see those papers?')
        self.__show_instruction_screen(self.instructions_2, 'Got it!')

    def __show_instruction_screen(self, list_of_instructions, button_text):
        pygame.mouse.set_visible(True)

        button = Button((self.W // 2, self.H - self.H // 5), button_text)
        while button.status != 'unpushed':
            pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

                if button.rect.collidepoint(pos) and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    button.push()
                if button.pushed and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    button.unpush()

            button.update()

            self.sc.fill(DARK_KHAKI)
            self.__print_instructions(list_of_instructions)
            self.sc.blit(button.image, button.rect)

            pygame.display.update()
            self.clock.tick(self.FPS)

    def __print_instructions(self, list_of_instructions):
        f_instruction = pygame.font.SysFont('arial', 22)

        sc_instruction = [f_instruction.render(text, True, TEXT_YELLOW) for text in list_of_instructions]
        pos_instruction = []
        pos = 15
        for sc in sc_instruction:
            pos_instruction.append(sc.get_rect(topleft=(self.W // 10, pos)))
            pos += 23

        for i in range(len(sc_instruction)):
            self.sc.blit(sc_instruction[i], pos_instruction[i])

    def __draw_all_surfaces(self):
        self.sc.blit(self.menu, (self.game_w, 0))
        self.sc.blit(self.game_place, (0, 0))


class Level:
    background_music = {x: f'sounds/BackgroundMusic/{x}.mp3' for x in range(1, 11)}
    vol = 0.5

    def __init__(self, game):
        self.game = game

        # Groups of jets, bombs, catapulted pilots, helicopters, missiles and alie jets
        self.jets = pygame.sprite.Group()
        self.dropped_bombs = pygame.sprite.Group()
        self.pilots = pygame.sprite.Group()
        self.helicopters = pygame.sprite.Group()
        self.rockets = pygame.sprite.Group()
        self.alie_jets = pygame.sprite.Group()

        # Start dusk
        self.how_dark = 0

        # Surface for spotlights and dusk
        # (overlay translucent black surface with or without spotlights on game area)
        self.spotlight_surf = SpotLightSurf((game.game_w, game.H), self.game.spotlights,
                                            self.game.ground_lvl, int(self.how_dark))
        self.rotate_spotlights_time = False

        # Surface for night vision aim mode
        self.nv_surf = NightVisionSurface((game.game_w, game.H))

        # Preparing cursor
        self.aim = Aim(main_surf=self.game.game_place, nv_surf=self.nv_surf)
        self.fl_change_aim = False

        # Cursor position
        self.pos = None
        self.pressed = None

        # Energy indicators
        self.laser_energy_bar = EnergyBar(3, self.game.H, RED, self.aim.energy, self.aim.energy_max)
        self.night_vision_energy_bar = EnergyBar(3, self.game.H, GREEN,
                                                 self.aim.nv_energy, self.aim.nv_energy_max)

        pygame.mixer.music.load(self.background_music[self.game.level_number])
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(self.vol)

        self.game.menu.info.reset_timer()

    def process_events(self):
        self.pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

            # Music pause / unpause
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.fl_change_aim = True

                if event.key == pygame.K_m:
                    if pygame.mixer.music.get_volume() != 0:
                        pygame.mixer.music.set_volume(0)
                    else:
                        pygame.mixer.music.set_volume(self.vol)

            for button in self.game.menu.buttons:
                if button.rect_game.collidepoint(self.pos) and event.type == pygame.MOUSEBUTTONDOWN \
                        and event.button == 1:
                    self.game.score -= button.push()
                if button.pushed and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    button.unpush(self.game.score)

            if event.type == self.game.jet_event:
                Jet(start_pos=(choice([0, self.game.game_w]),
                               rnd(10, self.game.H - self.game.ground.image.get_height() - 200)),
                    speed=rnd(2, 4),
                    bomb_dmg=rnd(25, 100),
                    moves=rnd(2, 6),
                    ground_lvl=self.game.ground_lvl,
                    width=self.game.game_w,
                    group=self.jets)

            if event.type == self.game.spotlight_rotate_event:
                self.rotate_spotlights_time = True

    def process_interactions(self):
        if self.game.fighter_bought and self.game.pilot_bought and not len(self.alie_jets) and \
                not bool(len(set(filter(lambda x: x.alie, self.pilots)))
                         + len(set(filter(lambda x: x.alie, self.helicopters)))) \
                and time() - AllieJet.time_out > AllieJet.time_service:
            AllieJet(start_pos=(choice([0, self.game.game_w]),
                                rnd(10, self.game.H - self.game.ground.image.get_height() - 200)),
                     speed=rnd(2, 4),
                     ground_lvl=self.game.ground_lvl,
                     width=self.game.game_w,
                     group=self.alie_jets)

        self.pressed = pygame.mouse.get_pressed()

        self.aim.update(self.pos, self.fl_change_aim)
        self.fl_change_aim = False

        if pygame.mouse.get_focused() and self.pos[0] < self.game.game_w:
            pygame.mouse.set_visible(False)

            # Target recognition
            if self.aim.target_recognition_bought:
                for group in [self.jets, self.helicopters, self.alie_jets]:
                    for unit in group:
                        if unit.rect.colliderect(self.aim.rect) and not unit.exploded:
                            self.aim.recognise(unit)

            # Giving to aim target for homing
            if self.aim.aim_type == 'homing' and self.aim.homing_target is None:
                for group in [self.alie_jets, self.jets, self.helicopters]:
                    for unit in group:
                        if unit.rect.colliderect(self.aim.rect) and not unit.exploded:
                            self.aim.homing_target = unit
                            self.aim.start_homing_time = time()

            # Shooting laser
            if self.aim.aim_type == 'simple' and self.pressed[0]:
                for i, group in enumerate([self.game.city, self.pilots, self.alie_jets,
                                           self.jets, self.dropped_bombs, self.helicopters, self.rockets]):
                    for unit in group:
                        if unit.rect.collidepoint(self.aim.rect.center):
                            self.game.score += self.aim.inflict_damage(unit)
                            if type(unit) == Pilot and unit.alie and unit.hp == 0:
                                self.game.menu.buttons[6].renew(self.game.score)
                                self.game.pilot_bought = False

                self.aim.shoted = bool(self.aim.shoot_laser())

            elif self.aim.aim_type == 'homing' and self.aim.homing and self.pressed[0]:
                for i, group in enumerate([self.alie_jets, self.jets, self.helicopters]):
                    for unit in group:
                        if unit.rect.collidepoint(self.aim.laser_point):
                            self.game.score += self.aim.inflict_damage(unit)

                self.aim.shoted = bool(self.aim.shoot_laser())

            else:
                self.aim.shoted = False

            # Checking alie jet and its pilot
            if self.game.fighter_bought:
                for jet in self.alie_jets:
                    if jet.exploded:
                        self.game.fighter_bought = False
                        self.game.menu.buttons[5].renew(self.game.score)

                        self.game.pilot_bought = any(map(lambda x: x.alie, self.pilots))
                        if not self.game.pilot_bought:
                            self.game.menu.buttons[6].renew(self.game.score)

            # Night vision on
            if self.pressed[2] and self.aim.nv_ready:
                self.aim.nv_on = True
            else:
                self.aim.nv_on = False

        else:
            pygame.mouse.set_visible(True)
            self.aim.shoted = False

        # Missiles hitting their targets
        for missile in self.rockets:
            if missile.rect.colliderect(missile.target.rect):
                self.game.score += missile.blow_up()

        # Charging laser energy
        if not (pygame.mouse.get_focused() and self.pos[0] < self.game.game_w) or not self.aim.shoted \
                or not self.aim.ready_to_shoot:
            self.aim.charge_laser_energy()

        # Bombs blow_up houses
        for bomb in self.dropped_bombs:
            if bomb.house.rect.colliderect(bomb.rect):
                self.game.score += bomb.blow_up()

        # Catapulted pilots are spawning helicopters
        for pilot in self.pilots:
            if pilot.landed:
                if pilot.help_signal_timer == 0:
                    Helicopter(pilot=pilot,
                               ground_lvl=self.game.ground_lvl,
                               game_w=self.game.game_w,
                               group=self.helicopters,
                               alie=pilot.alie)
                if pilot.captured_timer == 0:
                    self.game.score += pilot.get_captured()

        # Overlay dusk and rotating spotlights
        if self.game.menu.info.time > 200 and self.how_dark < self.game.darkness_limit:
            self.how_dark += 0.2
        if self.how_dark > self.game.darkness_limit:
            self.how_dark = self.game.darkness_limit

        for house in self.game.city:
            house.get_dark(int(self.how_dark))
        self.game.ground.get_dark(int(self.how_dark))

        self.spotlight_surf.update(self.game.spotlights, int(self.how_dark), self.rotate_spotlights_time)
        if self.rotate_spotlights_time:
            self.rotate_spotlights_time = False

        # Updating sprite groups
        self.rockets.update()
        self.jets.update(self.game.city, self.dropped_bombs, self.pilots)
        self.helicopters.update()
        self.dropped_bombs.update()
        self.pilots.update()
        self.alie_jets.update(self.rockets, self.jets, self.helicopters, self.pilots)

        self.laser_energy_bar.update(self.aim.energy, self.aim.energy_max)
        if self.aim.night_vision_bought:
            self.night_vision_energy_bar.update(self.aim.nv_energy, self.aim.nv_energy_max)

    def __del__(self):
        if self.aim.laser_sound:
            self.aim.laser_sound.stop()
            self.aim.laser_sound = None

        pygame.mixer.music.stop()
