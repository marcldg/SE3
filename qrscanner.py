import cv2
import numpy as np
import smtplib
import pyzbar.pyzbar as pyzbar
import pyqrcode
import pymongo
import ibmiotf.device
import time
import random
import getpass
import curses
import keyboard
import re
from datetime import datetime
from dateutil import parser
from pymongo import MongoClient
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Global variables used throughout the code
global scanned
global publishOnce
global timeElapsed
global elapsedTimeNotify
global prevUserScanned
global emailSentOnce

# Initialising variables & flags
scanned = False
publishOnce = False
timeElapsed = 0
elapsedTimeNotify = 0
prevUserScanned = ''
emailSentOnce = ''

userData = 0
userID = 0
userTemperature = 0
userQRID = 0
generatedAtTime = 0

# IBM Bluemix Login credentials
organisationID = '4c1rpi'
deviceType = 'UserQR'
deviceID = 'UQR'
authToken = 'prototypeuqr'

# Connecting to NODERED
params = {"org": organisationID, "type": deviceType, "id": deviceID, "auth-method": "token", "auth-token": authToken}
client = ibmiotf.device.HttpClient(params)

#Mongo DB 
cluster = MongoClient("mongodb+srv://MARCLDG:SIT31153HD@cluster0.f3acr.mongodb.net/Cluster0?retryWrites=true&w=majority")
db = cluster["userprofile"]
collection = db["userprofile"]

# SMTP email configuration
email = 'csafecampus@gmail.com'
email_password = 'SIT31153HD'

#function to get time
def time():
    now = datetime.now()
    return (now.strftime("%d/%m/%Y %H:%M:%S"))

#function to send QR code
def sendQRCode():
    subject = 'Campus Safe QR Authentication Pass'

    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = 'archadergm@gmail.com'
    msg['Subject'] = subject

    qremail = "How lovely is it to see you on campus! Your safety is our number one priority, this is why we have created your personal QR Authentication Code to securely grant you access to all facilities on campus. Please scan your code at the entrance of any buildings. You should note that this QR Code is available for you to use for a maximum duration of 6 hours. After these 6 hours the QR Code shall expire and you will need to scan your temperature and generate a new QR code at any of the Thermal Checkpoints around campus."
    msg.attach(MIMEText(qremail, 'plain'))

    qrcode = "qrcode.png"
    attachment =open(qrcode,'rb')

    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',"attachment; filename= "+qrcode)

    msg.attach(part)
    text = msg.as_string()
    server = smtplib.SMTP('smtp.gmail.com', 587) #port number to the server
    server.starttls() #secure connection to server
    server.login(email, email_password) #login to email
    server.sendmail(email, 'archadergm@gmail.com', text)
    server.quit()
    print("QR Code sent to your device ✔")

#function to send email to users that scan with temp above threshold
def sendCovidEmail():
    subject = 'Deakin C-safe temperature result'

    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = 'archadergm@gmail.com'
    msg['Subject'] = subject

    covidmessage = 'You have recently been scanned with a high temperature which could possibly imply a risk of covid infection.\n\nWe reccommend you to:\n\nStay home.\nMost people with COVID-19 have mild illness and can recover at home without medical care. Do not leave your home, except to get medical care. Do not visit public areas.\n\nTake care of yourself.\nGet rest and stay hydrated. Take over-the-counter medicines, such as acetaminophen, to help you feel better.\n\nStay in touch with your doctor.\nCall before you get medical care. Be sure to get care if you have trouble breathing, or have any other emergency warning signs, or if you think it is an emergency.\n\nAvoid public transportation, ride-sharing, or taxis.\nAs much as possible, stay in a specific room and away from other people and pets in your home. If possible, you should use a separate bathroom. If you need to be around other people or animals in or outside of the home, wear a mask.\n\nTell your close contacts that they may have been exposed to COVID-19. An infected person can spread COVID-19 starting 48 hours (or 2 days) before the person has any symptoms or tests positive. By letting your close contacts know they may have been exposed to COVID-19, you are helping to protect everyone.\n\nFollow the care instructions provided below and those instructed by local health department. Your local health authorities may give instructions on checking your symptoms and reporting information.'
    msg.attach(MIMEText(covidmessage, 'plain'))

    covid1 = "covid1.png"
    covid2 = "covid2.png"
    attachment1 =open(covid1, 'rb')
    attachment2 =open(covid2, 'rb')
    
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment1).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',"attachment1; filename= "+covid1)
    
    part2 = MIMEBase('application', 'octet-stream')
    part2.set_payload((attachment2).read())
    encoders.encode_base64(part2)
    part2.add_header('Content-Disposition',"attachment2; filename= "+covid2)

    msg.attach(part)
    msg.attach(part2)
    text = msg.as_string()
    server = smtplib.SMTP('smtp.gmail.com', 587) #port number to the server
    server.starttls() #secure connection to server
    server.login(email, email_password) #login to email
    server.sendmail(email, 'archadergm@gmail.com', text)
    server.quit()
    print("Safety information e-mail send to your device ✔")

# error prevention mechanism 
def limitInput(prompt):
    if not re.match("^[0-9]*$", prompt):
        print("Error! Only numbers ranging from 0-9 are allowed!\n")
        generateQR()
    
    elif len(prompt) < 0:
        print("Error! Numbers are missing - 9 numbers are required!\n")
        generateQR()
        
    elif len(prompt) > 9:
        print("Error! Too many numbers entered - 9 Numbers are required!\n")
        generateQR()
        
    elif len(prompt) < 9:
        print("Error! Numbers are missing - 9 numbers are required!\n")
        generateQR()

#function to generate QR code
def generateQR():
    print("Welcome to Deakin University ! \n")
    qrID = 0
    firstID = getpass.getpass(prompt=' Please enter your 9 Numerical Digit User ID...\n')
    limitInput(firstID)
    #print(firstID)
    secondID = getpass.getpass(prompt=' Please confirm your 9 Numerical Digit User ID...\n')
    limitInput(secondID)
    #print(secondID)
    
    if(firstID == secondID):
        qrID = secondID
        print("Logged in Successfully ✔ ")
    else:
        print("( ✕ ) The IDs provided do not match, you shall be redirected to the Welcome screen... ( ✕ )\n")
        generateQR()
    
    response = input("Pleased to see you at Burwood Campus \n for safety measures during times of pandemic, we are required to scan your temperature... \n Do you give us consent to scan your temperature ? \n Enter \n 1 for Yes \n 2 for No\n")
    #print(response)
    
    if not re.match("^[1-2]*$", response):
        print("Error! Only numbers ranging from 1-2 are allowed!\n")
        generateQR()
    elif int(response) == 0:
        print("Error! Please input a Number between 1-2!\n")
        generateQR()
    elif len(response) > 1:
        print("Error! Only Numbers from 1-2 are allowed!\n")
        generateQR()
    elif int(response) > 2:
        print("Error! Only Numbers from 1-2 are allowed!\n")
        generateQR()  
    elif int(response) < 1:
        print("Error! Only Numbers from 1-2 are allowed!\n")
        generateQR()
    else:
        if(int(response) == 1):
            qrTemperature = random.randint(33,39)
            print("Temperature being saved to your personal QR Code for identification purposes on campus...")
            generatedAtTime = datetime.now()
            qrcid = random.randint(10,90)
            qrProfile = pyqrcode.create(str(qrTemperature) + ", " + str(qrID) + ", " + str(generatedAtTime) + str(qrcid)) 
            qrProfile.png("qrcode.png", scale="10")
            print("Sending the QR Code to your device...")
            sendQRCode()
            qrID = 0
        else:
            print('Unfortunately, during pandemic times only users that scan their temperature can access the facilities. Stay at home safe. Goodluck ✔')
            generateQR()
            
generateQR()

qrscan = cv2.VideoCapture(0)
font = cv2.FONT_HERSHEY_PLAIN

created = False
# start detection
while True:
    _, frame = qrscan.read()
    
    userQR = pyzbar.decode(frame)
    
    for obj in userQR:
        userData = str(obj.data)
        userTemperature = int(userData[2:4])
        userID = int(userData[5:15])
        #print(userID)
        userScanTime = parser.parse(userData[16:36])
        #print(userScanTime)
        userQRID = int(userData[37:39])
        
        timeElapsed = int(((datetime.now() - userScanTime).total_seconds()))
        
        if(timeElapsed > 300):
            cv2.putText(frame, "Expired QR code, please visit closest Thermal Checkpoint", (50,50), font, 1, (0,0,235), 2 )
            scanned = False
        elif(userTemperature >=38):
            cv2.putText(frame,  "Your temperature might be higher than the norm please contact Deakin Health Department ", (30,50), font, 0.75, (0,0,235), 1 )
            scanned = False
        else:
            cv2.putText(frame, " Scanned with a temperature of: " + str(userTemperature) + " C - Granted Acess !", (50,50), font, 1, (0,235,0), 2 )
            scanned = True
                
        if(userTemperature >=38 and emailSentOnce != userQRID):
            #print(userTemperature)
            sendCovidEmail()
            emailSentOnce = userQRID 
            
        
    cv2.namedWindow('custom window', cv2.WINDOW_NORMAL)
    cv2.imshow('custom window', frame)
    cv2.resizeWindow('custom window', 1000, 800)
    
    key = cv2.waitKey(1)
    
    profileInDatabase = collection.find({"_id": userID})
    publishOnce = profileInDatabase.count() > 0
    
    for result in profileInDatabase:
        expiredProfile = result["scantime"]
        
        if(expiredProfile > 300):
            deleteProfile = collection.delete_one({"_id": userID})
    
    
    if(scanned == True and publishOnce == False):
        #push user profile to NODE-RED
        userProfile = {'userID': userID, 'Temperature': userTemperature, 'time': timeElapsed}
        client.publishEvent("UserProfile", "json", userProfile)
        
        #push data to MongoDB
        post = {"_id": userID, "temperature": userTemperature, "scantime": timeElapsed, "qrcid": userQRID, "scanned": True}
        collection.insert_one(post)
            
    if(publishOnce == True): 
        profileUpdate = collection.update_one({"_id": userID}, {"$set":{"scantime": timeElapsed,}})
        
    if(prevUserScanned != userID and timeElapsed < 300):
        #push user profile to NODE-RED
        userProfile = {'userID': userID, 'Temperature': userTemperature, 'time': timeElapsed}
        client.publishEvent("UserProfile", "json", userProfile)
        prevUserScanned = userID
        
    if(created == False):
        if keyboard.is_pressed('q'):  # if key 'q' is pressed
            generateQR()
    else:
        created = True
        
      



        


    
    