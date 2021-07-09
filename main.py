#Snake Game by Jaffar Alzeidi
#This is a snake game made with pygame
#The objective is to eat food and get as large as possible without colliding with the body of the snake
#Highscore saves to a local file
#The game's pause menu is made with tkinter
#Last modified on 07/04/2021

import random
import tkinter
import functools
import pygame
import pygame.freetype

#Game window dimensions
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 400

pygame.init()
JOKERMAN = pygame.freetype.Font("res/fonts/JOKERMAN.ttf", 17)   #Font used to display scores
EIGHT_BIT = pygame.freetype.Font("res/fonts/8-BIT.ttf", 17)     #Font used to display game over text

#Spawns at a random location within the screen, the snake grows when collided with this game object
class Food(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        left = random.randint(0, WINDOW_WIDTH/10 - 1) * 10
        top = random.randint(5, WINDOW_HEIGHT/10 - 1) * 10 
        self.surface = pygame.image.load("res/images/apple.jpg")
        self.rect = self.surface.get_rect(topleft = (left, top))

#Represents each part of the snake
class BodyPart(pygame.sprite.Sprite):
    def __init__(self, color, left, top):
        super().__init__()
        self.surface = pygame.Surface((10, 10))
        self.rect = self.surface.get_rect(topleft = (left, top))
        self.surface.fill(color)

#Controls where the snake will go
class Head(BodyPart):
    def __init__(self, color, left, top):
        super().__init__(color, left, top)
        self.x_speed = self.rect.width
        self.y_speed = 0

    #Changes the direction of the head based on key press
    #Head cannot go in the opposite of its current direction, as it would result in instant death
    def change_direction(self, pressed_keys):
        if pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_w]:
            if self.y_speed == 0:
                self.x_speed = 0
                self.y_speed = -self.rect.height
        elif pressed_keys[pygame.K_DOWN] or pressed_keys[pygame.K_s]:
            if self.y_speed == 0:
                self.x_speed = 0
                self.y_speed = self.rect.height
        elif pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]:
            if self.x_speed == 0:
                self.x_speed = -self.rect.width
                self.y_speed = 0
        elif pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]:
            if self.x_speed == 0:
                self.x_speed = self.rect.width
                self.y_speed = 0

    #Moves the head's location based on the current direction.
    #Checks if the head has moved beyond the playable area, in which case it comes out of the other side of the playable area
    def move(self):
        self.rect.move_ip(self.x_speed, self.y_speed)
        if self.rect.left < 0:
            self.rect.left = WINDOW_WIDTH - self.rect.width
        elif self.rect.left + self.rect.width > WINDOW_WIDTH:
            self.rect.left = 0
        elif self.rect.top < 50:
            self.rect.top = WINDOW_HEIGHT - self.rect.height
        elif self.rect.top + self.rect.height > WINDOW_HEIGHT:
            self.rect.top = 50

    #Draws a set of eyes on the head, the location of the eyes is dependent on the speed of the head
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

#Holds all the snake's body parts including the head
#The color variable holds the snake's primary color
#The secondary_color variable holds the snake's eye and stripe color
class Snake():
    def __init__(self, color, secondary_color, start_length):
        self.color = color
        self.secondary_color = secondary_color
        self.start_length = start_length
        self.eat_sound = Sound("res/sounds/bite.WAV")
        self.death_sound = Sound("res/sounds/death.WAV")

    #Creates the head and the snake's body parts. This method is called when the game starts, and every time the player
    #chooses to play again
    def construct(self):
        self.head = Head(self.color, WINDOW_WIDTH/2, WINDOW_HEIGHT/2)
        self.parts = []
        self.parts.append(self.head)
        for i in range(1, self.start_length):
            left = self.parts[i-1].rect.left - self.parts[i-1].rect.width
            top = self.parts[i-1].rect.top
            part = BodyPart(self.color, left, top)
            self.parts.append(part)

    #Changes the snake's primary color
    def change_color(self, hex_color):
        self.color = Color.to_rgb(hex_color)

    #Changes the snake's secondary color
    def change_sec_color(self, hex_color):
        self.secondary_color = Color.to_rgb(hex_color)
    
    #Renders the snake
    #The method fill is called for every part to erase stripes/eyes drawn in previous frames
    def render(self):
        for part in self.parts:
            part.surface.fill(self.color)
        self.head.draw_eyes(self.secondary_color)

    #The snake is moved by moving each part to the location of the part before it in the list of parts (except the head)
    def slither(self):
        last_index = len(self.parts) - 1
        for i in range(last_index, 0, -1):
            self.parts[i].rect.left = self.parts[i-1].rect.left
            self.parts[i].rect.top = self.parts[i-1].rect.top
        self.head.move()
    
    #Adds a new BodyPart to the snake, placing it at the snake's head's location, the snake's head is then moved.
    #NOTE: if grow is called, slither shouldn't be called during the same frame because grow places the newly created part
    #in the head's location, the the head is moved, thus creating the slither effect in a more efficient way
    def grow(self):
        part = BodyPart(self.color, self.head.rect.left, self.head.rect.top)
        self.parts.insert(1, part)
        self.head.move()
        return part

    #Checks if the snake's head collided with food
    def head_collided_food(self, food_list):
        if pygame.sprite.spritecollide(self.head, food_list, True):
            return True
        return False

    #Checks if any part of the snake has collided with food, this is called to make sure that newly spawned food does not
    #spawn on top of the snake
    def collided_food(self, food):
        for part in self.parts:
            if pygame.sprite.collide_rect(part, food):
                return True
        return False

    #Check if the snake's head collided its body
    def collided_body(self):
        for i in range(1, len(self.parts)):
            if pygame.sprite.collide_rect(self.head, self.parts[i]):
                return True
        return False

#Extends the sound functionality to only play if sound_on is true
class Sound(pygame.mixer.Sound):
    def __init__(self, src):
        super().__init__(src)

    def play(self, sound_on):
        if sound_on:
            super().play()

#Helper class which contains a method to convert from hex to rgb color format
class Color():
    def to_rgb(hex_color):
        r,g,b,a = pygame.Color(hex_color)
        rgb = r,g,b
        return rgb

#Image button with a callback function
class Button(pygame.sprite.Sprite):
    def __init__(self, img, left, top, on_click):
        super().__init__()
        self.surface = pygame.image.load(img).convert()
        self.rect = self.surface.get_rect(topleft = (left, top))
        self.on_click = on_click

    #Checks if the mouse was over the button when the click event was triggered.
    def was_clicked(self, mouse_x, mouse_y):
        if self.rect.left <= mouse_x <= self.rect.left + self.rect.width:
            if self.rect.top <= mouse_y <= self.rect.top + self.rect.height:
                self.on_click()

#Menu used to pause game and manipulate game settings
class SettingsMenu():
    def __init__(self, game):
        self.bg = "#87CEEB"                             #background color of the window
        self.root = tkinter.Tk()
        self.root.title(string = "Settings")
        self.root.minsize(width = 220, height = 210)
        self.root.configure(bg = self.bg)
        self.root.resizable(False, False)
        self.frame = tkinter.Frame(master = self.root, bg = self.bg)
        self.frame.pack()
        self.game = game
        self.sound = tkinter.BooleanVar()               #keeps track of the sound checkbutton's status
        self.confirmation = False                       #True when the conf_window is on screen, false otherwise
        self.add_widgets()
        self.center(self.root)
        self.check_quit()
        self.root.mainloop()

    #Periodically check for the pygame quit event, in which case the program is exited
    #Without this check, the program will not respond to the quit event on the pygame window
    def check_quit(self):
        if pygame.event.get(eventtype = pygame.QUIT):
            self.game.running = False
            self.root.destroy()
        self.root.after(250, self.check_quit)

    #Centers a window mid-screen
    def center(self, window):
        window.update_idletasks()                               #called to update the dimensions of the window
        window_width = window.winfo_width()
        window_height = window.winfo_height()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        window_x = int(screen_width/2 - window_width/2)
        window_y = int(screen_height/3 - window_height/3)
        window.geometry(f"+{window_x}+{window_y}")

    #Called when the sound checkbutton is clicked
    def on_toggle(self):
        if self.sound.get():
            self.game.sound = True
        else:
            self.game.sound = False

    #Widget to enable/disable sound effects in the game
    def sound_widget(self):
        self.sound.set(self.game.sound)       
        sound_checkbtn = tkinter.Checkbutton(master = self.frame, text = "Sound Effects",
                                             variable = self.sound, command = self.on_toggle, bg = self.bg)
        sound_checkbtn.pack(pady = 7)

    def on_reset(self):
        self.game.reset_highscore()
        self.game.update_highscore()
        self.exit_conf_window()

    #Exits the reset highscore confirmation window
    def exit_conf_window(self):
        self.confirmation = False
        self.conf_window.destroy()

    #Window used to confirm the resetting of the highscore.
    #If confirmation is true, then there is already a confirmation window on the screen, therefore there is no need to display
    #another one.
    def confirm_window(self):
        if self.confirmation:
            return
        self.conf_window = tkinter.Toplevel(self.root)
        self.conf_window.title(string = "Confirm")
        self.conf_window.configure(bg = self.bg)
        self.conf_window.resizable(False, False)
        self.conf_window.focus_set()
        self.conf_window.protocol("WM_DELETE_WINDOW", self.exit_conf_window)
        label = tkinter.Label(master = self.conf_window, text = "Do you wish to reset the current highscore?", fg = "red", bg = self.bg)
        label.pack()
        btn_frame = tkinter.Frame(master = self.conf_window, bg = self.bg)
        btn_frame.pack()
        yes_btn = tkinter.Button(master = btn_frame, text = "Yes", fg = "black", command = self.on_reset)
        no_btn = tkinter.Button(master = btn_frame, text = "No", fg = "black", command = self.exit_conf_window)
        yes_btn.pack(side = tkinter.LEFT, padx = 5, pady = 1)
        no_btn.pack(side = tkinter.LEFT, padx = 5, pady = 1)
        self.center(self.conf_window)
        self.confirmation = True

    def add_widgets(self):
        paused_lbl = tkinter.Label(master = self.frame, text = "Paused", fg = "red", bg = self.bg, font = "Times 18")
        paused_lbl.pack()
        self.sound_widget()
        colors = dict(black = "#000000", orange = "#FFA500", red = "#FF0000", cyan = "#00FFFF",
                      pink = "#FFC0CB", white = "#FFFFFF", blue = "#0000FF", neongreen = "#39FF14",
                      purple = "#800080", peach = "#FFE5B4")     
        self.color_options("Color: ", colors, self.game.snake.change_color)                         #Primary colors
        self.color_options("Secondary Color: ", colors, self.game.snake.change_sec_color)           #Secondary colors
        reset_btn = tkinter.Button(master = self.frame, text = "Reset Highscore",
                                   fg = "black", bd = 3, command = self.confirm_window)
        reset_btn.pack(pady = 7)

    #Displays color buttons with a description of what the buttons are used for.
    #Used for changing the primary and secondary colors of the snake.
    def color_options(self, desc, colors, on_click):
        colors_lbl = tkinter.Label(master = self.frame, text = desc, bg = self.bg)
        colors_lbl.pack()
        colors_frm = tkinter.Frame(master = self.frame)
        colors_frm.pack()
        for key, value in colors.items():
            color_btn = tkinter.Button(master = colors_frm, width = 1, height = 1, 
                                       bg = value, bd = 3, command = functools.partial(on_click, value))
            color_btn.pack(side = tkinter.LEFT)

class Game():
    ADDFOOD = pygame.USEREVENT + 1  #Custom Event used to spawn food a short while after the game starts
    def __init__(self):
        pygame.display.set_caption("Snake Game")
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.snake = Snake((0,255,255), (0,0,0), 5)
        self.clock = pygame.time.Clock()
        self.running = True
        self.sound = True
        self.settings_btn = Button("res/images/SettingsIcon.PNG", WINDOW_WIDTH - 50, 8, self.pause)
        self.highscore = self.read_highscore()

    #Pauses the game and displays the settings menu
    #MOUSEBUTTONUP events are cleared to avoid the spawning of multiple settings menus
    def pause(self):
        SettingsMenu(self)
        pygame.event.clear(eventtype = pygame.MOUSEBUTTONUP)
    
    #Reads the highscore from a local file
    #If the file is empty or the data in the file is not convertable to int (not a number) then 0 is returned
    def read_highscore(self):
        with open("storage/highscore.txt") as reader:
            data = reader.readline()
            try:
                return int(data)
            except ValueError:
                return 0
    
    #Overwrites the old highscore with the current highscore
    def write_highscore(self):
        with open("storage/highscore.txt", "r+") as file:
            file.truncate(0)
            file.write(str(self.highscore))

    #Deletes the saved highscore
    def reset_highscore(self):
        with open("storage/highscore.txt", "r+") as file:
            file.truncate(0)
        self.highscore = 0

    #Checks if the current score is greater than the high score, if so, the highscore's value is the same as the score
    def update_highscore(self):
        if len(self.snake.parts) > self.highscore:
            self.highscore = len(self.snake.parts)

    def display_scores(self):
        score = JOKERMAN.render("Length: " + str(len(self.snake.parts)), (0, 255, 255))
        highscore = JOKERMAN.render("Best Length: " + str(self.highscore), (0, 255, 255))
        self.window.blit(score[0], (10, 15))
        self.window.blit(highscore[0], (WINDOW_WIDTH/2 - highscore[1].width/2, 15))

    #Called at the beginning of the game and then each time the player loses and decides to play again.
    #Color and secondary color are supplied based on the snake's color and secondary color's values at the time the snake died.
    def init(self):
        self.snake.construct()
        self.food_list = pygame.sprite.Group()              #Used to detect collision of the head with food
        self.sprites = pygame.sprite.Group()                #Every sprite is added to this group for rendering
        self.sprites.add(iter(self.snake.parts))            #Add all of the snake's parts
        self.update_highscore()
        pygame.time.set_timer(Game.ADDFOOD, 1500, True)     #A one-time timer to spawn the food 1.5 secs after the game started

    #Spawns food in a random place on the map
    #If the food is spawned somewhere that collides with the snake, the food is respawned until it find an empty spot
    def spawn_food(self):
        food = Food()
        if self.snake.collided_food(food):
            food.kill()
            self.spawn_food()
        else: 
            self.sprites.add(food)
            self.food_list.add(food)

    #Called at each frame to handle the game's events
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == Game.ADDFOOD:
                self.spawn_food()
            elif event.type == pygame.MOUSEBUTTONUP:
                self.settings_btn.was_clicked(event.pos[0], event.pos[1])

    #Borders visibly define the playable area on the window
    def draw_borders(self):
        pygame.draw.line(self.window, (255, 255, 255), (0, 50), (WINDOW_WIDTH-1, 50), 1)
        pygame.draw.line(self.window, (255, 255, 255), (0, WINDOW_HEIGHT-1), (WINDOW_WIDTH-1, WINDOW_HEIGHT-1), 1)
        pygame.draw.line(self.window, (255, 255, 255), (0, 0), (0, WINDOW_HEIGHT-1), 1)
        pygame.draw.line(self.window, (255, 255, 255), (WINDOW_WIDTH-1, 0), (WINDOW_WIDTH-1, WINDOW_HEIGHT-1), 1)

    def render(self):
        self.window.fill((0,0,0))   #Erases all drawings from last frame
        self.snake.render()
        for sprite in self.sprites:
            self.window.blit(sprite.surface, sprite.rect)
        self.display_scores()
        self.window.blit(self.settings_btn.surface, self.settings_btn.rect)
        self.draw_borders()
        pygame.display.flip()

    #Displays game over text
    def you_lose(self):
        self.window.fill((0,0,0))
        self.display_scores()
        you_lose = EIGHT_BIT.render("Game Over, press ENTER to replay or ESC to quit.", (255,255,255))
        self.window.blit(you_lose[0], (15, WINDOW_HEIGHT/2))
        pygame.display.flip()

    #Called when the snake dies, allowing the player to play again or quit
    def game_over(self):
        self.you_lose()
        deciding = True     
        while deciding:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    deciding = False
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.init()
                        self.loop()
                        deciding = False

    #Game loop
    def loop(self):
        while self.running:
            self.handle_events()
            pressed_keys = pygame.key.get_pressed()
            self.snake.head.change_direction(pressed_keys)
            if self.snake.collided_body():
                self.snake.death_sound.play(self.sound)
                self.game_over()
                break
            if self.snake.head_collided_food(self.food_list):
                new_part = self.snake.grow()
                self.sprites.add(new_part)
                self.snake.eat_sound.play(self.sound)
                self.update_highscore()
                self.spawn_food()
            else:
                self.snake.slither()
            self.render()
            self.clock.tick(15)
        self.write_highscore()

#Entry point
if __name__ == '__main__':
    game = Game()
    game.init()
    game.loop()