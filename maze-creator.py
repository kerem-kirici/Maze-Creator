import cv2
import random
import numpy as np
from PIL import Image
import time
import os


class Maze:

    DIFFICULTY_LEVELS = {0: 0.2, 1: 0.4, 2: 0.7}
    POP_INDEXES = {0: lambda s: -1, 1: lambda s: s//2, 2: lambda s: 0}

    def __init__(self, size, difficulty_level, render_quality, show=False):
        self.size = size
        self.show = show
        self.render_quality = render_quality

        # to make maze's sides an odd number
        self.grid_size = (self.size[0] * 2 + 1, self.size[1] * 2 + 1)
        self.keys = {"road": 0, "wall": 1}

        self.maze = [[self.keys["wall"] for j in range(self.grid_size[1])] for i in range(self.grid_size[0])]

        self.starting_position = (0, 1)
        self.maze[self.starting_position[0]][self.starting_position[1]] = 0
        self.maze[0][1] = 0
        self.current_direction = "down"
        self.position = self.starting_position

        self.up = lambda coord, n: (coord[0] - n, coord[1])
        self.down = lambda coord, n: (coord[0] + n, coord[1])
        self.left = lambda coord, n: (coord[0], coord[1] - n)
        self.right = lambda coord, n: (coord[0], coord[1] + n)
        self.directions = ["up", "down", "left", "right"]
        self.opposite_directions = {"up": "down", "down": "up", "left": "right", "right": "left", None: None}

        # to return position where there is more than 1 possible direction
        self.break_up_points = []

        self.colors = {self.keys["road"]: (255, 255, 255), self.keys["wall"]: (100, 75, 100), "start": (100, 255, 100), "end": (100, 100, 255)}
        self.image_resize_constant = 800//max(self.grid_size)
        
        self.difficulty = Maze.DIFFICULTY_LEVELS[difficulty_level]
        self.difficulty_level = difficulty_level
        self.difficulties = {0: "Easy", 1: "Medium", 2: "Hard"}

        self.animation = True
        self.save_img = False

        self.distance = 0
        self.distances = {}
        self.end_point_distance = 0
        self.end_point = None

        if not os.path.isdir("images"):
            os.mkdir("images")

        self.file_name = f"{self.size[0]}-{self.size[1]}-Maze-{self.difficulties[self.difficulty_level]}-{int(time.time())}.jpg"

    def render(self):
        img_size = (self.grid_size[0]*self.render_quality, self.grid_size[1]*self.render_quality)
        env_image = np.zeros((img_size[0], img_size[1], 3), dtype=np.uint8)

        for i in range(img_size[0]):
            for j in range(img_size[1]):
                maze_i, maze_j = i//self.render_quality, j//self.render_quality
                if self.maze[maze_i][maze_j] != self.keys["wall"]:
                    if (maze_i, maze_j) == self.starting_position:
                        env_image[i][j] = self.colors["start"]
                    elif (maze_i, maze_j) == self.position:
                        env_image[i][j] = self.colors["end"]
                    else:
                        env_image[i][j] = self.colors[self.keys["road"]]
                else:
                    env_image[i][j] = self.colors[self.keys["wall"]]

        img = Image.fromarray(env_image, "RGB")
        resize_shape = [self.grid_size[0]*self.image_resize_constant, self.grid_size[1]*self.image_resize_constant]

        if resize_shape[0] > resize_shape[1]:
            resize_shape[1] = resize_shape[1] * max(self.grid_size)**2 // min(self.grid_size)**2
        elif resize_shape[0] < resize_shape[1]:
            resize_shape[0] = resize_shape[0] * max(self.grid_size)**2 // min(self.grid_size)**2
        resize_shape = tuple(resize_shape)

        img = np.array(img.resize(resize_shape))
        if self.save_img:
            cv2.imwrite(os.path.join("./images/", self.file_name), img)
        if self.show:
            #print(f"end_point: {self.end_point}, end_point_distance: {self.end_point_distance}, current_distance: {self.distance}")
            cv2.imshow("image", img)
            cv2.waitKey(int(self.animation))

    def create_maze(self):
        done = False

        self.action(self.current_direction, 1)

        while not done:
            self.action()
            done = self.finished()

            if self.save_img or self.show:
                self.render()

            if done:
                assert self.end_point != None
                self.animation = False
                self.save_img = True
                self.show = True
                self.position, self.current_direction = self.end_point
                self.position = self.get_new_coord(self.current_direction, 1)
                new_i, new_j = self.position
                self.maze[new_i][new_j] = 0

        return self.maze

    def finished(self):
        return not len(self.break_up_points)

    def action(self, direction=None, step=2):
        if direction == None:
            new_direction = self.get_new_direction()
        else:
            new_direction = direction
        if new_direction == self.opposite_directions[self.current_direction]:
            pop_index = self.POP_INDEXES[self.difficulty_level](len(self.break_up_points))
            self.position = self.break_up_points.pop(pop_index)
            self.current_direction = None
            self.distance = self.distances[self.position]
        else:
            self.current_direction = new_direction
            self.move(step)
            self.distance += 2
            
    def move(self, n):
        for i in range(n):
            self.position = self.get_new_coord(self.current_direction, 1)
            new_i, new_j = self.position
            self.maze[new_i][new_j] = 0

    def get_new_direction(self):
        possible_directions = []
        for direction in self.directions:
            if direction != self.opposite_directions[self.current_direction]:
                side_check = self.side_check(direction)
                wall_check = False
                if side_check:
                    wall_check = self.wall_check(direction)
                if side_check and wall_check:
                    possible_directions.append(direction)

        if len(possible_directions) > 1:
            self.break_up_points.append(self.position)
            self.distances[self.position] = self.distance

        if len(possible_directions):
            if self.current_direction in possible_directions and random.random() > self.difficulty:
                return self.current_direction
            else:
                return random.choice(possible_directions)

        end_point_check = self.end_point_check()
        if end_point_check:
            for direction in self.directions:
                side_check = self.side_check(direction)
                if not side_check and end_point_check:
                    if self.end_point_distance < self.distance:
                        self.end_point = (self.position, direction)
                        self.end_point_distance = self.distance
                        break
        return self.opposite_directions[self.current_direction]

    def end_point_check(self):
        wall_count = 0
        for direction in self.directions:
            i, j = self.get_new_coord(direction, 1)
            wall_count += self.maze[i][j] == self.keys["wall"]

        return wall_count == 3

    def side_check(self, direction):
        i, j = self.get_new_coord(direction, 2)
        if 0 <= i < self.size[0] * 2 + 1 and 0 <= j < self.size[1] * 2 + 1:
            return True
        return False

    def wall_check(self, direction):
        i, j = self.get_new_coord(direction, 2)
        return self.maze[i][j] == self.keys["wall"]

    def get_new_coord(self, direction, n):
        if direction == "up":
            return self.up(self.position, n)
        if direction == "down":
            return self.down(self.position, n)
        if direction == "left":
            return self.left(self.position, n)
        if direction == "right":
            return self.right(self.position, n)



rows = int(input("\nNumber of Rows: "))
columns = int(input("\nNumber of Columns: "))
size=(rows, columns)
print("\n1- Show while creating (Much Slower)\n2- Don't show while creating")
show = int(input("Choice: ")) == 1
print("\n1- Easy\n2- Medium\n3- Hard")
dif = int(input("Choice: ")) - 1

print("\n\nCreating Maze!")
start_time = time.time()
mc = Maze(size=size, difficulty_level=dif, render_quality=8, show=show)

while True:
    try:
        maze = mc.create_maze()
        break
    except:
        pass

print("\nMaze Created!")
print(f"progress time: {time.time() - start_time}")

print(f"Image saved as {mc.file_name} in the images folder.")

mc.render()


