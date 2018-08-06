""" Constants"""
FAIL_MODS_CALL = 'could not be built Error calling MODS web service'
'''
Fairly stupid: since we use split[:], and we rejoin the error texts,
we have to elide the colon from the search. The actual text is "could not be \
build: Error calling MODS..."
'''
FAIL_MODS_ID = 'failMODS'

FAIL_EXIF_STR = '(java.lang.RuntimeException Not an EXIF block)'
FAIL_EXIF_ID = 'notEXIF'

'''
In systems where fits/xml/fits.xml does not have the Tika tool excluding JPG
and JPEGfiles, you will see this error for batches which contain jpgs and jpegs
'''
FAIL_TIKA_ID = 'FailTika'
'''
No colons
'''
FAIL_TIKA_STR = ' Exception reading metadata (Error on line 1 An invalid XML\
 character (Unicode 0x1e)'

'''
Handle Jhove errors with multi-page tiffs
'''
FAIL_MULTI_PAGE_TIF_ID = 'FailMultiPageTif'
FAIL_MULTI_PAGE_TIF_STR = '(A sequence of more than one item is not\
 allowed as the first operand of \'div\')'
