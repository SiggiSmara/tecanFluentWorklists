#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import openpyxl as oxl
import sys
import os
import math
import copy

class makeCSV(object):
    
    def __init__(self, volFile, finalVol):

        self.volFile = volFile
        splitFile = os.path.split(volFile)
        self.workDir = splitFile[0]
        splitFile = splitFile[1][:-4]
        splitNames = splitFile.split("_")
        self.source = os.path.join(self.workDir, "barcodes", splitNames[0]+".xlsx")
        self.dest = os.path.join(self.workDir, "barcodes", splitNames[1]+".xlsx")
        self.myOutfile = os.path.join(self.workDir, "worklists",splitFile+".gwl")
        
        self.finalVol = finalVol
        self.vols = list()
        self.sourceBc = dict()
        self.destBc = dict()
        self.wellnoDest = dict()
        self.allAIDs = dict()

        self.initProcessing()


    def initProcessing(self):
        self.makeDestWell()
        self.readVols()
        self.sourceBc = self.readBarcodes(self.source)
        self.destBc = self.readBarcodes(self.dest)
        self.matchAIDs()
        self.makeWellnoDest()
            
        
    def makeDestWell(self):
        self.destinationWell = dict()
        wellNo = 1
        for i in range(0,12):
            if i not in self.destinationWell:
                self.destinationWell[i] = dict()
            for j in range(0,8):
                self.destinationWell[i][j]=wellNo
                wellNo = wellNo + 1 

    def getVol(self,initVol):
        missingVol = (self.finalVol - initVol * ( 1 - 2 * 0.03)) * (1 + 2*0.03)
        if missingVol < 0:
            missingVol = 0
        return(round(missingVol))

    def readVols(self):
        with open(self.volFile, "rb") as f:
            reader = csv.DictReader(f, fieldnames=['well','valRead','color'], delimiter=';')
            self.vols=list()
            for row in reader:
                self.vols.append({'wellNo':int(row['well']),
                                    'vol':float(row['valRead']), 
                                    'missingVol':self.getVol(float(row['valRead']))
                                })
        f.close()

    def readBarcodes(self, barcFile):
        onePlate = dict()
        for i in range(0,12):
            onePlate[i] = dict()
            for j in range(0,8):
                onePlate[i][j]=dict()

        xlReader = oxl.load_workbook(barcFile)
        # Get sheet names
        data = xlReader['TecanExport']
        for row in data['A2': 'F97']:
            well=row[2].value
            j = ord(well[0])-ord('A')
            i = int(well[1:])-1
            onePlate[i][j] = {'wellNo':self.destinationWell[i][j],'well':row[2].value,'barcode':row[4].value, 'AID':row[5].value}
        #with open(barcFile, "rb") as f:
            # reader = csv.reader(f, delimiter=',')
            # for row in reader:
            #     j = ord(row[2][0])-ord('A')
            #     i = int(row[2][1:])-1
            #     #print row[2], i, j
            #     onePlate[i][j] = {'wellNo':self.destinationWell[i][j],'well':row[2],'barcode':row[4], 'AID':row[5]}
        # f.close()
        return(onePlate)

    def makeWellnoDest(self):
        self.wellnoDest = dict()
        for i in range(0,12):
            for j in range(0,8):
                if len(self.destBc[i][j])>0:
                    self.wellnoDest[self.destBc[i][j]['wellNo']] = {'i':i,'j':j}

    def matchAIDs(self):
        sourceAIDs = dict()
        destAIDs = dict()
        for i in range(0,12):
            for j in range(0,8):
                if len(self.sourceBc[i][j])>0:
                    sourceAIDs[self.sourceBc[i][j]['AID']] = {'i':i,'j':j}
                if len(self.destBc[i][j])>0:
                    destAIDs[self.destBc[i][j]['AID']] = {'i':i,'j':j}
        self.allAIDs = dict()
        for oneAID in destAIDs:
            if oneAID not in sourceAIDs:
                response = raw_input("Destination AID(" + oneAID + ") not found in the source. \nTalk to Siggi before continuing  :)")
            self.allAIDs[oneAID] = {'source':sourceAIDs[oneAID], 'dest':destAIDs[oneAID]}

    def makeOneBatch(self, someVols):
        if len(someVols) > 8:
            return (someVols[0:8],someVols[8:])
        else:
            return (someVols,[])
    

    # def printResult(self):
    #     for i in range(0,len(self.batchDisps)):
    #         oneStep = self.batchDisps[i]
    #         for j in range(0,len(oneStep)):
    #             tips = oneStep[j]
    #             for h in range(0,len(tips)):
    #                 if tips[h][1]>0:
    #                     print "source",i,"step",j,"well",h+1,tips[h][1]

    def writeGWL(self):
        #print self.batchDisps
        with open(self.myOutfile, "wb") as f:
            writer = csv.writer(f, delimiter=';')
            oneBatch, restVols = self.makeOneBatch(self.vols)
            #print len(self.vols)
            while len(oneBatch)>0:
                for oneReadval in oneBatch:
                    destWellNo = oneReadval['wellNo']

                    di = self.wellnoDest[destWellNo]['i']
                    dj = self.wellnoDest[destWellNo]['j']
                    oneAID = self.destBc[di][dj]['AID']

                    si = self.allAIDs[oneAID]['source']['i']
                    sj = self.allAIDs[oneAID]['source']['j']

                    srcWellNo = self.sourceBc[si][sj]['wellNo']
                    writer.writerow(["A","SOURCE",None,None,srcWellNo,None,oneReadval['missingVol'],None,None,None,None])
                    writer.writerow(["D","DESTINATION",None,None,destWellNo,None,oneReadval['missingVol'],None,None,None,None])
                    writer.writerow(["W",None])
                writer.writerow(["B",None])
                oneBatch, restVols = self.makeOneBatch(restVols)

        f.close()


if __name__ == "__main__":
    wkdDir = None
    if len(sys.argv) > 2:
        volFile = sys.argv[1]
        finalVol = float(sys.argv[2])
        oneCSv = makeCSV(volFile, finalVol)
        oneCSv.writeGWL()
    else:
        response = raw_input("Expected two arguments, got " + str(len(sys.argv)-1) +"\nTalk to Siggi before continuing  :)")
    