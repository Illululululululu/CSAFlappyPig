import pygame
from pygame.locals import *
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 864
screen_height = 764

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Flappy Pig")

#define font
font = pygame.font.Font("assets/BAUHS93.ttf", 60)

#define colors
white = (255, 255, 255)

ground_scroll = 0
scroll_speed = 5
flying = False
game_over = False
pipe_gap = 170
pipe_frequency = 1500 #millisecs
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False

#load images
bg = pygame.image.load('assets/background_and_road_red.png')
ground_img = pygame.image.load('assets/ground.png')
button_img = pygame.image.load('assets/restart.png')

def draw_text(text, font,text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0
    return score

class Pig(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1,4):
            img = pygame.image.load(f'assets/pig{num}.png')
            img = pygame.transform.scale(img, (65,42))
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0

    def update(self):

        if flying == True:
            #gravity
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 654:
                self.rect.y += int(self.vel)
        if game_over == False:
            #jump
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False


            #animation
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            # # rotate
            # self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)

        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)

        if flying or game_over:
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)

        if flying == False and game_over == True:
         self.image = pygame.transform.rotate(self.images[self.index], -90)

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.original_image = pygame.image.load('assets/pipepig-removebg-preview.png')
        new_width = 80
        new_height = screen_height
        self.image = pygame.transform.scale(self.original_image, (new_width, new_height))
        self.rect = self.image.get_rect()


        #position 1 is from the top, -1 is from the bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap)/2]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap)/2]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):

        action = False

        #get mouse position
        pos = pygame.mouse.get_pos()

        #check if mouse is over button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        #draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action

pig_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Pig(100, int(screen_height / 2))

pig_group.add(flappy)

#creat a button
button = Button(screen_width / 2 - 50, screen_height / 2 - 100, button_img)

run = True
while run:

    clock.tick(60)

    screen.blit(bg, (0, 0))

    pig_group.draw(screen)
    pig_group.update()
    pipe_group.draw(screen)


    #draw ground
    screen.blit(ground_img, (ground_scroll, 654))

    #check the score
    if len(pipe_group) > 0:
        if pig_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
            and pig_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
            and pass_pipe == False:
            pass_pipe = True

        if pass_pipe == True:
            if pig_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False

    draw_text(str(score), font, white, int(screen_width / 2), 20)

    if pygame.sprite.groupcollide(pig_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True


    #check if bird hit the ground
    if flappy.rect.bottom >= 654:
        game_over = True
        flying = False

    if game_over == False and flying == True:

        #generate new pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2)+ pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 40:
            ground_scroll = 0

        pipe_group.update()

   #check for game over and restart
    if game_over == True:
        if button.draw() == True:
            game_over = False
            score = reset_game()


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True
    pygame.display.update()


pygame.quit()