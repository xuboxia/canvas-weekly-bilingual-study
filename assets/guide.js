(() => {
  const buttons = [...document.querySelectorAll('button[data-language]')];
  const lessons = [...document.querySelectorAll('.lesson')];
  const search = document.querySelector('#search');
  function filter() {
    const term = search.value.trim().toLocaleLowerCase();
    let visible = 0;
    lessons.forEach(section => {
      const text = [...section.querySelectorAll('p, h2, h3, code, td, th, figcaption')]
        .filter(el => !el.closest('.lang-zh, .lang-en') || getComputedStyle(el.closest('.lang-zh, .lang-en')).display !== 'none')
        .map(el => el.textContent).join(' ').toLocaleLowerCase();
      section.hidden = Boolean(term) && !text.includes(term);
      if (!section.hidden) visible++;
    });
    document.querySelector('#search-empty').hidden = visible > 0;
  }
  buttons.forEach(button => button.addEventListener('click', () => {
    document.body.dataset.language = button.dataset.language;
    document.documentElement.lang = button.dataset.language === 'zh' ? 'zh-CN' : 'en';
    buttons.forEach(b => b.setAttribute('aria-pressed', String(b === button)));
    filter();
  }));
  search.addEventListener('input', filter);
  document.querySelectorAll('nav a').forEach(link => link.addEventListener('click', () => {
    search.value = ''; filter();
  }));
  let closed = [];
  window.addEventListener('beforeprint', () => {
    closed = [...document.querySelectorAll('details:not([open])')];
    closed.forEach(item => item.open = true);
  });
  window.addEventListener('afterprint', () => { closed.forEach(item => item.open = false); });
  document.querySelector('#print').addEventListener('click', () => window.print());
})();
