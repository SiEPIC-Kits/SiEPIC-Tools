#################################################################################
#                SiEPIC Class Extension of Path & DPath Class                   #
#################################################################################

# Function Definitions
#################################################################################
'''
pya.Path and pya.DPath Extensions:
  - get_points(), returns list of pya.Points
  - get_dpoints(), returns list of pya.DPoints
  - is_manhattan(), tests to see if the path is manhattan
  - is_manhattan_endsegments(), tests to see if the path is manhattan (only the 1st and last segments)
  - radius_check(radius), tests to see of all path segments are long enough to be
    converted to a waveguide with bends of radius 'radius'
  - remove_colinear_points(), removes all colinear points in place
  - unique_points(), remove all but one colinear points
  - translate_from_center(offset), returns a new path whose points have been offset
    by 'offset' from the center of the original path

'''
import pya


def patch_path(Path_Klass):
    def to_dtype(self, dbu):
        Dpath = pya.DPath(self.get_dpoints(), self.width) * dbu
        Dpath.width = self.width * dbu
        return Dpath

    def to_itype(self, dbu):
        path = pya.Path([pt.to_itype(dbu) for pt in self.each_point()], round(self.width / dbu))
        path.width = round(self.width / dbu)
        return path

    def get_points(self):
        return [pya.Point(pt.x, pt.y) for pt in self.each_point()]

    def get_dpoints(self):
        return [pya.DPoint(pt.x, pt.y) for pt in self.each_point()]

    def is_manhattan_endsegments(self):
        if self.__class__ == pya.Path:
            pts = self.get_points()
        else:
            pts = self.get_dpoints()
        check = 1 if len(pts) == 2 else 0
        for i, pt in enumerate(pts):
            if (i == 1 or pts[i] == pts[-1]):
                if(pts[i].x == pts[i - 1].x or pts[i].y == pts[i - 1].y):
                    check += 1
        return check == 2


    def is_manhattan(self):
        if self.__class__ == pya.Path:
            pts = self.get_points()
        else:
            pts = self.get_dpoints()
        if len(pts) == 2:
            return True
            
        # check that each segment is horizontal or vertical:
        for i, pt in enumerate(pts[0:-1]):
            if not (pts[i].x == pts[i + 1].x or pts[i].y == pts[i + 1].y):
                return False

        # check that all corners are 90 degrees (not 180):
        from SiEPIC.utils import inner_angle_b_vectors
        for i in range(1, len(pts)-1):
            if ((inner_angle_b_vectors(pts[i]-pts[i-1],pts[i+1]-pts[i])+90)%360-90) != 90:
                return False
        return True

    def radius_check(self, radius):
        def all2(iterable):
            for element in iterable:
                if not element:
                    return False
            return True

        points = self.get_points()
        
        if len(points) > 2:
            lengths = [points[i].distance(points[i - 1]) for i, pt in enumerate(points) if i > 0]
            # first and last segment must be >= radius
            check1 = (lengths[0] >= radius)
            check2 = (lengths[-1] >= radius)
            # middle segments must accommodate two bends, hence >= 2 radius
            check3 = [length >= 2 * radius for length in lengths[1:-1]]
            return check1 and check2 and all(check3)
        else:
            return True

            
    def remove_colinear_points(self, verbose=False):
        """ remove all but 1 colinear point """
        from SiEPIC.utils import pt_intersects_segment, angle_b_vectors, angle_vector
        if self.__class__ == pya.Path:
            pts = self.get_points()
        else:
            pts = self.get_dpoints()

        for i in range(1,len(pts)-1):
            turn = ((angle_b_vectors(pts[i]-pts[i-1],pts[i+1]-pts[i])+90)%360-90)/90
            angle = angle_vector(pts[i]-pts[i-1])/90
            if verbose:
                print('%s, %s' %(turn, angle))

        # this version removed all colinear points, which doesn't make sense for a path
        self.points = [pts[0]] + [pts[i]
                                for i in range(1, len(pts) - 1) if not pt_intersects_segment(pts[i + 1], pts[i - 1], pts[i])] + [pts[-1]]
        return self


    def unique_points(self):
        if self.__class__ == pya.Path:
            pts = self.get_points()
        else:
            pts = self.get_dpoints()

        # only keep unique path points:
        output = []
        for pt in pts:
            if pt not in output:
                output.append(pt)
        self.points = output
        return self


    def translate_from_center(self, offset):
        from math import pi, cos, sin, acos, sqrt
        from .utils import angle_vector
        pts = [pt for pt in self.get_dpoints()]
        tpts = [pt for pt in self.get_dpoints()]
        for i in range(0, len(pts)):
            if i == 0:
                u = pts[i] - pts[i + 1]
                v = -u
            elif i == (len(pts) - 1):
                u = pts[i - 1] - pts[i]
                v = -u
            else:
                u = pts[i - 1] - pts[i]
                v = pts[i + 1] - pts[i]

            if offset < 0:
                o1 = pya.DPoint(abs(offset) * cos(angle_vector(u) * pi / 180 - pi / 2),
                                abs(offset) * sin(angle_vector(u) * pi / 180 - pi / 2))
                o2 = pya.DPoint(abs(offset) * cos(angle_vector(v) * pi / 180 + pi / 2),
                                abs(offset) * sin(angle_vector(v) * pi / 180 + pi / 2))
            else:
                o1 = pya.DPoint(abs(offset) * cos(angle_vector(u) * pi / 180 + pi / 2),
                                abs(offset) * sin(angle_vector(u) * pi / 180 + pi / 2))
                o2 = pya.DPoint(abs(offset) * cos(angle_vector(v) * pi / 180 - pi / 2),
                                abs(offset) * sin(angle_vector(v) * pi / 180 - pi / 2))

            p1 = u + o1
            p2 = o1
            p3 = v + o2
            p4 = o2
            d = (p1.x - p2.x) * (p3.y - p4.y) - (p1.y - p2.y) * (p3.x - p4.x)

            if round(d, 10) == 0:
                tpts[i] += p2
            else:
                tpts[i] += pya.DPoint(((p1.x * p2.y - p1.y * p2.x) * (p3.x - p4.x) - (p1.x - p2.x) * (p3.x * p4.y - p3.y * p4.x)) / d,
                                     ((p1.x * p2.y - p1.y * p2.x) * (p3.y - p4.y) - (p1.y - p2.y) * (p3.x * p4.y - p3.y * p4.x)) / d)

        if self.__class__ == pya.Path:
            return pya.Path([pya.Point(pt.x, pt.y) for pt in tpts], self.width)
        elif self.__class__ == pya.DPath:
            return pya.DPath(tpts, self.width)


    Path_Klass.to_dtype = to_dtype
    Path_Klass.to_itype = to_itype
    Path_Klass.get_points = get_points
    Path_Klass.get_dpoints = get_dpoints
    Path_Klass.is_manhattan_endsegments = is_manhattan_endsegments
    Path_Klass.is_manhattan = is_manhattan
    Path_Klass.radius_check = radius_check
    Path_Klass.remove_colinear_points = remove_colinear_points
    Path_Klass.unique_points = unique_points
    Path_Klass.translate_from_center = translate_from_center
    #pya.Path.snap = snap
    #pya.Path.snap_m = snap_m # function added by Karl McNulty (RIT) for metal pin functionality

# Path Extension
patch_path(pya.Path)

# DPath Extension
patch_path(pya.DPath)
