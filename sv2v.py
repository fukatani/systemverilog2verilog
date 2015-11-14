#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      rf
#
# Created:     14/11/2015
# Copyright:   (c) rf 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from optparse import OptionParser
import os

def main():
    optparser = OptionParser()
    (options, args) = optparser.parse_args()

    #TODO interface, enum, struct, union

    if args:
        filelist = args
    else:
        raise Exception("Verilog file is not assigned.")

    for f in filelist:
        if not os.path.exists(f): raise IOError("file not found: " + f)

    for file_name in filelist:
        sj = skip_judge()
        read_file = open(file_name, 'r')
        write_file = open(file_name.split()[0] + '_conv.v', 'w')
        try:
            for line_num, line in enumerate(read_file):
                skip_start_line_num = line_num
                while sj.judge_line(line):
                    line = next(read_file)
                    line_num += 1
                line = convert_for_logic(line, read_file)
                write_file.write(convert_line(line))
        except (StopIteration, Endmodule_exception):
            print('Error!! Irregular description around line ' + str(skip_start_line_num))

class Endmodule_exception(Exception): pass

def convert_for_logic(line, read_file):
    #TODO input
    logic_convert_dict = {'logic': 'reg', 'bit': 'reg', 'byte': 'reg [7:0]'}
    wire_convert_dict = {'logic': 'wire', 'bit': 'wire', 'byte': 'wire [7:0]'}
    wire_flag = False

    words = line.replace(';', '').split()
    if words[0] in logic_convert_dict.keys():
        if words[1][0] == '[':
            var_name = words[2]
        else:
            var_name = words[1]
        start_pointer = read_file.tell()
        while 'endmodule' in line:
            if 'assign' in line and var_name in line:
                wire_flag = True
                break
        read_file.seek(start_pointer)
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
                self.assert_flag = True
                return True
            elif 'default' in line:
                self.default_flag = True
                return True
            elif 'clocking' in line:
                self.clocking_flag = True
                return True
            elif 'sequence' in line:
                self.sequence_flag = True
                return True
            elif 'property' in line:
                self.property_flag = True
                return True

def convert_line(line):
    words = line.split(' ')
    for word in words:
        delete_word(word)
        replace_word(word)
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

if __name__ == '__main__':
    main()
