using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Linq.Expressions;

namespace Velocity.Examples
{
    class StructureMetrics
    {
        const string USER = "script";
        const string PASS = "script";

        const string WORKSTATION_PATH = @"C:\Velocity\Databases\vscDatabase";

        const string GRID_IP = "127.0.0.1";
        const int GRID_PORT = 57000;
        const string GRID_DB = "vscDatabase";

        const string PATIENT_ID = "AW3Y6TA684";
        const string PRIMARY_UID = "1.3.12.2.1107.5.1.4.54841.30000011071412175920300003025";
        const string SECONDARY_UID = "1.2.246.352.61.2.4621874044879001489.17114159699319862401";
        const string DEFORMABLE_NAME = "CBCT MULTI";
        const string RIGID_NAME = "RIGID";

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
            ValidOrThrow(engine.loadRegistrationByName(DEFORMABLE_NAME), engine);
            Console.WriteLine("Loaded registration: {0}", DEFORMABLE_NAME);


            var rops = engine.getRegistrationOperations();
            var sops = engine.getStructureOperations();

            var primaryVolume = engine.getPrimaryVolume();
            var secondaryVolume = engine.getSecondaryVolume();

            // find an external structure
            StructureSet primarySet = primaryVolume.getStructureSets().Where(ss => ss.getName() == "Original SIM").First();
            Structure structure = primarySet.getStructures().Where(s => s.getName() == "Mandible").First();
            Console.WriteLine("Using structure '{0}' from structure set '{1}'", structure.getName(), primarySet.getName());

            // create a new structure set on the secondary volume
            string targetSetName = DateTime.UtcNow.ToString("s", System.Globalization.CultureInfo.InvariantCulture).Substring(0, 16);
            var targetSet = sops.createStructureSet(targetSetName, false);
            ValidOrThrow(targetSet, sops);

            // copy the external to the new structure set
            Console.WriteLine("Copying structure to secondary...");
            var structureIds = new IntList(new int[] { structure.getVelocityId() });
            var newStructures = sops.copyStructuresToSecondary(structureIds, targetSet.getVelocityId());

            // IMPORTANT: call save after finishing a set of modifications to a structure set
            targetSet = sops.saveStructureSet(targetSet.getVelocityId());
            
            OrThrow(newStructures.Count == 1, sops);
            var newStructure = newStructures.First().Value;

            Action metrics = delegate () {
                var c = sops.conformality(structure.getVelocityId(), newStructure.getVelocityId());
                Console.WriteLine("Conformality: {0}", c);
                if (c < 0.0) {
                    Console.WriteLine("Error: {0}", sops.getErrorMessage());
                }

                var mets = sops.surfaceDistanceMetrics(structure.getVelocityId(), newStructure.getVelocityId());
                if (!mets.isValid) { 
                    Console.WriteLine("Error: {0}", sops.getErrorMessage());
                } else {
                    Console.WriteLine("Metrics: Hausdorff={0}, min={1}, median={2}, mean={3}, stddev={4}",
                        mets.hausdorffDistance, mets.min, mets.median, mets.mean, mets.standardDeviation);
                }
            };

            // show metrics on registration used for copying
            metrics();

            // now on an alternative registration
            ValidOrThrow(engine.loadRegistrationByName(RIGID_NAME), engine);
            Console.WriteLine("Loaded registration: {0}", RIGID_NAME);
            metrics();
        }
    }
}