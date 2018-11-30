
export const ACTION_1 = 'This is one example action'

export const changeText = (newText) =>{
	return {
		type : ACTION_1,
		payload : newText
	}
}