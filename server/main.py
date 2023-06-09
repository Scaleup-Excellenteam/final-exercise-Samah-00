import json
import os
import uuid
from datetime import datetime
from flask import Flask, request, jsonify

DEFAULT_PORT = 8080

# create an instance of the Flask class and assigns it to the variable app
app = Flask(__name__)
UPLOAD_FOLDER = '..\\uploads'
OUTPUT_FOLDER = '..\\outputs'
# set the configuration parameter 'UPLOAD_FOLDER' in app object to the value of UPLOAD_FOLDER
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def generate_filename(uid, original_filename):
    """
        Generate a new filename by combining the original filename, timestamp, and UID.

        Args:
            uid (str): Unique identifier for the file.
            original_filename (str): Original filename of the uploaded file.

        Returns:
            str: New filename with the format 'original_filename_timestamp_uid'.
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"{''.join(original_filename.split('.')[:-1])}_{timestamp}_{uid}.{original_filename.split('.')[-1]}"


def save_file(file, filename):
    """
       Save the uploaded file to the specified filename in the upload folder.

       Args:
           file (FileStorage): Uploaded file object.
           filename (str): Filename to save the file as.
    """
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


def find_files(files, uid):
    """
        Find files that contain the given UID in the given list.

        Args:
            files (List[str]): List of filenames to search.
            uid (str): Unique identifier to match.

        Returns:
            List[str]: List of filenames that contain the UID.
    """
    # the list comprehension iterates over files and adds a file if it contains the uid in its name
    matching_files = [file for file in files if uid in file]
    return matching_files


@app.route('/upload', methods=['POST'])
def upload():
    """
        Handle the upload endpoint.

        This endpoint receives a POST request with an attached file, generates a UID for the uploaded file,
        saves the file in the 'uploads' folder with a new filename containing the original filename, timestamp,
        and UID, and returns a JSON object with the UID of the upload.

        Returns:
            Response: JSON response with the UID of the upload.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file attached'}), 400

    file = request.files['file']
    uid = str(uuid.uuid4())     # create a unique identifier
    filename = generate_filename(uid, file.filename)
    save_file(file, filename)

    return jsonify({'uid': uid})


@app.route('/status/<uid>', methods=['GET'])
def status(uid):
    """
        Handle the status endpoint.

        This endpoint receives a GET request with a UID as a URL parameter. It checks the 'uploads' folder for
        files matching the given UID. If no matching file is found, it returns a JSON object with a 'not found'
        status. If a matching file is found, it checks the 'outputs' folder for a corresponding output file. If
        an output file exists, it retrieves the explanation from the file and sets the status to 'done'. If no
        output file is found, the status is set to 'pending'. The endpoint returns a JSON object with the status,
        original filename, timestamp, and explanation (if available).

        Args:
            uid (str): Unique identifier for the upload.

        Returns:
            Response: JSON response with the status, original filename, timestamp, and explanation (if available).
    """
    upload_files = os.listdir(app.config['UPLOAD_FOLDER'])
    matching_files = find_files(upload_files, uid)

    if not matching_files:
        return jsonify({'status': 'not found'}), 404

    filename = matching_files[0]
    timestamp = filename.split('_')[-2]     # retrieve the timestamp from the filename

    output_folder = OUTPUT_FOLDER
    output_files = os.listdir(output_folder)
    matching_output_files = find_files(output_files, uid)

    if matching_output_files:
        output_filename = matching_output_files[0]
        with open(os.path.join(output_folder, output_filename)) as f:
            explanation = json.load(f)
        curr_status = 'done'
    else:
        explanation = None
        curr_status = 'pending'

    return jsonify({
        'status': curr_status,
        'filename': '_'.join(filename.split('_')[:-2]),     # retrieve the original filename
        'timestamp': timestamp,
        'explanation': explanation
    })


if __name__ == '__main__':
    port = DEFAULT_PORT if os.environ.get('PORT') is None else int(os.environ.get('PORT'))
    app.run(port=port)
