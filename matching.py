
import math
import os

from dotenv import load_dotenv
from google import genai

from embedding import generate_embedding

load_dotenv()

# Gemini API configuration
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing")

client = genai.Client(api_key=api_key)


# Calculate cosine similarity between two embeddings
def cosine_similarity(vector_a, vector_b):

    if len(vector_a) != len(vector_b):
        raise ValueError("Embedding dimensions do not match")

    dot_product = sum(
        a * b for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(
        sum(a * a for a in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(b * b for b in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


# Calculate relevance between an agent and a post
def calculate_relevance(agent, post):

    agent_embedding = agent.get("embedding")
    post_embedding = post.get("embedding")

    # Generate embedding for older agent records
    if not agent_embedding:
        agent_text = " ".join(
            agent.get("interests", [])
        )

        agent_embedding = generate_embedding(agent_text)

    # Generate embedding for older post records
    if not post_embedding:
        post_text = (
            post.get("category", "") + " " +
            post.get("content", "")
        )

        post_embedding = generate_embedding(post_text)

    score = cosine_similarity(
        agent_embedding,
        post_embedding
    )

    return round(score, 4)


# Generate an AI comment for an agent
def generate_comment(agent, post):

    company_name = agent.get(
        "company_name",
        "Our company"
    )

    interests = agent.get("interests", [])

    prompt = f"""
    You are an AI agent representing {company_name}.

    Your interests:
    {", ".join(interests)}

    Another company published this post:

    {post.get("content", "")}

    Category:
    {post.get("category", "")}

    Write a professional and natural comment responding
    to this post.

    Requirements:
    - Connect the post with your company's interests.
    - Show genuine interest in collaboration.
    - Keep the response under 80 words.
    - Do not invent company facts.
    - Return only the comment.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        generated_comment = response.text

        if generated_comment and generated_comment.strip():
            return generated_comment.strip()

        raise ValueError(
            "Gemini returned an empty comment"
        )

    except Exception as error:

        print(
            "Gemini Comment Generation Failed:",
            error
        )

        return (
            f"{company_name} found your post interesting. "
            "Let's explore a possible collaboration!"
        )
