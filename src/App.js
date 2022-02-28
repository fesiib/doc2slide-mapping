import './App.css';
import AllOutlines from './pages/AllOutlines';
import Evaluation from './pages/Evaluation';
import SingleExample from './pages/SingleExample';

function App() {
	const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
	const mode = parseInt(urlParams.get('mode'))
	const presentationId = parseInt(urlParams.get('id'));

	const similartiyType = urlParams.get('similarityType');
	const outliningApproach = urlParams.get('outliningApproach');
	const applyThresholding = Boolean(urlParams.get('applyThresholding'));

	if (mode === 0) {
		return ( <div className='App'>
			<SingleExample
				presentationId={presentationId}
				similarityType={similartiyType}
				outliningApproach={outliningApproach}
				applyThresholding={applyThresholding}
			/>
		</div>);
	}
	else if (mode === 1) {
		return ( <div className='App'>
			<AllOutlines
				similarityType={similartiyType}
				outliningApproach={outliningApproach}
				applyThresholding={applyThresholding}
			/>
		</div>);
	}
	return (<div className='App'>
		<Evaluation/>
	</div>)
}

export default App;
