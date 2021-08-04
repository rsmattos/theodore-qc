#!/usr/bin/env python3
"""
Check if a file can be read by cclib and if all the required information is available.
"""
from __future__ import print_function, division
import sys

from .. import theo_header, cclib_interface, input_options, error_handler
from .actions import Action

class CCCheck(Action):

    name = 'cc_check'

    _questions = """
    logfile = :: existing_file
    printlevel = 1 :: int, alias=p
    """
    _colt_description = "Check if a logfile can be parsed with cclib"

    def run(logfile, printlevel):
        theo_header.print_header(__class__._colt_description)
        
        
        ioptions = input_options.dens_ana_options(ifile=None, check_init=False)
        ioptions['rtype'] = 'cclib'
        ioptions['rfile'] = logfile
        
        ccparser = cclib_interface.file_parser_cclib(ioptions)
        errcode = ccparser.check(lvprt=printlevel)
        
        if errcode <= 1:
            print(("\n %s can be parsed by using rtype='cclib' in dens_ana.in."%logfile))
            if errcode == 0:
                print(" Conversion to Molden format also possible")
            else:
                print(" But conversion to Molden format is not possible")
        else:
            print(("\n %s cannot be parsed by cclib (errcode=%i)!"%(logfile, errcode)))
