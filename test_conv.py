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
        sv2v.module_data_base().flash()
        module_dict = sv2v.convert2sv(["norm_test.sv",], True)
        self.assertTrue(filecmp.cmp('norm_test_conv.v', 'norm_test_conv_expect.v'))
        self.assertEqual(sorted(module_dict['TOP'].input, key = lambda x:x),
                        ['ADDR', 'CLK', 'READ', 'RST', 'WRITE', 'WRITE_DATA'])
        self.assertEqual(sorted(module_dict['TOP'].output, key = lambda x:x),
                        ['READ_DATA'])
        self.assertEqual(sorted(module_dict['SUB2'].input, key = lambda x:x),
                        ['CLK', 'IN', 'RST'])
        self.assertEqual(sorted(module_dict['SUB2'].output, key = lambda x:x),
                        ['OUT'])

    def test_submodule(self):
        sv2v.module_data_base().flash()
        module_dict = sv2v.convert2sv(["submodule.sv",], True)
        self.assertTrue(filecmp.cmp('submodule_conv.v', 'submodule_conv_expect.v'))

    def test_submodule2(self):
        sv2v.module_data_base().flash()
        module_dict = sv2v.convert2sv(["submodule2.sv",], True)
        self.assertTrue(filecmp.cmp('submodule2_conv.v', 'submodule2_conv_expect.v'))

    def tearDown(self):
        for (root, dirs, files) in os.walk(u'.'):
            for file in files:
                if '_comdel.v' in file:
                    os.remove(u'./' + file)
                elif '_eexpand.v' in file:
                    os.remove(u'./' + file)
                elif '_split.v' in file:
                    os.remove(u'./' + file)
##                elif '_conv.v' in file:
##                    os.remove(u'./' + file)

if __name__ == '__main__':
    unittest.main()
