import React, { useRef, useEffect } from "react"
import BGpublic from './public/page'
import BGprivate from './private/page'

function Background({type}) {

	const canva = useRef(null)

	useEffect(() => {
		if (canva.current)
			canva.current.style.filter = 'blur(5px)'
	}, [])

	return (
		<div className="position-fixed top-0">
			{type == "public" ? <BGpublic canva={canva}/> : <BGprivate canva={canva}/>}
		</div>
	)
}  

export default Background