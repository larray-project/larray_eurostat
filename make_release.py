#!/usr/bin/python
# Release script for larray-eurostat
# Licence: GPLv3
# Requires:
# * git
# * releaser
# * conda-build
# * anaconda-client
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
UPSTREAM_CONDAFORGE_FEEDSTOCK_REP = "https://github.com/conda-forge/larray_eurostat-feedstock.git"
ORIGIN_CONDAFORGE_FEEDSTOCK_REP = "https://github.com/larray-project/larray_eurostat-feedstock.git"


if __name__ == '__main__':
    argv = sys.argv
    if len(argv) < 2:
        print(f"Usage: {argv[0]} [-c|--conda] release_name|dev [step|startstep:stopstep] [branch]")
        print("make release steps:", ', '.join(f.__name__ for f, _ in make_release_steps))
        print("update conda-forge feedstock steps:", ', '.join(f.__name__ for f, _ in update_feedstock_steps))
        sys.exit()

    if argv[1] == '-c' or argv[1] == '--conda':
        update_feedstock(GITHUB_REP, UPSTREAM_CONDAFORGE_FEEDSTOCK_REP, ORIGIN_CONDAFORGE_FEEDSTOCK_REP,
                         SRC_CODE, *argv[2:], tmp_dir=TMP_PATH_CONDA)
    else:
        local_repository = abspath(dirname(__file__))
        make_release(local_repository, PACKAGE_NAME, SRC_CODE, *argv[1:], src_documentation=SRC_DOC, tmp_dir=TMP_PATH,
                     conda_build_args=CONDA_BUILD_ARGS)
