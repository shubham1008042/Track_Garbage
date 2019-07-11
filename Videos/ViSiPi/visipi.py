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

import time # so we can use "sleep" to wait between actions
from kepad1 import keypad
from time import sleep
from display import HD44780
from mysql_connect import dbConnection
import RPi.GPIO as io # import the GPIO library we just installed but call it "io"
import os
import signal
import subprocess
import threading
from threading import Timer
from datetime import datetime, timedelta

# Initialize the keypad class
kp = keypad()
#Initialize the lcd class
lcd = HD44780()
#DB interaction
con = dbConnection()
#path of the folder to share videos
videoPath = "../assets/videos/"
videoFile = ""
#wait for user input till 15 secs
waitSec = 15
## set GPIO mode to BCM
## this takes GPIO number instead of pin number
io.setmode(io.BCM)
## enter the number of whatever GPIO pin you're using
doorPin = 11
## use the built-in pull-up resistor
io.setup(doorPin, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
## initialize door 
doorOpen = 0
# user pin variable
userId=0
recInProgress = False
timer={}
recording={}
digitTimer={}
pro = {}
doorOpen =0
doorThreads = []
timerThreads = []
digitTimerThreads = []

def digit(currentTime):
	if(digitTimerThreads):
		for thread in digitTimerThreads:
			thread.cancel()
	# Loop while waiting for a keypress
	r = None
	print '-----------Getting digit in while------------'
	while r == None:
		r = kp.getKey()
		# wait for user to input digit for 15 seconds
		if(datetime.now().time() > addSecs(currentTime,  waitSec)):
			print 'Times up .. Restarting system '
			restart()
			break
		if (io.input(doorPin) and doorOpen == 0):
			print 'I was waiting for the Digit, But Door opened,so i am going out'
			break
	return r

def addSecs(tm, secs):
    fulldate = datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
    fulldate = fulldate + timedelta(seconds=secs)
    return fulldate.time()

def visiPi():
	lcd.clear()
	lcd.message(" Please enter your PIN: ")
	# Getting digit 1, printing it, then sleep to allow the next digit press.
	d1 = digit(datetime.now().time())
	print d1

	if d1 is None : 	
		return
	checkCancel(d1)
	lcd.message('*')
	sleep(1)
	 
	d2 = digit(datetime.now().time())
	print d2
	if d2 is None:
		return
	checkCancel(d2)
	lcd.message('*')
	sleep(1)
	 
	d3 = digit(datetime.now().time())
	print d3
	if d3 is None:
		return
	checkCancel(d3)
	lcd.message('*')
	sleep(1)
	 
	d4 = digit(datetime.now().time())
	print d4
	if d4 is None:
		return
	checkCancel(d4)
	lcd.message('*')
	 
	pin = "%s%s%s%s" %(d1,d2,d3,d4)
	
	if(pin):	
		# printing out the assembled 4 digit code.
		print "You Entered %s%s%s%s "%(d1,d2,d3,d4) 

		#check if user exists in database
		row = con.query_with_fetchone("select id, firstname, lastname from user where authkey='%s%s%s%s'"%(d1,d2,d3,d4))
		global userId
		if(row is not None):
			#print(row)
			userId = row[0]
			lcd.clear()
			lcd.message(' Welcome '+row[1]+'!\nYou can open the door now')
		else:
			lcd.clear()
			lcd.message(" Wrong PIN")
			callVisiPi(2)

def callVisiPi(sleepTime):
	sleep(sleepTime)
	visiPi()

def checkCancel(digit):
	print 'Check if',digit, 'is pressed'
	if(digit == 'C'):
		print 'C is pressed'
		lcd.clear()
		lcd.message('Cancelled..')
		restart()

def getProduct(videoFile, lastInsertedId):
	print "Please enter a product code: "
	# clean up lcd screen
	lcd.clear()
	lcd.message(' Please enter product code: ')
	print 'going to get digit'
	# Getting digit 1, printing it, then sleep to allow the next digit press.
	d1 = digit(datetime.now().time())
	
	if d1 is None :
		restart()
	checkCancel(d1)
	print "C is not pressed"
	lcd.message("%s" %(d1))
	sleep(1)

	d2 = digit(datetime.now().time())
	print d2
	if d2 is None:
		restart()
	checkCancel(d2)
	lcd.message("%s" %(d2))
	sleep(1)
	pcode = '%s%s' %(d1,d2)
	
	if pcode :
		#user entered product code
		# get product price 
		product = con.query_with_fetchone("select id, price from products where code='%s%s'"%(d1,d2))
		if(product is not None):
			#if user haven't entered the PIN
			productId = product[0]
			price = product[1]
			updateRecord(productId, price, lastInsertedId, videoFile)
		else :
			# if product code is wrong
			lcd.clear()
			lcd.message(' Wrong Product code')
			if userId:
				getProduct(videoFile, lastInsertedId)
			else : 
				restart()

def insertRecord(videoFile):
	#insert data in database
	print userId
	qry = "INSERT INTO `visipi`.`orders` (`user_id`, `product_id`, `price`, `video`, `status`, `createdAt`, `updatedAt`) VALUES (%s, %s, %s, %s, true, CURRENT_TIMESTAMP, '0000-00-00 00:00:00')" % (userId, 0, 0, "'"+videoFile+"'")
	print qry
	inserted = con.insert_in_db(qry)
        if(inserted == 0):
		#lcd.message(' Error in saving data!')
		print "Error in recording data"
        else:
		#lcd.message(' Thanks for your time!')
		print "Data inserted successfully "
		getProduct(videoFile,  inserted) #get product code from user

def updateRecord(product, price, lastInsertedId, videoFile):
	global recInProgress, userId
	print 'updating record and stopping process'
	print 'Stopping process with process id ', pro.pid
	os.killpg(pro.pid, signal.SIGTERM)
    	os.chmod(videoPath + videoFile, 777)
	recInProgress = False
	print 'After updating record. Setting recInProgress to ', recInProgress
	# lets update the record
	qry = 'Update `visipi`.`orders` set product_id=%s, price = %s, user_id=%s, updatedAt=CURRENT_TIMESTAMP where id=%s' %(product, "'"+price+"'", userId, lastInsertedId)
	userId = 0
	updated = con.update(qry)
	lcd.clear()
    	lcd.message(' Thanks for your time')
	sleep(5)
	restart()

def showTime():
	#print current time on the screen
	lcd.clear()
	lcd.message(datetime.now().strftime(' %Y-%m-%d %H:%M:%S') + '\n\nPress * to start')
	# cancel old threads
	if(timerThreads):
		for thread in timerThreads:
			thread.cancel()
			timerThreads.remove(thread)
	timer = Timer(60, showTime) #update time after every one minute
	timerThreads.append(timer)
	if timer.is_alive() is False:
		timer.start()
		

def getDigit(currentTime) :
	#get character '*' from user
	global digitTimer
	d = kp.getKey()
	if(digitTimerThreads):
		for thread in digitTimerThreads:
			print 'here thread is ',thread
			thread.cancel()
			thread.join()
			print 'we cancelled ', thread
			digitTimerThreads.remove(thread)
	print 'digit timer ', digitTimerThreads
	digitTimer = Timer(10, getDigit, [currentTime])
	print digitTimer
	digitTimerThreads.append(digitTimer)
	digitTimer.start()

	if(d == '*'):
		print 'Call Visipi'
		callVisiPi(1)
	elif(d=='C'):
		print 'Cancelled the transaction'
		#digitTimer.cancel()
		restart()

def checkDoor() : 
	global doorOpen, recInProgress, videoFile, videoPath, pro, recording, doorThreads, digitTimerThreads
	if(doorThreads):
		for thread in doorThreads:
			thread.cancel()
			doorThreads.remove(thread)
	print 'door threads ', doorThreads
	#record video if door is opened directly without entering the PIN
    	recording = Timer(5, checkDoor)
	doorThreads.append(recording)
    	recording.start()    
	## if the switch is open
	if (io.input(doorPin) and doorOpen == 0):
		print "Door Open Start Recording"
		lcd.clear()
		lcd.message(' Recording .... ')
        	doorOpen = 1
		print 'We are already recording you ',recInProgress 
		if(recInProgress and pro.pid):
			print 'Recording in process so stopping process', pro.pid
            		os.killpg(pro.pid, signal.SIGTERM)
            		os.chmod(videoPath + videoFile, 777)
            		recInProgress = False
			print 'In check door. Setting recInProgress to ', recInProgress
		videoFile = str(time.time()) + ".mp4"
		cmd = "avconv -f video4linux2 -r 25 -i /dev/video0 -f alsa -i plughw:C170,0 -ar 22050 -ab 64k -strict experimental -acodec aac -vcodec mpeg4 -y "+videoPath + videoFile
		pro = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell= True, preexec_fn=os.setsid)
		recInProgress = True
		if(digitTimerThreads):
			print 'Stop getting digit from user as door is opened'
			for thread in digitTimerThreads:
				thread.cancel()
				digitTimerThreads.remove(thread)
	## if the switch is closed and door does not equal 1
	if (io.input(doorPin)==False and doorOpen==1):
		print "===================Door Closed=====================" # stream a message saying "Close"
		doorOpen = 0
		insertRecord(videoFile) # insert data in database
	
def startUp():        
	print '-------------------------Starting up the system------------------------------------'
	userId = 0
	checkDoor() # check if door has been opened after every 2 secs
	showTime()  # display current time updated after every minute
	getDigit(datetime.now().time())  # wait for taking input from user after every second

def restart():
	print '---------------Re----------Starting up the system------------------------------------'
        global pro, videoFile, videoPath, timer, recording, digitTimer, doorThreads, digitTimerThreads, timerThreads

        print timer, '==Timer=='
        print recording, '==Recording=='
        print digitTimer, '==Digit Timer=='

        if(pro):
                print 'Process ID exists so stopping process ', pro.pid
                print pro.pid
                os.killpg(pro.pid, signal.SIGTERM)
                os.chmod(videoPath + videoFile, 777)
                pro = {}
                recInProgress = False
		print 'In restart . Setting recInProgress to ', recInProgress
                doorOpen = 0
        if(timerThreads):
                print 'Cancel Timer'
		for thread in timerThreads:
                        thread.cancel()
		timerThreads = []
        if(doorThreads):
                print 'Cancel Recording'
		for thread in doorThreads:
			thread.cancel() 
		doorThreads = []
        if(digitTimerThreads):
                print 'Cancel digit timer'
                for thread in digitTimerThreads:
                        thread.cancel()
		digitTimerThreads = []
	recInProgress = False
	checkDoor() # check if door has been opened after every 2 secs
        showTime()  # display current time updated after every minute
        getDigit(datetime.now().time())  # wait for taking input from user after every second

startUp()


