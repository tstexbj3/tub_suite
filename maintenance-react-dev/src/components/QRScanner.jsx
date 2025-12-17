import { useEffect, useRef, useState } from 'react'
import { Html5Qrcode } from 'html5-qrcode'

export default function QRScanner({ onScan }) {
  const [scanning, setScanning] = useState(false)
  const [error, setError] = useState(null)
  const [status, setStatus] = useState('')
  const scannerRef = useRef(null)
  const hasScannedRef = useRef(false)

  // Try different scanner configurations in order of preference
  const startScanning = async () => {
    setError(null)
    setStatus('Initializing camera...')
    hasScannedRef.current = false

    const onScanSuccess = async (decodedText, scanner) => {
      if (hasScannedRef.current) return
      hasScannedRef.current = true

      const assetName = extractAssetName(decodedText)
      if (assetName) {
        setStatus('QR Code detected!')
        try {
          await scanner.stop()
        } catch (e) {
          // Ignore stop errors
        }
        setScanning(false)
        scannerRef.current = null
        setTimeout(() => onScan(assetName), 100)
      }
    }

    // Configuration attempts in order of preference
    const configs = [
      // Config 1: Simple and reliable
      {
        scannerOpts: {},
        config: { fps: 10, qrbox: { width: 250, height: 250 } }
      },
      // Config 2: With experimental features
      {
        scannerOpts: {
          experimentalFeatures: { useBarCodeDetectorIfSupported: true }
        },
        config: { fps: 10, qrbox: { width: 250, height: 250 } }
      },
      // Config 3: Higher FPS
      {
        scannerOpts: {},
        config: { fps: 15, qrbox: 250 }
      }
    ]

    for (let i = 0; i < configs.length; i++) {
      try {
        const { scannerOpts, config } = configs[i]
        const scanner = new Html5Qrcode("qr-reader", scannerOpts)
        scannerRef.current = scanner

        await scanner.start(
          { facingMode: "environment" },
          config,
          (decodedText) => onScanSuccess(decodedText, scanner)
        )

        setScanning(true)
        setStatus('Scanning...')
        return // Success - exit the loop
      } catch (err) {
        console.warn(`Scanner config ${i + 1} failed:`, err.message)
        // Clean up failed scanner
        if (scannerRef.current) {
          try {
            await scannerRef.current.stop()
          } catch (e) {
            // Ignore
          }
          scannerRef.current = null
        }
      }
    }

    // All configs failed
    setError('Camera not available. Please use Search instead.')
    setStatus('')
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
    // Pattern priority (most specific first):
    // 1. /maintenance/checklist/{name} - qr_foundry redirect URL
    // 2. /checklist/{name} - direct checklist URL
    // 3. ?asset={name} or /asset/{name} - legacy patterns
    // 4. /app/asset/{name} - Frappe desk URL
    // 5. Plain text - treat as asset name directly

    let match = url.match(/\/(?:maintenance\/)?checklist\/([^?\/]+)/)
    if (match) return decodeURIComponent(match[1])

    match = url.match(/asset[=/]([^&\/]+)/)
    if (match) return decodeURIComponent(match[1])

    match = url.match(/\/app\/asset\/([^?\/]+)/)
    if (match) return decodeURIComponent(match[1])

    return url
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
