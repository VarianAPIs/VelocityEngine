# Velocity Scripting for Python (4.0.1.819)

## Installation

Velocity is packaged as a [Python wheel](https://pypi.org/project/wheel/) that 
you can install into your environment.  We currently require Python 2.7 and you 
must use the standard CPython interpreter.  We support Windows and MacOS.

To install, we recommend you create a [virtualenv](https://virtualenv.pypa.io/en/stable/) and 
then use `pip` to install.  You may need to install `pip` and `virtualenv` first.  
For example, on MacOS:

```bash
$ virtualenv velocity-env
New python executable in /Users/example/velocity-env/Scripts/python
Installing setuptools, pip, wheel...done.

$ source velocity-env/bin/activate

(velocity-env) $ pip install velocity-4.0.1.819-cp27-cp27m-macosx_10_12_intel.whl
Processing /Users/example/velocity-4.0.1.819-cp27-cp27m-macosx_10_12_intel.whl
Installing collected packages: velocity
Successfully installed velocity-velocity-4.0.1.819
```

Windows is similar except you use `activate.bat` in the `bin` folder instead of 
`source activate` to enable the virtualenv.

Once you've installed the wheel, you will be able to `import velocity` in scripts 
while the virtualenv is active.  You can find this README and some example scripts 
in your installation directory under `velocity-examples`, e.g. in this virtualenv 
example they will be found in `/Users/example/velocity-env/velocity-examples`.  If 
you are not using virtualenv, they will be found in your main Python installation.
The examples are also included in the archive this README comes in.

## Usage

To use, simply import the Velocity module in your scripts and create a `VelocityEngine`
instance:

```python
import velocity
e = velocity.VelocityEngine()
```

For more information, see the example scripts included with the installation and use 
the built-in class documentation, e.g. in the Python interpreter:

```python
>>> import velocity
>>> help(velocity) # for all the documentation
>>> help(velocity.VelocityEngine) # for a particular class
```

We recommend you follow this pattern to ensure logout when the process ends, to avoid 
leaving abandoned login sessions that will consume a license:

```python
import velocity
import atexit
e = velocity.VelocityEngine()
atexit.register(e.logout)
# the rest of your code here
```

