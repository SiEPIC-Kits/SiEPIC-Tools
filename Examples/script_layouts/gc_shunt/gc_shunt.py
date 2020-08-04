#%% import dependencies
cd_siepic = r"C:\Users\mhammood\Documents\GitHub\SiEPIC-Tools2\klayout_dot_config\python"
cd_pdk = r"C:\Users\mhammood\Documents\GitHub\SiEPIC-Tools2\klayout_dot_config\tech\GSiP"
pdk = 'GSiP'

#%% initialize imports
import sys, os
sys.path.append(cd_siepic); sys.path.append(cd_pdk)

try:
    import pya
except ImportError:
    import klayout.db as pya

from pya import Box, Trans, CellInstArray, Point, DPoint, Path

sys.path.append(cd_pdk+r"\pymacros")
from GSiP_Library import *
GSiP()
from SiEPIC.utils import arc_xy, get_technology_by_name
from siepic_tools.utils.tech import Tech
lib = get_technology_by_name(pdk, cd_pdk)
#%%create layout
ly = pya.Layout()
dbu = ly.dbu = 0.001
cell_top = ly.create_cell("Top")

#%%Define Layer mapping and floor plan
layer_Si220 = 'Si'
layer_floorplan = 'FloorPlan'
layer_text = 'Text'

LayerSiN = ly.layer(lib[layer_Si220])
fpLayerN = cell_top.layout().layer(lib[layer_floorplan])
TextLayerN = cell_top.layout().layer(lib[layer_text])
# Draw the floor plan
ly_height = 350
ly_width = 600
cell_top.shapes(fpLayerN).insert(Box(0,0, ly_width/dbu, ly_height/dbu))

#%%Import Grating couplers
GC_imported = ly.create_cell("Grating_Coupler_13deg_TE_1550_Oxide", pdk).cell_index()
gc_length = 41
GC_pitch = 127
t = Trans(Trans.R0, 0.5*ly_width/dbu, (0.5*ly_height-GC_pitch/2)/dbu)
cell_top.insert(CellInstArray(GC_imported, t, DPoint(0,GC_pitch).to_itype(dbu), Point(0,0), 2, 1))

#%%draw waveguide connecting grating couplers
path_pts = [[0,0], [0.5*ly_width+50,0], [0.5*ly_width+50, GC_pitch], [0,GC_pitch]]
path_pts = [Point(each[0], each[1]) for each in path_pts]
path = Path(); path.points = path_pts

from siepic_tools.utils.layout import layout_waveguide, layout_waveguide2
#layout_waveguide(cell_top, LayerSiN, path_pts, 0.5)

widths = [0.5,1]
layers = ['Si', 'DevRec']
offset = [0,0]
radius = 15
a = layout_waveguide2(lib, ly, cell_top, layers, widths, offset, path_pts, 15, 0,0)

cd_save = r"C:\Users\mhammood\scripts\scripted_layout"

os.chdir(cd_save)
ly.write("GSiP_loopback.gds")

# %%
