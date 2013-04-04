import sublime, sublime_plugin
import os
import subprocess
import re

PLATFORM = sublime.platform()
METALANG = 'metalang.exe'
EXTENSION = '.mq4'
WINE = 'wine'

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
PLUGIN_FOLDER = '%s/' % os.path.basename(BASE_PATH)
METALANG_PATH = os.path.join  (sublime.packages_path(), PLUGIN_FOLDER , METALANG)

def which(file):
    for path in os.environ["PATH"].split(":"):
        if os.path.exists(path + "/" + file):
                return path + "/" + file

    return None


class Mql4CompilerCommand(sublime_plugin.TextCommand):

    def init(self):
        view = self.view

        self.dirname   = os.path.realpath(os.path.dirname(view.file_name()))
        self.filename  = os.path.basename(view.file_name())
        self.extension = os.path.splitext(self.filename)[1]

        if PLATFORM != 'windows':
            self.wine_path = which(WINE)

    def isError(self):

        iserror = False

        if not os.path.exists(METALANG_PATH):
            print METALANG_PATH # Debug
            print "Mqlcompiler | error: metalang.exe not found"
            iserror = True

        if not self.view.file_name() :
            # check if console..
            print "Mqlcompiler | error: Buffer has to be saved first"
            iserror = True

        if self.extension != EXTENSION:
            print "Mqlcompiler | error: wrong file extension: ({0})". \
            format(self.extension)
            iserror = True

        if self.view.is_dirty():
            print "Mqlcompiler | error: Save File before compiling"
            iserror = True

        if PLATFORM != 'windows':
            if not self.wine_path :
                print "Mqlcompiler | error: wine is not installed"
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
        view = self.view

        new_view = view.window().new_file()
        new_view.set_scratch(True)
        new_edit = new_view.begin_edit()
        new_view.insert(new_edit, 0, output)
        new_view.end_edit(new_edit)
        sublime.status_message('Metalang')

        pass

    def run(self , edit):
        
        self.init()
        if self.isError():
            return

        stdout = self.runMetalang()
        output = self.formatOutput(stdout)

        self.newLogWindow(output)