import React from 'react'
import ReactDOM from 'react-dom/client'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import { BrowserRouter } from 'react-router-dom'
import { AuthProvider } from "./auth/context.jsx"
import { WebSocketProvider } from './websockets/provider.jsx'
import App from './App'

const root = ReactDOM.createRoot(document.getElementById('root'))
root.render(
	<BrowserRouter>
		<AuthProvider>
			<WebSocketProvider>
				<App/>
			</WebSocketProvider>
		</AuthProvider>
	</BrowserRouter>
)