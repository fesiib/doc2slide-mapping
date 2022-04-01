function LineChart(props) {
    const data = props?.data ? props.data : [];
    const width = props?.width ? props.width : 500;
    const height = props?.height ? props.height : 500;
    const shift = 10;

    if (data.length === 0) {
        return null;
    }


    let dataWidth = data.length + shift * 2;
    let dataHeight = 0;
    for (let val of data) {
        dataHeight = Math.max(val, dataHeight);
    }
    dataHeight += shift * 2;

    return <div>
        <h4> Frame Changes </h4>
        <svg version="1.1"
            width={width} height={height + 100}
            xmlns="http://www.w3.org/2000/svg"
            viewBox={`0 0 ${dataWidth} ${dataHeight}`}
            preserveAspectRatio="none"
            style={{
                backgroundColor: "lightgray"
            }}
        >
            {
                data.map((val, idx) => {
                    if (idx === 0) {
                        return null;
                    }
                    return (
                        <line
                            transform={`scale(1, -1) translate(0, -${dataHeight})`}
                            x1={idx + shift}
                            y1={data[idx-1] + shift} 
                            x2={idx + 1 + shift}
                            y2={val + shift}
                            stroke="black"
                            stroke-width="1"/>
                    );
                })
            }
        </svg>
    </div>
}

export default LineChart;