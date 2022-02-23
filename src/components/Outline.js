import React from 'react'

function Outline(props) {
    const isGenerated = props?.isGenerated;
    const outline = props?.outline;
    const slideInfo = props?.slideInfo;

    if (!outline) {
        return <div> {"LOADING"} </div>;
    }
    const output = outline.map((val, idx) => {
        const startSlide = slideInfo[val.startSlideIndex]
        const endSlide = slideInfo[val.endSlideIndex]

        const duration = new Date(0);
        duration.setSeconds(endSlide.endTime - startSlide.startTime);
        return (<li key={idx}>
            ({val.startSlideIndex} - {val.endSlideIndex}) {"\t"} {val.sectionTitle} {"\t"} {duration.getMinutes()}:{duration.getSeconds()}
        </li>);
    });
    return (<div style={{
        margin: "1em",
    }}>
        <h3> {isGenerated ? "Generated Outline" : "Ground Truth Outline"} </h3>
        <ol>
            {output}
        </ol>
    </div>);
}

export default Outline;