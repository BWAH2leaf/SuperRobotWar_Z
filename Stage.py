import io
import os

import glob
import subprocess

def pack():
    print('pack_Stage')
    root = r'yourFileRoot\*.new'
    fData = b''
    
    for i in glob.glob( root ):
        with open(i , 'rb') as F:
            temp  = F.read()

            if len(temp)%16 != 0:
                temp+=bytes( 16 - len(temp)%16 )

            fData += temp

    with open( 'STAGE_.bin','wb' ) as F:
        F.write( fData )


def Split(FlieName):
    print('Split Stage file')

    with open(FlieName, 'rb') as F:
        temp = F.read()

        target = bytes.fromhex('0112')
        index = -1

        indexList = []
        #print( target, len(temp) )
        while True:
            index = temp.find(target, index + 1)
            if index == -1:
                break

            if temp[ index+4:index+6 ].hex() == '1121':
                #print( temp[ index:index+6 ].hex() )
                '''
                if temp[ index-4: index-3 ].hex() == '00':
                    indexList.append( index-3 )
                    print( temp[ index-4:index ].hex() )
                else:
                    indexList.append( index-4 )
                #'''
                indexList.append( index-int(index%16) )
                print( index%16, index-int(index%16) )
                #input()

        F.seek( 0 )
        for c, x in enumerate( indexList, 1 ):
            print( c,len(indexList),indexList[c-1],indexList[-1],indexList[c-1] != indexList[-1] )
            newFN = FlieName.split('.')[0]+'_'+"{0:0>4}".format(c)
            if indexList[c-1] != indexList[-1]:
                with open(newFN, 'wb') as SF:
                    SF.write( F.read( indexList[c] - indexList[c-1] ) )
            else:
                with open(newFN, 'wb') as SF:
                    SF.write( F.read() )

            path = os.getcwd()
            subprocess.Popen('srwz -d '+newFN)

            #time.sleep(1)

if __name__ == '__main__':
    #Split('STAGE.BIN')
    pack()
