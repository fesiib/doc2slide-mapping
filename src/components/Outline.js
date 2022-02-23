import React from 'react'

function Outline(props) {
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
    return (<ol>
        {output}
    </ol>);
}

export default Outline;