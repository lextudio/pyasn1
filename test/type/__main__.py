#
# This file is part of pyasn1 software.
#
# Copyright (c) 2005-2017, Ilya Etingof <etingof@gmail.com>
# License: http://pyasn1.sf.net/license.html
#
try:
    import unittest2 as unittest

except ImportError:
    import unittest

suite = unittest.TestLoader().loadTestsFromNames(
    ['test.type.test_constraint.suite',
     'test.type.test_namedtype.suite',
     'test.type.test_namedval.suite',
     'test.type.test_tag.suite',
     'test.type.test_univ.suite']
)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)