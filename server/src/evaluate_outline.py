SKIPPED_TITLES = ['title', 'end', "no_section"]
GROUND_TRUTH_EXISTS = [0, 4, 6, 7, 9]

def process_title(title):
    return title.lower().strip()

def are_same_section_titles(title, gt_title):
    return title.startswith(gt_title) or gt_title.startswith(title)

def _evaluate_boundaries(outline, gt_outline):
    '''
        User might as well linearly navigate through video,
    and can only start scanning from segmentation boundaries
    either backwards or forward
    '''

    boundaries = [0]
    gt_boundaries = []

    for section in outline:
        boundaries.append(section["startSlideIndex"])

    total_slides_cnt = 0
    for section in gt_outline:
        gt_boundaries.append(section["startSlideIndex"])
        total_slides_cnt = max(total_slides_cnt, section["endSlideIndex"])

    boundaries.append(total_slides_cnt + 1)

    #print(boundaries)
    #print(gt_boundaries)

    error = 0

    boundary_idx = 0
    for gt_boundary in gt_boundaries:
        #print("Searching for: ", gt_boundary)
        while boundaries[boundary_idx] < gt_boundary and boundary_idx < len(boundaries):
            boundary_idx += 1
        
        #print("\tRight: ", boundaries[boundary_idx])    
        cur_error = abs(boundaries[boundary_idx] - gt_boundary)
        if boundary_idx > 0:
            #print("\tLeft: ", boundaries[boundary_idx - 1])
            cur_error = min(cur_error, abs(boundaries[boundary_idx - 1] - gt_boundary))
        #print("\t\tCurrent Error: ", cur_error)
        error += cur_error

    if total_slides_cnt == 0:
        return 0
    return round(100 - (error / total_slides_cnt) * 100, 2)

def _evaluate_time(outline, gt_outline, slide_info):
    '''
    '''

    sections_duration = {}
    gt_sections_duration = {}

    for section in outline:
        title = section["sectionTitle"]
        title = process_title(title)

        start_slide = slide_info[section["startSlideIndex"]]
        end_slide = slide_info[section["endSlideIndex"]]

        duration = end_slide["endTime"] - start_slide["startTime"]
        if title not in sections_duration:
            sections_duration[title] = 0
        sections_duration[title] += duration

    total_duration = 0

    for section in gt_outline:
        title = section["sectionTitle"]
        title = process_title(title)

        if title in SKIPPED_TITLES:
            continue

        start_slide = slide_info[section["startSlideIndex"]]
        end_slide = slide_info[section["endSlideIndex"]]

        duration = end_slide["endTime"] - start_slide["startTime"]
        if (duration < 0):
            print("Negative Duration:", title, duration, section["startSlideIndex"], section["endSlideIndex"])
            duration = -duration
        total_duration += duration
        if title not in gt_sections_duration:
            gt_sections_duration[title] = 0
        gt_sections_duration[title] += duration

    error = 0

    for (gt_title, gt_duration) in gt_sections_duration.items():
        found_pair = False
        for (title, duration) in sections_duration.items():
            if are_same_section_titles(title, gt_title):
                found_pair = True
                error += abs(duration - gt_duration)
                break
        if found_pair is False:
            error += gt_duration
    
    if total_duration == 0:
        return 0
    return round(100 - (error / total_duration) * 100, 2)

def _evaluate_structure(outline, gt_outline, slide_info):
    section_ids = {}
    section_cnt = 0

    gen_section_ids = []
    for section in outline:
        title = section["sectionTitle"]
        title = process_title(title)

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

    if m > 0:
        # for (k, v) in section_ids.items():
        #     print("\t", k, " - ", v)
        
        # print(gen_section_ids)
        # print(gt_section_ids)

        dp = [[-m for j in range(m)] for i in range(n)]
        for i in range(n):
            dp[i][0] = 0
            if gen_section_ids[i] == gt_section_ids[0]:
                dp[i][0] = 1
        for j in range(m):
            dp[0][j] = 0
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

    if m == 0:
        return 0
    return round((score / m) * 100, 2)

def _evaluate_mapping(outline, gt_outline, top_sections):
    '''
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

        for top_section in slide_top_sections:
            title = top_section[0]
            title = process_title(title)
            
            score = top_section[1]
            if are_same_section_titles(title, gen_title):
                gen_score = score
            if are_same_section_titles(title, gt_title):
                gt_score = score
        
        # print("Slide: ", slide_idx)
        # print("\t", gen_title, "-", gen_score)
        # print("\t", gt_title, "-", gt_score)

        total_score += gt_score
        if gt_score > gen_score:
            error += (gt_score - gen_score)

    if total_score == 0:
        return 0
    return round(100 - (error / total_score) * 100, 2)

def evaluate_outline(outline, gt_outline, slide_info, top_sections):
    return {
        "boundariesAccuracy": _evaluate_boundaries(outline, gt_outline),
        "timeAccuracy": _evaluate_time(outline, gt_outline, slide_info),
        "structureAccuracy": _evaluate_structure(outline, gt_outline, slide_info),
        "mappingAccuracy": _evaluate_mapping(outline, gt_outline, top_sections),
    }

def evaluate_performance(evaluations, presentation_ids):

    boundaryAccs = []
    timeAccs = []
    structureAccs = []
    mappingAccs = []

    for evaluation in evaluations:
        boundaryAccs.append(evaluation["boundariesAccuracy"])
        timeAccs.append(evaluation["timeAccuracy"])
        structureAccs.append(evaluation["structureAccuracy"])
        mappingAccs.append(evaluation["mappingAccuracy"])

    def calc_avg(lst):
        sum = 0
        for val in lst:
            sum += val
        
        if len(lst) > 0:
            sum /= len(lst)
        return round(sum, 2)

    return {
        "boundariesAccuracy": (boundaryAccs, calc_avg(boundaryAccs)),
        "timeAccuracy": (timeAccs, calc_avg(timeAccs)),
        "structureAccuracy": (structureAccs, calc_avg(structureAccs)),
        "mappingAccuracy": (mappingAccs, calc_avg(mappingAccs)),
        "presentation_ids": presentation_ids
    }