from dataclasses import dataclass


@dataclass
class Slide:
    slide_number: int
    text_boxes: List[str]

    def extract_text(self):
        pass

    async def generate_explanation(self):
        pass
