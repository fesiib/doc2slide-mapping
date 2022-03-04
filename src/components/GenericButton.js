function GenericButton(props) {
    const title = props?.title;
    const onClick = props?.onClick;
    const color = props?.color;
    return <button 
        onClick={onClick}
        style={{
            margin: "1em",
            height: "2em",
            background: (color ? color : "black"),
            color: "white"
        }}
    >
        {title}
    </button>
}

export default GenericButton;