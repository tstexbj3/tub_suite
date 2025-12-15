import { useEffect, useRef } from 'react'
import { Html5Qrcode } from 'html5-qrcode'

export default function QRScanner({ onScan }) {
  const qrRef = useRef(null)

  useEffect(() => {
    const scanner = new Html5Qrcode("qr-reader")
    
    scanner.start(
      { facingMode: "environment" },
      { fps: 10, qrbox: 250 },
      (decodedText) => {
        const assetName = extractAssetName(decodedText)
        if (assetName) {
          scanner.stop()
          onScan(assetName)
        }
      }
    )

    return () => {
      scanner.stop().catch(() => {})
    }
  }, [onScan])

  const extractAssetName = (url) => {
    const match = url.match(/asset[=/]([^&\/]+)/)
    return match ? match[1] : url
  }

  return <div id="qr-reader" style={{ width: '100%' }}></div>
}
