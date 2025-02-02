from typing import Dict
import sys
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.utils.log import logger


class RockPaperScissorsGame:
    def __init__(self):
        try:
            self.agents = self._initialize_agents()
        except Exception as e:
            logger.error(f"Failed to initialize agents: {str(e)}")
            raise

    def _initialize_agents(self) -> Dict[str, Agent]:
        """Initialize all required agents for Rock-Paper-Scissors with specific roles"""
        try:
            player_red_agent = Agent(
                name="player_red_agent",
                role="""
                    You are a Rock-Paper-Scissors player playing as RED. 
                    Your task is to select one of the three options: 'Rock', 'Paper', or 'Scissors'.
                    Consider simple strategies but make random choices to keep the game unpredictable.
                    Do not select the same option everytime.
                    Respond ONLY with your choice.
                """,
                model=OpenAIChat(id="gpt-4o"),
            )

            player_yellow_agent = Agent(
                name="player_yellow_agent",
                role="""
                    You are a Rock-Paper-Scissors player playing as YELLOW. 
                    Your task is to select one of the three options: 'Rock', 'Paper', or 'Scissors'.
                    You are slightly more strategic and may try to counter the RED player's previous choices.
                    Respond ONLY with your choice.
                    Do not select the same choice everytime. 
                """,
                model=OpenAIChat(id="gpt-4o"),
            )

            result_checker = Agent(
                name="result_checker",
                role="""
                    You are responsible for determining the winner in a Rock-Paper-Scissors game.
                    Given the choices of both players (RED and YELLOW), determine the winner based on the rules:
                    - Rock beats Scissors
                    - Scissors beats Paper
                    - Paper beats Rock
                    If both players choose the same, it's a draw.

                    Respond with 'WINNER - RED', 'WINNER - YELLOW', or 'DRAW' based on the outcome.
                """,
                model=OpenAIChat(id="gpt-4o"),
            )

            master_agent = Agent(
                name="master_agent",
                role="""
                    You are the master agent overseeing the Rock-Paper-Scissors game. 
                    Your job is to coordinate the gameplay using the following agents:
                    - **player_red_agent**: Chooses move for the RED player.
                    - **player_yellow_agent**: Chooses move for the YELLOW player.
                    - **result_checker**: Determines the winner based on both players' choices.

                    **Responsibilities:**
                    1. Start the game and clearly announce when each round begins.
                    2. Request choices from both RED and YELLOW agents.
                    3. Send both choices to the **result_checker** to determine the winner.
                    4. Display the choices of both players and the result after each round.
                    5. Continue for 5 rounds and declare the final winner based on who won the most rounds.

                    Respond with commentary after each round and provide the final score at the end.
                """,
                 instructions=[
                    "1. Ensure that all 5 rounds are played and do not stop before the 5 rounds.",
                ],
                model=OpenAIChat(id="gpt-4o"),
                markdown=True,
                team=[player_red_agent, player_yellow_agent, result_checker],
                show_tool_calls=True,
            )

            return {
                "red": player_red_agent,
                "yellow": player_yellow_agent,
                "checker": result_checker,
                "master": master_agent,
            }
        except Exception as e:
            logger.error(f"Error initializing agents: {str(e)}")
            raise

    def start_game(self):
        """Start and manage the Rock-Paper-Scissors game"""
        try:
            response = self.agents["master"].run(
                "New Rock-Paper-Scissors game started. Play 5 rounds. RED and YELLOW will alternate their moves. The player with the most wins will be declared the winner.",
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
        game = RockPaperScissorsGame()
        game.start_game()
    except Exception as e:
        print(f"Fatal error: {str(e)}")


if __name__ == "__main__":
    main()
