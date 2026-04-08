document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.btn-delete').forEach((button) => {
    button.addEventListener('click', (event) => {
      const confirmed = window.confirm('Tem certeza que deseja excluir este registro?');
      if (!confirmed) {
        event.preventDefault();
      }
    });
  });

  document.querySelectorAll('form[action*="/toggle"]').forEach((form) => {
    form.addEventListener('submit', (event) => {
      const button = form.querySelector('button');
      const actionLabel = button ? button.textContent.trim().toLowerCase() : 'alterar';
      const confirmed = window.confirm(`Deseja realmente ${actionLabel} este usuário?`);
      if (!confirmed) {
        event.preventDefault();
      }
    });
  });
});
