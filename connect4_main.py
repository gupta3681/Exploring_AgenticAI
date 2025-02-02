from typing import Dict, List,Union
import sys
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.utils.log import logger
from connect4_board import ConnectFourBoard
from agno.models.openai import OpenAIChat
import ast



class Connect4Game:
    def __init__(self):
        self.board = ConnectFourBoard()
        try:
            self.agents = self._initialize_agents()
        except Exception as e:
            logger.error(f"Failed to initialize agents: {str(e)}")
            raise
        
       


    def _initialize_agents(self) -> Dict[str, Agent]:
        """Initialize all required agents for Connect Four with specific roles"""
       
        try:
            # move_generator_agent = Agent(
            #     name="move_generator_agent",
            #     role="""You are a Connect Four rules expert. Given a board state which will be a 4x4 matrix, list ALL legal moves.
            #         Legal moves are the columns (0-3) where a piece can be dropped.
            #         Respond ONLY with the column numbers separated by commas, e.g., '0, 1, 2, 3'.""",
            #     model=Claude(id="claude-3-5-sonnet-20241022"),
            #     # debug_mode=True,
            # )

            player_red_agent = Agent(
                name="player_red_agent",
                role="""You are a Connect Four player playing as the RED player. Given the current board state
                    and a list of legal moves (columns where you can drop your piece), analyze them and choose
                    the move based on standard Connect Four strategies. You are an average player, you will not always choose the best move. Consider:
                    - Looking for a good move.
                    - Creating good paths
                    - Enusre you are only playing legal moves
                    Respond with the chosen column number (0-3) and why you chose it.""",
                model=OpenAIChat(id="gpt-4o"),
                # debug_mode=True,
            )

            player_yellow_agent = Agent(
                name="player_yellow_agent",
                role="""You are a Connect Four strategist playing as the YELLOW player. Given the current board state
                    and a list of legal moves (columns where you can drop your piece), analyze them and choose
                    the best move based on standard Connect Four strategies. Consider:
                    - Prioritising winning first rather than blocking the opponent always.
                    - Center control
                    - Blocking the opponent from winning
                    - Creating winning paths
                    - Try to trick the other player if you can but ensure to take the win if there is chance
                    - Enusre you are only playing legal moves
                    - Analyse the board carefully for best move but make sure it is legal.
                    Respond with the chosen column number (0-3) and why you chose it.""",
               model=OpenAIChat(id="gpt-4o"),
                # debug_mode=True,
            )
            
            board_state_manager = Agent(
                name="board_state_manager",
                role="""
                        You are a specialist in maintaining and modifying the board state for a Connect 4 game played between two players. Your primary responsibility is to ensure that every move is executed exactly as it would be in a real Connect 4 game. 
                        Key responsibilities include:
                        1. **Piece Insertion:** When a player makes a move, you will insert the player piece into the specified column. Pieces must always "fall" to the lowest available slot in that column. For example, if a column is empty, you cannot have a token in the middle, it will only get inserted to the bottom most space. 
                        2. **Board Representation:** The board is represented as a 2D list (a list of lists). Each cell in the board is either empty (denoted by '.') or contains a player's piece (for example, 'Y' for Yellow or 'R' for Red). The board dimensions are defined by a given number of rows and columns.
                        3. **Legal Moves Only:** Before inserting a piece, verify that the column is within range and has at least one empty slot. If the column is full or the column index is invalid, do not change the board state.
                        4. **State Persistence:** Ensure that the board state is correctly maintained and updated across moves.
                        5. **Feedback:** After processing a move, output the updated board state. If a move is illegal, indicate the error and leave the board state unchanged.
                        """,
               model=OpenAIChat(id="gpt-4o"),
                # debug_mode=True,
            )
            
            result_checker = Agent(
                name="result_checker",
                role="""
                    You are a specialist in analyzing the board state for a Connect 4 game played between two players. 
                    Your primary responsibility is to determine if there is a winner or if the game has resulted in a draw after each move.

                    **Key Responsibilities:**
                    1. **Winner Detection:** Analyze the current board state to identify if any player has won. A win is defined as four of the same player's pieces ('Y' for Yellow or 'R' for Red) consecutively aligned either horizontally, vertically, or diagonally (both left-to-right and right-to-left).

                    2. **Draw Detection:** Determine if the game has resulted in a draw. A draw occurs when all slots on the board are filled, and no player has achieved four consecutive pieces in any direction.

                    3. **Board Representation:** The board is represented as a 2D list (a list of lists). Each cell in the board is either empty (denoted by '.') or contains a player's piece ('Y' or 'R').

                    4. **Accurate Evaluation:** Ensure that your analysis is based solely on the provided board state without modifying it. You do not insert, remove, or alter any pieces on the board.

                    5. **Clear Feedback:** After analyzing the board:
                        - Indicate if there is a winner, specifying which player ('Y' or 'R') has won.
                        - If the game is a draw, clearly state that it is a draw.
                        - If the game is still ongoing with no winner or draw, indicate that the game should continue.
                """,
                model=OpenAIChat(id="gpt-4o"),
                # debug_mode=True,
            )
            
            master_agent = Agent(
                name="master_agent",
                role="""
                    You are the master agent overseeing the Connect Four game. Your primary objective is to coordinate the game flow using the following agents:
                    - **player_red_agent**: Selects moves for the RED player.
                    - **player_yellow_agent**: Selects moves for the YELLOW player.
                    - **board_state_manager**: Updates the board state based on the player's chosen move, following the rules of Connect Four (gravity rules).
                    - **result_checker**: Analyzes the board after each move to determine if there's a winner or a draw.

                    **Key Responsibilities:**
                    1. **Turn Management:** Alternate turns between the RED and YELLOW agents, starting with the RED player.
                    2. **Clear Commentary:** Provide clear, step-by-step commentary after every move, including which player made the move, which column was chosen, and any important updates.
                    3. **Board Display:** After every move, output the current board state in a clear, tabular format to reflect the updated game status.
                    4. **Move Validation:** When an agent selects a column, validate the move to ensure it's legal (i.e., the column is within bounds and not full). Clearly indicate if a move is invalid.
                    5. **Board Update:** After validating the move, send the move to the **board_state_manager** to get the updated board state according to the game rules.
                    6. **Game Progression:** Provide both the current board state and the list of legal moves to the current player’s agent to assist in move selection.
                    7. **Win/Draw Checking:** After every move, send the updated board to the **result_checker** to verify if there’s a winner or if the game has ended in a draw. Clearly announce the result of each check.
                    8. **Game Continuity:** Do not stop the game until the **result_checker** explicitly declares a winner or a draw.
                    9. **Clear Outcomes:** At the end of the game, respond with one of the following:
                    - `"WINNER - RED"` if the RED player wins.
                    - `"WINNER - YELLOW"` if the YELLOW player wins.
                    - `"TIE"` if the board is full with no winner.
                    10. **Consistent Board Updates:** Always output the board state in a tabular format after every move, validation, and result check for clarity.

                    **Important Rules:**
                    - The game starts with an empty board, and RED makes the first move.
                    - Tokens must follow the laws of gravity—they fall to the lowest available slot in the selected column.
                    - If an agent selects an invalid move (e.g., full column), prompt the same agent to select another move without switching turns.
                    - The master agent is strictly responsible for coordination and should not modify the board directly; always rely on the **board_state_manager** for board updates.
                    - The game only ends when the **result_checker** declares a winner or a tie.
                    - Do not end the game if there is no winner or a draw.
                """,
                instructions=[
                    "1. Coordinate the Connect Four game by managing turns between RED and YELLOW agents, starting with RED.",
                    "2. **After each move, clearly announce which player made the move and the column they chose.**",
                    "3. **Always output the board state in a clear, tabular format after each move and after important events.**",
                    "4. Provide the current board state and legal moves to the current player's agent to assist in move selection.",
                    "5. When a player selects a move, validate it to ensure the column is within bounds and not full. Clearly indicate if a move is invalid.",
                    "6. Use the **board_state_manager** agent to apply the move and receive the updated board state.",
                    "7. After updating the board, send the current board to the **result_checker** to determine if there’s a winner or a tie. Clearly announce the result of each check.",
                    "8. If the move is invalid, prompt the same player to make another move without switching turns.",
                    "9. Continue alternating turns and checking for a result until the **result_checker** declares a winner or a tie.",
                    "10. Clearly announce the final result with either 'WINNER - RED', 'WINNER - YELLOW', or 'TIE' at the end of the game.",
                    "11. **Ensure the board state is displayed in a tabular format after every step, including move selections, board updates, and result checks.**"
                ],
                model=OpenAIChat(id="gpt-4o"),
                markdown=True,
                team=[player_red_agent, player_yellow_agent, board_state_manager, result_checker],
                show_tool_calls=True,
            )


            return {
                "red": player_red_agent,
                "yellow": player_yellow_agent,
                "manager":board_state_manager,
                "checker":result_checker,
                # "move_generator": move_generator_agent,
                "master": master_agent,
            }
        except Exception as e:
            logger.error(f"Error initializing agents: {str(e)}")
            raise


    def start_game(self):
        """Start and manage the Connect Four game"""
        try:
            initial_state = self.board.get_board_state()
            response = self.agents["master"].print_response(
                f"New Connect Four game started. Current board state:\n{initial_state}\n"
                "Keep playing until there is a winner. Red plays first, then yellow and they keep switching.",
                stream=True,
            )
            
            for chunk in response:
                sys.stdout.write(chunk)
                sys.stdout.flush()
            
            return response
        except Exception as e:
            print(f"Error starting game: {str(e)}")
            raise
        

def main():
    try:
        game = Connect4Game()
        game.start_game()
    except Exception as e:
        print(f"Fatal error: {str(e)}")


if __name__ == "__main__":
    main()