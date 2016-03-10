import sublime, sublime_plugin
import os
import subprocess
import re

import sys

PLATFORM      = sublime.platform()
METALANG      = 'metalang.exe'
EXTENSION     = '.mq4'
WINE          = 'wine'

BASE_PATH     = os.path.abspath(os.path.dirname(__file__))
METALANG_PATH = os.path.join(BASE_PATH, METALANG)

def which(file):

    manual_path = os.path.join("/usr/bin", file)
    if os.path.exists(manual_path):
        return manual_path

    manual_path = os.path.join("/usr/local/bin", file)
    if os.path.exists(manual_path):
        return manual_path

    for dir in os.environ['PATH'].split(os.pathsep):
        path = os.path.join(dir, file)
        if os.path.exists(path):
            return path

    print ("PATH = {0}".format(os.environ['PATH']))
    return None


class Mql4CompilerCommand(sublime_plugin.TextCommand):

    def init(self):
        view = self.view

        if view.file_name() is not None :
            self.dirname   = os.path.realpath(os.path.dirname(view.file_name()))
            self.filename  = os.path.basename(view.file_name())
            self.extension = os.path.splitext(self.filename)[1]

        if PLATFORM != 'windows':
            self.wine_path = which(WINE)

    def isError(self):

        iserror = False

        if not os.path.exists(METALANG_PATH):
            print (METALANG_PATH) # Debug
            print ("Mqlcompiler | error: metalang.exe not found")
            iserror = True

        if PLATFORM != 'windows':
            if not self.wine_path :
                print ("Mqlcompiler | error: wine is not installed")
                iserror = True

        if self.view.file_name() is None :
            # check if console..
            print ("Mqlcompiler | error: Buffer has to be saved first")
            iserror = True

        else :

            if self.extension != EXTENSION:
                print ("Mqlcompiler | error: wrong file extension: ({0})".format(self.extension))
                iserror = True

            if self.view.is_dirty():
                print ("Mqlcompiler | error: Save File before compiling")
                iserror = True

        return iserror

    def runMetalang(self):

        command = [METALANG_PATH,self.filename]

        startupinfo = None

        # hide pop-up window on windows
        if PLATFORM == 'windows':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        # executing exe files with wine on mac / linux
        if PLATFORM != 'windows':
            command.insert(0,self.wine_path)

        # execution:
        proc = subprocess.Popen(command,
        cwd= self.dirname,
        stdout=subprocess.PIPE,
        shell=False,
        startupinfo=startupinfo)

        return proc.stdout.read()

    def formatOutput(self , stdout):

        output = ""
        log_lines = re.split('\n',stdout)
        group_files = []

        for l in log_lines :

            line = l.strip()

            if not line:
                continue

            line_arr = re.split(';',line)
            line_len = len(line_arr)

            if line_len < 5 :

                if re.match(r"^Exp file",line):
                    output+= "\n-----------------------\n"

                output+= line + "\n"

            if line_len == 5 :
                fpath = line_arr[2].split("\\")[-1]

                if fpath and not fpath in group_files:
                    group_files.append(fpath)
                    output += "\n-----------------------\n"
                    output += "file: {0}".format(fpath)
                    output += "\n-----------------------\n"

                if line_arr[3]:
                    output+= "line {0} | {1}".format(line_arr[3],line_arr[4])
                else:
                    output+= "{0}".format(line_arr[4])
                output+= "\n"

        return output


    def newLogWindow(self, output):
        window = self.view.window()

        new_view = window.create_output_panel("mql4log")
        new_view.run_command('erase_view')
        new_view.run_command('append', {'characters': output})
        window.run_command("show_panel", {"panel": "output.mql4log"})

        sublime.status_message('Metalang')

        pass

    def run(self , edit):

        self.init()
        if self.isError():
            return

        stdout = self.runMetalang()
        stdout = stdout.decode(encoding='UTF-8')
        output = self.formatOutput(stdout)
        self.newLogWindow(output)
