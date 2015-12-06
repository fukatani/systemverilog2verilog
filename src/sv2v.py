#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      rf
#
# Created:     14/11/2015
# Copyright:   (c) rf 2015
# Licence:     Apache Licence 2.0
#-------------------------------------------------------------------------------

from optparse import OptionParser
import os
import copy
import re
from systemverilog2verilog.src import util
from collections import OrderedDict

debug = True

def convert2sv(filelist=None, is_testing=False):
    optparser = OptionParser()
    (options, args) = optparser.parse_args()
    #TODO interface, struct, union

    if args and not is_testing:
        filelist = args
    elif not filelist:
        raise Exception("Verilog file is not assigned.")

    for file_name in filelist:
        if not os.path.exists(file_name): raise IOError("file not found: " + file_name)

    for file_name in filelist:
        name_without_extension = re.sub("\.[^.]*$", "", file_name)
        comdel_file = name_without_extension + '_comdel.v'
        delete_comments(file_name, comdel_file)

        make_module_info(comdel_file)

        enum_file_name = name_without_extension + '_eexpand.v'
        expand_enum(comdel_file, enum_file_name)
        split_file_name = name_without_extension + '_split.v'
        split_logic_decrarement(enum_file_name, split_file_name)
        sj = skip_judge()
        read_file = open(split_file_name, 'r')
        write_file = open(name_without_extension + '_conv.v', 'w')

        try:
            for line_num, line in enumerate(read_file):
                if line.split() and line.split()[0] == 'module':
                    module_name = get_module_name_from_line(line)
                    while ';' not in line:
                        line = convert_logic_in_fl(line)
                        write_file.write(line)
                        line = next(read_file) #skip module declarement
                    line = convert_logic_in_fl(line)
                    write_file.write(line)
                    line = next(read_file)

                    module_lines = []
                    while not line.split() or line.split()[0] != 'endmodule':
                        module_lines.append(line)
                        line = next(read_file)
                    while module_lines:
                        skip_start_line_num = line_num
                        while sj.judge_line(module_lines[0]):
                            module_lines = module_lines[1:]
                            line_num += 1
                        module_lines[0] = convert_for_logic(module_lines[0], module_lines, module_name)
                        write_file.write(replace_in_line(module_lines[0]))
                        module_lines = module_lines[1:]
                write_file.write(line)

        except (StopIteration, Endmodule_exception):
            print('Error!! Irregular description around line ' + str(skip_start_line_num))

        read_file.close()
        write_file.close()

    if is_testing:
        return module_data_base().module_dict

class Endmodule_exception(Exception): pass

def convert_for_logic(line, module_lines, module_name):
    logic_convert_dict = {'logic': 'reg', 'bit': 'reg', 'byte': 'reg [7:0]'}
    wire_convert_dict = {'logic': 'wire', 'bit': 'wire', 'byte': 'wire [7:0]'}
    wire_flag = False

    words = line.replace(';', '').split()
    if not words: return line
    if words[0] == 'input' or words[0] == 'output' or words[0] == 'inout':
        words = words[1:]
    if words[0] in logic_convert_dict.keys():
        if words[1][0] == '[':
            var_name = words[2]
        else:
            var_name = words[1]

        for i, templine in enumerate(module_lines):
            ml_words = set(templine.replace('(', ' ').split())
            if 'assign' in templine and var_name in templine[0:templine.find('=')]:
                wire_flag = True
                break
            elif var_name in module_data_base().module_dict[module_name].input:
                wire_flag = True
                break
            elif var_name in module_data_base().module_dict[module_name].inout:
                wire_flag = True
                break
            elif ml_words.intersection(module_data_base().module_dict.keys()):
                #TODO other module
                assigned_module = tuple(ml_words.intersection(module_data_base().module_dict.keys()))[0]
                dec_lines = []
                j = 0
                while ';' not in module_lines[i+j]:
                    dec_lines.append(module_lines[i+j])
                dec_lines.append(module_lines[i+j])#add last line
                dec_line = ' '.join(dec_lines).replace('\n', ' ')
                if '*' in dec_line: #assigned by wild card or not
                    wire_flag = (var_name in module_data_base().module_dict[assigned_module].input or
                                 var_name in module_data_base().module_dict[assigned_module].inout)
                    print('wild card')
                elif var_name in dec_line:
                    if '.' in dec_line: #assigned by port name
                        print('name assigned')
                    else: #assigned by order name
                        print('order')
                        assigned_vars = util.clip_in_blacket(dec_line).replace(" ","").split(',')
                        for i, assigned_var in enumerate(assigned_vars):
                            if assigned_var == var_name:
                                break
                        else:
                            raise Exception("Unexpected exception.")
                        print(i)

                    #end

        if wire_flag:
            line = line.replace(words[0], wire_convert_dict[words[0]])
        else:
            line = line.replace(words[0], logic_convert_dict[words[0]])
    return line

class skip_judge(object):
    """ [CLASSES]
        For skip not verilog block.ec. property ~ endproperty, cloking ~ endclocking.
    """
    def __init__(self):
        self.default_flag = False
        self.assert_flag = False
        self.clocking_flag = False
        self.sequence_flag = False
        self.property_flag = False
##        self.end_word_dict = {'assert': ';',
##                              'default': ';',
##                              'clocking': 'endclocking',
##                              'sequence': 'endsequence',
##                              'property': 'endproperty'}

    def judge_line(self, line):
        if any([self.default_flag, self.assert_flag, self.clocking_flag,
                self.sequence_flag, self.property_flag]):
                    if 'endmodule' in line:
                        raise Endmodule_exception
        if self.assert_flag:
            self.assert_flag = ';' not in line
            return True
        elif self.default_flag:
            self.default_flag = ';' not in line
            return True
        elif self.clocking_flag:
            self.clocking_flag = 'endclocking' not in line
            return True
        elif self.sequence_flag:
            self.sequence_flag = 'endsequence' not in line
            return True
        elif self.property_flag:
            self.property_flag = 'endproperty' not in line
            return True
        else:
            if 'assert' in line:
                self.assert_flag = ';' not in line
                return True
            elif 'default' in line:
                self.default_flag = ';' not in line
                return True
            elif 'clocking' in line:
                self.clocking_flag = 'endclocking' not in line
                return True
            elif 'sequence' in line:
                self.sequence_flag = 'endsequence' not in line
                return True
            elif 'property' in line:
                self.property_flag = 'endproperty' not in line
                return True

def replace_in_line(line):
    def delete_word(word):
        targets = ('unique', 'priority')
        if word in targets:
            return ''
        else:
            return word

    def replace_word(word):
        replace_dict = {'always_comb': 'always @*', 'always_latch': 'always @*',
                        'always_ff': 'always','int': 'integer', 'shortint': 'reg signed [15:0]',
                        'longint': 'reg signed [63:0]', "'0": "'d0", "'1": "'hffff"}
        if word in replace_dict.keys():
            return replace_dict[word]
        else:
            return word

    words = line.split(' ')
    for i, word in enumerate(words):
        words[i] = delete_word(word)
        words[i] = replace_word(word)
    converted_line = ' '.join(words)
    return converted_line

def split_logic_decrarement(read_file_name, write_file_name):
    """ [Functions]
       input A;
       output B;
       logic A,B;
       ->
       input A;
       output B;
       logic A;
       logic B;
    """

    write_file = open(write_file_name, 'w')
    with open(read_file_name, 'r') as f:
        in_module = False
        dec_line = False
        for line in f:
            words = line.replace(',', '').split()
            if not words:
                write_file.write(line)
                continue
            if 'module' in line.split():
                new_module = module_info()
                dec_line = True
            if dec_line:
                write_file.write(line)
                if ';' in line:
                    dec_line = False
                    in_module = True
            elif set(['logic', 'bit', 'byte']).intersection(words) and ',' in line:
                decrarements, packed_bit, unpacked_bit, var_names = separate_in_bracket(line)
                for var in var_names:
                    write_file.write(' '.join(decrarements + unpacked_bit + (var,) + packed_bit) + ';\n')
            else:
                write_file.write(line)
    write_file.close()

def separate_in_bracket(line):
    """ [Functions]
         input logic [2: 1] A,B [1:0];
         ->
         declarements = ['input', 'logic']
         packed bit = '[2: 1]'
         var_names = ['A', 'B']
         unpacked_bit = '[1:0]'
    """
    decrarements = []
    packed_bit = []
    unpacked_bit = []
    var_names = []

    line = line.replace(',', ' ')
    line = line.replace(';', '')
    line = line.replace('[', ' [')
    line = line.replace(']', '] ')

    words = line.split()

    in_bracket_flag = False
    for word in words:
        if word in ('logic', 'bit', 'byte', 'input', 'output', 'inout'):
            decrarements.append(word)
        elif word[0] == '[':
            in_bracket_flag = (word[-1] != ']')
            if var_names:
                packed_bit.append(word)
            else:
                unpacked_bit.append(word)
        elif word[-1] == ']':
            in_bracket_flag = False
            if var_names:
                packed_bit.append(word)
            else:
                unpacked_bit.append(word)
        elif in_bracket_flag:
            if var_names:
                packed_bit.append(word)
            else:
                unpacked_bit.append(word)
        else:
            var_names.append(word)
    return (tuple(decrarements), tuple(packed_bit),
            tuple(unpacked_bit), tuple(var_names))

def delete_comments(read_file_name, write_file_name):
    """ [Functions]
       delete char after '//' and from '/*' to '*/'
    """
    write_file = open(write_file_name, 'w')
    with open(read_file_name, 'r') as f:
        block_comment_flag = False
        for line in f:
            if block_comment_flag:
                if line.find('*/'):
                    write_file.write(line[line.find('*/'):-1])
                else:
                    continue
            elif line.find('//') >= 0:
                write_file.write(line[0:line.find('//')])
            elif line.find('/*') >= 0:
                if line.find('*/'):
                    write_file.write(line[0:line.find('/*')] + line[line.find('*/'):-1])
                else:
                    write_file.write(line[0:line.find('/*')])
                    block_comment_flag = True
            else:
                write_file.write(line)
    write_file.close()

def expand_enum(read_file_name, write_file_name):
    def get_enum_values(line):
        line = util.clip_in_blacket(line, '{')
        line = line.replace(' ','')

        enum_dict = OrderedDict()
        i = 0
        for val in line.split(','):
            if '=' in val:
                i = int(val[val.find('=') + 1:])
                enum_dict[val[0:val.find('=')]] = i
            else:
                enum_dict[val] = i
            i += 1
        return enum_dict
    write_file = open(write_file_name, 'w')
    with open(read_file_name, 'r') as f:
        for line in f:
            if 'enum' in line.split():
                for val, num in get_enum_values(line).items():
                    write_file.write(" ".join(('localparam', val, "= 'd", str(num), ';')))
            else:
                write_file.write(line)
    write_file.close()

def make_module_info(read_file_name):
    with open(read_file_name, 'r') as f:
        in_module = False
        dec_line = False
        for line in f:
            if 'module' in line.split():
                new_module = module_info()
                dec_line = True
            if dec_line:
                new_module.dec_lines.append(line)
                if ';' in line:
                    dec_line = False
                    new_module.readfirstline()
                    in_module = True
            elif re.match('endmodule', line):
                in_module = False
                mdb = module_data_base()
                mdb.set_module(new_module.name, new_module)
                if debug:
                    print(new_module.tostr())
            elif in_module:
                new_module.readline(line)

def convert_logic_in_fl(first_line):
    first_line = re.sub('input +logic +', 'input wire ', first_line)
    first_line = re.sub('inout +logic +', 'input wire ', first_line)
    return first_line

class module_data_base(object):
    """ [CLASSES]
        Singleton class for manage terminals for module data base.
    """
    _singleton = None
    def __new__(cls, *argc, **argv):
        if cls._singleton is None:
            cls._singleton = object.__new__(cls)
            cls.module_dict = {}
        return cls._singleton

    def set_module(self, module_name, module_info):
##        if self.module_dict is None:
##            self.module_dict = {}
        assert not module_name in self.module_dict.keys()
        self.module_dict[module_name] = module_info

    def flash(self):
        self.module_dict = {}
        self._singleton = None

class module_info(object):
    def __init__(self):
        self.name = ''
        self.dec_lines = []
        self.input = []
        self.output = []
        self.inout = []
        self.all_ports = []

    def _add_port(self, port_name, port_type):
        if port_type == 'input':
            self.input.append(port_name)
        elif port_type == 'inout':
            self.inout.append(port_name)
        elif port_type == 'output':
            self.output.append(port_name)
        self.all_ports.append(port_name)

    def readfirstline(self):
        """[FUNCTIONS]
        ex.
        module COMPARE(output GT, output LE, output EQ,
                       input [1:0] A, input [1:0] B, input C);
        """
        first_line = " ".join(self.dec_lines)
        first_line = first_line.replace('\n', ' ')
        self.name = get_module_name_from_line(first_line)
        first_line = re.sub("#\(.+?\)", " ", first_line)
        first_line = re.sub("\[.+?\]", " ", first_line)
        in_bracket = util.clip_in_blacket(first_line)
        decs = in_bracket.split(',')
        #words[-1] :exclude type definition
        for dec in decs:
            words = dec.split()
            self._add_port(words[-1], words[0])

    def readline(self, line):
        """[FUNCTIONS]
        ex.
        module COMPARE(GT, LE, EQ, A, B, C);
            output GT, LE, EQ;
            input [1: width_A] A, B;
            input [1: width_B] C;
        """
        #line = line.replace('(', ' ')
        #line = line.replace(')', ' ')
        line = re.sub("\[.+?\]", " ", line)
        line = line.replace(';', ' ;')
        line = line.replace(',', ' ')
        in_input_port = False
        in_output_port = False
        in_inout_port = False
        for word in line.split():
            if word == 'input':
                assert(not(in_input_port) and not(in_output_port) and not(in_inout_port))
                in_input_port = True
            elif word == 'output':
                assert(not(in_input_port) and not(in_output_port) and not(in_inout_port))
                in_output_port = True
            elif word == 'inout':
                assert(not(in_input_port) and not(in_output_port) and not(in_inout_port))
                in_inout_port = True
            elif word == ';':
                in_input_port = False
                in_output_port = False
                in_inout_port = False
            elif in_input_port:
                self._add_port(word, 'input')
            elif in_output_port:
                self._add_port(word, 'output')
            elif in_inout_port:
                self._add_port(word, 'inout')

    def tostr(self):
        return self.name + '\ninput:' + str(self.input) + '\noutput:' + str(self.output) + '\ninout:'+ str(self.inout)

def get_module_name_from_line(line):
    line = re.sub("#\(.+?\)", " ", line) #remove parameter description
    return line.replace('(', ' ').split()[1]

if __name__ == '__main__':
    convert2sv(["../test/submodule.sv",])
    #convert2sv(["../test/norm_test.sv",])
