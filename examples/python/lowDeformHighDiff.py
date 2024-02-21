#!/usr/bin/env python

import velocity
import atexit
import datetime
import math


'''
Database and login handling. We are setting variables for later
usage.
'''
# Database login variables. Change as needed.
DB_USER = 'script'
DB_PASS = 'script' # Replace the password here.


# Options for connecting to either a Workstation or GRID installation. Modify the fields as necessary.
# if workstation
WKST_DB_PATH = r'C:/Velocity/Databases/vscDatabase'
# if grid
GRID_DB_NAME = r'vscDatabase'
DB_IP = '127.0.0.1' # Assumes same computer as GRID
DB_PORT = 57000


# Set desired patient to load, as well as image volume names and registration name.
# Note: The cone-beam CT is set as primary so that the registration
# does not escape the bounds of the smaller image.
PATIENT_ID = "Velocity_1"
PRIMVOL= "CBCT"
SECVOL="CTSIM"
REG_NAME = "deform_01"


'''
Create the Velocity engine client and login. From here, we can load
patients and volumes using velengine as if it were a client.
'''
# Create the engine and a helper to check errors
e = velocity.VelocityEngine()
def orThrow(c, e=e):
  if not c or (hasattr(c, 'isValid') and not c.isValid()):
    raise RuntimeError(e.getErrorMessage())


#Login to Velocity user the script user credentials. The current configuration
#is to log into a Grid. In order to log into a Workstation, comment out
#the following line, and uncomment the next line.
orThrow(e.loginToGrid(DB_USER, DB_PASS, DB_IP, DB_PORT, GRID_DB_NAME))
#orThrow(e.loginToWorkstation(DB_USER, DB_PASS, WKST_DB_PATH, True))
atexit.register(e.logout) # ensure we log out when the script ends


# Load the patient and import operations
patient = e.loadPatientByPatientId(PATIENT_ID)
if not patient.isValid():
  print('Importing CBCT and CTSIM...')
  iops = e.getImportOperations()
  orThrow(iops.importDirectory(IMPORT_DIR, True))
  patient = e.loadPatientByPatientId(PATIENT_ID)
  orThrow(patient)
print('Loaded patient: {}'.format(PATIENT_ID))


# Get and load volumes
volumes = patient.getVolumes()


# Assign and set the primary and secondary volumes
primaryVol = next(v for v in volumes if v.getName() == PRIMVOL)
orThrow(e.loadPrimaryVolumeByUID(primaryVol.getVolumeUID()))
print('Loaded primary volume: {}'.format(primaryVol.getVolumeUID()))
secondaryVol = next(v for v in volumes if v.getName() == SECVOL)
orThrow(e.loadSecondaryVolumeByUID(secondaryVol.getVolumeUID()))
print('Loaded secondary volume: {}'.format(secondaryVol.getVolumeUID()))


# Load the registration and assign a variable to registration operations
orThrow(e.loadRegistrationByName(REG_NAME))
print('Loaded registration: {}'.format(REG_NAME))
regOps = e.getRegistrationOperations()
#orThrow(regOps.saveRegistration(), regOps)


'''
Create subtract from primary resample volume utilizing createResampledVolume().
The elementOperation of '2' corresponds to VolumeResampleSubtract operation.
The result is a volume with name 'Diff'.
Then, we print the size of the image.
'''
print('Creating createResampledVolume...')
volOps = e.getVolumeOperations()
SubVolID = volOps.createResampledVolume(2,'Diff')
print('Resampled Volume ID: {}'.format(SubVolID))
orThrow(e.loadPrimaryVolume(SubVolID))
print('Load resampled volume: {}'.format(SubVolID))
diffVolumetricData = volOps.getVolumetricData(SubVolID)
orThrow(diffVolumetricData, volOps)
diffVolumetricSize = diffVolumetricData.size[0]*diffVolumetricData.size[1]*diffVolumetricData.size[2]
print('Calculate createResampledVolume size: {}'.format(diffVolumetricSize))


'''
Reload CBCT as primary and registration in order to calc Jacobian
Note: Loading a new primary unseats the secondary, which is why
we need to reload the secondary and the registration as well.
'''
orThrow(e.loadPrimaryVolumeByUID(primaryVol.getVolumeUID()))
print('Loaded primary volume: {}'.format(primaryVol.getVolumeUID()))
orThrow(e.loadSecondaryVolumeByUID(secondaryVol.getVolumeUID()))
print('Loaded secondary volume: {}'.format(secondaryVol.getVolumeUID()))
orThrow(e.loadRegistrationByName(REG_NAME))
print('Loaded registration: {}'.format(REG_NAME))


# Calculate the Jacobian determinants, which helps us determine the extent of
# volume changes in each voxel.
print('Computing Jacobian...')
jacobian = regOps.computeJacobian()
orThrow(jacobian, regOps)
jacobianSize = jacobian.size[0]*jacobian.size[1]*jacobian.size[2]
print('Calculated Jacobian size: {}'.format(jacobianSize))
print('Done')


'''
Create mask from volumetric data in order to determine if there are regions
of high difference between the primary volume and deformed secondary volume,
but if there also was a lack of deformation in those regions.
'''
vops = e.getVolumeOperations()
primaryVol = e.getPrimaryVolume()
volumetricData = vops.getVolumetricData(primaryVol.getVelocityId())
orThrow(volumetricData, vops)
print('Creating mask using Diff and Jacobian...')

diffMask = velocity.StructureMask(diffVolumetricData.size)
for i in range(0, diffVolumetricData.size[0]*diffVolumetricData.size[1]*diffVolumetricData.size[2]):
  isDiff = abs(diffVolumetricData.data[i]) >= 700
  isRigid = abs(math.log(abs(jacobian.data[i]))) <= 0.5
  # Create a mask in which there is a significant difference between primary
  # and deformed secondary volume but not a significant change in volume
  diffMask.data[i] = isDiff and isRigid
print('Done')


# Mask should be voxel-aligned with the primary volume
mask = velocity.StructureMask(volumetricData.size)


# Create a new structure set on the primary volume
sops = e.getStructureOperations()
setName = datetime.datetime.now().isoformat()[5:16]
set = sops.createStructureSet(setName)
orThrow(set, sops)

print('Creating structure from mask...')
s1 = sops.createStructureFromMask(set.getVelocityId(), diffMask, "LowDeformHighDiff")
orThrow(s1, sops)


# IMPORTANT: call save after finishing a set of modifications to the structure set
sops.saveStructureSet(set.getVelocityId())

print('Done.')
