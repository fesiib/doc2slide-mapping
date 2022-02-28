import './App.css';
import Evaluation from './pages/Evaluation';
import SingleExample from './pages/SingleExample';

function App() {
	const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
	const mode = parseInt(urlParams.get('mode'))
	const presentationId = parseInt(urlParams.get('id'));

	return (<div className='App'>
		{mode == 0 ?
			<SingleExample
				presentationId={presentationId}
				similarityType={"embeddings"}
				outliningApproach={"dp_mask"}
				applyThresholding={false}
			/>
			:
			<Evaluation/>
		}
	</div>)
}

export default App;
