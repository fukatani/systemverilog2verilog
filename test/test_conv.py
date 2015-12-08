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
from systemverilog2verilog.src.sv2v import *
import filecmp

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        pass

    def test_normal(self):
        module_data_base().flash()
        module_dict, _, _ = convert2sv(["norm_test.sv",], True)
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
        module_data_base().flash()
        convert2sv(["submodule.sv",], True)
        self.assertTrue(filecmp.cmp('submodule_conv.v', 'submodule_conv_expect.v'))

    def test_submodule2(self):
        module_data_base().flash()
        convert2sv(["submodule2.sv",], True)
        self.assertTrue(filecmp.cmp('submodule2_conv.v', 'submodule2_conv_expect.v'))

    def test_submodule3(self):
        module_data_base().flash()
        module_dict, reg_dict, wire_dict = convert2sv(["name_and_order_assign.sv",], True)
        self.assertTrue(filecmp.cmp('name_and_order_assign_conv.v', 'name_and_order_assign_conv_expect.v'))

        self.assertEqual(reg_dict['SUB'], ['reg1'])
        self.assertEqual(reg_dict['SUB2'], ['reg1'])
        self.assertEqual(set(reg_dict['TOP']), set(['reg1', 'reg2', 'reg3']))

        self.assertEqual(wire_dict['SUB'], ['IN'])
        self.assertEqual(wire_dict['SUB2'], ['IN'])
        self.assertEqual(set(wire_dict['TOP']), set(['in1', 'OUT', 'OUTOUT', 'IN', 'IN2']))

    def test_eda(self):
        module_data_base().flash()
        module_data_base().flash()
        convert2sv(["dot_asterisk.sv",], True)
        self.assertTrue(filecmp.cmp('dot_asterisk_eda.v', 'dot_asterisk_eda_expect.v'))

    def tearDown(self):
        for (root, dirs, files) in os.walk(u'.'):
            for file in files:
                if '_comdel.v' in file:
                    os.remove(u'./' + file)
                elif '_eexpand.v' in file:
                    os.remove(u'./' + file)
                elif '_split.v' in file:
                    os.remove(u'./' + file)
                elif '_eda.v' in file:
                    os.remove(u'./' + file)
##                elif '_conv.v' in file:
##                    os.remove(u'./' + file)

if __name__ == '__main__':
    unittest.main()
