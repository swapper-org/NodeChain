"""
Unit tests for the ETH package
"""

from eth import *


class TestEth:

    def test_ensureHash(self):
        assert "0xf69e658120a03fcabfc3d564da7034885c5701ad" == utils.ensureHash("F69e658120a03fcABfc3D564Da7034885c5701Ad")
