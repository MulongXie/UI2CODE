import React from "react";
import ReactDOM from "react-dom";
import {Block17,Block18,Block19} from "./blocks;"
class Main extends React.Component{
	
	render(){
		return (
			<Block17/>
			<Block18/>
			<Block19/>
		)
	}
}
ReactDOM.render(<Main />, document.getElementById('root'))