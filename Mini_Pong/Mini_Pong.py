'''
Created on Jan 27, 2015

@author: Jack
'''

import pygame
import random
import datetime

LEFT_SIDE, RIGHT_SIDE = xrange(2)
SCREEN_WIDTH, SCREEN_HEIGHT = [19,14]
RESET_TO_AI_TIMER = 300
AI_DIFFICULTY = 0.2
FRAMERATE = 3000
exit_game = False

class Paddle(pygame.sprite.Sprite):
    def __init__(self, side):
        super(Paddle, self).__init__()
        self.image = pygame.Surface([1,3]).convert()
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect()
        if(side == LEFT_SIDE):
            self.rect.x = 0
        elif(side == RIGHT_SIDE):
            self.rect.x = SCREEN_WIDTH - 1
        self.rect.y = SCREEN_HEIGHT/2 - self.rect.height/2
        self.position = [float(self.rect.x), float(self.rect.y)]
        self.velocity = [0.0, 0.0]
        self.side = side
        
    def reset(self):
        self.position[1] = float(SCREEN_HEIGHT/2 - self.rect.height/2)
        
    def checkCollisions(self):
        #Check if we have collided with the ball
        collisions = pygame.sprite.spritecollide(self, sprites, False)
        #Make sure we don't collide with ourselves
        collisions.remove(self)
        if(collisions):
            #Invert the x component of the velocity of the ball, and speed it up a bit
            #Make sure the ball doesn't bounce inside the paddle
            if(((self.side == LEFT_SIDE) and (collisions[0].velocity[0] < 0.0)) 
               or ((self.side == RIGHT_SIDE) and (collisions[0].velocity[0] > 0.0))):
                collisions[0].velocity[0] *= -1.2
            #If the ball hits the edge of the paddle, redirect it out a bit
            if(collisions[0].rect.centery < self.rect.centery): collisions[0].velocity[1] -= 0.20
            if(collisions[0].rect.centery > self.rect.centery): collisions[0].velocity[1] += 0.20
        
    def update(self):
        #Velocity maxes out at 1px per frame
        if(self.velocity[0] >= 1.0): self.velocity[0] = 1.0
        if(self.velocity[1] >= 1.0): self.velocity[1] = 1.0
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
        
        #Check world boundaries
        if(self.position[1] < 0.0): self.position[1] = 0.0
        if(self.position[1] + float(self.rect.height) > float(SCREEN_HEIGHT)): self.position[1] = float(SCREEN_HEIGHT - self.rect.height)
                
        #Set sprite position to integer values
        self.rect.topleft = [round(self.position[0]), round(self.position[1])]

        self.checkCollisions()
        
class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super(Ball, self).__init__()
        self.image = pygame.Surface([2,2]).convert()
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect()
        self.reset(RIGHT_SIDE)
        self.maxspeed = 0.95
        
    def reset(self, last_point):
        #Set the ball to move away from whoever got the last point
        self.rect.topleft = [SCREEN_WIDTH/2 - self.rect.width/2,
                             SCREEN_HEIGHT/2 - self.rect.height/2]
        self.position = [float(self.rect.x), float(self.rect.y)]
        #Randomize the y velocity a bit, but keep the x velocity consistent
        if(last_point == LEFT_SIDE):
            self.velocity = [0.2, 0.25*(random.random()-0.5)]
        elif(last_point == RIGHT_SIDE):
            self.velocity = [-0.2, 0.25*(random.random()-0.5)]
    
    def update(self):
        #Clamp each component of our velocity at maxspeed
        if(self.velocity[0] >= self.maxspeed): self.velocity[0] = self.maxspeed
        if(self.velocity[1] >= self.maxspeed): self.velocity[1] = self.maxspeed
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
                
        #Set the sprite's position to integer values
        self.rect.topleft = (round(self.position[0]), round(self.position[1]))
        
        #bounce off the top and bottom of the screen
        if(self.rect.y <= 0): self.velocity[1] *= -1
        if(self.rect.y + self.rect.height >= SCREEN_HEIGHT): self.velocity[1] *= -1
        
        #Fixes issue where ball would get stuck at the top and bottom of the screen
        if(self.position[1] < 0.0): self.position[1] = 0.0
        if(self.position[1] + float(self.rect.height) > float(SCREEN_HEIGHT)): self.position[1] = float(SCREEN_HEIGHT - self.rect.height)
        
class Player(object):
    def __init__(self, paddle, score, side):
        self.paddle = paddle
        self.score = score
        self.aiTimer = 0
        self.speed = 0.5
            
    def moveUp(self):
        self.paddle.velocity[1] = -self.speed
        
    def moveDown(self):
        self.paddle.velocity[1] = self.speed
        
    def stop(self):
        self.paddle.velocity[1] = 0.0
        
    def displayScore(self):
        self.score.displayScore()
        
    def getPoint(self):
        self.score.addScore(1)
        
    def reset(self):
        self.paddle.reset()
        self.score.reset()
        
    def update(self):
        #Check if this player has been idle for a while, if so, we should be using AI
        if(self.aiTimer != 0):
            self.aiTimer -= 1
        else:
            #Check whose court is the ball in
            if(((self.paddle.side == LEFT_SIDE) and (ball.rect.centerx < SCREEN_WIDTH/2) and (ball.velocity[0] < 0.0))
               or ((self.paddle.side == RIGHT_SIDE) and (ball.rect.centerx > SCREEN_WIDTH/2) and (ball.velocity[0] > 0.0))):
                #If the ball is in our court, we should try and meet it at the edge of the screen
                #Find y-intercept at the edge of the screen
                if(self.paddle.side == LEFT_SIDE):
                    yintercept = -((ball.velocity[1]/ball.velocity[0])*float(ball.rect.centerx)) + float(ball.rect.centery)
                else:
                    yintercept = -((ball.velocity[1]/ball.velocity[0])*float(ball.rect.centerx - SCREEN_WIDTH)) + float(ball.rect.centery)
                #Add some error to the y-intercept to simulate the AI making errors
                yintercept += (1.0-AI_DIFFICULTY)*(SCREEN_HEIGHT*(random.random()-0.5))
                #Move towards that y-intercept
                self.paddle.velocity[1] = -((self.paddle.position[1] + self.paddle.rect.height/2) - yintercept)
            else:
                #If the ball is in the other player's court we should just follow it slowly
                self.paddle.velocity[1] = ball.velocity[1]*0.5
            #Double check that the paddle is not exceeding the player's speed
            if(self.paddle.velocity[1] > self.speed):
                self.paddle.velocity[1] = self.speed
            elif(self.paddle.velocity[1] < -self.speed):
                self.paddle.velocity[1] = -self.speed
            
class Score(pygame.sprite.Sprite):
    def __init__(self, number_sprites, side):
        super(Score, self).__init__()
        self.number_sprites = number_sprites
        
        self.image = self.number_sprites[0]
        self.rect = self.image.get_rect()
        if(side == LEFT_SIDE):
            self.rect.topleft = (1,1)
        elif(side == RIGHT_SIDE):
            self.rect.topleft = (SCREEN_WIDTH-self.rect.width-1,1)
        self.flashTimerMax = 15
        self.reset()
        
    def reset(self):
        self.points = 0
        self.displayScore()
        self.image = self.number_sprites[self.points]
        
    def displayScore(self):
        self.flashTimer = self.flashTimerMax
        self.image = self.number_sprites[self.points]
        
    def addScore(self, amt):
        self.points += amt
        self.flashTimer = self.flashTimerMax
        if(self.points < 10):
            self.image = self.number_sprites[self.points]
            
    def update(self):
        if(self.flashTimer != 0): 
            self.flashTimer -= 1
        else:
            self.image = self.number_sprites[len(self.number_sprites)-1]

if __name__ == '__main__':
    pygame.init()
    
    gamecolour = (255,255,255) #initialize the game colour to white
    #Pong is glad if it's friday
    if(datetime.datetime.today().weekday() == 4):
        gamecolour = (255,96,0)
    
    #Initialize the display, create a clock and set the key repeat
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN, 8)
    screen.set_palette([(0,0,0)]*256)
    screen.set_palette_at(0, gamecolour)
    pygame.key.set_repeat(0, 10)
    
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert()
    background.fill((0,0,0))
    
    #Create the scoreboard sprites
    number_sprites = []
    
    #Load the other scoreboard sprites
    numbers_image = pygame.image.load("ScoreBoard.png").convert()
    numbers_image.set_colorkey((0,0,0), pygame.RLEACCEL)
    numbers_image.set_palette(screen.get_palette())
    for i in xrange(0, 10):
        number_sprites.append(numbers_image.subsurface((i*3,0,3,5)))
        
    #The last sprite is blank so we can not draw the scoreboard
    blankimage = pygame.Surface([3,5]).convert()
    blankimage.fill((0,0,0))
    blankimage.set_colorkey((0,0,0), pygame.RLEACCEL)
    number_sprites.append(blankimage)
    
    #Create entities for the game
    ball = Ball()
    paddles = (Paddle(LEFT_SIDE), Paddle(RIGHT_SIDE))
    scoreboard = (Score(number_sprites, LEFT_SIDE), Score(number_sprites, RIGHT_SIDE))
    players = (Player(paddles[0], scoreboard[0], LEFT_SIDE), Player(paddles[1], scoreboard[1], RIGHT_SIDE))
    
    #Add all sprites to the sprite group
    sprites = pygame.sprite.Group()
    for paddle in paddles:
        sprites.add(paddle)
    sprites.add(ball)
    
    #Add the scoreboard to it's own group
    score_sprites = pygame.sprite.Group()
    for score in scoreboard:
        score_sprites.add(score)
    
    while(not exit_game):
        
        #Check for new key events
        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                exit_game = True
            elif (event.type == pygame.KEYDOWN):
                if (event.key == pygame.K_ESCAPE):
                    exit_game = True
                if (event.key == pygame.K_UP):
                    players[0].aiTimer = RESET_TO_AI_TIMER
                    players[0].moveUp()
                if (event.key == pygame.K_DOWN):
                    players[0].aiTimer = RESET_TO_AI_TIMER
                    players[0].moveDown()
            elif (event.type == pygame.KEYUP):
                if (event.key == pygame.K_UP):
                    players[0].aiTimer = RESET_TO_AI_TIMER
                    players[0].stop()
                if (event.key == pygame.K_DOWN):
                    players[0].aiTimer = RESET_TO_AI_TIMER
                    players[0].stop()
            
        #Update the sprites
        sprites.update()
        score_sprites.update()
        for player in players:
            player.update()
            
        #If the ball goes off screen, check which player gets a point, reset the ball
        if(ball.rect.x < -ball.rect.width):
            players[0].displayScore()
            players[1].getPoint()
            ball.reset(RIGHT_SIDE)
            for paddle in paddles: paddle.reset()
        elif(ball.rect.x > SCREEN_WIDTH):
            players[0].getPoint()
            players[1].displayScore()
            ball.reset(LEFT_SIDE)
            for paddle in paddles: paddle.reset()
            
        #If one player gets more than 9 points end the game and reset everything
        if((players[0].score.points > 9) or (players[1].score.points > 9)):
            ball.reset(RIGHT_SIDE)
            for player in players: player.reset()
            
        #Draw everything and wait one frame length
        screen.blit(background, (0,0))
        score_sprites.draw(screen)
        sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FRAMERATE)
        
    exit()