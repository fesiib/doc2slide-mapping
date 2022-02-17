import React, { useState } from "react";
import { HeatMapGrid } from "react-grid-heatmap";

function HeatMap(props) {
    const data = props.data;
    const paragraphs = props.paragraphs;
    const scripts = props.scripts;

    const [script, setScript] = useState(null);
    const [paragraph, setParagraph] = useState(null);

    const cellHeight = "10px";

    let scaleBar = [];
    for (let i = 0; i < data.length; i++) {
        scaleBar.push([(data.length - i) / data.length]);
    }

    return (
        <div style={{
            margin: "1em"
        }}>
            <div style={{
                display: "flex",
                gap: "2em"
            }}>
                <HeatMapGrid
                    data={scaleBar}
                    square={false}
                    cellHeight={"13px"}
                    cellStyle={(x, y, value) => {
                        const hue = (1 - value)
                        return {
                            background: `hsl(${hue*240}, 100%, 50%)`
                        };
                    }}
                    cellRender={(x, y, value) => {
                        return Math.round(value*100)/100;
                    }}
                
                />
                <HeatMapGrid
                    data={data}
                    square={true}
                    cellHeight={cellHeight}
                    cellStyle={(x, y, value) => {
                        const hue = (1 - value);
                        return {
                            background: `hsl(${hue*240}, 100%, 50%)`
                        };
                    }}
                    onClick={(x, y) => {
                        setParagraph(x);
                        setScript(y);
                    }}
                />
            </div>
            <div style={{
                display: "flex",
                flexDirection: "row",
                textAlign: "left",
                margin: 20,
                gap: 20,
            }}>
                <div style={{
                    width: "10%",
                }}>
                    {paragraph !== null ? `Score: ${data[paragraph][script]}` : "?"}
                </div>
                <div style={{
                    width: "45%",
                }}>
                    {paragraph !== null ? `${paragraph} ${paragraphs[paragraph]}` : "Select"}
                </div>
                
                <div style={{
                    width: "45%",
                }}>
                    {script !== null ? `${script} ${scripts[script]}` : "Select"}
                </div>
            </div>
        </div>
    )
}

export default HeatMap;

