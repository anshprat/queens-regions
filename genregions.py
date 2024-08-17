import numpy as np
from collections import deque
import random

# In-memory cache for checksums
checksum_cache = set()

def generate_random_queens_positions(size):
    """Generate a random valid solution for the 8-queens problem."""
    def is_valid(queens, row, col):
        for r, c in queens:
            if c == col or abs(r - row) == abs(c - col):
                return False
        return True

    def place_queens(row):
        if row == size:
            return True
        cols = list(range(size))
        random.shuffle(cols)  # Randomize the order of columns
        for col in cols:
            if is_valid(queens, row, col):
                queens.append((row, col))
                board[row][col] = 1
                if place_queens(row + 1):
                    return True
                queens.pop()
                board[row][col] = 0
        return False

    board = np.zeros((size, size), dtype=int)
    queens = []
    place_queens(0)
    return board

def generate_regions(board):
    size = len(board)
    region_id = 1
    regions = np.zeros((size, size), dtype=int)
    visited = np.zeros((size, size), dtype=bool)

    def bfs(start_row, start_col):
        nonlocal region_id
        queue = deque([(start_row, start_col)])
        regions[start_row][start_col] = region_id
        cells = [(start_row, start_col)]
        visited[start_row][start_col] = True
        while queue:
            r, c = queue.popleft()
            for nr, nc in [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]:
                if 0 <= nr < size and 0 <= nc < size and board[nr][nc] == 1 and not visited[nr][nc]:
                    regions[nr][nc] = region_id
                    visited[nr][nc] = True
                    queue.append((nr, nc))
                    cells.append((nr, nc))
        return cells

    # First pass to assign regions
    for row in range(size):
        for col in range(size):
            if board[row][col] == 1 and regions[row][col] == 0:
                cells_in_region = bfs(row, col)
                if len(cells_in_region) == 1:
                    # Reassign to a new region ID if necessary
                    region_id += 1
                    regions[cells_in_region[0][0]][cells_in_region[0][1]] = region_id
                region_id += 1

    # Ensure no zero regions and most regions have more than one cell
    new_region_id = region_id + 1

    for row in range(size):
        for col in range(size):
            if regions[row][col] == 0:
                # Assign a region number based on neighboring cells
                neighboring_ids = set()
                for nr, nc in [(row-1, col), (row+1, col), (row, col-1), (row, col+1)]:
                    if 0 <= nr < size and 0 <= nc < size and regions[nr][nc] != 0:
                        neighboring_ids.add(regions[nr][nc])

                if neighboring_ids:
                    regions[row][col] = random.choice(list(neighboring_ids))
                else:
                    regions[row][col] = new_region_id
                    new_region_id += 1

    return regions

def calculate_checksum(array):
    """Calculate a checksum for a 2D numpy array."""
    flat_array = array.flatten()
    return hash(tuple(flat_array))

def format_array(array):
    """Format the 2D numpy array for consistent printing and saving."""
    return "[\n" + "\n".join(f"    {list(row)}," for row in array.tolist()) + "\n]"

def save_to_file(filename, board, checksum, regions_formatted):
    """Save the board and its checksum to a file."""
    with open(filename, 'a') as file:
        if len(board)>0:
            file.write("Board:\n")
            for row in board:
                file.write(' '.join(map(str, row)) + '\n')
        if len(regions_formatted)>1:
            file.write("\nFormatted Regions:\n")
            file.write(regions_formatted)
        file.write(f"\nChecksum: {checksum}\n")


def main():
    size = 8
    board = generate_random_queens_positions(size)
    region_colors = generate_regions(board)

    # Calculate checksums
    board_checksum = calculate_checksum(board)
    regions_checksum = calculate_checksum(region_colors)

    # Check if the checksums are already in the cache
    if regions_checksum in checksum_cache:
        print("Duplicate checksum detected. Skipping save.")
        return

    # Add new checksums to the cache
    checksum_cache.add(board_checksum)
    checksum_cache.add(regions_checksum)

    # Format the regions output
    regions_formatted = format_array(region_colors)

    # Save to files
    save_to_file('queens.txt', board, board_checksum, '')
    save_to_file('regions.txt', np.zeros_like(region_colors), regions_checksum, regions_formatted)

    # Print to console as well
    print("Queens Board:")
    for row in board:
        print(' '.join(map(str, row)))
    
    print("\nRegion Colors:")
    print(regions_formatted)

    print(f"\nChecksum of Queens Board: {board_checksum}")
    print(f"Checksum of Region Colors: {regions_checksum}")

# Generate, print, and save the board with regions and checksums

c=0
while(c<10000):
    c=c+1
    main()
