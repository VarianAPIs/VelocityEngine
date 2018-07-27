from __future__ import with_statement, print_function
import velocity
import atexit

USER = 'script'
PASS = 'script'

#grid settings
GRID_IP = '127.0.0.1'
GRID_PORT = 57000
GRID_DB = 'jakedb'

#workstation settings
DB_PATH = '/Velocity/Databases/vscDatabase'

PATIENT_ID = '10052012'
PRIMARY_UID = '1.2.840.113619.2.55.3.278435321.302.1313753121.582'
SECONDARY_UID = '1.2.246.352.71.7.1873493392.2486330.20110829091331'
REG_NAME = 'DICOM'
STRUCT_1 = 'Bladder'
STRUCTSET_1UID = '1.2.276.0.7230010.3.1.4.1492057408.5156.1349471628.10'
DEFAULT_ALPHABETA_TISSUE = 3

e = velocity.VelocityEngine()
def orThrow(c, e=e):
  if not c or (hasattr(c, 'isValid') and not c.isValid()):
    raise RuntimeError(e.getErrorMessage())

orThrow(e.loginToGrid(USER, PASS, GRID_IP, GRID_PORT, GRID_DB))
#orThrow(e.loginToWorkstation(USER, PASS, DB_PATH, True))
orThrow(e.loadPatient(PATIENT_ID))
atexit.register(e.logout)

print('Loaded patient: {}'.format(PATIENT_ID))
orThrow(e.loadPrimaryVolume(PRIMARY_UID))
print('Loaded primary volume: {}'.format(PRIMARY_UID))
orThrow(e.loadSecondaryVolume(SECONDARY_UID))
print('Loaded secondary volume: {}'.format(SECONDARY_UID))

# create registration if it doesn't exist
regOps = e.getRegistrationOperations()
orThrow (e.loadRegistrationByName(REG_NAME))
print('Loaded existing registration object: {}'.format(REG_NAME))

structure = e.loadStructureByName(STRUCT_1, STRUCTSET_1UID)
orThrow(structure)
print('Loaded existing structure: {}'.format(STRUCT_1))

structNames = velocity.StringList([STRUCT_1])
structAlphaBetaRatio = velocity.DoubleList([2, DEFAULT_ALPHABETA_TISSUE])
structUIDs = velocity.StringList([structure.getInstanceUID()])

vo = e.getVolumeOperations()
orThrow(vo.createBEDoseByStructureUIDs(25, structNames, structUIDs, structAlphaBetaRatio) != -1, vo)
print ('Biological Effective Dose created')
