# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Various function and method decorators.'''

import warnings


class deprecated:
    '''A decorator to flag functionality as deprecated.'''

    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):

        def _wrapper(*args, **kwargs):
            warnings.warn(
                '%(function_name)s has been deprecated.' % {
                    'function_name': self.func.__name__ },
                DeprecationWarning)
            return self.func(*args, **kwargs)

        return _wrapper(*args, **kwargs)

