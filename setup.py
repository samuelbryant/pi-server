#!/usr/bin/env python3.6
import os
import sys
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
  long_description = f.read()

# Single source important information
exec(open('piserver/constants.py').read())

if sys.version_info[0] != 3:
    print('This script requires Python 3')
    exit(1)

setup(
    name='piserver',
    version=__version__,
    description=DESCRIPTION,
    python_requires='>=3',
    long_description=long_description,
    packages=['piserver'],
    install_requires=[
        # 'pkg-resources == 0.0.0',
        # 'pycairo >= 1.17.0',
        # 'pygobject >= 3.28.2'
    ],
    entry_points={
        'console_scripts': [
            ('%s=piserver.main:main' % PROGRAM),
            'pi-server-backup-jobs=piserver.main:listjobs'
        ],
    }
)
