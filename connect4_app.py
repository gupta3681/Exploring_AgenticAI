import streamlit as st
from connect4_main import Connect4Game

# Streamlit UI
st.title("🤖 Connect Four AI Battle")

# Button to start the game
if st.button("Start Game"):
    st.write("### 🕹️ Game in Progress...")

    game = Connect4Game()
    
    # Placeholder to stream output
    output_placeholder = st.empty()

    try:
        # Start the game and stream the response
        response = game.agents["master"].run(
            f"Current board state:\n{game.board.get_board_state()}\n"
            "Keep managing and outpting board until there is a winner. Red plays first, then yellow and they keep switching.",
            stream=True,
        )

        full_output = ""  # To accumulate the streamed response

        # Stream the output to the UI
        for chunk in response:
            full_output += chunk.content
            output_placeholder.markdown(full_output)  # Dynamically update the UI

        # Final output
        st.success("🎯 Game Over!")
        st.text_area("📜 Full Game Log", full_output, height=400)

    except Exception as e:
        st.error(f"Error starting game: {str(e)}")
