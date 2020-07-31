class LifeCell(object):
    ERROR = -1
    DEAD = 0
    HURT = 1
    ALIVE = 2

    state_repr = {
        ERROR : "E",
        DEAD  : " ",
        HURT  : "-",
        ALIVE : "O"
    }

    neighbors = []
    state = ERROR

    def __init__(self, height_pos, width_pos):
        self.state = LifeCell.ERROR
        self.next_state = LifeCell.ERROR
        self.width_pos = width_pos
        self.height_pos = height_pos
        self.there_was_change = False
        pass

    def __repr__(self):
        return "Cell ({},{})".format(self.height_pos, self.width_pos)

    def get_neighbors(self):
        return self.neighbors

    def assign_neighbors(self, neighbors):
        self.neighbors = neighbors

    def print_state(self):
        if self.state in LifeCell.state_repr.keys():
            return LifeCell.state_repr[self.state]
        else:
            return "?"

    def get_state(self):
        return self.state

    def set_state(self, new_state):
        self.next_state = new_state
        if self.state != new_state:
            self.there_was_change = True

    def set_alive(self):
        self.set_state(LifeCell.ALIVE)

    def set_hurt(self):
        self.set_state(LifeCell.HURT)

    def set_dead(self):
        self.set_state(LifeCell.DEAD)

    def step(self):
        alive_cnt = 0
        for cell in self.neighbors:
            if cell.get_state() == LifeCell.ALIVE:
                alive_cnt += 1

        if self.state == LifeCell.DEAD:
            if alive_cnt > 3:
                self.set_alive()

        elif self.state == LifeCell.HURT:
            if alive_cnt < 3:
                self.set_dead()
            elif alive_cnt > 4:
                self.set_dead()
            else:
                self.set_alive()

        elif self.state == LifeCell.ALIVE:
            if alive_cnt < 2:
                self.set_dead()
            elif alive_cnt == 4:
                self.set_hurt()
            elif alive_cnt > 4:
                self.set_dead()

    def update(self):
        self.state = self.next_state
        self.there_was_change = False

    def get_change_bool(self):
        return self.there_was_change

if __name__ == "__main__":
    pass