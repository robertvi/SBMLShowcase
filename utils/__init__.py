import shutil
import os
import pickle
import hashlib
import sys
from dataclasses import dataclass

@dataclass
class SuppressOutput:
    '''
    redirect stdout and/or stderr to os.devnull
    stdout: whether to suppress stdout
    stderr: whether to suppress stderr
    '''

    stdout: bool = False
    stderr: bool = False

    def suppress(self):
        'begin to suppress output(s)'
        if self.stdout:
            self.orig_stdout = sys.stdout
            sys.stdout = open(os.devnull,"w")
        if self.stderr:
            self.orig_stderr = sys.stderr
            sys.stderr = open(os.devnull,"w")

    def restore(self):
        'restore output(s)'
        if self.stdout:
            sys.stdout.close()
            sys.stdout = self.orig_stdout
        if self.stderr:
            sys.stderr.close()
            sys.stderr = self.orig_stderr


class MarkdownTable:
    '''
    helper class to accumulate rows of data with a header and optional summary row
    to be written to file as a markdown table
    '''
    def __init__(self,labels:str,keys:str,splitter='|'):
        'specify column headers and variable names'
        self.labels = [x.strip() for x in labels.split(splitter)]
        self.keys = [x.strip() for x in keys.split(splitter)]
        assert len(self.keys) == len(self.labels)
        self.data = {key:[] for key in self.keys}
        self.summary = None

    def append_row(self,vars):
        'ingest the next row from a variables dict (eg locals())'
        for key in self.keys:
            self.data[key].append(vars[key])

    def get_column(self,key):
        'return the named column'
        return self.data[key]
    
    def __getitem__(self,key):
        'convenience wrapper to allow square brackets access to columns'
        return self.get_column(key)
    
    def n_rows(self):
        'return number of data rows'
        return len(self.data[self.keys[0]])

    def n_cols(self):
        'return number of data columns'
        return len(self.data)

    def add_summary(self,key,value):
        'fill in the optional summary cell for the named column'
        if not self.summary:
            self.summary = {key:"" for key in self.keys}

        self.summary[key] = value

    def add_count(self,key,func,format='n={count}'):
        'add a basic summary counting how many times the function is true'
        count = len([ x for x in self.data[key] if func(x) ])

        self.add_summary(key,format.format(count=count))

    def transform_column(self,key,func):
        'pass all column values through a function'
        for i in range(len(self.data[key])):
            self.data[key][i] = func(self.data[key][i])

    def write(self,fout,sep='|',end='\n'):
        'write the markdown table to file'
        fout.write(sep + sep.join(self.labels) + sep + end)
        fout.write(sep + sep.join(['---' for x in self.labels]) + sep + end)
        if self.summary:
            fout.write(sep + sep.join([ str(self.summary[key]) for key in self.keys ]) + sep + end)

        for i in range(self.n_rows()):
            fout.write(sep + sep.join([ str(self.data[key][i]) for key in self.keys ])  + sep + end)


class RequestCache:
    '''
    caching is used to prevent the need to download the same responses from the remote server multiple times during testing
    '''

    def __init__(self,mode="off",direc="cache"):
        '''
        mode:
            "off" to disable caching (does not wipe any existing cache data)
            "store" to wipe and store fresh results in the cache
            "reuse" to reuse an existing cache
        direc: the directory used to store the cache
        '''
        self.mode = mode
        self.direc = direc

        if mode == "store": self.wipe()


    def wipe(self):
        'wipe any existing cache directory and setup a new empty one'

        shutil.rmtree(self.direc,ignore_errors=True)
        os.makedirs(self.direc,exist_ok=True)


    def get_path(self,request):
        '''
        return path to cached request response
        '''

        return f"{self.direc}/{hashlib.sha256(request.encode('UTF-8')).hexdigest()}"


    def get_entry(self,request):
        '''
        load cached response
        note this should only be used in a context where you trust the integrity of the cache files
        due to using pickle
        note also: no explicit handling of cache misses yet implemented
        '''

        with open(self.get_path(request),"rb") as f:
            return pickle.load(f)
        

    def set_entry(self,request,response):
        '''
        save a response to the cache
        '''

        with open(self.get_path(request),"wb") as fout:
            pickle.dump(response,fout)

