# Changelog

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