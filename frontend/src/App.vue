<template>
  <router-view />
  <AlertContainer />
</template>

<script>
import './charts/ChartjsConfig';
import AlertContainer from './components/AlertContainer.vue'
import { usePageTitle } from './composables/usePageTitle'

export default {
  components: {
    AlertContainer
  },
  setup() {
    usePageTitle()
  }
}
</script>

