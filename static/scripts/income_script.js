document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('income-form');
  form.querySelectorAll('select').forEach(select => {
    select.addEventListener('change', () => {
        console.log('Form submitted');
        form.submit();
    });
  });
});