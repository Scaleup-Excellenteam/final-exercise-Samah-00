import os
import json
from collections import namedtuple
import asyncio


from presentation.myPresentation import MyPresentation
from presentation.mySlide import MySlide


async def main(pptxfile):
    presentation = MyPresentation(filepath=pptxfile)
    presentation.parse()

    Explanations = namedtuple('Explanations', ['slide_number', 'explanation'])
    presentation.explanations = []

    for slide_number, _ in presentation.slides.items():  # Ignore slide_text_boxes for now
        slide_text_boxes = []  # Initialize as an empty list
        slide = MySlide(slide_number, slide_text_boxes)

    #     if not slide.extract_text():
    #         continue
    #
    #     explanation = await slide.generate_explanation()
    #     explanation_entry = Explanations(slide_number=slide_number, explanation=explanation)
    #     presentation.explanations.append(explanation_entry)
    #
    # filename = os.path.splitext(pptxfile)[0] + '.json'
    # with open(filename, 'w') as f:
    #     json.dump(presentation.explanations, f, indent=4)

# Path to the PowerPoint file
filepath = "End of course exercise - kickof - upload.pptx"

# Check if the file exists and has the correct extension
if os.path.isfile(filepath) and os.path.splitext(filepath)[1].lower() == ".pptx":
    # Run the main function asynchronously
    asyncio.run(main(filepath))
else:
    # Print an error message
    print("Invalid file path or unsupported file extension.")
