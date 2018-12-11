# coding: utf-8

# https://click.palletsprojects.com/en/7.x/setuptools/#setuptools-integration

"""
speleo-collector is a tool to collect weather and cavelink data.
Data is then prepared and stored to an influxDB instance.
"""
import re
from setuptools import setup, find_packages

version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('speleOWDL/speleowdl.py').read(),
    re.M
    ).group(1)

with open('README.rst', 'r') as f:
    long_description = f.read()

setup(
    name='speleo-OWDL',
    version=version,
    author='Sébastien Pittet',
    author_email='sebastien@pittet.org',
    description='Fetch Cavelink and Weather data and store it to influxDB.',
    long_description=long_description,
    url='https://github.com/SebastienPittet/speleo-OWDL',
    keywords='speleo cavelink netatmo weather',
    packages=find_packages(),
    license='MIT',
    platforms='any',
    include_package_data=True,
    install_requires=[
        'cavelink',
        'pyatmo',
        'Click',
        'colorama',
        'influxdb',
    ],
    entry_points={
        'console_scripts':['speleowdl = speleOWDL.speleowdl:main']
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Environment :: Console',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Other Audience'
    ]
)
