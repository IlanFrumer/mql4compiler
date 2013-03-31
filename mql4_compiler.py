import sublime, sublime_plugin
import os
import subprocess


METALANG_PATH = '/mql4compiler/metalang.exe'

class Mql4CompilerCommand(sublime_plugin.TextCommand):

    def run(self , edit):
        view = self.view
        fn = view.file_name()
        dirname  = os.path.realpath(os.path.dirname(fn))
        filename = os.path.basename(fn)
        metalang_path = sublime.packages_path() + METALANG_PATH

        proc = subprocess.Popen(['wine',metalang_path,filename], 
        cwd= dirname,
        stdout=subprocess.PIPE,
        shell=False)
        output = proc.stdout.read()
        print output
