#!/usr/bin/env python3
"""
Driver script for transition density matrix analysis in the case of unrestricted orbitals.
"""
from __future__ import print_function, division
import os, sys, time

# Python 2/3 compatibility
try:
    from time import process_time
except ImportError:
    from time import clock as process_time
try:
    from time import perf_counter
except ImportError:
    from time import time as perf_counter

from theodore import theo_header, lib_tden, lib_exciton, input_options, error_handler

(tc, tt) = (process_time(), perf_counter())

def ihelp():
    print(" analyze_UKS.py")
    print(" Command line options:")
    print("  -h, -H, -help: print this help")
    print("  -ifile, -f [dens_ana.in]: name of the input file")
    exit(0)

#--------------------------------------------------------------------------#
# Parsing and computations
#--------------------------------------------------------------------------#

ifile = 'dens_ana.in'

arg=sys.argv.pop(0)
while len(sys.argv)>0:
    arg = sys.argv.pop(0)
    if arg in ["-h", "-H", "-help"]:
        ihelp()
    elif arg == '-ifile' or arg == '-f':
        ifile = sys.argv.pop(0)
    else:
        raise error_handler.ElseError(arg, 'command line option')

if not os.path.exists(ifile):
    print('Input file %s not found!'%ifile)
    print('Please create this file using theoinp or specify its location using -ifile\n')
    ihelp()

ioptions = input_options.tden_ana_options(ifile)
theo_header.print_header('Transition density matrix analysis (UHF/UKS)', ioptions=ioptions)

# ALPHA spin
print("\nRunning alph-spin analysis in directory ALPHA")
ioptions['do_alpha_spin'] = True

tdena_alpha = lib_tden.tden_ana(ioptions)
#if 'mo_file' in ioptions: tdena.read_mos()
tdena_alpha.read_dens()

try:
    os.mkdir('ALPHA')
except FileExistsError:
    pass
os.chdir('ALPHA')
if 'at_lists' in ioptions:
    tdena_alpha.compute_all_OmFrag()
if ioptions['comp_ntos']:  tdena_alpha.compute_all_NTO()

print("\nALPHA-spin results")
tdena_alpha.print_summary()
os.chdir('..')

# BETA spin
print("\nRunning beta-spin analysis in directory BETA")
ioptions['do_alpha_spin'] = False

tdena_beta = lib_tden.tden_ana(ioptions)
#if 'mo_file' in ioptions: tdena.read_mos()
tdena_beta.read_dens()

try:
    os.mkdir('BETA')
except FileExistsError:
    pass
os.chdir('BETA')
if 'at_lists' in ioptions:
    tdena_beta.compute_all_OmFrag()
if ioptions['comp_ntos']:  tdena_beta.compute_all_NTO()

print("\nBETA-spin results")
tdena_beta.print_summary()
os.chdir('..')

# ALPHA+BETA
print("Starting spin-summed analysis")
# Add the alpha values on top of the beta values
for i, state in enumerate(tdena_beta.state_list):
    for aprop in ['Om', 'OmAt', 'OmFrag']:
        state[aprop] += tdena_alpha.state_list[i][aprop]
    for dprop in ['tden', 'PRNTO', 'S_HE', 'Z_HE', 'Om_desc']:
        del state[dprop]
if 'at_lists' in ioptions:
    tdena_beta.compute_all_OmFrag()

print("\nSpin-summed results")
tdena_beta.print_summary()

print("CPU time: % .1f s, wall time: %.1f s"%(process_time() - tc, perf_counter() - tt))
