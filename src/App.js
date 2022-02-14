import logo from './logo.svg';
import axios from 'axios'
import {useState, useEffect} from 'react';
import './App.css';

const WIDTH = 500;
const HEIGHT = WIDTH * 9 / 16;

function App() {
	const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const presentationID = parseInt(urlParams.get('id'));

	const [data, setData] = useState(null);

	const getData = () => {
		const dataPath = '/slideData/' + presentationID + '/result.json';
		fetch(
			dataPath,
			{
				headers : { 
					'Content-Type': 'application/json',
					'Accept': 'application/json'
				}
			}
		).then(function(response){
			return response.json();
	
		}).then(function(myJson) {
			setData(myJson)
		});
	}

	const outputOutline = (data) => {
		if (!data) {
			return "LOADING";
		}
		const output = data.outline.map((val, idx) => {
			return (<li key={idx}>
				{val.section} ({val.startSlideIndex} - {val.endSlideIndex})
			</li>);
		});
		return (<ul>
			{output}
		</ul>);
	}

	const outputSlideThumbnails = (data) => {
		if (!data) {
			return;
		}

		const thumbnailsPath = '/slideData/' + presentationID + '/images/';
		const output = data.slideInfo.map((slide, idx) => {
			const thumbnailPath = thumbnailsPath + slide.index.toString() + '.jpg';
			const title = "Script:\n\n" + slide.script + "\n\n\n\n\nOCR Result:\n\n" + slide.ocrResult;
			console.log(title);
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
					<div> {idx} </div>	
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

	const outputPaper = (data) => {
		console.log(data);
	}
	
	useEffect(()=>{
		getData();
	}, []);
	return (
		<div className="App">
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
				{outputPaper(data)};
			</div>
		</div>
	);
}

export default App;
