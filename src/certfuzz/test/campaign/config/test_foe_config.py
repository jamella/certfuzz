'''
Created on Apr 2, 2012

@organization: cert.org
'''
import unittest
from certfuzz.campaign.config.foe_config import Config
import os
import yaml
import tempfile
import shutil
#import pprint
from certfuzz.campaign.config import ConfigError
import logging

logger = logging.getLogger()
hdlr = logging.FileHandler(os.devnull)
logger.addHandler(hdlr)

class Test(unittest.TestCase):

    def _get_minimal_config(self):
        self.cfg_in = {'target': {'cmdline_template': '',
                                  'program': ''},
                       'runoptions': {}}
        fd, f = tempfile.mkstemp(suffix='.yaml', dir=self.tempdir, text=True)
        os.close(fd)
        with open(f, 'w') as fd:
            yaml.dump(self.cfg_in, fd)

        return Config(f)

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_empty_cfg_raises_exception(self):
        self.cfg_in = {}
        fd, f = tempfile.mkstemp(suffix='.yaml', dir=self.tempdir, text=True)
        os.close(fd)
        with open(f, 'w') as fd:
            yaml.dump(self.cfg_in, fd)

        self.assertRaises(KeyError, Config, f)

    def test_minimal_config(self):
        try:
            c = self._get_minimal_config()
        except Exception, e:
            self.fail('Exception on _get_minimal_config: %s' % e)

        self.assertTrue(c)

    def test_debugger_timeout_exceeds_runner(self):
        c = self._get_minimal_config()
        import itertools

        # no runner
        c.config.update({'runner': {'runner': None},
                         'debugger': {'runtimeout': 37}})
        c.validate()
        self.assertEqual(37, c.config['debugger']['runtimeout'])

        for (a, b) in itertools.product(range(10), range(10)):
            c.config.update({'runner': {'runner': 'foo', 'runtimeout': a},
                             'debugger': {'runtimeout': b}})
            self.assertEqual(a, c.config['runner']['runtimeout'])
            self.assertEqual(b, c.config['debugger']['runtimeout'])

            if a == 0 or b == 0:
                self.assertRaises(ConfigError, c.validate)
                continue
            c.validate()
            self.assertEqual(a, c.config['runner']['runtimeout'])
            expected = max(b, (2 * a))
            self.assertEqual(expected, c.config['debugger']['runtimeout'])

    def _counter(self):
        self.counter += 1

    def test_validation(self):
        c = self._get_minimal_config()
        self.counter = 0
        c.validations = [self._counter]
        for dummy in range(10):
            c.validate()
        self.assertEqual(10, self.counter)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
