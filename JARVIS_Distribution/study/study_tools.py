from core.ai import ask_jarvis


# ============================================================
# STUDY ASSISTANT
# ============================================================

def run_study_action(
    action,
    content,
    document_context="",
):
    """
    Perform a study-related task using the local LLM.
    """

    if not content and not document_context:

        return (
            "Please provide some study material first. "
            "You can upload a PDF or enter a topic."
        )

    # --------------------------------------------------------
    # Select instruction
    # --------------------------------------------------------

    if action == "Explain":

        instruction = """
Explain the topic clearly for a college student.

Start with a simple explanation.

Then explain the important concepts.

Use examples where helpful.

Avoid unnecessary complexity.
"""

    elif action == "Summarize":

        instruction = """
Create a well-structured study summary.

Include:

1. Main concepts
2. Important definitions
3. Key points
4. Important formulas or rules
5. Examples where useful

Keep it useful for exam revision.
"""

    elif action == "Important Questions":

        instruction = """
Analyze the study material and generate important
college-level examination questions.

Divide them into:

SHORT ANSWER QUESTIONS

LONG ANSWER QUESTIONS

CONCEPTUAL QUESTIONS

Do not invent information that is not supported
by the provided material.
"""

    elif action == "Flashcards":

        instruction = """
Create useful study flashcards.

Format every card exactly like:

CARD 1
Question: ...
Answer: ...

CARD 2
Question: ...
Answer: ...

Create approximately 10 cards.

Focus on important concepts and definitions.
"""

    elif action == "Quiz":

        instruction = """
Create a college-level quiz from the study material.

Create 10 multiple-choice questions.

Format:

Q1. Question

A. Option
B. Option
C. Option
D. Option

Do NOT reveal the answers immediately.

After all questions, provide:

ANSWER KEY

Q1: ...
Q2: ...
etc.
"""

    elif action == "Study Plan":

        instruction = """
Create a practical study plan based on the provided
material.

Organize it into:

Day 1
Day 2
Day 3
...

For each day include:

- Topics
- What to understand
- What to revise
- Practice activities

Prioritize important concepts.
"""

    else:

        instruction = """
Help the student understand the provided material.
"""

    # --------------------------------------------------------
    # Build prompt
    # --------------------------------------------------------

    prompt = f"""
You are JARVIS, an offline college study assistant.

Your task is:

{instruction}

STUDY MATERIAL:

-------------------------

{content}

-------------------------

"""

    if document_context:

        prompt += f"""

RELEVANT DOCUMENT CONTEXT:

-------------------------

{document_context}

-------------------------

"""

    prompt += """

Answer as a helpful college tutor.

Be accurate.

Use clear headings and bullet points.

Do not claim information that is not supported
by the provided material.
"""

    # --------------------------------------------------------
    # Use local Ollama
    # --------------------------------------------------------

    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]

    return ask_jarvis(
        messages,
        mode="Study"
    )