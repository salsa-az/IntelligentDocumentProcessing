import { ref, reactive } from 'vue'

const alerts = ref([])
let alertId = 0

export function useAlert() {
  const showAlert = (type, title, message, options = {}) => {
    const alert = {
      id: ++alertId,
      type,
      title,
      message,
      duration: options.duration || 5000,
      persistent: options.persistent || false
    }
    
    alerts.value.push(alert)
    
    if (!alert.persistent && alert.duration > 0) {
      setTimeout(() => {
        removeAlert(alert.id)
      }, alert.duration)
    }
    
    return alert.id
  }

  const removeAlert = (id) => {
    const index = alerts.value.findIndex(alert => alert.id === id)
    if (index > -1) {
      alerts.value.splice(index, 1)
    }
  }

  const clearAllAlerts = () => {
    alerts.value = []
  }

  // Convenience methods
  const showSuccess = (title, message, options) => showAlert('success', title, message, options)
  const showError = (title, message, options) => showAlert('error', title, message, options)
  const showWarning = (title, message, options) => showAlert('warning', title, message, options)
  const showInfo = (title, message, options) => showAlert('info', title, message, options)

  return {
    alerts,
    showAlert,
    removeAlert,
    clearAllAlerts,
    showSuccess,
    showError,
    showWarning,
    showInfo
  }
}