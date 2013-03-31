import sublime, sublime_plugin
import os
import subprocess
import re

METALANG_PATH = '/mql4compiler/metalang.exe'


## todos:

## check extension
## open error window log
## print on success


class Mql4CompilerCommand(sublime_plugin.TextCommand):

    def run(self , edit):
        view = self.view
        fn = view.file_name()
        dirname  = os.path.realpath(os.path.dirname(fn))
        filename = os.path.basename(fn)
        metalang_path = sublime.packages_path() + METALANG_PATH

        command = [metalang_path,filename]

        startupinfo = None

        # hide pop-up window on windows

        if os.name is 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        # executing exe files with wine on mac / linux

        if os.name is 'posix':
            command.insert(0,'wine')

        # execution:

        proc = subprocess.Popen(command, 
        cwd= dirname,
        stdout=subprocess.PIPE,
        shell=False,
        startupinfo=startupinfo)
        output = proc.stdout.read()

        ## format error log:

        log_lines = re.split('\n',output)

        for line in log_lines :          
            line_arr = re.split(';',line)            

            if len(line_arr) is 5 : 
                print "line {0} | {1}".format(line_arr[3],line_arr[4])