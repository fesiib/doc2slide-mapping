
def _evaluate_boundaries(outline, gt_outline):
    return 0

def _evaluate_time(outline, gt_outline, slide_info):
    return 0

def _evaluate_structure(outline, gt_outline, slide_info):
    return 0

def _evaluate_mapping(outline, gt_outline, top_sections):
    return 0

def evaluate_outline(outline, gt_outline, slide_info, top_sections):

    return {
        "boundariesAccuracy": _evaluate_boundaries(outline, gt_outline),
        "timeAccuracy": _evaluate_time(outline, gt_outline, slide_info),
        "structureAccuracy": _evaluate_structure(outline, gt_outline, slide_info),
        "mappingAccuracy": _evaluate_mapping(outline, gt_outline, top_sections),
    }