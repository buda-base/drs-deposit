from setuptools import setup

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
    name='DBApps',
    version='0.42.3',
    packages=['config', 'DBApps', 'DBApps.TBRCSrc', 'DBApps.Writers', 'DBApps.DBAppTests',
              'DBApps.SourceProcessors'],
    url='',
    license='',
    author='jimk',
    author_email='',
    description='DRS DB Apps Suite',
    entry_points={
        'console_scripts': [
            'DRSUpdate = DBApps.DRSUpdate:DRSUpdate',
            'genOutlines = DBApps.genOutlines:genOutlines',
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
