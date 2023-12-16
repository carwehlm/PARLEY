import numpy as np
from collections import deque
import copy
import csv

size = 10
start = (size - 1, 0)
end = (0, size - 1)
csv_file_path = "maps/map_"


def generate_one_map():
    map_data = []
    for j in range(0, size):
        l = []
        for i in range(0, size):
            r = int(np.random.normal(0, 1))
            if r < 0:
                r *= -1
            r *= 10
            if j == 0 | j == 9:
                r = 0
            if i == 0 | j == 9:
                r = 0
            l.append(r)
        map_data.append(l)
    return map_data


def has_path(map_data, start_pos, target_pos):
    rows = len(map_data)
    cols = len(map_data[0])

    # Initialize a visited set to keep track of visited cells
    visited = set()

    # Initialize a queue for BFS traversal
    queue = deque()
    queue.append(start_pos)

    while queue:
        current_pos = queue.popleft()

        if current_pos == target_pos:
            # A path to the target has been found
            return True

        x, y = current_pos

        # Define the possible neighbor positions
        neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]

        for neighbor_pos in neighbors:
            nx, ny = neighbor_pos

            # Check if the neighbor position is within the map boundaries
            if 0 <= nx < rows and 0 <= ny < cols:
                # Check if the neighbor cell is not an obstacle and has not been visited
                if map_data[nx][ny] == 0 and neighbor_pos not in visited:
                    visited.add(neighbor_pos)
                    queue.append(neighbor_pos)

    # No path to the target was found
    return False


def add_penalties(old_map_data):
    map_data = copy.deepcopy(old_map_data)
    for x in range(0, size):
        for y in range(0, size):
            neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
            for neighbor_pos in neighbors:
                nx, ny = neighbor_pos
                # Check if the neighbor position is within the map boundaries
                if 0 <= nx < size and 0 <= ny < size:
                    if old_map_data[nx][ny] != 0:
                        map_data[x][y] += 3
    return map_data


def generate_map():
    while True:
        map_data = generate_one_map()
        if has_path(map_data, start, end):
            return map_data


# method to create 90 maps of size 10x10
def create_90_maps():
    print(size)
    for i in range(10, 100):
        map_data = generate_map()
        map_data = add_penalties(map_data)
        with open(csv_file_path + str(i) + '.csv', 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            for row in map_data:
                csv_writer.writerow(row)


# method to create additional maps to investigate scalability
# creates maps of size 5x5, 15x15, 20x20
def create_3_maps():
    sizes = [5, 15, 20]
    for i in range(len(sizes)):
        global size, start, end
        size = sizes[i]
        start = (size - 1, 0)
        end = (0, size - 1)
        map_data = generate_map()
        map_data = add_penalties(map_data)
        with open(csv_file_path + str(i) + '.csv', 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            for row in map_data:
                csv_writer.writerow(row)
