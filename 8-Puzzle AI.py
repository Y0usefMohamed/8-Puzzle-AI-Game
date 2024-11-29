import random
import copy
import tkinter as tk
from tkinter import messagebox
from queue import Queue
import time

# Define the size of the puzzle (3x3 for 8-puzzle)
n = 3
goal_state = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]  # Goal state of the puzzle (ascending order)

# Directions for moving the empty space
row = [1, 0, -1, 0]
col = [0, -1, 0, 1]

# Function to generate a new node by swapping the empty space
def new_node(mat, empty_tile_pos, new_empty_tile_pos):
    new_mat = copy.deepcopy(mat)
    x1, y1 = empty_tile_pos
    x2, y2 = new_empty_tile_pos
    new_mat[x1][y1], new_mat[x2][y2] = new_mat[x2][y2], new_mat[x1][y1]
    return new_mat

# Function to check if the puzzle is solved (matches goal state)
def is_solved(puzzle):
    return puzzle == goal_state

# Function to get possible moves for the empty space
def get_possible_moves(puzzle):
    empty_tile_pos = [(i, row.index(0)) for i, row in enumerate(puzzle) if 0 in row][0]
    x, y = empty_tile_pos
    moves = []
    
    for dx, dy in zip(row, col):
        new_x, new_y = x + dx, y + dy
        if 0 <= new_x < n and 0 <= new_y < n:
            moves.append((new_x, new_y))
    return moves

# Function to calculate inversions in a puzzle (for solvability check)
def count_inversions(puzzle):
    one_d_puzzle = [tile for row in puzzle for tile in row if tile != 0]
    inversions = 0
    for i in range(len(one_d_puzzle)):
        for j in range(i + 1, len(one_d_puzzle)):
            if one_d_puzzle[i] > one_d_puzzle[j]:
                inversions += 1
    return inversions

# Function to check if a puzzle is solvable (number of inversions must be even)
def is_solvable(puzzle):
    return count_inversions(puzzle) % 2 == 0

# BFS algorithm with complexity tracking
def bfs_with_complexity(start_puzzle):
    queue = Queue()
    queue.put((start_puzzle, []))  # Store puzzle and the path of moves
    visited = set()
    visited.add(tuple(map(tuple, start_puzzle)))  # Add the puzzle state as a tuple for easy comparison
    
    # Complexity tracking
    nodes_generated = 0
    max_queue_size = 0
    
    while not queue.empty():
        max_queue_size = max(max_queue_size, queue.qsize())
        puzzle, path = queue.get()
        
        # Check if the puzzle is solved
        if is_solved(puzzle):
            return path, nodes_generated, max_queue_size
        
        empty_tile_pos = [(i, row.index(0)) for i, row in enumerate(puzzle) if 0 in row][0]
        
        for move in get_possible_moves(puzzle):
            nodes_generated += 1
            new_puzzle = new_node(puzzle, empty_tile_pos, move)
            new_puzzle_tuple = tuple(map(tuple, new_puzzle))
            if new_puzzle_tuple not in visited:
                visited.add(new_puzzle_tuple)
                queue.put((new_puzzle, path + [new_puzzle]))
    
    return [], nodes_generated, max_queue_size  # Return empty path if no solution found


# DFS algorithm (infinite)
def dfs_infinite(start_puzzle):
    stack = [(start_puzzle, [], set())]  # Include visited states set in the stack
    visited_states = set()  # Keep track of visited states to prevent revisiting
    
    while stack:
        puzzle, path, visited = stack.pop()
        
        # Check if the puzzle is solved
        if is_solved(puzzle):
            return path
        
        empty_tile_pos = [(i, row.index(0)) for i, row in enumerate(puzzle) if 0 in row][0]
        
        for move in get_possible_moves(puzzle):
            new_puzzle = new_node(puzzle, empty_tile_pos, move)
            new_puzzle_tuple = tuple(map(tuple, new_puzzle))
            
            # If we detect a loop (visited state), terminate the program and display a message
            if new_puzzle_tuple in visited_states:
                messagebox.showinfo("No Solution", "No solution: There is a loop!")
                return []
            
            visited_states.add(new_puzzle_tuple)
            stack.append((new_puzzle, path + [new_puzzle], visited_states))
    
    messagebox.showinfo("No Solution", "No solution found!")
    
    return []  # Return empty path if no solution is found


# DFS algorithm with limited depth
def dfs_limited(start_puzzle, max_depth=150):
    stack = [(start_puzzle, [], 0)]  # Include depth in the stack
    visited = set()
    visited.add(tuple(map(tuple, start_puzzle)))  # Mark initial state as visited

    nodes_generated = 0
    max_memory_used = 0

    while stack:
        max_memory_used = max(max_memory_used, len(stack))
        puzzle, path, depth = stack.pop()

        if is_solved(puzzle):
            return path, nodes_generated, max_memory_used

        if depth >= max_depth:
            continue

        empty_tile_pos = [(i, row.index(0)) for i, row in enumerate(puzzle) if 0 in row][0]

        for move in get_possible_moves(puzzle):
            new_puzzle = new_node(puzzle, empty_tile_pos, move)
            new_puzzle_tuple = tuple(map(tuple, new_puzzle))

            if new_puzzle_tuple not in visited:
                visited.add(new_puzzle_tuple)
                stack.append((new_puzzle, path + [new_puzzle], depth + 1))
                nodes_generated += 1

    return [], nodes_generated, max_memory_used  # Return empty path if no solution found



# UCS algorithm with complexity tracking
def ucs_with_complexity(start_puzzle):
    from queue import PriorityQueue
    
    pq = PriorityQueue()
    pq.put((0, start_puzzle, []))  # Store the cost, puzzle, and path of moves
    visited = set()
    visited.add(tuple(map(tuple, start_puzzle)))
    
    # Complexity tracking
    nodes_generated = 0
    max_memory_used = 0
    
    while not pq.empty():
        max_memory_used = max(max_memory_used, pq.qsize())
        cost, puzzle, path = pq.get()
        
        # Check if the puzzle is solved
        if is_solved(puzzle):
            return path, nodes_generated, max_memory_used
        
        empty_tile_pos = [(i, row.index(0)) for i, row in enumerate(puzzle) if 0 in row][0]
        
        for move in get_possible_moves(puzzle):
            nodes_generated += 1
            new_puzzle = new_node(puzzle, empty_tile_pos, move)
            new_puzzle_tuple = tuple(map(tuple, new_puzzle))
            
            if new_puzzle_tuple not in visited:
                visited.add(new_puzzle_tuple)
                pq.put((cost + 1, new_puzzle, path + [new_puzzle]))
    
    return [], nodes_generated, max_memory_used  # Return empty path if no solution found

# Function to generate a random initial puzzle state
def generate_initial_state():
    puzzle = list(range(n * n))
    random.shuffle(puzzle)
    puzzle = [puzzle[i * n:(i + 1) * n] for i in range(n)]
    return puzzle if is_solvable(puzzle) else generate_initial_state()  # Regenerate if unsolvable

# Function to update the puzzle grid in the GUI
def update_puzzle_gui(puzzle, label_frame):
    for widget in label_frame.winfo_children():
        widget.destroy()  # Clear previous widgets

    for i in range(n):
        for j in range(n):
            tile_value = puzzle[i][j]
            color = "lightblue" if tile_value != 0 else "white"  # Make 0 (empty space) white
            label = tk.Label(label_frame, text=str(tile_value), width=5, height=2, 
                             bg=color, relief="solid", font=("Arial", 18))
            label.grid(row=i, column=j, padx=2, pady=2)

# Function to solve the puzzle and visualize the solution step by step
def solve_puzzle(algorithm):
    global shuffled_puzzle
    steps = []
    nodes_generated = 0
    max_memory_used = 0
    num_moves = 0  # Initialize number of moves

    start_time = time.time()

    if algorithm == "BFS":
        steps, nodes_generated, max_memory_used = bfs_with_complexity(shuffled_puzzle)
    elif algorithm == "DFS":
        steps = dfs_infinite(shuffled_puzzle)
    elif algorithm == "DFS_Limited":
        steps, nodes_generated, max_memory_used = dfs_limited(shuffled_puzzle)
    elif algorithm == "UCS":
        steps, nodes_generated, max_memory_used = ucs_with_complexity(shuffled_puzzle)

    end_time = time.time()
    elapsed_time = end_time - start_time

    if steps:
        num_moves = len(steps) - 1  # Exclude the initial state from the count of moves

    complexity_label.config(
        text=f"Nodes Generated: {nodes_generated}\n"
             f"Max Memory Used: {max_memory_used}\n"
             f"Elapsed Time: {elapsed_time:.2f} seconds\n"
             f"Number of Moves: {num_moves}"  # Display the number of moves
    )

    if steps:
        def show_next_step(step_index):
            if step_index < len(steps):
                update_puzzle_gui(steps[step_index], label_frame)
                root.after(1000, show_next_step, step_index + 1)

        show_next_step(0)
    else:
        messagebox.showinfo("No Solution", "No solution found!")

# GUI setup
root = tk.Tk()
root.title("8-Puzzle Solver")

# Complexity Metrics Frame
complexity_frame = tk.Frame(root)
complexity_frame.pack(pady=20)

complexity_label = tk.Label(complexity_frame, text="Nodes Generated: 0\nMax Memory Used: 0\nElapsed Time: 0.00 seconds", 
                            font=("Arial", 14))
complexity_label.pack()


# Title Frame
title_frame = tk.Frame(root)
title_frame.pack(pady=20)

title_label = tk.Label(title_frame, text="Welcome to the 8-Puzzle Solver", font=("Arial", 20, "bold"))
title_label.pack()

# Choose Algorithm Frame
choose_algo_frame = tk.Frame(root)
choose_algo_frame.pack(pady=20)

choose_algo_label = tk.Label(choose_algo_frame, text="Choose an Algorithm:", font=("Arial", 16))
choose_algo_label.pack()

# Buttons to select algorithm
solve_button_bfs = tk.Button(choose_algo_frame, text="Solve with BFS", command=lambda: solve_puzzle("BFS"), width=35)
solve_button_bfs.pack(pady=5)

solve_button_dfs = tk.Button(choose_algo_frame, text="Solve with DFS", command=lambda: solve_puzzle("DFS"), width=35)
solve_button_dfs.pack(pady=5)

solve_button_dfs_limited = tk.Button(choose_algo_frame, text="Solve with DFS Using Limited Depth", command=lambda: solve_puzzle("DFS_Limited"), width=35)
solve_button_dfs_limited.pack(pady=5)

solve_button_ucs = tk.Button(choose_algo_frame, text="Solve with UCS", command=lambda: solve_puzzle("UCS"), width=35)
solve_button_ucs.pack(pady=5)

# Puzzle grid display
label_frame = tk.Frame(root)
label_frame.pack()

# Generate a solvable shuffled puzzle
shuffled_puzzle = generate_initial_state()

# Update the puzzle GUI initially
update_puzzle_gui(shuffled_puzzle, label_frame)

# Start the GUI
root.mainloop()
