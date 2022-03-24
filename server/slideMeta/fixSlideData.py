import os

SLIDE_DATA_PATH = "./slideData"
TH_PATH = "./talkingHeads"

def copy_ths():
    for filename in os.listdir(SLIDE_DATA_PATH):
        path = os.path.join(SLIDE_DATA_PATH, filename)
        if os.path.isdir(path) is False:
            continue
        th_path = os.path.join(path, "talkingHeadMask.json")

        new_path = os.path.join(TH_PATH, filename)
        os.makedirs(new_path, exist_ok=True)
        
        os.system("cp " + th_path + " " + new_path + "/")

def paste_ths():
    for filename in os.listdir(TH_PATH):
        path = os.path.join(TH_PATH, filename)
        th_path = os.path.join(path, "talkingHeadMask.json")
        
        if os.path.isfile(th_path) is False:
            continue

        new_path = os.path.join(SLIDE_DATA_PATH, filename)
        
        os.system("cp " + th_path + " " + new_path + "/")

def main():
    paste_ths()    

if __name__ == "__main__":
    main()

