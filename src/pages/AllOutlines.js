import axios from 'axios'
import {useState, useEffect} from 'react';
import Outline from '../components/Outline';
import AnnotationList from '../components/AnnotationList';
import ModelConfig from '../components/ModelConfig';
import { LONG_PRESENTATION_IDS } from './Annotation';

const _LONG_PRESENTATION_IDS = [
    //100000, 100004, 100006, 100007, 100009,
    //100010, 100012, 100013, 100014, 100015, 100016, 100017, 100018, 100019,
];
const SHORT_PRESENTATION_IDS = [
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
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
            ...SHORT_PRESENTATION_IDS,
            //...LONG_PRESENTATION_IDS
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
