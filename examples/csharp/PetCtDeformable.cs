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

            ValidOrThrow(engine.loadPatientByPatientId(PATIENT_ID), engine);
            Console.WriteLine("Loaded patient: {0}", PATIENT_ID);
            ValidOrThrow(engine.loadPrimaryVolumeByUID(PRIMARY_UID), engine);
            Console.WriteLine("Loaded primary volume: {0}", PRIMARY_UID);
            ValidOrThrow(engine.loadSecondaryVolumeByUID(SECONDARY_UID), engine);
            Console.WriteLine("Loaded secondary volume: {0}", SECONDARY_UID);

            // create registration
            var regOps = engine.getRegistrationOperations();
            Console.WriteLine("Creating registration object: {0}", REG_NAME);
            var registration = regOps.createNewRegistration(REG_NAME);
            ValidOrThrow(registration, regOps);
            ValidOrThrow(engine.loadRegistration(registration.getVelocityId()), engine);

            // first move the head into the right general area
            var manualSettings = new ManualRegistrationSettingsStructure();
            manualSettings.registrationMatrix = new MatrixR44d(1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, -8.1947, -275.0845, -394.5001, 1.0);
            orThrow(regOps.performManualAlignmentDICOM(manualSettings));

            Console.WriteLine("Running rigid registration ...");
            var rigidSettings = new RigidRegistrationSettingsStructure();

            rigidSettings.roiStart[0] = -102.021;
            rigidSettings.roiStart[1] = -74.7234;
            rigidSettings.roiStart[2] = -5.49291;
            rigidSettings.roiEnd[0] = 100.532;
            rigidSettings.roiEnd[1] = -410.341;
            rigidSettings.roiEnd[2] = -309.819;

            rigidSettings.primaryStartLevel = -110.02;
            rigidSettings.primaryEndLevel = 189.974;
            rigidSettings.secondaryStartLevel =  -125.014;
            rigidSettings.secondaryEndLevel = 224.998;

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

            OrThrow(regOps.performRigidRegistrationDICOM(rigidSettings), regOps);
            Console.WriteLine("done");

            // perform a deformable registration in the same area
            Console.WriteLine("Performing deformable registration...");
            var bsplineSettings = new BSplineDeformableRegistrationSettingsStructure();
            bsplineSettings.roiStart[0] = -102.021;
            bsplineSettings.roiStart[1] = -74.7234;
            bsplineSettings.roiStart[2] = -5.49291;
            bsplineSettings.roiEnd[0] = 100.532;
            bsplineSettings.roiEnd[1] = -410.341;
            bsplineSettings.roiEnd[2] = -309.819;

            bsplineSettings.primaryStartLevel = -110.02;
            bsplineSettings.primaryEndLevel = 189.974;
            bsplineSettings.secondaryStartLevel = -125.014;
            bsplineSettings.secondaryEndLevel = 224.998;

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

            OrThrow(regOps.performBsplineRegistrationDICOM(bsplineSettings), regOps);
            Console.WriteLine("done");

            // save the changes
            ValidOrThrow(regOps.saveRegistration(), regOps);
        }
    }
}
