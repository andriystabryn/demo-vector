#!/usr/bin/env python3
"""
AICompany HR Policy Specialist Agent (Non-RAG Version)
An AI agent that uses its general knowledge to answer policy questions.

Examples:
- How many vacation days do employees typically get?
- What is a standard remote work policy?
- Tell me about parental leave
- What are typical working hours?
- How does PTO usually work?
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

@traceable(name="AICompany Non-RAG Agent - Chat Session")
def chat_session(agent, conversation_history):
    """Wrapper function to group all messages in one LangSmith trace"""
    # Chat loop
    while True:
        # Get user input
        user_input = input("You: ").strip()
        
        if not user_input:
            continue
            
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("\nGoodbye! Feel free to reach out if you have more questions! 👋\n")
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
        system_prompt="""You are an HR assistant helping employees understand company policies and procedures.

IMPORTANT: You do NOT have access to AICompany's actual policy documents. You can only provide general guidance based on typical HR practices and common company policies.

Your approach:
- Provide general information about typical company policies
- Use phrases like "typically", "usually", "in most companies", "standard practice is"
- Acknowledge when you're giving general advice vs. specific company policy
- Recommend employees check official documentation or contact HR for specific details
- Be helpful but make it clear you're providing general guidance, not official policy

Your personality:
- Professional and helpful
- Friendly and approachable
- Honest about limitations
- Encourage employees to verify information with official sources

Guidelines:
- Provide helpful general information about HR topics
- Always clarify that you're giving general guidance, not AICompany-specific policy
- Suggest checking official policy documents for exact details
- Be conversational while remaining professional
- If you're uncertain, say so and recommend contacting HR directly
- Format your responses clearly with proper structure when listing information

Remember: You're here to provide general HR guidance, not official AICompany policy!""",
        name="AICompany Non-RAG HR Assistant"
    )
    
    print("="*60)
    print("💼 AICompany HR Assistant (Non-RAG Version) 💼")
    print("Ask me about general HR policies and procedures!")
    print("Note: I provide general guidance, not official AICompany policy.")
    print("For specific details, please check official documentation.")
    print("Type 'quit' or 'exit' to end.")
    print("="*60 + "\n")
    
    # Initialize conversation history
    conversation_history = []
    
    # Start chat session (grouped in LangSmith)
    chat_session(agent, conversation_history)

if __name__ == "__main__":
    main()
