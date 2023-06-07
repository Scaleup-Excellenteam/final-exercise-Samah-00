import logging

import requests
from datetime import datetime
from dataclasses import dataclass


messages = {
    "error_retrieve_data": "Failed to retrieve status:",
    "upload_exception": "Upload failed:",
    "uid_exception": "UID not found",
    "status_exception": "Failed to retrieve status:",
    "file_exception": "file_path argument is required and file should be of type .pptx."
}


@dataclass
class Status:
    """
    This class represents the status of a file in the system.
    It is defined as a data class using the @dataclass decorator.
    Properties:
        status (str): The status of the file.
        filename (str): The original filename of the uploaded file.
        timestamp (datetime): A datetime object representing the upload timestamp.
        explanation (str): The output returned from the Web API.
    Methods:
        is_done() -> bool: Returns True if the status is 'done', indicating that the file processing is completed.
        Returns False otherwise.
    """
    status: str
    filename: str
    timestamp: datetime
    explanation: str

    def is_done(self):
        return self.status == 'done'


def is_valid_filepath(file_path):
    return file_path is None or not file_path.endswith(".pptx")


class SystemClient:
    """
    This class provides a client interface for interacting with the web app system.
    Constructor:
        __init__(base_url: str): Initializes a new instance of the SystemClient class.
        base_url (str): The base URL of the web app.
    Methods:
        upload(file_path: str) -> str: Uploads a file to the web app.
        status(uid: str) -> Status: Retrieves the status of a file from the web app.
    """

    def __init__(self, base_url):
        self.base_url = base_url

    def upload(self, file_path=None):
        """
        upload(file_path: str) -> str: Checks if the file is valid and uploads a file to the web app.
        :param: file_path: The path of the file to upload.
        :return: the UID (unique identifier) of the uploaded file, if the upload was successful.
        """
        if not is_valid_filepath(file_path):
            # Handle the case where file_path is not provided or is not supported
            logging.warning(messages['file_exception'])
            return None

        upload_url = f"{self.base_url}/upload"
        with open(file_path, 'rb') as file:
            response = requests.post(upload_url, files={'file': file})
        if response.status_code != 200:
            raise Exception(f"{messages['upload_exception']} {response.json()['error']}")
        return response.json()['uid']

    def status(self, uid):
        """
        status(uid: str) -> Status: Retrieves the status of a file from the web app.
        :param: uid: The UID (unique identifier) of the file to check the status of.
        :return: a Status object representing the status of the file.
        :raises: an exception if the UID is not found or if there is an error retrieving the status.
        """
        status_url = f"{self.base_url}/status/{uid}"
        response = requests.get(status_url)
        if response.status_code == 404:
            raise Exception(messages['uid_exception'])
        elif response.status_code != 200:
            raise Exception(f"{messages['status_exception']} {response.json()}")
        data = response.json()
        timestamp = datetime.strptime(data['timestamp'], '%Y%m%d%H%M%S')
        return Status(data['status'], data['filename'], timestamp, data['explanation'])
