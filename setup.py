import pybind11
import sys
import os

from setuptools import setup
from pathlib import Path
from pybind11.setup_helpers import Pybind11Extension, build_ext

coverage = os.environ.get("COVERAGE") == "1"
this_dir = Path(__file__).parent.resolve()
extra_compile_args = ['/std:c++17'] if sys.platform == "win32" else ['-std=c++17']
extra_link_args: list[str] = []

if coverage:
    extra_compile_args += ['-O0', '-g', '--coverage']
    extra_link_args += ['--coverage']

ext_modules = [
    Pybind11Extension(
        'monero',
        [
            'src/cpp/common/py_monero_common.cpp',
            'src/cpp/daemon/py_monero_daemon_model.cpp',
            'src/cpp/daemon/py_monero_daemon_default.cpp',
            'src/cpp/daemon/py_monero_daemon_rpc.cpp',
            'src/cpp/wallet/py_monero_wallet_model.cpp',
            'src/cpp/wallet/py_monero_wallet.cpp',
            'src/cpp/wallet/py_monero_wallet_full.cpp',
            'src/cpp/wallet/py_monero_wallet_rpc.cpp',
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
            str(this_dir / 'external' / 'monero-cpp' / 'build')
        ],
        libraries=['monero-cpp'],
        language='c++',
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args
    ),
]

setup(
    name='monero',
    version='0.0.1',
    author='everoddandeven',
    author_email="everoddandeven@protonmail.com",
    maintainer='everoddandeven',
    maintainer_email='everoddandeven@protonmail.com',
    license="MIT",
    url='https://github.com/everoddandeven/monero-python',
    download_url="https://github.com/everoddandeven/monero-python/releases",
    description='A Python library for using Monero.',
    long_description='Python bindings for monero-cpp.',
    keywords=["monero", "monero-python", "python", "bindings", "pybind11"],
    ext_modules=ext_modules,
    install_requires=['pybind11>=2.12.0'],
    cmdclass={"build_ext": build_ext}
)
