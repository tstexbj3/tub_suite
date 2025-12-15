export const addTimestampToPhoto = (file) => {
  return new Promise((resolve) => {
    const img = new Image()
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')

    img.onload = () => {
      canvas.width = img.width
      canvas.height = img.height

      // Draw photo
      ctx.drawImage(img, 0, 0)

      // Add timestamp
      const timestamp = new Date().toLocaleString('th-TH', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })

      ctx.font = 'bold 24px Arial'
      ctx.fillStyle = 'rgba(0, 0, 0, 0.7)'
      ctx.fillRect(canvas.width - 220, canvas.height - 40, 210, 35)
      ctx.fillStyle = 'white'
      ctx.fillText(timestamp, canvas.width - 215, canvas.height - 15)

      canvas.toBlob((blob) => {
        resolve(new File([blob], file.name, { type: 'image/jpeg' }))
      }, 'image/jpeg', 0.95)
    }

    img.src = URL.createObjectURL(file)
  })
}

export const uploadPhoto = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('is_private', 0)

  const response = await fetch('/api/method/upload_file', {
    method: 'POST',
    headers: {
      'X-Frappe-CSRF-Token': window.csrf_token || ''
    },
    body: formData
  })

  const data = await response.json()
  return data.message.file_url
}
