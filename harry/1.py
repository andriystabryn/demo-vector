#!/usr/bin/env python3
"""
Harry Potter Movie Specialist Agent
An AI agent that knows everything about Harry Potter movies.

Examples:
- Who played Hermione Granger?
- What happens in the Chamber of Secrets?
- Tell me about the Triwizard Tournament
- What are the Deathly Hallows?
- Who killed Dumbledore?
"""
import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from datetime import datetime
from langsmith import traceable

# Load environment variables
load_dotenv()

def get_current_date() -> str:
    """Get today's date and time.
    Use this tool when you need to know the current date or when discussing movie release dates in context of 'today'."""
    return datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")

@traceable(name="Harry Potter Agent - Chat Session")
def chat_session(agent, conversation_history):
    """Wrapper function to group all messages in one LangSmith trace"""
    # Chat loop
    while True:
        # Get user input
        user_input = input("You: ").strip()
        
        if not user_input:
            continue
            
        if user_input.lower() in ['quit', 'exit', 'bye', 'mischief managed']:
            print("\nMischief Managed! ⚡ Goodbye, and may magic be with you!\n")
            return conversation_history
        
        # Add user message to history
        conversation_history.append({"role": "user", "content": user_input})
        
        # Run the agent
        print("\nThinking...")
        try:
            result = agent.invoke(
                {"messages": conversation_history}
            )
            
            # Get the assistant's response
            assistant_message = result['messages'][-1].content
            
            # Add assistant response to history
            conversation_history.append({"role": "assistant", "content": assistant_message})
            
            # Print the response
            print(f"\nAssistant: {assistant_message}\n")
            print("-" * 60 + "\n")
            
        except Exception as e:
            print(f"\nError: {str(e)}\n")
            print("Please try again.\n")
            # Remove the failed user message from history
            conversation_history.pop()

def main():
    # Create tools list (minimal tools, agent relies on knowledge in system prompt)
    tools = [get_current_date]
    
    # Create agent using the new create_agent function
    agent = create_agent(
        model="gpt-4o-mini",
        tools=tools,
        system_prompt="""You are the ultimate Harry Potter and the Sorcerer's Stone movie specialist! You know EVERYTHING about all 8 Harry Potter and the Sorcerer's Stone.

Your expertise includes:
- All movie plots, scenes, and storylines (Only in Harry Potter and the Sorcerer's Stone movie)
- Cast members and characters (actors, roles, character development)
- Behind-the-scenes facts, production details, and trivia
- Filming locations, special effects, and cinematography
- Quotes, spells, magical creatures, and artifacts
- Differences between books and movies
- Box office performance, awards, and critical reception
- Timeline of events across all films
- Hogwarts houses, professors, and students
- The Wizarding World lore as presented in the films

Your personality:
- Enthusiastic and passionate about Harry Potter
- Friendly and engaging, like talking to a fellow Potterhead
- Use magical references naturally (e.g., "Brilliant!", "Blimey!", "That's magical!")
- Occasionally reference spells or quotes when appropriate
- Remember previous questions in the conversation and build on them

Guidelines:
- Provide detailed, accurate answers about the movies
- If asked about books vs movies, clarify the differences
- Share interesting trivia and behind-the-scenes facts
- Be conversational and fun while remaining informative
- If you're not 100% certain about something, say so honestly
- Format your responses clearly with proper structure when listing information

Remember: You're here to share the magic of Harry Potter movies with fans!""",
        name="Harry Potter Movie Specialist"
    )
    
    print("="*60)
    print("⚡ Welcome to the Harry Potter Movie Specialist! ⚡")
    print("Ask me ANYTHING about the Harry Potter films!")
    print("Characters, plots, trivia, cast, behind-the-scenes, and more.")
    print("I remember our conversation, so ask follow-up questions anytime.")
    print("Type 'quit', 'exit', or 'mischief managed' to end.")
    print("="*60 + "\n")
    
    # Initialize conversation history
    conversation_history = []
    
    # Start chat session (grouped in LangSmith)
    chat_session(agent, conversation_history)

if __name__ == "__main__":
    main()
