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

def main():
    optparser = OptionParser()
    (options, args) = optparser.parse_args()
    #TODO interface, enum, struct, union

    if args:
        filelist = args
    else:
        raise Exception("Verilog file is not assigned.")

    for file_name in filelist:
        if not os.path.exists(file_name): raise IOError("file not found: " + file_name)

    for file_name in filelist:
        comdel_file = file_name.split()[0] + '_comdel.v'
        delete_comments(file_name, comdel_file)
        enum_file_name = file_name.split()[0] + '_eexpand.v'
        expand_enum(comdel_file, enum_file_name)
        split_file_name = file_name.split()[0] + '_split.v'
        split_logic_decrarement(enum_file_name, split_file_name)


        sj = skip_judge()
        read_file = open(split_file_name, 'r')
        write_file = open(file_name.split()[0] + '_conv.v', 'w')

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
    write_file = open(write_file_name, 'w')
    with open(read_file_name, 'r') as f:
        for line in f:
            if 'enum' in line.split():
                for val, num in get_enum_values(line).items():
                    write_file.write(" ".join(('localparam', val, "= 'd", str(num), ';')))
            else:
                write_file.write(line)

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

if __name__ == '__main__':
    main()
