import logging
import os
import re

def create_logger(name, filename, loglevel="DEBUG"):
    logger = logging.getLogger(name)
    logger.setLevel(loglevel)
    
    handler = logging.FileHandler(filename)
    handler.setLevel(loglevel)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)    
    return logger  

def create_logger_main(logs_path, loglevel="DEBUG"):
    manager_log = os.path.join(logs_path, 'manager.log')
    return create_logger('manager', manager_log, loglevel)

    
def create_logger_report(logs_path, report_file, loglevel="DEBUG"):
    report_log = os.path.join(logs_path, re.sub('\.report$', '.log', report_file))
    return create_logger(report_file, report_log, loglevel)
