from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE.md') as f:
    license = f.read()

setup(
    name='SystematicPrioritization',
    version='0.1.0',
    description='Weight and rank tasks by Importance, Urgency, and Difficulty (time-requirement)',
    long_description=readme,
    author='Andrew Sconzo',
    author_email='andrewsconzo@gmail.com',
    url='https://github.com/asconz/SystematicPrioritization',
    install_requires=['PyQt5','nose'],
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
