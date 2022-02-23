import axios from 'axios'
import {useState, useEffect} from 'react';
import './App.css';
import HeatMap from './components/HeatMap';
import Outline from './components/Outline';
import SlideThumbnails from './components/SlideThumbnails';
import ComparisonTable from './components/ComparisonTable';

function App() {
	const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const presentationId = parseInt(urlParams.get('id'));

	const [data, setData] = useState(null);
	const [paragraphs, setParagraphs] = useState([]);
	const [scripts, setScripts] = useState([]);
	const [sections, setSections] = useState([]);

	const evaluateOutline = (outline, gtOutline, slideInfo) => {
		return (<div>
			TODO!
		</div>);
	}
	
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
	return (
		<div className="App">
			<HeatMap 
				data={data ? data.similarityTable : []}
				paragraphs={data ? data.paperSentences : []}
				scripts={data ? data.scriptSentences : []}
			/>
			<h1> Presentation {presentationId} </h1>
			<div> Accuracy: {evaluateOutline(data?.outline, data?.groundTruthOutline, data?.slideInfo)} </div>
			<div style={{
				textAlign: "left",
				fontSize: "15pt",
				display: "flex",
			}}> 
				<Outline outline={data?.outline} slideInfo={data?.slideInfo} />
				<Outline outline={data?.groundTruthOutline} slideInfo={data?.slideInfo} />
			</div>
			<SlideThumbnails presentationId={presentationId} slideInfo={data?.slideInfo}/>
			<ComparisonTable paragraphs={paragraphs} scripts={scripts} sections={sections}/>
		</div>
	);
}

export default App;
