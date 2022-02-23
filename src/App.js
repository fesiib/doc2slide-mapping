import axios from 'axios'
import {useState, useEffect} from 'react';
import './App.css';
import HeatMap from './components/HeatMap';
import Outline from './components/Outline';
import SlideThumbnails from './components/SlideThumbnails';
import ComparisonTable from './components/ComparisonTable';
import PipelineAccuracy from './components/PipelineAccuracy';

function App() {
	const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const presentationId = parseInt(urlParams.get('id'));

	const [data, setData] = useState(null);
	const [paragraphs, setParagraphs] = useState([]);
	const [scripts, setScripts] = useState([]);
	const [sections, setSections] = useState([]);
	
	useEffect(() => {
		axios.post('http://localhost:3555/getData', {
			presentationId: presentationId,
			similarityType: "classifier",
			outliningApproach: "dp_mask",
			applyThresholding: false,
		}).then( (response) => {
			console.log(response);
			setParagraphs(response.data.paper);
			setScripts(response.data.script);
			setSections(response.data.sections);
			setData(response.data.data);
		});

	}, [presentationId]);

	if (!data) {
		return <div> LOADING !!! </div>
	}
	return (
		<div className="App">
			<HeatMap 
				data={data ? data.similarityTable : []}
				paragraphs={data ? data.paperSentences : []}
				scripts={data ? data.scriptSentences : []}
			/>
			<h1> Presentation {presentationId} </h1>

			<SlideThumbnails presentationId={presentationId} slideInfo={data?.slideInfo}/>
			<div style={{
				textAlign: "left",
				fontSize: "15pt",
				display: "flex",
			}}> 
				<Outline isGenerated={true} outline={data?.outline} slideInfo={data?.slideInfo} />
				<Outline isGenerated={false} outline={data?.groundTruthOutline} slideInfo={data?.slideInfo} />
			</div>
			<PipelineAccuracy evaluationData={null}/>
			<ComparisonTable paragraphs={paragraphs} scripts={scripts} sections={sections}/>
		</div>
	);
}

export default App;
