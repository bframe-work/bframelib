import os

PATH = os.path.dirname(__file__)
__version__ = "0.1.1"

# PATH must be exported first since subsequent modules reference it
from .client import Client, Source, DEFAULT_SOURCES
from .interpreter import Interpreter




