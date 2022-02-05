from requests import Session, Response
from todoapp.tests.utils.utils import logger
from json import JSONDecodeError


class BaseRequest:

    def __init__(self, session):
        self.session: Session = session
        self.host = None
        self.response: Response = Response()

    def add_host(self, host):
        self.host = host

    @property
    def response_json(self):
        return self.response.json()

    def get(self, resource, protocol='http'):
        url = f"{protocol}://{self.host}{resource}"
        logger.info("Request URL: %s" % url)
        self.response = self.session.get(url)
        self.log_response()
        return self.response

    def post(self, resource, data, protocol='http'):
        url = f"{protocol}://{self.host}{resource}"
        self.response = self.session.post(url, json=data)
        self.log_response()
        return self.response

    def put(self, resource, data=None, protocol='http'):
        url = f"{protocol}://{self.host}{resource}"
        if data:
            self.response = self.session.put(url, json=data)
        else:
            self.response = self.session.put(url)
        self.log_response()
        return self.response

    def delete(self, resource, protocol='http'):
        url = f"{protocol}://{self.host}{resource}"
        logger.info(f"URL: {url}")
        self.response = self.session.delete(url)
        self.log_response()
        return self.response

    def log_response(self):
        logger.info("Response status code: %s" % self.response.status_code)
        try:
            logger.info("Response JSON: %s" % self.response_json)
        except JSONDecodeError:
            logger.info("Response: %s" % self.response.text)
