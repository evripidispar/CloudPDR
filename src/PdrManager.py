from Ibf import Ibf
from multiprocessing.managers import BaseManager


class PdrManager(BaseManager):
    pass
PdrManager.register('Ibf', Ibf)        