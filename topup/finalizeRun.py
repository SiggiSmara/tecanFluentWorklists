#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import sys
import os
import glob
import shutil
from datetime import date
import openpyxl as oxl

class makeImport(object):
    
    def __init__(self, volFile, sampleType="Serum"):

        self.volFile = volFile
        splitFile = os.path.split(volFile)
        self.workDir = splitFile[0]
        splitFile = splitFile[1][:-4]
        splitNames = splitFile.split("_")
        self.source = os.path.join(self.workDir, "barcodes", splitNames[0]+".xlsx")
        self.dest = os.path.join(self.workDir, "barcodes", splitNames[1]+".xlsx")
        self.gwl = os.path.join(self.workDir, "worklists",splitFile+".gwl")
        self.splitNames = splitNames

        self.sourceBc = dict()
        self.destBc = dict()

        self.sourceWell = list()
        self.makeSrcWell()
        self.destinationWell = dict()
        self.makeDestWell()

        self.baseName = splitFile
        self.datestr = date.today().isoformat()
        self.sampleType = sampleType
        self.tecanOutpPath = "C:\\ProgramData\\Tecan\\VisionX\\Output"
        #self.tecanOutpPath = os.path.join(self.workDir,".") 

        self.myOutpFile = "limsImport_" + self.baseName + ".txt"

        self.tecanOutp = dict()

        self.readAll()

        self.outpHeader = [
            "TRackBC",
            "TargetPositionID",
            "TargetPositionBC",
            "SourceTubeBC",
            "TSumStateDescription",
            "Volume",
            #"DNAVolumeFromOrigin",
            #"Concentration",
            #"SampleType",
            "SampleDate",
            #"Note",
            #"ActionDateTime",
            "TotalVolume"
            #"CustomField",
            #"Operatore"
            ]
        
    def readAll(self):
        self.sourceBc = self.readBarcodes(self.source)
        self.destBc = self.readBarcodes(self.dest)
        self.readVols()
        self.readTecanOutp()

    def readVols(self):
        with open(self.volFile, "rb") as f:
            reader = csv.DictReader(f, fieldnames=['well','valRead','color'], delimiter=';')
            self.vols=list()
            for row in reader:
                self.vols.append({'wellNo':int(row['well']),
                                    'vol':float(row['valRead'])
                                })
        f.close()

    
    def readBarcodes(self, barcFile):
        onePlate = dict()
        # for i in range(0,12):
        #     onePlate[i] = dict()
        #     for j in range(0,8):
        #         onePlate[i][j]=dict()
        xlReader = oxl.load_workbook(barcFile)
        # Get sheet names
        data = xlReader['TecanExport']
        for row in data['A2': 'F97']:
            well=row[2].value
            j = ord(well[0])-ord('A')
            i = int(well[1:])-1
            onePlate[self.destinationWell[i][j]] = {'wellNo':self.destinationWell[i][j],'well':row[2].value,'barcode':row[4].value, 'AID':row[5].value}
        
        return(onePlate)

    def readTecanOutp(self):
        self.tecanOutp=list()
        with open(os.path.join(self.tecanOutpPath,"DESTINATION.csv"), "rb") as f:
            reader = csv.DictReader(f, delimiter=',')
            reader.next()
            for row in reader:
                if row['SRCRackID']=='SOURCE':
                    self.tecanOutp.append({
                            'src':int(row['SRCPos'])-1, 
                            'dest':int(row['Position'])-1,
                            'vol':float(row['Volume']), 
                            'time': row['Time']
                        })
    def makeDestWell(self):
        self.destinationWell = dict()
        wellNo = 0
        for i in range(0,12):
            if i not in self.destinationWell:
                self.destinationWell[i] = dict()
            for j in range(0,8):
                self.destinationWell[i][j]=wellNo
                wellNo = wellNo + 1 

    def makeSrcWell(self):
        self.sourceWell = list()
        for i in range(0,12):
            for j in range(0,8):
                self.sourceWell.append(str(chr(ord('A')+j))+str(i+1).zfill(2))
    
    
    def writeResult(self):
        with open(os.path.join(self.workDir, self.myOutpFile), "wb") as f:
            writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(self.outpHeader)
            onePltBarc = self.splitNames[1]
            
            for row in self.tecanOutp:
                #print self.destBc
                if not (self.vols[row['dest']]['wellNo'] -1 == row['dest']):
                    print("Check wells!", self.vols[row['dest']]['wellNo'], row['dest'])
                writer.writerow([onePltBarc,
                                self.sourceWell[row['dest']],
                                self.destBc[row['dest']]['barcode'],
                                self.sourceBc[row['src']]['barcode'],
                                "Correct pipetting",
                                round(row['vol'],1),
                                self.datestr + " " + row['time'],
                                round(self.vols[row['dest']]['vol'] + row['vol'], 1)
                                ])

        f.close()

    def mvFiles(self):
        dest_dir = os.path.join(self.workDir, self.baseName)
        if not os.path.isdir(dest_dir):
            os.mkdir(dest_dir)
        for file in glob.glob(os.path.join(self.tecanOutpPath,"DESTINATION.csv")):
            shutil.move(file, dest_dir)
        allfiles = (self.source, self.dest, self.gwl)
        for file in allfiles:
            if os.path.isfile(file):
                shutil.move(file, dest_dir)

#TODO: check for sanity and notify if missing files
if __name__ == "__main__":
    wkdDir = None
    if len(sys.argv) == 2:
        volFile = sys.argv[1]
        oneImp = makeImport(volFile)
        #oneImp.mvFiles()
        oneImp.writeResult()
    else:
        response = raw_input("Expected one argument, got " + str(len(sys.argv)-1) +"\nTalk to Siggi before continuing  :)")

