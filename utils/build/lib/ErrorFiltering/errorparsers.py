'''
Created on Jan 5, 2018

errorparsers contain functions which operate on a string and
return the work and volume. Each pattern goes with one or more
error types.
@author: jsk
'''
import re


def WorkThenVolume(errorBead):
    return WorkThenVolumeText(errorBead.errorText)


'''
Gets the work and volume from an error text
'''


def WorkThenVolumeText(errorText):
    '''
    Handles '^W[.*]-I[.*].*(rest of error text)
    i.e. when the text begins with Work-hyphen-Volume
    returns
    '''
    work = ''
    volume = ''
    beads = re.split('[\- ]', errorText)
    if len(beads) >= 2:
        work = beads[0]
        volume = beads[1]
    else:
        if len(beads) == 1:
            work = beads[0]
    return work, volume


EXIFre = None
'''
edu.harvard.hul.ois.fits.exceptions.FitsToolException NLNZ Metadata Extractor \
error while harvesting file W1CZ2540-I1CZ2706--I1CZ27060114__0114.jpg.
'''


def EXIFWork(errorBead):
    global EXIFre
    if EXIFre is None:
        EXIFre = re.compile('.*while harvesting file ([^\s]*).*')
    m = EXIFre.match(errorBead.errorText)
    s = m.group(1)
    w, v = WorkThenVolumeText(s)
    return f"{w}-{v}:", s


'''
The TIKA errors dont have a work/volume descriptor, so just return the \
bbconsole path
'''


def TikaParse(errorBead):
    return f"{errorBead.file}:", errorBead.lineNumber
