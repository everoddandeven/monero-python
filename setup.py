import pybind11
import sys

from setuptools import setup
from pathlib import Path
from pybind11.setup_helpers import Pybind11Extension, build_ext

this_dir = Path(__file__).parent.resolve()

ext_modules = [
  Pybind11Extension(
    'monero',
    [
      'src/cpp/py_monero.cpp'
    ],
    include_dirs=[
      pybind11.get_include(),
      str(this_dir / 'external' / 'monero-cpp' / 'src'),
      str(this_dir / 'external' / 'monero-cpp' / 'external' / 'monero-project' / 'src'),
      str(this_dir / 'external' / 'monero-cpp' / 'external' / 'monero-project' / 'contrib' / 'epee' / 'include'),
      str(this_dir / 'external' / 'monero-cpp' / 'external' / 'monero-project' / 'external'),
      str(this_dir / 'external' / 'monero-cpp' / 'external' / 'monero-project' / 'external' / 'easylogging++'),
      str(this_dir / 'external' / 'monero-cpp' / 'external' / 'monero-project' / 'external' / 'rapidjson' / 'include'),
      str(this_dir / 'src' / 'cpp'),
      str(this_dir / 'src' / 'cpp' / 'common'),
      str(this_dir / 'src' / 'cpp' / 'daemon'),
      str(this_dir / 'src' / 'cpp' / 'wallet')
    ],
    library_dirs=[
      str(this_dir / 'build'),
      str(this_dir / 'lib')
    ],
    libraries=['monero-cpp'],
    language='c++',
    extra_compile_args=['/std:c++17'] if sys.platform == "win32" else ['-std=c++17'],
  ),
]

setup(
  name='monero',
  version='0.1.0',
  author='everoddandeven',
  maintainer='everoddandeven',
  maintainer_email='everoddandeven@protonmail.com',
  url='https://github.com/everoddandeven/monero-python',
  description='A Python library for using Monero.',
  long_description='A library for using monero-cpp through python bindings.',
  ext_modules=ext_modules,
  install_requires=['pybind11>=2.12.0'],
  cmdclass={"build_ext": build_ext}
)
