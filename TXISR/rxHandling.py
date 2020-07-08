import io
import Check
import sys
import sqlite3
import struct
import subprocess
import calendar
import time

#we need import jacks camera code from the drivers
#we need import the boom deployer code from the drivers

### TODO: pass file location to Radio TX EXE
        ###import the camera driver
        ###import the boom driver
        ###import the command to tell the pi to turn off (watchdog)
        
        
### TODO: Write the Epoch time stamp (miliseconds) at the beginning of the transmission
### TODO: Pass Datatype to shawn's code 
### TODO: flag last tramission
        
'''
Processes:
    #1. Read Trasmission
    #2. Decode Transmission (from hex)
    #3. Produce rxData list from decoded TX
    #4. Determine the type of request recieved (database query or command)
    #5. Decide if transmitting DataType or Picture
    #6. Get packets or picture from the database
    #7. Packetize data and write to a file 
    #8. Wait until 5 seconds before the tx window starts
    #9. Call Shawn's Code
    #10. Exit (close interrupts if made)

'''

class TXISR:
    '''
    rxData holds the values gotten from the grounds transmission. (see Flight Logic doc appendix c table 5)
    0 = packet type
    1 = window start
    2 = window duration
    3 = data type
    4 = picture number (if applicable)
    '''
    rxData = []
    NombreDelArchivo = "test.txt"
    TxExe = "WHATEVER SHAWN CALLS THIS"
    
    def __init__(self):
        self.TX = io.open("/dev/tty/AMA0", 'r')
        self.readTX()
        #this varible is used to check if we can transmit or not (getter = getCanTX)
        canTX = True
        
        self.commandRecived()
        if getCanTX == False:
            # Run recieved commands
        else:
            #inizalize cammera driver
            #photo = camera()
            #inizalize boom driver
            #boom = boomDeployer()
            
            # not sure what im getting back
            # self.sendTosrCheck()
            
            '''
            Process #5
            '''
            if self.rxData[4].compareTo(None):
                self.driveDataType(self.rxData[0], self.rxData[1], self.rxData[2], self.rxData[3])
            else:
                self.drivePic(self.rxData[0], self.rxData[1], self.rxData[2], self.rxData[3], self.rxData[4])

    def readTX(self):
        '''
        Process #1 & #3
        '''
        for i in range(5):
            currentData = self.TX.readline()
            currentData = self.decodeTX(currentData)
            self.rxData.append(currentData)

    def decodeTX(self, hexMessage):
        '''
        Process #2
        '''
        return bytes.fromhex(hexMessage).decode('utf-8')

    def sendTosrCheck(self):
        Check(self.rxData[3], self.rxData[1], self.rxData[2])
    
    def drivePic (self, packType, winStart, winDur, dataType, picNum):
        '''
        Overloaded function if a picture is desired
        '''
        data = []
        
        if dataType == 3:
            picRes = h
        elif dataType == 4:
            picRes = l
        else:
            exit(1)
        
        data = self.getPicture(picNum, picRes)

        numLines = self.packetize(True, data)

        # delay 5 seconds to the start of the transmission window, then call Radio Driver
        curTime = calendar.timegm(time.gmtime())
        delay = ((winStart - curTime) - 5)
        time.sleep(delay)
            
        self.callRadioDriver(numLines, dataType, winDur)
    
    def driveSql (self, packType, winStart, winDur, dataType, sqlStatement):
        '''
        Overloaded function if an arbitrary sql statement is requested
        '''
        data = []
        
        data = self.getArbitrary(sqlStatement)
        
        ### TODO: Determine how to packetize arbitrary sql statement 
        # numLines = packetize(True, data)
        #
        
        # delay 5 seconds to the start of the transmission window, then call Radio Driver
        curTime = calendar.timegm(time.gmtime())
        delay = ((winStart - curTime) - 5)
        time.sleep(delay)
            
        self.callRadioDriver(numLines, dataType, winDur)
        
    def driveDataType (self, packType, winStart, winDur, dataType):   
        '''
        Overloaded function if no picture is requested 
        '''
        data = []
        data = self.getPackets(sys.argv[1], sys.argv[3])
        data.reverse()
        
        numLines = self.packetize(False, data)
        
        # delay 5 seconds to the start of the transmission window, then call Radio Driver
        curTime = calendar.timegm(time.gmtime())
        delay = ((winStart - curTime) - 5)
        time.sleep(delay)
            
        self.callRadioDriver(numLines, dataType, winDur)
        
    def callRadioDriver (self, numRecords, dataType, txWindow):
        '''
        Function that calls TX EXE
        '''
        ### TODO: TEST SUBPROCESS CALL METHOD ON EXE

        FNULL = open(os.devnull, 'w')
        args = TxExe "-<ARGUMENTS>"
        subprocess.call(args, stdout=FNULL, stderr=FNULL, shell=False)
        #subprocess.call(["<PATH_TO_TX_EXE>"])
        #subprocess.run(["<PATH_TO_FILE>", "-arg1 numRecords", "-dt dataType", "-tw txWindow"])

    def packetize(self, isPic, *dataList):
        """
        Takes an list(tuple(data)) from the database and writes a binary stream to a file
        call packetize(*<LIST NAME>, <BOOL VARIABLE>)
        """
        
        linesTotal = 0
        
        if isPic == True:
            ### TODO: Decide how to packetize a picture
            ### TODO: Locate the picture data and report to TX function .exe
            pass
        elif isPic == False:
            self.wipeTxFile()
            
            f = open(self.NombreDelArchivo, 'a')

            linesTotal = 0

            for tup in dataList:
                for value in tup:
                
                    ### STRING METHOD:
                    f.write(str(value))
                    f.write(',')
                     
                    ## BINARY METHOD
                    #ba = bytearray(struct.pack("f", value))
                    #t = ""
                    #for b in ba:
                    #    t = "0x%02x" % b
                    
                    ### HEX NUMBER METHOD: 
                    #hexNum = num_to_hex(value)			   
                    #f.write(hexNum)

                    ### HEX STRING METHOD:
                    #
                    #
                
                f.write('\n')
                linesTotal += 1
            f.write('@')
            f.write('\n')
        f.write(str(linesTotal))
        f.close()
        return linesTotal

    def wipeTxFile():
        file = open(self.NombreDelArchivo,"r+")
        file.truncate(0)
        file.close()
        
    ### HEX METHOD FUNCITON:
    '''
    def num_to_hex(n):
        return hex(struct.unpack('<I', struct.pack('<f', n))[0])
    '''
    ### USE THIS METHOD TO DECODE THE HEX STREAM (if being used) WHEN RECIEVED ON THE GROUND:
    '''
    def hex_to_num(h):
        h = str(h)
        h = h.replace("0x", "")
        return struct.unpack('!f', h.decode('hex'))[0]
    '''

    def getPackets(self, pacType, numPackets):
        """
        Constructs an sql query based on pacType and numPackets, returns the result.
        Process #6
        """
        lastTransmitted = 0
        connection = sqlite3.connect('../db.sqlite3')
        cursor = connection.execute(f'SELECT * FROM {pacType} WHERE time > {lastTransmitted} ORDER BY time DESC LIMIT {numPackets}')
        rows = cursor.fetchall()
        return rows
        

    def getPicture(self, picNum, res):
        """
        ... Actually, I don't know what this should do yet...
        Process #6
        """
        pass

    def getArbitrary(self, query):
        """
        executes arbitrary sql on the database target, returns whatever comes out.
        """
        connection = sqlite3.connect('../db.sqlite3')
        cursor = connection.execute(query)
        rows = cursor.fetchall()
        return rows


    def testingFunction(self):
        """
        Usage: command [-flag optional] [options]
        no flag: [<packet_type> <tx_window> <number_of_packets>]
        -a: [<sql_statement>]
        -p: [<picture_number> <resolution>]

        flags: -a, execute arbitrary sql.  Must be followed by a valid sqlite statement.
               -p, get picture.  <picture_number> is a non-negative integer, <resolution> is the size of the picture to prepare.
        """

        ### TESTING RESOURCE:
        '''
        data = []
        if sys.argv[1] == '-a':
            data = self.getArbitrary(sys.argv[2])
        elif sys.argv[1] == '-p':
            data = self.self.getPicture(sys.argv[2], sys.argv[3])
        else:
            data = self.getPackets(sys.argv[1], sys.argv[3])
            data.reverse()
        print(data)
        '''

    ### This part of the code checks to see if we are reciving a command to do something. 
    def commandRecived(self):
    '''
    Process #4
    '''
        if(self.rxData[0] == 0):
            return
        else :
            #turn off tx
            if(self.rxData[1] == 0):
                canTX = False
            #take pic
            else if(self.rxData[2] == 1) :
                #photo.Camera()
            #deploy boom
            else if(self.rxData[3] == 1) :
                #boom.boomDeployer()
            else if(self.rxData[4] == 1) :
                #reboot pi, send command to adruino
            else :
                return
                

    def getCanTX(self):
        return self.canTX

