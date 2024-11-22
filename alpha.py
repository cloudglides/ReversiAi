import math
import random
import concurrent.futures
import multiprocessing
from functools import partial

BOARD_SIZE = 8
EMPTY = 0
WHITE = -1
BLACK = 1

DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

EARLY_GAME_WEIGHTS = [
    [120, -20, 20, 10, 10, 20, -20, 120],
    [-20, -40, -5, -5, -5, -5, -40, -20],
    [20, -5, 10, 3, 3, 10, -5, 20],
    [10, -5, 3, 3, 3, 3, -5, 10],
    [10, -5, 3, 3, 3, 3, -5, 10],
    [20, -5, 10, 3, 3, 10, -5, 20],
    [-20, -40, -5, -5, -5, -5, -40, -20],
    [120, -20, 20, 10, 10, 20, -20, 120]
]

MID_GAME_WEIGHTS = [
    [120, -20, 20, 10, 10, 20, -20, 120],
    [-20, -30, -5, -5, -5, -5, -30, -20],
    [20, -5, 10, 3, 3, 10, -5, 20],
    [10, -5, 3, 5, 5, 3, -5, 10],
    [10, -5, 3, 5, 5, 3, -5, 10],
    [20, -5, 10, 3, 3, 10, -5, 20],
    [-20, -30, -5, -5, -5, -5, -30, -20],
    [120, -20, 20, 10, 10, 20, -20, 120]
]

LATE_GAME_WEIGHTS = [
    [120, -20, 20, 10, 10, 20, -20, 120],
    [-20, -20, -5, -5, -5, -5, -20, -20],
    [20, -5, 10, 5, 5, 10, -5, 20],
    [10, -5, 5, 5, 5, 5, -5, 10],
    [10, -5, 5, 5, 5, 5, -5, 10],
    [20, -5, 10, 5, 5, 10, -5, 20],
    [-20, -20, -5, -5, -5, -5, -20, -20],
    [120, -20, 20, 10, 10, 20, -20, 120]
]

class ParallelOthelloAI:
    def __init__(self, num_threads=None):
        self.num_threads = num_threads or (multiprocessing.cpu_count() * 2)

    def get_dynamic_weights(self, game_stage):
        if game_stage == "early":
            return EARLY_GAME_WEIGHTS
        elif game_stage == "mid":
            return MID_GAME_WEIGHTS
        else:
            return LATE_GAME_WEIGHTS

    def parallel_move_evaluation(self, board_state, player_color, moves, game_stage):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            eval_func = partial(self.evaluate_move, board_state, player_color, game_stage)
            move_scores = list(executor.map(eval_func, moves))
        return moves, move_scores

    def evaluate_move(self, board_state, player_color, game_stage, move):
        x, y = move
        new_board = self.apply_move(board_state, x, y, player_color)
        return (
            self.positional_evaluation(new_board, player_color, game_stage) +
            self.mobility_evaluation(new_board, player_color) +
            self.stability_evaluation(new_board, player_color)
        )

    def positional_evaluation(self, board, player_color, game_stage):
        weights = self.get_dynamic_weights(game_stage)
        return sum(
            weights[r][c] if board[r][c] == player_color
            else -weights[r][c] if board[r][c] == -player_color
            else 0
            for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)
        )

    def mobility_evaluation(self, board, player_color):
        player_moves = len(self.get_valid_moves(board, player_color))
        opponent_moves = len(self.get_valid_moves(board, -player_color))
        return 30 * (player_moves - opponent_moves)

    def stability_evaluation(self, board, player_color):
        corners = [(0, 0), (0, BOARD_SIZE-1), (BOARD_SIZE-1, 0), (BOARD_SIZE-1, BOARD_SIZE-1)]
        return sum(100 if board[x][y] == player_color else -100 if board[x][y] == -player_color else 0 for (x, y) in corners)

    def apply_move(self, board, x, y, player_color):
        new_board = [row[:] for row in board]
        new_board[x][y] = player_color
        opponent_color = -player_color

        for dx, dy in DIRECTIONS:
            to_flip = []
            nx, ny = x + dx, y + dy
            while 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
                if new_board[nx][ny] == opponent_color:
                    to_flip.append((nx, ny))
                elif new_board[nx][ny] == player_color:
                    for flip_x, flip_y in to_flip:
                        new_board[flip_x][flip_y] = player_color
                    break
                else:
                    break
                nx, ny = nx + dx, ny + dy

        return new_board

    def get_valid_moves(self, board, player_color):
        return [(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)
                if self.is_valid_move(board, r, c, player_color)]

    def is_valid_move(self, board, x, y, player_color):
        if board[x][y] != EMPTY:
            return False

        opponent_color = -player_color
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and board[nx][ny] == opponent_color:
                temp_x, temp_y = nx, ny
                while 0 <= temp_x < BOARD_SIZE and 0 <= temp_y < BOARD_SIZE:
                    temp_x, temp_y = temp_x + dx, temp_y + dy
                    if 0 <= temp_x < BOARD_SIZE and 0 <= temp_y < BOARD_SIZE:
                        if board[temp_x][temp_y] == player_color:
                            return True
                        elif board[temp_x][temp_y] == EMPTY:
                            break
        return False

    def evaluate_board(self, board, player_color):
        return sum(
            1 if cell == player_color else -1 if cell == -player_color else 0
            for row in board for cell in row
        )

    def minimax(self, board, depth, player_color, maximizing_player, alpha, beta, game_stage):
        valid_moves = self.get_valid_moves(board, player_color if maximizing_player else -player_color)
        if depth == 0 or not valid_moves:
            return self.evaluate_board(board, player_color)

        if maximizing_player:
            max_eval = -float("inf")
            for move in valid_moves:
                new_board = self.apply_move(board, move[0], move[1], player_color)
                eval = self.minimax(new_board, depth -1, player_color, False, alpha, beta, game_stage)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float("inf")
            for move in valid_moves:
                new_board = self.apply_move(board, move[0], move[1], -player_color)
                eval = self.minimax(new_board, depth - 1, player_color, True, alpha, beta, game_stage)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

def move(board_state, player_color):
    ai = ParallelOthelloAI()
    valid_moves = ai.get_valid_moves(board_state, player_color)

    if not valid_moves:
        return None

    game_stage = "early" if sum(cell != EMPTY for row in board_state for cell in row) < 20 else \
                 "mid" if sum(cell != EMPTY for row in board_state for cell in row) < 50 else \
                 "late"

    moves, move_scores = ai.parallel_move_evaluation(board_state, player_color, valid_moves, game_stage)
    best_move = max(zip(moves, move_scores), key=lambda x: x[1])[0]
    return best_move
