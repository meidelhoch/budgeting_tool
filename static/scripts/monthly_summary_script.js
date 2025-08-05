document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('monthly-summary-form');
  form.querySelectorAll('select').forEach(select => {
    select.addEventListener('change', () => {
        console.log('Form submitted');
        form.submit();
    });
  });
});