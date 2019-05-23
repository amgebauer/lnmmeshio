from setuptools import setup

setup(
    name='lnmmeshio',
    version='2.0.1',
    packages=['lnmmeshio',],
    license='unlicensed. All rights reserved.',
    long_description=open('README.md').read(),
    install_requires=[
        'progress>=1.5',
        'numpy>=1.16.3',
        'python-utils>=2.3.0',
        'meshio>=2.3.8'
    ]
)