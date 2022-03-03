import {combineReducers} from 'redux';
import storage from 'redux-persist/lib/storage';

import annotationState from './annotationState';

const RESET_APP = "RESET_APP";

const appReducer = combineReducers({
    annotationState,
});

export const resetApp = () => ({
    type: RESET_APP,
});

const rootReducer = (state, action) => {
    switch(action.type) {
        case RESET_APP:
            storage.removeItem('persist:root');
            return appReducer(undefined, action);
        default:
            return appReducer(state, action);
    }
}

export default rootReducer;