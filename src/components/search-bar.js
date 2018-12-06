import React from 'react'
import { StyleSheet, View, Dimensions } from 'react-native'
import { Icon } from 'react-native-elements'
import {SearchBar} from 'react-native-elements'

const width = Dimensions.get('window').width * 0.6

export default class Search extends React.Component {

	render(){
	 	return(
      <View style={{flexDirection:'row', alignItems: 'center'}}>
        <SearchBar
          leftIconContainerStyle={styles.searchIconsStyle}
          rightIconContainerStyle={styles.searchIconsStyle}
          containerStyle={styles.searchcontainerStyle}
          inputStyle = {styles.searchInputStyle}
          lightTheme
          round
          searchIcon={{ size: 24 }}
          placeholder='Type Here...' 
        />
        <Icon reverse color='white' reverseColor='gray' type='material-community' name='tune' />
      </View>
    )
	}
}

const styles = StyleSheet.create({
  searchIconsStyle: {
    backgroundColor:'white',
    paddingLeft:10,
    marginLeft:0,
    marginRight:0
  },
  searchcontainerStyle: {
    width: width,
    backgroundColor:'transparent',
    borderWidth:0,
    borderBottomColor: 'transparent',
    borderTopColor: 'transparent'
  },
  searchInputStyle: {
    backgroundColor:'white',
    marginLeft: 0
  }

});