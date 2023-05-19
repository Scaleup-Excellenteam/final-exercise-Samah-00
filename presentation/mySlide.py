from dataclasses import dataclass
from typing import List
import openai
import time


openai.api_key = "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"
model = 'text-davinci-003'


@dataclass
class MySlide:
    slide_number: int
    text_boxes: List[str]

    async def generate_explanation(self):
        # Construct the prompt using the slide's text
        prompt = self.construct_prompt()

        time.sleep(20)  # Delay for 20 seconds

        # Send the prompt in a request to the OpenAI API
        response = None
        try:
            response = openai.Completion.create(
                model=model,  # Use the gpt-3.5-turbo model
                prompt=prompt,
                max_tokens=300,
                n=1,  # Generate a single response
                stop=None,
            )
        except Exception as e:
            print(f"An error occurred while calling the OpenAI API: {e}")
            return ""  # Return an empty string in case of an error

        # Extract the AI's reply from the response
        if response and response.choices:
            reply = response.choices[0].text.strip()
        else:
            reply = ""  # If no response received

        return reply

    def construct_prompt(self):
        # Construct the prompt using the slide's text
        prompt = f"Slide {self.slide_number}:"
        for text_box in self.text_boxes:
            prompt += f"\n{text_box}"
        prompt += "\n\nAI, please explain the slide."

        return prompt
