from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties
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

UPDATE_RATE = 10 #updates per sec
UPDATE_PERIOD = 1/UPDATE_RATE

# This helps reduce the amount of code used by loading objects, since all of
# the objects are pretty much the same.
def loadObject(tex=None, pos=LPoint3(0, 0), depth=SPRITE_POS, scale=1,
               transparency=True):
    # Every object uses the plane model and is parented to the camera
    # so that it faces the screen.
    obj = loader.loadModel("models/plane")
    obj.reparentTo(render)

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

# Function to put instructions on the screen.
def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1, 1, 1, 1), scale=.07,
                        shadow=(0, 0, 0, 1), parent=base.a2dTopLeft,
                        pos=(0.08, -pos - 0.04), align=TextNode.ALeft)


class GameView(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        # This code puts the standard title and instruction text on screen
        self.title = OnscreenText(text="2D Game of Life but it's 3D",
                                  parent=base.a2dBottomRight, scale=.07,
                                  align=TextNode.ARight, pos=(-0.1, 0.1),
                                  fg=(1, 1, 1, 1), shadow=(0, 0, 0, 0.5))

        #Game specific starting point
        self.g = grid.LifeGrid2D(2*SCREEN_X, 2*SCREEN_Y)
        grid.LifeGrid2D.sprinkle_life(self.g, 2*SPRINKLE_COUNT)
        self.sprinkle_timer = 0
        self.sim_step_timer = UPDATE_PERIOD

        # Disable default mouse-based camera control.  This is a method on the
        # ShowBase class from which we inherit.
        self.disableMouse()
        # Make the mouse invisible, turn off normal mouse controls
        self.disableMouse()
        props = WindowProperties()
        props.setCursorHidden(True)
        self.win.requestProperties(props)
        self.camLens.setFov(60)
        self.accept("escape", sys.exit)

        #Handle mouse input and movement
        self.heading = 0
        self.pitch = 0
        self.mousex = 0
        self.mousey = 0
        self.last = 0
        self.mousebtn = [0, 0, 0]
        self.keyboardbtn = {"w": 0, "a": 0, "s": 0, "d": 0, "lcontrol" : 0, "space": 0}
        self.accept("w", self.setKeyBtn, ["w", 1])
        self.accept("w-up", self.setKeyBtn, ["w", 0])
        self.accept("a", self.setKeyBtn, ["a", 1])
        self.accept("a-up", self.setKeyBtn, ["a", 0])
        self.accept("s", self.setKeyBtn, ["s", 1])
        self.accept("s-up", self.setKeyBtn, ["s", 0])
        self.accept("d", self.setKeyBtn, ["d", 1])
        self.accept("d-up", self.setKeyBtn, ["d", 0])
        self.accept("lcontrol", self.setKeyBtn, ["lcontrol", 1])
        self.accept("lcontrol-up", self.setKeyBtn, ["lcontrol", 0])
        self.accept("space", self.setKeyBtn, ["space", 1])
        self.accept("space-up", self.setKeyBtn, ["space", 0])
        self.accept("f3", self.toggleDebug, [])

        #setup debug text
        self.show_debug_text = False
        self.dtext_xyz = addInstructions(0.1, "TEST")
        self.dtext_heading = addInstructions(0.20, "TEST")
        self.dtext_pitch = addInstructions(0.3, "TEST")
        self.toggleDebug()
        self.toggleDebug()

        #Center the camera on the game grid
        self.camera.setPos(0, 0, 0)
        self.camera.setHpr(self.heading, self.pitch, 0)

        # Load the background color
        # self.setBackgroundColor((0.65, 0.65, 0.65, 1))

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
        self.cameraTask = taskMgr.add(self.controlCamera, "cameratask")

    def setKeyBtn(self, btn_key, value):
        self.keyboardbtn[btn_key] = value

    def toggleDebug(self):
        if self.show_debug_text:
            self.show_debug_text = False
            self.dtext_xyz.destroy()
            self.dtext_heading.destroy()
            self.dtext_pitch.destroy()
        else:
            self.show_debug_text = True

    def drawDebug(self):
        self.dtext_xyz.destroy()
        self.dtext_heading.destroy()
        self.dtext_pitch.destroy()
        dtext_heading_text = "Heading: {:.2f}".format(self.heading)
        dtext_pitch_text = "Pitch: {:.2f}".format(self.pitch)
        dtext_xyz_text = "[X, Y, Z]: {:.2f}, {:.2f}, {:.2f}".format(self.camera.getX(),
                                                        self.camera.getY(),
                                                        self.camera.getZ())
        self.dtext_xyz = addInstructions(0.07, dtext_xyz_text)
        self.dtext_heading = addInstructions(0.14, dtext_heading_text)
        self.dtext_pitch = addInstructions(0.21, dtext_pitch_text)


    def controlCamera(self, task):
        # figure out how much the mouse has moved (in pixels)
        md = self.win.getPointer(0)
        x = md.getX()
        y = md.getY()
        if self.win.movePointer(0, 100, 100):
            self.heading = self.heading - (x - 100) * 0.2
            self.pitch = self.pitch - (y - 100) * 0.2
        if self.pitch < -45:
            self.pitch = -45
        if self.pitch > 45:
            self.pitch = 45
        self.camera.setHpr(self.heading, self.pitch, 0)

        delta = globalClock.getDt()
        move_x = delta * 30 * -self.keyboardbtn['a'] + delta * 30 * self.keyboardbtn['d']
        move_y = delta * 30 * -self.keyboardbtn['lcontrol'] + delta * 30 * self.keyboardbtn['space']
        move_z = delta * 30 * self.keyboardbtn['s'] + delta * 30 * -self.keyboardbtn['w']
        self.camera.setPos(self.camera, move_x, -move_z, move_y)
        self.camera.setHpr(self.heading, self.pitch, 0)

        elapsed = task.time - self.last
        if self.last == 0:
            elapsed = 0
        if self.camera.getX() < -59.0:
            self.camera.setX(-59)
        if self.camera.getX() > 59.0:
            self.camera.setX(59)
        if self.camera.getY() < -59.0:
            self.camera.setY(-59)
        if self.camera.getY() > 59.0:
            self.camera.setY(59)
        if self.camera.getZ() < -20.0:
            self.camera.setZ(-20.0)
        if self.camera.getZ() > 45.0:
            self.camera.setZ(45)
        # self.focus = self.camera.getPos() + (dir * 5)
        self.last = task.time

        if self.show_debug_text:
            self.drawDebug()


        return Task.cont

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
        self.sim_step_timer += globalClock.getDt()
        if self.sim_step_timer > UPDATE_PERIOD:
            self.sim_step_timer -= UPDATE_PERIOD
            self.g.process_current_step()
            self.g.update_to_next_step()
            self.update_sprites()

        return Task.cont


if __name__ == "__main__":
    v = GameView()
    v.run()

