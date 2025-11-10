"""
Shared embedding generation utilities
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_embedding(text: str, model="text-embedding-3-small") -> list[float]:
    """
    Generate embedding for a text using OpenAI.
    
    Args:
        text: The text to generate embedding for
        model: The OpenAI embedding model to use
    
    Returns:
        List of floats representing the embedding vector
    """
    text = text.replace("\n", " ")
    response = openai_client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding
