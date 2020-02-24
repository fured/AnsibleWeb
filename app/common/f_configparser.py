#!/bin/env python
# -*- coding: utf-8 -*-

"""
Author: fured
Date: 2019.10.17
Desc: 修改ConfigParser将空格和冒号转换为等号的问题
"""

import configparser


class FConfigParser(configparser.ConfigParser):
    def write(self, fp):
        if self._defaults:
            fp.write("[%s]\n" % DEFAULTSECT)
            for (key, value) in self._defaults.items():
                fp.write("%s  %s\n" % (key, str(value).replace("\n", "\n\t")))
            fp.write("\n")
        for section in self._sections:
            fp.write("[%s]\n" % section)
            for (key, value) in self._sections[section].items():
                if key != "__name__":
                    fp.write("%s  %s\n" %
                             (key, str(value).replace("\n", "\n\t")))
            fp.write("\n")

    def optionxform(self, optionstr):
        return optionstr
