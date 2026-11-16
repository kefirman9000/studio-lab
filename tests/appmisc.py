"""Problem report (redaction, sections) and the app-window helpers - no network, no GUI."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sgcore import diagnostics, appwindow  # noqa: E402


def main():
    home = os.path.expanduser('~')
    t = diagnostics.redact(f'{home}/x a@b.com ' + 'ab' * 32 + ' key=ABCDEFGHIJKLMNOPQRSTUV')
    assert home not in t and 'a@b.com' not in t and 'ab' * 32 not in t and 'ABCDEFGHIJKLMNOP' not in t, t
    jobs = {'j1': dict(status='error', error='boom', started=1.0, items=[{'options': {'style': 'trance', 'seed': 3}}], results=[],
                       log=['Traceback (most recent call last): ...']),
            'j2': dict(status='done', started=2.0, items=[], results=[{'warnings': ['lead: plugin failed']}], log=[])}
    r = diagnostics.build(jobs, 'it broke')
    for want in ('STUDIO LAB PROBLEM REPORT', 'it broke', '=== Versions', '=== Sound libraries', '=== Plugins',
                 'ERROR: boom', 'trance seed 3', 'warning: lead: plugin failed', '=== Recent log'):
        assert want in r, want
    appwindow.find_browser()                     # never raises, whatever is installed
    print('ok  problem report + redaction, app window helpers')
    print('all good')


if __name__ == '__main__':
    main()
