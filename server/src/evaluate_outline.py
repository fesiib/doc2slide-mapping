from math import floor


SKIPPED_TITLES = ['title', 'end', "no_section"]
GROUND_TRUTH_EXISTS = [100000, 100004, 100006, 100007, 100009]
ACC_BOUNDARY_RANGE = 1

def process_title(title):
    return title.lower().strip()

def are_same_section_titles(title, gt_title):
    return title.startswith(gt_title) or gt_title.startswith(title)

def f1_score(precision, recall):
    if precision + recall == 0:
        return 0
    return 2 * (precision * recall) / (precision + recall)

def __calculate_boundary_coverage(a_boundaries, b_boundaries, total_cnt):
    coverage = 0
    a_boundaries.append(total_cnt + 1)    
    boundary_idx = 0
    for b_boundary in b_boundaries:
        #print("Searching for: ", gt_boundary)
        while a_boundaries[boundary_idx] <= b_boundary and boundary_idx < len(a_boundaries):
            boundary_idx += 1
        
        #print("\tRight: ", boundaries[boundary_idx])    
        cur_error = a_boundaries[boundary_idx] - b_boundary - 1
        if boundary_idx > 0:
            #print("\tLeft: ", boundaries[boundary_idx - 1])
            cur_error = min(cur_error, b_boundary - a_boundaries[boundary_idx - 1])
        cur_total = min(b_boundary, total_cnt - b_boundary)
        coverage += (cur_total - cur_error) / cur_total
        #print("\t\tCurrent Error & Total: ", cur_error, cur_total)

    if len(b_boundaries) > 0:
        coverage /= len(b_boundaries)
    else:
        coverage = 1

    a_boundaries.pop()
    return coverage

def _evaluate_boundaries(outline, gt_outline):
    '''
        User might as well linearly navigate through video,
    and can only start scanning from segmentation boundaries
    either backwards or forward
    '''
    total_slides_cnt = 0
    for section in gt_outline:
        total_slides_cnt = max(total_slides_cnt, section["endSlideIndex"])


    boundaries = []
    for section in outline:
        title = section["sectionTitle"]
        title = process_title(title)

        if title in SKIPPED_TITLES:
            continue

        if section["startSlideIndex"] < total_slides_cnt:
            boundaries.append(section["startSlideIndex"])

    gt_boundaries = []
    for section in gt_outline:
        title = section["sectionTitle"]
        title = process_title(title)

        if title in SKIPPED_TITLES:
            continue

        if section["startSlideIndex"] < total_slides_cnt:
            gt_boundaries.append(section["startSlideIndex"])

    accurate_boundaries_cnt = 0
    gt_boundary_idx = 0
    for boundary in boundaries:
        while gt_boundary_idx < len(gt_boundaries) \
            and boundary - gt_boundaries[gt_boundary_idx] > ACC_BOUNDARY_RANGE:
            gt_boundary_idx += 1
        if gt_boundary_idx == len(gt_boundaries):
            break
    
        if abs(boundary - gt_boundaries[gt_boundary_idx]) <= ACC_BOUNDARY_RANGE:
            accurate_boundaries_cnt += 1
            gt_boundary_idx += 1


    precision = accurate_boundaries_cnt / max(1, len(boundaries))
    recall = __calculate_boundary_coverage(boundaries, gt_boundaries, total_slides_cnt)

    return round(f1_score(precision, recall) * 100, 2)

def _evaluate_time(outline, gt_outline, slide_info):
    '''
    '''

    sections_duration = {}
    gt_sections_duration = {}

    for section in outline:
        title = section["sectionTitle"]
        title = process_title(title)

        if title in SKIPPED_TITLES:
            continue

        start_slide = slide_info[section["startSlideIndex"]]
        end_slide = slide_info[section["endSlideIndex"]]

        duration = end_slide["endTime"] - start_slide["startTime"]
        if title not in sections_duration:
            sections_duration[title] = 0
        sections_duration[title] += duration


    for section in gt_outline:
        title = section["sectionTitle"]
        title = process_title(title)

        if title in SKIPPED_TITLES:
            continue

        start_slide = slide_info[section["startSlideIndex"]]
        end_slide = slide_info[section["endSlideIndex"]]

        duration = end_slide["endTime"] - start_slide["startTime"]
        if title not in gt_sections_duration:
            gt_sections_duration[title] = 0
        gt_sections_duration[title] += duration

    error = 0
    cnt_gt_sections = 0
    for (gt_title, gt_duration) in gt_sections_duration.items():
        if gt_duration == 0:
            continue
        cnt_gt_sections += 1
        found_pair = False
        for (title, duration) in sections_duration.items():
            if are_same_section_titles(title, gt_title):
                found_pair = True
                error += min(1, abs(duration - gt_duration) / gt_duration)
                break
        if found_pair is False:
            error += 1

    if cnt_gt_sections == 0:
        return 50
    return round(100 - (error / cnt_gt_sections) * 100, 2)

def _evaluate_structure(outline, gt_outline, slide_info):
    section_ids = {}
    section_cnt = 0

    gen_section_ids = []
    for section in outline:
        title = section["sectionTitle"]
        title = process_title(title)

        if title in SKIPPED_TITLES:
            continue

        if title not in section_ids:
            section_ids[title] = section_cnt
            section_cnt += 1
        gen_section_ids.append(section_ids[title])

    gt_section_ids = []
    for section in gt_outline:
        title = section["sectionTitle"]
        title = process_title(title)

        if title in SKIPPED_TITLES:
            continue

        for found_title in section_ids.keys():
            if are_same_section_titles(found_title, title):
                section_ids[title] = section_ids[found_title]
                break
        if title not in section_ids:
            section_ids[title] = section_cnt
            section_cnt += 1
        gt_section_ids.append(section_ids[title])

    n = len(gen_section_ids)
    m = len(gt_section_ids)

    score = 0

    if m > 0 and n > 0:
        # for (k, v) in section_ids.items():
        #     print("\t", k, " - ", v)
        
        # print(gen_section_ids)
        # print(gt_section_ids)

        dp = [[-m for j in range(m)] for i in range(n)]
        dp[0][0] = int(gen_section_ids[0] == gt_section_ids[0])
        for i in range(1, n):
            dp[i][0] = dp[i-1][0]
            if gen_section_ids[i] == gt_section_ids[0]:
                dp[i][0] = 1
        for j in range(1, m):
            dp[0][j] = dp[0][j-1]
            if gen_section_ids[0] == gt_section_ids[j]:
                dp[0][j] = 1

        for i in range(1, n):
            for j in range(1, m):
                if gen_section_ids[i] == gt_section_ids[j]:
                    dp[i][j] = max(dp[i][j], dp[i-1][j-1] + 1)
                dp[i][j] = max(dp[i][j], dp[i-1][j])
                dp[i][j] = max(dp[i][j], dp[i][j-1])

        # print("DP:")
        # for i in range(n):
        #     print("\t", dp[i])

        score = dp[n-1][m-1]

    precision = score / max(1, n)
    recall = score / max(1, m)

    return round(f1_score(precision, recall) * 100, 2)

def _evaluate_mapping(outline, gt_outline, top_sections):
    '''
        Calculate our mapping scores against ground truth

        What to do when ground truth mapping score is less than generated mapping score?
        - absolute?
        - give big penalty
        In general, has to see if such cases are frequent....
    '''

    section_idx = 0
    gt_section_idx = 0

    total_score = 0
    error = 0

    for slide_idx, slide_top_sections in enumerate(top_sections):
        while section_idx < len(outline) and outline[section_idx]["endSlideIndex"] < slide_idx:
            section_idx += 1
        if section_idx == len(outline):
            print("Not all slides are mapped in *generated* outline???")
            break

        while gt_section_idx < len(gt_outline) and gt_outline[gt_section_idx]["endSlideIndex"] < slide_idx:
            gt_section_idx += 1
        if gt_section_idx == len(gt_outline):
            print("Not all slides are mapped in *ground_truth* outline???")
            break

        gen_title = outline[section_idx]["sectionTitle"]
        gt_title = gt_outline[gt_section_idx]["sectionTitle"]

        gen_title = process_title(gen_title)
        gt_title = process_title(gt_title)

        if gen_title in SKIPPED_TITLES or gt_title in SKIPPED_TITLES:
            continue

        gen_score = 0
        gt_score = 0
        mx_score = 0

        for top_section in slide_top_sections:
            title = top_section[0]
            title = process_title(title)
            
            score = top_section[1]
            
            mx_score = max(mx_score, score)

            if are_same_section_titles(title, gen_title):
                gen_score = score
            if are_same_section_titles(title, gt_title):
                gt_score = score
        
        # print("Slide: ", slide_idx)
        # print("\t", gen_title, "-", gen_score)
        # print("\t", gt_title, "-", gt_score)

        # total_score += gt_score
        # if gt_score > gen_score:
        #     error += (gt_score - gen_score)
        total_score += mx_score
        error += (mx_score - gt_score)

    if total_score == 0:
        return 50
    return round(100 - (error / total_score) * 100, 2)

def _evaluate_overall(outline, gt_outline, slide_info):
    total_time = 0
    overlapped_time = 0
    separate_overlapped_times = [0, 0, 0]
    separate_total_times = [0, 0, 0]

    labels = ["empty1" for i in range(len(slide_info))]
    gt_labels = ["empty2" for i in range(len(slide_info))]

    for gt_section in gt_outline:
        gt_title = process_title(gt_section["sectionTitle"])
        # if gt_title in SKIPPED_TITLES:
        #     continue
        start_slide = gt_section["startSlideIndex"]
        end_slide = gt_section["endSlideIndex"]

        for id in range(start_slide, end_slide + 1):
            gt_labels[id] = gt_title

        gt_start = slide_info[start_slide]["startTime"]
        gt_end = slide_info[end_slide]["endTime"]
        total_time += gt_end - gt_start

    for section in outline:
        title = process_title(section["sectionTitle"])
        start_slide = section["startSlideIndex"]
        end_slide = section["endSlideIndex"]

        for id in range(start_slide, end_slide + 1):
            labels[id] = title

    invalid = False
    for idx in range(1, len(slide_info)):
        cur_duration = slide_info[idx]["endTime"] - slide_info[idx]["startTime"]
        if labels[idx] == "empty1" or gt_labels[idx] == "empty2":
            invalid = True
        pos = floor(idx / len(slide_info) * 3)
        separate_total_times[pos] += cur_duration
        if are_same_section_titles(labels[idx], gt_labels[idx]):
            overlapped_time += cur_duration
            separate_overlapped_times[pos] += cur_duration
    
    if total_time == 0:
        return 0, [0, 0, 0]

    for i in range(3):
        if separate_total_times[i] > 0:
            separate_overlapped_times[i] = round(separate_overlapped_times[i] / separate_total_times[i], 3)

    return round((overlapped_time / total_time), 3), separate_overlapped_times

def evaluate_outline(outline, gt_outline, slide_info, top_sections):
    overall, separate_scores = _evaluate_overall(outline, gt_outline, slide_info)
    return {
        "boundariesAccuracy": _evaluate_boundaries(outline, gt_outline),
        "overallAccuracy": overall,
        "structureAccuracy": _evaluate_structure(outline, gt_outline, slide_info),
        "mappingAccuracy": _evaluate_mapping(outline, gt_outline, top_sections),
        "separateAccuracy": separate_scores,
    }

def evaluate_performance(evaluations, presentation_ids):

    boundaryAccs = []
    timeAccs = []
    overallAccs = []
    structureAccs = []
    mappingAccs = []
    separateAccs = []

    for evaluation in evaluations:
        boundaryAccs.append(evaluation["boundariesAccuracy"])
        overallAccs.append(evaluation["overallAccuracy"])
        structureAccs.append(evaluation["structureAccuracy"])
        mappingAccs.append(evaluation["mappingAccuracy"])
        separateAccs.append(evaluation["separateAccuracy"])

    def calc_avg(lst):
        sum = 0
        for val in lst:
            sum += val
        
        if len(lst) > 0:
            sum /= len(lst)
        return round(sum, 2)

    return {
        "boundariesAccuracy": (boundaryAccs, calc_avg(boundaryAccs)),
        "overallAccuracy": (overallAccs, calc_avg(overallAccs)),
        "structureAccuracy": (structureAccs, calc_avg(structureAccs)),
        "mappingAccuracy": (mappingAccs, calc_avg(mappingAccs)),
        "separateAccuracy": (separateAccs, calc_avg(separateAccs)),
        "presentation_ids": presentation_ids
    }