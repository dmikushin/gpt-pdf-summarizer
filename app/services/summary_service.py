"""This module contains functions to generate summaries of text using the OpenAI GPT models."""

import os
import textwrap
import logging
import time
from typing import Optional

import openai
import streamlit as st
import asyncio

from .conversations import Conversations

# Set up logging
logging.basicConfig(level=logging.INFO)


@st.cache_resource
def set_openai_api_key(API_KEY: Optional[str] = None):
    """Set the OpenAI API key.

    The function first checks if the key is in the environment variables.
    If not, it uses the provided API_KEY argument. If the API_KEY argument is not provided, the function does nothing.

    Args:
        API_KEY (str, optional): The OpenAI API key. Defaults to None.
    """
    if "OPENAI_API_KEY" in os.environ:
        openai.api_key = os.environ.get("OPENAI_API_KEY")

    if API_KEY is not None:
        openai.api_key = API_KEY

    logging.info("API key set successfully.")


async def generate_summary(text: str, max_length: int = 100) -> str:
    """
    Generate a summary of the given text using the OpenAI GPT-3 model.

    Args:
        text (str): The text to summarize.
        max_length (int, optional): The maximum length of the summary. Defaults to 100.

    Returns:
        str: The generated summary.
    """
    prompt = f"Summarize this document :\n\n{text}\n"
    logging.debug(f"Prompt: {prompt}")

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.2,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        print(">>>>generate_summary::summary")
        summary = completion.choices[0].message["content"]
        print(f">>>>generate_summary::{completion.choices[0].message['content']}")
        return summary

    except Exception as e:
        logging.error(f"Error generating summary: {e}")
        return ""

async def summarize_large_text(
    conversations: Conversations,
    text: str,
    max_summarize_chars: int = 9000,
    max_chars_per_request: int = 4000,
    summary_chars_length: int = 1000,
) -> Conversations:
    """Summarize a large text by breaking it into chunks and summarizing each chunk separately.

    The summarized chunks are added to the conversation.

    Args:
        conversations (Conversations): The conversation object to add the summaries to.
        text (str): The text to summarize.
        max_summarize_chars (int, optional): The maximum number of characters to summarize. Defaults to 9000.
        max_chars_per_request (int, optional): The maximum number of characters per request. Defaults to 4000.
        summary_chars_length (int, optional): The length of the summary. Defaults to 1000.

    Returns:
        Conversations: The updated conversation object with the summaries added.
    """
    wrapped_text: list = textwrap.wrap(text, max_chars_per_request)
    length = max_summarize_chars // max_chars_per_request
    wrapped_text = wrapped_text[:length]

    progress_text = "Operation in progress. Please wait."
    my_bar = st.progress(0, text=progress_text)

    logging.debug(f"Wrapped text: {wrapped_text}")
    logging.debug(f"Length of wrapped text: {len(wrapped_text)}")
    logging.debug(f"Summary length: {summary_chars_length}")
    logging.debug(f"Max chars per request: {max_chars_per_request}")
    logging.debug(f"Max summarize chars: {max_summarize_chars}")

    logging.info("Generating summaries...")

    try:
        for idx, chunk in enumerate(wrapped_text):
            my_bar.progress(idx, text=progress_text)
            summary_chunk = await generate_summary(chunk, summary_chars_length)
            conversations.add_message("user", f"summarize: {chunk}")
            conversations.add_message("assistant", summary_chunk)
        return conversations
    except openai.InvalidRequestError as e:
        print("An error has occurred: ", e)
        # When a "request token exceeded limit" error occurs,
        # the number of characters in the request is reduced
        # by 20% and the request continues to be made.
        # The lower limit on the number of characters in a request
        # is set to 2000 to avoid multiple re-executions.
        if max_chars_per_request < 1000:
            raise e
        elif e.code == 'context_length_exceeded':
            return summarize_large_text(
                conversations,
                text,
                max_chars_per_request=int(max_chars_per_request * 0.8)
            )
        else:
            raise e


async def continue_conversation(
    conversations: Conversations, question: str
) -> Conversations:
    """
    Continue the conversation by adding a user question and generating a response from the assistant.

    Args:
        conversations (Conversations): The conversation object to add the question and response to.
        question (str): The user's question.

    Returns:
        Conversations: The updated conversation object with the question and response added.
    """
    conversations.add_message(role="user", content=question)

    try:
        response = await openai.ChatCompletion.create(
            model="gpt-3.5-turbo", temperature=0.3, messages=conversations.get_message_dict_list()
        )
    except Exception as e:
        logging.error(f"Error continuing conversation: {e}")
        return conversations

    answer = response.choices[0].message["content"]
    conversations.add_message(role="assistant", content=answer)

    return conversations
