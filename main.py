import pygame as pg
import random
from opcje import *
from sprites import *
from os import path

class Game:
    def __init__(self):
        # inicjalizacja gry
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()

    def load_data(self):
        # ładowanie high scoree
        self.dir = path.dirname(__file__)
        img_dir = path.join(self.dir, 'img')
        with open(path.join(self.dir, HS_FILE), 'r') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0
        # ładowanie tekstury gracza
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))
        # ładowanie dźwięków
        self.snd_dir = path.join(self.dir, 'snd')
        self.jump_sound = pg.mixer.Sound(path.join(self.snd_dir, 'Jump.wav'))


    def new(self):
        # rozpoczęcie nowej gry
        self.score = 0
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.player = Player(self)
        self.all_sprites.add(self.player)
        for plat in PLATFORM_LIST:
            p = Platform(*plat)
            self.all_sprites.add(p)
            self.platforms.add(p)
        pg.mixer.music.load(path.join(self.snd_dir, 'song17.mp3'))    
        self.run()

    def run(self):
        # pętla gry
        pg.mixer.music.play()
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        # aktualizacja
        self.all_sprites.update()
        # sprawdzanie czy kolizja z platofromą
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                self.player.pos.y = hits[0].rect.top
                self.player.vel.y = 0

        # przewijanie ekranu
        if self.player.rect.top <= HEIGHT / 4:
            self.player.pos.y += abs(self.player.vel.y)
            for plat in self.platforms:
                plat.rect.y += abs(self.player.vel.y)
                if plat.rect.top >= HEIGHT:
                    plat.kill()
                    self.score += 10

        # koniec gry
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.playing = False

        # tworzenie nowych platform
        while len(self.platforms) < 4:
            width = random.randrange(50, 100)
            p = Platform(random.randrange(0, WIDTH - width),
                         random.randrange(-75, -30),
                         width, 20)
            self.platforms.add(p)
            self.all_sprites.add(p)

    def events(self):
        # wyłapywanie eventów
        for event in pg.event.get():
            # sprawdzanie zamknięcia okna
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            # skakanie     
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump()
                if event.key == pg.K_ESCAPE: 
                    if self.playing == True:
                        self.playing = False
                        self.show_go_screen()

                               
                          

    def draw(self):
        # rysowanie na ekranie
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        self.draw_text(str(self.score), 22, WHITE, WIDTH / 2, 15)
        # render
        pg.display.flip()

    def show_start_screen(self):
        # ekran początkowy
        self.screen.fill(BGCOLOR)
        self.draw_text(TITLE, 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Strzałki - Ruch Lewo/Prawo, Spacja - Skok", 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("ESC - Wyjście do menu, F12 - Wyłączenie gry", 22, WHITE, WIDTH / 2 , HEIGHT / 2 + 25)
        self.draw_text("Naciśnij klawisz aby zagrać", 22, WHITE, WIDTH / 2, HEIGHT * 10 / 14)
        self.draw_text("Twórca: Jakub Jakubiszak", 16, WHITE, WIDTH / 2, HEIGHT * 7 / 8)
        self.draw_text("Muzyka: https://opengameart.org", 16, WHITE, WIDTH / 2, HEIGHT * 15 / 16)
        self.draw_text("Grafika: https://opengameart.org", 16, WHITE, WIDTH / 2, HEIGHT * 10 / 11)
        self.draw_text("Najlepszy wynik: " + str(self.highscore), 22, WHITE, WIDTH / 2, 15)
        pg.display.flip()
        self.wait_for_key()

    def show_go_screen(self):
        # ekran końcowy i wynik
        if not self.running:
            return
        self.screen.fill(BGCOLOR)
        self.draw_text("GAME OVER", 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Wynik: " + str(self.score), 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Naciśnij klawisz aby zagrać ponownie", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        self.draw_text("Twórca: Jakub Jakubiszak", 16, WHITE, WIDTH / 2, HEIGHT * 7 / 8)
        self.draw_text("Muzyka: https://opengameart.org", 16, WHITE, WIDTH / 2, HEIGHT * 15 / 16)
        self.draw_text("Grafika: https://opengameart.org", 16, WHITE, WIDTH / 2, HEIGHT * 10 / 11)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("NOWY NAJLEPSZY WYNIK!", 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
            with open(path.join(self.dir, HS_FILE), 'w') as f:
                f.write(str(self.score))
        else:
            self.draw_text("Najlepszy wynik: " + str(self.highscore), 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        # zaczęcie gry po wcisnięciu guzika
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:
                    if event.key == pg.K_F12:
                        waiting = False
                        self.running = False
                if event.type == pg.KEYUP:
                    waiting = False

    def draw_text(self, text, size, color, x, y):
        # tekst na ekranie
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

#uruchamianie obiektu
g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()
                        

pg.quit()