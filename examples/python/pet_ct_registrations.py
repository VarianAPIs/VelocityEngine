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

# requires "PETCT, Deformable" data already imported
PATIENT_ID = "H&N 1"
PRIMARY_UID = '1.3.12.2.1107.5.1.4.1031.30000009080711125237500008699'
SECONDARY_UID = '1.2.840.113704.1.111.3200.1253806429.28'
REG_NAME = 'python_registration'

# create the engine and a helper to check errors
e = velocity.VelocityEngine()
def orThrow(c, e=e):
  if not c or (hasattr(c, 'isValid') and not c.isValid()):
    raise RuntimeError(e.getErrorMessage())

#orThrow(e.loginToWorkstation(DB_USER, DB_PASS, DB_PATH, True))
orThrow(e.loginToGrid(DB_USER, DB_PASS, DB_IP, DB_PORT, DB_NAME))
atexit.register(e.logout) # ensure we log out when the script ends

orThrow(e.loadPatientByPatientId(PATIENT_ID))
print('Loaded patient: {}'.format(PATIENT_ID))
orThrow(e.loadPrimaryVolumeByUID(PRIMARY_UID))
print('Loaded primary volume: {}'.format(PRIMARY_UID))
orThrow(e.loadSecondaryVolumeByUID(SECONDARY_UID))
print('Loaded secondary volume: {}'.format(SECONDARY_UID))

# create registration
regOps = e.getRegistrationOperations()
print('Creating registration object: {}'.format(REG_NAME))
registration = regOps.createNewRegistration(REG_NAME)
orThrow(registration, regOps)
orThrow(e.loadRegistration(registration.getVelocityId()))

# first move the head into the right general area
print('Running manual registration...')
manualSettings = velocity.ManualRegistrationSettingsStructure()
manualSettings.registrationMatrix = (
  1.0, 0.0, 0.0, 0.0,
  0.0, 1.0, 0.0, 0.0,
  0.0, 0.0, 1.0, 0.0, 
  -8.1947, -275.0845, -394.5001, 1.0)
orThrow(regOps.performManualAlignmentDICOM(manualSettings), regOps)
print('done.')

# now run rigid registration
print('Running rigid registration...')
regSettings = velocity.RigidRegistrationSettingsStructure()
regSettings.roiStart[0] = -102.021;
regSettings.roiStart[1] = -74.7234;
regSettings.roiStart[2] = -5.49291;
regSettings.roiEnd[0] = 100.532;
regSettings.roiEnd[1] = -410.341;
regSettings.roiEnd[2] = -309.819;

regSettings.primaryStartLevel = -110.02;
regSettings.primaryEndLevel = 189.974;
regSettings.secondaryStartLevel =  -125.014;
regSettings.secondaryEndLevel = 224.998;

regSettings.preProcessingMethod = 0
regSettings.performInitialAutoAlignment = True
regSettings.disableRotations = False
regSettings.maximumNumberOfIterations = 45
regSettings.minimumStepLength = 0.0001
regSettings.maximumStepLength = 17.0
regSettings.samplesDenominator = 10
regSettings.numberOfHistogramBins = 25
orThrow(regOps.performRigidRegistrationDICOM(regSettings), regOps)
print('done.')

print('Performing deformable registration...')
bsplineSettings = velocity.BSplineDeformableRegistrationSettingsStructure()
bsplineSettings.roiStart[0] = -102.021
bsplineSettings.roiStart[1] = -74.7234
bsplineSettings.roiStart[2] = -5.49291
bsplineSettings.roiEnd[0] = 100.532;
bsplineSettings.roiEnd[1] = -410.341;
bsplineSettings.roiEnd[2] = -309.819;

bsplineSettings.primaryStartLevel = -110.02
bsplineSettings.primaryEndLevel = 189.974
bsplineSettings.secondaryStartLevel = -125.014
bsplineSettings.secondaryEndLevel = 224.998

bsplineSettings.preprocessingMethod = 0
bsplineSettings.numberOfMultiResolutionLevels = 3 # so each vector setting should be length 3
bsplineSettings.applyBoundaryContinuityConstraints = velocity.BoolList([False]*3)
bsplineSettings.applyTopologicalRegularizer = velocity.BoolList([False]*3)
r3dZeroes = velocity.VectorR3d(0.0)
bsplineSettings.topologicalRegularizerDistanceLimitingCoefficient = velocity.VectorR3dList([r3dZeroes]*3)
bsplineSettings.numberOfHistogramBins = velocity.IntList([50]*3)
bsplineSettings.maximumNumberOfIterations = velocity.IntList([30]*3)
bsplineSettings.maximumNumberOfConsecutiveOptimizerAttempts = velocity.IntList([10]*3)
bsplineSettings.metricValuePercentageDifference = velocity.DoubleList([0.0]*3)
bsplineSettings.minimumStepLength = velocity.DoubleList([0.000001]*3)
bsplineSettings.maximumStepLength = velocity.DoubleList([100.0]*3)
bsplineSettings.samplesDenominator = velocity.IntList([5]*3)
bsplineSettings.relaxationFactor = velocity.DoubleList([0.9]*3)
bsplineSettings.gradientMagnitudeTolerance = velocity.DoubleList([0.000000000000000000005]*3)
bsplineSettings.gridCellSize = velocity.VectorR3dList(( velocity.VectorR3d(5.0), velocity.VectorR3d(10.0), velocity.VectorR3d(15.0) ))
bsplineSettings.gridCellSizeType = velocity.CharList([ord('n')]*3)

orThrow(regOps.performBsplineRegistrationDICOM(bsplineSettings), regOps)
print('done')

# changes are just in memory, save changes to the database
orThrow(regOps.saveRegistration(), regOps)
