# setup.py
from skbuild import setup

setup(
    name='monero',
    version='0.0.1',
    author='everoddandeven',
    author_email="everoddandeven@protonmail.com",
    maintainer='everoddandeven',
    maintainer_email='everoddandeven@protonmail.com',
    license="MIT",
    packages=["monero"],
    url='https://github.com/everoddandeven/monero-python',
    download_url="https://github.com/everoddandeven/monero-python/releases",
    description='A Python library for using Monero.',
    long_description='Python bindings for monero-cpp.',
    keywords=["monero", "monero-python", "python", "bindings", "pybind11"],
)
