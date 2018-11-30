import {ACTION_1} from './action'

const initialState ={
	loading : false,
	text    :'whatever you want'
}

export default reducer = (state = initialState, action) => {
	
	switch (action.type){

		case ACTION_1: 
		{
			return {
				...state, 
				text : action.payload 
			}
		}

		default:

			return state;

	}

}