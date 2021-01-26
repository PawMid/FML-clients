import sys


def progressBar(totalData, dataCount, newline=False):
    filled = (dataCount) / totalData
    filled = round(filled * 100, 1)
    filNFrac = round(filled)
    bar = ''
    sys.stdout.write('\b' * (len('Progress: |') * 100 + len('| ' + str(filled))))
    bar = bar + '#' * filNFrac + '-' * (100 - filNFrac) + '| ' + str(filled) + '% ' + str(dataCount) + '/' + str(totalData)
    sys.stdout.write('Progress: |' + ' ' * 100 + '| ' + str(filled) + '\b' * (100 + len('| ' + str(filled))) + bar)
    sys.stdout.flush()
    if filled == 100:
        print(' Done.', end='')
    if newline:
        print()
