import os
import json

#from evaluate_outline import evaluate_outline

YK_IDS = [
    "1bd9f9c0a6b343c584cbfc882325edb7",
    "547dc6d4788f4eea9a0dd109a11b9fb5",
    "d4ffd82aa2da44dca54945b851d2ef1b",
    "4313977a266a4429af1241f98f2f1390",
    "550d025f94ef4af8ab517f74dea87673",
    "40e6da689d26490285b2e2dd07699675",
    "95a993219864455f8751651e2fd6a36e",
    "6c662c055b5049fb91dfa6bc981483b0",
    "bc12457c083049ab9556d6e540e42dc8",
    "a61a49fdc0b548fd807559b5df8a5150",
    "6299b0345fdb471eac81c7c1272a81d4",
    "5b98ff662df542f99349aa37bc2c23ba",
    "ab73993e8c54451e80bc2fa5657b1f5c",
    "8001d7afc01c40f0a891849ecd24a9bb",
    "0e8ebbac5af24c56bf83bb44512e65c1",
    "22f17291e995489dac4286953017e200",
    "9c4c114f954f4df3a2fb642c60f36ea1",
    "b56a6b3040554defa3b0b7bd9ad495ca",
    "ed4ad71f093542f7ac9445d80dc48b15",
    "8a73fb66ce2c46088d2a046b7ca5f415"
]

TK_IDS = [
    "c243ff2d812a4690b47eb88eee171b69",
    "fee8171c4e9341e3a44f4f6f275676da",
    "a945291fd6af4386804737ff748cbfe4",
    "6af799e7e57e4c35afdd55b21d33d1a2",
    "db4e32cfdef74398a4cb03b8efb9030d",
    "c07e98e625fc429aad04c316145a71f1",
    "87ac696a66424386a3677f1637e5290a",
    "01dacdf28ddc4349b40367886df78a30",
    "ee2f1018db4c43a195d089f278e0bdd9",
    "b5873cb4eff049a48868d19f67cf8f30",
    "dd793dd7142047ecb7de6b979c3673c7",
    "f30779ba98864c388a7efa5f819a1464",
    "1d0cbfb7e7cb4fe08abaec5e8fbdc948",
    "0ff3153c3aca4fb9a19faac9a6263040",
    "bcdacd44a1e6404bb4d6e59b849338d4",
    "3009e155360e4da7a144f9a0ff0fd294",
    "94c8ecd28840497792174edc2461fa57",
    "edc4882e277346f5aa67cfef5f34d858",
    "f50dbffa8720430fbf3cf453cb641be2",
    "db8c6fd14aa9455fbdde80907e4a2d3b"
]

GT_IDS = [
    "76ae45e5777b435dbfdaee47e2604776",
    "22dc9b0cb2fe40a39c7e0b1e7b958bcc",
    "e5ccf9fdfb364f5d8bfe422eec670b31",
    "c18627fe560c422db6d031d314f7f061",
    "a00c10f2018243b399b9d22422eb8d98",
    "8e0d9d5a3d934b88b845b307bd3223f4",
    "7f0b3d3730c5450fafb74a679a2cb2c0",
    "bc79e114364548d3b218d61e012c0497",
    "5b67c51043d14201b59174c34c381cfb",
    "803d26bb81424cb5a104053a63038b6e",
    "bc6916334bec446297aca9cca6aa18e0",
    "c0d2ef836544477c9a7f9349b3820a82",
    "89aaeccc469c41a689d5ef83ce84ed96",
    "b8f103c0df094974bb03408567b9b44b",
    "c289f50005104aa7856d2ae65b8bb939",
    "2aacb5c6544d4cfc9ae6e47b8ecc7624",
    "3dec867ef20c4008bd93209c68faea04",
    "e9a12118b19a4012a795ddacdeca6218",
    "ab6c2b89e5874a48ac7ee9aac7a46997",
    "7f190d8aa26b48d58d0cb612152d7644",
]

def read_json(path):
    obj = {}
    with open(path, 'r') as f:
        encoded = f.read()
        try:
            obj = json.loads(encoded)
        except:
            obj = {}
    return obj   

def scan_annotations(path):
    if os.path.exists(path) is False:
        return {}
    annotations = {}
    for filename in os.listdir(path):
        if filename.endswith('.json'):
            id = filename.split('.')[0]
            obj = read_json(os.path.join(path, filename))
            annotations[id] = obj["groundTruthSegments"]
    return annotations

if __name__ == "__main__":
    lst = [439, 510, 90, 589, 674, 689, 549, 13, 307, 477, 106, 161, 271, 214, 147, 318, 372, 46, 231, 504]

    lst = sorted(lst)

    # in_order = []

    # for filename in lst:
    #     found = False
    #     for id in yk_ids:
    #         path = os.path.join("./slideMeta/slideData/", str(filename), "annotations", id + ".json")
    #         if os.path.isfile(path) is False:
    #             continue
    #         in_order.append(id)
    #         found = True
    #         break
    #     if found is False:
    #         print("No :", filename)
    #         in_order.append("empty")
    
    # print(json.dumps(in_order, indent=2))

    # for id, filename in zip(GT_IDS, lst):
    #     path = os.path.join("./slideMeta/slideData/", str(filename), "annotations", id + ".json")
    #     if os.path.isfile(path) is False:
    #         print(path)
    #         continue

    #     gt_path = os.path.join("./slideMeta/slideData/", str(filename), "groundTruth.json")

    #     with open(path, "r") as src:
    #         obj = json.load(src)
    #         with open(gt_path, 'w') as dst:
    #             json.dump(obj, dst, indent=2)

    slides_evaluation_overall = [[[0, 100, -1] for j in range(3)] for i in range(3)]
    slides_evaluation_separate = [[[[0, 100, -1] for k in range(3)] for j in range(3)] for i in range(3)]


    time_evaluation_overall = [[[0, 100, -1] for j in range(3)] for i in range(3)]
    time_evaluation_separate = [[[[0, 100, -1] for k in range(3)] for j in range(3)] for i in range(3)]


    def update_sum_min_max(triplet, score):
        triplet[0] += score
        triplet[1] = min(triplet[1], score)
        triplet[2] = max(triplet[2], score)
        return triplet
    
    for i, presentation_id in enumerate(lst):
        path = os.path.join("./slideMeta/slideData/", str(presentation_id))

        slide_info = []

        with open(os.path.join(path, "result.json"), "r") as f:
            json_obj = json.load(f)
            slide_info = json_obj["slideInfo"]

        ids = [TK_IDS[i], YK_IDS[i], GT_IDS[i]]
        annotations = []
        for id in ids:
            with open(os.path.join(path, "annotations", id + ".json"), "r") as f:
                json_obj = json.load(f)
                annotations.append(json_obj["groundTruthSegments"])

        for ix in range(3):
            for jx in range(3):
                if ix == jx:
                    continue
                evaluation_result = evaluate_outline(annotations[ix], annotations[jx], slide_info, [])

                slides_evaluation_overall[ix][jx] = update_sum_min_max(slides_evaluation_overall[ix][jx], evaluation_result["overallSlidesAccuracy"])
                for k in range(3):
                    slides_evaluation_separate[ix][jx][k] = update_sum_min_max(slides_evaluation_separate[ix][jx][k], evaluation_result["separateSlidesAccuracy"][k])
                

                time_evaluation_overall[ix][jx] = update_sum_min_max(time_evaluation_overall[ix][jx], evaluation_result["overallTimeAccuracy"])
                for k in range(3):
                    time_evaluation_separate[ix][jx][k] = update_sum_min_max(time_evaluation_separate[ix][jx][k], evaluation_result["separateTimeAccuracy"][k])

    for i in range(3):
        for j in range(3):
            slides_evaluation_overall[i][j][0] = round(slides_evaluation_overall[i][j][0] / len(lst), 3)
            time_evaluation_overall[i][j][0] = round(time_evaluation_overall[i][j][0] / len(lst), 3)
            for k in range(3):
                slides_evaluation_separate[i][j][k][0] = round(slides_evaluation_separate[i][j][k][0] / len(lst), 3)
                time_evaluation_separate[i][j][k][0] = round(time_evaluation_separate[i][j][k][0] / len(lst), 3)

    for i in range(3):
        for j in range(3):
            if i == j:
                continue
            print("\t\t --> ", i, j)
            print("Slides Score: ", slides_evaluation_overall[i][j][0])
            print("\t Beginning Score:", slides_evaluation_separate[i][j][0][0])
            print("\t Middle Score:", slides_evaluation_separate[i][j][1][0])
            print("\t End Score:", slides_evaluation_separate[i][j][2][0])
            print("")
            print("Time Score: ", time_evaluation_overall[i][j][0])
            print("\t Beginning Score:", time_evaluation_separate[i][j][0][0])
            print("\t Middle Score:", time_evaluation_separate[i][j][1][0])
            print("\t End Score:", time_evaluation_separate[i][j][2][0])
            print("")

        