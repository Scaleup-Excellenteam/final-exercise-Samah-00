import asyncio
from dataclasses import dataclass
from typing import List
import openai
import time
import os
from dotenv import load_dotenv

# before running the code, please make sure that the environment variables section includes:
# name: OPENAI_API_KEY, value: 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
# Load environment variables from .env file
load_dotenv()

model = 'text-davinci-003'
max_tokens = 1000
error_messages = {
    "rate_limit": "Rate limit exceeded. Waiting for 60 seconds...",
    "authentication": "Invalid API key.",
    "exception": "An error occurred while calling the OpenAI API:",
    "timeout": "Request to OpenAI API timed out."
}


@dataclass
class MySlide:
    """
    Represents a slide in a presentation.

    Attributes:
        slide_number (int): The slide number.
        text_boxes (List[str]): List of text boxes in the slide.
    """

    slide_number: int
    text_boxes: List[str]

    async def generate_explanation(self):
        """
        Generates an explanation for the slide using OpenAI's GPT-3.5 model.

        Returns:
            str: The generated explanation for the slide.
        """
        # Get the API key from the environment variable
        openai.api_key = os.getenv("OPENAI_API_KEY")
        # Construct the prompt using the slide's text
        prompt = self.construct_prompt()

        # Send the prompt in a request to the OpenAI API
        response = None
        while not response:
            try:
                print(f"Processing Slide # {self.slide_number}")
                response = openai.Completion.create(
                    model=model,
                    prompt=prompt,
                    max_tokens=max_tokens,
                    stop=None,
                )
            except openai.error.AuthenticationError:
                print(error_messages["authentication"])
                return ""
            except asyncio.TimeoutError:
                print(error_messages["timeout"])
                return ""  # Return an empty string in case of a timeout
            except openai.error.RateLimitError:
                print(error_messages["rate_limit"])
                time.sleep(60)  # Wait for 60 seconds before making the next request
            except Exception as e:
                print(f"{error_messages['exception']} {e}")
                return ""  # Return an empty string in case of an error

        # Extract the AI's reply from the response
        if response and response.choices:
            reply = response.choices[0].text.strip()
        else:
            reply = ""  # If no response received

        return reply

    def construct_prompt(self):
        """
        Constructs the prompt for the slide.

        Returns:
            str: The constructed prompt.
        """
        # Construct the prompt using the slide's text
        prompt = f"Slide {self.slide_number}:"
        for text_box in self.text_boxes:
            prompt += f"\n{text_box}"
        prompt += "\n\nAI, please explain the slide."

        return prompt
