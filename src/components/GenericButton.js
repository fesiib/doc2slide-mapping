function GenericButton(props) {
    const title = props?.title;
    const onClick = props?.onClick;
    const color = props?.color;
    const disabled = props?.disabled;
    return <button 
        disabled={disabled}
        onClick={onClick}
        style={{
            margin: "1em",
            height: "2em",
            background: (color ? color : "black"),
            color: "white",
            opacity: (disabled ? 0: 1),
        }}
    >
        {title}
    </button>
}

export default GenericButton;