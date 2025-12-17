import { useEffect, useRef, useState } from 'react'
import { Html5Qrcode } from 'html5-qrcode'

export default function QRScanner({ onScan }) {
  const [scanning, setScanning] = useState(false)
  const [error, setError] = useState(null)
  const [status, setStatus] = useState('')
  const scannerRef = useRef(null)
  const hasScannedRef = useRef(false)

  const startScanning = async () => {
    try {
      setError(null)
      setStatus('Initializing camera...')
      hasScannedRef.current = false

      const scanner = new Html5Qrcode("qr-reader", {
        verbose: false,
        // Use experimental features for better detection
        experimentalFeatures: {
          useBarCodeDetectorIfSupported: true  // Use native BarcodeDetector API if available (faster!)
        }
      })
      scannerRef.current = scanner

      // Try to get high-resolution camera for better scanning
      const config = {
        fps: 15,
        qrbox: 250,
        // Request higher resolution if available
        videoConstraints: {
          facingMode: "environment",
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      }

      await scanner.start(
        { facingMode: "environment" },
        config,
        async (decodedText) => {
          // Prevent multiple scans
          if (hasScannedRef.current) return
          hasScannedRef.current = true

          const assetName = extractAssetName(decodedText)
          if (assetName) {
            setStatus('QR Code detected!')

            // Stop scanner first, then navigate
            try {
              await scanner.stop()
            } catch (e) {
              console.log('Scanner stop error (ignored):', e)
            }
            setScanning(false)
            scannerRef.current = null

            // Small delay to ensure cleanup before navigation
            setTimeout(() => {
              onScan(assetName)
            }, 100)
          }
        }
      )
      setScanning(true)
      setStatus('Scanning...')
    } catch (err) {
      setError('Camera not available. Please use Search instead.')
      setStatus('')
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
    <div className="qr-scanner-container">
      {!scanning && !error && (
        <button className="primary" onClick={startScanning} style={{width: '100%'}}>
          📷 Start QR Scanner
        </button>
      )}

      {error && (
        <div style={{color: '#ff6b6b', padding: '1rem', textAlign: 'center'}}>
          {error}
        </div>
      )}

      {/* Scanner viewport with overlay */}
      <div className={`scanner-viewport ${scanning ? 'active' : ''}`}>
        <div id="qr-reader"></div>

        {/* Scanner overlay */}
        {scanning && (
          <div className="scanner-overlay">
            {/* Corner markers */}
            <div className="corner top-left"></div>
            <div className="corner top-right"></div>
            <div className="corner bottom-left"></div>
            <div className="corner bottom-right"></div>

            {/* Scanning line */}
            <div className="scan-line"></div>

            {/* Scan area hint */}
            <div className="scan-hint">{status || 'Position QR code within frame'}</div>
          </div>
        )}
      </div>

      {scanning && (
        <button onClick={stopScanning} className="stop-scanner-btn">
          ✕ Stop Scanner
        </button>
      )}
    </div>
  )
}
