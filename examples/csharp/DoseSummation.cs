using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Velocity.Examples {
    class DoseSummation {
        static void OrThrow(bool result, dynamic source) {
            if (!result)
                throw new Exception(source.getErrorMessage());
        }

        static void ValidOrThrow(PatientDataItem result, dynamic source) {
            if (!result.isValid())
                throw new System.Exception(source.getErrorMessage());
        }

        static Registration makeAutoReg(VelocityEngine e, Volume pVol, Volume sVol, String regName) {
            ValidOrThrow(e.loadPrimaryVolume(pVol.getVelocityId()), e);
            Console.WriteLine("Loaded primary volume: {0}", pVol.getName());
            ValidOrThrow(e.loadSecondaryVolume(sVol.getVelocityId()), e);
            Console.WriteLine("Loaded secondary volume: {0}", sVol.getName());

            // create registration
            var regOps = e.getRegistrationOperations();
            Console.WriteLine("Creating registration object: {0}", regName);
            var registration = regOps.createNewRegistration(regName);
            ValidOrThrow(registration, regOps);
            ValidOrThrow(e.loadRegistration(registration.getVelocityId()), e);

            Console.WriteLine("Running rigid registration ...");
            var rigidSettings = new DefaultRigidRegistrationSettings();
            OrThrow(regOps.performRigidRegistrationDICOM(rigidSettings), regOps);
         
            // save the changes
            ValidOrThrow(regOps.saveRegistration(), regOps);
            return registration;
        }

        static void Main(string[] args) {
            const string USER = "script";
            const string PASS = "script";
            const string WORKSTATION_PATH = @"C:\Velocity\Databases\WKS414";
            const string GRID_IP = "127.0.0.1";
            const int    GRID_PORT = 57000;
            const string GRID_DB = "vscDatabase";

            const string PATIENT_ID = "hyperarc";

            // connect to db
            var engine = new VelocityEngine();
            Action<bool> orThrow = result => OrThrow(result, engine);
            //orThrow(engine.loginToGrid(USER, PASS, GRID_IP, GRID_PORT, GRID_DB));
            orThrow(engine.loginToWorkstation(USER, PASS, WORKSTATION_PATH, true));
            AppDomain.CurrentDomain.ProcessExit += (source, data) => { engine.logout(); };

            var volOps = engine.getVolumeOperations();
            var patient = engine.loadPatientByPatientId(PATIENT_ID);
    
            ValidOrThrow(patient, engine);
            Console.WriteLine("Loaded patient: {0}", PATIENT_ID);

            //sort CTs ascending by AcquisitionDate
            var cts = patient.getVolumes("CT").OrderBy(o => o.getAcquisitionDate());
            var doses = patient.getVolumes("RTDOSE");

            // find all CT-DS in the same frame of reference
            //if multiple DS for same CT pick first one that has a plan
            var ctDosePair = new Dictionary<Volume, Volume>();
            Console.WriteLine("Finding CT-DS pairs to be resampled") ;
            foreach (Volume ct in cts) {
                var plans = ct.getLinkedPlans().ToList();
                foreach (Volume d in doses) {
                    if (d.getName() == "auto resampled" || d.getName() == "SUM RTDOSE") 
                        continue;
                    if (ct.getFrameOfReferenceUID() == d.getFrameOfReferenceUID()) {
                        ctDosePair[ct] = d;
                        bool hasPlan = plans.Exists(p => p.getInstanceUID() == d.getPlanUID());
                        if (hasPlan) break;
                    }
                }
            }

            //resample doses onto the most recent CT
            Console.WriteLine("Resampling DS onto most recent CT");
            var primaryCT = cts.Last(); // most recent by Acq Date
            var resampledDoses = new IntList(); // holds the ids of all doses to be summed
            var primaryDoseId = -1;

            foreach (Volume ct in ctDosePair.Keys) {
                var dose = ctDosePair[ct];
                if (ct.getVelocityId() != primaryCT.getVelocityId()) {
                    //need to load CT-DS to activate/create DICOM registration needed for chain
                    ValidOrThrow(engine.loadPrimaryVolume(ct.getVelocityId()), engine);
                    Console.WriteLine("Loaded CT {0} as primary", ct.getName());
                    ValidOrThrow(engine.loadSecondaryVolume(dose.getVelocityId()), engine);
                    Console.WriteLine("Loaded dose {0} as secondary", dose.getName());
                    var dicomReg = engine.loadRegistrationByName("DICOM");
                    ValidOrThrow(dicomReg, engine);

                    // make new reg for resampling between primary CT and secondary CT
                    var ct2ctReg = makeAutoReg(engine, primaryCT, ct, "resample_reg");

                    //now load primary CT and dose, load chain reg and resample onto primary CT
                    ValidOrThrow(engine.loadPrimaryVolume(primaryCT.getVelocityId()), engine);
                    Console.WriteLine("Loaded CT {0} as primary volume", primaryCT.getName());
                    ValidOrThrow(engine.loadSecondaryVolume(dose.getVelocityId()), engine);
                    Console.WriteLine("Loaded Dose id {0} as secondary volume", dose.getName());
                    //load registration resample_reg + DICOM
                    orThrow(engine.loadChainRegistration(ct2ctReg.getVelocityId(), dicomReg.getVelocityId()));
                    Console.WriteLine("Loaded registration resample_reg + DICOM");
                    Console.WriteLine("Creating resampled dose...");

                    var id = volOps.createResampledVolume(VolumeResampleOperation.VolumeResampleReplace, "auto resampled");
                    if (id == -1) {
                        Console.WriteLine("Error creating resampled dose {0}", volOps.getErrorMessage());
                        continue;
                    }

                    Console.WriteLine("Resampled dose created with id {0}", (id));
                    resampledDoses.Add(id);
                }
                else {
                    //this dose does not require resample, same FOR as primary CT
                    primaryDoseId = dose.getVelocityId();
                    resampledDoses.Add(primaryDoseId);
                }
            }

            Console.WriteLine("Summing {0} dose volumes ...", resampledDoses.Count());
            ValidOrThrow(engine.loadPrimaryVolume(primaryDoseId), engine);
            //load primary dose as anchor
            Console.WriteLine("Loaded DS id {0} as primary volume", primaryDoseId);
            int sumId = volOps.createResampledVolumeAggregate(VolumeResampleOperation.VolumeResampleAdd, resampledDoses, (int)ResampleFlags.Flags.AllowNone); // sum
            if (sumId == -1) {
                Console.WriteLine("Error creating sum dose {0}", volOps.getErrorMessage());
            }
            else {
                Console.WriteLine("Sum dose created with id {0}", sumId);
            }
        }
    }   
}
