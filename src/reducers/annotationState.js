import { v4 } from "uuid";

const SET_STEP = "SET_STEP";
const SET_PRESENTATION_ID = "SET_PRESENTATION_ID";
const SUBMIT = "SUBMIT";

const ADD_BOUNDARY = "ADD_BOUNDARY";
const REMOVE_BOUNDARY = "REMOVE_BOUNDARY";

const SET_LABEL = "SET_LABEL";

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

function randomId() {
    let strId = v4().toString();
    return strId.replaceAll("-", "");
}

const initialState = {
    presentationData: null,
    presentationId: -1,
    submissionId: randomId(),
    step: 0,
    labels: {
        1: "Title",
    },
};

export const NO_LABEL = "NO_LABEL";


const annotationState = (
    state = {
        ...initialState,
        submissionId: randomId(),
    }, action) => {
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
            if (new_boundary < 2
                || state.labels.hasOwnProperty(new_boundary)
            ) {
                return state;
            }
            return {
                ...state,
                labels: {
                    ...state.labels,
                    [new_boundary]: NO_LABEL,
                }
            };
        }
        case REMOVE_BOUNDARY: {
            const boundary = action.payload.boundary;
            if (boundary < 2
                || !state.labels.hasOwnProperty(boundary)
            ) {
                return state;
            }

            const new_labels = {
                ...state.labels,
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
        default:
            return state;
    }
}

export default annotationState;