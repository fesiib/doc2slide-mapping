import axios from 'axios'
import {useState, useEffect} from 'react';
import HeatMap from '../components/HeatMap';
import Outline from '../components/Outline';
import SlideThumbnails from '../components/SlideThumbnails';
import ComparisonTable from '../components/ComparisonTable';
import PipelineAccuracy from '../components/PipelineAccuracy';
import ModelConfig from '../components/ModelConfig';
import AnnotationList from '../components/AnnotationList';

function SingleExample(props) {
    const presentationId = props?.presentationId;
    const similarityType = props?.similarityType;
	const similarityMethod = props?.similarityMethod;
    const outliningApproach = props?.outliningApproach;
    const applyThresholding = props?.applyThresholding;
	const applyHeuristics = props?.applyHeuristics;

	const [data, setData] = useState(null);
	const [paragraphs, setParagraphs] = useState([]);
	const [scripts, setScripts] = useState([]);
	const [sections, setSections] = useState([]);
	
	useEffect(() => {
		axios.post('http://localhost:7777/mapping/process_presentation', {
			presentationId: presentationId,
			similarityType: similarityType,
			similarityMethod: similarityMethod,
			outliningApproach: outliningApproach,
			applyThresholding: applyThresholding,
			applyHeuristics: applyHeuristics,
		}).then( (response) => {
			console.log(response);
			setParagraphs(response.data.paper);
			setScripts(response.data.script);
			setSections(response.data.sections);
			setData(response.data.data);
		});

	}, [presentationId, similarityType, similarityMethod, outliningApproach, applyThresholding, applyHeuristics]);

	if (!data) {
		return <div> LOADING !!! </div>
	}
	return (
		<div>
            <ModelConfig
                similarityType={similarityType}
				similarityMethod={similarityMethod}
                outliningApproach={outliningApproach}
                applyThresholding={applyThresholding}
				applyHeuristics={applyHeuristics}
            />
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
				<AnnotationList annotations={data?.annotations} slideInfo={data?.slideInfo}/>
				
			</div>
			<PipelineAccuracy evaluationData={data?.evaluationData}/>
			<ComparisonTable paragraphs={paragraphs} scripts={scripts} sections={sections}/>
		</div>
	);
}

export default SingleExample;
