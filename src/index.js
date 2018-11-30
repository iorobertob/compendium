import React        from 'react';
import MyButton     from './components/button';
import { StyleSheet, Text, View }       from 'react-native';
import { connect}   from 'react-redux';
import { changeText} from './store/action';
import {createStackNavigator, createAppContainer} from 'react-navigation';
import Home from './screens/home';
import Screen2 from './screens/screen2'


const MainNavigator = createStackNavigator({
  HomePage: {screen: Home},
  SecondPage: {screen: Screen2},},
  { initialRouteName : 'HomePage'}
  );

const Root = createAppContainer(MainNavigator);

export default Root