<template>
  <div class="relative">
    <flat-pickr ref="flatpickr" class="form-input pl-9 w-full" :config="config" v-model="date"></flat-pickr>
    <div class="absolute inset-0 right-auto flex items-center pointer-events-none">
      <svg class="fill-current text-gray-400 dark:text-gray-500 ml-3" width="16" height="16" viewBox="0 0 16 16">
        <path d="M5 4a1 1 0 0 0 0 2h6a1 1 0 1 0 0-2H5Z" />
        <path d="M4 0a4 4 0 0 0-4 4v8a4 4 0 0 0 4 4h8a4 4 0 0 0 4-4V4a4 4 0 0 0-4-4H4ZM2 4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V4Z" />
      </svg>
    </div>    
  </div>
</template>

<script>
import flatPickr from 'vue-flatpickr-component'

export default {
  name: 'Datepicker',
  props: ['align', 'modelValue'],
  emits: ['update:modelValue'],
    data (props) {
      return {
        date: props.modelValue,
        config: {
          mode: 'single',
          static: false,
          monthSelectorType: 'dropdown',
          dateFormat: 'M j, Y',
          defaultDate: props.modelValue || new Date(),
          prevArrow: '<svg class="fill-current" width="7" height="11" viewBox="0 0 7 11"><path d="M5.4 10.8l1.4-1.4-4-4 4-4L5.4 0 0 5.4z" /></svg>',
          nextArrow: '<svg class="fill-current" width="7" height="11" viewBox="0 0 7 11"><path d="M1.4 10.8L0 9.4l4-4-4-4L1.4 0l5.4 5.4z" /></svg>',
          onReady: (selectedDates, dateStr, instance) => {
            instance.element.value = dateStr;
            const customClass = (props.align) ? props.align : '';
            instance.calendarContainer.classList.add(`flatpickr-${customClass}`);            
          },
          onChange: (selectedDates, dateStr, instance) => {
            instance.element.value = dateStr;
            this.$emit('update:modelValue', dateStr);
          },
        },                
      }
    },  
  components: {
    flatPickr
  },
  watch: {
    modelValue(newVal) {
      if (newVal !== this.date) {
        this.date = newVal;
        if (this.$refs.flatpickr && this.$refs.flatpickr.fp) {
          this.$refs.flatpickr.fp.setDate(newVal);
        }
      }
    }
  }
}
</script>