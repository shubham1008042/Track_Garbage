############################################
# __      ___     _ _____ _ 
# \ \    / (_)   (_)  __ (_)
#  \ \  / / _ ___ _| |__) | 
#   \ \/ / | / __| |  ___/ |
#    \  /  | \__ \ | |   | |
#     \/   |_|___/_|_|   |_|
#
# +-+-+-+-+-+-+-+ +-+-+ +-+-+-+-+-+-+-+-+
# |P|o|w|e|r|e|d| |b|y| |Z|a|p|b|u|i|l|d|
# +-+-+-+-+-+-+-+ +-+-+ +-+-+-+-+-+-+-+-+
#############################################

from kepad1 import keypad # to read input from keypad
from time import sleep
from lcdtextext import display # to display characters in character LCD
from mysql_connect import dbConnection # to interact with DB
import RPi.GPIO as io  # import the GPIO library we just installed but call it "io"
import os
import signal, sys
import subprocess # to run video recording commands
import threading
from threading import Thread   # to manage multiple threads functionality
from datetime import datetime, timedelta    # datetime class
#bar code scanner
from evdev import InputDevice, ecodes, list_devices, categorize # to read input from bar code reader
from select import select
import requests
import time  # so we can use "sleep" to wait between actions

io.setwarnings(False)
# Initialize the keypad class
kp = keypad()

# Initialize the lcd class
lcd = display()

# path of the folder to share videos
#videoPath = "/home/pi/visipi/trunk/python/videos/"
videoPath = "/home/pi/python/videos/"
destVideoDir = "/var/www/visipi/trunk/assets/videos/"
videoFile = ""
# cmd = 'sudo avconv -f video4linux2 -r 25 -i /dev/video0 -f alsa -i plughw:C170,0 -ar 22050 -ab 64k -strict experimental -b 250000 -y '
# cmd = "avconv -f video4linux2 -r 1 -b 64k -i /dev/video0 -f alsa -i plughw:C170,0 -ar 22050 -strict experimental -b 64k -acodec aac -vcodec mpeg4 -r 24 -y "
# cmd = " avconv -f video4linux2 -r 25 -i /dev/video0 -f alsa -i plughw:C170,0 -ar 22050 -ab 64k -strict experimental -acodec aac -vcodec mpeg4 -y "
#currently working
cmd = "avconv -f video4linux2 -r 16 -i /dev/video0 -f alsa -i plughw:C170,0 -r 16 -b 80k -s 480x320 -strict experimental -y "
#cmd = "avconv -f video4linux2 -r 16 -i /dev/video0 -s 480x320 -strict experimental -y "

## set GPIO mode to BCM
## this takes GPIO number instead of pin number
io.setmode(io.BCM)

## enter the number of whatever GPIO pin you're using
doorPin = 11

# Lock the door
lockPin = 2
io.setup(lockPin, io.OUT)
io.output(lockPin, 1)

## use the built-in pull-up resistor
io.setup(doorPin, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp

sendMailUrl = 'http://visipi.zapbuild.com:1340/sendmail/'
# wait for user input till 15 secs
waitSec = 15
## initialize door
doorOpen = 0
# user pin variable
userId = 0
recInProgress = False
pro = {}from select import select??\
con = {}
products = []
cancelled = False
barcode=''

#bar code scanner
keys = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"

scancodes = {
    # Scancode: ASCIICode
    0: None, 1: u'ESC', 2: u'1', 3: u'2', 4: u'3', 5: u'4', 6: u'5', 7: u'6', 8: u'7', 9: u'8',
    10: u'9', 11: u'0', 12: u'-', 13: u'=', 14: u'BKSP', 15: u'TAB', 16: u'Q', 17: u'W', 18: u'E', 19: u'R',
    20: u'T', 21: u'Y', 22: u'U', 23: u'I', 24: u'O', 25: u'P', 26: u'[', 27: u']', 28: u'CRLF', 29: u'LCTRL',
    30: u'A', 31: u'S', 32: u'D', 33: u'F', 34: u'G', 35: u'H', 36: u'J', 37: u'K', 38: u'L', 39: u';',
    40: u'"', 41: u'`', 42: u'LSHFT', 43: u'\\', 44: u'Z', 45: u'X', 46: u'C', 47: u'V', 48: u'B', 49: u'N',
    50: u'M', 51: u',', 52: u'.', 53: u'/', 54: u'RSHFT', 56: u'LALT', 100: u'RALT'
}

def cancelTransaction(currentTime):
    """
    Thread's function to check if user cancelled the transaction instead of scanning bar code
    :param currentTime: waits for 15 seconds
    :return:
    """
    global cancelled, barcode
    #print 'in cancel transaction barcode is %s'%(barcode)
    while(True):
        if (datetime.now().time() > addSecs(currentTime, waitSec)):
            cancelled = True
            
            print 'Times up .. in digit function'
            return
        print '-------getting key-------%s'%(barcode)
        digitKey=kp.getKey()
        print barcode
        print digitKey
        if digitKey is not None and digitKey is not 'A':
            if(digitKey=='C' or digitKey=='D'):
                print 'in cancel transaction function'
                print threading.current_thread()
                cancelled = True
                lcd.message('Cancelled..')
                #restart()
                #break
                print 'going back'
                return
            else:
                cancelled == False
                d1=digitKey
                lcd.message('Please enter the ','code: %s'%(d1))
                sleep(0.1)
                d2 = digit(datetime.now().time())
                print d2
                if d2 is None:
                    return
                checkCancel(d2)
                lcd.message('Please enter the ','code: %s%s'%(d1, d2))
                sleep(0.1)
                barcode = '%s%s' % (d1, d2)
                
                return
        elif(barcode!=""):
            return
        sleep(0.1)


def verifyBarCode(barcode, videoFile, lastInsertedId):
    """
    checks if bar code matches with the product database
    :param barcode:
    :param videoFile:
    :param lastInsertedId:
    :return:
    """
    print 'lets verify the bar code'
    if(barcode == ''):
        print 'barcode is blank'
        getProductCode(videoFile, lastInsertedId)
        return
    #barcode = getBarCode()
    print 'barcode is %s'%(barcode)
    lcd.message('Please enter the ','code: %s'%(barcode))
    
    #get product price
    product = con.query_with_fetchone("select id, price from products where status=1 and (code='%s' or barcode='%s')" %(barcode, barcode))
    #sleep(0.5)
    if product is not None:
        # if user haven't entered the PIN
        productId = product[0]
        price = product[1]
        lcd.message('Quantity : 1')
        qty = 1
        # get quantity
        while (True):
            d = kp.getKey()
            if d is not None:
                if (d == 'D'): # transaction is completed
                    products.insert(0, (productId, lastInsertedId, price, qty))
                    updateRecord(products, lastInsertedId) # lets update the records
                    break
                elif(d == 'A'): # user wants to buy another product
                    products.insert(0, (productId, lastInsertedId, price, qty)) # update array of products
                    getProductCode(videoFile, lastInsertedId) # then lets get the product code
                    break
                elif(d == 'C'): # user cancelled the transaction
                    restart() # then lets restart the system
                    break
                elif (d not in (0, 'B','*','#') ): # user changed the qunatity of the product
                    qty = d
                    lcd.message('Qunatity : %s'%(qty))
    else:
        # if product code is wrong
        lcd.message('Wrong Product code')
        sleep(2)
        if userId:
            getProductCode(videoFile, lastInsertedId)
        else:
            restart()

def getProductCode(videoFile, lastInsertedId):
    """
    asks for the product code from the user
    :param videoFile: recorded videoFile
    :param lastInsertedId:
    :return: goes to verify bar code
    """
    global products
    lcd.message('Please enter the ','code:')
    cancelTransaction(datetime.now().time())

#    t2 = Thread(target = cancelTransaction, args=[datetime.now().time()])
    print cancelled
    print '---------------------Reached here with the result----------------'
    if(cancelled == True):
        print 'you clicked on cancel'
        print 'Ending the program'
        sleep(1)
        restart()
    if(cancelled == False):
        print barcode
        print 'got the barcode'
        verifyBarCode(barcode, videoFile, lastInsertedId)
    
def digit(currentTime):
    """
    gets user input for entering user's PIN
    :param currentTime: waits for 15 seconds to restart
    :return:
    """
    print '===== digit function ==========='
    # Loop while waiting for a keypress
    r = None
    print '-----------Getting digit in while------------'
    while r is None:
        r = kp.getKey()
        # wait for user to input digit for 15 seconds
        if (datetime.now().time() > addSecs(currentTime, waitSec)):
            print 'Times up .. in digit function'
            restart()
            break
        if (io.input(doorPin) and doorOpen == 0):
            print 'I was waiting for the Digit, But Door opened,so i am going out'
            break
        if r is None : 
            sleep(0.1)
    return r


def addSecs(tm, secs):
    fulldate = datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
    fulldate = fulldate + timedelta(seconds=secs)
    return fulldate.time()


def visiPi():
    """
    this function checks user's 4 digit PIN and verify if user have entered the correct PIN
    :return:userId as a global variable
    """
    global recInProgress, videoFile, pro, videoPath, cmd, userId
    #lcd.clear()
    lcd.message("Please enter your","4-digit PIN:")
    # Getting digit 1, printing it, then sleep to allow the next digit press.
    d1 = digit(datetime.now().time())
    print d1

    if d1 is None:
        return
    checkCancel(d1) # if user preses 'C' to cancel the transaction in between
    lcd.message("Please enter your","4-digit PIN: *")
    sleep(0.1)

    d2 = digit(datetime.now().time())
    print d2
    if d2 is None:
        return
    checkCancel(d2)
    lcd.message("Please enter your","4-digit PIN: **")
    sleep(0.1)

    d3 = digit(datetime.now().time())
    print d3
    if d3 is None:
        return
    checkCancel(d3)
    lcd.message("Please enter your","4-digit PIN: ***")
    sleep(0.1)

    d4 = digit(datetime.now().time())
    print d4
    if d4 is None:
        return
    checkCancel(d4)
    lcd.message("Please enter your","4-digit PIN: ****")

    pin = "%s%s%s%s" % (d1, d2, d3, d4)

    if (pin):
        # printing out the assembled 4 digit code.
        print "You Entered %s%s%s%s " % (d1, d2, d3, d4)

        # check if user exists in database
        row = con.query_with_fetchone("select id, firstname, lastname from users where authkey='%s%s%s%s'" % (d1, d2, d3, d4))
        if (row is not None):
            if not recInProgress :
                videoFile = str(time.time()) + ".mp4" # generate a random string for video file name
                print 'Running command ', cmd + videoPath + videoFile
                pro = subprocess.Popen("exec " + cmd + videoPath + videoFile, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
                recInProgress = True
            else :
                print '--------------Recording in progress-----------------'
                #delete last inserted record
                deleteRecord()

            userId = row[0]
            print 'Open the door'
            #io.output(lockPin, 0)  # open the door
    	    lcd.message('Welcome ' + row[1] + '!', 'You can open the', 'door now')
            sleep(1)
            io.output(lockPin, 0)  # open the door
            checkDoor(datetime.now().time()) # check if user have opened the door or not
        else:
            #lcd.clear()
            lcd.message("Wrong PIN")
            callVisiPi(2) # demands the User's PIN again


def callVisiPi(sleepTime):
    """
    a small function to wait for few seconds and call the main function to check user's input
    :param sleepTime: to wait for few seconds
    :return:calls another function
    """
    sleep(sleepTime)
    visiPi()

def checkCancel(digit):
    """
    method to check if user pressed 'C' to cancel the transaction
    :param digit:
    :return:
    """
    global cancelled
    print 'Check if', digit, 'is pressed'
    if (digit == 'C'):
        cancelled = True
        print 'C is pressed'
        lcd.message('Cancelled..')
        sleep(0.5)
        restart()
        return

def insertRecord(videoFile):
    """
    insert record in database
    :param videoFile:insert recorded file along with user id in database
    :return:asks for product code from user
    """
    global lastInsertedEntry
    qry = "INSERT INTO " \
          "`orders` " \
          "(`user_id`, `video`, `status`, `createdAt`, `updatedAt`) " \
          "VALUES " \
          "(%s, %s, true, CURRENT_TIMESTAMP, '0000-00-00 00:00:00')" % (userId, "'" + videoFile + "'")
    print qry
    lastInsertedEntry = con.insert_in_db(qry)
    if (lastInsertedEntry == 0):
        # lcd.message(' Error in saving data!')
        print "Error in recording data"
    else:
        # lcd.message(' Thanks for your time!')
        print "Data inserted successfully"
        getProductCode(videoFile, lastInsertedEntry)  # get product code from user


def updateRecord(rows,lastInsertedId):
    """
    update orders and orderproducts table
    :param rows: products array
    :param lastInsertedId: last inserted id from orders table
    :return:sends mail to user who bought the product
    """

    global recInProgress
    try:
        qry = 'Insert into `orderproducts`(`product_id`, `order_id`, `price`, `qty`, `createdAt`, `updatedAt`) values (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)'
        con.insertMany(qry, rows) # insert products array
        setTotal = 'Update `orders` set total=(select sum(price*qty) from orderproducts where order_id=%s) where id=%s' %(lastInsertedId, lastInsertedId)
        print setTotal
        con.update(setTotal) #update total price in orders table
        #print '--------------------------------------------------------------------------'
        #print '%s%s'%(sendMailUrl, lastInsertedId)
        #print '--------------------------------------------------------------------------'
        lcd.message('Enjoy your food :)')
        # send email to user on purchase
#	r = requests.get('%s%s'%(sendMailUrl, lastInsertedId))
 #       print r.text
        sleep(1)
        # after 2 sec, restart the process
        restart()
    except:
        print 'Exception in this block.. going out '
        restart()
     # send email to user on purchase
    #r = requests.get('%s%s'%(sendMailUrl, lastInsertedId))
    #print r.text

def deleteRecord():
    qry = 'delete from `orders` where id=%s' % (lastInsertedEntry)
    con.update(qry)

def getDigit():
    """
    starts the system and see if user presses * to use visicooler
    :return: database connection object as a global variable
    """
    global con
    # get character '*' from user
    lcd.message('Press * to start')
    print '----------in get digit function--------'
    while (True):
        d = kp.getKey()
        if (d == '*'):
            print 'Call Visipi ', time.strftime("%d/%m/%Y %I:%M:%S")
            try:
                # DB interaction
                con = dbConnection()
                callVisiPi(0.1) # wait for 0.1 sec
            except IOError as e:
                print e
                print 'Couldnt connect to db'
                lcd.message('Database Issue', 'Please contact Admin')
                sleep(2)
                restart()
            break
        elif (d == 'C'):
            print 'Cancelled the transaction'
            restart()
            break
        sleep(0.1)

def checkDoor(currentTime):
    """
    checks if user have opened the door and starts recording
    :param currentTime: if door is not opened for 15 secs(param : waitsec) then transaction is started again
    :return: calls to another function to insert entries in database
    """
    print 'in check door function'
    global doorOpen, recInProgress, videoFile, videoPath, pro, cmd
    afterSomeTime = addSecs(currentTime, waitSec) # adds 15 seconds to currentTime parameter

    while (True):
        ## if the switch is open
        if (io.input(doorPin) and doorOpen == 0):
            # user opened the door
            lcd.message('Recording .... ')
            doorOpen = 1

        ## if the switch is closed and doorOpen is not equal 1
        if (io.input(doorPin) == False and doorOpen == 1):
            print "===================Door Closed====================="  # stream a message saying "Close"
            #lcd.message('You closed the door')
            doorOpen = 0
            io.output(lockPin, 1)
            insertRecord(videoFile)  # insert data in database
            break
        if (io.input(doorPin) == False and doorOpen == 0 and (datetime.now().time() > afterSomeTime)):
            # user didn't open the door for waitSeconds(15 seconds)
            print 'Times up .. not opened door'
            restart()
            break
        sleep(0.5)


def startUp():
    """ first method that is called after starting the script
    :return: returns nothing but calls to another function to get user input
    """
    print '-------------------------Starting up the system------------------------------------'
    try:
        getDigit() # lets get the user input
    except KeyboardInterrupt:
        print '\nGoodBye from start'
        io.cleanup()


def restart():
    """
    function to stop all process, reset all variables and restart the transaction
    :return:null
    """
    print '---------------Re----------Starting up the system------------------------------------'
    global pro, videoFile, videoPath, recInProgress, con, products, cancelled, barcode
    print 'currently active threads %s'%(threading.activeCount())
    print threading.enumerate()

    try:
        barcode=""
        cancelled = False
        #lcd.clear()
        con.close()
        io.output(lockPin, 1)  # lock the door again
        doorOpen = 0
        if pro:
            print 'Recording in process so stopping process', pro.pid
            os.killpg(pro.pid, signal.SIGTERM)
            try:
                os.chmod(videoPath + videoFile, 777)
            except:
                print 'Could not give permissions to the file'
            recInProgress = False
        pro = {}
        products = []
        getDigit()
    except KeyboardInterrupt:
        print 'I am leaving now'
        io.cleanup()


startUp()
#getProductCode('sdsa', 2)
#getBarCode()


