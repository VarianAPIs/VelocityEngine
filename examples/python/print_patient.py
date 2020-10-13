
import velocity
import sys
import atexit

DB_NAME = r'vscDatabase'
DB_USER = 'script'
DB_PASS = 'script'
# if workstation
DB_PATH = r'/Velocity/Databases/vscDatabase'
# if grid
DB_IP = '127.0.0.1'
DB_PORT = 57000

# assumes "sixCBCT, AdaptiveMonitoring" patient loaded by default
PATIENT_ID = 'AW3Y6TA684'

# optional patient id argument
patientId = sys.argv[1] if len(sys.argv) > 1 else PATIENT_ID

e = velocity.VelocityEngine()
def orThrow(c, e=e):
  if not c or (hasattr(c, 'isValid') and not c.isValid()):
    raise RuntimeError(e.getErrorMessage())

#orThrow(e.loginToWorkstation(DB_USER, DB_PASS, DB_PATH, True))
orThrow(e.loginToGrid(DB_USER, DB_PASS, DB_IP, DB_PORT, DB_NAME))
atexit.register(e.logout) # ensure we log out when the script ends

pops = e.getPatientDataOperations()
patient = pops.getPatientByPatientId(patientId)
orThrow(patient, pops)

def compare_key(obj_and_name):
  """Compare objects for printing.  We consider 
  wrapped lists (having size()) to come after anything else, 
  otherwise sort by name.
  """
  obj, obj_name = obj_and_name
  return (hasattr(obj, 'size'), obj_name)

def print_object(obj, obj_name, indent=0, seen_ids=None):
  """Recursively prints an object.
  @param obj       the object to print
  @param obj_name  the object name used when printing
  @param indent    indentation level, for internal use
  @param seen_ids  infinite recursion prevention, for internal use
  """
  pre = '-' * indent
  if seen_ids is None:
    seen_ids = set()
  # for std::vector wrappers
  if hasattr(obj, 'size'):
    # print the name, then each child, e.g. 'obj', then 'obj[0]', 'obj[1]', etc
    print('{}{} [{} elements]:'.format(pre, obj_name, obj.size()))
    for i, child in enumerate(obj):
      child_name = obj_name + '[' + str(i) + ']'
      print_object(child, child_name, indent + 1, seen_ids)
  # for non-API types
  elif not hasattr(obj, 'this'):
    # print the name and value
    print('{}{}: {}'.format(pre, obj_name, obj))
  # for all other API types
  else:
    # prevent infinite loop by checking for already seen objects
    seen_id = (repr(type(obj)), obj.getVelocityId())
    if seen_id in seen_ids:
      print('{}{}: {}'.format(pre, obj_name, "[ALREADY SEEN]"))
    else:
      # remember that we saw this one
      seen_ids.add(seen_id)

      # get all the data inspection functions and call them
      try:
        children = [ (getattr(obj, attr)(), attr) for attr in dir(obj) if (attr.startswith('get') or attr.startswith('is')) and attr not in ('this', 'getRecord') ]
        # sort to get primitives before child lists
        children.sort(key=compare_key)
        # now recurse to all the children
        for child, attr in children:
          child_name = obj_name + '.' + attr + '()'
          print_object(child, child_name, indent + 1, seen_ids)
      except:
        print('Problem with object: {} (attrs={})'.format(obj, dir(obj)))


print_object(patient, 'patient')
