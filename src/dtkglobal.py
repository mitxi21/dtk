import json
import ntpath
import os
import platform
import shelve
import shutil
import stat
import subprocess
import threading
import base64
import io
import csv
import wx

advSetting = True
unlockSetting = True
unzipSetting = True
defaultPackagesToExclude = "et4ae5"
defaultPreScriptFolder = "data\\scripts\\PreReleaseScript.txt"
defaultScriptFolder = "data\\scripts\\PostReleaseScript.txt"
defaultMetadataFolder = "sfdc\\src\\"
defaultApiVersion = "45.0"
defaultSandboxTypes = ["Config", "QA", "UAT", "Prod"]
deploymentTypes = ["Folder", "Git", "Zip"]
testRunTypes = ["NoTestRun","RunSpecifiedTests","RunLocalTests","RunAllTestsInOrg"]
retrieveTypes = ["Manifest File", "Metadata Retrieve"]
metadataTypes = [
    "ApexClass",
    "ApexComponent",
    "ApexPage",
    "ApexTestSuite",
    "ApexTrigger",
    "AppMenu",
    "ApprovalProcess",
    "AuraDefinitionBundle",
    "ConnectedApp",
    "ContentAsset",
    "CspTrustedSite",
    "CustomApplication",
    "CustomApplicationComponent",
    "CustomLabels",
    "CustomMetadata",
    "CustomObject",
    "CustomObjectTranslation",
    "CustomPermission",
    "CustomSite",
    "CustomTab",
    "Dashboard",
    "Document",
    "DuplicateRule",
    "EmailTemplate",
    "ExternalDataSource",
    "FlexiPage",
    "Flow",
    "FlowDefinition",
    "GlobalValueSet",
    "Group",
    "HomePageLayout",
    "Layout",
    "Letterhead",
    "MatchingRules",
    "NamedCredential",
    "PermissionSet",
    "Profile",
    "ProfilePasswordPolicy",
    "Queue",
    "QuickAction",
    "RemoteSiteSetting",
    "Report",
    "ReportType",
    "Role",
    "Settings",
    "SharingRules",
    "StandardValueSet",
    "StandardValueSetTranslation",
    "StaticResource",
    "Territory",
    "TopicsForObjects",
    "Translations",
    "Workflow",
]
metadataTemplates = ["All", "None", "Profiles and related", "Typical"]
metadataTemplatesSelection = {
    "Profiles and related": [
        "ApexClass",
        "ApexPage",
        "CustomApplication",
        "CustomMetadata",
        "CustomObject",
        "CustomPermission",
        "CustomTab",
        "FlexiPage",
        "Layout",
        "Profile",
    ],
    "Typical": [
        "ApexClass",
        "ApexPage",
        "ApexTrigger",
        "CspTrustedSite",
        "CustomApplication",
        "CustomMetadata",
        "CustomObject",
        "CustomPermission",
        "CustomTab",
        "Dashboard",
        "EmailTemplate",
        "FlexiPage",
        "Group",
        "HomePageLayout",
        "Layout",
        "PermissionSet",
        "Profile",
        "Queue",
        "Report",
        "ReportType",
        "Workflow",
    ],
}
orgList = []
orgDict = dict()
soqlList = ["Custom Settings"]
soqlDict = {
    "Custom Settings Migration": "SELECT OCE__SObjectName__c, OCE__Level__c, OCE__IsList__c, OCE__RecordName__c, OCE__OwnerName__c, OCE__Data__c FROM OCE__CustomSettingsMigration__c where OCE__SObjectName__c not in ('OCE__UserSettings__c','OCE__CallDiscussionRecordtype__c') ORDER BY OCE__SObjectName__c ASC, OCE__Level__c ASC, OCE__OwnerName__c, OCE__RecordName__c ASC"
}
targets = []
workspaces = []
testLevels = ["NoTestRun", "RunSpecifiedTests", "RunLocalTests", "RunAllTestsInOrg"]
metadataTemplatesFileName = "metadataTemplates.json"
SOQLTemplatesFileName = "SOQLTemplates.json"

#Accelerate Integration: Global Variables
accelerateEnableSetting = False
accelerateDevEnableSetting = False
accelerateGitURL = "https://gitlab.ims.io/accelerators/oce_accelerate.git"
accelerateGitUser = ""
accelerateGitPassword = ""
dtkAccelerateCfg = dict()
accelerateGitBranch = ""
accelerateMetadataGitFolder = ""
acceleratePreDeployScriptFile = ""
acceleratePostDeployScriptFile = ""
accelerateVersion = ""
confluenceURL = ""
activationScriptName = ""
postMasterDataFolder = ""
postMasterDataScript = ""
accelerateModulesAvailable = dict()
acceleratedeploymentTypes = ["Folder", "Git"]
gitPreffix = "https://"
gitSuffix = "gitlab.ims.io/accelerators/oce_accelerate.git"

def SaveSettings(
    advSettingIn,
    unlockSettingIn,
    unzipSettingIn,
    accelerateEnableSettingIn,
    accelerateDevEnableSettingIn,
    accelerateGitURLIn,
    accelerateGitUserIn,
    accelerateGitPasswordIn,
    metadataTypesSettingIn,
    defaultPackagesToExcludeIn,
    defaultMetadataFolderIn,
    defaultPreScriptFolderIn,
    defaultScriptFolderIn,
    defaultApiVersionIn,
):
    homePath = os.path.join(os.path.expanduser("~"), ".dtkconfig")
    if not os.path.exists(homePath):
        os.makedirs(homePath)
    completeName = "settingsdtk.config"
    shelfFile = shelve.open(os.path.join(homePath, completeName))
    global advSetting
    advSetting = advSettingIn
    shelfFile["advSetting"] = advSettingIn
    global unlockSetting
    unlockSetting = unlockSettingIn
    shelfFile["unlockSetting"] = unlockSettingIn
    global unzipSetting
    unzipSetting = unzipSettingIn
    shelfFile["unzipSetting"] = unzipSettingIn
    global accelerateEnableSetting
    accelerateEnableSetting = accelerateEnableSettingIn
    shelfFile["accelerateEnableSetting"] = accelerateEnableSettingIn
    global accelerateDevEnableSetting
    accelerateDevEnableSetting = accelerateDevEnableSettingIn
    shelfFile["accelerateDevEnableSetting"] = accelerateDevEnableSettingIn

    global accelerateGitURL
    accelerateGitURL = accelerateGitURLIn
    shelfFile["accelerateGitURL"] = accelerateGitURLIn
    global accelerateGitUser
    accelerateGitUser = accelerateGitUserIn
    shelfFile["accelerateGitUser"] = accelerateGitUserIn
    global accelerateGitPassword
    accelerateGitPassword = accelerateGitPasswordIn
    shelfFile["accelerateGitPassword"] = accelerateGitPasswordIn
    global metadataTypes
    metadataTypes = metadataTypesSettingIn.split(",")
    metadataTypes.sort()
    shelfFile["metadataTypes"] = metadataTypes
    global defaultPackagesToExclude
    defaultPackagesToExclude = defaultPackagesToExcludeIn
    shelfFile["defaultPackagesToExclude"] = defaultPackagesToExcludeIn
    global defaultMetadataFolder
    defaultMetadataFolder = defaultMetadataFolderIn
    shelfFile["defaultMetadataFolder"] = defaultMetadataFolderIn
    global defaultPreScriptFolder
    defaultPreScriptFolder = defaultPreScriptFolderIn
    shelfFile["defaultPreScriptFolder"] = defaultPreScriptFolderIn
    global defaultScriptFolder
    defaultScriptFolder = defaultScriptFolderIn
    shelfFile["defaultScriptFolder"] = defaultScriptFolderIn
    global defaultApiVersion
    defaultApiVersion = defaultApiVersionIn
    shelfFile["defaultApiVersion"] = defaultApiVersionIn
    shelfFile.close()


def LoadSettings():
    homePath = os.path.join(os.path.expanduser("~"), ".dtkconfig")
    if not os.path.exists(homePath):
        os.makedirs(homePath)
    completeName = "settingsdtk.config"
    shelfFile = shelve.open(os.path.join(homePath, completeName))
    if "advSetting" in shelfFile:
        global advSetting
        advSetting = shelfFile["advSetting"]
    if "unlockSetting" in shelfFile:
        global unlockSetting
        unlockSetting = shelfFile["unlockSetting"]
    if "unzipSetting" in shelfFile:
        global unzipSetting
        unzipSetting = shelfFile["unzipSetting"]
    if "accelerateEnableSetting" in shelfFile:
        global accelerateEnableSetting
        accelerateEnableSetting = shelfFile["accelerateEnableSetting"]
    if "accelerateDevEnableSetting" in shelfFile:
        global accelerateDevEnableSetting
        accelerateDevEnableSetting = shelfFile["accelerateDevEnableSetting"]
    if "accelerateGitURL" in shelfFile:
        global accelerateGitURL
        accelerateGitURL = shelfFile["accelerateGitURL"]
    if "accelerateGitUser" in shelfFile:
        global accelerateGitUser
        accelerateGitUser = shelfFile["accelerateGitUser"]
    if "accelerateGitPassword" in shelfFile:
        global accelerateGitPassword
        accelerateGitPassword = shelfFile["accelerateGitPassword"]
    if "metadataTypes" in shelfFile:
        global metadataTypes
        metadataTypes = shelfFile["metadataTypes"]
    if "defaultPackagesToExclude" in shelfFile:
        global defaultPackagesToExclude
        defaultPackagesToExclude = shelfFile["defaultPackagesToExclude"]
    if "defaultMetadataFolder" in shelfFile:
        global defaultMetadataFolder
        defaultMetadataFolder = shelfFile["defaultMetadataFolder"]
    if "defaultPreScriptFolder" in shelfFile:
        global defaultPreScriptFolder
        defaultPreScriptFolder = shelfFile["defaultPreScriptFolder"]
    if "defaultScriptFolder" in shelfFile:
        global defaultScriptFolder
        defaultScriptFolder = shelfFile["defaultScriptFolder"]
    if "defaultApiVersion" in shelfFile:
        global defaultApiVersion
        defaultApiVersion = shelfFile["defaultApiVersion"]
    shelfFile.close()


def MakeModal(self, modal=True):
    if modal and not hasattr(self, "_disabler"):
        self._disabler = wx.WindowDisabler(self)
    if not modal and hasattr(self, "_disabler"):
        del self._disabler


def LoadOrganizations():
    completeName = "organizations.json"
    orgFileUrl = os.path.join(os.path.expanduser("~"), ".dtkconfig", completeName)
    global orgDict
    if not os.path.exists(orgFileUrl):
        thread = threading.Thread(target=CreateOrgsFromSfdx)
        thread.setDaemon(True)
        thread.start()
    else:
        ReadOrgs()


def CreateOrgsFromSfdx():
    cmd = ["sfdx", "force:alias:list"]
    if (platform.system() != "Windows"):
        cmd = ["/usr/local/bin/sfdx" + " " + "force:alias:list"]
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
    directory = os.path.join(os.path.expanduser("~"), ".dtk", "log")
    if not os.path.exists(directory):
        os.makedirs(directory)
    outputFileUrl = os.path.join(directory, "initorgs.log")
    outputFile = open(outputFileUrl, "wb")
    outputFile.write(proc.stdout.read())
    outputFile.close()
    fileOutput = open(outputFileUrl, "r", encoding="utf8")
    i = 0
    for line in fileOutput:
        if i > 2:
            sdbx = line.split()
            if len(sdbx) > 0:
                splitSdbx = sdbx[0].split("_")
                if len(splitSdbx) > 0:
                    sdbxName = splitSdbx[0]
                    j = 1
                    while j < len(splitSdbx) - 1:
                        sdbxName += "_" + splitSdbx[j]
                        j += 1
                    if sdbxName in orgDict:
                        sdbxConf = orgDict[sdbxName]
                        sdbxConf["sandboxes"].append(splitSdbx[len(splitSdbx) - 1])
                        orgDict[sdbxName] = sdbxConf
                    else:
                        sdbxConf = {}
                        sdbxConf["sandboxes"] = [splitSdbx[len(splitSdbx) - 1]]
                        sdbxConf["giturl"] = ""
                        sdbxConf["gituser"] = ""
                        sdbxConf["gitpass"] = ""
                        sdbxConf["metadatafolder"] = defaultMetadataFolder
                        sdbxConf["preScript"] = defaultPreScriptFolder
                        sdbxConf["script"] = defaultScriptFolder
                        orgDict[sdbxName] = sdbxConf
        i += 1
    fileOutput.close()
    os.remove(outputFileUrl)
    StoreOrgs()
    ReadOrgs()


def StoreOrgs():
    completeName = "organizations.json"
    directory = os.path.join(os.path.expanduser("~"), ".dtkconfig")
    if not os.path.exists(directory):
        os.makedirs(directory)
    orgFileUrl = os.path.join(directory, completeName)
    orgFile = open(orgFileUrl, "wb")
    global orgDict
    strOrgDict = json.dumps(orgDict, indent=4, sort_keys=True)
    bynaryOrgDict = strOrgDict.encode()
    orgFile.write(bynaryOrgDict)
    orgFile.close()


def ReadOrgs():
    completeName = "organizations.json"
    directory = os.path.join(os.path.expanduser("~"), ".dtkconfig")
    if not os.path.exists(directory):
        return
    orgFileUrl = os.path.join(directory, completeName)
    orgFile = open(orgFileUrl, "r", encoding="utf8")
    global orgDict
    global orgList
    orgDict = json.loads(orgFile.read())
    orgFile.close()
    orgList = []
    for org in orgDict:
        orgList.append(org)


def Encode(key, string):
    encoded_chars = []
    for i in range(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr(ord(string[i]) + ord(key_c) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = "".join(encoded_chars)
    return encoded_string


def Decode(key, string):
    encoded_chars = []
    for i in range(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr((ord(string[i]) - ord(key_c) + 256) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = "".join(encoded_chars)
    return encoded_string


def PathLeaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def RemoveReadonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def CopyDir(src, dest, ignore=None):
    if os.path.isdir(src):
        if not os.path.isdir(dest):
            os.makedirs(dest)
        files = os.listdir(src)
        if ignore is not None:
            ignored = ignore(src, files)
        else:
            ignored = set()
        for f in files:
            if f not in ignored:
                CopyDir(os.path.join(src, f), os.path.join(dest, f), ignore)
    else:
        shutil.copyfile(src, dest)

def ProcessCommandScriptLine(lineSplit, lineStr, targetName, sourceName, deployDataUrl, lineNumber, deployStageUrl):
    error = False
    errorMsg = ""
    cmd = []
    if len(lineSplit) > 1:
        if lineSplit[0] == "CMDEXECUTE":
            if lineSplit[1] != "":

                if "{gitroot}" in lineSplit[1]:
                    lineSplit[1] = lineSplit[1].replace("{gitroot}",deployStageUrl)
                cmd = lineSplit[1].split()
            else:
                error = True
                errorMsg = "Expected more values in command column " + str(lineNumber) + ": " + lineStr
    else:
        error = True
        errorMsg = "Expected more values in script at line " + str(lineNumber) + ": " + lineStr
    return error, errorMsg, cmd 

def ProcessFileScriptLine(lineSplit, lineStr, targetName, sourceName, deployDataUrl, lineNumber, deployStageUrl):
    error = False
    errorMsg = ""
    pathStringFileSource = ""
    pathStringFileTarget = ""
    returnMsg = ""
    if len(lineSplit) >= 7:
        if lineSplit[1] == "REPLACE":
            colReplaceIndexInSource = 0
            colReplaceIndexInTarget = 0
            fileToReplaceContent = lineSplit[2]
            fileSource = lineSplit[3]
            fileTarget = lineSplit[4]
            replaceField = lineSplit[5]
            matchFieldGrand = lineSplit[6]
            matchFieldList = []
            matchFieldListIndexSource = []
            matchFieldListIndexTarget = []
            matchFieldSplit = matchFieldGrand.split("+")
            for matchField in matchFieldSplit:
                matchFieldList.append(matchField)
            ##
            fileSourceUrl = fileSource
            if "{gitroot}" in fileSource:
                splitFileSourceUrl = fileSource.split("{gitroot}")
                if len(splitFileSourceUrl) > 1:
                    fileSourceUrl = os.path.join(deployStageUrl, splitFileSourceUrl[1])
                    pathStringFileSource = os.path.join(deployDataUrl, PathLeaf(fileSourceUrl))
                    if not os.path.exists(fileSourceUrl):
                        error = True
                        errorMsg = "File " + fileSourceUrl + " not found."
                        return error, errorMsg, returnMsg
                    if not os.path.exists(pathStringFileSource):
                        shutil.copy(fileSourceUrl, deployDataUrl)
            pathStringFileSource = os.path.join(deployDataUrl, PathLeaf(fileSourceUrl))    
            #pathStringFileSource = os.path.join(deployDataUrl, fileSource)

            if not os.path.exists(pathStringFileSource):
                error = True
                errorMsg = "File " + pathStringFileSource + " not found."
            sourceFile = open(pathStringFileSource, "r", encoding="utf8")
            firstLine = sourceFile.readline()
            columns = firstLine.split(",")
            i = 0
            for col in columns:
                value = col.strip("\r\n")
                if value in matchFieldList:
                    matchFieldListIndexSource.append(i)
                if replaceField == value:
                    colReplaceIndexInSource = i
                i += 1
            sourceFile.close()
            ##
            fileTargetUrl = fileTarget
            if "{gitroot}" in fileTarget:
                splitFileTargetUrl = fileTarget.split("{gitroot}")
                if len(splitFileTargetUrl) > 1:
                    fileTargetUrl = os.path.join(deployStageUrl, splitFileTargetUrl[1])
                    pathStringFileTarget = os.path.join(deployDataUrl, PathLeaf(fileTargetUrl))
                    if not os.path.exists(fileTargetUrl):
                        error = True
                        errorMsg = "File " + fileTargetUrl + " not found."
                        return error, errorMsg, returnMsg
                    if not os.path.exists(pathStringFileTarget):
                        shutil.copy(fileTargetUrl, deployDataUrl)
            pathStringFileTarget = os.path.join(deployDataUrl, PathLeaf(fileTargetUrl))
            #pathStringFileTarget = os.path.join(deployDataUrl, fileTarget)
            if not os.path.exists(pathStringFileTarget):
                error = True
                errorMsg = "File " + pathStringFileTarget + " not found."
            targetFile = open(pathStringFileTarget, "r", encoding="utf8")
            firstLine = targetFile.readline()
            columns = firstLine.split(",")
            i = 0
            for col in columns:
                value = col.strip("\r\n")
                if value in matchFieldList:
                    matchFieldListIndexTarget.append(i)
                if replaceField == value:
                    colReplaceIndexInTarget = i
                i += 1
            targetFile.close()

            dictSource = dict()
            sourceFile = open(pathStringFileSource, "r", encoding="utf8")
            for line in sourceFile:
                splitLine = line.split(",")
                if len(splitLine) > 1:
                    dictKey = ""
                    first = True
                    for index in matchFieldListIndexSource:
                        if first:
                            dictKey = splitLine[index].strip("\r\n")
                            first = False
                        else:
                            dictKey += "_" + splitLine[index].strip("\r\n")
                    dictSource[dictKey] = splitLine[colReplaceIndexInSource]
            sourceFile.close()

            dictTarget = dict()
            targetFile = open(pathStringFileTarget, "r", encoding="utf8")
            for line in targetFile:
                splitLine = line.split(",")
                if len(splitLine) > 1:
                    dictKey = ""
                    first = True
                    for index in matchFieldListIndexTarget:
                        if first:
                            dictKey = splitLine[index].strip("\r\n")
                            first = False
                        else:
                            dictKey += "_" + splitLine[index].strip("\r\n")
                    dictTarget[dictKey] = splitLine[colReplaceIndexInTarget]
            targetFile.close()

            replaced = False
            fileToReplaceContentUrl = fileToReplaceContent
            pathStringFileToReplaceContent = ""
            if "{gitroot}" in fileToReplaceContent:
                splitFileToReplaceContentUrl = fileToReplaceContent.split("{gitroot}")
                if len(splitFileToReplaceContentUrl) > 1:
                    fileToReplaceContentUrl = os.path.join(deployStageUrl, splitFileToReplaceContentUrl[1])
                    pathStringFileToReplaceContent = os.path.join(deployDataUrl, PathLeaf(fileToReplaceContentUrl))
                    if not os.path.exists(fileToReplaceContentUrl):
                        error = True
                        errorMsg = "File " + fileToReplaceContentUrl + " not found."
                        return error, errorMsg, returnMsg
                    if not os.path.exists(pathStringFileToReplaceContent):
                        shutil.copy(fileToReplaceContentUrl, deployDataUrl)
            pathStringFileToReplaceContent = os.path.join(deployDataUrl, PathLeaf(fileToReplaceContentUrl))
            if not os.path.exists(pathStringFileToReplaceContent):
                error = True
                errorMsg = "File " + pathStringFileToReplaceContent + " not found."
                return error, errorMsg, returnMsg
            for key in dictSource:
                if key in dictTarget:
                    allTextToReplaceContentFile = open(pathStringFileToReplaceContent, "r", encoding="utf8")
                    allTextToReplaceContent = allTextToReplaceContentFile.read()
                    allTextToReplaceContentFile.close()
                    if dictSource[key] in allTextToReplaceContent:
                        replaced = True
                        allTextToReplaceContent = allTextToReplaceContent.replace(dictSource[key], dictTarget[key])
                        allTextToReplaceContentFile = open(pathStringFileToReplaceContent, "wb")
                        bynaryContent = allTextToReplaceContent.encode()
                        allTextToReplaceContentFile.write(bynaryContent)
                        allTextToReplaceContentFile.close()
            if replaced:
                returnMsg = (
                    "Replaced values from file "
                    + pathStringFileToReplaceContent
                    + " using "
                    + pathStringFileSource
                    + " as source and "
                    + pathStringFileTarget
                    + " as target. Match fields: "
                    + matchFieldGrand
                    + ". Replace: "
                    + replaceField
                    + "."
                )
            if not replaced:
                returnMsg = (
                    "No values replaced from file "
                    + pathStringFileToReplaceContent
                    + "."
                )
    else:
        error = True
    if len(lineSplit) >= 8:
        if lineSplit[1] == "COPY":
            colCopyIndexInSource = 0
            colCopyIndexInTarget = 0
            fileToCopyContent = lineSplit[2]
            fileSource = lineSplit[3]
            fileTarget = lineSplit[4]
            sourceCopyFieldGrand = lineSplit[5]
            targetCopyField = lineSplit[6]
            matchFieldGrand = lineSplit[7]

            sourceCopyFieldList = []
            sourceCopyFieldListIndexSource = []
            sourceCopyFieldSplit = sourceCopyFieldGrand.split("+")
            for sourceCopyField in sourceCopyFieldSplit:
                sourceCopyFieldList.append(sourceCopyField)

            matchFieldList = []
            matchFieldListIndexSource = []
            matchFieldListIndexTarget = []
            matchFieldSplit = matchFieldGrand.split("+")
            for matchField in matchFieldSplit:
                matchFieldList.append(matchField)
            # SOURCE FILE PARSED FOR COLUMN INDEX
            pathStringFileSource = os.path.join(deployDataUrl, fileSource)
            if not os.path.exists(pathStringFileSource):
                error = True
                errorMsg = "File " + pathStringFileSource + " not found."
                return error, errorMsg, returnMsg
            sourceFile = open(pathStringFileSource, "r", encoding="utf8")
            firstLine = sourceFile.readline()
            columns = firstLine.split(",")
            i = 0
            for col in columns:
                value = col.strip("\r\n")
                if value in matchFieldList:
                    matchFieldListIndexSource.append(i)
                if value in sourceCopyFieldList:
                    sourceCopyFieldListIndexSource.append(i)
                i += 1
            sourceFile.close()

            pathStringFileTarget = os.path.join(deployDataUrl, fileTarget)
            if not os.path.exists(pathStringFileTarget):
                error = True
                errorMsg = "File " + pathStringFileTarget + " not found."
                return error, errorMsg, returnMsg
            targetFile = open(pathStringFileTarget, "r", encoding="utf8")
            firstLine = targetFile.readline()
            columns = firstLine.split(",")
            i = 0
            for col in columns:
                value = col.strip("\r\n")
                if value in matchFieldList:
                    matchFieldListIndexTarget.append(i)
                if targetCopyField == value:
                    colCopyIndexInTarget = i
                i += 1
            targetFile.close()

            # SOURCE FILE PARSED FOR CONTENT
            dictSource = dict()
            sourceFile = open(pathStringFileSource, "r", encoding="utf8")
            for line in sourceFile:
                splitLine = line.split(",")
                if len(splitLine) > 1:
                    dictKey = ""
                    dictValue = ""
                    first = True
                    for index in matchFieldListIndexSource:
                        if first:
                            dictKey = splitLine[index].strip("\r\n")
                            first = False
                        else:
                            dictKey += "_" + splitLine[index].strip("\r\n")
                    first = True
                    for index in sourceCopyFieldListIndexSource:
                        if first:
                            dictValue = splitLine[index].strip("\r\n")
                            first = False
                        else:
                            dictValue += "_" + splitLine[index].strip("\r\n")
                    dictSource[dictKey] = dictValue
            sourceFile.close()

            copied = False
            fileToCopyContentUrl = fileToCopyContent
            pathStringFileToCopyContent = ""
            if "{gitroot}" in fileToCopyContent:
                splitFileToCopyContentUrl = fileToCopyContent.split("{gitroot}")
                if len(splitFileToCopyContentUrl) > 1:
                    fileToCopyContentUrl = os.path.join(deployStageUrl, splitFileToCopyContentUrl[1])
                    pathStringFileToCopyContent = os.path.join(deployDataUrl, PathLeaf(fileToCopyContentUrl))
                    # if not os.path.exists(fileToCopyContentUrl):
                    #     error = True
                    #     errorMsg = "File " + fileToCopyContentUrl + " not found."
                    if not os.path.exists(pathStringFileToCopyContent):
                        shutil.copy(fileToCopyContentUrl, deployDataUrl)
            pathStringFileToCopyContent = os.path.join(deployDataUrl, PathLeaf(fileToCopyContentUrl))
            if not os.path.exists(pathStringFileToCopyContent):
                error = True
                errorMsg = "File " + pathStringFileToCopyContent + " not found."
            if not os.path.exists(pathStringFileTarget):
                error = True
                errorMsg = "File " + pathStringFileTarget + " not found."
                return error, errorMsg
            # LOOP
            targetFile = open(pathStringFileTarget, "r", encoding="utf8")
            resultsFile = open(pathStringFileToCopyContent, "w", encoding="utf8")
            headerLine = targetFile.readline()
            resultsFile.write(headerLine)
            for line in targetFile:
                splitLine = line.split(",")
                resultsSplit = splitLine
                if len(splitLine) > 1:
                    dictKey = ""
                    first = True
                    for index in matchFieldListIndexTarget:
                        if first:
                            dictKey = splitLine[index].strip("\r\n")
                            first = False
                        else:
                            dictKey += "_" + splitLine[index].strip("\r\n")
                    if dictKey in dictSource:
                        copied = True
                        resultsSplit[colCopyIndexInTarget] = dictSource[dictKey]
                    resultsLine = ",".join(resultsSplit)
                    if not resultsLine.endswith("\n"):
                        resultsLine = resultsLine + "\n"
                    resultsFile.write(resultsLine)
            resultsFile.close()
            targetFile.close()

            if copied:
                returnMsg = (
                    "Copied values in file "
                    + pathStringFileToCopyContent
                    + " using "
                    + pathStringFileSource
                    + " as source and "
                    + pathStringFileTarget
                    + " as target. Match fields: "
                    + matchFieldGrand
                    + ". Copy fields: "
                    + sourceCopyFieldGrand
                    + " into field:"
                    + targetCopyField
                    + "."
                )
            if not copied:
                returnMsg = (
                    "No values copied in file "
                    + pathStringFileToCopyContent
                    + "."
                )
    if error:
        errorMsg = "Expected more values in script at line " + str(lineNumber) + ": " + lineStr
    return error, errorMsg, returnMsg


def ProcessDataScriptLine(lineSplit, lineStr, targetName, sourceName, deployDataUrl, lineNumber, deployStageUrl):
    error = False
    errorMsg = ""
    cmd = []
    target = ""
    pathString = ""
    if len(lineSplit) >= 1:
        if lineSplit[0] == "SOURCE":
            target = sourceName
        if lineSplit[0] == "TARGET":
            target = targetName
    else:
        error = True
        errorMsg = "Expected more values in script at line " + lineNumber + ": " + lineStr
        return error, errorMsg, target, pathString, cmd
    if len(lineSplit) >= 3:
        if lineSplit[1] == "SOQLQUERY":
            if len(lineSplit) < 4:
                error = True
                errorMsg = "Expected more values in script at line " + lineNumber + ": " + lineStr
                return error, errorMsg, target, pathString, cmd
            query = lineSplit[2]
            fileTarget = lineSplit[3]
            pathString = os.path.join(deployDataUrl, fileTarget)
            cmd = (
                "sfdx force:data:soql:query --apiversion "
                + defaultApiVersion
                + " -u "
                + target
                + " -q "
                + query
                + " -r csv"
            )
            if (platform.system() != "Windows"):
                cmd = ("/usr/local/bin/sfdx force:data:soql:query --apiversion "
                + defaultApiVersion
                + " -u "
                + target
                + " -q "
                + query
                + " -r csv"
            )
        if lineSplit[1] == "BULKDELETE":
            if len(lineSplit) < 5:
                error = True
                errorMsg = "Expected more values in script at line " + lineNumber + ": " + lineStr
                return error, errorMsg, target, pathString, cmd
            customObject = lineSplit[2]
            fileTarget = lineSplit[3]            
            waitTime = lineSplit[4]
            fileToReplaceContentUrl = fileTarget
            if "{gitroot}" in fileTarget:
                splitFileToReplaceContentUrl = fileTarget.split("{gitroot}")
                if len(splitFileToReplaceContentUrl) > 1:
                    fileToReplaceContentUrl = os.path.join(deployStageUrl, splitFileToReplaceContentUrl[1])
                    pathString = os.path.join(deployDataUrl, PathLeaf(fileToReplaceContentUrl))
                    if not os.path.exists(pathString):
                        shutil.copy(fileToReplaceContentUrl, deployDataUrl)
            pathString = os.path.join(deployDataUrl, PathLeaf(fileToReplaceContentUrl))
            if not os.path.exists(pathString):
                error = True
                errorMsg = "File specified not found on line " + lineNumber + ": " + lineStr
                return error, errorMsg, target, pathString, cmd
            cmd = [
                "sfdx",
                "force:data:bulk:delete",
                "--apiversion",
                defaultApiVersion,
                "-u",
                target,
                "-s",
                customObject,
                "-f",
                pathString,
                "-w",
                waitTime
            ]
            if (platform.system() != "Windows"):
                cmd = ["/usr/local/bin/sfdx" + " " + "force:data:bulk:delete" + " " + "--apiversion" + " " + defaultApiVersion + " " + "-u" + " " + target + " " + "-s" + " " + customObject + " " + "-f" + " " + pathString + " " + "-w" + " " + waitTime]
        if lineSplit[1] == "BULKUPSERT":
            if len(lineSplit) < 6:
                error = True
                errorMsg = "Expected more values in script at line " + lineNumber + ": " + lineStr
                return error, errorMsg, target, pathString, cmd
            customObject = lineSplit[2]
            fileTarget = lineSplit[3]
            externalId = lineSplit[4]
            waitTime = lineSplit[5]
            fileToReplaceContentUrl = fileTarget
            if "{gitroot}" in fileTarget:
                splitFileToReplaceContentUrl = fileTarget.split("{gitroot}")
                if len(splitFileToReplaceContentUrl) > 1:
                    fileToReplaceContentUrl = os.path.join(deployStageUrl, splitFileToReplaceContentUrl[1])
                    pathString = os.path.join(deployDataUrl, PathLeaf(fileToReplaceContentUrl))
                    if not os.path.exists(pathString):
                        shutil.copy(fileToReplaceContentUrl, deployDataUrl)
            pathString = os.path.join(deployDataUrl, PathLeaf(fileToReplaceContentUrl))
            if not os.path.exists(pathString):
                error = True
                errorMsg = "File specified not found on line " + str(lineNumber) + ": " + lineStr
                return error, errorMsg, target, pathString, cmd
            cmd = [
                "sfdx",
                "force:data:bulk:upsert",
                "--apiversion",
                defaultApiVersion,
                "-u",
                target,
                "-s",
                customObject,
                "-i",
                externalId,
                "-f",
                pathString,
                "-w",
                waitTime
            ]
            if (platform.system() != "Windows"):
                cmd = ["/usr/local/bin/sfdx" + " " + "force:data:bulk:upsert" + " " + "--apiversion" + " " + defaultApiVersion + " " + "-u" + " " + target + " " + "-s" + " " + customObject + " " + "-i" + " " + externalId + " " + "-f" + " " + pathString + " " + "-w" + " " + waitTime]
        if lineSplit[1] == "RECORDCREATE":
            if len(lineSplit) < 4:
                error = True
                errorMsg = "Expected more values in script at line " + lineNumber + ": " + lineStr
                return error, errorMsg, target, pathString, cmd
            customObject = lineSplit[2]
            values = lineSplit[3]
            cmd = [
                "sfdx",
                "force:data:record:create",
                "--apiversion",
                defaultApiVersion,
                "-u",
                target,
                "-s",
                customObject,
                "-q",
                '"' + values + '"',
            ]
            cmd = (
                "sfdx force:data:record:create --apiversion "
                + defaultApiVersion
                + " -u "
                + target
                + " -s "
                + customObject
                + " -q "
                + values
            )
            if (platform.system() != "Windows"):
                cmd = ("/usr/local/bin/sfdx force:data:record:create --apiversion "
                + defaultApiVersion
                + " -u "
                + target
                + " -s "
                + customObject
                + " -q "
                + values
            )
        if lineSplit[1] == "RECORDDELETE":
            customObject = lineSplit[2]
            values = lineSplit[3]
            externalId = lineSplit[4]
            cmd = (
                "sfdx force:data:record:delete --apiversion "
                + defaultApiVersion
                + " -u "
                + target
                + " -s "
                + customObject
                + " -i "
                + values
                )
            if (platform.system() != "Windows"):
                cmd = ("/usr/local/bin/sfdx force:data:record:delete --apiversion "
                + defaultApiVersion
                + " -u "
                + target
                + " -s "
                + customObject
                + " -i "
                + values
                )
            if externalId == "values":
                cmd = (
                    "sfdx force:data:record:delete --apiversion "
                    + defaultApiVersion
                    + " -u "
                    + target
                    + " -s "
                    + customObject
                    + " -w "
                    + values
                )
                if (platform.system() != "Windows"):
                    cmd = ("/usr/local/bin/sfdx force:data:record:delete --apiversion "
                        + defaultApiVersion
                        + " -u "
                        + target
                        + " -s "
                        + customObject
                        + " -w "
                        + values
                    )
        if lineSplit[1] == "RECORDUPDATE":
            if len(lineSplit) < 6:
                error = True
                errorMsg = "Expected more values in script at line " + lineNumber + ": " + lineStr
                return error, errorMsg, target, pathString, cmd
            customObject = lineSplit[2]
            externalId = lineSplit[3]
            values = lineSplit[4]
            valuesToUpdate = lineSplit[5]
            cmd = (
                "sfdx force:data:record:update --apiversion "
                + defaultApiVersion
                + " -u "
                + target
                + " -s "
                + customObject
                + " -i "
                + values
                + " -v "
                + valuesToUpdate
            )
            if (platform.system() != "Windows"):
                cmd = ("/usr/local/bin/sfdx force:data:record:update --apiversion "
                + defaultApiVersion
                + " -u "
                + target
                + " -s "
                + customObject
                + " -i "
                + values
                + " -v "
                + valuesToUpdate
                )
            if externalId == "values":
                cmd = (
                    "sfdx force:data:record:update --apiversion "
                    + defaultApiVersion
                    + " -u "
                    + target
                    + " -s "
                    + customObject
                    + " -w "
                    + values
                    + " -v "
                    + valuesToUpdate
                )
                if (platform.system() != "Windows"):
                    cmd = ("/usr/local/bin/sfdx force:data:record:update --apiversion "
                        + defaultApiVersion
                        + " -u "
                        + target
                        + " -s "
                        + customObject
                        + " -w "
                        + values
                        + " -v "
                        + valuesToUpdate
                        )
        if lineSplit[1] == "APEXEXECUTE":
            fileTarget = lineSplit[2]
            fileToReplaceContentUrl = fileTarget
            if "{gitroot}" in fileTarget:
                splitFileToReplaceContentUrl = fileTarget.split("{gitroot}")
                if len(splitFileToReplaceContentUrl) > 1:
                    fileToReplaceContentUrl = os.path.join(deployStageUrl, splitFileToReplaceContentUrl[1])
                    pathString = os.path.join(deployDataUrl, PathLeaf(fileToReplaceContentUrl))
                    if not os.path.exists(pathString):
                        shutil.copy(fileToReplaceContentUrl, deployDataUrl)
            pathString = os.path.join(deployDataUrl, PathLeaf(fileToReplaceContentUrl))
            if not os.path.exists(pathString):
                error = True
                errorMsg = "File specified not found on line " + str(lineNumber) + ": " + lineStr
                return error, errorMsg, target, pathString, cmd
            cmd = ["sfdx", "force:apex:execute", "--apiversion", defaultApiVersion, "-u", target, "-f", pathString]
            if (platform.system() != "Windows"):
                cmd = ["/usr/local/bin/sfdx" + " " + "force:apex:execute" + " " + "--apiversion" + " " + defaultApiVersion + " " + "-u" + " " + target + " " + "-f" + " " + pathString]
    else:
        error = True
        errorMsg = "Expected more values in script at line " + lineNumber + ": " + lineStr
    return error, errorMsg, target, pathString, cmd


def ProcessMetadataScriptLine(lineSplit, lineStr, targetName, sourceName, deployDataUrl, lineNumber, deployStageUrl):
    error = False
    errorMsg = ""
    cmd = []
    target = ""
    pathString = ""
    if len(lineSplit) >= 1:
        if lineSplit[0] == "SOURCE":
            target = sourceName
        if lineSplit[0] == "TARGET":
            target = targetName
    else:
        error = True
        errorMsg = "Expected more values in script at line " + lineNumber + ": " + lineStr
        return error, errorMsg, target, pathString, cmd

    if lineSplit[1] == "DEPLOYZIP":
        if len(lineSplit) < 8:
            error = True
            errorMsg = "Expected more values in script at line " + lineNumber + ": " + lineStr
            return error, errorMsg, target, pathString, cmd
        fileTarget = lineSplit[2]
        testLevel = lineSplit[3]
        checkOnly = lineSplit[4]
        ignoreWarnings = lineSplit[5]
        ignoreErrors = lineSplit[6]
        waitParam = lineSplit[7]
        deployType = "Zip"
        zipFileToDeployUrl = fileTarget
        if "{gitroot}" in fileTarget:
            splitZipFileToDeployUrl = fileTarget.split("{gitroot}")
            if len(splitZipFileToDeployUrl) > 1:
                zipFileToDeployUrl = os.path.join(deployStageUrl, splitZipFileToDeployUrl[1])
                pathString = os.path.join(deployDataUrl, PathLeaf(zipFileToDeployUrl))
                if not os.path.exists(pathString):
                    shutil.copy(zipFileToDeployUrl, deployDataUrl)
        pathString = os.path.join(deployDataUrl, PathLeaf(zipFileToDeployUrl))
        if not os.path.exists(pathString):
            error = True
            errorMsg = "File specified not found on line " + str(lineNumber) + ": " + lineStr
            return error, errorMsg, target, pathString, cmd
        if testLevel not in testRunTypes:
            error = True
            errorMsg = "TestRun type not supported on line " + str(lineNumber) + ": " + lineStr
            return error, errorMsg, target, pathString, cmd
        if checkOnly not in ["YES","NO"]:
            error = True
            errorMsg = "Check only (YES,NO) not supported on line " + str(lineNumber) + ": " + lineStr
            return error, errorMsg, target, pathString, cmd
        if ignoreWarnings not in ["YES","NO"]:
            error = True
            errorMsg = "Ignore warnings (YES,NO) not supported on line " + str(lineNumber) + ": " + lineStr
            return error, errorMsg, target, pathString, cmd
        if ignoreErrors not in ["YES","NO"]:
            error = True
            errorMsg = "Ignore errors (YES,NO) not supported on line " + str(lineNumber) + ": " + lineStr
            return error, errorMsg, target, pathString, cmd  
    return error, errorMsg, target, pathString, cmd        


def getImageStream():
    img_b64 = """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"""
    img = base64.b64decode(img_b64)
    return io.BytesIO(img)


def StoreMetadataTemplates():
    global metadataTemplatesFileName
    completeName = metadataTemplatesFileName
    directory = os.path.join(os.path.expanduser("~"), ".dtkconfig")
    if not os.path.exists(directory):
        os.makedirs(directory)
    metadataTemplatesFileUrl = os.path.join(directory, completeName)
    metadataTemplatesFile = open(metadataTemplatesFileUrl, "wb")
    strMetadataTemplates = json.dumps(metadataTemplatesSelection, indent=4, sort_keys=True)
    binaryMetadataTemplates = strMetadataTemplates.encode()
    metadataTemplatesFile.write(binaryMetadataTemplates)
    metadataTemplatesFile.close()
    ReadMetadataTemplates()


def LoadMetadataTemplates():
    global metadataTemplatesFileName
    completeName = metadataTemplatesFileName
    metadataTemplatesFileUrl = os.path.join(os.path.expanduser("~"), ".dtkconfig", completeName)
    if not os.path.exists(metadataTemplatesFileUrl):
        thread = threading.Thread(target=CreateMetadataTemplatesDefault)
        thread.setDaemon(True)
        thread.start()
    else:
        ReadMetadataTemplates()


def ReadMetadataTemplates():
    global metadataTemplatesFileName
    global metadataTemplates
    global metadataTemplatesSelection
    completeName = metadataTemplatesFileName
    directory = os.path.join(os.path.expanduser("~"), ".dtkconfig")
    if not os.path.exists(directory):
        return
    metadataTemplatesFileUrl = os.path.join(directory, completeName)
    metadataTemplatesFile = open(metadataTemplatesFileUrl, "r", encoding="utf8")
    metadataTemplatesSelection = json.loads(metadataTemplatesFile.read())
    metadataTemplatesFile.close()
    metadataTemplates = []
    metadataTemplates.append("All")
    metadataTemplates.append("None")
    for mdTemplate in metadataTemplatesSelection:
        metadataTemplates.append(mdTemplate)


def CreateMetadataTemplatesDefault():
    global metadataTemplatesFileName
    completeName = metadataTemplatesFileName
    directory = os.path.join(os.path.expanduser("~"), ".dtkconfig")
    if not os.path.exists(directory):
        os.makedirs(directory)
    outputFileUrl = os.path.join(directory, completeName)
    outputFile = open(outputFileUrl, "wb")
    metadataTemplatesDump = json.dumps(metadataTemplatesSelection, indent=4, sort_keys=True)
    metadataTemplatesEncoded = metadataTemplatesDump.encode()
    outputFile.write(metadataTemplatesEncoded)
    outputFile.close()
    fileOutput = open(outputFileUrl, "r", encoding="utf8")
    fileOutput.close()
    ReadMetadataTemplates()


def StoreSOQLTemplates():
    global SOQLTemplatesFileName
    completeName = SOQLTemplatesFileName
    directory = os.path.join(os.path.expanduser("~"), ".dtkconfig")
    if not os.path.exists(directory):
        os.makedirs(directory)
    soqlTemplatesFileUrl = os.path.join(directory, completeName)
    soqlTemplatesFile = open(soqlTemplatesFileUrl, "wb")
    strSOQLTemplates = json.dumps(soqlDict, indent=4, sort_keys=True)
    binarySOQLTemplates = strSOQLTemplates.encode()
    soqlTemplatesFile.write(binarySOQLTemplates)
    soqlTemplatesFile.close()
    ReadSOQLTemplates()


def LoadSOQLTemplates():
    global SOQLTemplatesFileName
    completeName = SOQLTemplatesFileName
    soqlTemplatesFileUrl = os.path.join(os.path.expanduser("~"), ".dtkconfig", completeName)
    if not os.path.exists(soqlTemplatesFileUrl):
        thread = threading.Thread(target=CreateSOQLTemplatesDefault)
        thread.setDaemon(True)
        thread.start()
    else:
        ReadSOQLTemplates()


def ReadSOQLTemplates():
    global SOQLTemplatesFileName
    global soqlList
    global soqlDict
    completeName = SOQLTemplatesFileName
    directory = os.path.join(os.path.expanduser("~"), ".dtkconfig")
    if not os.path.exists(directory):
        return
    soqlTemplatesFileUrl = os.path.join(directory, completeName)
    soqlTemplatesFile = open(soqlTemplatesFileUrl, "r", encoding="utf8")
    soqlDict = json.loads(soqlTemplatesFile.read())
    soqlTemplatesFile.close()
    soqlList = []
    for soqlTemplate in soqlDict:
        soqlList.append(soqlTemplate)


def CreateSOQLTemplatesDefault():
    global SOQLTemplatesFileName
    completeName = SOQLTemplatesFileName
    directory = os.path.join(os.path.expanduser("~"), ".dtkconfig")
    if not os.path.exists(directory):
        os.makedirs(directory)
    outputFileUrl = os.path.join(directory, completeName)
    outputFile = open(outputFileUrl, "wb")
    soqlTemplatesDump = json.dumps(soqlDict, indent=4, sort_keys=True)
    soqlTemplatesEncoded = soqlTemplatesDump.encode()
    outputFile.write(soqlTemplatesEncoded)
    outputFile.close()
    fileOutput = open(outputFileUrl, "r", encoding="utf8")
    fileOutput.close()
    ReadSOQLTemplates()

#Accelerate Integration: Load Configuration
def LoadAccelerateConfiguration():
    directory = os.path.join(os.path.expanduser("~"), ".dtkconfig")
    AccelerateDeployConfiguration = os.path.join(directory, "AccelerateDeployConfiguration")
    if os.path.exists(AccelerateDeployConfiguration):
        shutil.rmtree(AccelerateDeployConfiguration,onerror=RemoveReadonly)

    global gitPreffix
    global gitSuffix
    accelerateGitURLSptl = accelerateGitURL.split("//")
    if len(accelerateGitURLSptl) > 1:
            gitPreffix = accelerateGitURLSptl[0] + "//"
            gitSuffix = accelerateGitURLSptl[1]

    gitAcceleratelUrl = gitPreffix + accelerateGitUser + ":" + accelerateGitPassword + "@" + gitSuffix

    if accelerateDevEnableSetting:
        gitBranch = 'dtkConfiguration4Developers'
    else:
        gitBranch = 'dtkConfiguration'

    cmd = ["git", "clone", "--single-branch", "--branch", gitBranch, gitAcceleratelUrl, AccelerateDeployConfiguration]
    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE
    )
    proc.wait()
    return ReadAccelerateDtkCfg(AccelerateDeployConfiguration)

def ReadAccelerateDtkCfg(directory):
    completeName = "dtkConfiguration.json"
    orgFileUrl = os.path.join(directory, completeName)
    if not os.path.exists(orgFileUrl):
        return False
    orgFile = open(orgFileUrl, "r", encoding="utf8")
    global dtkAccelerateCfg
    dtkAccelerateCfg = json.loads(orgFile.read())
    orgFile.close()

    global accelerateGitBranch
    global accelerateMetadataGitFolder
    global acceleratePreDeployScriptFile
    global acceleratePostDeployScriptFile
    global accelerateVersion
    global confluenceURL
    global activationScriptName
    global postMasterDataFolder
    global postMasterDataScript
    global accelerateModulesAvailable

    for config in dtkAccelerateCfg:    
        if config == 'gitBranch':
            accelerateGitBranch = dtkAccelerateCfg[config]
        elif config == 'metadataGitFolder':
            accelerateMetadataGitFolder = dtkAccelerateCfg[config]
        elif config == 'preDeployScriptFile':
            acceleratePreDeployScriptFile = dtkAccelerateCfg[config]
        elif config == 'postDeployScriptFile':
            acceleratePostDeployScriptFile = dtkAccelerateCfg[config]
        elif config == 'version':
            accelerateVersion = dtkAccelerateCfg[config]
        elif config == 'confluenceURL':
            confluenceURL = dtkAccelerateCfg[config]
        elif config == 'activationScriptName':
            activationScriptName = dtkAccelerateCfg[config]
        elif config == 'postMasterDataFolder':
            postMasterDataFolder = dtkAccelerateCfg[config]
        elif config == 'postMasterDataScript':
            postMasterDataScript = dtkAccelerateCfg[config]
        elif config == 'modulesAvailable':
            accelerateModulesAvailable = dtkAccelerateCfg[config]
        else:
            print(dtkAccelerateCfg[config])
    return True