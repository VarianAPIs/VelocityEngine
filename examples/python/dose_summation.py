import velocity
import sys
import atexit
from datetime import datetime

DB_USER = 'script'
DB_PASS = 'script'
DB_PATH = 'C:\Velocity\Databases\WKS414'
PATIENT_ID = 'hyperarc'

#grid settings
GRID_IP = '127.0.0.1'
GRID_PORT = 57000
GRID_DB = 'vscDatabase'

# optional patient id argument
patientId = sys.argv[1] if len(sys.argv) > 1 else PATIENT_ID

e = velocity.VelocityEngine()
def orThrow(c, e=e):
  if not c or (hasattr(c, 'isValid') and not c.isValid()):
    raise RuntimeError(e.getErrorMessage())

orThrow(e.loginToWorkstation(DB_USER, DB_PASS, DB_PATH, True))
#orThrow(e.loginToGrid(USER, PASS, GRID_IP, GRID_PORT, GRID_DB))
atexit.register(e.logout) # ensure we log out when the script ends

def makeAutoReg(pVol, sVol, regName):
    orThrow(e.loadPrimaryVolume(pVol.getVelocityId()))
    print('Loaded {} as primary volume'.format(pVol.getName()))
    orThrow(e.loadSecondaryVolume(sVol.getVelocityId()))
    print('Loaded {} as secondary volume'.format(sVol.getName()))
    print('Creating registration object: {}'.format(regName))
    registration = regOps.createNewRegistration(regName)
    orThrow(registration, regOps)
    orThrow(e.loadRegistration(registration.getVelocityId()))
    # now run rigid registration
    print('Running rigid registration...')
    regSettings = velocity.DefaultRigidRegistrationSettings()
    orThrow(regOps.performRigidRegistrationDICOM(regSettings), regOps)
    print('reg done.')
    orThrow(regOps.saveRegistration(), regOps)
    return registration

patient = e.loadPatientByPatientId(patientId)
regOps = e.getRegistrationOperations()
volOps = e.getVolumeOperations()
orThrow(patient)
print('Loaded patient: {}'.format(patientId))

#sort CTs by AcquisitionDate
cts = list(patient.getVolumes('CT'))
cts.sort(key=lambda x: x.getAcquisitionDate())
doses = list(patient.getVolumes('RTDOSE'))

# find all CT-DS in the same frame of reference
# if multiple DS for same CT pick first one that has a plan
print ('-- Finding CT-DS pairs to be resampled --') 
ctDosePair = {}
for ct in cts:
  plans = list(ct.getLinkedPlans())
  for d in doses:
    if d.getName() == 'auto resampled' or d.getName() == 'Sum RTDOSE': continue
    if ct.getFrameOfReferenceUID() == d.getFrameOfReferenceUID():
      ctDosePair[ct] = d
      if next((p for p in plans if p.getInstanceUID() == d.getPlanUID()), None) != None:
        break

  
# resample doses onto the most recent CT
print ('-- Resampling DS onto most recent CT --') 
primaryCT = cts[-1] # most recent by Acq Date
resampledDoses = []
primaryDoseId = -1

for ct in ctDosePair:
  dose = ctDosePair.get(ct)
  if ct.getVelocityId() != primaryCT.getVelocityId():
    # need to load CT-DS to activate/create DICOM registration needed for chain
    orThrow(e.loadPrimaryVolume(ct.getVelocityId()))
    print('Loaded CT {} as primary volume'.format(ct.getName()))
    orThrow(e.loadSecondaryVolume(dose.getVelocityId()))
    print('Loaded Dose {} as secondary volume'.format(dose.getName()))
    dicomReg = e.loadRegistrationByName('DICOM')
    orThrow(dicomReg)

    #make new reg for resampling between primary CT and secondary CT
    ct2ctReg = makeAutoReg(primaryCT, ct, 'resample_reg') 

    # now load primary CT and dose, load chain reg and resample onto primary CT
    orThrow(e.loadPrimaryVolume(primaryCT.getVelocityId()))
    print('Loaded CT {} as primary volume'.format(primaryCT.getName()))
    orThrow(e.loadSecondaryVolume(dose.getVelocityId()))
    print('Loaded Dose id {} as secondary volume'.format(dose.getName()))
    #load registration resample_reg + DICOM
    orThrow(e.loadChainRegistration(ct2ctReg.getVelocityId(), dicomReg.getVelocityId()))
    print('Loaded registration: {}'.format('resample_reg + DICOM')) 
    print('Creating resampled dose...') 
    id = volOps.createResampledVolume(velocity.VolumeResampleReplace, "auto resampled")
    if id == -1:
      print('Error creating resampled dose ' + volOps.getErrorMessage()) 
      continue
    print('Resampled dose created with id {}'.format(id)) 
    resampledDoses.append(id)
  else:
    #this dose does not require resample, same FOR as primary CT
    primaryDoseId = dose.getVelocityId()
    resampledDoses.append(primaryDoseId)
     
print('Summing {} dose volumes ...'.format(len(resampledDoses)))
orThrow(e.loadPrimaryVolume(primaryDoseId)) # load primary dose as anchor
print('Loaded DS id {} as primary volume'. format(primaryDoseId))
sumId = volOps.createResampledVolumeAggregate(velocity.VolumeResampleAdd, resampledDoses, velocity.ResampleFlags.AllowNone) # sum
if sumId == -1:
  print('Error creating sum dose ' + volOps.getErrorMessage()) 
else:
  print('Sum dose created with id {}'.format(sumId))
