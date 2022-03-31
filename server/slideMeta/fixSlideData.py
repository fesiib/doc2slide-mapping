import os
import json
from string import digits
import fitz

SLIDE_DATA_PATH = "./slideData"
SLIDE_DATA_2_PATH = "./slideData2"
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

    def olTraversal(root):
        nodes = [root]
        while nodes:
            node = nodes.pop()
            print("[OUTLINE]- %s ==> %d" % (node.title, node.dest.page))
            print()
            next = node.next
            if next:
                nodes.append(next)
            else:
                print("[OUTLINE]<")
            down = node.down
            if down:
                print("[OUTLINE]>")
                nodes.append(down)

    default_titles = ["ABSTRACT", "CCS CONCEPTS", "KEYWORDS"]

    for id, ids in bad_section:
        print(id)
        path = os.path.join(SLIDE_DATA_PATH, id, "paper.pdf")
        with fitz.open(path) as pdf:
            toc = pdf.get_toc(simple=False)

            for lvl, title, page_num, dest in toc:
                print(title, dest["to"])
                xref = dest["xref"]
                for key in pdf.xref_get_keys(xref):
                    print(key, "=" , pdf.xref_get_key(xref, key))

            contents = [[] for i in range(len(toc))]
            toc_idx = 0
            pages = pdf.pages()
            for page in pages:
                if toc_idx == len(toc):
                    break

                blocks = page.get_text("blocks")
                for block in blocks:
                    print(block)
        break

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

def paste_slide_data_2():
    for filename in os.listdir(SLIDE_DATA_2_PATH):
        path = os.path.join(SLIDE_DATA_2_PATH, filename)

        new_path = os.path.join(SLIDE_DATA_PATH, filename)
        
        os.system("cp -r " + path + "/* " + new_path + "/")


def main():
    paste_slide_data_2()

if __name__ == "__main__":
    main()

