function GenericButton(props) {
    const title = props?.title;
    const onClick = props?.onClick;
    return <button 
        onClick={onClick}
        style={{
            margin: "1em",
            height: "2em",
        }}
    >
        {title}
    </button>
}

export default GenericButton;