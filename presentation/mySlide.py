from dataclasses import dataclass
from typing import List


@dataclass
class MySlide:
    slide_number: int
    text_boxes: List[str]

    def extract_text(self):
        pass

    async def generate_explanation(self):
        pass
