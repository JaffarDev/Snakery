import random
import tkinter
import functools
import pygame
import pygame.freetype

#Game window dimensions
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 400

pygame.init()
JOKERMAN = pygame.freetype.Font("res/fonts/JOKERMAN.ttf", 17)
EIGHT_BIT = pygame.freetype.Font("res/fonts/8-BIT.ttf", 17)

#Spawns at a random location within the screen, snake grows when collided with this game object
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
    #Snake cannot go in the opposite of its current direction, as it would result in instant death
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
    #Checks if the head has moved beyond the window, in which case it comes out of the other side of the window.
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
    def __init__(self, color, secondary_color, length):
        self.color = color
        self.secondary_color = secondary_color
        self.eat_sound = Sound("res/sounds/bite.WAV")
        self.death_sound = Sound("res/sounds/death.WAV")
        self.head = Head(self.color, WINDOW_WIDTH/2, WINDOW_HEIGHT/2)
        self.parts = []
        self.parts.append(self.head)
        for i in range(1, length):
            left = self.parts[i-1].rect.left - self.parts[i-1].rect.width
            top = self.parts[i-1].rect.top
            part = BodyPart(self.color, left, top)
            self.parts.append(part)

    def change_color(self, hex_color):
        self.color = Color.to_rgb(hex_color)
        for part in self.parts:
            part.surface.fill(self.color)

    def change_sec_color(self, hex_color):
        self.secondary_color = Color.to_rgb(hex_color)

    #Draws stripes on each snake part.
    #Each part has a stripe between it and the block after it in the list of parts.
    def draw_stripes(self):
        for i in range(len(self.parts)-1):
            x_diff = self.parts[i].rect.left - self.parts[i+1].rect.left
            y_diff = self.parts[i].rect.top - self.parts[i+1].rect.top
            if x_diff > 0:
                pygame.draw.line(self.parts[i].surface, self.secondary_color, (1,1), (1,8), 1)
            elif x_diff < 0:
                pygame.draw.line(self.parts[i].surface, self.secondary_color, (8,1), (8,8), 1)
            elif y_diff > 0:
                pygame.draw.line(self.parts[i].surface, self.secondary_color, (1,1), (8,1), 1)
            else:
                pygame.draw.line(self.parts[i].surface, self.secondary_color, (1,8), (8,8), 1)
    
    #Renders the snake
    #The method fill is called for every part to erase stripes/eyes drawn in previous frames
    def render(self):
        for part in self.parts:
            part.surface.fill(self.color)
        self.head.draw_eyes(self.secondary_color)
        self.draw_stripes()

    #The snake is moved by moving each part to the location of the part before it in the list of parts (except the head)
    def slither(self):
        last_index = len(self.parts) - 1
        for i in range(last_index, 0, -1):
            self.parts[i].rect.left = self.parts[i-1].rect.left
            self.parts[i].rect.top = self.parts[i-1].rect.top
        self.head.move()
    
    #Adds a new BodyPart to the snake, placing it at the snake's head's location, the snake's head is then moved.
    #NOTE: if grow is called, there is no need to call slither during the same frame because grow places the newly created part
    #in the head's location, the the head is moved, thus creating the slither effect in a more efficient way
    def grow(self):
        part = BodyPart(self.color, self.head.rect.left, self.head.rect.top)
        self.parts.insert(1, part)
        self.head.move()
        return part

    #The snake grows if the head collided with food.
    def collided_food(self, food, sprites):
        food_eaten = pygame.sprite.spritecollide(self.head, food, True)
        if len(food_eaten) != 0:
            new_part = self.grow()
            sprites.add(new_part)
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
        self.root = tkinter.Tk()
        self.root.title(string = "Settings")
        self.root.minsize(width = 220, height = 210)
        self.frame = tkinter.Frame(master = self.root)
        self.frame.pack()
        self.game = game
        self.sound = tkinter.BooleanVar()
        self.confirmation = False                       #Keeps track of whether the reset highscore confirmation window is on-screen
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
                                             variable = self.sound, command = self.on_toggle)
        sound_checkbtn.pack(pady = 7)

    def reset_highscore(self):
        self.game.reset_highscore()
        self.game.update_highscore()
        self.exit_conf_window()

    #Exits the reset highscore confirmation window
    def exit_conf_window(self):
        self.confirmation = False
        self.window.destroy()

    #Window used to confirm the resetting of the highscore
    def confirm_window(self):
        if self.confirmation:
            return
        self.window = tkinter.Toplevel(self.root)
        self.window.title(string = "Confirm")
        self.window.protocol("WM_DELETE_WINDOW", self.exit_conf_window)
        label = tkinter.Label(master = self.window, text = "Do you wish to reset the current highscore?", fg = "red")
        label.pack()
        btn_frame = tkinter.Frame(master = self.window)
        btn_frame.pack()
        yes_btn = tkinter.Button(master = btn_frame, text = "Yes", fg = "black", command = self.reset_highscore)
        no_btn = tkinter.Button(master = btn_frame, text = "No", fg = "black", command = self.exit_conf_window)
        yes_btn.pack(side = tkinter.LEFT, padx = 5, pady = 1)
        no_btn.pack(side = tkinter.LEFT, padx = 5, pady = 1)
        self.center(self.window)
        self.confirmation = True

    def add_widgets(self):
        paused_lbl = tkinter.Label(master = self.frame, text = "Paused", fg = "red", font = "Times 18")
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
        colors_lbl = tkinter.Label(master = self.frame, text = desc)
        colors_lbl.pack()
        colors_frm = tkinter.Frame(master = self.frame)
        colors_frm.pack()
        for key, value in colors.items():
            color_btn = tkinter.Button(master = colors_frm, width = 1, height = 1, 
                                       bg = value, command = functools.partial(on_click, value))
            color_btn.pack(side = tkinter.LEFT)

class Game():
    ADDFOOD = pygame.USEREVENT + 1  #Custom Event used to spawn food a short while after the game starts
    def __init__(self):
        pygame.display.set_caption("Snake Game")
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
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
        self.window.blit(score[0], (10, 10))
        self.window.blit(highscore[0], (WINDOW_WIDTH/2 - highscore[1].width/2, 10))

    #Called at the beginning of the game and then each time the player loses and decides to play again.
    #Color and secondary color are supplied based on the snake's color and secondary color's values at the time the snake died.
    def newgame(self, color, secondary_color):
        self.snake = Snake(color, secondary_color, 5)
        self.food = pygame.sprite.Group()                   #Used to detect collision of the head with food
        self.sprites = pygame.sprite.Group()                #Every sprite is added to this group for rendering
        self.sprites.add(iter(self.snake.parts))            #Add all of the snake's parts
        self.update_highscore()
        pygame.time.set_timer(Game.ADDFOOD, 1500, True)     #A one-time timer to spawn the food 1.5 secs after the game started

    def spawn_food(self):
        food = Food()
        self.sprites.add(food)
        self.food.add(food)

    #Called at each frame to handle the game's events
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == Game.ADDFOOD:
                self.spawn_food()
            elif event.type == pygame.MOUSEBUTTONUP:
                self.settings_btn.was_clicked(event.pos[0], event.pos[1])

    #Renders all sprites to the screen and displays the score
    def render(self):
        self.window.fill((0,0,0))   #Erases all drawings from last frame
        self.snake.render()
        for sprite in self.sprites:
            self.window.blit(sprite.surface, sprite.rect)
        self.display_scores()
        self.window.blit(self.settings_btn.surface, self.settings_btn.rect)
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
                if event.type == pygame.QUIT:
                    deciding = False
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.newgame(self.snake.color, self.snake.secondary_color)
                        self.loop()
                        deciding = False
                    elif event.key == pygame.K_ESCAPE:
                        deciding = False
                        self.running = False

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
            if self.snake.collided_food(self.food, self.sprites):
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
    game.newgame((0,255,255), (0,0,0))
    game.loop()