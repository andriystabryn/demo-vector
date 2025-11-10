#!/usr/bin/env python3
"""
RAG Chatbot for AICompany HR Policies
Uses Supabase vector database for semantic search

Examples:
- How many vacation days do I get?
- What is the remote work policy?
- How do I request parental leave?
- What are the working hours?
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

def search_policies(query: str) -> str:
    """Search the AICompany policy document using semantic vector search.
    
    This tool searches through company policies which are divided into sections. It uses AI embeddings
    to find the most semantically relevant policy sections based on the meaning of your query, not just keywords.
    Each result shows the section number, section title, and full section content.
    
    Use this tool when the user asks questions about:
    - Company policies and procedures
    - Benefits and compensation
    - Leave policies and time off
    - Work schedules and remote work
    - Code of conduct and compliance
    
    Args:
        query: The user's question or search query about company policies
    
    Returns:
        Relevant policy sections with section numbers, titles, and similarity scores
    """
    try:
        # Generate embedding for the query
        query_embedding = generate_embedding(query)
        
        # Search in Supabase
        result = supabase.rpc(
            'match_aicompany_policies',
            {
                'query_embedding': query_embedding,
                'match_threshold': 0.35,  # Lower threshold to catch more results
                'match_count': 5  # Return more results for better context
            }
        ).execute()
        
        if not result.data:
            return "No relevant information found in the company policies."
        
        # Format the results
        formatted_results = []
        for i, doc in enumerate(result.data, 1):
            formatted_results.append(
                f"[Section {doc['section_number']}: {doc['section_title']} - Similarity: {doc['similarity']:.2f}]\n"
                f"{doc['content']}"
            )
        
        return "\n\n---\n\n".join(formatted_results)
        
    except Exception as e:
        return f"Error searching policies: {str(e)}"

def get_section_by_number(section_number: int, include_adjacent: bool = False) -> str:
    """Get the content of a specific policy section, optionally including adjacent sections.
    Use this tool when you need to see a specific section number or explore sections around a found result.
    
    Args:
        section_number: The section number to retrieve (0-12)
        include_adjacent: If True, also returns the previous and next sections for context
    
    Returns:
        The section content, or adjacent sections if requested
    """
    try:
        if include_adjacent:
            # Get the section and its neighbors
            sections_to_fetch = [section_number - 1, section_number, section_number + 1]
            sections_to_fetch = [s for s in sections_to_fetch if 0 <= s <= 12]  # Keep valid sections only
            
            result = supabase.table('aicompany_policies').select('*').in_('section_number', sections_to_fetch).order('section_number').execute()
        else:
            # Get just the specific section
            result = supabase.table('aicompany_policies').select('*').eq('section_number', section_number).execute()
        
        if not result.data:
            return f"Section {section_number} not found in the database."
        
        # Format the results
        formatted_sections = []
        for doc in result.data:
            formatted_sections.append(
                f"[Section {doc['section_number']}: {doc['section_title']}]\n"
                f"{doc['content']}"
            )
        
        return "\n\n---\n\n".join(formatted_sections)
        
    except Exception as e:
        return f"Error fetching section: {str(e)}"

def get_policy_stats() -> str:
    """Get statistics about the AICompany policy database.
    Use this when the user asks about the policy document length, number of sections, or general information.
    
    Returns:
        Statistics about the policy document as a formatted string
    """
    try:
        result = supabase.table('aicompany_policies').select('*', count='exact').execute()
        count = result.count
        
        return f"""AICompany Policy Document:
- Total sections indexed: {count}
- Last Updated: November 2024
- Covers: Work policies, benefits, code of conduct, and more
- You can ask me about any company policy, benefit, or procedure!"""
    except Exception as e:
        return f"Error getting policy stats: {str(e)}"

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
            print("\nGoodbye! Feel free to reach out if you have more policy questions! 👋\n")
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
    tools = [search_policies, get_section_by_number, get_policy_stats, get_today_date]
    
    # Create agent using the new create_agent function
    agent = create_agent(
        model="gpt-4o-mini",
        tools=tools,
        system_prompt="""You are a helpful HR assistant with deep knowledge of AICompany's policies and procedures.
You help employees understand company policies, benefits, procedures, and guidelines.
When answering questions, use the search_policies tool to find relevant information from the official policy document.
If you need more context around a found section, use get_section_by_number with include_adjacent=True to see surrounding sections.
Provide accurate, professional responses based on the policy content.
If you find relevant sections, reference the section numbers and titles.
Remember the conversation context and refer back to previous questions when relevant.
Be friendly and helpful, but always base your answers on the actual policy document.""",
        name="2.py - AICompany HR Assistant"
    )
    
    print("=" * 60)
    print("👔 AICompany HR Policy Assistant 👔")
    print("Ask me anything about AICompany policies and procedures!")
    print("I can help with benefits, leave, work schedules, and more.")
    print("Type 'quit' or 'exit' to end the conversation.")
    print("=" * 60 + "\n")
    
    # Initialize conversation history
    conversation_history = []
    
    # Start chat session (grouped in LangSmith)
    chat_session(agent, conversation_history)

if __name__ == "__main__":
    main()
