import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const pageTitle = ref('NexClaim')

export function usePageTitle() {
  const route = useRoute()

  const setTitle = (title) => {
    pageTitle.value = title
    document.title = `${title} - NexClaim`
  }

  watch(() => route.meta, (meta) => {
    const title = meta?.title || 'NexClaim'
    setTitle(title)
  }, { immediate: true })

  return {
    pageTitle,
    setTitle
  }
}