"""
Base class for triggers.
"""
from abc import ABC, abstractmethod

from .. import logger


class _Trigger(ABC):
    """
    Base trigger class.

    Parameters
    ----------
    verbose : bool
        If True, display a logger.info message when a trigger is sent.
    """

    @abstractmethod
    def __init__(self, verbose: bool = True):
        self._verbose = bool(verbose)

    @abstractmethod
    def signal(self, value: int):
        """
        Send a trigger value.
        """
        if self._verbose:
            logger.info(f'Sending trigger {value}.')
        else:
            logger.debug(f'Sending trigger {value}.')

    @abstractmethod
    def _set_data(self, value: int):
        """
        Set the trigger signal to value.
        """
        logger.debug('Setting data to %d' % value)

    # --------------------------------------------------------------------
    @property
    def verbose(self):
        return self._verbose

    @verbose.setter
    def verbose(self, verbose: bool):
        self._verbose = bool(verbose)