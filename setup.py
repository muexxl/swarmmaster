
from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='swarmmaster',
    version='0.1.1',
    description='Swarmmaster connects multiple Mavlink clients via radio and forwards MAVLINK packages via UDP to a ground control station ',
    long_description=readme,
    author='Stephan Muekusch',
    author_email='stephan@1drone.de',
    url='https://github.com/muexxl/swarmmaster.git',
    license=license,
    packages=find_packages(exclude=('tests', 'test_integration','docs')),
    scripts=['swarmmaster-run']
)

