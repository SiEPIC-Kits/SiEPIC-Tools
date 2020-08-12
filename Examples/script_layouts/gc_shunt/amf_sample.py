cd_siepic = r"C:\Users\mhammood\Documents\GitHub\SiEPIC-Tools2\klayout_dot_config\python"
cd_pdk = r"C:\Users\mhammood\Documents\GitHub\SiEPIC-Tools2\klayout_dot_config\tech\GSiP"

#%% initialize imports
import sys, os
sys.path.append(cd_siepic); sys.path.append(cd_pdk)

try:
    import pya
except ImportError:
    import klayout.db as pya

from pya import Box, Trans, CellInstArray, Point, DPoint, Path, DPath

sys.path.append(cd_pdk+r"\pymacros")
from GSiP_Library import *
GSiP()
from SiEPIC.utils import arc_xy, get_technology_by_name
from siepic_tools.utils.tech import Tech
lib = get_technology_by_name(pdk, cd_pdk)