using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Linq.Expressions;

namespace Velocity.Examples
{
    class BED
    {
        const string USER = "script";
        const string PASS = "script";

        const string WORKSTATION_PATH = @"C:\Velocity\Databases\vscDatabase";

        const string GRID_IP = "127.0.0.1";
        const int GRID_PORT = 57000;
        const string GRID_DB = "vscDatabase";

        const string PATIENT_ID = "10052012";
        const string PRIMARY_UID = "1.2.840.113619.2.55.3.278435321.302.1313753121.582";
        const string SECONDARY_UID = "1.2.246.352.71.7.1873493392.2486330.20110829091331";
        const string REG_NAME = "DICOM";
        const string STRUCT_1 = "Bladder";
        const string STRUCTSET_1UID = "1.2.276.0.7230010.3.1.4.1492057408.5156.1349471628.10";
        const int DEFAULT_ALPHABETA_TISSUE = 3;

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

            // load registration
            ValidOrThrow(engine.loadRegistrationByName(REG_NAME), engine);
            Console.WriteLine("Loaded registration: {0}", REG_NAME);

            var structure = engine.loadStructureByName(STRUCT_1, STRUCTSET_1UID);
            ValidOrThrow(structure, engine);
            Console.WriteLine("Loading existing structure: {0}", STRUCT_1);

            var structNames = new StringList(new string[] { STRUCT_1 });
            var structAlphaBetaRatio = new DoubleList(new double[] { 2, DEFAULT_ALPHABETA_TISSUE });
            var structUIDs = new StringList(new string[] { structure.getInstanceUID() });

            var vo = engine.getVolumeOperations();
            OrThrow(vo.createBEDoseByStructureUIDs(25, structNames, structUIDs, structAlphaBetaRatio) != -1, vo);
            Console.WriteLine("Biological Effective Dose created");
        }
    }
}