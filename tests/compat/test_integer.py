#
# This file is part of pyasn1 software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pyasn1/license.html
#
import sys

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from tests.base import BaseTestCase

from pyasn1.compat import integer


class IntegerTestCase(BaseTestCase):
    def test_from_bytes_zero(self):
        assert 0 == integer.from_bytes(bytes([0]), signed=False)

    def test_from_bytes_unsigned(self):
        assert -66051 == integer.from_bytes(bytes([254, 253, 253]), signed=True)

    def test_from_bytes_signed(self):
        assert 66051 == integer.from_bytes(bytes([0, 1, 2, 3]), signed=False)

    def test_from_bytes_empty(self):
        assert 0 == integer.from_bytes(bytes([]))


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite)
