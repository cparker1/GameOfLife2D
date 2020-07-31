import Cell
import random
import itertools

class LifeGrid2D(object):

    def __init__(self, width, height):
        self.width = width #must be >2
        self.height = height #must be >2
        self.was_there_change = False
        self.grid = [[Cell.LifeCell(h, w) for w in range(width)] for h in range(height)]
        self.set_start_states()
        self.update_to_next_step()

    def set_start_states(self):
        for h, row in enumerate(self.grid):
            for w, cell in enumerate(row):
                cell.set_dead()
                cell.assign_neighbors(self.get_cell_neighbors(h, w))

    def sprinkle_life(self, count):
        for _ in range(count):
            h = random.randrange(0, self.height)
            w = random.randrange(0, self.width)
            self.grid[h][w].set_alive()
        self.update_to_next_step()

    def process_current_step(self):
        self.was_there_change = False
        for h, row in enumerate(self.grid):
            for w, cell in enumerate(row):
                cell.step()
                self.was_there_change |= cell.get_change_bool()

    def update_to_next_step(self):
        for h in self.grid:
            for w in h:
                w.update()

    def print_grid(self):
        print("\n")
        for row in self.grid:
            row_str = ""
            for cell in row:
                row_str = "{} {}".format(row_str, cell.print_state())
            print(row_str)
        print(self.was_there_change)

    def get_cell_neighbors(self, cell_h, cell_w):
        up    = cell_h - 1
        down  = cell_h + 1
        left  = cell_w - 1
        right = cell_w + 1

        # Using a wrapping scheme, i.e. far left is adjacent to far right
        #wrap bottom to top. toroidal.
        if up < 0: up = self.height - 1
        if down > self.height - 1: down = 0
        if left < 0: left = self.width - 1
        if right > self.width - 1: right = 0

        return [self.grid[up][cell_w],
                self.grid[down][cell_w],
                self.grid[cell_h][left],
                self.grid[cell_h][right],
                self.grid[up][left],
                self.grid[up][right],
                self.grid[down][left],
                self.grid[down][right]]


if __name__ == "__main__":
    g = LifeGrid2D(10,10)
    while input("Enter 'Q' to quit") != "Q":
        g.process_current_step()
        g.update_to_next_step()
        g.print_grid()