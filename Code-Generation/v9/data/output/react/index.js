import React from "react";
import ReactDOM from "react-dom";
import {Block1,Block2,Block3,Block7,Block8} from "./blocks;"
class Main extends React.Component{
	
	render(){
		return (
			<Block1/>
			<Block2/>
			<Block3/>
			<Block7/>
			<Block8/>
		)
	}
}
ReactDOM.render(<Main />, document.getElementById('root'))