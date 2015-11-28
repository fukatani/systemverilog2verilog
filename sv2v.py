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

def convert2sv(filelist=None):
    optparser = OptionParser()
    (options, args) = optparser.parse_args()
    #TODO interface, struct, union

    if args:
        filelist = args
    elif not filelist:
        raise Exception("Verilog file is not assigned.")

    for file_name in filelist:
        if not os.path.exists(file_name): raise IOError("file not found: " + file_name)

    for file_name in filelist:
        name_without_extension = re.sub("\.[^.]*$", "", file_name)
        comdel_file = name_without_extension + '_comdel.v'
        delete_comments(file_name, comdel_file)
        enum_file_name = name_without_extension + '_eexpand.v'
        expand_enum(comdel_file, enum_file_name)
        split_file_name = name_without_extension + '_split.v'
        split_logic_decrarement(enum_file_name, split_file_name)
        sj = skip_judge()
        read_file = open(split_file_name, 'r')
        write_file = open(name_without_extension + '_conv.v', 'w')

        try:
            for line_num, line in enumerate(read_file):
                write_file.write(line)
                if line.split() and line.split()[0] == 'module':
                    line = next(read_file) #skip module declarement
                    module_lines = []
                    while not line.split() or line.split()[0] != 'endmodule':
                        module_lines.append(line)
                        line = next(read_file)
                    while module_lines:
                        skip_start_line_num = line_num
                        while sj.judge_line(module_lines[0]):
                            module_lines = module_lines[1:]
                            line_num += 1
                        module_lines[0] = convert_for_logic(module_lines[0], module_lines)
                        write_file.write(convert_line(module_lines[0]))
                        module_lines = module_lines[1:]
                    write_file.write(line) #write endmodule

        except (StopIteration, Endmodule_exception):
            print('Error!! Irregular description around line ' + str(skip_start_line_num))

class Endmodule_exception(Exception): pass

def convert_for_logic(line, module_lines):
    logic_convert_dict = {'logic': 'reg', 'bit': 'reg', 'byte': 'reg [7:0]'}
    wire_convert_dict = {'logic': 'wire', 'bit': 'wire', 'byte': 'wire [7:0]'}
    wire_flag = False

    words = line.replace(';', '').split()
    if not words: return line
    if words[0] == 'input' or words[0] == 'output':
        words = words[1:]
    if words[0] in logic_convert_dict.keys():
        if words[1][0] == '[':
            var_name = words[2]
        else:
            var_name = words[1]
        for templine in module_lines:
            if 'assign' in templine and var_name in templine[0:templine.find('=')]:
                wire_flag = True
                break
        if wire_flag:
            line = line.replace(words[0], wire_convert_dict[words[0]])
        else:
            line = line.replace(words[0], logic_convert_dict[words[0]])
    return line

class skip_judge(object):

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

def convert_line(line):
    words = line.split(' ')
    for i, word in enumerate(words):
        words[i] = delete_word(word)
        words[i] = replace_word(word)
    converted_line = ' '.join(words)
    return converted_line

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

def split_logic_decrarement(read_file_name, write_file_name):
    write_file = open(write_file_name, 'w')
    with open(read_file_name, 'r') as f:
        for line in f:
            words = line.replace(',', '').split()
            if not words:
                write_file.write(line)
                continue
            if set(['logic', 'bit', 'byte']).intersection(words) and ',' in line:
                decrarements, packed_bit, unpacked_bit, var_names = separate_in_bracket(line)
                for var in var_names:
                    write_file.write(' '.join(decrarements + unpacked_bit + (var,) + packed_bit) + ';\n')
            else:
                write_file.write(line)

def separate_in_bracket(line):
    decrarements = []
    packed_bit = []
    unpacked_bit = []
    var_names = []

    line = line.replace(',', '')
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

def expand_enum(read_file_name, write_file_name):
    def get_enum_values(line):
        rb_pos = line.find('{')
        lb_pos = line.find('}')

        if rb_pos == -1 or lb_pos == -1:
            raise Exception('Illegal enumerate.')

        line = line[rb_pos+1:lb_pos]
        line = line.replace(' ','')

        enum_dict = {}
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

def make_module_info(read_file_name, write_file_name):
    #TODO imple
    write_file = open(write_file_name, 'w')
    in_module = False
    dec_line = False
    with open(read_file_name, 'r') as f:
        for line in f:
            if 'module' in line.split():
                module_name = line.split()[1].split('(')
                new_module = module_info(module_name)
                dec_line = ';' in line
            if dec_line:
                new_module.dec_lines.append(line)
                if ';' in line:
                    dec_line = False
                    new_module.readfirtsline()
            elif in_module:
                module_info.readline(line)
            elif 'endmodule':
                in_module = False
                print(module_info.tostr())

class module_info(object):
    def __init__(self, name):
        self.name = name
        self.dec_lines = []
        self.input = []
        self.output = []
        self.inout = []

    def readfirtsline(self):
        """[FUNCTIONS]
        ex.
        module COMPARE(output GT, output LE, output EQ,
                       input [1:0] A, input [1:0] B, input C);
        """
        first_line = " ".join(self.dec_lines)
        first_line = re.sub("\[.+?\]", " ", first_line)
        in_bracket = re.findall("\(.+?\)", first_line)[0]
        words = in_bracket.split(',')
        for i, word in enumerate(words):
            if word == 'input':
                self.input.append(words[i + 1])
            elif word == 'output':
                self.output.append(words[i + 1])
            if word == 'inout':
                self.inout.append(words[i + 1])

    def readline(self, line):
        """[FUNCTIONS]
        ex.
        module COMPARE(GT, LE, EQ, A, B, C);
        縲縲output GT, LE, EQ;
        縲縲input [1: width_A] A, B;
        縲縲input [1: width_B] C;
        """
        #line = line.replace('(', ' ')
        #line = line.replace(')', ' ')
        line = re.sub("\[.+?\]", " ", line)
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
            elif in_input_port:
                self.input.append(word)
            elif in_output_port:
                self.output.append(word)
            elif in_inout_port:
                self.inout.append(word)
            elif word == ';':
                in_input_port = False
                in_output_port = False
                in_inout_port = False

    def tostr(self):
        return self.name + 'input' + str(self.input) + 'output' + str(self.output) + 'inout'+ str(self.inout)

if __name__ == '__main__':
    convert2sv(["test.sv",])
