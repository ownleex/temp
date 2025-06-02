import React, { useEffect, useState, useRef } from "react"
import { useNavigate } from "react-router-dom"
import { Image, Form, Button } from "react-bootstrap"
import { useAuth } from "../../auth/context"
import ErrorModal from "../../global/error-modal"
import axiosInstance from '../../auth/instance'

function ProfileEdit({ user }) {

	const navigate = useNavigate()
	const { refreshUser } = useAuth()

	const [file, setFile] = useState(null)
	const [preview, setPreview] = useState(null)
	const [text, setText] = useState("")

	const fileInputRef = useRef(null)

	const [show, setShow] = useState(false)
	const hideModal = () => setShow(false)
	const [info, setInfo] = useState("")

	const updateInfo = async (string) => {

		try {
			const formData = new FormData()
			if (text)
				formData.append('description', text)
			if (string == "reset") {
				const response = await fetch("/default.jpg")
				const blob = await response.blob()
				const defaultFile = new File([blob], "default.jpg", { type: blob.type })
				formData.append("avatar", defaultFile)
			}
			else if (file)
				formData.append('avatar', file)
			const response = await axiosInstance.put('/users/api/player/update-info/', formData)
			if (response.data.code == 1000) {
				await refreshUser()
				navigate(`/profile/${user.name}`)
			}
		}
		catch(error) {
			setFile(null)
			setPreview(null)
			if (fileInputRef.current)
				fileInputRef.current.value = null
			if (error && error.response && error.response.data && error.response.data.message) {
				setInfo(error.response.data.message)
				setShow(true)
			}
		}
	}

	useEffect(() => {
		if (!file) return;
		const reader = new FileReader();
		reader.onloadend = () => {
		setPreview(reader.result);
	};
	reader.readAsDataURL(file);
	}, [file])

	return (
		<>
			<Image src={user.avatar} className={`${user.online
                	? "border border-success"
                	: "border border-danger"} border-3 rounded-circle`}
                style={{ width: "150px", height: "150px", objectFit: "cover" }} />
            {file && !show &&
                <Image src={preview} className={`${user.online
                       	? "border border-success"
                       	: "border border-danger"} border-3 rounded-circle`}
                    style={{ width: "150px", height: "150px", objectFit: "cover" }} />}
            <Form>
                <Form.Group>
        	        <Form.Control type="file" onChange={(e) => setFile(e.target.files[0])} id="formFile" ref={fileInputRef}/>
                    <Form.Control type="text" value={text} onChange={(e) => setText(e.target.value)} id="formText" />
                </Form.Group>
            </Form>
            <Button className="rounded-0 btn btn-dark fw-bolder" onClick={() => updateInfo("")}>
                <i className="bi bi-pencil" style={{ fontSize: "20px" }} />
            </Button>
			<Button className="rounded-0 btn btn-dark fw-bolder" onClick={() => updateInfo("reset")}>
                Reset Avatar
            </Button>
			<ErrorModal show={ show } hideModal={ hideModal } contextId={ 6 } info={ info } />
		</>
	)
}

export default ProfileEdit
