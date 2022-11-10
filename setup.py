from os.path import dirname, join

from setuptools import setup

import wocelconnectors


def read_file(filename):
    with open(join(dirname(__file__), filename)) as f:
        return f.read()


setup(
    name=wocelconnectors.__name__,
    version=wocelconnectors.__version__,
    description=wocelconnectors.__doc__.strip(),
    long_description=read_file('README.md'),
    author=wocelconnectors.__author__,
    author_email=wocelconnectors.__author_email__,
    py_modules=[wocelconnectors.__name__],
    include_package_data=True,
    packages=['wocelconnectors', 'wocelconnectors.algo', 'wocelconnectors.algo.connectors',
              'wocelconnectors.algo.connectors.util', 'wocelconnectors.algo.connectors.variants'],
    url='http://www.pm4py.org',
    license='GPL 3.0',
    install_requires=[
        "pm4py==2.3.0rc2",
        "requests",
        "pywin32",
        "Flask",
        "flask-cors",
        "setuptools"
    ]
)
