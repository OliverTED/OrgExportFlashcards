#! /usr/bin/env python

# https://pythonhosted.org/setuptools/setuptools.html




import sys, re

from setuptools import setup, find_packages

install_requires = 'PyOrgMode'

name = "OrgExportFlashcards"

url = 'https://github.com/OliverTED/OrgExportFlashcards'

long_description = """
`{name}` ...

`website/docs <{url}>`_
""".format(**locals())

# https://pypi.python.org/pypi?:action=list_classifiers
classifiers = '''
Development Status :: 1 - Planning
#Development Status :: 2 - Pre-Alpha
#Development Status :: 3 - Alpha
#Development Status :: 4 - Beta
#Development Status :: 5 - Production/Stable
#Development Status :: 6 - Mature
Environment :: Console
Intended Audience :: End Users/Desktop
License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)
Programming Language :: Python
Topic :: Utilities
'''.split('\n')
classifiers = filter(lambda s: re.match('^[^#]', s), classifiers)


# print(find_packages())

setup(name = name,
      description = '',
      version = '0.0.1',
      license = 'GPL',
      author = 'Oliver Burghard',
      author_email = 'oliverburghard@web.de',
      url = url,
      classifiers = classifiers,
      packages = find_packages(),
      install_requires = install_requires,
      long_description = long_description,
      entry_points = {
          'console_scripts': [
              'org_to_flashcards = src.main:main'
          ]
      },
      )
