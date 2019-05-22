import os,sys,numpy

def cutWavLoudest(srcDirAbsPath:str, dstDirAbsPath:str, desired_ms:int):
    if sys.platform == "win32":
        srcDirAbsPath = srcDirAbsPath + "\\" if srcDirAbsPath[-1] != "\\" else srcDirAbsPath
        dstDirAbsPath = dstDirAbsPath + "\\" if dstDirAbsPath[-1] != "\\" else dstDirAbsPath
    else: # "linux" or mac??;
        srcDirAbsPath = srcDirAbsPath + "/" if srcDirAbsPath[-1] != "/" else srcDirAbsPath
        dstDirAbsPath = dstDirAbsPath + "/" if dstDirAbsPath[-1] != "/" else dstDirAbsPath

    # search wav file from srcDirAbsPath;
    srcWavAbsPathDict = {}
    for fileName in os.listdir(srcDirAbsPath):
        if fileName.rsplit(".", 1)[-1] != "wav":
            continue
        else:
            srcWavAbsPathDict[fileName] = (srcDirAbsPath + fileName)

    # process function;
    def getWavLoudestArray(srcPcmNpData, desired_ms, rate, samplesTotal):
        pcmNpDataAbsArray = numpy.fabs(srcPcmNpData)
        needSamplesTotal = (desired_ms * rate) // 1000

        loudest_start_index = 0
        rangeMaxSumTmp = 0
        for i in range(samplesTotal - needSamplesTotal):
            thisSum = numpy.sum(pcmNpDataAbsArray[i : i+needSamplesTotal])
            if thisSum > rangeMaxSumTmp:
                rangeMaxSumTmp = thisSum
                loudest_start_index = i

        loudest_end_index = loudest_start_index + needSamplesTotal
        return srcPcmNpData[loudest_start_index : loudest_end_index]

    # open wav;
    for wavFileName in srcWavAbsPathDict:
        wavAbsPath = srcWavAbsPathDict[wavFileName]
        with wave.open(wavAbsPath, "rb") as wavFile:
            wavFileParams = wavFile.getparams()
            wavFileChannels = wavFileParams[0]
            wavFileSampWidth_Byte = wavFileParams[1]
            wavFileRate = wavFileParams[2]
            wavFileSamplesTotal = wavFileParams[3]
            if wavFileChannels > 1:
                raise TypeError("only support mono wav")
            if wavFileSampWidth_Byte != 2:
                raise TypeError("only support 16bit wav")

            pcmData = wavFile.readframes(wavFileSamplesTotal)
            pcmNpArray = numpy.frombuffer(pcmData, "int16")         
            
            # process 
            loudestArray = getWavLoudestArray(pcmNpArray, desired_ms, 
                                            wavFileRate, wavFileSamplesTotal)

            # save wav;
            with wave.open(dstDirAbsPath + wavFileName, "wb") as wavOut:
                wavOut.setnchannels(wavFileChannels)
                wavOut.setsampwidth(wavFileSampWidth_Byte)
                wavOut.setframerate(wavFileRate)
                for val in loudestArray:
                    data = struct.pack('<h', val)
                    wavOut.writeframesraw(data)
                wavOut.writeframes(b"")

cutWavLoudest(r"C:\Users\feve\Downloads\wavInputDir", r"C:\Users\feve\Downloads\6666\wavOutputDir", 500)
