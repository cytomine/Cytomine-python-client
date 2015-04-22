# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='Cytomine Python Client',
    version='0.1',
    author='Benjamin Stévens',
    author_email='b.stevens@ulg.ac.be',    
    packages=['cytomine', 'cytomine.models'],    
    url='http://www.cytomine.be',
    license='LICENSE',
    description='Cytomine Python Client.',
    long_description=open('README.txt').read(),    
    install_requires=[
        'httplib2',
        'progressbar',
        'poster',
        'Pillow',
    ]
)
