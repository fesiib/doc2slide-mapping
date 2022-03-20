
def sort_section_data(section_data):
    label_list = sorted(list(set(section_data)))

    # for i, label in enumerate(label_list):
    #     print(i, ":", label)

    section_ids = {}
    rest = []
    for title in section_data:
        title_parts = title.strip().split(" ")
        id = -1
        try:
            id = int(title_parts[0])
        except:
            id = -1
        if id < 0:
            #raise ValueError(title_parts)
            rest.append(title)
            continue
        section_ids[id] = title

    rest = list(set(rest))

    ids = sorted(section_ids.keys())

    label_list = []

    for i, key in enumerate(ids):
        # if i + 1 != key:
        #     raise ValueError(str(i + 1) + " != " + str(key))
        label_list.append(section_ids[key])
    label_list.extend(rest)
    return label_list