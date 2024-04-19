import os
import asyncio
import zipfile
import npyscreen
import shutil
import json
from telegram import Bot, InputFile
from encrypt import *
# Define constants
chatWithMe = 0
TOKEN = ""
def readFromCfg():
    global chatWithMe, TOKEN
    file = open("config.cfg","r+")
    chatWithMe = int(file.readline())
    TOKEN = file.readline()
readFromCfg()
bot = Bot(token=TOKEN)
#_________________________________________
# Define the EncryptionWindows form
class EncryptionWindows(npyscreen.Form):
    def exit(self):
        self.parentApp.switchForm("MAIN")

    def submit(self):
        self.parentApp.sharedData["password"] = self.password.value
        if self.parentApp.sharedData["mode"] == 0:
            self.parentApp.switchForm("LOCAL")
        else:
            self.parentApp.switchForm("JSON")

    def create(self):
        self.password = self.add(npyscreen.TitleText, name="Type in password:", value="")
        self.submitButton = self.add(npyscreen.ButtonPress, name="Submit", when_pressed_function=self.submit)
        self.exitButton = self.add(npyscreen.ButtonPress, name="Exit", when_pressed_function=self.exit)

class YesNoNotificationForm(npyscreen.Form):
    def create(self):
        self.add(npyscreen.FixedText, value="Do you want to replace files in folder", editable=False)
        self.yes_button = self.add(npyscreen.ButtonPress, name="Yes",when_pressed_function = self.on_ok)
        self.no_button = self.add(npyscreen.ButtonPress, name="No",when_pressed_function = self.on_ok)

    def on_ok(self):
        if self.yes_button.value:
            self.parentApp.sharedData["replace"] = True
        elif self.no_button.value:
            self.parentApp.sharedData["replace"] = False
        self.parentApp.switchForm("MAIN")

#Define FromJSON
class FromLocal(npyscreen.Form):
    def exit(self):
        self.parentApp.switchForm("MAIN")
    def submit(self): 
        self.parentApp.sharedData["path"] = self.json.value
        self.parentApp.switchForm("MAIN")
    def create(self):
        self.json = self.add(npyscreen.TitleFilenameCombo, name="Choose a file:")
        self.submitButton = self.add(npyscreen.ButtonPress, name="Submit", when_pressed_function=self.submit)

class FromJSON(npyscreen.Form):
    def exit(self):
        self.parentApp.switchForm("MAIN")
    def submit(self):
        if(os.path.exists(".this.json")):
            fromJson = []
            file = open(".this.json", "rt")
            jsonInput = json.load(file)
            for key in jsonInput.keys():
                fromJson.append(str(key))
            self.parentApp.sharedData["path"] = fromJson[int(self.json.value[0])]
        self.parentApp.switchForm("MAIN")
    def create(self):
        fromJson = []
        if(os.path.exists(".this.json")):
            file = open(".this.json", "rt")
            jsonInput = json.load(file)
            for key in jsonInput.keys():
                fromJson.append(str(key))
        else:
            npyscreen.notify_confirm("You have nothing to download", title="Alert")
        self.json = self.add(npyscreen.TitleSelectOne, max_height=4, name="Select file", value="Select file",
        values=fromJson, scroll_exit=True)
        self.submitButton = self.add(npyscreen.ButtonPress, name="Submit", when_pressed_function=self.submit)
        self.exitButton = self.add(npyscreen.ButtonPress, name="Exit", when_pressed_function=self.exit)
# Define the MainWindow form
class MainWindow(npyscreen.Form):
    def exit(self):
        self.parentApp.switchForm(None)
    def submit(self):
        self.parentApp.sharedData["mode"] = self.mode.value[0]
        if self.encryption.value[0] == 0:
            if self.mode.value[0] == 0:
                if "password" not in self.parentApp.sharedData:
                    self.parentApp.switchForm("ENCRYPTION")
                else:
                    filePath = self.parentApp.sharedData["path"]
                    zipFileName = filePath + ".zip"
                    zip_files(filePath, zipFileName)
                    encrypt_file(zipFileName, self.parentApp.sharedData["password"], zipFileName + ".enc")
                    os.remove(zipFileName)
                    fileId = asyncio.run(uploadBigFile(zipFileName + ".enc", chatWithMe, bot))
                    writeArrayToJson(filePath, fileId, os.getcwd())
                    os.remove(zipFileName + ".enc")
                    self.parentApp.sharedData.pop("path")
            elif self.mode.value[0] == 1:
                if "password" not in self.parentApp.sharedData:
                    self.parentApp.switchForm("ENCRYPTION")
                else:
                    file = open(".this.json", "rt")
                    filePath = self.parentApp.sharedData["path"]
                    jsonInput = json.load(file)
                    print(filePath)
                    asyncio.run(downloadBigFile(jsonInput[str(filePath)],chatWithMe,bot,"ZippedFolder.zip.enc"))
                    decrypt_file("ZippedFolder.zip.enc",self.parentApp.sharedData["password"], "ZippedFolder.zip")
                    os.remove("ZippedFolder.zip.enc")
                    if os.path.exists(filePath):
                        if not "replace" in self.parentApp.sharedData:
                            self.parentApp.switchForm("REPLACE")
                        else:
                            if self.parentApp.sharedData["replace"]:
                                unzip_file("ZippedFolder.zip",filePath)
                            else:
                                pass
                    os.remove("ZippedFolder.zip")
        if self.encryption.value[0] == 1:
            if self.mode.value[0] == 0:
                if not "path" in self.parentApp.sharedData:
                    self.parentApp.switchForm("LOCAL")
                else:
                    filePath = self.parentApp.sharedData["path"]
                    zip_files(self.parentApp.sharedData["path"], "ZippedFolder.zip")
                    fileId = asyncio.run(uploadBigFile("ZippedFolder.zip", chatWithMe, bot))
                    os.remove("ZippedFolder.zip")
                    writeArrayToJson(filePath, fileId, os.getcwd())
            elif self.mode.value[0] == 1:
                if not "path" in self.parentApp.sharedData:
                    self.parentApp.switchForm("JSON")
                else:
                    file = open(".this.json", "rt")
                    filePath = self.parentApp.sharedData["path"]
                    jsonInput = json.load(file)
                    asyncio.run(downloadBigFile(jsonInput[filePath],chatWithMe,bot,"ZippedFolder.zip"))
                    if os.path.exists(filePath):
                        if not "replace" in self.parentApp.sharedData:
                            self.parentApp.switchForm("REPLACE")
                        else:
                            if self.parentApp.sharedData["replace"]:
                                unzip_file("ZippedFolder.zip",filePath)
                            else:
                                pass
                    os.remove("ZippedFolder.zip")
    def create(self):
        self.mode = self.add(npyscreen.TitleSelectOne, max_height=4, name="Select mode", value="Select mode",
                             values=["UploadFolder", "DownloadFolder"], scroll_exit=True)
        self.encryption = self.add(npyscreen.TitleSelectOne, max_height=8, name="Select mode", value="Select mode",
                                   values=["With Encryption", "Without Encryption"], scroll_exit=True)
        self.submitButton = self.add(npyscreen.ButtonPress, name="Submit", when_pressed_function=self.submit)
        self.exitButton = self.add(npyscreen.ButtonPress, name="Exit", when_pressed_function=self.exit)

# Define the MyApplication class
class MyApplication(npyscreen.NPSAppManaged):
    def onStart(self):
        self.sharedData = {}
        self.addForm("MAIN", MainWindow, name="My Form")
        self.addForm("ENCRYPTION", EncryptionWindows, name="Encryption Form")
        self.addForm("JSON", FromJSON, name="Choose from stored JSON")
        self.addForm("LOCAL", FromLocal, name="Choose from local storage")
        self.addForm("REPLACE",YesNoNotificationForm,name="Are u sure?")

#_________________________________________

# Function to zip files
def zip_files(folder_path, output_path):
    with zipfile.ZipFile(output_path, 'w') as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))
def unzip_file(zip_file_path,extract_dir):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

splittedFilesFolderPostfix = ".onlyForMyBeautifulCode"
# Function to split a file into smaller parts
def splitFile(maxFileSize: int, filePath: str):
    file = open(filePath, "rb")
    dirPath = filePath + splittedFilesFolderPostfix
    os.makedirs(dirPath, exist_ok=True)
    fileSize = os.path.getsize(filePath)
    splittedFileAmount = 0
    while file.tell() < fileSize:
        tempFile = open(os.path.join(dirPath, f"{splittedFileAmount + 1}"), "wb")
        data = file.read(maxFileSize)
        tempFile.write(data)
        tempFile.close()
        splittedFileAmount += 1
    file.close()

# Function to connect files back together
def connectFiles(folderPath: str):
    outputFileName = folderPath[:-1] + "file"
    outputFile = open(outputFileName, "wb")
    files = sorted(os.listdir("tempDirForFileWord" + splittedFilesFolderPostfix)) 
    for i in range(len(files)):
        tempFile = open(os.path.join(folderPath, str(i + 1)), "rb")
        data = tempFile.read()
        outputFile.write(data)
        tempFile.close()
    outputFile.close()

# Function to upload a file to Telegram
async def uploadFile(filePath: str, chat_id: int, bot, filename: str) -> int:
    with open(filePath, "rb") as file:
        message = await bot.send_document(chat_id=chat_id, document=InputFile(file), connect_timeout=2000000, filename=filename)
        return message.document.file_id

# Function to download a file from Telegram
async def downloadFile(fileId: str, fileOutputPath: str, bot):
    fileTG = await bot.get_file(fileId)
    file_name = fileTG.file_path.split('/')[-1]
    await fileTG.download_to_drive(custom_path=fileOutputPath)

# Function to upload a large file by splitting it into smaller parts
async def uploadBigFile(filePath: str, chat_id: int, bot):
    splitFile(20000000, filePath)
    fileIDArray = []
    files = sorted(os.listdir(filePath + splittedFilesFolderPostfix), key=lambda x: int(x)) 
    for i in files:
        fileID = await uploadFile(filePath + splittedFilesFolderPostfix + "/" + i, chat_id, bot, filename=str(i))
        fileIDArray.append(fileID)
    shutil.rmtree(filePath + splittedFilesFolderPostfix)
    return fileIDArray

# Function to download a large file from Telegram
async def downloadBigFile(filePathArray, chat_id: int, bot,outputFileName):
    os.mkdir("tempDirForFileWord" + splittedFilesFolderPostfix)
    for i in range(1, len(filePathArray) + 1):
        await downloadFile(filePathArray[i-1], "tempDirForFileWord" + splittedFilesFolderPostfix + "/" + str(i), bot)
    connectFiles("tempDirForFileWord" + splittedFilesFolderPostfix + "/")
    shutil.rmtree("tempDirForFileWord" + splittedFilesFolderPostfix + "/")
    os.rename("tempDirForFileWord" + splittedFilesFolderPostfix + "file", outputFileName)


# Function to recursively upload files from a folder
async def uploadFolder(folderPath: str):
    sortedFiles = sorted(os.listdir(folderPath))
    data = []
    for i in sortedFiles:
        fullPath = os.path.abspath(os.path.join(folderPath, i))
        if os.path.isdir(fullPath):
            fileIds = await uploadFolder(fullPath)
            fileIds = ["folder"] + fileIds
            writeArrayToJson(fullPath,fileIds,folderPath)
        else:
            print(os.path.abspath(fullPath))
            fileIds = await uploadBigFile(os.path.abspath(fullPath), chatWithMe, bot)
            data.append(writeArrayToJson(os.path.abspath(fullPath), fileIds, folderPath))
    return data

# Function to write file IDs to a JSON file
def writeArrayToJson(fileName: str, arrayOfIDS, relativePath=""):
    jsonPath = os.path.join(relativePath, ".this.json")
    print(jsonPath)
    if not os.path.exists(jsonPath):
        jsonFILE = open(jsonPath, "w+")
    else:
        jsonFILE = open(jsonPath, "r")
    try:
        data = json.load(jsonFILE)
    except:
        data = {}
    data[fileName] = arrayOfIDS
    jsonFILE.close()
    jsonFILEout = open(jsonPath, "wt")
    json.dump(data, jsonFILEout)
    return data
    
async def restoreFolder(bot, jsonInput):
    for key, value in jsonInput.items():
        if value[0] == "folder":
            os.makedirs(key, exist_ok=True)
            for i in range(1,len(value)):
                print(value[i])
                await restoreFolder(bot, value[i])
        else:
            await downloadBigFile(value, chatWithMe, bot, key)

# Main function to upload files from a folder
def console():
    app = MyApplication()
    app.run()

if __name__ == "__main__":
    console()