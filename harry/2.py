#!/usr/bin/env python3
"""
RAG Chatbot for Harry Potter and the Sorcerer's Stone Screenplay
Uses Supabase vector database for semantic search

Examples:
- What happens when Harry talks to the snake?
- Tell me about the scene at the zoo
- What does Uncle Vernon say to Harry?
- Describe the Dursleys
"""
import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from datetime import datetime
import json
from openai import OpenAI
from supabase import create_client, Client
from langsmith import traceable

# Load environment variables
load_dotenv()

# Initialize clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def generate_embedding(text: str) -> list[float]:
    """Generate embedding for a text using OpenAI."""
    text = text.replace("\n", " ")
    response = openai_client.embeddings.create(
        input=[text], 
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def search_screenplay(query: str) -> str:
    """Search the Harry Potter and the Sorcerer's Stone screenplay using semantic vector search.
    
    This tool searches through the screenplay which is divided into scenes. It uses AI embeddings
    to find the most semantically relevant scenes based on the meaning of your query, not just keywords.
    Each result shows the scene number, scene title, and full scene content.
    
    Use this tool when the user asks questions about:
    - Character dialogue or quotes
    - Specific events or plot points
    - Scene descriptions or actions
    - Character interactions or relationships
    
    Args:
        query: The user's question or search query about the screenplay
    
    Returns:
        Relevant scenes from the screenplay with scene numbers, titles, and similarity scores
    """
    try:
        # Generate embedding for the query
        query_embedding = generate_embedding(query)
        
        # Search in Supabase
        result = supabase.rpc(
            'match_harry_potter',
            {
                'query_embedding': query_embedding,
                'match_threshold': 0.35,  # Lower threshold to catch more results
                'match_count': 5  # Return more results for better context
            }
        ).execute()
        
        if not result.data:
            return "No relevant information found in the screenplay."
        
        # Format the results
        formatted_results = []
        for i, doc in enumerate(result.data, 1):
            formatted_results.append(
                f"[Scene {doc['scene_number']}: {doc['scene_title']} - Similarity: {doc['similarity']:.2f}]\n"
                f"{doc['content']}"
            )
        
        return "\n\n---\n\n".join(formatted_results)
        
    except Exception as e:
        return f"Error searching screenplay: {str(e)}"

def get_scene_by_number(scene_number: int, include_adjacent: bool = False) -> str:
    """Get the content of a specific scene, optionally including adjacent scenes.
    Use this tool when you need to see a specific scene number or explore scenes around a found result.
    
    Args:
        scene_number: The scene number to retrieve (0-22)
        include_adjacent: If True, also returns the previous and next scenes for context
    
    Returns:
        The scene content, or adjacent scenes if requested
    """
    try:
        if include_adjacent:
            # Get the scene and its neighbors
            scenes_to_fetch = [scene_number - 1, scene_number, scene_number + 1]
            scenes_to_fetch = [s for s in scenes_to_fetch if 0 <= s <= 22]  # Keep valid scenes only
            
            result = supabase.table('harry_potter').select('*').in_('scene_number', scenes_to_fetch).order('scene_number').execute()
        else:
            # Get just the specific scene
            result = supabase.table('harry_potter').select('*').eq('scene_number', scene_number).execute()
        
        if not result.data:
            return f"Scene {scene_number} not found in the database."
        
        # Format the results
        formatted_scenes = []
        for doc in result.data:
            formatted_scenes.append(
                f"[Scene {doc['scene_number']}: {doc['scene_title']}]\n"
                f"{doc['content']}"
            )
        
        return "\n\n---\n\n".join(formatted_scenes)
        
    except Exception as e:
        return f"Error fetching scene: {str(e)}"

def get_screenplay_stats() -> str:
    """Get statistics about the Harry Potter screenplay database.
    Use this when the user asks about the screenplay length, number of pages, or general information.
    
    Returns:
        Statistics about the screenplay as a formatted string
    """
    try:
        result = supabase.table('harry_potter').select('*', count='exact').execute()
        count = result.count
        
        return f"""Harry Potter and the Sorcerer's Stone Screenplay:
- Total pages indexed: {count}
- Source: Original movie screenplay by Steve Kloves
- Based on the novel by J.K. Rowling
- You can ask me about any scene, character, or dialogue from the movie!"""
    except Exception as e:
        return f"Error getting screenplay stats: {str(e)}"

def get_today_date() -> str:
    """Get today's date.
    Use this tool when you need to know the current date, day of the week, or answer questions about today."""
    return datetime.now().strftime("%A, %B %d, %Y")

@traceable(name="2.py - RAG Chat Session")
def chat_session(agent, conversation_history):
    """Wrapper function to group all messages in one LangSmith trace"""
    # Chat loop
    while True:
        # Get user input
        user_input = input("You: ").strip()
        
        if not user_input:
            continue
            
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("\nGoodbye! Thanks for exploring the Harry Potter screenplay! 🪄\n")
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
    # Create tools list
    tools = [search_screenplay, get_scene_by_number, get_screenplay_stats, get_today_date]
    
    # Create agent using the new create_agent function
    agent = create_agent(
        model="gpt-4o-mini",
        tools=tools,
        system_prompt="""You are a helpful AI assistant with deep knowledge of the Harry Potter and the Sorcerer's Stone screenplay.
You help users explore scenes, characters, and dialogue from the movie.
When answering questions, use the search_screenplay tool to find relevant information from the actual screenplay.
If you need more context around a found scene, use get_scene_by_number with include_adjacent=True to see surrounding scenes.
Provide accurate, engaging responses based on the screenplay content.
If you find relevant scenes, reference the scene numbers and titles.
Remember the conversation context and refer back to previous questions when relevant.""",
        name="2.py - Harry Potter RAG Chat"
    )
    
    print("=" * 60)
    print("🪄 Harry Potter Screenplay RAG Chatbot 🪄")
    print("Ask me anything about Harry Potter and the Sorcerer's Stone!")
    print("I can help you explore scenes, characters, and dialogue.")
    print("Type 'quit' or 'exit' to end the conversation.")
    print("=" * 60 + "\n")
    
    # Initialize conversation history
    conversation_history = []
    
    # Start chat session (grouped in LangSmith)
    chat_session(agent, conversation_history)

if __name__ == "__main__":
    main()
