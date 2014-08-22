"""
Ordbok
-----------------

Bring order to the chaos of configuration
using a hierarchy of cofiguration files and your environment.
"""
from setuptools import setup

setup(
    name='ordbok',
    version='0.1.4',
    packages=['ordbok'],
    url='http://github.com/alphaworksinc/ordbok',
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
        'pyyaml'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English ',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
