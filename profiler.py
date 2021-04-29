import cProfile, pstats
import io
from io import BytesIO as StringIO
import sys

python_major_version = sys.version_info[0]

def profile(func):
    '''decorator that uses cProfile to profile a function'''
    # info for columns: https://docs.python.org/3/library/profile.html#instant-user-s-manual

    def profile_information(*args, **kwargs):
        '''give runtime information about the function'''
        prof = cProfile.Profile()# start the profiler
        prof.enable()
        info = func(*args, **kwargs) # execute our function
        prof.disable() # stop the profiler after running the function

        # get the results of profiler and print results to standard output
        if python_major_version == 2:
            s = StringIO()
        elif python_major_version == 3:
            s = io.StringIO()
        # this link for things to sort by: https://docs.python.org/3/library/profile.html#pstats.Stats.sort_stats
        sortkey = 'cumulative'
        # create an instance of a statistics object from a profile instance
        # then, sort the profile instance by cumulative runtime
        ps = pstats.Stats(prof, stream=s).sort_stats(sortkey)

        # prints out all the statistics to the stringIO object
        ps.print_stats()

        # print out the stored value from stringIO
        # print(s.getvalue())

        # write profiler output to a specified file
        with open('profile_tool_output.txt', 'w+') as profile_tool_output:
            profile_tool_output.write(s.getvalue())
        return info
    
    return profile_information