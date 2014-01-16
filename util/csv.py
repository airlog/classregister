# coding=utf-8

def parse(csvstr, colSep = ",", rowSep = "\n"):
    """ Wczytuje plik CSV jako lista (wiersze) krotek (kolumny). """
    return [tuple(row.split(colSep)) for row in csvstr.split(rowSep)]

