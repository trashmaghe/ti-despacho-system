document.addEventListener('DOMContentLoaded', () => {
  const deleteButtons = document.querySelectorAll('.btn-delete');
  deleteButtons.forEach((button) => {
    button.addEventListener('click', (event) => {
      const confirmed = window.confirm('Tem certeza que deseja excluir este registro?');
      if (!confirmed) {
        event.preventDefault();
      }
    });
  });
});
