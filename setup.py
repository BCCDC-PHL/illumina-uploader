from pathlib import Path

from setuptools import setup, find_packages

import illumina_uploader

setup(
    name='illumina-uploader',
    version=illumina_uploader.__version__,
    description='',
    author='Jaideep Singh',
    author_email='jaideep.singh@bccdc.ca',
    url='https://github.com/BCCDC-PHL/illumina-uploader',
    packages=find_packages(exclude=('test', 'test.*')),
    python_requires='>=3.5',
    install_requires=Path('requirements.txt').read_text(),
    setup_requires=[],
    tests_require=[],
    entry_points = {
        'console_scripts': [
            'illumina-uploader=illumina_uploader.illumina_uploader:main',
            'illumina-uploader-api=illumina_uploader.server',
        ],
    }
)
