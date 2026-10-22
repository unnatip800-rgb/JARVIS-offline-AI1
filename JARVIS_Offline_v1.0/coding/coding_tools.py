from core.ai import ask_jarvis


# ============================================================
# CODING ASSISTANT
# ============================================================

def run_coding_action(
    action,
    content,
    language="Python",
):
    """
    Perform a coding-related task using the local LLM.
    """

    if not content.strip():

        return (
            "Please provide some code or a programming "
            "problem first."
        )

    # --------------------------------------------------------
    # ACTION INSTRUCTIONS
    # --------------------------------------------------------

    if action == "Generate Code":

        instruction = f"""
Generate clean, working {language} code for the
programming requirement provided by the user.

Requirements:

- Provide complete code.
- Use clear variable and function names.
- Add comments where useful.
- Do not unnecessarily complicate the solution.
- Explain how the code works after the code.
"""

    elif action == "Explain Code":

        instruction = f"""
Explain the following {language} code clearly.

Explain:

1. What the program does
2. How it works
3. Important functions
4. Important variables
5. The execution flow
6. Time and space complexity where applicable

Assume the student is learning programming.
"""

    elif action == "Debug Code":

        instruction = f"""
Debug the following {language} code.

Find:

1. Syntax errors
2. Runtime errors
3. Logical errors
4. Potential edge cases

Then provide:

CORRECTED CODE

After the corrected code, explain what was wrong
and how you fixed it.
"""

    elif action == "Review Code":

        instruction = f"""
Review the following {language} code as a senior
programmer helping a college student.

Analyze:

1. Correctness
2. Readability
3. Code structure
4. Potential bugs
5. Security concerns if applicable
6. Maintainability
7. Best practices

Give specific suggestions for improvement.
"""

    elif action == "Optimize Code":

        instruction = f"""
Optimize the following {language} code.

Look for:

- unnecessary operations
- inefficient algorithms
- repeated code
- unnecessary memory usage
- poor data structures

Provide:

1. Optimized code
2. Explanation of improvements
3. Before vs after complexity when possible
"""

    elif action == "Convert Code":

        instruction = f"""
Convert the provided code into the requested
programming language.

Preserve:

- functionality
- logic
- important behavior

Explain important differences between the
original and converted versions.
"""

    else:

        instruction = """
Help the student solve the programming problem.
"""

    # --------------------------------------------------------
    # BUILD PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are JARVIS, an offline programming assistant
for college students.

Programming language:

{language}

Task:

{instruction}

USER INPUT:

-------------------------

{content}

-------------------------

Important rules:

- Give technically accurate answers.
- Do not invent libraries or functions.
- Prefer simple solutions suitable for students.
- Format code using Markdown code blocks.
- Explain important concepts clearly.
"""

    # --------------------------------------------------------
    # LOCAL LLM
    # --------------------------------------------------------

    messages = [
        {
            "role": "user",
            "content": prompt,
        }
    ]

    return ask_jarvis(
        messages,
        mode="Coding",
    )