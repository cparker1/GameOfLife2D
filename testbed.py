from direct.showbase.ShowBase import ShowBase
from panda3d.core import LPoint3, LVector3
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode, TransparencyAttrib
from direct.task.Task import Task

import grid
from cell import LifeCell
from os import system
import sys
import time

# Constants that will control the behavior of the game. It is good to
# group constants like this so that they can be changed once without
# having to find everywhere they are used in code
SPRITE_POS = 80     # At default field of view and a depth of 55, the screen
# dimensions is 40x30 units
SCREEN_X = 40       # Screen goes from -20 to 20 on X
SCREEN_Y = 30       # Screen goes from -15 to 15 on Y

LIFECELL_SPRITES = {LifeCell.ALIVE: "alive.png",
                    LifeCell.HURT : "hurt.png",
                    LifeCell.DEAD : "dead.png"}

SPRINKLE_TIMER = 10
SPRINKLE_COUNT = int(2*SCREEN_X*2*SCREEN_Y/2)

# This helps reduce the amount of code used by loading objects, since all of
# the objects are pretty much the same.
def loadObject(tex=None, pos=LPoint3(0, 0), depth=SPRITE_POS, scale=1,
               transparency=True):
    # Every object uses the plane model and is parented to the camera
    # so that it faces the screen.
    obj = loader.loadModel("models/plane")
    obj.reparentTo(camera)

    # Set the initial position and scale.
    obj.setPos(pos.getX(), depth, pos.getY())
    obj.setScale(scale)

    # This tells Panda not to worry about the order that things are drawn in
    # (ie. disable Z-testing).  This prevents an effect known as Z-fighting.
    obj.setBin("unsorted", 0)
    obj.setDepthTest(False)

    if transparency:
        # Enable transparency blending.
        obj.setTransparency(TransparencyAttrib.MAlpha)

    if tex:
        # Load and set the requested texture.
        tex = loader.loadTexture("gfx/" + tex)
        obj.setTexture(tex, 1)

    return obj


class GameView(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        # This code puts the standard title and instruction text on screen
        self.title = OnscreenText(text="Testing",
                                  parent=base.a2dBottomRight, scale=.07,
                                  align=TextNode.ARight, pos=(-0.1, 0.1),
                                  fg=(1, 1, 1, 1), shadow=(0, 0, 0, 0.5))

        #Game specific starting point
        self.g = grid.LifeGrid2D(2*SCREEN_X, 2*SCREEN_Y)
        grid.LifeGrid2D.sprinkle_life(self.g, 2*SPRINKLE_COUNT)
        self.sprinkle_timer = 0

        # Disable default mouse-based camera control.  This is a method on the
        # ShowBase class from which we inherit.
        self.disableMouse()
        self.accept("escape", sys.exit)

        # Load the background color
        # self.setBackgroundColor((50, 50, 50, 1))

        #test loading model, loader function/class is a part of ShowBase
        self.cell_sprites = []
        for h in range(self.g.get_size()[0]):
            for w in range(self.g.get_size()[1]):
                new_sprite = loadObject(LIFECELL_SPRITES[LifeCell.DEAD],
                                        scale=1,
                                        transparency=True)
                new_sprite.setX(-SCREEN_X + w*(2*SCREEN_X)/(2*SCREEN_X)) #iterator times length/n
                new_sprite.setZ(-SCREEN_Y + h*(2*SCREEN_Y)/(2*SCREEN_Y))  # iterator times length/n
                self.cell_sprites.append([new_sprite, self.g.get_cell(h, w)])




        # Now we create the task. taskMgr is the task manager that actually
        # calls the function each frame. The add method creates a new task.
        # The first argument is the function to be called, and the second
        # argument is the name for the task.  It returns a task object which
        # is passed to the function each frame.
        self.gameTask = taskMgr.add(self.game_loop, "gameLoop")

    def update_sprites(self):
        for cellpack in self.cell_sprites:
            sprite = cellpack[0]
            cell = cellpack[1]
            status = cell.get_state()
            new_texture = loader.loadTexture("gfx/" + LIFECELL_SPRITES[status])
            sprite.setTexture(new_texture, 1)

    def game_loop(self, task):
        self.sprinkle_timer += globalClock.getDt()
        if self.sprinkle_timer > SPRINKLE_TIMER:
            self.sprinkle_timer = 0
            self.g.sprinkle_life(SPRINKLE_COUNT)

        #update the grid state
        self.g.process_current_step()
        self.g.update_to_next_step()
        self.update_sprites()
        time.sleep(0.25)
        return Task.cont


if __name__ == "__main__":

    v = GameView()
    v.run()
    # g = grid.LifeGrid2D(30, 13)
    # grid.LifeGrid2D.sprinkle_life(g, 100)
    # step_cnt = 0
    #
    # while True:
    #     system("cls")
    #     print("Ctrl+c to quit")
    #     g.process_current_step()
    #     g.update_to_next_step()
    #     step_cnt += 1
    #     g.print_grid()
    #     time.sleep(0.5)
    #     if g.was_there_change is False:
    #         g.sprinkle_life(100)
    #     elif step_cnt > 5:
    #         g.sprinkle_life(30)
    #         step_cnt = 0
    #
    #
