"""
Ordbok
-----------------

Bring order to the chaos of configuration
using a hierarchy of cofiguration files and your environment.
"""
from setuptools import setup

setup(
    name='ordbok',
    version='0.1.9',
    packages=['ordbok'],
    url='http://github.com/eriktaubeneck/ordbok',
    license='MIT',
    author='Erik Taubeneck',
    author_email='erik.taubeneck@gmail.com',
    description='Bring order to the chaos of configuration.',
    long_description=__doc__,
    py_modules=['ordbok'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'pyyaml >=3.0, <4.a0',
        'six>= 1.9.0, <2.a0',
        'simple-crypt>=4.0.0, <5.a0'
    ],
    entry_points="""
    [console_scripts]
    ordbok = ordbok.cli:main
    """,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English ',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
