import os
import json
from string import digits
import fitz
import re

SLIDE_DATA_PATH = "./slideData"
SLIDE_DATA_2_PATH = "./slideData2"
TH_PATH = "./talkingHeads"
SLIDE_IMAGES_PATH = "./slideDataImages"

def fix_paper_data():

    all_ids = []

    for filename in os.listdir(SLIDE_DATA_PATH):
        path = os.path.join(SLIDE_DATA_PATH, filename, "paperData.json")
        if os.path.isfile(path) is False:
            continue
        # if (int(filename) >= 100000):
        #     continue
        all_ids.append(int(filename))

    all_ids = sorted(all_ids)
    bad_ids = []

    def remove_space(text):
        return re.sub("\s+", " ", text)

    for id in all_ids[200:]:
        print(id)
        
        toc = []
        toc_path = os.path.join(SLIDE_DATA_PATH, str(id), "TOC.json")
        with open(toc_path, "r") as f:
            toc_json = json.load(fp = f)
            toc = toc_json["toc"]
        if len(toc) == 0:
            bad_ids.append(id)
            continue

        pdf_path = os.path.join(SLIDE_DATA_PATH, str(id), "paper.pdf")
        with fitz.open(pdf_path) as pdf:
            section_data = []
            visual_data = []
            paper_data = []
            all_lines = []

            for page in pdf.pages():
                text = page.get_text("text")
                lines = text.split("\n")
                filtered_lines = []
                for line in lines:
                    line = line.strip()
                    if "CHI \u201921" in line:
                        print(line)
                        continue
                    # title
                    if len(paper_data) > 0 and paper_data[0].lower() in line.lower():
                        print(line)
                        continue
                    filtered_lines.append(line)
                all_lines.extend(filtered_lines)
                
                # blocks = page.get_text("blocks")
                # paper_data.extend(blocks)

            entire_text = " ".join(all_lines)
            entire_text = remove_space(entire_text.strip())
            entire_text = re.sub("-\s", "", entire_text)

            last_cut = 0
            section_data.append("TITLE")
            paper_data_range = [[0, len(entire_text)]]

            for i in range(len(toc)):
                if toc[i]["level"] != 1:
                    continue
                title = remove_space(toc[i]["title"].strip())
                title = title.upper()
                idx = entire_text[last_cut:].find(title) + last_cut
                section_data.append(title)
                paper_data_range[-1][1] = idx
                paper_data_range.append([idx, len(entire_text)])
                last_cut = idx

            for i, cur_range in enumerate(paper_data_range):
                paper_data.append(entire_text[cur_range[0]:cur_range[1]])
                if str(len(paper_data[-1])) == 0:
                    print("Couldn't: ", section_data[i])
                visual_data.append(section_data[i] + " --> " + str(len(paper_data[-1])))

            with open(os.path.join(SLIDE_DATA_PATH, str(id), "readerData.json"), "w") as f:
                json.dump({
                    "visualData": visual_data,
                    "toc": toc,
                    "sectionData": section_data,
                    "paperData": paper_data, 
                }, fp=f, indent=2)

def get_tocs():
    all_ids = []

    for filename in os.listdir(SLIDE_DATA_PATH):
        path = os.path.join(SLIDE_DATA_PATH, filename, "paperData.json")
        if os.path.isfile(path) is False:
            continue
        all_ids.append(int(filename))

    all_ids = sorted(all_ids)

    for id in all_ids:
        print(id)
        pdf_path = os.path.join(SLIDE_DATA_PATH, str(id), "paper.pdf")
        with fitz.open(pdf_path) as pdf:
            toc = pdf.get_toc(simple=True)
            struct_toc = []
            for lvl, title, page in toc:
                struct_toc.append({
                    "level": lvl,
                    "title": title,
                    "page": page,
                })
            with open(os.path.join(SLIDE_DATA_PATH, str(id), "TOC.json"), "w") as f:
                json.dump({
                    "toc": struct_toc,
                }, fp=f, indent=2)

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

def bad_paper_data():
    no_sections = []
    no_number = []
    bad_sections = []
    no_conclusion = []
    for filename in os.listdir(SLIDE_DATA_PATH):
        path = os.path.join(SLIDE_DATA_PATH, filename, "result.json")
        if os.path.isfile(path) is False:
            continue
        with open(path, "r") as f:
            result_json = json.load(fp=f)
            section_titles = result_json["sectionTitles"]
            if len(section_titles) == 0:
                no_sections.append((int(filename), []))
                continue
            last_id_str = section_titles[-1].strip().split(" ")[0]
            if last_id_str.isnumeric() is False:
                no_number.append((int(filename), section_titles))
                continue
            if int(last_id_str) != len(section_titles):
                bad_sections.append((int(filename), section_titles))
                continue
            if "conclusion" not in section_titles[-1].lower():
                no_conclusion.append((int(filename), section_titles))
                continue
    no_sections = sorted(no_sections, key=(lambda x: x[0]))
    no_number = sorted(no_number, key=(lambda x: x[0]))
    bad_sections = sorted(bad_sections, key=(lambda x: x[0]))
    no_conclusion = sorted(no_conclusion, key=(lambda x: x[0]))

    for id, titles in bad_sections:
        # print("\t", id)
        # for i, title in enumerate(titles):
        #     print(i, ":", title)
        print(id, end=', ')

def main():
    fix_paper_data()

if __name__ == "__main__":
    main()

