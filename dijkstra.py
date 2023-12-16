import heapq

def compute_directions(map_data, target_pos):
    rows = len(map_data)
    cols = len(map_data[0])

    # Initialize a 2D directions list with None values
    dir = [[None] * cols for _ in range(rows)]

    # Initialize a 2D distances list with infinity values
    distances = [[float('inf')] * cols for _ in range(rows)]
    distances[target_pos[0]][target_pos[1]] = 0

    # Initialize a priority queue for Dijkstra's algorithm
    priority_queue = [(0, target_pos)]

    while priority_queue:
        current_distance, current_pos = heapq.heappop(priority_queue)

        x, y = current_pos

        # Define the possible neighbor positions
        neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]

        for neighbor_pos in neighbors:
            nx, ny = neighbor_pos

            # Check if the neighbor position is within the map boundaries
            if 0 <= nx < rows and 0 <= ny < cols:
                # Calculate the tentative distance to the neighbor
                neighbor_distance = distances[x][y] + get_weight(map_data, neighbor_pos)

                # Update the distance and direction if the tentative distance is lower
                if neighbor_distance < distances[nx][ny]:
                    distances[nx][ny] = neighbor_distance
                    dir[nx][ny] = compute_direction(current_pos, neighbor_pos)

                    # Add the neighbor position to the priority queue for further traversal
                    heapq.heappush(priority_queue, (neighbor_distance, neighbor_pos))

    for row in range(len(dir)):
        for col in range(len(dir[row])):
            if dir[row][col] is None:
                dir[row][col] = "5"
    return dir


def get_weight(map_data, position):
    x, y = position
    return int(map_data[x][y]) if int(map_data[x][y]) < 10 else float(
        'inf')  # Return the weight unless it's an obstacle


def compute_direction(current_pos, neighbor_pos):
    # Compute the direction based on the difference in coordinates
    dx = neighbor_pos[0] - current_pos[0]
    dy = neighbor_pos[1] - current_pos[1]

    # Return the direction based on the sign of the differences
    if dx < 0:
        return "1"
    elif dx > 0:
        return "0"
    elif dy < 0:
        return "3"
    elif dy > 0:
        return "2"
    else:
        return "5"  # No direction if the coordinates are the same

