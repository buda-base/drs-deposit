from setuptools import setup

setup(
    name='utils',
    version='0.42',
    packages=['ScanBuild', 'ErrorFiltering'],
    url='',
    license='',
    author='jimk',
    author_email='jimk@bdrc.org',
    description='Analyze batch build results',
    entry_points={
        'console_scripts': [
            'scanBuild = ScanBuild.ScanBuild:scanBuild'
        ]
    }
)
