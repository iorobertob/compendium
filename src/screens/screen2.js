import React        from 'react';
import MyButton     from '../components/button';
import { StyleSheet, Text, View }       from 'react-native';
import { connect}   from 'react-redux';
import { changeText} from '../store/action';
import {createStackNavigator} from 'react-navigation';

class Screen2 extends React.Component {
  render() {
    
    return (
    
        <View style={styles.container}>
          <Text>Second page</Text>
        </View>
    )
  }
}

const styles = StyleSheet.create({
  container:{
    flex: 1,
    backgroundColor : '#FFF',
    alignItems      : 'center',
    justifyContent  : 'center',
  }
})

const mapStateToProps = (state) => {
  return{
     text:state.events.text
  }
}


const mapDispatchToProps = dispatch => { 
  return {
	changeTextProp: (text) => dispatch(changeText(text))
}}


export default connect (mapStateToProps,mapDispatchToProps)(Screen2)
