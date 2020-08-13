__version__ = '0.4'
#from . import install, extend, _globals, core, examples, github, lumerical, scripts, utils, setup
# from . import install, extend, _globals, core, examples, github, scripts, utils, setup
op_tag = "" #operation tag which defines whether we are loading library in script or GUI env

try:
    import pya
    if "Application" in str(dir(pya)):
        from SiEPIC.utils import get_technology_by_name
        op_tag = "GUI" 
    else:
        op_tag = "script"
except ImportError:
    import klayout.db as pya
    op_tag = "script"

from . import extend, _globals, core, github, scripts, utils, setup, install
import siepic_tools