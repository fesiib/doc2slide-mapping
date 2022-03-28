import axios from 'axios'
import {useState, useEffect} from 'react';
import Outline from '../components/Outline';
import AnnotationList from '../components/AnnotationList';
import ModelConfig from '../components/ModelConfig';

const SHORT_PRESENTATION_IDS = [
    439, 510, 90, 589, 674, 689, 549, 13, 307, 477, 106, 161, 271, 214, 147, 318, 372, 46, 231, 504
    //11, 12, 13, 14, 15, 16,
];

function AllOutlines(props) {
    const similarityType = props?.similarityType;
    const similarityMethod= props?.similarityMethod;
    const outliningApproach = props?.outliningApproach;
    const applyThresholding = props?.applyThresholding;
	const applyHeuristics = props?.applyHeuristics;

	const [data, setData] = useState({});
	
	useEffect(() => {
        let requests = [];
        const presentationIds = [
            ...SHORT_PRESENTATION_IDS
        ];
        for (let presentationId of presentationIds) {
            requests.push(axios.post('http://server.hyungyu.com:7777/mapping/presentation_data_specific', {
                presentationId: presentationId,
                similarityType: similarityType,
                similarityMethod: similarityMethod,
                outliningApproach: outliningApproach,
                applyThresholding: applyThresholding,
                applyHeuristics: applyHeuristics,
            }));
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
                    <Outline title="Generated" outline={curData?.outline} slideInfo={curData?.slideInfo} />
                    <AnnotationList 
                        gtOutline={curData?.groundTruthOutline}
                        annotations={curData?.annotations}
                        slideInfo={curData?.slideInfo}
                        evaluationData={curData?.evaluationData}
                    />
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
