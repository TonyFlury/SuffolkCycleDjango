div.barchart-outer {
background-image: url( '/static/SuffolkCycleRide/images/target-background.png' );
/* background-repeat:repeat-x; */
background-size: 100% 100%;
width:650px;
height:2em;
padding: 5px 5px;
margin:10px 0px 20px 0px;
position:relative;
border-radius: 10px;
display:flex;
box-shadow: 2px 2px 4px 2px rgba(0, 0, 0, 0.6);
border: thin solid grey ;
}


div.barchart-inner {
background-image: url( '/static/SuffolkCycleRide/images/target-foreground3.png' );
background-size: cover ;
border-radius: 5px;
height:calc( 2em - 2px);
position:absolute;
top:6px;
left:5px;
margin-left:5px;
margin-right:5px;
box-shadow: 1px 1px 2px 1px rgba(0, 0, 0, 0.6);
box-sizing: border-box;
width:auto;
}

div.barchart-inner-inset {
border-radius: 5px;
border: black solid white;
height:2em;
position:absolute;
top:5px;
left:5px;
margin-left:5px;
margin-right:5px;
box-shadow: -3px 3px 4px 1px rgba(0, 0, 0, 0.8) inset;
box-sizing: border-box;
width: 640px;
}

div.barchart-text {
font-weight: bold;
color: black ;
margin: auto;
display:block;
position:relative;
margin-left:5px;
margin-right:5px;
padding-left: 10px;
align-items: left;
}

div.picture {
box-shadow: 2px 2px 4px 2px rgba(0, 0, 0, 0.6);
}

div#statement-block,
div#url-block,
div.statement {
    margin-top:10px;
}

div#intro-block {
    margin-bottom:20px;
    text-align:center
}

div.statement {
    margin-left:20px;
}