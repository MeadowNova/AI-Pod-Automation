import os
import logging

def setup_logging():
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'logs')
    log_dir = os.path.abspath(log_dir)
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'app.log')

    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, mode='a'),
                logging.StreamHandler()
            ]
        )
