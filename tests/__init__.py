"""Test suites. Every temporary folder a test makes (rendered songs, stems, sound libraries) goes into one scratch
folder for the run, which is deleted when the run ends - so test runs don't pile up gigabytes of WAVs in the temp dir."""
import atexit
import shutil
import tempfile

_RUN_DIR = tempfile.mkdtemp(prefix='studiolab-tests-')
tempfile.tempdir = _RUN_DIR
atexit.register(shutil.rmtree, _RUN_DIR, True)
