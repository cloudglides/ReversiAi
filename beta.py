
import time
import random
import multiprocessing
from functools import lru_cache

# Directions for checking and flipping discs
DIRECTIONS = [
    (-1, 0), (1, 0), (0, -1), (0, 1),
    (-1, -1), (-1, 1), (1, -1), (1, 1)
]

# Corner and edge positions
CORNERS = [(0, 0), (0, 7), (7, 0), (7, 7)]
ADJACENT_CORNERS = [
    (0, 1), (1, 0), (1, 1),
    (0, 6), (1, 6), (1, 7),
    (6, 0), (6, 1), (7, 1),
    (6, 6), (6, 7), (7, 6)
]

# Opening book (example)
OPENING_BOOK = {
    # Example for first few moves (just as placeholders)
    (3, 3): [(3, 4), (4, 3)],
    (4, 4): [(3, 3), (4, 5)]
}

# Check if a move is valid
def is_valid_move(board, player, row, col):
    if board[row][col] != 0:
        return False

    for dr, dc in DIRECTIONS:
        r, c = row + dr, col + dc
        found_opponent = False
        while 0 <= r < 8 and 0 <= c < 8:
            if board[r][c] == -player:
                found_opponent = True
            elif board[r][c] == player and found_opponent:
                return True
            elif board[r][c] == 0:
                break
            r += dr
            c += dc
    return False

# Apply a move to the board
def apply_move(board, player, row, col):
    new_board = [row[:] for row in board]
    new_board[row][col] = player

    for dr, dc in DIRECTIONS:
        r, c = row + dr, col + dc
        discs_to_flip = []
        while 0 <= r < 8 and 0 <= c < 8:
            if new_board[r][c] == -player:
                discs_to_flip.append((r, c))
            elif new_board[r][c] == player:
                for rr, cc in discs_to_flip:
                    new_board[rr][cc] = player
                break
            else:
                break
            r += dr
            c += dc
    return new_board

# Get all valid moves
def get_valid_moves(board, player):
    return [
        (row, col)
        for row in range(8)
        for col in range(8)
        if is_valid_move(board, player, row, col)
    ]

# Heuristic evaluation function
def evaluate_board(board, player):
    score = 0
    for r in range(8):
        for c in range(8):
            if board[r][c] == player:
                if (r, c) in CORNERS:
                    score += 100
                elif (r, c) in ADJACENT_CORNERS:
                    score -= 50
                else:
                    score += 1
    return score

# Minimax with higher depth and parallelization
def minimax(board, player, depth, is_maximizing):
    if depth == 0 or not get_valid_moves(board, player):
        return evaluate_board(board, player)

    # Parallelize the search
    with multiprocessing.Pool() as pool:
        valid_moves = get_valid_moves(board, player)
        move_scores = pool.starmap(minimax_move, [(move, board, player, depth, is_maximizing) for move in valid_moves])

    return max(move_scores) if is_maximizing else min(move_scores)

# Helper function to evaluate a single move in parallel
def minimax_move(move, board, player, depth, is_maximizing):
    new_board = apply_move(board, player, *move)
    return minimax(new_board, -player, depth - 1, not is_maximizing)

# Monte Carlo simulation with increased simulations
def monte_carlo(board, player, simulations=50):
    scores = {}
    valid_moves = get_valid_moves(board, player)

    for move in valid_moves:
        scores[move] = 0
        for _ in range(simulations):
            sim_board = apply_move(board, player, *move)
            current_player = -player
            while get_valid_moves(sim_board, current_player):
                sim_move = random.choice(get_valid_moves(sim_board, current_player))
                sim_board = apply_move(sim_board, current_player, *sim_move)
                current_player = -current_player

            scores[move] += evaluate_board(sim_board, player)

    best_move = max(scores, key=lambda move: scores[move])
    return best_move

# Opening book-based move selection
def opening_move(board, player):
    first_move = tuple(board[row][col] for row in range(8) for col in range(8))
    if first_move in OPENING_BOOK:
        return OPENING_BOOK[first_move]
    return None

# Main function to decide the move
def move(board, player):
    start_time = time.time()

    # Check for opening move
    opening = opening_move(board, player)
    if opening:
        return opening

    # Get all valid moves
    valid_moves = get_valid_moves(board, player)
    if not valid_moves:
        return None

    # Priority 1: Capture corners
    for move in valid_moves:
        if move in CORNERS:
            return move

    # Priority 2: Prevent opponent corner capture
    for move in valid_moves:
        temp_board = apply_move(board, player, *move)
        opponent_moves = get_valid_moves(temp_board, -player)
        if not any(m in CORNERS for m in opponent_moves):
            return move

    # Priority 3: Use Minimax with higher depth
    best_move = minimax(board, player, depth=5, is_maximizing=True)

    # Priority 4: Monte Carlo fallback
    if not best_move:
        best_move = monte_carlo(board, player, simulations=10)

    end_time = time.time()
    print(f"Move decided: {best_move} in {end_time - start_time:.4f} seconds")
    return best_move
