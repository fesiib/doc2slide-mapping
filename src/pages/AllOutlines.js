import axios from 'axios'
import {useState, useEffect} from 'react';
import Outline from '../components/Outline';
import PipelineAccuracy from '../components/PipelineAccuracy';
import ModelConfig from '../components/ModelConfig';

const PRESENTATION_IDS = [0];

function AllOutlines(props) {
    const similarityType = props?.similarityType;
    const outliningApproach = props?.outliningApproach;
    const applyThresholding = props?.applyThresholding;

	const [data, setData] = useState({});
	
	useEffect(() => {
        for (let presentationId of PRESENTATION_IDS) {
            axios.post('http://localhost:3555/get_data', {
                presentationId: presentationId,
                similarityType: similarityType,
                outliningApproach: outliningApproach,
                applyThresholding: applyThresholding,
            }).then( (response) => {
                console.log(response);
                setData({
                    ...data,
                    [presentationId]: response.data.data,
                });
            });
        }

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
                </div>
                <PipelineAccuracy evaluationData={curData?.evaluationData}/>
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
