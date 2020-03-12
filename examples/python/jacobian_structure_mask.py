#!/usr/bin/env python

import velocity
import atexit
import datetime
import math

DB_NAME = r'vscDatabase'
DB_USER = 'script'
DB_PASS = 'script'
# if workstation
DB_PATH = r'/Velocity/Databases/vscDatabase'
# if grid
DB_IP = '127.0.0.1'
DB_PORT = 57000

# requires "OPT 3, CBCT adaptive" data
IMPORT_DIR = "C:\demodata\OPT 3, CBCT adaptive"
PATIENT_ID = "H&N 3"
REG_NAME = 'python_registration'

# create the engine and a helper to check errors
e = velocity.VelocityEngine()
def orThrow(c, e=e):
  if not c or (hasattr(c, 'isValid') and not c.isValid()):
    raise RuntimeError(e.getErrorMessage())

orThrow(e.loginToWorkstation(DB_USER, DB_PASS, DB_PATH, True))
#orThrow(e.loginToGrid(DB_USER, DB_PASS, DB_IP, DB_PORT, DB_NAME))
atexit.register(e.logout) # ensure we log out when the script ends

patient = e.loadPatientByPatientId(PATIENT_ID)
if not patient.isValid():
  print('Importing CBCT and CTSIM...')
  iops = e.getImportOperations()
  orThrow(iops.importDirectory(IMPORT_DIR, True))
  patient = e.loadPatientByPatientId(PATIENT_ID)
  orThrow(patient)
print('Loaded patient: {}'.format(PATIENT_ID))

#get and load volumes
volumes = patient.getVolumes()

primaryVol = next(v for v in volumes if v.getName() == 'CTSIM')
secondaryVol = next(v for v in volumes if v.getName() == 'CBCT')

orThrow(e.loadPrimaryVolumeByUID(primaryVol.getVolumeUID()))
print('Loaded primary volume: {}'.format(primaryVol.getVolumeUID()))
orThrow(e.loadSecondaryVolumeByUID(secondaryVol.getVolumeUID()))
print('Loaded secondary volume: {}'.format(secondaryVol.getVolumeUID()))

# create registration
regOps = e.getRegistrationOperations()
print('Creating registration object: {}'.format(REG_NAME))
registration = regOps.createNewRegistration(REG_NAME)
orThrow(registration, regOps)
orThrow(e.loadRegistration(registration.getVelocityId()))


# now run rigid registration
print('Running rigid registration...')
regSettings = velocity.RigidRegistrationSettingsStructure()
orThrow(regOps.performRigidRegistrationDICOM(regSettings), regOps)
print('done.')

print('Performing deformable registration...')
bsplineSettings = velocity.BSplineDeformableRegistrationSettingsStructure()
orThrow(regOps.performBsplineRegistrationDICOM(bsplineSettings), regOps)
print('done')

# changes are just in memory, save changes to the database
orThrow(regOps.saveRegistration(), regOps)

print('Computing Jacobian...')
jacobian = regOps.computeJacobian()
orThrow(jacobian, regOps)
print('done')

# create mask from volumetric data
thresholdValue = 800 #HU
vops = e.getVolumeOperations()
primaryVol = e.getPrimaryVolume()
volumetricData = vops.getVolumetricData(primaryVol.getVelocityId())
orThrow(volumetricData, vops)

# mask should be voxel-aligned with the volume
mask = velocity.StructureMask(volumetricData.size)

print('Creating mask from threshold... ')
for i in range(0,volumetricData.size[0]*volumetricData.size[1]*volumetricData.size[2]):
  isDense = volumetricData.data[i] >= thresholdValue
  isNonRigid = abs(math.log(abs(jacobian.data[i]))) >= 0.5
  
  # find dense material like bone that had non-rigid deformation
  mask.data[i] = isDense and isNonRigid
print('done')

# create a new structure set on the primary volume
sops = e.getStructureOperations()
setName = datetime.datetime.now().isoformat()[:16]
set = sops.createStructureSet(setName)
orThrow(set, sops)

print('Creating structure from mask ... ')
s1 = sops.createStructureFromMask(set.getVelocityId(), mask, "mask_API")
orThrow(s1, sops)

# create a new structure by applying a margin
s2 = sops.createStructure(set.getVelocityId(), "mask_API + Margin")
orThrow(s2, sops)

marginSettings = velocity.MarginSettings(5)

print('Applying margin ... ')
s2 = sops.margin(set.getVelocityId(), s1.getVelocityId(), s2.getVelocityId(), marginSettings)
orThrow(s2, sops)

# IMPORTANT: call save after finishing a set of modifications to the structure set
sops.saveStructureSet(set.getVelocityId())

print('Done.')


