# 
#

class BodyPart extends pygame.sprite.Sprite{
    Surface surf;   #pygame object for a rectangular area to draw on
    Rect rect;      #coordinates representing the location of the part
    BodyPart(color) {
        #Calls the sprite's __init__ method
        #sets the surface color to the color in parameter
    }
}

class Direction extends enum {
    UP, DOWN, LEFT, RIGHT
}

class Head extends BodyPart {
    Direction direction;
    Head(color) {
        #calls the superclass' __init__ to give the head a color
    }
    change_dir(pressed_keys) {
        #Changes the head's direction
    }
    move() {
        #Updates the head's location based on the current direction 
    }
}

class Snake {
    Head head
    List parts
    Snake(int length){
        #contruct snake 
    }
    void slither(){
        #Move each part of the snake to the position of the part before it
    }
    void grow(){
    }
    head.move()
}

main() {
    #initialize the game
    #start the snake with a fixed length
    #print out highscore and current score
    
    write_highscore(int highscore) {
        #saves new highscore to a local file
    }
    
    int read_highscore() {
        #retrieve highscore from local file
    }
}