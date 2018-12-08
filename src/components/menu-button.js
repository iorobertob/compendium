import React from 'react'
import { View } from 'react-native'
import { Icon } from 'react-native-elements'
import { withNavigation } from 'react-navigation';
import { DrawerActions } from 'react-navigation-drawer';

class MenuButton extends React.Component {
	 render(){
	 	return(
      <View style={{flexDirection:'row', alignItems:'center'}}>
        <Icon 
          reverse 
          color='white' 
          reverseColor='gray' 
          type='material-community' 
          name='menu' 
          onPress={() => this.props.navigation.dispatch(DrawerActions.toggleDrawer())}
        />
      </View>
     )
	 }
}

export default withNavigation(MenuButton)