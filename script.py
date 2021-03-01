import io
import os
from struct import *

import csv

def importCSV(FileName, TextOffset, SystemOffset):
    '''
    orgFileName, TextOffset, SystemOffset
    '''
    print( 'make_Stage' )
    
    # 진리표, 대응표, 등등 char table(ex 亜,가 )
    with open('jp2kr.txt','r',encoding='utf8') as dictj2K:
        Dict = {}
        kList = []
        
        for x in dictj2K.readlines():
            Dict[ x[:-1].split(',')[1] ] = x[:-1].split(',')[0]
            kList.append(x[:-1].split(',')[1])

    with open( FileName, 'rb' ) as F:
        fData = F.read()
        bData = io.BytesIO( fData )

    tempData = bData.read( TextOffset )
    bData.seek( SystemOffset )
    
    temp = b''
    temp_all = b''
    
    while True:
        temp = bData.read(4)
        if temp.hex() == '00000000':
            SystemData = temp_all
            break
        else:
            temp_all += temp
    
    newCsvFileName = '작업 시트 - '+FileName.split('.')[0]+'.csv'
    with open(newCsvFileName, 'r', encoding='utf8') as F:
        rdr = list( csv.reader(F) )
        tableData = b''
        textData = b''
        for line in rdr:
            text = line[3] # row3
            
            # translation text
            ktext = ''
            for x in text.replace(',','、'):
                ktext += Dict[x] if x in kList else x
            
            textData = ktext.replace('■','　').encode('cp932')+bytes(16-len(ktext.replace('■','　').encode('cp932'))%16)
            
            orgOffset = pack('<L', int(line[1]))
            newOffset = pack('<L', len(tempData)+7696128 - 16)

            index = -1
            while True:
                index = fData.find(orgOffset, index + 1)
                if index == -1:
                    break
                tempData = tempData[:index]+newOffset+tempData[index+4:]
                
            tempData+=textData

    print( 'check the new system offset poin is [', pack('<L', len(tempData)+7696128 - 16 ).hex()[:4], ']' )
    print( 'you find System offset bytes, 0x756f00+SystemOffset, is last 2bytes in LE.' )
    print( 'you manual change 2bytes' )
    
    tempData += SystemData
    tempData += bytes( (128 - len(tempData)%128) + 16 )

    finData = tempData[:12]+pack('<L', len(tempData[16:]))+tempData[16:]

    finData = finData[:32]+pack('<L', len(finData)-unpack('<L', finData[28:32])[0]-80)+finData[36:40]+pack('<L', unpack('<L', finData[12:16])[0]+7696128)+pack('<L', unpack('<L', finData[12:16])[0]+7696128)+finData[48:]
            
    with open( FileName.split('.')[0]+'.new', 'wb' ) as F:
        F.write( finData )

def exportCSV(FileName, TextOffset, SystemOffset):
    print( 'check' )
    
    List = []

    fData = []
    
    with open(FileName, 'rb') as F:
        bData = F.read()
        F.seek( TextOffset )
        temp_All = b''

        Trig00 = False
        TrigPrint = True

        Count = 0
        
        while True:
            if F.tell() == SystemOffset : break

            temp = F.read(1)
            if temp.hex() != '00':
                Trig00 = False
                TrigPrint = True
                temp_All+=temp
            
            else:
                if TrigPrint:
                    Trig00 = True

            if Trig00:
                intOffset = F.tell()+7696128 - 16 - len(temp_All) - 1
                Offset =  pack('<L', intOffset)
                if not temp_All.decode('cp932').replace('　','■') in List:                    
                    fData.append( [ "{0:0>4}".format(Count), intOffset, temp_All.decode('cp932').replace('　','■'), temp_All.decode('cp932').replace('　','■') ] )
                    Count += 1
                    
                else:
                    print( temp_All.decode('cp932').replace('　','■') )
                    input('Error')
                Trig00 = False
                TrigPrint = False
                temp_All = b''
                
        with open( FileName.split('.')[0]+'.csv','w',encoding='UTF8', newline='') as FD:
            wr = csv.writer(FD)
            for x in fData:
                wr.writerow(x)
                    
if __name__ == '__main__':
    print( 'convert program start' )

    #exportCSV('STAGE_0002.bin', 22288, 45840)
    importCSV('STAGE_0002.bin', 22288, 45840)

    '''file is not STAGE.BIN you before must split STAGE.BIN file.
    TextOffset is Script Start Offset. you find manully,
    SystemOffset is Script text end. some kind of Offset, 4 bytes, LE.'''
    
