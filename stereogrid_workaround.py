import os
import sys
import subprocess
import tempfile
import numpy as np
import matplotlib.pyplot as plt
from apsg import Group, Vec3
from apsg.helpers import (
    KentDistribution,
    sind,
    cosd,
    acosd,
    asind,
    atand,
    atan2d,
    angle_metric,
    l2v,
    getldd,
    _linear_inverse_kamb,
    _square_inverse_kamb,
    _schmidt_count,
    _kamb_count,
    _exponential_kamb,
)
import matplotlib.tri as tri

class StereoGrid(object):
    """
    Workaround implemented as qhull fails when called from
    within QGIS python in ubuntu 18.04, QGIS 3.4 :-( 

    """

    def __init__(self, d=None, **kwargs):
        self.initgrid(**kwargs)
        if d:
            assert isinstance(d, Group), "StereoGrid need Group as argument"
            self.calculate_density(np.asarray(d), **kwargs)

    def __repr__(self):
        return (
            "StereoGrid with %d points.\n" % self.n +
            "Maximum: %.4g at %s\n" % (self.max, self.max_at) +
            "Minimum: %.4g at %s" % (self.min, self.min_at)
        )

    @property
    def min(self):
        return self.values.min()

    @property
    def max(self):
        return self.values.max()

    @property
    def min_at(self):
        return Vec3(self.dcgrid[self.values.argmin()]).aslin

    @property
    def max_at(self):
        return Vec3(self.dcgrid[self.values.argmax()]).aslin

    def _buildtrig_workaround( self, x, y ):
        tfh, tfname = tempfile.mkstemp('.npy', 'tmp_contour_generator')
        tfh2, tfname2 = tempfile.mkstemp('.npy', 'tmp_contour_generator')
        os.close(tfh)
        os.close(tfh2)
        trig = None
        try:
            np.save(tfname, np.vstack((x,y)))
            pydir = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
            pyscript = os.path.join(pydir, 'buildtrig_qhull_workaround.py')
            python = sys.executable
            result = subprocess.call([python, pyscript, tfname, tfname2])
            triangles = np.load(tfname2)
            trig = tri.Triangulation(x, y, triangles)
        finally:
            os.remove(tfname)
            os.remove(tfname2)
        return trig

    def initgrid(self, **kwargs):
        # parse options
        grid = kwargs.get("grid", "radial")
        if grid == "radial":
            ctn_points = int(
                np.round(np.sqrt(kwargs.get("npoints", 1800)) / 0.280269786)
            )
            # calc grid
            self.xg = 0
            self.yg = 0
            for rho in np.linspace(0, 1, int(np.round(ctn_points / 2 / np.pi))):
                theta = np.linspace(0, 360, int(np.round(ctn_points * rho + 1)))[:-1]
                self.xg = np.hstack((self.xg, rho * sind(theta)))
                self.yg = np.hstack((self.yg, rho * cosd(theta)))
        elif grid == "ortho":
            n = int(np.round(np.sqrt(kwargs.get("npoints", 1800) - 4) / 0.8685725142))
            x, y = np.meshgrid(np.linspace(-1, 1, n), np.linspace(-1, 1, n))
            d2 = (x ** 2 + y ** 2) <= 1
            self.xg = np.hstack((0, 1, 0, -1, x[d2]))
            self.yg = np.hstack((1, 0, -1, 0, y[d2]))
        else:
            raise TypeError("Wrong grid type!")
        self.dcgrid = l2v(*getldd(self.xg, self.yg)).T
        self.n = self.dcgrid.shape[0]
        self.values = np.zeros(self.n, dtype=np.float)
        self.triang = self._buildtrig_workaround(self.xg, self.yg)

    def calculate_density(self, dcdata, **kwargs):
        """Calculate density of elements from ``Group`` object.

        """
        # parse options
        sigma = kwargs.get("sigma", 1 / len(dcdata) ** (-1 / 7))
        weighted = kwargs.get("weighted", False)
        method = kwargs.get("method", "exp_kamb")
        trim = kwargs.get("trim", False)

        func = {
            "linear_kamb": _linear_inverse_kamb,
            "square_kamb": _square_inverse_kamb,
            "schmidt": _schmidt_count,
            "kamb": _kamb_count,
            "exp_kamb": _exponential_kamb,
        }[method]

        # weights are given by euclidean norms of data
        if weighted:
            weights = np.linalg.norm(dcdata, axis=1)
            weights /= weights.mean()
        else:
            weights = np.ones(len(dcdata))
        for i in range(self.n):
            dist = np.abs(np.dot(self.dcgrid[i], dcdata.T))
            count, scale = func(dist, sigma)
            count *= weights
            self.values[i] = (count.sum() - 0.5) / scale
        if trim:
            self.values[self.values < 0] = 0

    def apply_func(self, func, *args, **kwargs):
        """Calculate values using function passed as argument.
        Function must accept vector (3 elements array) as argument
        and return scalar value.

        """
        for i in range(self.n):
            self.values[i] = func(self.dcgrid[i], *args, **kwargs)

    def contourf(self, *args, **kwargs):
        """ Show filled contours of values."""
        fig, ax = plt.subplots(figsize=settings["figsize"])
        # Projection circle
        ax.text(0, 1.02, "N", ha="center", va="baseline", fontsize=16)
        ax.add_artist(plt.Circle((0, 0), 1, color="w", zorder=0))
        ax.add_artist(plt.Circle((0, 0), 1, color="None", ec="k", zorder=3))
        ax.set_aspect("equal")
        plt.tricontourf(self.triang, self.values, *args, **kwargs)
        plt.colorbar()
        plt.axis('off')
        plt.show()

    def contour(self, *args, **kwargs):
        """ Show contours of values."""
        fig, ax = plt.subplots(figsize=settings["figsize"])
        # Projection circle
        ax.text(0, 1.02, "N", ha="center", va="baseline", fontsize=16)
        ax.add_artist(plt.Circle((0, 0), 1, color="w", zorder=0))
        ax.add_artist(plt.Circle((0, 0), 1, color="None", ec="k", zorder=3))
        ax.set_aspect("equal")
        plt.tricontour(self.triang, self.values, *args, **kwargs)
        plt.colorbar()
        plt.axis('off')
        plt.show()

    def plotcountgrid(self):
        """ Show counting grid."""
        fig, ax = plt.subplots(figsize=settings["figsize"])
        # Projection circle
        ax.text(0, 1.02, "N", ha="center", va="baseline", fontsize=16)
        ax.add_artist(plt.Circle((0, 0), 1, color="w", zorder=0))
        ax.add_artist(plt.Circle((0, 0), 1, color="None", ec="k", zorder=3))
        ax.set_aspect("equal")
        plt.triplot(self.triang, "bo-")
        plt.axis('off')
        plt.show()

