import React from 'react';
import {StyleSheet, View} from 'react-native';

export default class SideMenu extends React.Component{
	 render(){
	 	return(
       <View style={styles.container}/>
     )
	 }
}


const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});