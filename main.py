import random
import tkinter
import pygame
import pygame.freetype

WINDOW_WIDTH = 700
WINDOW_HEIGHT = 500

pygame.init()
FONT = pygame.freetype.Font("res/fonts/JOKERMAN.TTF", 17)

class GameObject(pygame.sprite.Sprite):
    def __init__(self, left, top):
        super().__init__()
        self.surface = pygame.Surface((10, 10))
        self.rect = self.surface.get_rect(topleft = (left, top))

#Area representing each part of the snake
class BodyPart(GameObject):
    def __init__(self, color, left, top):
        super().__init__(left, top)
        self.surface.fill(color)

#Controls where the snake will go
class Head(BodyPart):
    def __init__(self, color, left, top):
        super().__init__(color, left, top)
        self.x_speed = self.rect.width
        self.y_speed = 0

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

    def draw_eyes(self, color):
        if self.x_speed < 0:
            pygame.draw.circle(self.surface, color, (2,2), 1)
            pygame.draw.circle(self.surface, color, (2,8), 1)
        elif self.x_speed > 0:
            pygame.draw.circle(self.surface, color, (8,2), 1)
            pygame.draw.circle(self.surface, color, (8,8), 1)
        elif self.y_speed < 0:
            pygame.draw.circle(self.surface, color, (2,2), 1)
            pygame.draw.circle(self.surface, color, (8,2), 1)
        else:
            pygame.draw.circle(self.surface, color, (2,8), 1)
            pygame.draw.circle(self.surface, color, (8,8), 1)

class Food(GameObject):
    def __init__(self):
        left = random.randint(0, WINDOW_WIDTH/10) * 10
        top = random.randint(4, WINDOW_HEIGHT/10) * 10 
        super().__init__(left, top)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.surface.fill(color)

#Hold all the snake's body parts including the head
class Snake():
    def __init__(self, color, secondary_color, length):
        self.color = color
        self.secondary_color = secondary_color
        self.eat_sound = pygame.mixer.Sound("res/sounds/bite.WAV")
        self.death_sound = pygame.mixer.Sound("res/sounds/death.WAV")
        self.head = Head(self.color, WINDOW_WIDTH/2, WINDOW_HEIGHT/2)
        self.parts = []
        self.parts.append(self.head)
        for i in range(1, length):
            left = self.parts[i-1].rect.left - self.parts[i-1].rect.width
            top = self.parts[i-1].rect.top
            part = BodyPart(self.color, left, top)
            self.parts.append(part)

    def change_color(self, hex_color):
        r,g,b,a = pygame.Color(hex_color)
        rgb_color = r,g,b
        self.color = rgb_color
        for part in self.parts:
            part.surface.fill(rgb_color)
    
    #Draws a set of eyes and stripes for the snake.
    def animate(self):
        for part in self.parts:
            part.surface.fill(self.color)
        self.head.draw_eyes(self.secondary_color)
        for i in range(len(self.parts)-1):
            x_diff = self.parts[i].rect.left - self.parts[i+1].rect.left
            y_diff = self.parts[i].rect.top - self.parts[i+1].rect.top
            if x_diff > 0:
                pygame.draw.line(self.parts[i].surface, self.secondary_color, (0,0), (0,9), 1)
            elif x_diff < 0:
                pygame.draw.line(self.parts[i].surface, self.secondary_color, (9,0), (9,9), 1)
            elif y_diff > 0:
                pygame.draw.line(self.parts[i].surface, self.secondary_color, (0,0), (9,0), 1)
            else:
                pygame.draw.line(self.parts[i].surface, self.secondary_color, (0,9), (9,9), 1)
            

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
        part = BodyPart(self.color, self.head.rect.left, self.head.rect.top)
        self.parts.insert(1, part)
        self.head.move()
        return part

    def collided_food(self, food, sprites):
        food_collided = pygame.sprite.spritecollide(self.head, food, True)
        if len(food_collided) != 0:
            new_part = self.grow()
            sprites.add(new_part)
            self.eat_sound.play()
            return True
        return False

    #Checks if the head collided with the body, which causes the game to end
    def collided_body(self):
        for i in range(1, len(self.parts)):
            if pygame.sprite.collide_rect(self.head, self.parts[i]):
                self.head.kill()
                self.death_sound.play()
                return True
        return False

class Button(pygame.sprite.Sprite):
    def __init__(self, left, top, on_click):
        super().__init__()
        self.surface = pygame.image.load("res/images/SettingsIcon.PNG").convert()
        self.rect = self.surface.get_rect(topleft = (left, top))
        self.on_click = on_click

    #Checks if the mouse was over the button when the click event happened.
    def was_clicked(self, mouse_x, mouse_y):
        if self.rect.left <= mouse_x <= self.rect.left + self.rect.width:
            if self.rect.top <= mouse_y <= self.rect.top + self.rect.height:
                self.on_click()

class SettingsMenu(tkinter.Frame):
    def __init__(self, game):
        self.game = game
        self.window = tkinter.Tk()
        self.window.geometry("240x360")
        self.add_widgets()
        self.color_options()
        self.window.mainloop()

    def add_widgets(self):
        self.frame = tkinter.Frame(master = self.window)
        self.frame.pack()
        paused_lbl = tkinter.Label(master = self.frame, text = "Paused", fg = "red", font = "Times 18")
        paused_lbl.pack()
        music_toggle = tkinter.Checkbutton(master = self.frame, text = "Music")
        music_toggle.pack(pady = 10)

    def color_options(self):
        colors_frm = tkinter.Frame(master = self.frame)
        colors_frm.pack()
        colors_lbl = tkinter.Label(master = colors_frm, text = "Snake color: ", justify = "left")
        colors_lbl.grid(column = 0, row = 0)
        colors = dict(black = "#000000", orange = "#FFA500", red = "#FF0000", cyan = "#00FFFF")
        next_column = 1
        for key, value in colors.items():
            color_btn = tkinter.Button(
                master = colors_frm,
                width = 1,
                height = 1,
                bg = value,
                command = lambda x=value: self.game.snake.change_color(x)
            )
            color_btn.grid(column = next_column, row = 0, padx = 1)
            next_column += 1

class Game():
    ADDFOOD = pygame.USEREVENT + 1  #Custom Event used to spawn food at regular intervals
    def __init__(self):
        pygame.display.set_caption("Snake Game")
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.settings_btn = Button(WINDOW_WIDTH - 50, 8, self.pause)
        self.highscore = self.read_highscore()

    def pause(self):
        pygame.time.set_timer(Game.ADDFOOD, 0)      #Food must not be added while the game is paused
        SettingsMenu(self)                         
        pygame.time.set_timer(Game.ADDFOOD, 1500)
    
    #Reads the highscore from a local file
    #If the file is empty or the data in the file is not convertable to int (not a number) then 0 is returned
    def read_highscore(self):
        with open("storage/highscore.txt") as reader:
            data = reader.readline()
            try:
                return int(data)
            except ValueError:
                return 0
    
    #Erases all data from the file and writes the new highscore
    def write_highscore(self):
        with open("storage/highscore.txt", "r+") as file:
            file.truncate(0)
            file.write(str(self.highscore))

    def update_highscore(self):
        if len(self.snake.parts) > self.highscore:
            self.highscore = len(self.snake.parts)

    def display_scores(self):
        score = FONT.render("Length: " + str(len(self.snake.parts)), (0, 255, 255))
        highscore = FONT.render("Best Length: " + str(self.highscore), (0, 255, 255))
        self.window.blit(score[0], (10, 10))
        self.window.blit(highscore[0], (WINDOW_WIDTH/2 - highscore[1].width/2, 10))

    #Used for unit testing
    #def write_highscore(self, newscore):
        #with open("storage/highscore.txt", "w") as writer:
            #writer.truncate(0)
            #writer.write(str(newscore))

    #Called at the beginning of the game and then each time the player loses and decided to play again
    def newgame(self):
        self.snake = Snake((100, 100, 100), (255, 255, 255), 5)
        self.food = pygame.sprite.Group()
        self.sprites = pygame.sprite.Group()
        self.sprites.add(iter(self.snake.parts))
        pygame.time.set_timer(Game.ADDFOOD, 1500)

    #Called at each frame to handle the game's events
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == Game.ADDFOOD:
                food = Food()
                self.sprites.add(food)
                self.food.add(food)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.settings_btn.was_clicked(event.pos[0], event.pos[1])

    #Renders all sprites to the screen and displays the score
    def render(self):
        self.window.fill((0,0,0))   #Erases all drawings from last frame
        self.snake.animate()        
        for sprite in self.sprites:
            self.window.blit(sprite.surface, sprite.rect)
        self.display_scores()
        self.window.blit(self.settings_btn.surface, self.settings_btn.rect)
        pygame.display.flip()

    def loop(self):
        while self.running:
            self.handle_events()
            pressed_keys = pygame.key.get_pressed()
            self.snake.head.change_direction(pressed_keys)
            if self.snake.collided_body():
                self.running = False
            if self.snake.collided_food(self.food, self.sprites):
                self.update_highscore()
            else:
                self.snake.slither()
            self.render()
            self.clock.tick(15)
        self.write_highscore()

game = Game()
game.newgame()
game.loop()