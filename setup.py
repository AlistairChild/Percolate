import setuptools
from setuptools import setup, find_packages

with open("README.mdown", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="percolate",
    version="0.0.1",
    packages=find_packages(exclude=["tests*"]),
    license="MIT",
    description="Percolate is a project that allows data to flow in pathways specified by the main function",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "setuptools >= 41.2.0",
        "numpy>=1.18.1",
        "scipy>=1.4.1",
        "wxPython>=4.1.0",
        "matplotlib>=3.1.2",
        "lmfit>=1.0.0",
        "pandas>=1.1.4",
        "scipy>=1.4.1",
    ],  # more
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "percolate= percolate:gui",
        ],
    },
    # url='github link',#more
    author="Alistair Child",
    author_email="alistair@mtoto.org",
)
