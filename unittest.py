#-------------------------------------------------------------------------------
# test_ra.py
#
# the test for all pyverilog_toolbox function
#
# Copyright (C) 2015, Ryosuke Fukatani
# License: Apache 2.0
#-------------------------------------------------------------------------------


import sys
import os
import unittest
import sv2v
import filecmp

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        pass

    def test_normal(self):
        sv2v.convert2sv(["test.sv",])
        filecmp.cmpfiles('test_conv.v', 'test_conv_expect.v')


if __name__ == '__main__':
    unittest.main()
