import random
from enum import Enum
import pygame
import pygame.freetype

WINDOW_WIDTH = 700
WINDOW_HEIGHT = 500   
pygame.init()
FONT = pygame.freetype.Font("res/fonts/JOKERMAN.TTF", 17)

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
        last_index = len(self.parts) - 1
        for i in range(last_index, 0, -1):
            self.parts[i].rect.left = self.parts[i-1].rect.left
            self.parts[i].rect.top = self.parts[i-1].rect.top
        self.head.move()
    
    #Adds a new BodyPart to the snake, placing it at the snake's head's location, the snake's head is then moved.
    #NOTE: if grow is called, there is no need to call slither during the same frame
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

class SnakeGame():
    ADDFOOD = pygame.USEREVENT + 1  #Custom Event used to spawn food at regular intervals
    def __init__(self):
        pygame.display.set_caption("Snake Game")
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.highscore = self.read_highscore()
    
    def read_highscore(self):
        with open("storage/highscore.txt") as reader:
            data = reader.readline()
            try:
                return int(data)
            except ValueError:
                return 0
    
    def write_highscore(self):
        with open("storage/highscore.txt", "r+") as file:
            file.truncate(0)
            file.write(str(self.highscore))

    #Used for unit testing
    #def write_highscore(self, newscore):
        #with open("storage/highscore.txt", "w") as writer:
            #writer.truncate(0)
            #writer.write(str(newscore))
    
    def newgame(self):
        self.snake = Snake(5)
        self.foods = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(iter(self.snake.parts))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == SnakeGame.ADDFOOD:
                food = Food()
                self.all_sprites.add(food)
                self.foods.add(food)

    def render(self):
        self.window.fill((0,0,0))
        for sprite in self.all_sprites:
            self.window.blit(sprite.surface, sprite.rect)
        FONT.render_to(self.window, (10, 10), "Score: " + str(len(self.snake.parts)), (0, 255, 255))
        FONT.render_to(self.window, (WINDOW_WIDTH/2 - 50, 10), "Highscore: " + str(self.highscore), (0, 255, 255))

    #Checks if the head collided the body, which causes the game to end
    def collided_body(self):
        for i in range(1, len(self.snake.parts)):
            if pygame.sprite.collide_rect(self.snake.head, self.snake.parts[i]):
                self.snake.head.kill()
                self.running = False

    #If the head collides with food, the snake grows
    def collided_food(self):
        food_collided = pygame.sprite.spritecollide(self.snake.head, self.foods, True)
        if len(food_collided) != 0:
            return True
        else:
            return False

    def gameloop(self):
        pygame.time.set_timer(SnakeGame.ADDFOOD, 1500)
        while self.running:
            self.handle_events()
            pressed_keys = pygame.key.get_pressed()
            self.snake.head.change_direction(pressed_keys)
            self.collided_body()
            if self.collided_food():
                new_part = self.snake.grow()
                self.all_sprites.add(new_part)
                if len(self.snake.parts) > self.highscore:
                    self.highscore = len(self.snake.parts)
            else:
                self.snake.slither()
            self.render()
            pygame.display.flip()
            self.clock.tick(15)
        self.write_highscore()

game = SnakeGame()
game.newgame()
game.gameloop()
