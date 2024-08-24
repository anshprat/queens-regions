import random
import hashlib
from collections import deque

checksum_cache = set()
DEBUG = bool(False)
max_region_size = 10

def debug_print(*args):
    if DEBUG:
        print(args)

def is_safe(board, row, col):
    for i in range(8):
        if board[row][i] == 1 or board[i][col] == 1:
            return False
    for i, j in zip(range(row, -1, -1), range(col, -1, -1)):
        if board[i][j] == 1:
            return False
    for i, j in zip(range(row, -1, -1), range(col, 8)):
        if board[i][j] == 1:
            return False
    return True

def solve_queens():
    board = [[0 for _ in range(8)] for _ in range(8)]
    queens = []
    
    def backtrack(row):
        if row == 8:
            return True
        cols = list(range(8))
        random.shuffle(cols)
        for col in cols:
            if is_safe(board, row, col):
                board[row][col] = 1
                queens.append((row, col))
                if backtrack(row + 1):
                    return True
                board[row][col] = 0
                queens.pop()
        return False
    
    backtrack(0)
    return queens, board

def get_neighbors(r, c):
    return [(r+1, c), (r-1, c), (r, c+1), (r, c-1)]

def create_region_map(queens):
    def get_neighbors(r, c):
        return [(r+1, c), (r-1, c), (r, c+1), (r, c-1)]

    def is_valid_and_empty(r, c):
        return 0 <= r < 8 and 0 <= c < 8 and region_map[r][c] == 0

    def bfs_fill(start_r, start_c, color):
        queue = deque([(start_r, start_c)])
        region_map[start_r][start_c] = color
        cells_filled = 1

        while queue and cells_filled < max_region_size:
            r, c = queue.popleft()
            for nr, nc in get_neighbors(r, c):
                if is_valid_and_empty(nr, nc):
                    region_map[nr][nc] = color
                    queue.append((nr, nc))
                    cells_filled += 1
                    if cells_filled == max_region_size:
                        break

    region_map = [[0 for _ in range(8)] for _ in range(8)]
    colors = list(range(1, 9))
    random.shuffle(colors)

    # Place queens and start regions
    for (r, c), color in zip(queens, colors):
        bfs_fill(r, c, color)

    # Fill remaining cells
    for color in colors:
        while True:
            empty_cells = [(r, c) for r in range(8) for c in range(8) if region_map[r][c] == 0]
            if not empty_cells:
                break
            start_r, start_c = random.choice(empty_cells)
            bfs_fill(start_r, start_c, color)

        return region_map

def calculate_checksum(queens, region_map):
    board_str = ''.join([''.join(map(str, row)) for row in region_map])
    queens_str = ''.join([f"{r}{c}" for r, c in queens])
    combined_str = board_str + queens_str
    return hashlib.md5(combined_str.encode()).hexdigest()

def generate_solution():
    queens, queens_board = solve_queens()
    region_map = create_region_map(queens)
    checksum = calculate_checksum(queens, region_map)
    return queens, queens_board, region_map, checksum

def print_board(board):
    for row in board:
        print(row, ",")
    print()
    

def count_regions(region_map):
    regions = set()
    for row in region_map:
        regions.update(row)
    return len(regions)

def color_distribution(region_map):
    color_counts = {}
    for row in region_map:
        for color in row:
            color_counts[color] = color_counts.get(color, 0) + 1
    return color_counts

def check_contiguous_regions(region_map):
    def get_neighbors(r, c):
        return [(r+1, c), (r-1, c), (r, c+1), (r, c-1)]

    def bfs(start_r, start_c, color, visited):
        queue = deque([(start_r, start_c)])
        visited.add((start_r, start_c))
        region_size = 1

        while queue:
            r, c = queue.popleft()
            for nr, nc in get_neighbors(r, c):
                if 0 <= nr < 8 and 0 <= nc < 8 and region_map[nr][nc] == color and (nr, nc) not in visited:
                    queue.append((nr, nc))
                    visited.add((nr, nc))
                    region_size += 1

        return region_size

    visited = set()
    color_regions = {}

    for r in range(8):
        for c in range(8):
            if (r, c) not in visited:
                color = region_map[r][c]
                region_size = bfs(r, c, color, visited)
                
                if color not in color_regions:
                    color_regions[color] = [region_size]
                else:
                    color_regions[color].append(region_size)

    non_contiguous = {color: sizes for color, sizes in color_regions.items() if len(sizes) > 1}

    if non_contiguous:
        debug_print("Non-contiguous regions found:")
        for color, sizes in non_contiguous.items():
            debug_print(f"Color {color}: {len(sizes)} disconnected regions of sizes {sizes}")
        return False
    else:
        debug_print("All regions are contiguous.")
        return True


def save_to_file(filename, board, checksum, regions_formatted):
    """Save the board and its checksum to a file."""
    with open(filename, 'a') as file:
        if len(board)>0:
            file.write("Board:"+checksum+"\n")
            for row in board:
                file.write(' '.join(map(str, row)) + '\n')
                
        if len(regions_formatted)>1:
            # file.write("\nFormatted Regions:\n")
            # regions_formatted=regions_formatted+","
            region = "\""+str(checksum) +"\":"+str(regions_formatted)+","
            file.write(region)
        # file.write(f"\nChecksum: {checksum}\n")

# Generate and debug_print the solution
# queens, queens_board, region_map, checksum = generate_solution()
# is_region_contiguous = check_contiguous_regions(region_map)
# debug_print(check_contiguous_regions(region_map))
is_region_contiguous = False
c=0
num_boards=100
while not is_region_contiguous or c < num_boards:
    debug_print(c)
    queens, queens_board, region_map, checksum = generate_solution()
    if checksum in checksum_cache:
        debug_print("Duplicate checksum detected. Skipping checks.")
        continue
    checksum_cache.add(checksum)
    is_region_contiguous = check_contiguous_regions(region_map)
    if is_region_contiguous:
        c=c+1
        print_board(region_map)
        save_to_file('queens.txt', queens_board, checksum, '')
        save_to_file('regions.txt', '', checksum, region_map)

        
        # print(c)
        




# debug_print("Queens positions (list):")
# debug_print(queens)
# debug_print("\nQueens positions (8x8 matrix):")
# debug_print_board(queens_board)
# debug_print("Region map:")
# debug_print_board(region_map)

# if not is_region_contiguous:
#     debug_print("The region map contains non-contiguous regions and needs to be regenerated.")
# else:
#     debug_print("The region map is valid with all contiguous regions.")

# debug_print(f"Number of regions: {count_regions(region_map)}")
# debug_print("Color distribution:")
# for color, count in color_distribution(region_map).items():
#     debug_print(f"Color {color}: {count} cells")
# debug_print(f"Checksum: {checksum}")