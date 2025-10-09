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
  props: {
    align: String,
    modelValue: {
      type: [String, Number, Date, Array],
      default: null
    }
  },
  emits: ['update:modelValue'],
    data (props) {
      return {
        date: this.convertToDisplayFormat(props.modelValue) || null,
        config: {
          mode: 'single',
          static: false,
          dateFormat: 'M j, Y',
          defaultDate: this.convertToDisplayFormat(props.modelValue) || new Date(),
          prevArrow: '<svg class="fill-current" width="7" height="11" viewBox="0 0 7 11"><path d="M5.4 10.8l1.4-1.4-4-4 4-4L5.4 0 0 5.4z" /></svg>',
          nextArrow: '<svg class="fill-current" width="7" height="11" viewBox="0 0 7 11"><path d="M1.4 10.8L0 9.4l4-4-4-4L1.4 0l5.4 5.4z" /></svg>',

          onReady: (selectedDates, dateStr, instance) => {
            instance.element.value = dateStr;
            const customClass = (props.align) ? props.align : '';
            instance.calendarContainer.classList.add(`flatpickr-${customClass}`);
            
            // Convert month to dropdown
            const monthElement = instance.monthElements[0];
            if (monthElement) {
              const currentDate = instance.selectedDates[0] || new Date();
              const currentMonth = currentDate.getMonth();
              const monthSelect = document.createElement('select');
              monthSelect.className = 'form-select text-sm dark:bg-gray-800 dark:border-gray-600 dark:text-gray-100 ml-2 mr-2 flex-0.75';
              
              const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
              months.forEach((month, index) => {
                const option = document.createElement('option');
                option.value = index;
                option.textContent = month;
                if (index === currentMonth) option.selected = true;
                monthSelect.appendChild(option);
              });
              
              monthSelect.addEventListener('change', (e) => {
                const newMonth = parseInt(e.target.value);
                const currentDate = instance.selectedDates[0] || new Date();
                const newDate = new Date(currentDate.getFullYear(), newMonth, currentDate.getDate());
                instance.setDate(newDate);
              });
              
              monthElement.parentNode.replaceChild(monthSelect, monthElement);
              instance.monthElements[0] = monthSelect;
            }
            
            // Convert year input to dropdown
            const yearInput = instance.yearElements[0];
            if (yearInput) {
              const currentDate = instance.selectedDates[0] || new Date();
              const currentYear = currentDate.getFullYear();
              const yearSelect = document.createElement('select');
              yearSelect.className = 'form-select text-sm dark:bg-gray-800 dark:border-gray-600 dark:text-gray-100 flex-1';
              
              // Add years from 1900 to current year + 10
              for (let year = 1900; year <= new Date().getFullYear() + 10; year++) {
                const option = document.createElement('option');
                option.value = year;
                option.textContent = year;
                if (year === currentYear) option.selected = true;
                yearSelect.appendChild(option);
              }
              
              yearSelect.addEventListener('change', (e) => {
                const newYear = parseInt(e.target.value);
                const currentDate = instance.selectedDates[0] || new Date();
                const newDate = new Date(newYear, currentDate.getMonth(), currentDate.getDate());
                instance.setDate(newDate);
              });
              
              yearInput.parentNode.replaceChild(yearSelect, yearInput);
              instance.yearElements[0] = yearSelect;
            }
            
            // Apply flex layout to current month container
            const currentMonthContainer = instance.currentMonthElement?.parentNode;
            if (currentMonthContainer) {
              currentMonthContainer.style.display = 'flex';
              currentMonthContainer.style.gap = '8px';
              currentMonthContainer.style.alignItems = 'center';
              currentMonthContainer.style.width = '100%';
            }
          },
          onChange: (selectedDates, dateStr, instance) => {
            instance.element.value = dateStr;
            // Convert display format back to YYYY-MM-DD for database
            if (selectedDates[0]) {
              const date = selectedDates[0];
              const year = date.getFullYear();
              const month = String(date.getMonth() + 1).padStart(2, '0');
              const day = String(date.getDate()).padStart(2, '0');
              const dbFormat = `${year}-${month}-${day}`;
              this.$emit('update:modelValue', dbFormat);
            }
          },
        },                
      }
    },  
  components: {
    flatPickr
  },
  methods: {
    convertToDisplayFormat(dateStr) {
      if (!dateStr) return null;
      if (typeof dateStr === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
        const [year, month, day] = dateStr.split('-');
        return new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
      }
      if (dateStr instanceof Date) {
        return dateStr;
      }
      return dateStr;
    }
  },
  watch: {
    modelValue(newVal) {
      const displayDate = this.convertToDisplayFormat(newVal);
      if (displayDate !== this.date) {
        this.date = displayDate;
        if (this.$refs.flatpickr && this.$refs.flatpickr.fp) {
          this.$refs.flatpickr.fp.setDate(displayDate);
        }
      }
    }
  }
}
</script>