import os
import json
from collections import namedtuple
import asyncio


from presentation.myPresentation import MyPresentation


async def main(pptxfile):
    """
    Main function to generate explanations for each slide in a PowerPoint presentation.

    Args:
        pptxfile (str): The path to the PowerPoint file.

    Generates explanations for each slide in the PowerPoint presentation, stores them in a list of namedtuples,
    and saves the explanations to a JSON file.

    The explanations are stored as namedtuples with fields 'slide_number' and 'explanation'.

    The JSON file is saved with the same name as the PowerPoint file, but with the extension '.json'.

    Example usage:
        asyncio.run(main("presentation.pptx"))
    """
    presentation = MyPresentation(filepath=pptxfile)
    presentation.parse()

    Explanations = namedtuple('Explanations', ['slide_number', 'explanation'])
    presentation.explanations = []

    for slide_number, slide in presentation.slides.items():
        explanation = await slide.generate_explanation()
        explanation_entry = Explanations(slide_number=slide_number, explanation=explanation)
        presentation.explanations.append(explanation_entry)

    filename = os.path.splitext(pptxfile)[0] + '.json'
    with open(filename, 'w') as f:
        json.dump(presentation.explanations, f, indent=4)


if __name__ == '__main__':
    while True:
        # Get the file name from the user
        file_name = input("Enter the name of the PowerPoint file: ")

        # Check if the file exists and has the correct extension
        if os.path.isfile(file_name) and os.path.splitext(file_name)[1].lower() == ".pptx":
            # Run the main function asynchronously
            asyncio.run(main(file_name))
            break  # Exit the loop if a valid file path is provided
        else:
            # Print an error message and continue the loop
            print("Invalid file path or unsupported file extension.")
