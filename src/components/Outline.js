import React from 'react'

function Outline(props) {
    const title = props?.title
    const outline = props?.outline;
    const slideInfo = props?.slideInfo;

    if (!outline | !slideInfo) {
        return <div> {"LOADING"} </div>;
    }
    const output = outline.map((val, idx) => {
        const startSlide = slideInfo[val.startSlideIndex]
        const endSlide = slideInfo[val.endSlideIndex]

        const duration = new Date(0);
        duration.setSeconds(endSlide.endTime - startSlide.startTime);
        return (<li key={idx}>
            <div style={{
                display:"flex",
            }}>

                <span style={{
                    padding: "1em"
                }}>
                    ({val.startSlideIndex} - {val.endSlideIndex}) 
                </span>
                
                <span style={{
                    padding: "1em"
                }}>
                    {val.sectionTitle} 
                </span>
                
                <span style={{
                    padding: "1em"
                }}>
                       {duration.getMinutes()}:{duration.getSeconds()} mins
                </span>
            </div>
        </li>);
    });
    return (<div style={{
        margin: "1em",
        display: "flex",
        flexDirection: "column",
    }}>
        <h4> {title} </h4>
        <ol style={{
            alignSelf: "center",
            margin: "0em",
            textAlign: "left",
            fontSize: "10px",
        }}>
            {output}
        </ol>
    </div>);
}

export default Outline;