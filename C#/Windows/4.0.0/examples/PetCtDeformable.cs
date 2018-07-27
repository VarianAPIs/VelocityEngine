using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Linq.Expressions;

namespace Velocity.Examples {
    class PetCtDeformable {
        const string USER = "script";
        const string PASS = "script";

        const string WORKSTATION_PATH = @"C:\Velocity\Databases\vscDatabase";

        const string GRID_IP = "127.0.0.1";
        const int GRID_PORT = 57000;
        const string GRID_DB = "vscDatabase";

        const string PATIENT_ID = "H&N 1";
        const string PRIMARY_UID = "1.3.12.2.1107.5.1.4.1031.30000009080711125237500008699";
        const string SECONDARY_UID = "1.2.840.113704.1.111.3200.1253806429.28";
        const string REG_NAME = "csharp_registration";

        static void OrThrow(bool result, dynamic source) {
            if (!result)
                throw new Exception(source.getErrorMessage());
        }

        static void ValidOrThrow(PatientDataItem result, dynamic source) {
            if (!result.isValid())
                throw new System.Exception(source.getErrorMessage());
        }

        static void Main(string[] args) {

            // connect to the grid
            var engine = new VelocityEngine();
            Action<bool> orThrow = result => OrThrow(result, engine);
            //orThrow(engine.loginToGrid(USER, PASS, GRID_IP, GRID_PORT, GRID_DB));
            orThrow(engine.loginToWorkstation(USER, PASS, WORKSTATION_PATH, true));
            AppDomain.CurrentDomain.ProcessExit += (source, data) => { engine.logout(); };

            orThrow(engine.loadPatientByPatientId(PATIENT_ID));
            Console.WriteLine("Loaded patient: {0}", PATIENT_ID);
            orThrow(engine.loadPrimaryVolumeByUID(PRIMARY_UID));
            Console.WriteLine("Loaded primary volume: {0}", PRIMARY_UID);
            orThrow(engine.loadSecondaryVolumeByUID(SECONDARY_UID));
            Console.WriteLine("Loaded secondary volume: {0}", SECONDARY_UID);

            // create registration
            var regOps = engine.getRegistrationOperations();
            Console.WriteLine("Creating registration object: {0}", REG_NAME);
            var registration = regOps.createNewRegistration(REG_NAME);
            ValidOrThrow(registration, regOps);
            ValidOrThrow(engine.loadRegistration(registration.getVelocityId()), engine);

            // first move the head into the right general area
            var manualSettings = new ManualRegistrationSettingsStructure();
            manualSettings.registrationMatrix = new MatrixR44d(1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, -0.308194699, -0.38874362499, -0.583499961, 1.0);
            orThrow(regOps.performManualAlignment(manualSettings));

            Console.WriteLine("Running rigid registration ...");
            var rigidSettings = new RigidRegistrationSettingsStructure();

            rigidSettings.roiStart[0] = -0.102021;
            rigidSettings.roiStart[1] = -0.1362766;
            rigidSettings.roiStart[2] = -0.55900709;
            rigidSettings.roiEnd[0] = 0.100532;
            rigidSettings.roiEnd[1] = 0.19934;
            rigidSettings.roiEnd[2] = -0.254681;

            rigidSettings.primaryStartLevel = 15084.0;
            rigidSettings.primaryEndLevel = 20035.0;
            rigidSettings.secondaryStartLevel = 16361.0;
            rigidSettings.secondaryEndLevel = 22731.0;

            rigidSettings.preprocessingMethod = PreprocessingFilterMethod.NoFilter;
            rigidSettings.performInitialAutoAlignment = true;
            rigidSettings.disableRotationsX = false;
            rigidSettings.disableRotationsY = false;
            rigidSettings.disableRotationsZ = false;
            rigidSettings.maximumNumberOfIterations = 45;
            rigidSettings.minimumStepLength = 0.0001;
            rigidSettings.maximumStepLength = 17.0;
            rigidSettings.samplesDenominator = 10;
            rigidSettings.numberOfHistogramBins = 25;

            orThrow(regOps.performRigidRegistration(rigidSettings));
            Console.WriteLine("done");

            // perform a deformable registration in the same area
            Console.WriteLine("Performing deformable registration...");
            var bsplineSettings = new BSplineDeformableRegistrationSettingsStructure();
            bsplineSettings.roiStart[0] = -0.102021;
            bsplineSettings.roiStart[1] = -0.1362766;
            bsplineSettings.roiStart[2] = -0.55900709;
            bsplineSettings.roiEnd[0] = 0.100532;
            bsplineSettings.roiEnd[1] = 0.19934;
            bsplineSettings.roiEnd[2] = -0.254681;

            bsplineSettings.primaryStartLevel = 15084.0;
            bsplineSettings.primaryEndLevel = 20035.0;
            bsplineSettings.secondaryStartLevel = 16361.0;
            bsplineSettings.secondaryEndLevel = 22731.0;

            bsplineSettings.preprocessingMethod = PreprocessingFilterMethod.NoFilter;
            bsplineSettings.numberOfMultiResolutionLevels = 3; //  # so each List setting should be length 3
            bsplineSettings.applyBoundaryContinuityConstraints = new BoolList(new bool[] { false, false, false });
            bsplineSettings.applyTopologicalRegularizer = new BoolList(new bool[] { false, false, false });
            var r3dZeroes = new VectorR3d(0.0);
            bsplineSettings.topologicalRegularizerDistanceLimitingCoefficient = new VectorR3dList(new VectorR3d[] { r3dZeroes, r3dZeroes, r3dZeroes });
            bsplineSettings.numberOfHistogramBins = new IntList(new int[] { 50, 50, 50 });
            bsplineSettings.maximumNumberOfIterations = new IntList(new int[] { 30, 30, 30 });
            bsplineSettings.maximumNumberOfConsecutiveOptimizerAttempts = new IntList(new int[] { 10, 10, 10 });
            bsplineSettings.metricValuePercentageDifference = new DoubleList(new double[] { 0.0, 0.0, 0.0 });
            bsplineSettings.minimumStepLength = new DoubleList(new double[] { 0.000001, 0.000001, 0.000001 });
            bsplineSettings.maximumStepLength = new DoubleList(new double[] { 100.0, 100.0, 100.0 });
            bsplineSettings.samplesDenominator = new IntList(new int[] { 5, 5, 5 });
            bsplineSettings.relaxationFactor = new DoubleList(new double[] { 0.9, 0.9, 0.9 });
            bsplineSettings.gradientMagnitudeTolerance = new DoubleList(Enumerable.Repeat(0.000000000000000000005, 3).ToArray());
            bsplineSettings.gridCellSize = new VectorR3dList(new VectorR3d[] { new VectorR3d(5.0), new VectorR3d(10.0), new VectorR3d(15.0) });
            bsplineSettings.gridCellSizeType = new CharList(new char[] { 'n', 'n', 'n' });

            orThrow(regOps.performBsplineRegistration(bsplineSettings));
            Console.WriteLine("done");

            // save the changes
            ValidOrThrow(regOps.saveRegistration(), regOps);
        }
    }
}
