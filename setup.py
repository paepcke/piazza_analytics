import multiprocessing
from setuptools import setup, find_packages

test_requirements = ['sentinels>=0.0.6', 'nose>=1.0']

setup(
    name = "piazza_analytics",
    version = "0.0.1",
    packages = find_packages(),

    # Dependencies on other packages:
    setup_requires   = ['nose>=1.1.2'],
    tests_require    = test_requirements,
    install_requires = ['MySQL-python>=1.2.5', 
			             'networkx>=1.11',
                        'progressbar>=2.3',
                        'plotly>=2.0.2',
                        'matplotlib>=1.5.3',
                        'numpy>=1.11.1',
                        'scipy>=0.18.1',
                        #'ez_setup>=0.9',  # must be installed ahead of time with pip install ez_setup
                        'spc>=0.3'

			] + test_requirements,

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
     #   '': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
     #   'hello': ['*.msg'],
    },

    # metadata for upload to PyPI
    author = "Ankita Bahani",
    author_email = "paepcke@cs.stanford.edu",
    description = "Building meaningful Analytics from Piazza interactions ",
    license = "BSD",
    keywords = "forum",
    url = "git@github.com:paepcke/piazza_analytics.git",   # project home page, if any
)
