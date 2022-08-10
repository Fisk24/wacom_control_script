import os, re

def main():
    basedir = "/usr/share/libwacom/"
    dirList = os.listdir(basedir)
    for file in dirList:
        if file == "__pycache__":
            continue
        fullfile   = os.path.join(basedir, file)
        tabletName = "None"
        modelName  = "None"
        if not os.path.isdir(fullfile):
            with open(fullfile, "r") as tablet:
                contents = tablet.readlines()
                for line in contents:
                    modelMatch = re.search(r"^ModelName=", line)
                    nameMatch  = re.search(r"^Name=", line)
                    if nameMatch != None:
                        tabletName = line.strip("\n").split("=")[-1]
                        if tabletName == "":
                            tabletName = "None"
                    if modelMatch != None:
                        modelName = line.strip("\n").split("=")[-1]
                        if modelName == "":
                            modelName = "None"
        print("tablet:",tabletName, modelName, fullfile)

if __name__ == '__main__':
    main()
