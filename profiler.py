import cProfile
import pstats
import io
from io import BytesIO as StringIO
import sys

'''
Useful References:
column output:
https://docs.python.org/3/library/profile.html#instant-user-s-manual
sorting output:
https://docs.python.org/3/library/profile.html#pstats.Stats.sort_stats
'''

'''
Example Usage:

from profiler import profiler

@profiler(run_profiler=True)
def func(params):
    print('hello world')
'''

'''
Important Note:

Use the decorator once at the highest level function.
This is because the profiler profiles all called functions
from the initially called function.

Example:

def func():
    print('hello world')

@profiler(run_profiler=True)
def main():
    func()
'''

python_major_version = sys.version_info[0]


def profiler(run_profiler):

    def profile_decorator(func):
        ''' decorator that uses cProfile module to profile a given function '''

        def profile_information(*args, **kwargs):
            ''' output run time info about a function to a specified file'''

            profile = cProfile.Profile()
            profile.enable()
            func_output = func(*args, **kwargs)
            profile.disable()

            # initialize text buffer for profile info
            if python_major_version == 2:
                s = StringIO()
            elif python_major_version == 3:
                s = io.StringIO()

            sortkey = 'cumulative'

            # create an instance of a statistics object from a profile instance
            # sort the rows of the profile instance by the sortkey
            ps = pstats.Stats(profile, stream=s).sort_stats(sortkey)

            # prints out all the statistics to the stringIO text buffer
            ps.print_stats()

            # write profiler output to a specified file
            with open('profile_tool_output.txt', 'w+') as profile_tool_output:
                profile_tool_output.write(s.getvalue())
            # discard text buffer
            s.close()
            return func_output

        if run_profiler:
            return profile_information

        return func

    return profile_decorator
