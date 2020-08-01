import grid
from os import system
import time

if __name__ == "__main__":
    g = grid.LifeGrid2D(30, 13)
    grid.LifeGrid2D.sprinkle_life(g, 100)
    step_cnt = 0

    while True:
        system("cls")
        print("Ctrl+c to quit")
        g.process_current_step()
        g.update_to_next_step()
        step_cnt += 1
        g.print_grid()
        time.sleep(0.5)
        if g.was_there_change is False:
            g.sprinkle_life(100)
        elif step_cnt > 5:
            g.sprinkle_life(30)
            step_cnt = 0


