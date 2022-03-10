import axios from 'axios'
import {useState, useEffect} from 'react';
import Outline from '../components/Outline';
import AnnotationList from '../components/AnnotationList';
import ModelConfig from '../components/ModelConfig';
import { ANNOTATION_PRESENTATION_IDS } from './Annotation';

const ALL_PRESENTATION_IDS = [
    0, 4, 6, 7, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 24, 26, 27, 28,
    29,
    //31, 32, 33,
    // 42, 43, 44, 46, 49, 72, 75, 78, 79, 80, 81, 82, 83, 84,
    // 85, 86, 87, 88, 89, 90, 91, 92, 94, 95, 96, 97, 98, 99,
    // 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111,
    // 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123,
    // 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135,
    // 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147,
    // 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159,
    // 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 171, 172,
    // 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184,
    // 185, 186, 188, 191, 192, 193, 194, 195, 196, 197, 198, 199,
    // 200, 201, 202, 204, 205, 207, 208, 209, 210, 211, 212
]

function AllOutlines(props) {
    const similarityType = props?.similarityType;
    const similarityMethod= props?.similarityMethod;
    const outliningApproach = props?.outliningApproach;
    const applyThresholding = props?.applyThresholding;
	const applyHeuristics = props?.applyHeuristics;

	const [data, setData] = useState({});
	
	useEffect(() => {
        let requests = [];
        for (let presentationId of ALL_PRESENTATION_IDS) {
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
