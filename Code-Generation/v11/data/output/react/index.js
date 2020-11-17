import React from "react";
import ReactDOM from "react-dom";
import {Block9,Block10,Block11,Block15,Block16} from "./blocks;"
class Main extends React.Component{
	
	render(){
		return (
			<Block9/>
			<Block10/>
			<Block11/>
			<Block15/>
			<Block16/>
		)
	}
}
ReactDOM.render(<Main />, document.getElementById('root'))