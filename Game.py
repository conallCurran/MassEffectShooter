#! /usr/bin/env python

# Space Shooter.
# A scrolling arcade shooter.

#
#   Copyright (C) 2009  Tyler Gray, Chad Haley
#   I adapted space shooter and used its contents as my template for this pythin game.
#   All code has been re written by Conall Curran for the Mass effect game
#   Copyright BioWare and EA Games.




import os, sys, pygame, random
from pygame.locals import *

os.environ['SDL_VIDEO_CENTERED'] = "1"
pygame.init()
pygame.display.set_caption("Mass Effect")
icon = pygame.image.load("img/Space Shooter.png")
icon = pygame.display.set_icon(icon)
screen = pygame.display.set_mode((800, 600))
pygame.mouse.set_visible(0)

background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((0, 0, 0))

music = pygame.mixer.music.load("music/score.mp3")
pygame.mixer.music.play(2)



def load_image(name, colorkey=None):
    fullname = os.path.join(name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()


def load_sound(name):
    class NoneSound:
        def play(self): pass

    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join(name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print 'Cannot load sound:', fullname
        raise SystemExit, message
    return sound



class Arena(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("img/MassEffect.jpg", -1)
        self.dy = 0
        self.reset()

    def update(self):
        self.rect.bottom += self.dy
        if self.rect.bottom >= 1000:
            self.reset()

    def reset(self):
        self.rect.top = -100


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("img/normandy2.png", -1)
        self.rect.center = (400, 500)
        self.dx = 0
        self.dy = 0
        self.reset()
        self.lasertimer = 0
        self.lasermax = 5
        self.bombamount = 1
        self.bombtimer = 0
        self.bombmax = 10

    def update(self):
        self.rect.move_ip((self.dx, self.dy))

        #Fire the laser
        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE]:
            self.lasertimer = self.lasertimer + 1
            if self.lasertimer == self.lasermax:
                laserSprites.add(Laser(self.rect.midtop))
                fire.play()
                self.lasertimer = 0

        #Fire the bomb
        if key[pygame.K_LCTRL]:
            self.bombtimer = self.bombtimer + 1
            if self.bombtimer == self.bombmax:
                self.bombtimer = 0
                if self.bombamount > 0:
                    self.bombamount = self.bombamount - 1
                    score.bomb += -1
                    bombSprites.add(Bomb(self.rect.midtop))
                    torpedo.play()


        #Player Boundaries
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > 800:
            self.rect.right = 800

        if self.rect.top <= 260:
            self.rect.top = 260
        elif self.rect.bottom >= 600:
            self.rect.bottom = 600


    def reset(self):
        self.rect.bottom = 600


class Laser(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("img/laser1.png", -1)
        self.rect.center = pos


    def update(self):
        if self.rect.top < 0:
            self.kill()
        else:
            self.rect.move_ip(0, -15)


class Bomb(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("img/torpedo1.png", -1)
        self.rect.center = pos

    def update(self):
        if self.rect.top < 0:
            self.kill()
        else:
            self.rect.move_ip(0, -5)
        if pygame.sprite.groupcollide(enemySprites, bombSprites, 1, 1):
            bombExplosionSprites.add(BombExplosion(self.rect.center))
            explode.play()


class EnemyLaser(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("img/laser2.png", -1)
        self.rect.center = pos


    def update(self):
        if self.rect.bottom < 0:
            self.kill()
        else:
            self.rect.move_ip(0, 15)


#Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, centerx):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("img/enemy.png", -1)
        self.rect = self.image.get_rect()
        self.dy = 8
        self.reset()

    def update(self):
        self.rect.centerx += self.dx
        self.rect.centery += self.dy
        if self.rect.top > screen.get_height():
            self.reset()

        #random 1 - 60 determines if firing
        efire = random.randint(1, 40)
        if efire == 1:
            enemyLaserSprites.add(EnemyLaser(self.rect.midbottom))
            efire = load_sound("sounds/laser.ogg")
            efire.play()

        #Laser Collisions
        if pygame.sprite.groupcollide(enemySprites, laserSprites, 1, 1):
            explosionSprites.add(EnemyExplosion(self.rect.center))
            explode.play()
            score.score += 10

        #Bomb Collisions
        if pygame.sprite.groupcollide(enemySprites, bombSprites, 1, 1):
            bombExplosionSprites.add(BombExplosion(self.rect.center))
            explode.play()
            score.score += 10

        #Bomb Explosion Collisions
        if pygame.sprite.groupcollide(enemySprites, bombExplosionSprites, 1, 0):
            explosionSprites.add(EnemyExplosion(self.rect.center))
            explode.play()
            score.score += 10


    def reset(self):
        self.rect.bottom = 0
        self.rect.centerx = random.randrange(0, screen.get_width())
        self.dy = random.randrange(5, 10)
        self.dx = random.randrange(-2, 2)


class Shield(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("img/Bubble.png", 4)
        self.rect.center = pos
        self.counter = 0
        self.maxcount = 2

    def update(self):
        self.counter = self.counter + 1
        if self.counter == self.maxcount:
            self.kill()


class EnemyExplosion(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("img/oursin.png", -1)
        self.rect.center = pos
        self.counter = 0
        self.maxcount = 10

    def update(self):
        self.counter = self.counter + 1
        if self.counter == self.maxcount:
            self.kill()


class BombExplosion(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("img/bombexplosion.png", -1)
        self.rect.center = pos
        self.counter = 0
        self.maxcount = 5

    def update(self):
        self.counter = self.counter + 1
        if self.counter == self.maxcount:
            self.kill()


class BombPowerup(pygame.sprite.Sprite):
    def __init__(self, centerx):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("img/torpedopowerup.png", -1)
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randrange(0, screen.get_width())


    def update(self):
        if self.rect.top > screen.get_height():
            self.kill
        else:
            self.rect.move_ip(0, 6)


class ShieldPowerup(pygame.sprite.Sprite):
    def __init__(self, centerx):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("img/shieldpowerup.png", -1)
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randrange(0, screen.get_width())


    def update(self):
        if self.rect.top > screen.get_height():
            self.kill
        else:
            self.rect.move_ip(0, 6)


class Score(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.shield = 100
        self.score = 0
        self.bomb = 1
        self.font = pygame.font.Font("fonts/arial.ttf", 28)

    def update(self):
        self.text = "Shield: %d                        Score: %d                        Torpedo: %d" % (
            self.shield, self.score, self.bomb)
        self.image = self.font.render(self.text, 1, (0, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (400, 20)


class Gameover(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font("fonts/planet5.ttf", 48)

    def update(self):
        self.text = ("GAME OVER")
        self.image = self.font.render(self.text, 1, (0, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (400, 300)


class Gameoveresc(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font("fonts/arial.ttf", 28)

    def update(self):
        self.text = "PRESS ESC TO RETURN"
        self.image = self.font.render(self.text, 1, (0, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (400, 400)


def game():
    #Game Objects
    global player
    player = Player()
    global score
    score = Score()

    global fire
    fire = load_sound("sounds/laser.ogg")
    global explode
    explode = load_sound("sounds/explode.ogg")
    global torpedo
    torpedo = load_sound("sounds/torpedo.ogg")
    global powerup
    powerup = load_sound("sounds/powerup.ogg")


    playerSprite = pygame.sprite.RenderPlain((player))

    global enemySprites
    enemySprites = pygame.sprite.RenderPlain(())
    enemySprites.add(Enemy(200))
    enemySprites.add(Enemy(300))
    enemySprites.add(Enemy(400))

    global laserSprites
    laserSprites = pygame.sprite.RenderPlain(())

    global bombSprites
    bombSprites = pygame.sprite.RenderPlain(())
    global enemyLaserSprites
    enemyLaserSprites = pygame.sprite.RenderPlain(())

    global bombPowerups
    bombPowerups = pygame.sprite.RenderPlain(())
    global shieldPowerups
    shieldPowerups = pygame.sprite.RenderPlain(())

    shieldSprites = pygame.sprite.RenderPlain(())

    global explosionSprites
    explosionSprites = pygame.sprite.RenderPlain(())

    global bombExplosionSprites
    bombExplosionSprites = pygame.sprite.RenderPlain(())

    scoreSprite = pygame.sprite.Group(score)
    gameOverSprite = pygame.sprite.RenderPlain(())

    arena = Arena()
    arena = pygame.sprite.RenderPlain((arena))


    clock = pygame.time.Clock()
    keepGoing = True
    counter = 0

    while keepGoing:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    keepGoing = False
                elif event.key == pygame.K_LEFT:
                    player.dx = -10
                elif event.key == K_RIGHT:
                    player.dx = 10
                elif event.key == K_UP:
                    player.dy = -10
                elif event.key == K_DOWN:
                    player.dy = 10
            elif event.type == KEYUP:
                if event.key == K_LEFT:
                    player.dx = 0
                elif event.key == K_RIGHT:
                    player.dx = 0
                elif event.key == K_UP:
                    player.dy = 0
                elif event.key == K_DOWN:
                    player.dy = 0




        screen.blit(background, (0, 0))
        playerSprite.update()
        enemySprites.update()
        laserSprites.update()
        bombSprites.update()
        enemyLaserSprites.update()
        bombPowerups.update()
        shieldPowerups.update()
        shieldSprites.update()
        explosionSprites.update()
        bombExplosionSprites.update()
        arena.update()
        scoreSprite.update()
        gameOverSprite.update()

        arena.draw(screen)
        playerSprite.draw(screen)
        enemySprites.draw(screen)
        laserSprites.draw(screen)
        bombSprites.draw(screen)
        enemyLaserSprites.draw(screen)
        bombPowerups.draw(screen)
        shieldPowerups.draw(screen)
        shieldSprites.draw(screen)
        explosionSprites.draw(screen)
        bombExplosionSprites.draw(screen)
        scoreSprite.draw(screen)
        gameOverSprite.draw(screen)
        pygame.display.flip()

        counter += 1
        if counter >= 20:
            enemySprites.add(Enemy(300))
            counter = 0

        spawnShieldpowerup = random.randint(1, 500)
        if spawnShieldpowerup == 1:
            shieldPowerups.add(ShieldPowerup(300))


        spawnBombpowerup = random.randint(1, 500)
        if spawnBombpowerup == 1:
            bombPowerups.add(BombPowerup(300))
            bombPowerupcounter = 0


        for hit in pygame.sprite.groupcollide(enemyLaserSprites, playerSprite, 1, 0):
            explode.play()
            explosionSprites.add(Shield(player.rect.center))
            score.shield -= 10
            if score.shield <= 0:
                gameOverSprite.add(Gameover())
                gameOverSprite.add(Gameoveresc())
                playerSprite.remove(player)


        for hit in pygame.sprite.groupcollide(enemySprites, playerSprite, 1, 0):
            explode.play()
            explosionSprites.add(Shield(player.rect.center))
            score.shield -= 10
            if score.shield <= 0:
                gameOverSprite.add(Gameover())
                gameOverSprite.add(Gameoveresc())
                playerSprite.remove(player)

        for hit in pygame.sprite.groupcollide(shieldPowerups, playerSprite, 1, 0):
            if score.shield < 100:
                powerup.play()
                score.shield += 10

        for hit in pygame.sprite.groupcollide(bombPowerups, playerSprite, 1, 0):
            powerup.play()
            player.bombamount += 1
            score.bomb += 1


class SpaceMenu:
    def __init__(self, *options):

        self.options = options
        self.x = 0
        self.y = 0
        self.font = pygame.font.Font(None, 32)
        self.option = 0
        self.width = 1
        self.color = [0, 0, 0]
        self.hcolor = [0, 0, 0]
        self.height = len(self.options) * self.font.get_height()
        for o in self.options:
            text = o[0]
            ren = self.font.render(text, 1, (0, 0, 0))
            if ren.get_width() > self.width:
                self.width = ren.get_width()


    def draw(self, surface):
        i = 0
        for o in self.options:
            if i == self.option:
                clr = self.hcolor
            else:
                clr = self.color
            text = o[0]
            ren = self.font.render(text, 1, clr)
            if ren.get_width() > self.width:
                self.width = ren.get_width()
            surface.blit(ren, (self.x, self.y + i * self.font.get_height()))
            i += 1

            #Menu Input

    def update(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_DOWN:
                    self.option += 1
                if e.key == pygame.K_UP:
                    self.option -= 1
                if e.key == pygame.K_RETURN:
                    self.options[self.option][1]()
        if self.option > len(self.options) - 1:
            self.option = 0
        if self.option < 0:
            self.option = len(self.options) - 1


    def set_pos(self, x, y):
        self.x = x
        self.y = y

    def set_font(self, font):
        self.font = font

    def set_highlight_color(self, color):
        self.hcolor = color

    def set_normal_color(self, color):
        self.color = color

    def center_at(self, x, y):
        self.x = x - (self.width / 2)
        self.y = y - (self.height / 2)


def missionMenu():
    arena = Arena()
    arena = pygame.sprite.RenderPlain((arena))


    #Title for Option Menu
    menuTitle = SpaceMenu(
        ["Mass Effect"])

    #Option Menu Text
    instructions = SpaceMenu(
        [""],
        [""],
        ["Earth is ground zero in the war to save the Galaxy"],
        [""],
        ["Sheperd and his team are the only hope left to mankind!"],
        [""],
        ["Navigate the Normandy with the arrow keys and use"],
        [""],
        ["the space bar to fire the proton laser. Use the left CTRL"],
        [""],
        ["key to shoot a torpedo. Be careful, you have a limited"],
        [""],
        ["supply. Kill as many reapers as you can!"],
        [""],
        [""],
        ["                   PRESS ESC TO RETURN                    "])

    menuTitle.center_at(150, 150)
    menuTitle.set_font(pygame.font.Font("fonts/planet5.ttf", 48))
    menuTitle.set_highlight_color((0, 255, 0))


    instructions.center_at(440, 350)

    instructions.set_font(pygame.font.Font("fonts/arial.ttf", 22))

    instructions.set_normal_color((0, 255, 0))


    clock = pygame.time.Clock()
    keepGoing = True

    while keepGoing:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    keepGoing = False
        screen.blit(background, (0, 0))
        arena.update()
        arena.draw(screen)
        menuTitle.draw(screen)
        instructions.draw(screen)
        pygame.display.flip()


def aboutMenu():
    #Arena
    arena = Arena()
    arena = pygame.sprite.RenderPlain((arena))

    #About Menu Text
    #Title for Option Menu
    menuTitle = SpaceMenu(
        ["Mass Effect"])

    info = SpaceMenu(
        [""],
        [""],
        ["Adapted by Conall Curran from Space Shooter Beta"],
        [""],
        [" That was devloped by the Monty Pythons."],
        [""],
        ["Student's from Mr. Raza's DPT 110 class"],
        [""],
        [""],
        ["Mass Effect is Copyright of BioWare and EA Games."],
        [""],
        ["      PRESS ESC TO RETURN            "])


    menuTitle.center_at(150, 150)
    menuTitle.set_font(pygame.font.Font("fonts/planet5.ttf", 48))
    menuTitle.set_highlight_color((0, 255, 0))

    info.center_at(400, 310)

    info.set_font(pygame.font.Font("fonts/arial.ttf", 28))

    #About Menu Font Color
    info.set_normal_color((0, 255, 0))


    #Set Clock
    clock = pygame.time.Clock()
    keepGoing = True

    while keepGoing:
        clock.tick(30)
        #input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    keepGoing = False
        #Draw
        screen.blit(background, (0, 0))
        arena.update()
        arena.draw(screen)
        menuTitle.draw(screen)
        info.draw(screen)
        pygame.display.flip()


#Functions

def option1():
    game()


def option2():
    missionMenu()


def option3():
    aboutMenu()


def option4():
    pygame.quit()
    sys.exit()


def main():
    arena = Arena()
    arena = pygame.sprite.RenderPlain((arena))



    menuTitle = SpaceMenu(
        ["Mass Effect"])

    menu = SpaceMenu(
        ["Start", option1],
        ["Misson", option2],
        ["About", option3],
        ["Quit", option4])



    menuTitle.center_at(150, 150)
    menuTitle.set_font(pygame.font.Font("fonts/planet5.ttf", 48))
    menuTitle.set_highlight_color((0, 255, 0))

    menu.center_at(400, 320)
    menu.set_font(pygame.font.Font("fonts/arial.ttf", 32))
    menu.set_highlight_color((0, 255, 0))
    menu.set_normal_color((0, 85, 0))

    clock = pygame.time.Clock()
    keepGoing = True

    while 1:
        clock.tick(30)

        events = pygame.event.get()

        menu.update(events)

        for e in events:
            if e.type == pygame.QUIT:
                pygame.quit()
                return

        screen.blit(background, (0, 0))
        arena.update()
        arena.draw(screen)
        menu.draw(screen)
        menuTitle.draw(screen)
        pygame.display.flip()


if __name__ == "__main__":
    main()
