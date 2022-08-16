from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
from os.path import abspath, dirname


# Program argument defaults
ARG_DEFAULTS = {
    'server_addr': '10.0.5.69',
    'server_port': 9000,
    'client_port': 6688,
    'client_id': 'b2f4c0d4'
}

# Base project directory
PROJECT_ROOT = dirname(abspath(__file__))

# ANSI terminal colors (for logging)
ANSI_BLUE = '\x1b[36;20m'
ANSI_GREEN = '\x1b[32;20m'
ANSI_GREY = '\x1b[38;20m'
ANSI_RED = '\x1b[31;20m'
ANSI_RED_BOLD = '\x1b[31;1m'
ANSI_YELLOW = '\x1b[33;20m'
ANSI_RESET = '\x1b[0m'

# Log format
LOG_LVL_SUCCESS = INFO - 5
LOG_FMT_DATE = '%Y-%m-%d %H:%M:%S'
LOG_FMT_STR = '[%(levelname)s] %(funcName)s: %(message)s (%(filename)s:%(lineno)d)'
LOG_FMT_STR_WITHDATE = '%(asctime)s {0}'.format(LOG_FMT_STR)
LOG_FMT_COLOR = {
    DEBUG: ANSI_GREY + LOG_FMT_STR + ANSI_RESET,
    LOG_LVL_SUCCESS: ANSI_GREEN + LOG_FMT_STR + ANSI_RESET,
    INFO: ANSI_BLUE + LOG_FMT_STR + ANSI_RESET,
    WARNING: ANSI_YELLOW + LOG_FMT_STR + ANSI_RESET,
    ERROR: ANSI_RED + LOG_FMT_STR + ANSI_RESET,
    CRITICAL: ANSI_RED_BOLD + LOG_FMT_STR + ANSI_RESET
}
