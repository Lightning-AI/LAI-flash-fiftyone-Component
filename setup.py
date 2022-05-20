#!/usr/bin/env python

import os
from importlib.util import module_from_spec, spec_from_file_location

from setuptools import setup, find_packages

_PATH_ROOT = os.path.dirname(__file__)

def _load_py_module(fname, pkg="flash_fiftyone"):
    spec = spec_from_file_location(
        os.path.join(pkg, fname), os.path.join(_PATH_ROOT, pkg, fname)
    )
    py = module_from_spec(spec)
    spec.loader.exec_module(py)
    return py


setup_tools = _load_py_module("setup_tools.py")

REQUIREMENTS = [req.strip() for req in open("requirements.txt").readlines()]

setup(
    name='flash_fiftyone',
    version='0.0.0',
    description='Run FiftyOne with Flash for any task!',
    author='Ethan Harris, Kushashwa Ravi Shrimali',
    author_email='ethan@grid.ai',
    url='https://github.com/PyTorchLightning/LAI-flash-fiftyone',
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=setup_tools._load_requirements(_PATH_ROOT),
)