# coding=utf-8

"""
Moduł zawiera skrypty Python'a pochodzące od osób trzecich a wykorzystywane w naszym projekcie.
Wywołanie tego skryptu dodaje je do PYTHONPATH umożliwiając ich użycie.
"""

from sys import path
from os.path import abspath

path.append(abspath("externals/torndb/"))

