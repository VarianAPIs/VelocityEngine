import setuptools
import os
import glob
import platform

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

with open("README.md", "r") as fh:
    long_description = fh.read()

# gather the libraries to include
libs = []
for match in ('dll', 'pyd', 'so'):
    libs += map(os.path.basename, glob.glob('velocity/*.{}'.format(match)))
if platform.system() == 'Darwin':
    libs += package_files('velocity/libs')
    libs += package_files('velocity/frameworks')

examples = glob.glob('examples/*.py')

package_data = libs

class BinaryDistribution(setuptools.Distribution):
    def has_ext_modules(self):
        return True
    def is_pure(self):
        return False

setuptools.setup(
    name="velocity",
    version="4.0.0.792",
    description="Velocity scripting for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    package_data={'velocity': package_data},
    data_files=[('velocity-examples', examples + ['README.md'])],
    python_requires='>=2.7,<3',
    classifiers=(
        "Programming Language :: Python :: 2",
    ),
    distclass=BinaryDistribution
)

