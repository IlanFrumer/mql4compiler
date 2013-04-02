import sublime, sublime_plugin
import os
import subprocess
import re

METALANG = 'metalang.exe'

## todos:

## on error: open log on new window
## check includes / imports


class Mql4CompilerCommand(sublime_plugin.TextCommand):

    def run(self , edit):
        view = self.view

        path = os.path.dirname(os.path.realpath(__file__))
        metalang_path = os.path.join  (path , METALANG)
        fn = view.file_name()
        dirname  = os.path.realpath(os.path.dirname(fn))
        filename = os.path.basename(fn)        
        extension = os.path.splitext(filename)[1]

        if extension != ".mq4":
            print "Mqlcompiler | error: wrong file extension: ({0})".format(extension)
            return

        if view.is_dirty():
            print "Mqlcompiler | error: Save File before compiling"
            return

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

        for l in log_lines :

            line = l.strip()

            if not line:
                continue

            line_arr = re.split(';',line)            
            line_len = len(line_arr)

            if line_len == 1 :
                print line
            if line_len == 5 : 
                print "line {0} | {1}".format(line_arr[3],line_arr[4])