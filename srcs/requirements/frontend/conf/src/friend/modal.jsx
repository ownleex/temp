import React, { useState } from "react"
import { Modal, Tabs, Tab } from "react-bootstrap"
import ErrorModal from "../global/error-modal"
import ListModal from "./list"
import SearchModal from "./search"
import RequestModal from "./request"
import BlockModal from "./block"

function FriendModal({ friend, setFriend }) {

	const handleClose = () => setFriend(false)
	const [tab, setTab] = useState('friendlist')

	const [show, setShow] = useState(false)
	const hideModal = () => setShow(false)
	const [info, setInfo] = useState("")

	return (
		<Modal show={friend} onHide={handleClose}>
			<Modal.Header closeButton />
			<Modal.Body>
				<Tabs activeKey={tab} onSelect={setTab} fill>
					<Tab eventKey="friendlist" title="Friend List">
						<ListModal tab={ tab } setShow={ setShow } setInfo={ setInfo }/>
					</Tab>
					<Tab eventKey="addfriend" title="Add Friend">
						<SearchModal tab={ tab } setShow={ setShow } setInfo={ setInfo }/>
					</Tab>
					<Tab eventKey="friendrequest" title="Friend Request">
						<RequestModal tab={ tab } setShow={ setShow } setInfo={ setInfo }/>
					</Tab>
					<Tab eventKey="blocklist" title="Block List">
						<BlockModal tab={ tab } setShow={ setShow } setInfo={ setInfo }/>
					</Tab>
    			</Tabs>
			</Modal.Body>
			<ErrorModal show={ show } hideModal={ hideModal } contextId={ 3 } info={ info } />
		</Modal>
	)
}

export default FriendModal