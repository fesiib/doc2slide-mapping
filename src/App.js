import logo from './logo.svg';
import axios from 'axios'
import {useState, useEffect} from 'react';
import './App.css';
import HeatMap from './components/HeatMap';

const WIDTH = 500;
const HEIGHT = WIDTH * 9 / 16;

function App() {
	const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const presentationID = parseInt(urlParams.get('id'));

	const [data, setData] = useState(null);
	const [paragraphs, setParagraphs] = useState([]);
	const [scripts, setScripts] = useState([]);

	const getData = () => {
		axios.post('http://localhost:3555/getData', {
			presentationId: presentationID,
			similarityType: "classifier",
			outliningApproach: "dp_mask",
			applyThresholding: false,
		}).then( (response) => {
			console.log(response);
			setParagraphs(response.data.paper);
			setScripts(response.data.script);
			setData(response.data.data);
		});
	}

	const outputOutline = (data) => {
		if (!data) {
			return "LOADING";
		}
		const output = data.outline.map((val, idx) => {
			return (<li key={idx}>
				({val.startSlideIndex} - {val.endSlideIndex}) {"\t"} {val.section} 
			</li>);
		});
		return (<ol>
			{output}
		</ol>);
	}

	const outputSlideThumbnails = (data) => {
		if (!data) {
			return;
		}
		const thumbnailsPath = '/slideData/' + presentationID + '/images/';
		const output = data.slideInfo.map((slide, idx) => {
			const thumbnailPath = thumbnailsPath + slide.index.toString() + '.jpg';
			const title = "Script:\n\n" + slide.script + "\n\n\n\n\nOCR Result:\n\n" + slide.ocrResult;

			const startTime = new Date(0);
			startTime.setSeconds(slide.startTime);

			const endTime = new Date(0);
			endTime.setSeconds(slide.endTime);

			return (
				<div key={idx} 
				>
					<div style={{
						overflow: "hidden",
						width: WIDTH,
						height: HEIGHT,
						display: "flex",
						flexDirection: "column",
						justifyContent: "center",
						marginRight: 5,
					}}>
						<img src={thumbnailPath} title={title} style={{
							width: WIDTH,
							objectFit: 'cover',
						}}/>
					</div>
					<div> 
						{idx} {" "}
						({startTime.getMinutes()}:{startTime.getSeconds()} - {endTime.getMinutes()}:{endTime.getSeconds()})
					</div>	
				</div>
			)
		});
		return <div style={{
			display: "flex",
			flexWrap: "nowrap",
			overflowX: "scroll",
			margin: 20,
		}}>
			{output}
		</div>;
	}

	const outputTable = (paragraphs, scripts) => {
		const outputParagraphs = paragraphs.map((paragraph, idx) => {
			return (
				<div style={{
					display:  "flex",
					gap: 10,
					margin: 10,
				}}>
					{idx}
					<div>
						{paragraph}
					</div>
				</div>
			)
		});

		const outputScripts = scripts.map((script, idx) => {
			return (
				<div style={{
					display:  "block",
					gap: 10,
					margin: 10,
				}}>
					{idx}
					<div>
						{script}
					</div>
				</div>
			)
		});

		return <div style={{
			display: "flex",
			flexDirection: "row",
			textAlign: "left",
			margin: 20,
		}}>
			<div style={{
				width: "50%",
			}}>
				{outputParagraphs}
			</div>
			
			<div style={{
				width: "50%",
			}}>
				{outputScripts}
			</div>
		</div>
	}
	
	useEffect(()=>{
		getData();
	}, []);
	return (
		<div className="App">
			<HeatMap 
				data={data ? data.similarityTable : []}
				paragraphs={data ? data.paperSentences : []}
				scripts={data ? data.scriptSentences : []}
			/>
			<h1> Presentation {presentationID} </h1>
			<div style={{
				textAlign: "left",
				fontSize: "15pt",
			}}> 
				{outputOutline(data)} 
			</div>
			<div>
				{outputSlideThumbnails(data)}
			</div>
			<div>
				{outputTable(paragraphs, scripts)}
			</div>
		</div>
	);
}

export default App;
