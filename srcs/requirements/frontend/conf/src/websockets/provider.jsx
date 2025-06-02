import React from 'react'
import { Notification } from './notification'
import { Game } from './game'
import { Chat } from './chat'
import { PrivateChat } from './privateChat'

export const WebSocketProvider = ({ children }) => {

	return (
		<Notification>
			<Chat>
				<PrivateChat>
					<Game>
						{children}
					</Game>
				</PrivateChat>
			</Chat>
		</Notification>
	)
}
