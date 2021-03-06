'''
Created on Apr 12, 2011

@organization: cert.org
'''
import logging
import os

from .directory import Directory
from ..fuzztools import filetools
from .seedfile import SeedFile, SeedFileError
from ..scoring.scorable_set import ScorableSet2, EmptySetError
logger = logging.getLogger(__name__)

class SeedfileSet(ScorableSet2):
    '''
    classdocs
    '''
    def __init__(self, campaign_id=None, originpath=None, localpath=None,
                 outputpath='.', logfile=None, datafile=None):
        '''
        Constructor
        '''

        if not datafile:
            datafile = os.path.join(outputpath, 'seedfile_set_data.csv')

        super(self.__class__, self).__init__(datafile=datafile)

        self.campaign_id = campaign_id
        self.seedfile_output_base_dir = outputpath

        self.originpath = originpath
        self.localpath = localpath
        # TODO: merge self.outputpath with self.seedfile_output_base_dir
        self.outputpath = outputpath

        self.origindir = None
        self.localdir = None
        self.outputdir = None

        if logfile:
            hdlr = logging.FileHandler(logfile)
            logger.addHandler(hdlr)

        logger.debug('SeedfileSet output_dir: %s', self.seedfile_output_base_dir)

    def __enter__(self):
        self._setup()
        return self

    def __exit__(self, etype, value, traceback):
        pass

    def _setup(self):
        self._set_directories()
        self._copy_files_to_localdir()
        self._add_local_files_to_set()

    def _set_directories(self):
        if self.originpath:
            self.origindir = Directory(self.originpath)
        if self.localpath:
            self.localdir = Directory(self.localpath, create=True)
        if self.outputpath:
            self.outputdir = Directory(self.outputpath, create=True)

    def _copy_files_to_localdir(self):
        for f in self.origindir:
            self.copy_file_from_origin(f)

    def _add_local_files_to_set(self):
        self.localdir.refresh()
        files_to_add = [f.path for f in self.localdir]
        self.add_file(*files_to_add)

    def add_file(self, *files):
        for f in files:
            try:
                seedfile = SeedFile(self.seedfile_output_base_dir, f)
            except SeedFileError:
                logger.warning('Skipping empty file %s', f)
                continue
            logger.info('Adding file to set: %s', seedfile.path)
            self.add_item(seedfile.md5, seedfile)

    def copy_file_from_origin(self, f):
        if (os.path.basename(f.path) == '.DS_Store'):
            return 0

        # convert the local filenames from <foo>.<ext> to <md5>.<ext>
        basename = 'sf_' + f.md5 + f.ext
        targets = [os.path.join(d, basename) for d in (self.localpath, self.outputpath)]
        filetools.copy_file(f.path, *targets)
        for target in targets:
            filetools.make_writable(target)
        return 1

    def paths(self):
        for x in self.things.values():
            yield x.path

    def next_item(self):
        '''
        Returns a seedfile object selected per the scorable_set object.
        Verifies that the seedfile exists, and removes any nonexistent
        seedfiles from the set
        '''
        if not len(self.things):
            raise EmptySetError

        while len(self.things):
            logger.debug('Thing count: %d', len(self.things))
            # continue until we find one that exists, or else the set is empty
            sf = ScorableSet2.next_item(self)
            if sf.exists():
                # it's still there, proceed
                return sf
            else:
                # it doesn't exist, remove it from the set
                logger.warning('Seedfile no longer exists, removing from set: %s', sf.path)
                self.del_item(sf.md5)


    def __setstate__(self, state):
        newstate = state.copy()

        # copy out old things and replace with an empty dict
        oldthings = newstate.pop('things')
        newstate['things'] = {}

        # refresh the directories
        self.__dict__.update(newstate)
        self._setup()

        # clean up things that no longer exist
        self.sfcount = 0
        self.sfdel = 0
        for k, old_sf in oldthings.iteritems():
            # update the seedfiles for ones that are still present
            if k in self.things:
#                print "%s in things..." % k
                self.things[k].__setstate__(old_sf)
                self.sfcount += 1

    def __getstate__(self):
        state = ScorableSet2.__getstate__(self)

        # remove things we can recreate
        try:
            for k in ('origindir', 'localdir', 'outputdir'):
                del state[k]
        except KeyError:
            # it's ok if they don't exist
            pass

        return state
