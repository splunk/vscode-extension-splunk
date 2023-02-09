import React, { useState } from "react";
import ButtonGroup from '@splunk/react-ui/ButtonGroup';
import Button from '@splunk/react-ui/Button';
import styled from "styled-components";

const ToggleButton = styled(Button)`
font-size: 10px;
margin-bottom: 10px;

border: 0px;
box-shadow: 0;
&:not([disabled]):focus {
    border: 0;
    outline: none; 
    box-shadow: none !important;
}
`
export default function VizSelector({value, onChange, isCollapsed}) {

    const [collapsed, setCollapsed] = useState(isCollapsed || false)

    const onCollapse = function() {
        setCollapsed(true)
    }

    const onExpand = function() {
        setCollapsed(false)
    }

    return (
        <div style={{"display": "flex", "justifyContent": "space-between"}}>
        <div>
        {!collapsed &&
        <ButtonGroup tabIndex={-1} style={{"marginBottom": 10}}>
            <Button tabIndex={-1} selected={value == "events" ? true : false} onClick={() => onChange("events")}>Events</Button>
            <Button tabIndex={-1} selected={value == "single" ? true : false}  onClick={() => onChange("single")}>Single</Button>
            <Button tabIndex={-1} selected={value == "table" ? true : false}  onClick={() => onChange("table")}>Table</Button>
            <Button tabIndex={-1} selected={value == "line" ? true : false}  onClick={() => onChange("line")}>Line</Button>
            <Button tabIndex={-1} selected={value == "column" ? true : false}  onClick={() => onChange("column")}>Column</Button>
            <Button tabIndex={-1} selected={value == "bar" ? true : false}  onClick={() => onChange("bar")}>Bar</Button>
            <Button tabIndex={-1} selected={value == "area" ? true : false}  onClick={() => onChange("area")}>Area</Button>
            <Button tabIndex={-1} selected={value == "pie" ? true : false}  onClick={() => onChange("pie")}>Pie</Button>
            <Button tabIndex={-1} selected={value == "scatter" ? true : false}  onClick={() => onChange("scatter")}>Scatter</Button>
            <Button tabIndex={-1} selected={value == "bubble" ? true : false}  onClick={() => onChange("bubble")}>Bubble</Button>
            <Button tabIndex={-1} selected={value == "punchcard" ? true : false}  onClick={() => onChange("punchcard")}>Punchcard</Button>
            <Button tabIndex={-1} selected={value == "link" ? true : false}  onClick={() => onChange("link")}>Link</Button>
        </ButtonGroup>}
        </div>
        <div>
        {collapsed ?       
            <ToggleButton tabIndex={-1} onClick={onExpand} appearance="flat">Show Chart Selector</ToggleButton> 
            :     
            <ToggleButton tabIndex={-1} onClick={onCollapse} appearance="flat">Hide Chart Selector</ToggleButton> 
        }
        </div>
        </div>
    )
}