import sublime, sublime_plugin
import os
import subprocess
import re

PLATFORM = sublime.platform()
METALANG = 'metalang.exe'
PLUGIN_FOLDER = "mql4compiler"
WINE_PATH = '/usr/bin/wine'

## todos:

## on error: open log on new window

class Mql4CompilerCommand(sublime_plugin.TextCommand):

    def run(self , edit):
        view = self.view
        file_path = view.file_name()

        metalang_path = os.path.join  (sublime.packages_path(), PLUGIN_FOLDER , METALANG)

        if not os.path.exists(metalang_path):
            print "Mqlcompiler | error: metalang.exe not found"
            return
    
        if not file_path :
            print "Mqlcompiler | error: Buffer has to be saved first"
            return

        dirname  = os.path.realpath(os.path.dirname(file_path))
        filename = os.path.basename(file_path)        
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

        if PLATFORM == 'windows':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        # executing exe files with wine on mac / linux

        if PLATFORM != 'windows':
            command.insert(0,WINE_PATH)

        # execution:

        proc = subprocess.Popen(command, 
        cwd= dirname,
        stdout=subprocess.PIPE,
        shell=False,
        startupinfo=startupinfo)
        output = proc.stdout.read()

        ## format error log:

        print "======================="

        log_lines = re.split('\n',output)

        group_files = []
        
        for l in log_lines :

            line = l.strip()

            if not line:
                continue

            line_arr = re.split(';',line)            
            line_len = len(line_arr)

            if line_len < 5 :
                print line
            if line_len == 5 : 
                fpath = line_arr[2].split("\\")[-1]
                if not fpath in group_files:
                    group_files.append(fpath)
                    print "-----------------------"
                    print "file: {0}".format(fpath)


                print "line {0} | {1}".format(line_arr[3],line_arr[4])