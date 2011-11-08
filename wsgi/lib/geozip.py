# -*- coding: utf-8 -*-
import os, sys, zipfile

class GeoZip:
    """
    This class supports extraction of geospatial files in stored in a zip file. It searches the file contents for files ending in common geospatial extentions and groups the accordingly.
    """
    
    def __init__ ( self, zfile ):
        self.zfile = zipfile.ZipFile(zfile)
        self.namelist = self.zfile.namelist()
        self.filelist = []
        self.datadir = ""
        self.filegroups = {} # e.g. {".shp": ["file1",file2], ".shx": ["file1","file2"] }
    def check_integrity (self):
        return self.zfile.testzip() == None
    
    def extract(self,datadir):
        self.datadir = datadir
        self.zfile.extractall(datadir)
        self.filelist = [ os.path.join(self.datadir, x) for x in self.namelist ]
        
    def group_files (self):
        """group files based on their extention"""
        for f in self.filelist:
            # base = f[f.rfind('/')+1:f.rfind('.')] (I need the whole dir in case the user zipped a whole directory tree)
            ext = f[f.rfind('.'):]
            if self.filegroups.has_key(ext):
                self.filegroups[ext].append(f)
            else:
                self.filegroups[ext] = [ f ]
    
    def getFilesByType(self, ext):
        """ ext: the extention to look for *including the dot* e.g. ".shp" """
        if self.filegroups.has_key(ext):
            return self.filegroups[ext]
        else:
            return []
    
    def getShapeFiles(self):
        """ TODO: check that it's has all the necessary files like .shx """
        return self.getFilesByType(".shp")

    def getGeoTiffFiles(self):
        """ TODO: check that it's has all the necessary files like .tfw """
        return self.getFilesByType(".tif")

    def getGMLFiles(self):
        """ TODO: check that it's has all the necessary files like .xsd """
        return self.getFilesByType(".gml")

if __name__ == "__main__":
    f = GeoZip ("OSMM_tiff.zip")
    if f.check_integrity() == False:
        print "Checksum error: zipfile is corrupted"
        sys.exit(1)
    f.extract('/tmp/') # data_dir
    f.group_files()
    print `f.filegroups`
    print "Shape files found: " + `f.getShapeFiles()`
    print "GeoTiff files found: " + `f.getGeoTiffFiles()`
    print "GML files found: " + `f.getGeoGMLFiles()`
