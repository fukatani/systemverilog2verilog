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

import re

def clip_in_blacket(line, bracket='('):
    if bracket == '(':
        return re.findall("\(.+?\)", line)[0][1:-1]
    elif bracket == '[':
        return re.findall("\[.+?\]", line)[0][1:-1]
    elif bracket == '{':
        return re.findall("\{.+?\}", line)[0][1:-1]
