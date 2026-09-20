import sys
import logging

import scheduler


def logging_config():
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True
    )

if __name__ == '__main__':
    logging_config()
    logger = logging.getLogger(__name__)
    scheduler.run_ohlcv_scheduler()