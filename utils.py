import io
import zlib
import numpy as np
import re

def checkDirs(path):
    pass

def compress_nparr(nparr):
    bytestream = io.BytesIO()
    np.save(bytestream, nparr)
    uncompressed = bytestream.getvalue()
    compressed = zlib.compress(uncompressed)
    return compressed


def uncompress_nparr(bytestring):
    return np.load(io.BytesIO(zlib.decompress(bytestring)))


def empty(arr):
    return len(arr) == 0


def readNetTypes(path='..\\config.txt'):
    return __readProperty('nets', path).split(',')


def getClientsNumber(path='..\\config.txt'):
    return int(__readProperty('nDevices', path))


def getTesterPort(path='..\\config.txt'):
    return int(__readProperty('testerPort', path))


def __readProperty(prop, path='..\\config.txt'):
    with open(path, 'r') as config:
        lines = config.readlines()
        for line in lines:
            line = line.replace(' ', '')
            line = line.split('=')
            if line[0] == prop:
                return line[1]


def validateType(variable, expected):
    '''

    :param variable: variable to be checked
    :param expected: expected type of variable
    :return:
    '''
    if not isinstance(variable, expected):
        message = 'Parameter has wrong type. Expected ' + str(expected) + ' got ' + str(type(variable))
        raise ValueError(message)

def generateLatexTabular(rows, cols, pagePercent=1, savePath=None):
    '''

    :param rows: dict, key - row label, value - array of values for that label
    :param cols: ordered dict, key - order, value - column name
    :param pagePercent: float from 1 to 0 - width of array in %
    :param savePath: string, path to save generated tabular if None then tabular is printed in prompt
    :return:
    '''
    col_num = (len(cols) + 1)
    col_wid = (pagePercent * 20) / col_num
    newline = '\\\\'
    newLineBegin = '\n\t\t'
    newRow = '\n\t\t\\hline'
    firstRow = newLineBegin + ''
    for c in cols.keys():
        firstRow += ' & ' + cols[c].replace('_', '\_')
    firstRow += newline
    bein = '\\begin{tabularx}{\\textwidth}{\n\t| >{\centering\\arraybackslash}X'
    col = '\n\t| >{\centering\\arraybackslash}x'
    for i in range(len(cols)):
        bein += col
    bein += ' |}'
    bein += newRow
    bein += firstRow + newRow

    for key in rows.keys():
        line = newLineBegin + str(key) + ' & '
        for val in rows[key]:
            line += str(val) + ' & '
        line = line[:-3]
        line += newline
        line += newRow
        bein += line
    end = '\n\\end{tabularx}'
    bein += end
    if savePath is None:
        print(bein)
    else:
        with open(savePath, mode='w', newline='\n') as file:
            file.write(bein)
            file.close()