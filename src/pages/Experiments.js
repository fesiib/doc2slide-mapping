import axios from 'axios';
import { useEffect, useState } from "react";
import SlideThumbnails from '../components/SlideThumbnails';

function Experiments() {
    const startPresentationId = 0;
    const endPresentationId = 100;

    const [allPresentations, setAllPresentations] = useState([])

    useEffect(() => {
        let requests = []
        for (let presentationId = startPresentationId; presentationId < endPresentationId; presentationId++) {
            const similarityType = "keywords";
            const similarityMethod = "tf-idf";
            const outliningApproach = "dp_mask";
            const applyThresholding = true;
            const applyHeuristics = true;
            requests.push(axios.post('http://server.hyungyu.com:7777/mapping/process_presentation', {
                presentationId: presentationId,
                similarityType: similarityType,
                similarityMethod: similarityMethod,
                outliningApproach: outliningApproach,
                applyThresholding: applyThresholding,
                applyHeuristics: applyHeuristics,
            }));
        }
        Promise.all(requests).then( (responses) => {
            let _allPresentations = []
            for (let response of responses) {
                _allPresentations.push(response.data);
            }
            setAllPresentations(_allPresentations);
        });
    }, [])
    
    const outputKRandomPerPresentation = (k) => {
        let output = []
        for (let presentationId = startPresentationId; presentationId < endPresentationId; presentationId++) {
            let row = [];
            for (let id = 0; id < k+2; id++) {
                //const rid = Math.round(Math.random() * 8) + 1;
                const rid = id + 1;
                let curLink = `http://server.hyungyu.com:7777/images/${presentationId}/${rid}.jpg`;
                
                if (id === k) {
                    curLink = `http://server.hyungyu.com:7777/images/${presentationId}/acc_frame_0.jpg`;    
                }
                else if (id === k+1) {
                    curLink = `http://server.hyungyu.com:7777/images/${presentationId}/edges_acc_frame_0.jpg`;    
                }
                const title = `presentaiton_${presentationId}_${rid}`;
                row.push((<img width={500} key={title} src={curLink} title={title}/>));
            }
            output.push((<div
                key={presentationId}
                style={{margin: "1em"}}
            >
                <h2> ID: {presentationId} </h2>
                <div
                    style={{
                        display: "flex",
                        flexDirection: "row",
                        overflow: "scroll",
                        gap: "1em",
                        margin: "1em",
                    }}
                >
                    {row}
                </div>
            </div>));
        }
        return output;
    }

    const outputPresentations = () => {
        return allPresentations.map((allData, allIdx) => {
            const presentationId = allData?.presentationId;
            const data = allData?.data;
            const script = allData?.script;
            let slideInfo = data?.slideInfo ? data.slideInfo : [];

            for (let idx = 0; idx < slideInfo.length; idx++) {
                slideInfo[idx].script = script[idx];
            }
            console.log(slideInfo); 
            return <div key={allIdx} style={{
                margin: "1em",
            }}>
                <h2> ID: {presentationId} </h2>
                <SlideThumbnails
                    slideInfo={slideInfo}
                    presentationId={presentationId}
                    startIdx={0}
                    endIdx={data?.slideCnt}
                />
            </div>
        })
    }

    return (<div>
        {outputKRandomPerPresentation(4)}
        {/* { outputPresentations() } */}
    </div>)

}

export default Experiments;