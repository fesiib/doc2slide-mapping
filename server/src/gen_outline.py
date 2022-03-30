from __init__ import sort_section_data


PENALTY = 0.5
MIN_SEGMENTS = 3
MIN_CNT_SLIDES_PER_SEGMENT = 3
MIN_DURATION_PER_SEGMENT = 30 # seconds

GENERIC_SECTION_TITLES = ["introduction", "discussion", "conclusion"]

def should_skip_section(title):
    title = title.strip().lower()
    for skip_title in GENERIC_SECTION_TITLES:
        if skip_title in title:
            return True
    return False

def get_outline_dp(label_dict, top_sections, slide_info):
    n = len(label_dict)
    m = len(slide_info)
    INF = (m + 1) * 100

    Table = [ [ (-INF, n, -1) for j in range(m)] for i in range(m) ]

    def getSegment(start, end):
        if end - start < 2:
            return (-INF, n)

        scores = [0 for i in range(n)]
        for i in range(start, end):
            for top_section in top_sections[i]:
                pos = label_dict.index(top_section[0])
                scores[pos] += top_section[1]
        result_section = -1
        for i in range(n):
            if result_section == -1 or scores[result_section] < scores[i]:
                result_section = i

        return (scores[result_section], result_section)

    Table[0][0] = (0, n, 0)

    for i in range(1, m):
        segment_result = getSegment(i, i + 1)

        Table[i][i] = (max(Table[i-1][i-1][0] + segment_result[0], Table[i][i][0]), segment_result[1], i)

        for j in range(i+1, m) :
            for k in range(i-1, j) :
                cost = getSegment(k+1, j+1)
                if Table[i][j][0] < Table[i-1][k][0] + cost[0]:
                    Table[i][j] = (Table[i-1][k][0] + cost[0], cost[1], k + 1)

    weights = []
    for i in range(m) :
        weights.append(Table[i][m - 1][0])

    max_value = -INF
    optimal_segments = -1

    for i in range(len(Table)) :
        if max_value < Table[i][m - 1][0]:
            max_value = Table[i][m - 1][0]
            optimal_segments = i

    final_result = [ 0 for i in range(m) ]

    cur_slide = m - 1

    while optimal_segments > 0:
        start = Table[optimal_segments][cur_slide][2]
        cur_section = Table[optimal_segments][cur_slide][1]

        for i in range(start, cur_slide + 1) :
            final_result[i] = cur_section
        
        cur_slide = start - 1
        optimal_segments = optimal_segments - 1

        if cur_slide < 0 :
            print("WHAT???? ERROR ERROR ERROR ERROR")
            break

    outline = []

    outline.append({
        'sectionTitle': "NO_SECTION",
        'startSlideIndex': 0,
        'endSlideIndex': 0
    })

    for i in range(1, len(final_result)) :
        if outline[-1]['sectionTitle'] != label_dict[final_result[i]]:
            outline.append({
                'sectionTitle': label_dict[final_result[i]],
                'startSlideIndex': i,
                'endSlideIndex': i
            })
        else :
            outline[-1]['endSlideIndex'] = i
    return outline, weights

def get_outline_strong(label_dict, apply_heuristics, slide_info, top_sections, transitions):
    weights = []
    outline = []
    outline.append({
        "sectionTitle": "TITLE",
        "startSlideIndex": 1,
        "endSlideIndex": transitions[0],
    })

    # for slide_idx in range(len(top_sections)):
    #     scores = []
    #     for top_section in top_sections[slide_idx]:
    #         scores.append(top_section[1])
    #     scores = sorted(scores)
    #     mx_rank = len(scores) - 1
    #     for i, top_section in enumerate(top_sections[slide_idx]):
    #         rank = mx_rank
    #         while rank > 0 and scores[rank] > top_section[1]:
    #             rank -= 1
    #         if mx_rank > 0:
    #             top_sections[slide_idx][i] = (top_section[0], rank / mx_rank)
    #         else:
    #             top_sections[slide_idx][i] = (top_section[0], 0)
    #     print(slide_idx, " : ")
    #     for i in range(mx_rank + 1):
    #         for top_section in top_sections[slide_idx]:
    #             if i == top_section[1]:
    #                 print("\t", top_section[0], ":", top_section[1])

    with open("./experiments.csv", "w") as f:
        print("title", end=",", file=f)
        for idx in range(1, len(transitions) - 1):
            print(str(transitions[idx - 1] + 1) + "-" + str(transitions[idx]), end=",", file=f)
        print("", file=f)

        info = []

        new_label_dict = []

        for label in label_dict:
            # if should_skip_section(label):
            #     continue
            new_label_dict.append(label)
            scores_max = []
            scores_avg = []
            scores_total = []

            for idx in range(1, len(transitions) - 1):
                scores_total.append(0)
                scores_avg.append(0)
                scores_max.append(-1)
                for i in range(transitions[idx - 1] + 1, transitions[idx] + 1):
                    for top_section in top_sections[i]:
                        if top_section[0] != label:
                            continue
                        scores_total[-1] += top_section[1]
                        scores_max[-1] = max(scores_max[-1], top_section[1])
                        break
                if transitions[idx] > transitions[idx-1]:
                    scores_avg[-1] = scores_total[-1] / (transitions[idx] - transitions[idx - 1])            
            
            print(label, end=",", file=f)
            for val in scores_max:
                print(round(val, 2), end=",", file=f)
            print("", file=f)
            info.append(scores_max)
        
        dp = [[0 for i in range(len(transitions) - 1)]]
        prevs = [[0 for i in range(len(transitions) - 1)]]

        for i, label in enumerate(new_label_dict):
            dp.append([0])
            prevs.append([0])
            
            larger_thans = [0]
            for j in range(1, len(transitions) - 1):
                larger_thans.append(0)
                if "introduction" in label.lower() or ("related" in label.lower() and "work" in label.lower()) or "background" in label.lower():
                    if j > (len(transitions) - 1) / 2:
                        dp[-1].append(0)
                        prevs[-1].append(0)
                        continue
                
                if "discussion" in label.lower() or "conclusion" in label.lower():
                    if j <= (len(transitions) - 1) / 2:
                        dp[-1].append(0)
                        prevs[-1].append(0)
                        continue

                l = max(0, i + 1)
                r = min(len(new_label_dict), i + 4)
                if r == len(new_label_dict):
                    l = max(0, r - 3)

                for k in range(l, r):
                    if k == i:
                        continue
                    if info[i][j - 1] >= info[k][j - 1] - ((k - i) / len(new_label_dict)):
                        larger_thans[-1] += 1
                
                dp[-1].append(dp[-2][j])
                prevs[-1].append(j)

                if dp[-1][-1] < dp[-1][-2] + larger_thans[-1]:
                    dp[-1][-1] = dp[-1][-2] + larger_thans[-1]
                    prevs[-1][-1] = prevs[-1][-2]

                # sum_larger_thans = larger_thans[-1]
                # for k in range(j - 1, 0, -1):
                #     sum_larger_thans += larger_thans[k]
                
                # for k in range(1, j):
                #     if dp[-1][-1] <= dp[-2][k] + sum_larger_thans:
                #         dp[-1][-1] = dp[-2][k] + sum_larger_thans
                #         prevs[-1][-1] = k
                #     sum_larger_thans -= larger_thans[k]

            print(label, ":", dp[-1])
            print(label, ":", prevs[-1])
            print(label, ":", larger_thans)
            # if "introduction" in label.lower():
            #     raw_outline.append(1)
            #     for j in range(2, len(transitions) - 1):
            #         if (larger_thans[j] > larger_thans[j - 1]):
            #             raw_outline[-1] = j
            #         else:
            #             break
            #     continue

            # if "discussion" in label.lower():
            #     raw_outline.append(raw_outline[-1])
            #     while (raw_outline[-1] < len(transitions) - 2 and larger_thans[raw_outline[-1]] < larger_thans[raw_outline[-1] + 1]):
            #         raw_outline[-1] += 1
            #     continue       
         
            # if "conclusion" in label.lower():
            #     raw_outline.append(len(transitions) - 2)
            #     break

            # cur_transition = raw_outline[-1]
            # for k in range(0, len(potentially)):
            #     if potentially[k] <= raw_outline[-1]:
            #         continue
            #     elif cur_transition == raw_outline[-1]:
            #         cur_transition = potentially[k]
            #         continue
            #     if cur_transition == -1 or potentially[k] - cur_transition == 1:
            #         cur_transition = potentially[k]
            #     else:
            #         break
            # raw_outline.append(cur_transition)
            # print(label, ":", potentially)

        raw_outline = []

        i = len(new_label_dict) - 1
        j = len(transitions) - 2
        while (i >= 0 and j >= 0):
            raw_outline.append(j)
            next_j = prevs[i][j]
            i -= 1
            j = next_j

        raw_outline = raw_outline[::-1]

        for i in range(len(raw_outline)):
            if i == 0 or raw_outline[i] == raw_outline[i - 1]:
                continue
            outline.append({
                "sectionTitle": new_label_dict[i - 1],
                "startSlideIndex": transitions[raw_outline[i-1]] + 1,
                "endSlideIndex": transitions[raw_outline[i]],
            })
    outline.append({
        "sectionTitle": "END",
        "startSlideIndex": transitions[-2] + 1,
        "endSlideIndex": transitions[-1],
    })

    return outline, weights


def get_outline_dp_mask(label_dict, apply_heuristics, slide_info, top_sections, transitions, target_mask = None):
    n = len(label_dict)
    m = len(slide_info)
    INF = (m + 1) * 100

    outline = [{
        "sectionTitle": "END",
        "startSlideIndex": transitions[-2] + 1,
        "endSlideIndex": transitions[-1],
    }]
    
    total_duration = slide_info[m-2]["endTime"] - slide_info[1]["startTime"]
    
    min_cnt_slides_per_segment = min(MIN_CNT_SLIDES_PER_SEGMENT, len(transitions) - 2)
    min_segments = min(MIN_SEGMENTS, round((len(transitions) - 2) / min_cnt_slides_per_segment))
    min_duration_per_segment = min(MIN_DURATION_PER_SEGMENT, total_duration / min_segments)

    print(min_cnt_slides_per_segment, min_duration_per_segment, min_segments)

    dp = [[(-INF, n, -1) for j in range(m)] for i in range(1 << n)]
    dp[0][transitions[0]] = (0, n, -1)

    for i in transitions[:-1]:
        scores = [0 for k in range(n)]
        for j in range(i + 1, transitions[-1]):
            for top_section in top_sections[j]:
                pos = label_dict.index(top_section[0])
                scores[pos] += top_section[1]
            if j not in transitions:
                continue
            # Heuristics
            # if apply_heuristics is True:
            #     if j - i < min_cnt_slides_per_segment:
            #         continue
            #     if slide_info[j]["endTime"] - slide_info[i + 1]["startTime"] < min_duration_per_segment:
            #         continue
            for mask in range(0, (1 << n)):
                if dp[mask][i][0] < 0:
                    continue
                penalty = 0
                inc_penalty = 0
                for k in range (n-1,0,-1):
                    penalty += inc_penalty
                    if mask & (1 << k) > 0:
                        inc_penalty = PENALTY
                        continue

                    nmask = mask | (1 << k)

                    # Heuristics
                    if apply_heuristics is True:
                        if should_skip_section(label_dict[k]):
                            continue
                        if (dp[nmask][j][0] < dp[mask][i][0] + scores[k] - penalty):
                            dp[nmask][j] = (dp[mask][i][0] + scores[k] - penalty, k, i)
                    else:
                        if (dp[nmask][j][0] < dp[mask][i][0] + scores[k]):
                            dp[nmask][j] = (dp[mask][i][0] + scores[k], k, i)

    # Slide #1 -> title
    # Slide #last -> end


    recover_mask = 0
    recover_slide_id = transitions[-2]

    weights = [-1 for i in range(n + 1)]

    for mask in range(1 << n):
        cnt_segments = bin(mask).count('1')
        weights[cnt_segments] = max(weights[cnt_segments], dp[mask][recover_slide_id][0])
        # if cnt_segments < min_segments:
        #     continue
        if dp[mask][recover_slide_id][0] > dp[recover_mask][recover_slide_id][0]:
            recover_mask = mask
        if cnt_segments < bin(recover_mask).count('1') and dp[mask][recover_slide_id][0] == dp[recover_mask][recover_slide_id][0]:
            recover_mask = mask
    if target_mask is not None:
        recover_mask = target_mask
        print(bin(target_mask), bin(recover_mask), dp[target_mask][recover_slide_id][0])
    
    while recover_mask > 0:
        print(recover_mask, recover_slide_id, dp[recover_mask][recover_slide_id])
        section_id = dp[recover_mask][recover_slide_id][1]
        next_recover_mask = recover_mask ^ (1 << section_id)
        next_recover_slide_id = dp[recover_mask][recover_slide_id][2]
        outline.append({
            "sectionTitle": label_dict[section_id],
            "startSlideIndex": next_recover_slide_id + 1,
            "endSlideIndex": recover_slide_id,
        })
        recover_mask = next_recover_mask
        recover_slide_id = next_recover_slide_id
    
    outline.append({
        "sectionTitle": "TITLE",
        "startSlideIndex": 1,
        "endSlideIndex": transitions[0],
    })

    return outline[::-1], weights

def get_outline_simple(top_sections):
    outline = []
    weights = []

    for i in range(1, len(top_sections)):
        scores = {
            "NO_SECTION": 0
        }
        for j in range(0, len(top_sections[i])):
            if top_sections[i][j][0] not in scores:
                scores[top_sections[i][j][0]] = 0    
            scores[top_sections[i][j][0]] = max(scores[top_sections[i][j][0]], top_sections[i][j][1])
        section = "NO_SECTION"
        for (k, v) in scores.items():
            if v > scores[section]:
                section = k
        outline.append({
            "sectionTitle": section,
            "startSlideIndex": i,
            "endSlideIndex": i,
        })
        weights.append(scores[section])
    return outline, weights

def get_outline_generic(outlining_approach, apply_heuristics, slide_info, section_data, top_sections, slides_segmentation, target_mask = None):
    transitions = []
    for slides_segment in slides_segmentation:
        if slides_segment['endSlideIndex'] < 1:
            continue
        transitions.append(slides_segment['endSlideIndex'])
    label_dict = sort_section_data(section_data)
    for i, label in enumerate(label_dict):
        print(i, ":", label)
    print(transitions)

    if len(transitions) < 2 or len(slide_info) < 3:
        return [{
            "sectionTitle": "PAPER",
            "startSlideIndex": 1,
            "endSlideIndex": len(slide_info) - 1,
        }], [-1, 0]

    if outlining_approach == 'strong':
        return get_outline_strong(label_dict, apply_heuristics, slide_info, top_sections, transitions)

    if outlining_approach == 'dp_mask':
        return get_outline_dp_mask(label_dict, apply_heuristics, slide_info, top_sections, transitions, target_mask)
    if outlining_approach == 'simple':
        return get_outline_simple(top_sections)
    
    return get_outline_dp(label_dict, top_sections)