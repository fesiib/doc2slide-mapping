import React from "react";

function ComparisonTable(props) {
    const paragraphs = props?.paragraphs;
    const scripts = props?.scripts;
    const sections = props?.sections;

    const outputParagraphs = paragraphs.map((paragraph, idx) => {
        return (
            <div key={"paragraph_" + idx.toString()} style={{
                display:  "flex",
                gap: 10,
                margin: 10,
            }}>
                {idx}
                <div>
                    <p> { sections[idx] }</p>
                    <p> { paragraph } </p>
                </div>
            </div>
        )
    });

    const outputScripts = scripts.map((script, idx) => {
        return (
            <div key={"script_" + idx.toString()} style={{
                display:  "block",
                gap: 10,
                margin: 10,
            }}>
                {idx}
                <div>
                    {script}
                </div>
            </div>
        )
    });

    return (<div>
        <h2> Comparison: Paper paragraphs (left) - Slide Scripts (right) </h2>
        <div style={{
            display: "flex",
            flexDirection: "row",
            textAlign: "left",
            margin: 20,
        }}>
            <div style={{
                width: "50%",
            }}>
                {outputParagraphs}
            </div>
            
            <div style={{
                width: "50%",
            }}>
                {outputScripts}
            </div>
        </div>
    </div>)
}

export default ComparisonTable;