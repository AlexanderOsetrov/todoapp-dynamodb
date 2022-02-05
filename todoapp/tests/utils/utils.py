import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logging.getLogger("selenium").setLevel("WARNING")
logging.getLogger("urllib3").setLevel("WARNING")
