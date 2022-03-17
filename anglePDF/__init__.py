from __future__ import division
from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution("anglePDF").version
except DistributionNotFound:
    # package is not installed
    pass
