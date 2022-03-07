from setuptools import setup
import os


def open_file(fname):
    return open(os.path.join(os.path.dirname(__file__), fname))


setup(
    name='google_image_scraper',
    version='0.0.2',
    author='Fabian Gruben',
    author_email='fabian.gruben@googlemail.com',
    packages=['google_image_scraper'],
    url='https://github.com/FabianGruben/google_image_scraper',
    license="MIT",
    classifiers=[
        'Programming Language :: Python :: 3.6',
    ],
    description='Google Image scraper using Selenium',
    long_description=open_file('README.md').read(),
    #dependencies for your library
    install_requires = ['selenium'],
    zip_safe=True,
    #additional data

)
