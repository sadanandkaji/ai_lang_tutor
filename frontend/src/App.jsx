
import './App.css'
import { BrowserRouter,Route,Routes } from "react-router-dom"
import Dashboard from './components/lib/dashboard'
import Summary from './components/lib/summary'




function App() {
  

  return <>
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path='/summary' element={<Summary/>}/>
     
   
    </Routes>
  </BrowserRouter>
  </>
  
}

export default App
