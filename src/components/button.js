import React from 'react';
import {StyleSheet, Text, View, TouchableHighlight, Button} from 'react-native';



export default class MyButton extends React.Component{
	 render(){
	 	return(
	 		<Button 
	 		title='TITLE' 
	 		color='#AAA'
	 		onPress={this.props.pressThisButton}/>
      );
	 }
}


const styles = StyleSheet.create({
  buttonStyle: {
    flex: 1,
    backgroundColor: '#AAA',
    alignItems: 'center',
    justifyContent: 'center',
  },
});