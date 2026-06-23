"""Abstract base service for the service layer pattern."""
import logging

logger = logging.getLogger("finditai")


class BaseService:
    """Base class for all domain services."""

    def __init__(self):
        self.logger = logging.getLogger(f"finditai.{self.__class__.__name__}")
