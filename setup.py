#!/usr/bin/env python
from setuptools import setup, find_packages
import client 

METADATA = dict(
    name='ribida',
    version=client.__version__,
    author='chen chiyuan',
    author_email='chenchiyuan03@.com',
    description='kagalaska client',
    long_description=open('README.md').read(),
    url='http://github.com/chenchiyuan/ribida',
    keywords='kagalaska tag search engine',
    install_requires=[],
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Environment :: Web Environment',
        'Topic :: Internet',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    zip_safe=False,
    packages=find_packages(),
)

if __name__ == '__main__':
    setup(**METADATA)

