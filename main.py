import sys
import re
import datetime
import math


def readfile(path, key):
    try:
        f = open(path, key)
    except FileNotFoundError:
        print("can't open file")
    else:
        return f


def searchCount(line, key):
    numOfIter = line.count(key)
    return numOfIter


def searchY(line):
    y = line[1:4]
    return y


def dieOrigin(file):
    xCounter = 0
    yCounter = 0
    counter = 0
    counter2 = 0
    mapFile = readfile(file, 'r')
    for line in mapFile:
        if re.findall('[+-]\d{2}.[+-]\d', line):
            lineX = (line.strip().split(' '))
            for i in lineX:
                counter += 1
                if i == '+00':
                    xCounter = counter
        if re.findall('[+-]\d{2}.\|', line):
            counter2 += 1
            lineY = line.strip().split(' ')
            if lineY[0] == '+00':
                yCounter = counter2
    yOffset = 0 if yCounter == math.ceil(counter2 / 2) else yCounter - math.ceil(counter2 / 2)
    xOffset = 0 if xCounter == math.ceil(counter / 2) else xCounter - math.ceil(counter / 2)
    mapFile.close()
    return xOffset, yOffset


def lotId(file):
    lot_id = 0
    mapFile = readfile(file, 'r')
    for line in mapFile:
        if re.findall('Lot_id', line):
            lot_id = line.split(':')[1].strip()
    mapFile.close()
    return lot_id


def waferId(file):
    wafer = 0
    slot = 0
    mapFile = readfile(file, 'r')
    for line in mapFile:
        if re.findall('Wafer_id', line):
            wafer = line.split(':')[1].strip()
        if re.findall('Slot_no', line):
            slot = line.split(':')[1].strip()
    mapFile.close()
    return wafer, slot


def searchX(file, index):
    mapFile = readfile(file, 'r')
    for line in mapFile:
        if re.findall('[+-]\d{2}.[+-]', line):
            return line[index - 1: index + 2]
    mapFile.close()


def logic(file1, file2, key):
    xOffset, yOffset = dieOrigin(file1)
    wafer_id, slot_id = waferId(file1)
    mapFile = readfile(file1, 'r')
    outFile = readfile(file2, 'a')
    strings = '''DieOrigin {1} {2};
WaferID "@{0}";
Slot {3};
SampleCenterLocation 12080 15640;
ClassLookup 1
  0 "0"  ;
InspectionTest 1;
SampleTestPlan 5 \n''' \
        .format(wafer_id, xOffset, yOffset, slot_id)
    outFile.write(strings)
    counter1 = 0
    for line in mapFile:
        index = 0
        if line.find(key) > -1:
            if re.findall('\d{2}', line[0:4]):
                count = searchCount(line, key)
                for i in range(count):
                    index = line.find(key, index + 1)
                    y = searchY(line)
                    x = (searchX(file1, index))
                    let = '%(x)s %(y)s \n' % {'x': int(x) + xOffset, 'y': -(int(y) + yOffset)}
                    outFile.write(let)
                    counter1 += 1
    mapFile.close()
    outFile.write('''AreaPerTest 1.7777700000e+010;
DefectRecordSpec 15 DEFECTID XREL YREL XINDEX YINDEX XSIZE YSIZE DEFECTAREA DSIZE CLASSNUMBER TEST CLUSTERNUMBER ROUGHBINNUMBER FINEBINNUMBER REVIEWSAMPLE;
DefectList \n''')
    mapFile = readfile(file1, 'r')
    counter2 = 1
    for line in mapFile:
        index = 0
        if line.find(key) > -1:
            if re.findall('\d{2}', line[0:4]):
                count = searchCount(line, key)
                for i in range(count):
                    index = line.find(key, index + 1)
                    y = searchY(line)
                    x = searchX(file1, index)
                    let = '''{0} 1670 21190 {1} {2} 10 10 100 1.42124 0 1 0 0 0 0'''.format(counter2, int(x) + xOffset, -(int(y) + yOffset))
                    outFile.write(let)
                    if counter2 == counter1:
                        outFile.write(';\n')
                    else:
                        outFile.write('\n')
                    counter2 += 1
    outFile.write('''SummarySpec {0}
  TESTNO    NDEFECT    DEFDENSITY    NDIE    NDEFDIE  ;
SummaryList
  1    {1}    1.0000000000e+000    5    5  ;
'''.format(counter1, counter2 - 1))
    outFile.close()
    mapFile.close()


def initFile(file, lot):
    file = readfile(file, 'a')
    strings = '''FileVersion 1 2;
FileTimestamp {0};
InspectionStationID "Agilent" "WTS" "4070";
SampleType WAFER;
ResultTimestamp {1};
LotID "{2}";
SampleSize 1 200;
DeviceID "AT250G_TC250_33V_5V_PSP_WAC_v01";
SetupID "AT250G_TC250_33V_5V_PSP_WAC_v01" {1};
StepID "WAT";
ResultsID "qwerty";
SampleOrientationMarkType NOTCH;
OrientationMarkLocation DOWN;
DiePitch 24160 31280;
'''.format(str(datetime.datetime.now()).split('.')[0],
           str(datetime.datetime.now()).split('.')[0],
           str(lot))
    file.write(strings)
    file.close()


def main():
    if sys.argv.count('-c') & sys.argv.count('-f'):
        if (sys.argv.index('-f') == 1) & (sys.argv.index('-c') == len(sys.argv) - 2):
            indexF = sys.argv.index('-f')
            reg = sys.argv[sys.argv.index('-c') + 1]
            outFileName = '%(name)s.001' % {'name': sys.argv[indexF + 1]}
            lot_Id = lotId(sys.argv[indexF + 1])
            initFile(outFileName, lot_Id)
            for i in (sys.argv[indexF + 1:sys.argv.index('-c')]):
                logic(i, outFileName, reg)
        else:
            print('               Invalid                  ')
            print('==>>>>   script -f files -c param <<<<==')
            return
    else:
        print('               Invalid                  ')
        print('==>>>>   script -f files -c param <<<<==')
        return


main()
