import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import CreditIntelligenceDashboard from './CreditIntelligenceDashboard'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
    <div className="App">
      <CreditIntelligenceDashboard />
    </div>
    </>
  )
}




export default App

