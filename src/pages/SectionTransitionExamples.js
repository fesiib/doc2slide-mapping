import { useEffect, useState } from "react";
import axios from "axios";
import "../App.css";
import SlideThumbnails from "../components/SlideThumbnails";

const EXAMPLE_OUTLINE_DICT = {
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

const EXAMPLE_OUTLINE = [
    {
        "sectionTitle": "TITLE",
        "startSlideIndex": 1,
        "endSlideIndex": 1
    },
    {
        "sectionTitle": "2 RELATEDWORK",
        "startSlideIndex": 2,
        "endSlideIndex": 5
    },
    {
        "sectionTitle": "1 INTRODUCTION",
        "startSlideIndex": 6,
        "endSlideIndex": 13
    },
    {
        "sectionTitle": "4 STUDY 1: QUALITATIVE STUDY OF REQUESTS AND RESPONSES",
        "startSlideIndex": 14,
        "endSlideIndex": 30
    },
    {
        "sectionTitle": "5 STUDY 2: REQUEST TYPES, RESPONSE FUNCTIONS, AND THE VALUE OF RESPONSES Methods",
        "startSlideIndex": 31,
        "endSlideIndex": 46
    },
    {
        "sectionTitle": "7 DESIGN IMPLICATIONS",
        "startSlideIndex": 47,
        "endSlideIndex": 49
    },
    {
        "sectionTitle": "END",
        "startSlideIndex": 50,
        "endSlideIndex": 50
    }
];

function AnnotationSummary(props) {
    const outline = props?.outline;
    const presentationId = props?.presentationId;
    const slideInfo = props?.slideInfo;

    return (<div>
        <ul>
            {
                outline.map((segment, idx) => {
                    return (
                        <li key={idx}> {segment.sectionTitle}
                            <SlideThumbnails 
                                presentationId={presentationId}
                                slideInfo={slideInfo}
                                startIdx={segment.startSlideIndex}
                                endIdx={segment.endSlideIndex + 1}
                            />       
                        </li>
                    )
                })
            }
        </ul>
    </div>)
}

function SectionTransitionExamples() {
    const presentationId = 100000;

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
            <b> Section Transition </b> is a major topic/section transitions that can be detected from slides {"&"} scripts.
            </p>
            <div>
                Presentation 0 Annotation: the slides were segmented based on high-level section titles in the original paper: 
                <AnnotationSummary
                    presentationId={presentationId}
                    outline={EXAMPLE_OUTLINE}
                    slideInfo={data?.slideInfo}
                />
            </div>
        </div>
        <a href={"annotation"}> Go Back </a>
    </div>)
}

export default SectionTransitionExamples;
export {
    AnnotationSummary
};