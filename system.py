import os
import time
import picamera
import subprocess
import sqlite3
from cryptography.fernet import Fernet
#packages

#main 
def main():
    #Display the entry and welcome prompt
    print("Welcome To")
    print(" ______ _____   _____  ____  _____  ")
    print("|  ____|  __ \ / ____|/ __ \|  __ \ ")
    print("| |__  | |__) | (___ | |  | | |  | |")
    print("|  __| |  ___/ \___ \| |  | | |  | |")
    print("| |    | |     ____) | |__| | |__| |")
    print("|_|    |_|    |_____/ \____/|_____/ \n")
    yorn = input("Would you like to enter? [y/n]")
    #check user input
    #if y or Y, entry is requested
    if (str(yorn) == "y" or str(yorn) == "Y"):  
        #Take picture and check it against db
        status = takeAndCheck()
        #clean temporary files from check process
        cleanTmp()
        #check status returned by takeAndCheck() (1 = entry, 0 = denied)
        if(status == 1):
            #entry gained
            welcome()
        else:
            #access denied
            print("\nAccess Denied\n")
            
    else:
        print("Bye Bye.")

#def to clean temporary files
def cleanTmp():
    #terminal call to delete files
    os.system("sudo rm /media/pi/rasusb/NBIS/toBe/temp/*")
    os.system("sudo rm /media/pi/rasusb/NBIS/toBe/database/test.xyt")
                                     

#def to take pic 
def takePic():
    #assign camera
    camera = picamera.PiCamera()
    #crop image frame
    camera.zoom=(0.3,0.31,0.4,0.5)
    #set zoom harware using fomula provided in docs
    value = (520 << 4) & 0x3ff0
    val1 = (value >> 8) & 0x3f
    val2 = value & 0xf0
    #initliaze nfiq
    nfiq=5
    #while a picture of nfiq 1 is not taken
    while(int(nfiq) >= 2):
        #set zoom
        os.system("i2cset -y 0 0x0c %d %d" % (val1,val2))
        #set camera resolution
        camera.resolution = (1920,1080)
        #dislay the photo is about to be taken
        print("Taking Picture In:")
        print("3")
        time.sleep(1)
        print("2")
        time.sleep(1)
        print("1")
        #take picture
        camera.capture("/media/pi/rasusb/NBIS/toBe/temp/taken.jpeg")
        #convert taken picture to grayscale for analysis
        os.system("sudo convert /media/pi/rasusb/NBIS/toBe/temp/taken.jpeg -colorspace GRAY /media/pi/rasusb/NBIS/toBe/temp/holder.jpeg")
        #check nfiq value of picture
        nfiq = subprocess.check_output("sudo /media/pi/rasusb/NBIS/bin/nfiq /media/pi/rasusb/NBIS/toBe/temp/holder.jpeg", shell=True)
        #if nfiq is 2 or greater display quality fail message
        if(int(nfiq) >= 2):
            print("Image did not pass quality check. Trying again.")
    
    #close camera
    camera.close() 

#its a secret
def getKey():
    key = b'psXR9RXGPP716yBrRA-IcQ4iw6pdYePd6iVhDBwzstE='
    return key

#def to encrypt database
def encryptDB():
    #assign encryption key
    fernet = Fernet(getKey())
    #open file
    with open('/media/pi/rasusb/NBIS/toBe/fingers.db', 'rb') as file:
        original = file.read()
    #encrypt file
    encrypted = fernet.encrypt(original)
    #write encrypted file
    with open('/media/pi/rasusb/NBIS/toBe/fingers.db', 'wb') as encFile:
        encFile.write(encrypted)
    
def decryptDB():
    #assign encryption key
    fernet = Fernet(getKey())
    #open encrypted file
    with open('/media/pi/rasusb/NBIS/toBe/fingers.db', 'rb') as encFile:
        encrypted = encFile.read()
    #decrypt file
    decrypted = fernet.decrypt(encrypted)
    #write decrypted file
    with open('/media/pi/rasusb/NBIS/toBe/fingers.db', 'wb') as dec_file:
        dec_file.write(decrypted)
#def to take qulity pic and check against datatbase
def takeAndCheck():
    #display entry ascii
    print("__          ___                         __     __        ___  ")
    print("\ \        / / |            /\          \ \   / /       |__ \ ")
    print(" \ \  /\  / /| |__   ___   /  \   _ __ __\ \_/ /__  _   _  ) |")
    print("  \ \/  \/ / | '_ \ / _ \ / /\ \ | '__/ _ \   / _ \| | | |/ / ")
    print("   \  /\  /  | | | | (_) / ____ \| | |  __/| | (_) | |_| |_|  ")
    print("    \/  \/   |_| |_|\___/_/    \_\_|  \___||_|\___/ \__,_(_)  \n")
    #take picture
    takePic()
    #process pic with mindtct
    os.system("sudo /media/pi/rasusb/NBIS/bin/mindtct /media/pi/rasusb/NBIS/toBe/temp/holder.jpeg /media/pi/rasusb/NBIS/toBe/temp/temp")
    #decrypt database 
    decryptDB()
    #get amount of files in DB
    maxV = checkDB()
    #for all files in database
    for i in range(1,maxV + 1):
        #check bozorth value between taken and data base xyt files
        name = getFile(i)
        bozorth = os.popen("sudo /media/pi/rasusb/NBIS/bin/bozorth3 -m1 /media/pi/rasusb/NBIS/toBe/temp/temp.xyt /media/pi/rasusb/NBIS/toBe/database/test.xyt").read()
        #check bozorth value against threshold
        #entry threshold = greater than 20
        if(int(bozorth) > 20):
            #display user
            print("USER: " + name)
            #reencrypt database
            encryptDB()
            #return match value
            return 1
    #reencrypt if no match is found
    encryptDB()
    #return non-match value
    return 0
            
#def to enroll to database
def enroll(pName, photo):
    #decrypt database for use
    decryptDB()
    #SQL query to insert
    insert_query = "INSERT INTO prints (name, img) VALUES (?, ?)"
    #connect to DB
    conn = sqlite3.connect("/media/pi/rasusb/NBIS/toBe/fingers.db")
    cursor = conn.cursor()
    #process img to blob format
    printPhoto = processImg(photo)
    #execute query
    cursor.execute(insert_query, (pName, printPhoto))
    #commit changes
    conn.commit()
    #close connection
    conn.close()
    print("Enrollment Successful!")
    #reencrypt database
    encryptDB()

#def to convert file to binary data
def processImg(photo):
    with open(photo, "rb") as file:
        blob = file.read()
    return blob

#def to get file from db by id value
def getFile(ID):
    #SQL query
    file_query = "SELECT * FROM prints WHERE id = ?"
    #connect to db
    conn = sqlite3.connect("/media/pi/rasusb/NBIS/toBe/fingers.db")
    cursor = conn.cursor()
    #execute query
    cursor.execute(file_query, (ID,))
    #get results
    result = cursor.fetchall()
    for row in result:
        #assign name output to name
        name = row[1]
        #assign file output to photo
        photo = row[2]
    
    #path to write to
    path = "/media/pi/rasusb/NBIS/toBe/database/test.xyt"
    #write binary data to xyt file
    writeTest(photo, path)
    #commit changes
    conn.commit()
    #close connection
    conn.close()
    #return name 
    return name

#def to write binary data to xyt
def writeTest(photo, fileB):
    with open(fileB, 'wb') as file:
        file.write(photo)

#def to return amount of files in db
def checkDB():
    #SQL query
    max_query = "SELECT MAX(id) FROM prints"
    #connect to DB
    conn = sqlite3.connect("/media/pi/rasusb/NBIS/toBe/fingers.db")
    cursor = conn.cursor()
    #execute query
    cursor.execute(max_query)
    #fetch results
    result = cursor.fetchall()
    #record result
    for row in result:
        am = row[0]
    #close connection
    conn.close()
    #return amount of entries in db 
    return am

#main program after entry is granted
def welcome():
    #initialize stay var
    stay = 1
    #display acess granted ascii
    print("           _____ _____ ______  _____ _____    _____ _____            _   _ _______ ______ _____  ")
    print("     /\   / ____/ ____|  ____|/ ____/ ____|  / ____|  __ \     /\   | \ | |__   __|  ____|  __ \ ")
    print("    /  \ | |   | |    | |__  | (___| (___   | |  __| |__) |   /  \  |  \| |  | |  | |__  | |  | |")
    print("   / /\ \| |   | |    |  __|  \___ \\___  \  | | |_ |  _  /   / /\ \ | . ` |  | |  |  __| | |  | |")
    print("  / ____ \ |___| |____| |____ ____) |___) | | |__| | | \ \  / ____ \| |\  |  | |  | |____| |__| |")
    print(" /_/    \_\_____\_____|______|_____/_____/   \_____|_|  \_\/_/    \_\_| \_|  |_|  |______|_____/ ")
    print("-------------------------------------------------------------------------------------------------")
    #while stay var is 1
    while(stay == 1):        
        #print options
        print("|e to enroll | m to reveal secret message | q to quit|\n")                                                                                        
        #open user input
        usrIn = input().lower()
        #test user input against options
        if(str(usrIn) == "q"):
            #q to quit
            stay = 0
        elif(str(usrIn) == "e"):
            #e starts enrollmen process
            print("-------------------------------------------------------------------------------------------------")
            print("Beginning Enrollment Process!")
            #take enrollment pic
            takePic()
            #process image
            os.system("sudo /media/pi/rasusb/NBIS/bin/mindtct /media/pi/rasusb/NBIS/toBe/temp/holder.jpeg /media/pi/rasusb/NBIS/toBe/temp/temp")
            #prompt for name of new user
            name = input("Enter Name of Person to be Enrolled: ")
            #enroll new user
            enroll(str(name), "/media/pi/rasusb/NBIS/toBe/temp/temp.xyt")
            #enrollment successful
            print("Enrollment Complete")
            print("-------------------------------------------------------------------------------------------------")
        elif(str(usrIn) == "m"):
            #m to print message
            print("This project was fun and educational")

if __name__ == "__main__":
        main()

   

