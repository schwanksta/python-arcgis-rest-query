import sys
from setuptools import setup

install_requires = [
    "argparse>=1.2.1",
    "requests>=2.4.3"
]

setup(
    name='arcgis-rest-query',
    version='0.14',
    description='A tool to download a layer from an ArcGIS web service as GeoJSON',
    author='Ken Schwencke',
    author_email='schwank@gmail.com',
    url='https://github.com/Schwanksta/python-arcgis-rest-query',
    license='MIT',
    packages=('arcgis',),
    scripts=(
        'bin/arcgis-get',
    ),
    install_requires=install_requires,
)
