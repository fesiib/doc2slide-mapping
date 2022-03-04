import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

import {
	BrowserRouter,
	Routes,
	Route,
} from 'react-router-dom';


import {Provider} from 'react-redux';
import {PersistGate} from 'redux-persist/integration/react';
import configureStore from './config/store';
import SectionTransitionExamples from './pages/SectionTransitionExamples';
import Annotation from './pages/Annotation';
const {store, persistor} = configureStore();

ReactDOM.render(
	<Provider store={store}>
    	<PersistGate loading={null} persistor={persistor}>
			<BrowserRouter>
				<Routes>
					<Route path="/" element={<App />} />
					<Route path="/section_transition_examples" element={<SectionTransitionExamples/>} />
					<Route path="/annotation" element={<Annotation/>} />
				</Routes>
			</BrowserRouter>
		</PersistGate>
	</Provider>,
  	document.getElementById('root')
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
