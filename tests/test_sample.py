import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logger import logger
import pytest


def test_logger_initialization():
    """
    Test to ensure the logger can be initialized without error.
    """
    assert logger is not None
    logger.info("Executing sample test.")

def test_sample_addition():
    """
    A simple test to verify pytest is set up correctly.
    """
    assert 1 + 1 == 2
