import React, {useState} from 'react'
import axios from 'axios'

export default function App(){
  const [income, setIncome] = useState(5000)
  const [recurring, setRecurring] = useState(2500)
  const [savings, setSavings] = useState(500)
  const [result, setResult] = useState('')
  const [symbol, setSymbol] = useState('AAPL')
  const [quote, setQuote] = useState(null)
  const [history, setHistory] = useState([])
  const [file, setFile] = useState(null)
  const [wsMessages, setWsMessages] = useState([])
  const [wsConnected, setWsConnected] = useState(false)
  const [wsSocket, setWsSocket] = useState(null)

  const runDebt = async () =>{
    const payload = { user: { income: Number(income), recurring_spending: Number(recurring), savings: Number(savings), debts: [] } }
    const r = await axios.post('http://localhost:8000/analyze/debt', payload)
    setResult(r.data.summary)
  }

  const fetchQuote = async () =>{
    try{
      const r = await axios.get('http://localhost:8000/market/quote', { params: { symbol }})
      setQuote(r.data)
    }catch(e){
      setQuote({error: e.message})
    }
  }

  const fetchHistory = async () =>{
    try{
      const r = await axios.get('http://localhost:8000/market/history', { params: { symbol, period: '1mo' }})
      setHistory(r.data.history || [])
    }catch(e){
      setHistory([])
    }
  }

  const uploadCsv = async () =>{
    if(!file) return alert('Select a CSV file')
    const form = new FormData()
    form.append('file', file)
    form.append('doc_id', 'usercsv1')
    const r = await axios.post('http://localhost:8000/ingest/upload_csv', form, { headers: {'Content-Type': 'multipart/form-data'} })
    alert('Uploaded rows: ' + r.data.rows)
  }

  const startStream = (action) => {
    if(wsSocket) wsSocket.close()
    setWsMessages([])
    const ws = new WebSocket('ws://localhost:8000/ws/analyze')
    ws.onopen = () => {
      setWsConnected(true)
      ws.send(JSON.stringify({ action, user: { income: Number(income), recurring_spending: Number(recurring), discretionary_spending: 0, debts: [], savings: Number(savings) } }))
    }
    ws.onmessage = (evt) => {
      try{
        const data = JSON.parse(evt.data)
        setWsMessages(prev => [...prev, data])
      }catch(e){
        setWsMessages(prev => [...prev, { raw: evt.data }])
      }
    }
    ws.onclose = () => { setWsConnected(false); setWsSocket(null) }
    ws.onerror = () => { setWsConnected(false) }
    setWsSocket(ws)
  }

  return (
    <div style={{padding:20}}>
      <h1>Personal Financial Advisor (demo)</h1>
      <div>
        <label>Income: </label>
        <input value={income} onChange={e=>setIncome(e.target.value)} />
      </div>
      <div>
        <label>Recurring spending: </label>
        <input value={recurring} onChange={e=>setRecurring(e.target.value)} />
      </div>
      <div>
        <label>Savings: </label>
        <input value={savings} onChange={e=>setSavings(e.target.value)} />
      </div>
      <div style={{marginTop:10}}>
        <button onClick={runDebt}>Run Debt Analyzer</button>
      </div>

      <hr />
      <h2>Market Lookup</h2>
      <div>
        <label>Symbol: </label>
        <input value={symbol} onChange={e=>setSymbol(e.target.value.toUpperCase())} />
        <button onClick={fetchQuote} style={{marginLeft:8}}>Get Quote</button>
        <button onClick={fetchHistory} style={{marginLeft:8}}>Get 1mo History</button>
      </div>
      {quote && <pre style={{whiteSpace:'pre-wrap'}}>{JSON.stringify(quote, null, 2)}</pre>}
      {history.length>0 && (
        <div>
          <h3>History (last {history.length}):</h3>
          <pre style={{whiteSpace:'pre-wrap'}}>{JSON.stringify(history.slice(-10), null, 2)}</pre>
        </div>
      )}

      <hr />
      <h2>Upload Financial CSV</h2>
      <div>
        <input type="file" accept=".csv" onChange={e=>setFile(e.target.files[0])} />
        <button onClick={uploadCsv}>Upload CSV</button>
      </div>

      <hr />
      <h2>Live Analysis Stream</h2>
      <div>
        <button onClick={()=>startStream('debt')}>Stream Debt Analysis</button>
        <button onClick={()=>startStream('savings')} style={{marginLeft:8}}>Stream Savings Strategy</button>
        <button onClick={()=>startStream('debt_payoff')} style={{marginLeft:8}}>Stream Debt Payoff Plan</button>
      </div>
      <div style={{marginTop:10}}>
        <strong>WebSocket:</strong> {wsConnected ? 'connected' : 'disconnected'}
      </div>
      <div style={{marginTop:10}}>
        <h4>Stream messages</h4>
        <pre style={{whiteSpace:'pre-wrap'}}>{JSON.stringify(wsMessages, null, 2)}</pre>
      </div>

      <hr />
      <pre style={{whiteSpace:'pre-wrap', marginTop:20}}>{result}</pre>
    </div>
  )
}
