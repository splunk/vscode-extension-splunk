import logging
import logging.handlers
import os

def setup(level, name, file_name, use_rotating_handler=True):
    """
    Setup a logger for the REST handler.

    Arguments:
    level -- The logging level to use
    name -- The name of the logger to use
    file_name -- The file name to log to
    use_rotating_handler -- Indicates whether a rotating file handler ought to be used
    """

    logger = logging.getLogger(name)
    logger.propagate = False  # Prevent the log messages from being duplicated in the python.log file
    logger.setLevel(level)
    log_file_path = os.path.join(os.environ['SPLUNK_HOME'], 'var', 'log', 'splunk', file_name)
    if use_rotating_handler:
        file_handler = logging.handlers.RotatingFileHandler(log_file_path, maxBytes=25000000, backupCount=5)
    else:
        file_handler = logging.FileHandler(log_file_path)
    formatter = logging.Formatter('%(created)f %(levelname)s :%(lineno)d %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger
