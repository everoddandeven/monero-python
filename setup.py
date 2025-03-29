from setuptools import setup, Extension
import pybind11
import sys
from pathlib import Path

this_dir = Path(__file__).parent.resolve()

ext_modules = [
    Extension(
        'monero',
        ['src/monero_bindings.cpp'],
        include_dirs=[
            pybind11.get_include(),
            str(this_dir / 'external' / 'boost'),
            str(this_dir / 'external' / 'monero-cpp' / 'src'),
        ],
        library_dirs=[
            str(this_dir / 'build'),
        ],
        libraries=['libmonero-cpp'],
        language='c++',
        extra_compile_args=['/std:c++17'],
    ),
]

setup(
    name='monero-python',
    version='0.1.0',
    author='Mecanik',
    description='Official Python bindings for monero-cpp (bounty)',
    ext_modules=ext_modules,
    install_requires=['pybind11>=2.12.0'],
)
