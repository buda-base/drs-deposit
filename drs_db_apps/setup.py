from setuptools import setup, find_packages

long_description = """
bdrc-db-lib clients that support the HUL DRS deposit process
"""
setup(
    name='bdrc-drs-deposit',
    version='1.00.00',
    packages=find_packages(),
    url='',
    license='',
    author='jimk',
    author_email='jimk@tbrc.org',
    description='Bdrc Drs client',
    python_requires='>=3.7',
    install_requires=['pymysql', 'lxml', 'bdrc-db-lib'],
    classifiers=["Programming Language :: Python :: 3", "License :: OSI Approved :: MIT License",
                 "Operating System :: MacOS :: MacOS X", "Operating System :: OS Independent",
                 "Development Status :: 5 - Production/Stable"],
    entry_points={
        'console_scripts': [
            'DRSUpdate = DRSUpdate:DRSUpdate',
            'genOutlinesQuery = genOutlinesFromQuery:genOutlines',
            'addRelated = addRelated:AddRelated',
            'genWorks = genWorks:genWorks',
            'genVolumes = genWorks:genVolumes',
            'getReadyRelated = getReadyRelated:GetReadyRelated',
            'getReadyWorks = getReadyWorks:getReadyWorks',
            'getNamedWorks = getNamedWorks:getNamedWorks',
            'splitWorks = splitWorks:splitWorks',
            'update_build_status = updateBuildStatus:update_build_status'
        ]
    }
)
