import json
import os
import uuid
from datetime import datetime
from flask import Flask, request, jsonify

from server import TIME_FORMAT, DEFAULT_PORT, Status, STATUS_VALUES
from utilities import dir_utils, file_utils
from database.database import session, User, Upload


# create an instance of the Flask class and assigns it to the variable app
app = Flask(__name__)
# set the configuration parameter 'UPLOAD_FOLDER' in app object to the value of UPLOAD_FOLDER
app.config['UPLOAD_FOLDER'] = dir_utils.UPLOAD_FOLDER


def generate_filename(uid, original_filename):
    """
        Generate a new filename by combining the original filename, timestamp, and UID.

        Args:
            uid (str): Unique identifier for the file.
            original_filename (str): Original filename of the uploaded file.

        Returns:
            str: New filename with the format 'uid.pptx'.
    """
    return uid + '.' + original_filename.split('.')[file_utils.FILE_FORMAT_INDEX]


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


def create_user(email):
    """
    Create a new User object if it doesn't exist already based on the provided email.

    Args:
        email (str): The email address of the user.

    Returns:
        User: The created or existing User object.
    """
    user = session.query(User).filter_by(email=email).first()
    if not user:
        user = User(email=email)
        session.add(user)
    return user


def create_upload(file, uid, filename, user):
    """
    Create a new Upload object and associate it with the provided user.

    Args:
        file (FileStorage): Uploaded file object.
        uid (str): Unique identifier for the new_upload.
        filename (str): Original filename of the uploaded file.
        user (User): The User object to associate with the new_upload.

    Returns:
        Upload: The created Upload object.
    """
    new_upload = Upload(uid=uid, filename=filename, upload_time=datetime.now(), user=user)
    session.add(new_upload)
    session.commit()
    return new_upload


def calculate_finish_time(start_time):
    """
    Calculate the finish time based on the current time and the start time.

    Args:
        start_time (datetime): The start time of the upload.

    Returns:
        str: The finish time formatted as a string.
    """
    current_time = datetime.now()
    finish_time = start_time + (current_time - start_time)
    return finish_time.strftime(TIME_FORMAT)


@app.route('/new_upload', methods=['POST'])
def upload():
    """
    Handle the new_upload endpoint.

    This endpoint receives a POST request with an attached file and optional email parameter.
    It generates a unique identifier (UID) for the uploaded file, saves the file in the 'uploads' folder
    using the UID as the filename, and creates a new Upload object associated with an optional User object
    based on the provided email.
    The Upload object is then committed to the database.
    The endpoint returns a JSON response with the UID of the new_upload.

    Request Parameters:
        - file: The attached file to be uploaded.

    Optional Parameters:
        - email: The email address of the user. If provided, the uploaded file will be associated with this user.

    Returns:
        Response: JSON response with the UID of the new_upload.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file attached'}), 400

    file = request.files['file']
    uid = str(uuid.uuid4())     # create a unique identifier
    filename = generate_filename(uid, file.filename)
    save_file(file, filename)

    user = None
    if 'email' in request.form:
        email = request.form['email']
        user = create_user(email)

    new_upload = create_upload(file, uid, file.filename, user)

    return jsonify({'uid': uid})


# @app.route('/status/<uid>', methods=['GET'])
# def status(uid):
#     """
#         Handle the status endpoint.
#
#         This endpoint receives a GET request with a UID as a URL parameter. It checks the 'uploads' folder for
#         files matching the given UID. If no matching file is found, it returns a JSON object with a 'not found'
#         status. If a matching file is found, it checks the 'outputs' folder for a corresponding output file. If
#         an output file exists, it retrieves the explanation from the file and sets the status to 'done'. If no
#         output file is found, the status is set to 'pending'. The endpoint returns a JSON object with the status,
#         original filename, timestamp, and explanation (if available).
#
#         Args:
#             uid (str): Unique identifier for the upload.
#
#         Returns:
#             Response: JSON response with the status, original filename, timestamp, and explanation (if available).
#     """
#     upload_files = dir_utils.get_files_list(app.config['UPLOAD_FOLDER'])
#     matching_files = find_files(upload_files, uid)
#
#     if not matching_files:
#         return jsonify({'status': 'not found'}), 404
#
#     filename = matching_files[0]
#     timestamp = filename.split('_')[-2]     # retrieve the timestamp from the filename
#
#     output_files = dir_utils.get_files_list(dir_utils.OUTPUT_FOLDER)
#     matching_output_files = find_files(output_files, uid)
#
#     if matching_output_files:
#         output_filename = matching_output_files[0]
#         with open(os.path.join(dir_utils.OUTPUT_FOLDER, output_filename)) as f:
#             explanation = json.load(f)
#         curr_status = 'done'
#     else:
#         explanation = None
#         curr_status = 'pending'
#
#     return jsonify({
#         'status': curr_status,
#         'filename': '_'.join(filename.split('_')[:-2]),     # retrieve the original filename
#         'timestamp': timestamp,
#         'explanation': explanation
#     })


@app.route('/curr_status/<uid>', methods=['GET'])
def status(uid):
    """
        Handle the curr_status endpoint.

        This endpoint receives a GET request with a UID as a URL parameter. It fetches the corresponding upload from
        the database based on the provided UID. If no matching upload is found, it returns a JSON object with a
        'not found' curr_status. If a matching upload is found, it checks if there is an associated output file in the
        database. If an output file exists, it retrieves the explanation from the file and sets the curr_status to 'done'.
        If no output file is found, the curr_status is set to 'pending'. The endpoint returns a JSON object with the curr_status,
        original filename, timestamp, explanation (if available), and finish time (if available).

        Args:
            uid (str): Unique identifier for the upload.

        Returns:
            Response: JSON response with the curr_status, original filename, timestamp, explanation (if available),
            and finish time (if available).
    """
    # Fetch the upload from the database based on the provided UID
    upload = session.query(Upload).filter_by(uid=uid).first()

    if not upload:
        return jsonify({'status': STATUS_VALUES['not_found']}), 404

    # Retrieve the relevant data from the upload object
    filename = upload.filename
    timestamp = upload.upload_time.strftime(TIME_FORMAT)

    # Check if an output file exists for the upload
    output_files = dir_utils.get_files_list(dir_utils.OUTPUT_FOLDER)
    matching_output_files = find_files(output_files, uid)
    if matching_output_files:
        output_filename = matching_output_files[0]
        with open(os.path.join(dir_utils.OUTPUT_FOLDER, output_filename)) as f:
            explanation = json.load(f)
        curr_status = STATUS_VALUES['done']
        finish_time = calculate_finish_time(timestamp)
    else:
        explanation = None
        curr_status = STATUS_VALUES['pending']
        finish_time = None

    # Create a named tuple for the curr_status
    curr_status = Status(status=curr_status, filename=filename, timestamp=timestamp,
                         explanation=explanation, finish_time=finish_time)

    return jsonify(curr_status._asdict())


if __name__ == '__main__':
    port = DEFAULT_PORT if os.environ.get('PORT') is None else int(os.environ.get('PORT'))
    app.run(port=port)
