import './App.css';
import AllOutlines from './pages/AllOutlines';
import Annotation from './pages/Annotation';
import Evaluation from './pages/Evaluation';
import SingleExample from './pages/SingleExample';

function App() {
	const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
	const mode = parseInt(urlParams.get('mode'))
	const presentationId = parseInt(urlParams.get('id'));

	const similartiyType = urlParams.get('similarityType');
	const similarityMethod = urlParams.get('similarityMethod');
	const outliningApproach = urlParams.get('outliningApproach');
	const applyThresholding = urlParams.get('applyThresholding') === 'true' ? true : false;
	const applyHeuristics = urlParams.get('applyHeuristics') === 'true' ? true : false;

	if (mode === 0) {
		return ( <div className='App'>
			<SingleExample
				presentationId={presentationId}
				similarityType={similartiyType}
				similarityMethod={similarityMethod}
				outliningApproach={outliningApproach}
				applyThresholding={applyThresholding}
				applyHeuristics={applyHeuristics}
			/>
		</div>);
	}
	else if (mode === 1) {
		return ( <div className='App'>
			<AllOutlines
				similarityType={similartiyType}
				similarityMethod={similarityMethod}
				outliningApproach={outliningApproach}
				applyThresholding={applyThresholding}
				applyHeuristics={applyHeuristics}
			/>
		</div>);
	}
	else if (mode === 2) {
		console.log(presentationId)
		return ( <div className='App'>
			<Annotation
				presentationId={presentationId}
			/>
		</div>)
	}
	return (<div className='App'>
		<Evaluation/>
	</div>)
}

export default App;
