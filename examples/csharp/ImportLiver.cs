using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Velocity.Examples {
    class Program {
        const string USER = "script";
        const string PASS = "script";
        const string WORKSTATION_PATH = @"C:\Velocity\Databases\vscDatabase";

        const string GRID_IP = "127.0.0.1";
        const int GRID_PORT = 57000;
        const string GRID_DB = "vscDatabase";

        const string LIVER_PATIENT_ID = "0045";
        const string LIVER_IMPORT_DIR = @"C:\demodata\SPECT, Liver";

        /**
         * Convenience function to test loading a patient and listing the associated volume UIDS.
         */
        static void loadAndListVolumes(VelocityEngine engine, string patientId) {
            if (!engine.loadPatientByPatientId(patientId).isValid()) {
                Console.WriteLine("Could not load patient id {0}, error: {1}", patientId, engine.getErrorMessage());
            } else {
                var volumeIds = engine.getPatientVolumeUIDs(patientId);
                Console.WriteLine("Patient id {0} has volume UIDs: {1}", patientId, String.Join(", ", volumeIds));
            }
        }

        static void Main(string[] args) {
            // connect to the grid
            var engine = new VelocityEngine();
            if (!engine.loginToWorkstation(USER, PASS, WORKSTATION_PATH, true)) { 
            //if (!engine.loginToGrid(USER, PASS, GRID_IP, GRID_PORT, GRID_DB)) {
                throw new System.Exception(engine.getErrorMessage());
            }
            AppDomain.CurrentDomain.ProcessExit += (source, data) => { engine.logout(); };

            // try to list liver patient volumes
            loadAndListVolumes(engine, LIVER_PATIENT_ID);

            var importOps = engine.getImportOperations();

            Console.WriteLine("Importing SPECT, Liver ...");
            if (importOps.importDirectory(LIVER_IMPORT_DIR, true)) {
                Console.WriteLine("Successfully imported.");
            } else {
                Console.WriteLine("Import error: {0}", importOps.getErrorMessage());
            }

            // try again to list the volumes for the liver patient
            loadAndListVolumes(engine, LIVER_PATIENT_ID);
        }
    }
}
