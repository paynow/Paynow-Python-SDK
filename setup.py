from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='paynow',  # Required
    version='1.0.2',  # Required
    description='Paynow Python SDK',  # Required
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://gitlab.com/paynow-developer-hub/Paynow-Python-SDK',  # Optional
    author='WebDev Projects',  # Optional
    author_email='pkg-dev@webdevworld.com',  # Optional
    classifiers=[  # Optional
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Payment Gateway',

        # Pick your license as you wish
        'License :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='paynow-api paynow-zimbabwe paynow-zimbabwe-api paynow-zimbabwe-sdk',  # Optional
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required
    # This field lists other packages that your project depends on to run.
    # Any package you put here will be installed by pip when your project is
    # installed, so they must be valid existing projects.
    #
    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['requests'],  # Optional
    project_urls={  # Optional
        'Bug Reports': 'https://gitlab.com/paynow-developer-hub/Paynow-Python-SDK/issues',
        'Source': 'https://gitlab.com/paynow-developer-hub/Paynow-Python-SDK',
    },
)
