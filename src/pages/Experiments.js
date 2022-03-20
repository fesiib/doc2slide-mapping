import axios from 'axios';
import { useEffect, useState } from "react";
import SlideThumbnails from '../components/SlideThumbnails';

const INTERVAL = 10;
const PRESENTATION_IDS_CNT = 745;

function Experiments() {
    const [allPresentations, setAllPresentations] = useState([])
    const [showAllSlides, setShowAllSlides] = useState(false);
    const [startPresentationId, setStartPresentationId] = useState(0);
    const [endPresentationId, setEndPresentationId] = useState(INTERVAL);

    useEffect(() => {
        let presentationIds = []
        for (let presentationId = startPresentationId; presentationId < endPresentationId; presentationId++) {
            presentationIds.push(presentationId);
        }
        axios.post('http://server.hyungyu.com:7777/mapping/bulk_data', {
            presentationIds: presentationIds
        }).then( (response) => {
            console.log(response);
            const bulkData = response.data.bulkData;
            let _allPresentations = []
            for (let presentationData of bulkData) {
                _allPresentations.push(presentationData);
            }
            setAllPresentations(_allPresentations);
        });
    }, [startPresentationId, endPresentationId])
    
    const outputKRandomPerPresentation = (k) => {
        let output = []
        for (let presentationId = startPresentationId; presentationId < endPresentationId; presentationId++) {
            let row = [];
            for (let id = -1; id < k+2; id++) {
                //const rid = Math.round(Math.random() * 8) + 1;
                const rid = id + 1;
                let curLink = `http://server.hyungyu.com:7777/images/${presentationId}/${rid}.jpg`;
                
                if (id === -1) {
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
            let slideInfo = data?.slideInfo ? data.slideInfo : [];
            return <div key={allIdx} style={{
                margin: "1em",
            }}>
                <h2> ID: {presentationId} </h2>
                <SlideThumbnails
                    slideInfo={slideInfo}
                    presentationId={presentationId}
                    startIdx={1}
                    endIdx={data?.slideCnt}
                    outline={data?.outline}
                />
            </div>
        })
    }

    const outputSelectorRanges = (interval) => {
        let output = []
        for (let presentationId = 0; presentationId < PRESENTATION_IDS_CNT; presentationId += interval) {
            const start = presentationId;
            const end = Math.min(PRESENTATION_IDS_CNT, presentationId + interval);
            output.push(
                <option
                    value={start.toString() + "-" + end.toString()}
                    key={start.toString() + "-" + end.toString()}
                >
                    {start} - {end - 1}
                </option>
            );
        }
        return output
    }

    return (<div>
        <div style={{
            margin: "1em",
        }}>
            <label
                htmlFor="presentationIds"
            > Show All Slides </label>
            <select 
                id="presentationIds"
                value={
                    startPresentationId.toString()+'-'+endPresentationId.toString()
                }
                onChange={(event) => {
                    const value = event.target.value;
                    const ids = value.split("-").map((val) => Number.parseInt(val));
                    setStartPresentationId(ids[0])
                    setEndPresentationId(ids[1])
                }}
            >
                {
                    outputSelectorRanges(INTERVAL)
                }
            </select>
        </div>
        <div style={{
            margin: "1em",
        }}>
            <label
                htmlFor="showAllSlides"
            > Show All Slides </label>
            <input 
                id="showAllSlides"
                type="checkbox"
                value={showAllSlides}
                onChange={(event) => setShowAllSlides(event.target.checked)}
            />
        </div>
        {
            showAllSlides ?
            outputPresentations()
            :
            outputKRandomPerPresentation(4)
        }
    </div>)

}

export default Experiments;