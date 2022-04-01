const ALTER_STATE = "ALTER_STATE";

export const alterState = (payload) => ({
    type: ALTER_STATE,
    payload,
});

const initialState = {
    presentationExcluded: {}
};

function experimentsState(
    state = {
        ...initialState,
    },
    action,
) {
    switch (action.type) {
        case ALTER_STATE: {
            const presentationId = action.payload;
            const curState = state.presentationExcluded[presentationId] ? state.presentationExcluded[presentationId] : false;
            return {
                presentationExcluded: {
                    ...state.presentationExcluded,
                    [presentationId]: (!curState),
                }
            };
        }
        default:
            return state;
    }
}

export default experimentsState;