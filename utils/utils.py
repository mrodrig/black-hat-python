import argparse

class ConvertToInt(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError('nargs not allowed')
        super(ConvertToInt, self).__init__(option_strings, dest, **kwargs)
    def __call__(self, parser, namespace, values, option_string=None):
        if type(values) is str:
            setattr(namespace, self.dest, int(values))
        else: raise Exception('Non-convertible value provided for ConvertToInt')
