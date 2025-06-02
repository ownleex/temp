import * as THREE from 'three'
import { setAll } from './shapes'

const createCanva = (canva, state, groupName, groupScore, scene) => {

	const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1)
	camera.position.set(35, -30, 30)
	camera.lookAt(35, 15, 5)
	
	const renderer = new THREE.WebGLRenderer({ canvas: canva, antialias: true })
	renderer.shadowMap.enabled = true
	renderer.shadowMap.type = THREE.VSMShadowMap
	renderer.toneMapping = THREE.ACESFilmicToneMapping
	renderer.toneMappingExposure = 2.0
	renderer.setSize(window.innerWidth, window.innerHeight)

	const objects = setAll(scene, state, groupName, groupScore)

	return { renderer, camera, objects }
}

export default createCanva