import axios from 'axios'
import {useState, useEffect} from 'react';
import Outline from '../components/Outline';
import PipelineAccuracy from '../components/PipelineAccuracy';
import ModelConfig from '../components/ModelConfig';

const PRESENTATION_IDS = [0, 4, 6, 7, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20];

function AllOutlines(props) {
    const similarityType = props?.similarityType;
    const outliningApproach = props?.outliningApproach;
    const applyThresholding = props?.applyThresholding;

	const [data, setData] = useState({});
	
	useEffect(() => {
        let requests = [];
        for (let presentationId of PRESENTATION_IDS) {
            requests.push(axios.post('http://localhost:3555/get_data', {
                presentationId: presentationId,
                similarityType: similarityType,
                outliningApproach: outliningApproach,
                applyThresholding: applyThresholding,
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
	}, [similarityType, outliningApproach, applyThresholding]);

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
                    <Outline isGenerated={false} outline={curData?.groundTruthOutline} slideInfo={curData?.slideInfo} />
                    <PipelineAccuracy evaluationData={curData?.evaluationData}/>
                </div>
            </div>
        });
    }

	return (
		<div>
            <ModelConfig
                similarityType={similarityType}
                outliningApproach={outliningApproach}
                applyThresholding={applyThresholding}
            />
            {outputOutlines()}
		</div>
	);
}

export default AllOutlines;
