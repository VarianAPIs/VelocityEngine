from __future__ import print_function
import velocity
import sys
import atexit
import uuid
import datetime

DB_NAME = r'vscDatabase'
DB_USER = 'script'
DB_PASS = 'script'
# if workstation
DB_PATH = r'/Velocity/Databases/vscDatabase'
# if grid
DB_IP = '127.0.0.1'
DB_PORT = 57000

# requires "sixCBCT, AdaptiveMonitoring" data already imported
PATIENT_ID = 'AW3Y6TA684'
PRIMARY_UID = '1.3.12.2.1107.5.1.4.54841.30000011071412175920300003025'
SECONDARY_UID = '1.2.246.352.61.2.4621874044879001489.17114159699319862401'
REGISTRATION_NAME = 'CBCT MULTI'
RIGID_NAME = "RIGID"

e = velocity.VelocityEngine()
def orThrow(c, e=e):
  if not c or (hasattr(c, 'isValid') and not c.isValid()):
    raise RuntimeError(e.getErrorMessage())

#orThrow(e.loginToWorkstation(DB_USER, DB_PASS, DB_PATH, True))
orThrow(e.loginToGrid(DB_USER, DB_PASS, DB_IP, DB_PORT, DB_NAME))
atexit.register(e.logout)
orThrow(e.loadPatient(PATIENT_ID))
print('Loaded patient: {}'.format(PATIENT_ID))
orThrow(e.loadPrimaryVolume(PRIMARY_UID))
print('Loaded primary volume: {}'.format(PRIMARY_UID))
orThrow(e.loadSecondaryVolume(SECONDARY_UID))
print('Loaded secondary volume: {}'.format(SECONDARY_UID))
orThrow(e.loadRegistrationByName(REGISTRATION_NAME))
print('Loaded registration: {}'.format(REGISTRATION_NAME))

rops = e.getRegistrationOperations()
sops = e.getStructureOperations()

primaryVol = e.getPrimaryVolume()
secondaryVol = e.getSecondaryVolume()


# find an external structure, throws StopIteration if not found
primarySet = next(s for s in primaryVol.getStructureSets() if s.getName() == 'Original SIM')
structure = next(s for s in primarySet.getStructures() if s.getName() == 'Mandible')
print('Using structure "{}" from structure set "{}"'.format(structure.getName(), primarySet.getName()))

# create a new structure set on the secondary volume
targetSetName = datetime.datetime.now().isoformat()[:16]
targetSet = sops.createStructureSet(targetSetName, False)
orThrow(targetSet, sops)

# copy the external to the new structure set
print('Copying structure to secondary...')
newStructures = sops.copyStructuresToSecondary([structure.getVelocityId()], targetSet.getVelocityId())
orThrow(len(newStructures) == 1, sops)
newStructureId = iter(newStructures).next()
newStructure = newStructures[newStructureId]
print('Structure copied to secondary, computing metrics...')

def metrics():
  # compute metrics on the copied external structure
  c = sops.conformality(structure.getVelocityId(), newStructure.getVelocityId())
  print('Conformality: {}'.format(c))
  if c < 0.0:
    print('Error: {}'.format(sops.getErrorMessage()))

  mets = sops.surfaceDistanceMetrics(structure.getVelocityId(), newStructure.getVelocityId())
  if not mets.isValid:
    print('Error: {}'.format(sops.getErrorMessage()))
  else:
    print('Metrics: Hausdorff={}, min={}, median={}, mean={}, stddev={}'.format(mets.hausdorffDistance, mets.min, mets.median, mets.mean, mets.standardDeviation))

# show metrics on registration used for copying
metrics()

# now on an alternative registration
orThrow(e.loadRegistrationByName(RIGID_NAME))
print('Loaded registration: {}'.format(RIGID_NAME))
metrics()
