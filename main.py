import os
import json
from collections import namedtuple

from presentation.presentation import Presentation
from presentation.mySlide import Slide


async def main(filepath):
    presentation = Presentation(filepath=filepath)
    presentation.parse()

    Explanations = namedtuple('Explanations', ['slide_number', 'explanation'])
    presentation.explanations = []

    for slide_number, slide_text_boxes in presentation.slides.items():
        slide = Slide(slide_number, slide_text_boxes)

        if not slide.extract_text():
            continue

        explanation = await slide.generate_explanation()
        explanation_entry = Explanations(slide_number=slide_number, explanation=explanation)
        presentation.explanations.append(explanation_entry)

    filename = os.path.splitext(filepath)[0] + '.json'
    with open(filename, 'w') as f:
        json.dump(presentation.explanations, f, indent=4)
