
import {Dimensions} from 'react-native';
import {createStackNavigator, createDrawerNavigator, createAppContainer} from 'react-navigation';
import Home from './screens/home';
import Screen2 from './screens/screen2'
import SideMenu from './components/side-menu';


const MainNavigator = createStackNavigator({
    HomePage: {
      screen: Home
    },
    SecondPage: {
      screen: Screen2, 
    },
  },{ 
    initialRouteName : 'HomePage',
  }
);

const MyDrawerNavigator = createDrawerNavigator(
  {
    Item1: {
      screen: MainNavigator,
    },
  },{
    contentComponent: SideMenu,
    drawerWidth: Dimensions.get('window').width * 0.85, 
  }
);

const Root = createAppContainer(MyDrawerNavigator);

export default Root