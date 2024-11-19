from setuptools import setup, find_packages

setup(
    name="semcalc",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'pytest',
        'python-dateutil',
    ],
)
