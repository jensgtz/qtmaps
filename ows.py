# -*- coding: UTF-8 -*-

'''
@created: 11.11.2017
@author : Jens Götze
@email  : jg_git@gmx.net
@license: BSD
'''

from owslib.wms import WebMapService


# test

def test1():
    wms = WebMapService('http://wms.jpl.nasa.gov/wms.cgi', version='1.1.1')
    print(wms.identification.type)
    print(wms.identification.title)


def test():
    test1()

if __name__ == "__main__":
    test()