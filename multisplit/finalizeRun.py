#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import sys
import os
import glob
import shutil

class makeImport(object):
    
    def __init__(self, workDir, sampleType="Serum"):

        self.workDir =workDir
        if self.workDir == None:
            self.getWorkDir()

        self.sourceWell = list()
        self.makeSrcWell()

        self.baseName = self.readBasename()
        self.datestr = '20'+self.baseName[5:13]
        self.sampleType = sampleType
        self.tecanOutpPath = "C:\\ProgramData\\Tecan\\VisionX\\Output"
        #self.tecanOutpPath = os.path.join(self.workDir,".") 

        self.myOutpFile = "limsImport_" + self.baseName + ".txt"

        self.srcBrcds = list()
        self.dstBrcds = list()
        self.dstNuncBrcds = dict()
        self.tecanOutp = dict()

        self.readAll()

        self.outpHeader = [
            "TRackBC",
            "TargetPositionID",
            "TargetPositionBC",
            "SourceTubeBC",
            "TSumStateDescription",
            "Volume",
            "DNAVolumeFromOrigin",
            "Concentration",
            "SampleType",
            "SampleDate",
            "Note",
            "ActionDateTime",
            "CustomField",
            "Operatore"
            ]
        
    def readAll(self):
        self.readSrcBarc()
        self.readDstBarc()
        self.readTecanOutp()

    def getWorkDir(self):
        workDir=os.path.join(os.path.dirname(os.path.abspath(__file__)))
        if not os.path.isdir(workDir):
            workDir=os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])))
        self.workDir = workDir

    def readSrcBarc(self):
        self.srcBrcds = list()
        with open(os.path.join(self.workDir,self.baseName+"srcBrcds.txt"), "rb") as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                self.srcBrcds.append(row[0])

        f.close()

    def readDstBarc(self):
        self.dstBrcds = list()
        with open(os.path.join(self.workDir,self.baseName+"destBrcds.txt"), "rb") as f:
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                for oneBrcd in row:
                    if oneBrcd not in ("Nunc1","Nunc2","Nunc3"):
                        self.dstBrcds.append(oneBrcd)               
        f.close()
        self.readNuncBarc()

    def readNuncBarc(self):
        self.dstNuncBrcds=dict()
        for onePltBarc in self.dstBrcds:
            self.dstNuncBrcds[onePltBarc]=dict()
            file = os.path.join(self.workDir,onePltBarc+".txt")
            while not os.path.isfile(file):
                response = raw_input("Could not find " + file + "\nPlease make sure it is present and press Enter...")

            with open(os.path.join(self.workDir,onePltBarc+".txt"), "rb") as f:
                reader = csv.reader(f, delimiter=',')
                for row in reader:
                    self.dstNuncBrcds[onePltBarc][row[2]]=row[4]
            f.close()

    def readTecanOutp(self):
        self.tecanOutp=dict()
        for i in range(len(self.dstBrcds)):
            onePltBarc = self.dstBrcds[i]
            self.tecanOutp[onePltBarc]=list()
            with open(os.path.join(self.tecanOutpPath,"Nunc"+str(i+1)+".csv"), "rb") as f:
                reader = csv.DictReader(f, delimiter=',')
                reader.next()
                for row in reader:
                    rowSrc  = int(row['SRCPos'])/24 + 23/24 
                    self.tecanOutp[onePltBarc].append({
                                                'src':int(rowSrc), 
                                                'dest':int(row['Position'])-1,
                                                'vol':float(row['Volume']), 
                                                'time': row['Time']
                                            })

    def readBasename(self):
        file =  os.path.join(self.workDir,"convertParams.txt")
        if not os.path.isfile(file):
            response = raw_input("Could not find " + file + "\nThe lims import file generation script will fail shortly after you press Enter! Talk to Siggi before :)")
        with open(file, "rb") as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                if int(row[2]) == 1:
                    base = os.path.basename(os.path.normpath(row[0].replace("\\", "/")))
                    return base[0:(len(base)-4)]
                
        f.close()

    def makeSrcWell(self):
        self.sourceWell = list()
        
        for i in range(0,12):
            for j in range(0,8):
                self.sourceWell.append(str(chr(ord('A')+j))+str(i+1).zfill(2))
    
    
    def writeResult(self):
        with open(os.path.join(self.workDir, self.myOutpFile), "wb") as f:
            writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(self.outpHeader)
            for onePltBarc in self.dstBrcds:
                for row in self.tecanOutp[onePltBarc]:
                    #print row
                    writer.writerow([onePltBarc,
                                    self.sourceWell[row['dest']],
                                    self.dstNuncBrcds[onePltBarc][self.sourceWell[row['dest']]],
                                    self.srcBrcds[row['src']]+"-S1",
                                    "Correct pipetting",
                                    row['vol'],
                                    "",
                                    "",
                                    self.sampleType,
                                    "",
                                    "",
                                    self.datestr + " " + row['time'],
                                    "",
                                    ""])

        f.close()

    def mvFiles(self):
        dest_dir = os.path.join(self.workDir, self.baseName)
        if not os.path.isdir(dest_dir):
            os.mkdir(dest_dir)
        for file in glob.glob(os.path.join(self.tecanOutpPath,"Nunc*.csv")):
            shutil.move(file, dest_dir)
        for file in glob.glob(os.path.join(self.workDir, self.baseName +"*")):
            if os.path.isfile(file):
                shutil.move(file, dest_dir)
        for file in self.dstBrcds:
            file = os.path.join(self.workDir,file+".txt")
            if os.path.isfile(file):
                shutil.move(file, dest_dir)

#TODO: check for sanity and notify if missing files

if __name__ == "__main__":
    wkdDir = None
    if len(sys.argv) > 1:
        wkdDir = sys.argv[1]
    oneImp = makeImport(wkdDir)
    oneImp.mvFiles()
    oneImp.writeResult()