import os
import json
from collections import namedtuple
import asyncio
import time
import logging

from presentation.my_presentation import MyPresentation
from utilities import dir_utils


PROCESSED_FILES = set()
messages = {
    "no_unprocessed_files": "No unprocessed files found. Waiting for new files...",
    "invalid_file": "Invalid file path or unsupported file extension.",
    "process_success": "File processed successfully: ",
    "saved": "Explanation saved: "
}


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

    return presentation


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='{asctime} {levelname} {message}', style='{')

    while True:
        # Scan the uploads' folder for unprocessed files
        unprocessed_files = [file for file in dir_utils.get_files_list(dir_utils.UPLOAD_FOLDER)
                             if file not in PROCESSED_FILES]

        if not unprocessed_files:
            # If no unprocessed files found, print a message and continue to the next iteration
            logging.info(messages["no_unprocessed_files"])
            time.sleep(10)
            continue

        for file_name in unprocessed_files:
            # Get the full file path
            file_path = os.path.join(dir_utils.UPLOAD_FOLDER, file_name)

            # Check if the file exists and has the correct extension
            if os.path.isfile(file_path) and os.path.splitext(file_name)[1].lower() == ".pptx":
                # Process the file
                try:
                    logging.info(f"Processing file {file_name}")
                    presentation = asyncio.run(main(file_path))
                except Exception as e:
                    logging.error(f"Error processing file: {file_name}. Error: {e}")
                    continue
            else:
                # Print an error message and continue the loop
                logging.warning(f'{file_name}: {messages["invalid_file"]}')
                continue

            # Record the processed file
            PROCESSED_FILES.add(file_name)

            # Save the explanation JSON in the outputs folder
            output_file_path = os.path.join(dir_utils.OUTPUT_FOLDER, os.path.splitext(file_name)[0] + '.json')
            with open(output_file_path, 'w') as f:
                json.dump(presentation.explanations, f, indent=4)

            # Print debugging messages
            logging.info(f"{messages['process_success']}{file_name}")
            logging.info(f"{messages['saved']}{output_file_path}")

        # Sleep for a few seconds before the next iteration
        time.sleep(10)
