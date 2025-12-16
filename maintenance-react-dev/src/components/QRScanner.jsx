import { useEffect, useRef, useState } from 'react'
import { Html5Qrcode } from 'html5-qrcode'

export default function QRScanner({ onScan }) {
  const [scanning, setScanning] = useState(false)
  const [error, setError] = useState(null)
  const scannerRef = useRef(null)

  const startScanning = async () => {
    try {
      setError(null)
      const scanner = new Html5Qrcode("qr-reader")
      scannerRef.current = scanner
      
      await scanner.start(
        { facingMode: "environment" },
        { fps: 10, qrbox: 250 },
        (decodedText) => {
          const assetName = extractAssetName(decodedText)
          if (assetName) {
            scanner.stop()
            setScanning(false)
            onScan(assetName)
          }
        }
      )
      setScanning(true)
    } catch (err) {
      setError('Camera not available. Please use Search instead.')
      console.error('QR Scanner error:', err)
    }
  }

  const stopScanning = () => {
    if (scannerRef.current) {
      scannerRef.current.stop()
      setScanning(false)
    }
  }

  useEffect(() => {
    return () => {
      if (scannerRef.current) {
        scannerRef.current.stop().catch(() => {})
      }
    }
  }, [])

  const extractAssetName = (url) => {
    const match = url.match(/asset[=/]([^&\/]+)/)
    return match ? match[1] : url
  }

  return (
    <div>
      {!scanning && !error && (
        <button className="primary" onClick={startScanning} style={{width: '100%'}}>
          Start QR Scanner
        </button>
      )}
      
      {error && (
        <div style={{color: 'red', padding: '1rem'}}>
          {error}
        </div>
      )}
      
      {scanning && (
        <>
          <div id="qr-reader" style={{ width: '100%' }}></div>
          <button onClick={stopScanning} style={{marginTop: '1rem', width: '100%'}}>
            Stop Scanner
          </button>
        </>
      )}
    </div>
  )
}
