#!/usr/bin/env python
import velocity
import atexit

DB_NAME = r'vscDatabase'
DB_USER = 'script'
DB_PASS = 'script'
# if workstation
DB_PATH = r'/Velocity/Databases/vscDatabase'
# if grid
DB_IP = '127.0.0.1'
DB_PORT = 57000

IMPORT_DIR = '/demodata/SPECT, Liver'

LIVER_PATIENT_ID = '0045'

# create the engine and a helper to check errors
e = velocity.VelocityEngine()
def orThrow(c, e=e):
  if not c or (hasattr(c, 'isValid') and not c.isValid()):
    raise RuntimeError(e.getErrorMessage())

#orThrow(e.loginToWorkstation(DB_USER, DB_PASS, DB_PATH, True))
orThrow(e.loginToGrid(DB_USER, DB_PASS, DB_IP, DB_PORT, DB_NAME))
atexit.register(e.logout) # ensure we log out when the script ends    

# a python function to load a patient and list the volume uids
def loadAndListVolumes(patientId):
  patient = e.loadPatientByPatientId(patientId)
  if not patient.isValid():
    print('Could not load patient id {}, error: {}'.format(patientId, e.getErrorMessage()))
  else:
    volIds = e.getPatientVolumeUIDs(patientId)
    print('Patient id {} has volume UIDs: {}'.format(patientId, volIds))


# try to list liver patient volumes
loadAndListVolumes(LIVER_PATIENT_ID)

# import the liver patient
iops = e.getImportOperations()

print('Importing SPECT, Liver ...')
if iops.importDirectory(IMPORT_DIR, True):
  print('Successfully imported.')
else:
  print('Import error: {}'.format(iops.getErrorMessage()))

# try again to list the volumes for the liver patient
loadAndListVolumes(LIVER_PATIENT_ID)

