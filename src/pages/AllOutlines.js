import axios from 'axios'
import {useState, useEffect} from 'react';
import Outline from '../components/Outline';
import PipelineAccuracy from '../components/PipelineAccuracy';
import AnnotationList from '../components/AnnotationList';
import ModelConfig from '../components/ModelConfig';

//const PRESENTATION_IDS = [0, 4, 6, 7, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20];

const PRESENTATION_IDS = [0, 4, 6, 7, 9];


function AllOutlines(props) {
    const similarityType = props?.similarityType;
    const similarityMethod= props?.similarityMethod;
    const outliningApproach = props?.outliningApproach;
    const applyThresholding = props?.applyThresholding;
	const applyHeuristics = props?.applyHeuristics;

	const [data, setData] = useState({});
	
	useEffect(() => {
        let requests = [];
        for (let presentationId of PRESENTATION_IDS) {
            requests.push(axios.post('http://server.hyungyu.com:7777/mapping/presentation_data_specific', {
                presentationId: presentationId,
                similarityType: similarityType,
                similarityMethod: similarityMethod,
                outliningApproach: outliningApproach,
                applyThresholding: applyThresholding,
                applyHeuristics: applyHeuristics,
            }))
        }
        Promise.all(requests).then( (responses) => {
            let curData = {};
            for (let response of responses) {
                console.log(response);
                curData = {
                    ...curData,
                    [response.data.presentationId]: response.data.data,
                };
            }
            setData(curData);
        });
	}, [similarityType, similarityMethod, outliningApproach, applyThresholding, applyHeuristics]);

	if (!data) {
		return <div> LOADING !!! </div>
	}

    const outputOutlines= () => {
        return Object.keys(data).map((presentationId, idx) => {
            const curData = data[presentationId];
            return <div key={idx}>
			    <h1> Presentation {presentationId} </h1>
                <div style={{
                    textAlign: "left",
                    fontSize: "15pt",
                    display: "flex",
                }}> 
                    <Outline isGenerated={true} outline={curData?.outline} slideInfo={curData?.slideInfo} />
                    <AnnotationList gtOutline={curData?.groundTruthOutline} annotations={curData?.annotations} slideInfo={curData?.slideInfo} />
                    <PipelineAccuracy evaluationData={curData?.evaluationData}/>
                </div>
            </div>
        });
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
            {outputOutlines()}
		</div>
	);
}

export default AllOutlines;
