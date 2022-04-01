import axios from 'axios'
import {useState, useEffect} from 'react';
import Outline from '../components/Outline';
import AnnotationList from '../components/AnnotationList';
import ModelConfig from '../components/ModelConfig';
import PipelineAccuracy from '../components/PipelineAccuracy';

const SHORT_PRESENTATION_IDS = [
    13,
    46,
    90,
    106,
    147,
    161,
    214,
    231,
    271,
    307,
    318,
    372,
    439,
    477,
    504,
    510,
    549,
    589,
    674,
    689
    //11, 12, 13, 14, 15, 16,
];

const NULL_EVALUATION_DATA = {
    boundariesAccuracy: 0,
    timeAccuracy: 0,
    structureAccuracy: 0,
    overallTimeAccuracy: 0,
    separateTimeAccuracy: [0, 0, 0],
    overallSlidesAccuracy: 0,
    separateSlidesAccuracy: [0, 0, 0],
    mappingAccuracy: 0,
    separateMappingAccuracy: [0, 0, 0],
};

function AllOutlines(props) {
    const similarityType = props?.similarityType;
    const similarityMethod= props?.similarityMethod;
    const outliningApproach = props?.outliningApproach;
    const applyThresholding = props?.applyThresholding;
	const applyHeuristics = props?.applyHeuristics;

	const [data, setData] = useState({});

    const [avgGTEvaluation, setAvgGTEvaluation] = useState({ ...NULL_EVALUATION_DATA });

    const [badPresentationIds, setBadPresentationIds] = useState([]);

    const isBadPresentation = (groundTruth) => {
        // if (groundTruth.hasOwnProperty("separateSlidesAccuracy")) {
        //     return groundTruth.separateSlidesAccuracy[2] < 0.4;
        // }

        if (groundTruth.hasOwnProperty("overallSlidesAccuracy")) {
            return groundTruth.overallSlidesAccuracy < 0.5;
        }
        return false;
    }
	
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
            let curBadPresentationIds = []
            let curData = {};
            let curAvgGTEvaluation = { ...NULL_EVALUATION_DATA }
            let cnt = 0

            for (let response of responses) {
                console.log(response);
                const presentationId = response.data.presentationId;
                const data = response.data.data;
                curData = {
                    ...curData,
                    [presentationId]: data
                };
                const gtEvaluation = data?.evaluationData?.groundTruth;

                if (gtEvaluation) {
                    if (isBadPresentation(gtEvaluation)) {
                        curBadPresentationIds.push(presentationId);
                    }
                    cnt++;
                    for (let key in curAvgGTEvaluation) {
                        if (
                            key === "separateTimeAccuracy"
                            || key === "separateSlidesAccuracy"
                            || key === "separateMappingAccuracy"
                        ) {
                            for (let i = 0; i < 3; i++) {
                                curAvgGTEvaluation[key][i] += gtEvaluation[key][i];
                            }
                        }
                        else {
                            curAvgGTEvaluation[key] += gtEvaluation[key];
                        }
                    }
                }
            }
            if (cnt > 0) {
                for (let key in curAvgGTEvaluation) {
                    if (
                        key === "separateTimeAccuracy"
                        || key === "separateSlidesAccuracy"
                        || key === "separateMappingAccuracy"
                    ) {
                        for (let i = 0; i < 3; i++) {
                            curAvgGTEvaluation[key][i] = Math.round(curAvgGTEvaluation[key][i] / cnt * 1000) / 1000;
                        }
                    }
                    else {
                        curAvgGTEvaluation[key] = Math.round(curAvgGTEvaluation[key] / cnt * 1000) / 1000;
                    }
                }
            }
            setData(curData);
            setAvgGTEvaluation(curAvgGTEvaluation);
            setBadPresentationIds(curBadPresentationIds);

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
            <PipelineAccuracy
                title={"Average Accuracy"}
                evaluationData={avgGTEvaluation}
            />
            <div style={{
                textAlign: "left",
                margin: "2em",
            }}>
                <h3> Bad Presentation Ids: </h3>
                <div> {badPresentationIds.map((val) => val + ", ")} </div>
            </div>
            {outputOutlines()}
		</div>
	);
}

export default AllOutlines;
