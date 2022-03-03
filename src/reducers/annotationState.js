const SET_STEP = "SET_STEP";
const SUBMIT = "SUBMIT";

const ADD_BOUNDARY = "ADD_BOUNDARY";
const REMOVE_BOUNDARY = "REMOVE_BOUNDARY";

const ADD_LABEL = "ADD_LABEL";
const REMOVE_LABEL = "REMOVE_LABEL";

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

const initialState = {
    step: 0,
    labels: {
        1: "title",
    },
};


const annotationState = (state = initialState, action) => {
    switch (action.type) {
        case SET_STEP: {
            const new_step = action.payload.step;
            return {
                ...state,
                step: new_step,
            }
        }
        case ADD_BOUNDARY: {
            const new_boundary = action.payload.boundary
            if (new_boundary < 2
                || state.labels.hasOwnProperty(new_boundary)
            ) {
                return state;
            }
            return {
                ...state,
                labels: {
                    ...state.labels,
                    [new_boundary]: "NO_LABEL",
                }
            };
        }
        case REMOVE_BOUNDARY: {
            const boundary = action.payload.boundary
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
        default:
            return state;
    }
}

export default annotationState;