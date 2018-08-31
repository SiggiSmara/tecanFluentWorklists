#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import sys
import os
import math
import copy

class makeCSV(object):
    
    def __init__(self, workDir):

        self.numread = 1
        self.workDir = workDir
        self.myTXTfile = ""
        self.lastTXTfile = ""
        self.splVol = 220
        self.vols=list()
        self.batches = list()
        self.batchDisps = list()
        self.destinationWell = dict()
        self.makeDestWell()
        if self.workDir == None:
            self.getWorkDir()
        self.readConvfile()
        self.myOutfile = self.myTXTfile[:-3]+"gwl"
        

    def processConvsettings(self):
            self.readTxt()
            self.makeBatches()
            self.makeAllBatchDisp()

    def getWorkDir(self):
        workDir=os.path.join(os.path.dirname(os.path.abspath(__file__)))
        if not os.path.isdir(workDir):
        #     print "first", workDir
        # else:
            workDir=os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])))
            #print "second", workDir

        self.workDir = workDir

    def readConvfile(self):
        file =  os.path.join(self.workDir,"convertParams.txt")
        if not os.path.isfile(file):
            response = raw_input("Could not find " + file + "\nThe Tecan script will fail shortly after you press Enter! Talk to Siggi before :)")

        with open(file, "rb") as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                self.myTXTfile=row[0]
                self.sourceRunner=row[1]
                self.numread=int(row[2])
                self.splVol = int(row[3])
                if self.numread == 1:
                    self.processConvsettings()
                else:
                    oldbatchDisps = copy.deepcopy(self.batchDisps)
                    #print oldbatchDisps
                    self.processConvsettings()
                    #print self.batchDisps[0][0]
                    for i in range(0,len(oldbatchDisps)):
                        for h in range(0,len(oldbatchDisps[i])):
                            for j in range(0,len(oldbatchDisps[i][h])):
                                oldbatchDisps[i][h][j]=-1
                        oldJlen = len(oldbatchDisps[i])
                        for h in range(0,len(self.batchDisps[i])):
                            #print i,j
                            #oldbatchDisps[i].append(list())
                            for j in range(0,len(self.batchDisps[i][h])):
                                oldbatchDisps[i][h].append(self.batchDisps[i][h][j])
                    self.batchDisps = oldbatchDisps
        f.close()
        
    def makeDestWell(self):
        self.destinationWell = dict()
        wellNo = 1
        for i in range(0,12):
            if i not in self.destinationWell:
                self.destinationWell[i] = dict()
            for j in range(0,8):
                self.destinationWell[i][j]=wellNo
                wellNo = wellNo + 1 

    def readTxt(self):
        with open(self.myTXTfile, "rb") as f:
            reader = csv.reader(f, delimiter=',')
            self.vols=list()
            firstRow = True
            for row in reader:
                if not firstRow:
                    #-25 for the leftovers in the tube
                    self.vols.append(float(row[0])-25)
                firstRow=False
        f.close()
    
    def makeOneBatch(self, someVols):
        if len(someVols) > 8:
            return (someVols[0:8],someVols[8:])
        else:
            return (someVols,[])

    def makeBatches(self):
        batches = list()
        oneBatch, restVols = self.makeOneBatch(self.vols)
        batches.append(oneBatch)
        while len(restVols) > 0:
            oneBatch, restVols = self.makeOneBatch(restVols)
            batches.append(oneBatch)

        self.batches = batches

    def getVol(self,restVol):
        cutoff = 300+150
        if self.numread ==2:
            cutoff = 300
        if restVol > cutoff:
            return self.splVol
        else:
            return restVol

    def makeOneDispStep(self, batchList):
        oneStep=list()
        for i in range(0,len(batchList)):
            oneVol = self.getVol(batchList[i])
            if oneVol == self.splVol:
                oneStep.append((i,self.getVol(batchList[i])))
            elif self.numread == 2:
                oneStep.append((i,self.getVol(batchList[i])))      
        return oneStep

    def makeOneBatchDisp(self, batchList):
        allSteps = list()
        # print "numread",self.numread
        while sum(batchList)>0:
            oneStep = self.makeOneDispStep(batchList)
            batchList = [a - b[1] for a, b in zip(batchList, oneStep)]
            if len(oneStep) > 0:
                allSteps.append(oneStep)
                # print "add"
        return allSteps

    def makenewOneBatchDisp(self, batchList):
        allSteps = dict()
        for i in range(0,len(batchList)):
            allSteps[i]=list()
            totVol = batchList[i]
            oneVol = self.getVol(totVol)
            while oneVol > 0:
                if oneVol == self.splVol:
                    allSteps[i].append(oneVol)
                elif self.numread == 2:
                    allSteps[i].append(oneVol)    
                totVol = totVol - oneVol
                oneVol = self.getVol(totVol)
        return allSteps

    def makeAllBatchDisp(self):
        self.batchDisps = list()
        for oneBatch in self.batches:
            #self.batchDisps.append(self.makeOneBatchDisp(oneBatch))
            self.batchDisps.append(self.makenewOneBatchDisp(oneBatch))

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
        with open(os.path.join(self.workDir,self.myOutfile), "wb") as f:
            writer = csv.writer(f, delimiter=';')
            for i in range(0,len(self.batchDisps)):
                oneStep = self.batchDisps[i]
                for h in range(0,len(oneStep)):
                    oneWell = oneStep[h]
                    oneFound = False
                    for j in range(0,len(oneWell)):
                        totVol = oneWell[j]
                        if totVol > 0:
                            oneFound = True
                            writer.writerow(["A",self.sourceRunner,None,None,i*8+h+1,None,round(totVol),None,None,None,None])
                            writer.writerow(["D","Nunc"+str(i+1),None,None,self.destinationWell[j][h],None,round(totVol),None,None,None,None])
                    if oneFound:
                        writer.writerow(["W",None])
                writer.writerow(["B",None])

        f.close()


if __name__ == "__main__":
    wkdDir = None
    if len(sys.argv) > 1:
        wkdDir = sys.argv[1]
    oneCSv = makeCSV(wkdDir)
    oneCSv.writeGWL()
    