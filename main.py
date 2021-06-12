import random
from enum import Enum
import pygame

WINDOW_WIDTH = 700    #Width of the game window
WINDOW_HEIGHT = 500   #Height of the game window

class GameObject(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surface = pygame.Surface((10,10))
        self.rect = self.surface.get_rect()

#Area representing each part of the snake
class BodyPart(GameObject):
    def __init__(self, color):
        super().__init__()
        self.surface.fill(color)

#Special type of body part with a direction, dictates where the rest of the snake will move
class Head(BodyPart):
    def __init__(self, color):
        super().__init__(color)
        self.x_speed = self.rect.width
        self.y_speed = 0
        self.rect.left = WINDOW_WIDTH/2
        self.rect.top = WINDOW_HEIGHT/2

    #Changes the direction of the head based on key press
    def change_direction(self, pressed_keys):
        if pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_w]:
            self.x_speed = 0
            self.y_speed = -self.rect.height
        elif pressed_keys[pygame.K_DOWN] or pressed_keys[pygame.K_s]:
            self.x_speed = 0
            self.y_speed = self.rect.height
        elif pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]:
            self.x_speed = -self.rect.width
            self.y_speed = 0
        elif pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]:
            self.x_speed = self.rect.width
            self.y_speed = 0

    #Moves the head's location based on the current direction
    def move(self):
        self.rect.move_ip(self.x_speed, self.y_speed)
        if self.rect.left < 0:
            self.rect.left = WINDOW_WIDTH - self.rect.width
        elif self.rect.left + self.rect.width > WINDOW_WIDTH:
            self.rect.left = 0
        elif self.rect.top < 0:
            self.rect.top = WINDOW_HEIGHT - self.rect.height
        elif self.rect.top + self.rect.height > WINDOW_HEIGHT:
            self.rect.top = 0

#Hold all the snake's body parts including the head
class Snake():
    def __init__(self, length):
        self.head = Head((100,100,100))
        self.parts = []
        self.parts.append(self.head)
        for i in range(1, length):
            part = BodyPart((255,255,255))
            self.parts.append(part)
            part.rect.left = self.parts[i-1].rect.left - part.rect.width
            part.rect.top = self.parts[i-1].rect.top

    #The snake is moved by moving each part to the location of the part before it (except the head)
    def slither(self):
        last_index = len(self.parts) - 1     #Start from the last index
        for i in range(last_index, 0, -1):
            self.parts[i].rect.left = self.parts[i-1].rect.left
            self.parts[i].rect.top = self.parts[i-1].rect.top
        self.head.move()

    def grow(self):
        part = BodyPart((255,255,255))
        part.rect.left = self.head.rect.left
        part.rect.top = self.head.rect.top
        self.parts.insert(1, part)
        self.head.move()
        return part

class Food(GameObject):
    def __init__(self):
        super().__init__()
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.surface.fill(color)
        self.rect.left = random.randint(0, WINDOW_WIDTH/10) * 10
        self.rect.top = random.randint(0, WINDOW_HEIGHT/10) * 10 

pygame.init()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

snake = Snake(5)
running = True

foods = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

all_sprites.add(iter(snake.parts))

ADDFOOD = pygame.USEREVENT + 1
pygame.time.set_timer(ADDFOOD, 1500)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == ADDFOOD:
            food = Food()
            all_sprites.add(food)
            foods.add(food)

    pressed_keys = pygame.key.get_pressed()
    snake.head.change_direction(pressed_keys)

    for i in range(1, len(snake.parts)):
        if pygame.sprite.collide_rect(snake.head, snake.parts[i]):
            snake.head.kill()
            running = False

    collided_food = pygame.sprite.spritecollide(snake.head, foods, True)
    if len(collided_food) != 0:
        new_part = snake.grow()
        all_sprites.add(new_part)
    else:
        snake.slither()

    window.fill((0,0,0))
    for sprite in all_sprites:
        window.blit(sprite.surface, sprite.rect)

    pygame.display.flip()
    clock.tick(15)