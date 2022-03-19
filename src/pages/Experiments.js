function Experiments() {
    const startPresentationId = 1;
    const endPresentationId = 744;
    
    const outputKRandomPerPresentation = (k) => {
        let output = []
        for (let presentationId = startPresentationId; presentationId < endPresentationId; presentationId++) {
            let row = [];
            for (let id = 0; id < k+2; id++) {
                //const rid = Math.round(Math.random() * 8) + 1;
                const rid = id + 1;
                let curLink = `http://internal.kixlab.org:7778/images/${presentationId}/${rid}.jpg`;
                
                if (id === k) {
                    curLink = `http://internal.kixlab.org:7778/images/${presentationId}/acc_frame_0.jpg`;    
                }
                else if (id === k+1) {
                    curLink = `http://internal.kixlab.org:7778/images/${presentationId}/edges_acc_frame_0.jpg`;    
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

    return (<div>
        {outputKRandomPerPresentation(3)}
    </div>)

}

export default Experiments;