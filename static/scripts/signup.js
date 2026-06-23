/* ── Signup page: password visibility + live match check ── */
document.addEventListener('DOMContentLoaded', () => {

  // Password visibility toggles (handles both password + confirm fields)
  document.querySelectorAll('.toggle-pw').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.dataset.target || 'password';
      const input    = document.getElementById(targetId);
      input.type = input.type === 'password' ? 'text' : 'password';
    });
  });

  // Live password-match indicator
  const passwordInput = document.getElementById('password');
  const confirmInput  = document.getElementById('confirm');
  const matchMsg      = document.getElementById('pw-match');

  if (!passwordInput || !confirmInput || !matchMsg) return;

  function checkMatch() {
    if (!confirmInput.value) {
      matchMsg.style.display = 'none';
      return;
    }
    matchMsg.style.display = 'block';
    if (passwordInput.value === confirmInput.value) {
      matchMsg.textContent = '✓ Passwords match';
      matchMsg.className   = 'pw-match-msg ok';
    } else {
      matchMsg.textContent = '✗ Passwords do not match';
      matchMsg.className   = 'pw-match-msg err';
    }
  }

  passwordInput.addEventListener('input', checkMatch);
  confirmInput.addEventListener('input', checkMatch);
});