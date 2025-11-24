# Import required modules
import os
from dotenv import load_dotenv
from openai import OpenAI

# Loading API key from .env file (keeps your key private)

load_dotenv()  # Looks for .env file in the project root
api_key = os.getenv("OPENAI_API_KEY")  # Fetch OPENAI_API_KEY from .env

# Fail if no key is set (guides the user)
if not api_key:
    print("No OpenAI API key found — running in DEMO MODE.")
    demo_questions = [
        ("What is 2 + 2?", "4", "2 plus 2 is 4."),
        ("What is the capital of France?", "Paris", "Paris is the capital of France.")
    ]
    score = 0
    for i, (q, a, e) in enumerate(demo_questions):
        print(f"\nQuestion {i+1}: {q}")
        user_answer = input("Your answer: ")
        if user_answer.strip().lower() == a.lower():
            print("Correct!")
            score += 1
        else:
            print(f"Incorrect. Correct answer: {a}")
            if input("Want an explanation? (yes/no): ").strip().lower() == "yes":
                print("Explanation:", e)
    print(f"\nDemo complete! Your score: {score}/{len(demo_questions)}")
    exit()

# Set the global API key for OpenAI API
client = OpenAI(api_key=api_key)

print("Welcome to the AI Quiz Bot!")

# Ask the user to choose a subject and difficulty for the quiz
subject = input("Choose a subject: either Maths/Science): ").strip()
difficulty = input("Choose a difficulty: easy/medium/hard): ").strip()

# Ask how many questions they want to answer
rounds = int(input("How many questions would you like to answer? "))

def generate_question(subject, difficulty):
    """
    Uses OpenAI API to generate a quiz question, answer, and explanation
    based on the chosen subject and difficulty.
    """
    prompt = (
        f"Generate a {difficulty} level {subject} quiz question. "
        "Provide ONLY: 1. The question, 2. The short answer, 3. A brief explanation. "
        "Format: 'Question: ... Answer: ... Explanation: ...'"
    )

    # Send request to OpenAI Chat model
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=0.7
    )
    output = response.choices[0].message.content

    # Parse output into question, answer, and explanation safely
    question = ""
    answer = ""
    explanation = ""

    for line in output.split("\n"):
        line = line.strip()
        if line.lower().startswith("question:"):
            question = line.split(":", 1)[1].strip()
        elif line.lower().startswith("answer:"):
            answer = line.split(":", 1)[1].strip()
        elif line.lower().startswith("explanation:"):
            explanation = line.split(":", 1)[1].strip()

    return question, answer, explanation

def check_answer(question, answer, user_answer):
    """
    Asks OpenAI API to evaluate whether the user's answer is correct.
    Only expects 'Yes' or 'No' as a reply.
    """
    prompt = (
        f"Question: {question}\n"
        f"Correct Answer: {answer}\n"
        f"User Answer: {user_answer}\n"
        "Is the user's answer correct? Respond only with Yes or No."
    )

    # Send the prompt to the OpenAI ChatCompletion API and get its response
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=5,
        temperature=0
    )

    verdict = response.choices[0].message.content.strip()
    return verdict == "Yes"

score = 0  # Track the user's score

# Loop over each question
for i in range(rounds):
    # Generate a new question, answer, and explanation
    question, answer, explanation = generate_question(subject, difficulty)
    print(f"\nQuestion {i+1}: {question}")
    user_answer = input("Your answer: ")

    # Check the user's answer using the AI
    if check_answer(question, answer, user_answer):
        print("Correct!")
        score += 1  # Increment score if correct
    else:
        print(f"Incorrect. Correct answer: {answer}")
        # Offer the explanation if they want it
        if input("Want an explanation? (yes/no): ").strip().lower() == "yes":
            print("Explanation:", explanation)

# Display final results
print(f"\nQuiz Complete! Your score: {score}/{rounds}")
