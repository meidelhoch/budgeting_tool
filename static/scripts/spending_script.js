document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('spending-form');
  form.querySelectorAll('select').forEach(select => {
    select.addEventListener('change', () => {
        console.log('Form submitted');
        form.submit();
    });
  });
});