# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name='Cytomine Python Utilities',
    version='0.1',
    author='Benjamin Stévens',
    author_email='b.stevens@ulg.ac.be',
    packages=['cytomine_utilities'],
    url='http://www.cytomine.be',
    license='LICENSE.txt',
    description='Cytomine Python Client.',
    long_description=open('README.txt').read(),
    install_requires=[
        "Cytomine-Python-Client >= 0.1",
        "numpy",
        "shapely",
        #"pyopencv"
    ],
    dependency_links = [
        'git+ssh://git@github.com/cytomine/Cytomine-Python-Client.git#egg=Cytomine-Python-Client-0.1'
    ]
)
