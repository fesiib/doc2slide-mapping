import os

SLIDE_DATA_PATH = "./slideData"
TH_PATH = "./talkingHeads"


def main():
    for filename in os.listdir(SLIDE_DATA_PATH):
        path = os.path.join(SLIDE_DATA_PATH, filename)
        if os.path.isdir(path) is False:
            continue
        th_path = os.path.join(path, "talkingHeadMask.json")

        new_path = os.path.join(TH_PATH, filename)
        os.makedirs(new_path, exist_ok=True)
        
        os.system("cp " + th_path + " " + new_path + "/")

if __name__ == "__main__":
    main()

