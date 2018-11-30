import React        from 'react';
import MyButton     from '../components/button';
import { StyleSheet, Text, View }       from 'react-native';
import { connect}   from 'react-redux';
import { changeText} from '../store/action';
import {createStackNavigator} from 'react-navigation';
import { MapView } from 'expo';
import { Icon, SearchBar } from 'react-native-elements'

class Home extends React.Component {

  static navigationOptions = {
      title: '',
      headerTransparent:true,
      headerRight:(
        
        <View style={{flexDirection:'row', 
                      alignItems:'center'}}>
          <SearchBar
            leftIconContainerStyle={{backgroundColor:'white',
                                    paddingLeft:10,
                                    marginLeft:0,
                                    marginRight:0}}
            rightIconContainerStyle={{backgroundColor:'white',
                                    paddingRight:10,
                                    marginRight:0, 
                                    marginLeft:0}}
            containerStyle={{backgroundColor:'transparent',
                              borderWidth:0,
                              borderBottomColor: 'transparent',
                              borderTopColor: 'transparent'}}
            inputStyle = {{backgroundColor:'white',
                          marginLeft: 0}}
            lightTheme
            round
            searchIcon={{ size: 24 }}
            placeholder='Type Here...' />
          <Icon reverse color='white' reverseColor='gray' type='material-community' name='tune' />
        </View>
      ),
      headerLeft:(
        <View><Icon reverse color='white' reverseColor='gray' type='material-community' name='menu' /></View>
      )
  };


  render() {

    return (
        
        <View style={styles.container}>
          <MapView
            style={{ flex: 1 }}
            initialRegion={{
            latitude: 37.78825,
            longitude: -122.4324,
            latitudeDelta: 0.0922,
            longitudeDelta: 0.0421,
          }}/>
          {/* <Text style={{...styles.text, top:0}}>Filter</Text> */}
          <View style={{...styles.text}} >
              {/* <Icon type='material-community' name='tune' /> */}
          </View>
          
        </View>
 
    );
  }
} 

const styles = StyleSheet.create({
  container:{
    flex: 1
  },
  text:{
    position:"absolute",
    top: 50,
    right: 20,
    width: "auto",
    height: 20,
    paddingRight: 5,
  }
})



const mapStateToProps = (state) => {
  return{
     text:state.events.text
  };
}


const mapDispatchToProps = dispatch => { 
  return {
	changeTextProp: (text) => dispatch(changeText(text))
}}


export default connect (mapStateToProps,mapDispatchToProps)(Home)