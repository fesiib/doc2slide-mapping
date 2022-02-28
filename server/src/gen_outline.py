PENALTY = 0.5
MIN_SEGMENTS = 3

def get_outline_dp(section_data, top_sections, script_sentence_range):
    label_dict = sorted(list(set(section_data)))
    
    INF = (len(script_sentence_range) + 1) * 100
    n = len(label_dict)

    Table = [ [ (-INF, n, -1) for j in range(len(script_sentence_range))] for i in range(len(script_sentence_range)) ]

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

    for i in range(1, len(script_sentence_range)):
        segment_result = getSegment(i, i + 1)

        Table[i][i] = (max(Table[i-1][i-1][0] + segment_result[0], Table[i][i][0]), segment_result[1], i)

        for j in range(i+1, len(script_sentence_range)) :
            for k in range(i-1, j) :
                cost = getSegment(k+1, j+1)
                if Table[i][j][0] < Table[i-1][k][0] + cost[0]:
                    Table[i][j] = (Table[i-1][k][0] + cost[0], cost[1], k + 1)

    weights = []
    for i in range(len(script_sentence_range)) :
        weights.append(Table[i][len(script_sentence_range) - 1][0])

    max_value = -INF
    optimal_segments = -1

    for i in range(len(Table)) :
        if max_value < Table[i][len(script_sentence_range) - 1][0]:
            max_value = Table[i][len(script_sentence_range) - 1][0]
            optimal_segments = i

    final_result = [ 0 for i in range(len(script_sentence_range)) ]

    cur_slide = len(script_sentence_range) - 1
    print(max_value, optimal_segments)

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

def get_outline_dp_mask(section_data, top_sections, script_sentence_range, target_mask = None):
    label_dict = sorted(list(set(section_data)))

    for i, section in enumerate(label_dict):
        print(i, ":", section)

    n = len(label_dict)
    m = len(script_sentence_range)
    INF = (m + 1) * 100

    dp = [[(-INF, n, -1) for j in range(m)] for i in range(1 << n)]
    dp[0][0] = (0, n)

    for i in range(m):
        scores = [0 for k in range(n)]
        for j in range(i + 1, m):
            for top_section in top_sections[j]:
                pos = label_dict.index(top_section[0])
                scores[pos] += top_section[1]

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
                    if (dp[nmask][j][0] < dp[mask][i][0] + scores[k] - penalty):
                        dp[nmask][j] = (dp[mask][i][0] + scores[k] - penalty, k, i)

    recover_mask = 0
    recover_slide_id = m - 1

    weights = [-1 for i in range(n + 1)]

    for mask in range(1 << n):
        cnt_segments = bin(mask).count('1')
        weights[cnt_segments] = max(weights[cnt_segments], dp[mask][recover_slide_id][0])
        if cnt_segments < MIN_SEGMENTS:
            continue
        if dp[mask][recover_slide_id][0] > dp[recover_mask][recover_slide_id][0]:
            recover_mask = mask
        if cnt_segments < bin(recover_mask).count('1') and dp[mask][recover_slide_id][0] == dp[recover_mask][recover_slide_id][0]:
            recover_mask = mask

    if target_mask is not None:
        recover_mask = target_mask
        print(bin(target_mask), bin(recover_mask), dp[target_mask][recover_slide_id][0])
    
    outline = []
    while recover_slide_id > 0:
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

def get_outline_generic(outlining_approach, section_data, top_sections, script_sentence_range, target_mask = None):
    if outlining_approach == 'dp_mask':
        return get_outline_dp_mask(section_data, top_sections, script_sentence_range, target_mask)
    if outlining_approach == 'simple':
        return get_outline_simple(top_sections)
    
    return get_outline_dp(section_data, top_sections, script_sentence_range)