import requests

from core.config import (
    OLLAMA_URL,
    MODEL
)

from core.prompts import (
    get_system_prompt
)


def ask_jarvis(
    messages,
    mode="General",
    document_context="",
    memories=None
):

    system_prompt = get_system_prompt(mode)

    conversation = system_prompt

    # -----------------------------------------
    # Long-term memory
    # -----------------------------------------

    if memories:

        conversation += """

RELEVANT USER MEMORY:

"""

        for memory in memories:

            conversation += (
                f"- {memory}\n"
            )

    # -----------------------------------------
    # Document context
    # -----------------------------------------

    if document_context:

        conversation += """

RELEVANT DOCUMENT INFORMATION:

-------------------------

"""

        conversation += document_context

        conversation += """

-------------------------

Use the document information when
answering the user's question.

If the answer cannot be found in
the document, say so clearly.
"""

    # -----------------------------------------
    # Conversation
    # -----------------------------------------

    conversation += """

CONVERSATION:

"""

    for message in messages:

        if message["role"] == "user":

            conversation += (
                f"Student: {message['content']}\n"
            )

        else:

            conversation += (
                f"JARVIS: {message['content']}\n"
            )

    conversation += "\nJARVIS:"

    # -----------------------------------------
    # Ollama
    # -----------------------------------------

    response = requests.post(

        OLLAMA_URL,

        json={
            "model": MODEL,
            "prompt": conversation,
            "stream": False
        },

        timeout=180
    )

    response.raise_for_status()

    data = response.json()

    return data["response"]