## Othello (Reversi) AI with Alpha & Beta Bots

This project implements an Othello (Reversi) AI with two bots, Alpha and Beta, that strategically play the game.

### AI Decision Making

Both Alpha and Beta bots analyze the board using various techniques:

* **Corner Control:** Prioritize placing pieces in corner squares.
* **Edge Prevention:** Discourage placing pieces near the edge.
* **Monte Carlo Simulations:** Simulate random game continuations to estimate outcomes.

### Core Function: move

The `move` function in `alpha.py & beta.py` takes:
* **board_state:** 8x8 array representing the board
* **player_color:** 1 for black, -1 for white

It:
1. Analyzes the board state using the techniques above.
2. Simulates potential game outcomes through Monte Carlo simulations.
3. Calculates scores based on factors like corner control and board dominance.
4. Returns the move that maximizes the bot's score.

### Running the Simulation

1. Clone the repository.
2. Run: `python3 simulation.py`

This simulates a game between Alpha and Beta.

### Dependencies

This project is written in pure Python and doesn't rely on external libraries.
