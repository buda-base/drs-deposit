from setuptools import setup, find_packages

long_description = '# BDRC DBApp Parser ' \
                   'Basic parsers for db apps. Library only'
setup(
    name='bdrc-DBAppParser',
    version='1.00.04',
    packages=find_packages(),
    url='',
    license='MIT',
    author='jimk',
    author_email='jimk@tbrc.org',
    description='# BDRC DbApp Parser'
                'Common arg parsing libraries for bdrc-utils',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.7',
    classifiers=["Programming Language :: Python :: 3", "License :: OSI Approved :: MIT License",
                 "Operating System :: MacOS :: MacOS X", "Operating System :: OS Independent",
                 "Development Status :: 5 - Production/Stable"]
)
