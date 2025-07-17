document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('budget-form');
  form.querySelectorAll('select').forEach(select => {
    select.addEventListener('change', () => {
        console.log('Form submitted');
        form.submit();
    });
  });
});