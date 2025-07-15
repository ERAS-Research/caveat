from setuptools import setup, find_packages
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
setup(
    name = 'caveat',
    version = '0.1_dev',

    author="Torsten Reuschel",
    author_email="torsten.reuschel@unb.ca",
    ##not sure whether i should have put myself here as well so i left it as is in the toml file
    description = "Context-Aware Verification, Emulation, and Training",
    packages = find_packages(),
    long_description=read("README.md"),
)
