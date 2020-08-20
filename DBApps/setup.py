from setuptools import setup, find_packages

#
# Simpler than simple:
# python setup.py install
# And then you have in your $PYTHON/bin (on MacOS)
# ls -l $(dirname $(which getNamedWorks))
# (py361) jimk@Druk:DBApps$ ls -l $(dirname $(which getNamedWorks))
# total 312
# ...
# -rwxr-xr-x   1 jimk  staff   413 Jun 19 17:31 getNamedWorks
# and this is an executable script which wraps the entry points
setup(
    name='bdrc_DBApps',
    version='1.00.00',
    # packages=['config', 'DBApps', 'DBApps.TBRCSrc', 'DBApps.Writers', 'DBApps.DBAppTests',
    #           'DBApps.SourceProcessors'],
    packages=find_packages(),
    url='',
    license='',
    author='jimk',
    author_email='jimk@tbrc.org',
    description='BDRC DRS DB Apps Suite',
    python_requires='>=3.7',
    classifiers=["Programming Language :: Python :: 3", "License :: OSI Approved :: MIT License",
                 "Operating System :: MacOS :: MacOS X", "Operating System :: OS Independent",
                 "Development Status :: 5 - Production/Stable"],
    entry_points={
        'console_scripts': [
            'DRSUpdate = DBApps.DRSUpdate:DRSUpdate',
            'genOutlinesQuery = DBApps.genOutlinesFromQuery:genOutlines',
            'addRelated = DBApps.addRelated:AddRelated',
            'genWorks = DBApps.genWorks:genWorks',
            'genVolumes = DBApps.genWorks:genVolumes',
            'getReadyRelated = DBApps.getReadyRelated:GetReadyRelated',
            'getReadyWorks = DBApps.getReadyWorks:getReadyWorks',
            'getNamedWorks = DBApps.getNamedWorks:getNamedWorks',
            'splitWorks = DBApps.splitWorks:splitWorks',
            'updateBuildStatus = DBApps.updateBuildStatus:updateBuildStatus'
        ]
    }
)
