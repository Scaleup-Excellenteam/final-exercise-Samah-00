import requests
from datetime import datetime
from dataclasses import dataclass
import time

API_BASE_URL = "http://localhost:8080"
FILE_TO_PROCESS = '..\\End_of_course_exercise.pptx'
messages = {
    "uid_message": "Uploaded file with UID:",
    "error_retrieve_data": "Failed to retrieve status:",
    "upload_exception": "Upload failed:",
    "uid_exception": "UID not found",
    "status_exception": "Failed to retrieve status:",
    "file_exception": "file_path argument is required."
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
        upload(file_path: str) -> str: Uploads a file to the web app.
        :param: file_path: The path of the file to upload.
        :return: the UID (unique identifier) of the uploaded file, if the upload was successful.
        :raises: an exception if the upload fails.
        """
        if file_path is None:
            # Handle the case where file_path is not provided
            raise ValueError(messages['file_exception'])

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


def run_system_test(client, file_path=None):
    uid = client.upload(file_path)
    print(f"{messages['uid_message']} {uid}")

    while True:
        try:
            status = client.status(uid)
            print(f"Status: {status.status}")
            print(f"Filename: {status.filename}")
            print(f"Timestamp: {status.timestamp}")
            print(f"Explanation: {status.explanation}")
        except Exception as e:
            print(f"{messages['error_retrieve_data']} {e}")
        time.sleep(20)  # Sleep for 20 seconds between iterations


if __name__ == '__main__':
    client = SystemClient(API_BASE_URL)
    run_system_test(client, FILE_TO_PROCESS)
