"""
Airflow logging configuration patch.

This module configures logging for Airflow to ensure proper log output
in containerized and non-containerized environments.
"""

import logging


def configure_logging():
    """Configure logging for Airflow tasks and DAGs."""
    # Set up root logger to be more verbose during DAG parsing and task execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Suppress overly verbose third-party loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)


# Apply logging configuration on module import
configure_logging()
