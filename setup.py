"""
flask-yaml-config
-----------------

Bring order to the chaos of Flask configuration
using a hierarchy of yaml files and your environment.
"""
from setuptools import setup

setup(
    name='ordbok',
    version='0.1.0',
    packages=['ordbok'],
    url='http://github.com/alphaworksinc/ordbok',
    license='MIT',
    author='Erik Taubeneck',
    author_email='erik.taubeneck@gmail.com',
    description='Bring order to the chaos of Flask configuration.',
    long_description=__doc__,
    py_modules=['ordbok'],
    zip_safe=False,
    include_package_data=True,
    playforms='any',
    install_requires=[
        'Flask',
        'pyyaml'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: MIT',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
