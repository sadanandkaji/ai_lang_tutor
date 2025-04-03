
import './App.css'
import { BrowserRouter,Route,Routes } from "react-router-dom"
import Dashboard from './components/lib/dashboard'
import Summary from './components/lib/summary'
import Review from './components/lib/review'




function App() {
  

  return <>
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path='/summary' element={<Summary/>}/>
      <Route path='/review'  element={<Review/>}/>
     
   
    </Routes>
  </BrowserRouter>
  </>
  
}

export default App
