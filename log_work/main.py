import package1
import app_logger

logger = app_logger.get_logger(__name__)

def main():
    logger.info("Programm is starting...")
    package1.process(msg="message")
    logger.warning("This must appears as in terminal as in the file")
    logger.info("Programm finish...")

if __name__ == '__main__':
    main()