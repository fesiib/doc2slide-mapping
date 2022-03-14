import { v4 } from "uuid";

const SET_STEP = "SET_STEP";
const SET_PRESENTATION_ID = "SET_PRESENTATION_ID";

const ADD_BOUNDARY = "ADD_BOUNDARY";
const REMOVE_BOUNDARY = "REMOVE_BOUNDARY";

const SET_LABEL = "SET_LABEL";

const ADD_ANNOTATION = "ADD_ANNOTATION";
const DEL_ANNOTATION = "DEL_ANNOTATION";

const RESTART_ANNOTATION = "RESTART_ANNOTATION";

export const setPresentationid = (payload) => ({
    type: SET_PRESENTATION_ID,
    payload
});

export const setStep = (payload) => ({
    type: SET_STEP,
    payload
})

export const addBoundary = (payload) => ({
    type: ADD_BOUNDARY,
    payload
});

export const removeBoundary = (payload) => ({
    type: REMOVE_BOUNDARY,
    payload
});

export const setLabel = (payload) => ({
    type: SET_LABEL,
    payload
});

export const addAnnotation = (payload) => ({
    type: ADD_ANNOTATION,
    payload
})

export const delAnnotation = (payload) => ({
    type: DEL_ANNOTATION,
    payload
})

export const restartAnnotation = (payload) => ({
    type: RESTART_ANNOTATION,
    payload
});

function randomId() {
    let strId = v4().toString();
    return strId.replaceAll("-", "");
}

const initialState = {
    presentationData: null,
    presentationId: -1,
    submissionId: randomId(),
    refAnnotations: {},
    step: 0,
    labels: {
        1: "TITLE"
    },
    submissions: {},
};

export const NO_LABEL = "NO_LABEL";


const annotationState = (
    state = {
        ...initialState,
        submissionId: randomId(),
    }, action) => {      
        
        const endIdxs = [ ...Object.keys(state.labels).map((val) => parseInt(val)).sort((p1, p2) => p1 - p2)];
        const getNextEndIdx = (target_idx) => {
            const label_idx = endIdxs.find((value, idx) => {
                if (value > target_idx) {
                    return true;
                }
                return false;
            })
            return label_idx;
        }

        switch (action.type) {
            case SET_PRESENTATION_ID: {
                const presentationId = action.payload.presentationId;
                const presentationData = action.payload.presentationData;
                return {
                    ...state,
                    presentationId,
                    presentationData,
                }
            }
            case SET_STEP: {
                const new_step = action.payload.step;
                return {
                    ...state,
                    step: new_step,
                }
            }
            case ADD_BOUNDARY: {
                const new_boundary = action.payload.boundary;
                if (new_boundary < 1
                    || state.labels.hasOwnProperty(new_boundary)
                ) {
                    return state;
                }
                const nextEndIdx = getNextEndIdx(new_boundary);
                return {
                    ...state,
                    labels: {
                        ...state.labels,
                        [new_boundary]: state.labels[nextEndIdx],
                        [nextEndIdx]: NO_LABEL,
                    }
                };
            }
            case REMOVE_BOUNDARY: {
                const boundary = action.payload.boundary;
                if (boundary < 1
                    || !state.labels.hasOwnProperty(boundary)
                ) {
                    return state;
                }
                const nextEndIdx = getNextEndIdx(boundary);

                const new_labels = {
                    ...state.labels,
                    [nextEndIdx]: state.labels[boundary],
                }
                delete new_labels[boundary];

                return {
                    ...state, 
                    labels: new_labels,
                };
            }
            case SET_LABEL: {
                const boundary = action.payload.boundary;
                const label = action.payload.label === "" ? NO_LABEL : action.payload.label;

                const new_labels = {
                    ...state.labels,
                    [boundary]: label,
                };
                return {
                    ...state, 
                    labels: new_labels,
                };
            }
            case ADD_ANNOTATION: {
                const submissionId = action.payload.submissionId;
                const outline = action.payload.outline;
                return {
                    ...state,
                    refAnnotations: {
                        ...state.refAnnotations,
                        [submissionId]: outline,
                    },
                };
            }
            case DEL_ANNOTATION: {
                const submissionId = action.payload.submissionId;

                let newRefAnnotations = { ...state.refAnnotations };
                delete newRefAnnotations[submissionId];

                return {
                    ...state,
                    refAnnotations: newRefAnnotations,
                };
            }
            case RESTART_ANNOTATION: {
                const submitted = action.payload.submitted;
                if (!submitted) {
                    return {
                        ...initialState,
                        submissionId: randomId(),
                        submissions: {
                            ...state.submissions,
                        }
                    };
                }
                const presentationId = state.presentationId;
                const submissionId = state.submissionId;

                const new_submissions = { ...state.submissions };
                if (!new_submissions.hasOwnProperty(presentationId)) {
                    new_submissions[presentationId] = [];
                }
                new_submissions[presentationId].push(submissionId);
                return {
                    ...initialState,
                    submissionId: randomId(),
                    submissions: {
                        ...new_submissions,
                    }
                };
            }
            default:
                return state;
        }
}

export default annotationState;