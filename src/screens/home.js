import React from 'react'
import { StyleSheet, View } from 'react-native'
import { connect}   from 'react-redux'
import { changeText} from '../store/action'
import { MapView } from 'expo'
import Search from '../components/search-bar'
import MenuButton from '../components/menu-button'

class Home extends React.Component {

  static navigationOptions = {
      title: '',
      headerTransparent:true,
      headerRight:(
        <Search/>
      ),
      headerLeft:(
        <MenuButton/>
      ),
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
  },
})

const mapStateToProps = (state) => {
  return {
     text:state.events.text,
  };
}

const mapDispatchToProps = dispatch => { 
  return {
	  changeTextProp: (text) => dispatch(changeText(text)),
  }
}

export default connect (mapStateToProps,mapDispatchToProps)(Home)