document.addEventListener('DOMContentLoaded', () => {
  const root = document.documentElement;
  const presets = window.APP_THEME_PRESETS || [];
  const presetMap = new Map(presets.map((preset) => [preset.id, preset]));
  const defaultPreset = presetMap.get(window.DEFAULT_THEME_ID) || presets[0];
  const themePanel = document.querySelector('[data-theme-panel]');
  const themeToggleButtons = document.querySelectorAll('[data-theme-toggle]');
  const modeButtons = document.querySelectorAll('[data-theme-mode]');
  const presetButtons = document.querySelectorAll('[data-theme-id]');
  const modeLabel = document.querySelector('[data-current-mode-label]');

  const storage = {
    theme: 'controle-ti:theme',
    byMode: 'controle-ti:theme-by-mode',
  };

  const getPreset = (themeId) => presetMap.get(themeId) || defaultPreset;

  const readModeMemory = () => {
    try {
      return JSON.parse(localStorage.getItem(storage.byMode) || '{}');
    } catch (error) {
      return {};
    }
  };

  const writeModeMemory = (data) => {
    localStorage.setItem(storage.byMode, JSON.stringify(data));
  };

  const syncThemeUi = () => {
    const activePreset = getPreset(root.dataset.theme);
    const currentMode = activePreset.mode;

    if (modeLabel) {
      modeLabel.textContent = currentMode === 'dark' ? 'Modo escuro' : 'Modo claro';
    }

    modeButtons.forEach((button) => {
      button.classList.toggle('is-active', button.dataset.themeMode === currentMode);
      button.setAttribute('aria-pressed', String(button.dataset.themeMode === currentMode));
    });

    presetButtons.forEach((button) => {
      button.classList.toggle('is-active', button.dataset.themeId === activePreset.id);
      button.setAttribute('aria-pressed', String(button.dataset.themeId === activePreset.id));
    });
  };

  const applyTheme = (themeId) => {
    const preset = getPreset(themeId);
    const memory = readModeMemory();

    root.dataset.theme = preset.id;
    root.dataset.colorMode = preset.mode;
    localStorage.setItem(storage.theme, preset.id);
    memory[preset.mode] = preset.id;
    writeModeMemory(memory);
    syncThemeUi();
  };

  themeToggleButtons.forEach((button) => {
    button.addEventListener('click', () => {
      const opened = themePanel?.classList.toggle('is-open');
      button.setAttribute('aria-expanded', String(Boolean(opened)));
    });
  });

  modeButtons.forEach((button) => {
    button.addEventListener('click', () => {
      const mode = button.dataset.themeMode;
      const memory = readModeMemory();
      const targetPreset = memory[mode] || presets.find((preset) => preset.mode === mode)?.id || defaultPreset.id;
      applyTheme(targetPreset);
    });
  });

  presetButtons.forEach((button) => {
    button.addEventListener('click', () => {
      applyTheme(button.dataset.themeId);
    });
  });

  document.addEventListener('click', (event) => {
    if (!themePanel) return;
    const clickedToggle = event.target.closest('[data-theme-toggle]');
    const insidePanel = event.target.closest('[data-theme-panel]');
    if (!clickedToggle && !insidePanel) {
      themePanel.classList.remove('is-open');
      themeToggleButtons.forEach((button) => button.setAttribute('aria-expanded', 'false'));
    }
  });

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

  syncThemeUi();
});
