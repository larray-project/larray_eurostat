import os
from setuptools import setup, find_packages


def readlocal(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


DISTNAME = 'larray_eurostat'
VERSION = '0.34-dev'
AUTHOR = 'Alix Damman, Gaetan de Menten, Geert Bryon, Johan Duyck'
AUTHOR_EMAIL = 'ald@plan.be'
DESCRIPTION = "Additional package to import Eurostat files using LArray"
LONG_DESCRIPTION = readlocal("README.rst")
SETUP_REQUIRES = []
INSTALL_REQUIRES = ['larray']
TESTS_REQUIRE = ['pytest']

LICENSE = 'GPLv3'
URL = 'https://github.com/larray-project/larray_eurostat'
PACKAGE_DATA = {'larray_eurostat': ['tests/data/*']}

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Operating System :: OS Independent',
    'Intended Audience :: Science/Research',
    'Intended Audience :: Developers',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Topic :: Scientific/Engineering',
    'Topic :: Software Development :: Libraries',
]

setup(
    name=DISTNAME,
    version=VERSION,
    license=LICENSE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    classifiers=CLASSIFIERS,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    setup_requires=SETUP_REQUIRES,
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRE,
    url=URL,
    packages=find_packages(),
    package_data=PACKAGE_DATA,
)
