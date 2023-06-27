import logging
import requests
from datetime import datetime
from dataclasses import dataclass

from utilities import request_utils
from client_utils import PROCESS_DONE, TIME_FORMAT, CLIENT_MESSAGES


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
        return self.status == PROCESS_DONE


def is_valid_filepath(file_path):
    return not (file_path is None or not file_path.endswith(".pptx"))


class SystemClient:
    """
    This class provides a client interface for interacting with the web app system.
    Constructor:
        __init__(base_url: str): Initializes a new instance of the SystemClient class.
        base_url (str): The base URL of the web app.
    Methods:
        upload(file_path: str, email: str = None) -> str: Uploads a file to the web app with an optional email.
        status(uid: str, email: str = None, filename: str = None) -> Status: Retrieves the status of a file from the web app
            based on the UID, email, and/or filename.
    """

    def __init__(self, base_url):
        self.base_url = base_url

    def upload(self, file_path=None, email=None):
        """
        upload(file_path: str, email: str = None) -> str: Checks if the file is valid and uploads a file to the web app with an optional email.
        :param: file_path: The path of the file to upload.
        :param: email: The email address to attach to the uploaded file.
        :return: the UID (unique identifier) of the uploaded file, if the upload was successful.
        """
        if not is_valid_filepath(file_path):
            # Handle the case where file_path is not provided or is not supported
            logging.warning(CLIENT_MESSAGES['file_exception'])
            return None

        upload_url = f"{self.base_url}/upload"
        files = {'file': open(file_path, 'rb')}
        data = {'email': email} if email else None
        response = requests.post(upload_url, files=files, data=data)
        if response.status_code != request_utils.RETURN_VALUES['ok']:
            raise Exception(f"{CLIENT_MESSAGES['upload_exception']} {response.json()['error']}")
        return response.json()['uid']

    def status(self, uid, email=None, filename=None):
        """
        status(uid: str, email: str = None, filename: str = None) -> Status: Retrieves the status of a file from the web app
            based on the UID, email, and/or filename.
        :param: uid: The UID (unique identifier) of the file to check the status of.
        :param: email: The email address associated with the file (optional).
        :param: filename: The original filename of the file (optional).
        :return: a Status object representing the status of the file.
        :raises: an exception if the UID is not found or if there is an error retrieving the status.
        """
        status_url = f"{self.base_url}/status/{uid}"
        params = {'filename': filename, 'email': email}
        response = requests.get(status_url, params=params)
        if response.status_code == request_utils.RETURN_VALUES['page-not-found']:
            raise Exception(CLIENT_MESSAGES['uid_exception'])
        elif response.status_code != request_utils.RETURN_VALUES['ok']:
            raise Exception(f"{CLIENT_MESSAGES['status_exception']} {response.json()}")
        data = response.json()
        timestamp = datetime.strptime(data['timestamp'], TIME_FORMAT)
        return Status(data['status'], data['filename'], timestamp, data['explanation'])
