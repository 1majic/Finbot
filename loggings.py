import logging
from datetime import datetime

date = datetime.now().strftime('%d.%m.%y')
logging.basicConfig(
    level=logging.INFO,
    filename=f'{date}.log',
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)


def lets_logging(message_type, message):
    if message_type == "info":
        logging.info(message)
    elif message_type == "warning":
        logging.warning(message)