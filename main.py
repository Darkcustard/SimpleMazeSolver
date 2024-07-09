import pygame
import random
import time

width = 50
height = 50
line = 4


# Maze generation and sundries
resolution = pygame.Vector2(1000,1000)
maze = [[[False, False, False, False] for _ in range(width)] for _ in range(height)]
window = pygame.display.set_mode(resolution)
pygame.font.init()
width_ratio = resolution.x / (width*2)
height_ratio = resolution.y / (height*2)
cursor = (random.randint(0,width-1), random.randint(0,height-1))
clock = pygame.time.Clock()
move_cooldown = 0
move_time = 0

# Maze solver
start = (0,0)
end = (height-1, width-1)
closed = [(start,0,0)]
done = []
final = [(start,0,0)]
stalled = 0
solved = False
solved_index = None
solve_cooldown = 0
solve_time = 0



def get_draw_pos(a):
    return (width_ratio+a[1]*2*width_ratio,height_ratio+a[0]*2*height_ratio)

def check_range(a,bounds):
    if a[0] < 0: return False
    if a[0] > bounds[0]: return False
    if a[1] < 0: return False
    if a[1] > bounds[1]: return False
    return True

def move(maze, origin):
    
    # Find possible directions
    directions = [(-1,0),(0,1),(1,0),(0,-1)]
    opposite_i = [2,3,0,1]
    options = []
    for i, direction in enumerate(directions):
        new_pos = (origin[0]+direction[0], origin[1]+direction[1])
        if check_range(new_pos, (height-1,width-1)):
            if not maze[origin[0]][origin[1]][i] and maze[new_pos[0]][new_pos[1]] == [False, False, False, False]:
                options.append(i)

    # Case 1, Possible move
    if len(options) != 0:
        i = random.choice(options)
        direction = directions[i]
        maze[origin[0]][origin[1]][i] = True
        maze[origin[0]+direction[0]][origin[1]+direction[1]][opposite_i[i]]= True
        pygame.draw.line(window, (125,125,125),get_draw_pos(origin),get_draw_pos((origin[0]+direction[0], origin[1]+direction[1])),line)
        return (origin[0]+direction[0], origin[1]+direction[1])
    
    # Case 2, stuck
    direction_choices = []
    root_choices = []

    for r,row in enumerate(maze):
        for c,col in enumerate(row):

            # Find a point to branch off to
            if col != [False, False, False, False]:
                directions = [(-1,0),(0,1),(1,0),(0,-1)]
                for i, direction in enumerate(directions):
                    if check_range((r+direction[0],c+direction[1]),(height-1,width-1)):
                        if maze[r+direction[0]][c+direction[1]] == [False, False, False, False] and not  maze[r][c][i]:
                            direction_choices.append(direction)
                            root_choices.append((r,c))

    if len(direction_choices) > 0:
        
        index = random.randint(0,len(direction_choices)-1)
        direction = direction_choices[index]
        r,c = root_choices[index]
        i = directions.index(direction)

        maze[r][c][i] = True
        maze[r+direction[0]][c+direction[1]][opposite_i[i]] = True
        pygame.draw.line(window, (125,125,125),get_draw_pos((r,c)),get_draw_pos((r+direction[0], c+direction[1])),line)
        return (r+direction[0], c+direction[1])

            
    # Case 3, Done
    return (0,0)





while True:

    dt = clock.tick()/1000
    keys = pygame.key.get_pressed()
    move_time += dt
    solve_time += dt


    # Do maze creation move
    if stalled < 2:
        if move_time > move_cooldown:
            move_time = 0
            cursor = move(maze, cursor)
            if cursor == start:
                stalled += 1

    # Do maze solver move
    elif not solved and solve_time > solve_cooldown and pygame.key.get_pressed()[ord(" ")]:
        
        # Init move
        solve_time = 0
        options = []
        directions = [(-1,0),(0,1),(1,0),(0,-1)]
        opposite_i = [2,3,0,1]

        # Iterate over each explored node
        for coord, prev, g in closed:

            if coord == end:
                solved = True
                solved_index = final.index((coord,prev,g))

            # Check adjacent nodes of explored nodes
            exposed = False
            for i,direction in enumerate(directions):
                destination = (coord[0]+direction[0], coord[1]+direction[1])

                # Check if node in current direction is connected
                if maze[coord[0]][coord[1]][i]:

                    # Check if connected node isn't already explored
                    explored = False
                    for c, _, _ in closed:
                        if c == destination:
                            explored = True

                    for c,_,_ in done:
                        if c == destination:
                            explored = True

                    # Add to list of options
                    if not explored:
                        f = abs(destination[0]-end[0]) + abs(destination[1]-end[1])#+g+1 -> Depth first
                        options.append((destination, final.index((coord,prev,g)), g+1, f ))
                        exposed = True
                
            if not exposed:
                closed.remove((coord,prev,g))
                done.append((coord,prev,g))



        options.sort(key=lambda x : x[3])
        if len(options) > 0:
            best = options[0]
            pygame.draw.line(window, (255,255,255), get_draw_pos(best[0]), get_draw_pos(final[best[1]][0]), line)
            closed.append((best[0], best[1], best[2]))
            final.append((best[0],best[1],best[2]))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
 
    # Solved
    if solved:
        root = final[solved_index]
        destination = final[root[1]]

        while root != final[0]:
            pygame.draw.line(window, (0,255,0), get_draw_pos(root[0]), get_draw_pos(destination[0]),line)
            root = destination
            destination = final[root[1]]

    pygame.display.update()