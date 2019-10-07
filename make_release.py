#!/usr/bin/python
# coding=utf-8
# Release script for larray-eurostat
# Licence: GPLv3
# Requires:
# * git
from __future__ import print_function, unicode_literals

import sys
from os.path import abspath, dirname
from releaser import make_release
from releaser import update_feedstock
from releaser.make_release import steps_funcs as make_release_steps
from releaser.update_feedstock import steps_funcs as update_feedstock_steps

TMP_PATH = r"c:\tmp\larray_eurostat_new_release"
TMP_PATH_CONDA = r"c:\tmp\larray_eurostat_conda_new_release"
PACKAGE_NAME = "larray_eurostat"
SRC_CODE = "larray_eurostat"
SRC_DOC = None
CONDA_BUILD_ARGS = {'--user': 'larray-project'}

GITHUB_REP = "https://github.com/larray-project/larray_eurostat"
CONDA_FEEDSTOCK_REP = "https://github.com/larray-project/larray_eurostat-feedstock.git"
ONLINE_DOC = None


if __name__ == '__main__':
    argv = sys.argv
    if len(argv) < 2:
        print("Usage: {} [-c|--conda] release_name|dev [step|startstep:stopstep] [branch]".format(argv[0]))
        print("make release steps:", ', '.join(f.__name__ for f, _ in make_release_steps))
        print("update conda-forge feedstock steps:", ', '.join(f.__name__ for f, _ in update_feedstock_steps))
        sys.exit()

    if argv[1] == '-c' or argv[1] == '--conda':
        argv = argv[2:]
        update_feedstock(GITHUB_REP, CONDA_FEEDSTOCK_REP, SRC_CODE, *argv, tmp_dir=TMP_PATH_CONDA)
    else:
        local_repository = abspath(dirname(__file__))
        make_release(local_repository, PACKAGE_NAME, SRC_CODE, *argv[1:], src_documentation=SRC_DOC, tmp_dir=TMP_PATH,
                     conda_build_args=CONDA_BUILD_ARGS)
