import time
import alpha  # Importing Alpha bot
import beta   # Importing Beta bot

def print_board(board):
    """Utility to print the board in a readable format."""
    symbols = {1: 'W', -1: 'B', 0: '.'}  # Swap Beta (Black) and Alpha (White)
    for row in board:
        print(' '.join(symbols[cell] for cell in row))
    print()

def initialize_board():
    """Initialize the standard Othello board with swapped colors."""
    board = [[0 for _ in range(8)] for _ in range(8)]
    board[3][3], board[4][4] = 1, 1  # Beta (Black) starts in (3,3), (4,4) - swapped
    board[3][4], board[4][3] = -1, -1  # Alpha (White) starts in (3,4), (4,3) - swapped
    return board

def is_game_over(board):
    """Check if the game is over."""
    for row in board:
        if 0 in row:
            return False
    return True

def get_winner(board):
    """Determine the winner of the game with swapped colors."""
    beta_score = sum(row.count(1) for row in board)  # Beta is now White (1)
    alpha_score = sum(row.count(-1) for row in board)  # Alpha is now Black (-1)
    if beta_score > alpha_score:
        return f"Beta (White) wins with score {beta_score}!"  # Beta is now White
    elif alpha_score > beta_score:
        return f"Alpha (Black) wins with score {alpha_score}!"  # Alpha is now Black
    else:
        return f"It's a tie! Both players scored {beta_score}."

def simulate_game():
    """Simulate the game between Alpha and Beta bots."""
    board = initialize_board()
    player_turn = 1  # Beta starts the game (Black), but now it's Beta (White) due to swap

    print("Initial Board:")
    print_board(board)

    no_valid_move_count = 0  # Counter to check if both players have no valid moves consecutively

    while not is_game_over(board):
        start_time = time.time()  # Start time for the current move

        if player_turn == 1:  # Beta's turn (White, after the swap)
            move = beta.move(board, player_turn)
        else:  # Alpha's turn (Black, after the swap)
            move = alpha.move(board, player_turn)

        move_time = time.time() - start_time  # Calculate time for the move

        if move is None:
            # If the player has no valid moves, skip their turn
            print(f"{'Beta (White)' if player_turn == 1 else 'Alpha (Black)'} has no valid moves, skipping turn.")
            no_valid_move_count += 1  # Increment counter
            player_turn = -player_turn  # Switch turn
            if no_valid_move_count == 2:  # If both players have no valid moves, the game ends
                print("Both players have no valid moves. Game Over.")
                break
            continue
        else:
            no_valid_move_count = 0  # Reset counter if a valid move is found

        row, col = move
        board = make_move(board, row, col, player_turn)
        print(f"{'Beta (White)' if player_turn == 1 else 'Alpha (Black)'} played: {move}")
        print(f"Move took {move_time:.4f} seconds")
        print_board(board)

        # Switch turns
        player_turn = -player_turn

    print("Final Board:")
    print_board(board)
    print(get_winner(board))

def make_move(board, row, col, player_color):
    """Execute a move and flip the discs accordingly."""
    new_board = [r[:] for r in board]
    new_board[row][col] = player_color
    opponent = -player_color

    for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
        to_flip = []
        x, y = row + dx, col + dy
        while 0 <= x < 8 and 0 <= y < 8 and board[x][y] == opponent:
            to_flip.append((x, y))
            x += dx
            y += dy

        if to_flip and 0 <= x < 8 and 0 <= y < 8 and board[x][y] == player_color:
            for flip_x, flip_y in to_flip:
                new_board[flip_x][flip_y] = player_color

    return new_board

# Run the simulation
if __name__ == "__main__":
    simulate_game()
