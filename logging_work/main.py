import logging

logging.basicConfig(level=logging.DEBUG, filename="mylog.log", format="%(asctime)s %(message)s",
                    datefmt="%m/%d/%Y %I:%M:%S")
logging.warning('is when this event was logged.')
