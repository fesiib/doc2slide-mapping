import { useEffect, useState } from "react";
import axios from "axios";
import "../App.css";
import SlideThumbnails from "../components/SlideThumbnails";

const EXAMPLES = {
    ["Title Page (1-1)"]: {
        startIdx: 1,
        endIdx: 1,
    },
    ["Background and Motivation  (2-13)"]: {
        startIdx: 2,
        endIdx: 13,
    },
    ["Study 1  (14-30)"]: {
        startIdx: 14,
        endIdx: 30,
    },
    ["Study 2  (31-46)"]: {
        startIdx: 31,
        endIdx: 46,
    },
    ["Design Implications  (47-49)"]: {
        startIdx: 47,
        endIdx: 49,
    },
    ["End  (50-50)"]: {
        startIdx: 50,
        endIdx: 50,
    },
};

function SectionTransitionExamples() {
    const presentationId = 0;

    const [data, setData] = useState(null);

    useEffect(() => {
        axios.post('http://server.hyungyu.com:7777/mapping/presentation_data', {
            presentationId: presentationId,
        }).then( (response) => {
            console.log(response);
            setData(response.data.data);
        });
    }, []);

    return (<div 
        className="App"
        style={{
            textAlign: "left",
            margin: "2em",
        }}
    >
        <h2> Definition: Section Transition </h2>
        <div>
            <p>
                Please specify <b> not more than 5-6 transitions</b>.
            </p>
            <p>
            <b> Section Transition </b> is a major topic/section transitions that can be detected from slides {"&"} scripts.
            </p>
            <div>
                Example Transitions: 
                <ul>
                    {
                        Object.keys(EXAMPLES).map((exampleTitle, idx) => {
                            return (
                                <li key={idx}> {exampleTitle}
                                    <SlideThumbnails 
                                        presentationId={presentationId}
                                        slideInfo={data?.slideInfo}
                                        startIdx={EXAMPLES[exampleTitle].startIdx}
                                        endIdx={EXAMPLES[exampleTitle].endIdx + 1}
                                    />       
                                </li>
                            )
                        })
                    }
                </ul>
            </div>
        </div>
        <a href={"annotation"}> Go Back </a>
    </div>)
}

export default SectionTransitionExamples;