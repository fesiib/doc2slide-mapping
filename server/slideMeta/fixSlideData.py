import os
import json
from string import digits

SLIDE_DATA_PATH = "./slideData"
TH_PATH = "./talkingHeads"
SLIDE_IMAGES_PATH = "./slideDataImages"

def fix_paper_data():
    def get_main_section(title):
        title_parts = title.strip().split(" ")
        if (title_parts[0] in digits) is False:
            return False
        for title_part in title_parts[1:]:
            if len(title_part) < 2: 
                continue
            elif title_part.isupper() is True or title_part in digits:
                break
            else:
                return False
        return True

    no_section = []
    bad_section = []

    for filename in os.listdir(SLIDE_DATA_PATH):
        path = os.path.join(SLIDE_DATA_PATH, filename, "paperData.json")

        if os.path.isfile(path) is False:
            continue

        if (int(filename) >= 100000):
            continue

        paper_data_json = {}

        with open(path, "r") as f:
            paper_data_json = json.load(f)

        section_ids = {}

        if "sections" in paper_data_json:
            for section in paper_data_json["sections"]:
                if "title" in section and "text" in section["title"]:
                    title = section["title"]["text"]
                    if get_main_section(title) is True:
                        title_parts = title.strip().split(" ")
                        id = -1
                        try:
                            id = int(title_parts[0])
                        except:
                            id = -1
                        if id < 0:
                            #raise ValueError(title_parts)
                            continue
                        section_ids[id] = title

        ids = sorted(section_ids.keys())
        if len(ids) == 0:
            no_section.append(filename)
            continue
        if len(ids) != ids[-1]:
            bad_section.append((filename, section_ids))
    print(bad_section[0])

def paste_images():
    for filename in os.listdir(SLIDE_IMAGES_PATH):
        path = os.path.join(SLIDE_IMAGES_PATH, filename)
        if os.path.isdir(path) is False:
            continue

        new_path = os.path.join(SLIDE_DATA_PATH, filename)
        
        os.system("cp " + path + "/* " + new_path + "/")

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
    fix_paper_data()    

if __name__ == "__main__":
    main()

