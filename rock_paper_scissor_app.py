import streamlit as st
from rock_paper_scissor_main import RockPaperScissorsGame

# Initialize the game
game = RockPaperScissorsGame()

st.title("🤖 Rock-Paper-Scissors AI Game")

# Placeholder for game results
result_placeholder = st.empty()

# Start the game button
if st.button("Start Game"):
    with st.spinner("Playing 5 rounds..."):
        
        response = game.agents["master"].run(
                "New Rock-Paper-Scissors game started. Play 5 rounds. RED and YELLOW will alternate their moves. The player with the most wins will be declared the winner.",
                stream=True,
        )

        full_output = ""  # To accumulate the streamed response

        # Stream the output to the UI
        for chunk in response:
            full_output += chunk.content
            result_placeholder.markdown(full_output)  # Dynamically update the UI

        # Final output
        st.success("🎯 Game Over!")
        st.text_area("📜 Full Game Log", full_output, height=400)

        # Display the full game output
        result_placeholder.text(full_output)

# Option to restart the game
if st.button("Restart Game"):
    st.experimental_rerun()
