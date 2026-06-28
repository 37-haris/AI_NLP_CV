// ── Tab switching ─────────────────────────────────────────────────────────────
function showPanel(name) {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));

  document.getElementById('panel-' + name).classList.add('active');
  document.getElementById('tab-' + name).classList.add('active');
}

// ── Login ─────────────────────────────────────────────────────────────────────
async function handleLogin() {
  const username = document.getElementById('login-user').value.trim();
  const password = document.getElementById('login-pass').value;
  const errEl    = document.getElementById('login-err');

  errEl.classList.remove('show');

  if (!username || !password) {
    errEl.textContent = 'Veuillez remplir tous les champs.';
    errEl.classList.add('show');
    return;
  }

  try {
    const res  = await fetch('/auth/login', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ username, password })
    });
    const data = await res.json();

    if (!res.ok) {
      errEl.textContent = data.detail || 'Erreur de connexion.';
      errEl.classList.add('show');
      return;
    }

    // Save user info and redirect to the chat page
    sessionStorage.setItem('user', JSON.stringify(data.user));
    window.location.href = '/chat';

  } catch {
    errEl.textContent = 'Impossible de contacter le serveur.';
    errEl.classList.add('show');
  }
}

// ── Signup ────────────────────────────────────────────────────────────────────
async function handleSignup() {
  const firstname = document.getElementById('su-fname').value.trim();
  const lastname  = document.getElementById('su-lname').value.trim();
  const username  = document.getElementById('su-user').value.trim();
  const password  = document.getElementById('su-pass').value;
  const password2 = document.getElementById('su-pass2').value;
  const errEl     = document.getElementById('su-err');

  errEl.classList.remove('show');

  if (!firstname || !lastname || !username || !password || !password2) {
    errEl.textContent = 'Veuillez remplir tous les champs.';
    errEl.classList.add('show');
    return;
  }

  if (password !== password2) {
    errEl.textContent = 'Les mots de passe ne correspondent pas.';
    errEl.classList.add('show');
    return;
  }

  if (password.length < 6) {
    errEl.textContent = 'Le mot de passe doit contenir au moins 6 caractères.';
    errEl.classList.add('show');
    return;
  }

  try {
    const res  = await fetch('/auth/register', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ firstname, lastname, username, password })
    });
    const data = await res.json();

    if (!res.ok) {
      errEl.textContent = data.detail || "Erreur lors de l'inscription.";
      errEl.classList.add('show');
      return;
    }

    // Show success banner on the login panel and switch to it
    const banner = document.getElementById('login-success');
    banner.textContent = '✓ Compte créé ! Tu peux maintenant te connecter.';
    banner.classList.add('show');
    showPanel('login');

  } catch {
    errEl.textContent = 'Impossible de contacter le serveur.';
    errEl.classList.add('show');
  }
}

// ── Enter key support ─────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('login-pass').addEventListener('keydown', e => {
    if (e.key === 'Enter') handleLogin();
  });
  document.getElementById('su-pass2').addEventListener('keydown', e => {
    if (e.key === 'Enter') handleSignup();
  });
});