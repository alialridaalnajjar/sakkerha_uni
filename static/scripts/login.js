/* ── Password visibility toggle (login page) ───────────── */
document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.querySelector('.toggle-pw');
  if (!toggleBtn) return;

  toggleBtn.addEventListener('click', () => {
    const input = document.getElementById('password');
    input.type = input.type === 'password' ? 'text' : 'password';
  });
});