import time
import pygame
from enum import Enum

WINDOW_WIDTH = 700    #Width of the game window
WINDOW_HEIGHT = 500   #Height of the game window

#Direction of the head of the snake
class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

#Area representing each part of the snake
class BodyPart(pygame.sprite.Sprite):
    def __init__(self, color):
        super().__init__()
        self.surface = pygame.Surface((10,10))
        self.surface.fill(color)
        self.rect = self.surface.get_rect()

#Special type of body part with a direction, dictates where the rest of the snake will move
class Head(BodyPart):
    def __init__(self, color):
        super().__init__(color)
        self.direction = Direction.RIGHT
        self.rect.left = WINDOW_WIDTH/2
        self.rect.top = WINDOW_HEIGHT/2

    #Changes the direction of the head based on key press
    def change_direction(self, pressed_keys):
        if pressed_keys[pygame.K_UP]:
            self.direction = Direction.UP
        elif pressed_keys[pygame.K_DOWN]:
            self.direction = Direction.DOWN
        elif pressed_keys[pygame.K_LEFT]:
            self.direction = Direction.LEFT
        elif pressed_keys[pygame.K_RIGHT]:
            self.direction = Direction.RIGHT

    #Moves the head's location based on the current direction
    def move(self):
        if self.direction == Direction.UP:
            self.rect.move_ip(0,-10)
        elif self.direction == Direction.DOWN:
            self.rect.move_ip(0,10)
        elif self.direction == Direction.LEFT:
            self.rect.move_ip(-10,0)
        else:
            self.rect.move_ip(10,0)

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
    def __init__(self, length, speed):
        self.speed = speed
        self.head = Head((100,100,100))
        self.parts = []
        self.parts.append(self.head)
        for i in range(1, length):
            part = BodyPart((255,255,255))
            self.parts.append(part)
            part.rect.left = self.parts[i-1].rect.left - part.rect.width
            part.rect.top = self.parts[i-1].rect.top

    #The snake is moved by moving each part to the location of the part before it (except the head)
    #The operation explained above is done <speed> times
    def slither(self):
        last_index = len(self.parts) - 1     #Start from the last index
        for j in range(last_index, 0, -1):
            if self.parts[j].rect.left < self.parts[j-1].rect.left:
                self.parts[j].rect.move_ip(self.speed, 0)
            elif self.parts[j].rect.left > self.parts[j-1].rect.left:
                self.parts[j].rect.move_ip(-self.speed, 0)
            elif self.parts[j].rect.top < self.parts[j-1].rect.top:
                self.parts[j].rect.move_ip(0, self.speed)
            else:
                self.parts[j].rect.move_ip(0, -self.speed)
        self.head.move()

pygame.init()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

snake = Snake(10, 10)
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pressed_keys = pygame.key.get_pressed()
    snake.head.change_direction(pressed_keys)

    snake.slither()

    window.fill((0,0,0))
    for part in snake.parts:
        window.blit(part.surface, part.rect)
    
    pygame.display.flip()
    clock.tick(15)