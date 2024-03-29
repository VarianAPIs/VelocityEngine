# Changelog

## [4.1.4.1217] - 2022-03-08
### Added
PlanOperations: 
- Container plan creation.

StructureOperations: 
- Structure delete.
- Structure set creation with External contour.

PatientDataOperations
- Delete volumes, registrations, structure sets, plans.

### Changed
- Fix Issue #15 - crop and smooth parameter documentation.
- Fix Issue #19 - enforce volume match for load registration.
- ROI box fix - don't require a particular order for the corner points.
- Mac build for Python 3.9.

## [4.1.4.1216] - 2021-06-02
### Added
- Dose summation example script.

### Changed
- Build against released Velocity 4.1.4.

## [4.1.2.1199] - 2020-10-09

### Added
- Adaptive plan creation.
- Chain registration loading.
- Default Settings for rigid and deformable registrations.
 
### Changed
- BED functions, examples, and documentation updated.
- Fix Issue #8 - structure mask for secondary structure.
- Fix Issue #7 - hang on script exit for Windows.
- C# example fixes.
- Python guide updates.

## [4.1.2.1197] - 2020-06-10
### Changed
- Fixed missing dependency DLL for C#.

## [4.1.2.1194] - 2020-03-12
### Changed
- Build against released Velocity 4.1.2.

## [4.1.1.1184] - 2020-03-11
### Changed
- Build against released Velocity 4.1.1.

## [4.1.0.1145] - 2020-03-11
### Added
- Python 3 support.

### Changed
- Build against released Velocity 4.1.0.
- Examples converted to Python 3.

### Removed
- Python 2 support.

## [4.0.1.822] - 2019-06-13
### Added
- Functions to get bounds of structures and intersections between volumes.  Can be used as ROI for registration operations.

### Changed
- Updated inline documentation.
- Updated Python user guide.
- Updated examples to use `DICOM` versions of registration operations, see removals below.

### Removed
- `RegistrationOperations` which use Velocity-internal coordinate systems:
  - `performRigidRegistration`
  - `performBSplineRegistration`
  - `performManualAlignment`
- Use the `DICOM` suffixed versions of the above.
- Removed unused type for structure guided.

 
## [4.0.1.820] - 2019-05-09
### Added
- Support for burn-in structure-guided deformable image registration.
- Python user guide.

### Changed
- Build against released Velocity 4.0.1.


## [4.0.0.793] - 2018-07-27
### Added
- Build of scripting APIs against Velocity 4.0.0.
- Examples in Python and C#. 
