'''
Created on Apr 15, 2011

@organization: cert.org
'''

import unittest
import tempfile
import os
from certfuzz.file_handlers.seedfile import SeedFile
from pprint import pprint
from certfuzz.fuzztools.rangefinder import RangeFinder

class Test(unittest.TestCase):

    def setUp(self):
        (fd, self.file) = tempfile.mkstemp()
        self.dir = tempfile.mkdtemp()
        self.content = "I'm here and I'm ready. They're not. Bring it."
        os.write(fd, self.content)
        os.close(fd)
        self.sf = SeedFile(self.dir, self.file)

    def tearDown(self):
        os.remove(self.file)
        assert not os.path.exists(self.file)

    def test_init(self):
        self.assertEqual(self.sf.output_dir, os.path.join(self.dir, self.sf.md5))

    def test_record_hit(self):
        self.assertEqual(0, self.sf.successes)
        self.assertFalse('x' in self.sf.seen)
        self.sf.record_success('x')
        self.assertEqual(1, self.sf.successes)
        self.assertTrue('x' in self.sf.seen)

    def test_getstate(self):
        self.assertEqual(RangeFinder, type(self.sf.rangefinder))
        state = self.sf.__getstate__()
        self.assertEqual(dict, type(state))
        self.assertEqual(dict, type(state['rangefinder']))

    def test_setstate(self):
        state = self.sf.__getstate__()

        self.assertEqual(0, self.sf.tries)
        self.assertEqual(0, state['tries'])

        # can we change something?
        state['tries'] = 1000
        self.sf.__setstate__(state)
        self.assertEqual(1000, self.sf.tries)
        # make sure we restore rangefinder
        self.assertEqual(RangeFinder, type(self.sf.rangefinder))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
