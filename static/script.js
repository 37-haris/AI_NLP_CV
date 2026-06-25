// ── DOM refs ──────────────────────────────────────────────────────────────────
const sidebar     = document.getElementById('sidebar');
const toggleBtn   = document.getElementById('toggle-sidebar');
const openBtn     = document.getElementById('open-sidebar');
const messagesEl  = document.getElementById('messages');
const emptyState  = document.getElementById('empty-state');
const msgInput    = document.getElementById('msg-input');
const sendBtn     = document.getElementById('send-btn');
const fileInput   = document.getElementById('file-input');
const uploadBtn   = document.getElementById('upload-btn');
const imgStrip    = document.getElementById('img-strip');
const dragOverlay = document.getElementById('drag-overlay');
const topbarTitle = document.getElementById('topbar-title');
const chatList    = document.getElementById('chat-list');
const newChatBtn  = document.getElementById('new-chat-btn');
const mainEl      = document.getElementById('main');

// ── State ─────────────────────────────────────────────────────────────────────
let pendingImage = null;   // { dataUrl, name, size }
let pendingFile  = null;   // raw File object for FormData
let isGenerating = false;
let chatCounter  = 4;

// ── Sidebar collapse / expand ─────────────────────────────────────────────────
toggleBtn.addEventListener('click', () => {
  sidebar.classList.add('collapsed');
  openBtn.style.display = 'flex';
});
openBtn.addEventListener('click', () => {
  sidebar.classList.remove('collapsed');
  openBtn.style.display = 'none';
});

// ── Textarea auto-resize ──────────────────────────────────────────────────────
msgInput.addEventListener('input', () => {
  msgInput.style.height = 'auto';
  msgInput.style.height = Math.min(msgInput.scrollHeight, 140) + 'px';
  updateSendBtn();
});
msgInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    if (!sendBtn.disabled) send();
  }
});

function updateSendBtn() {
  sendBtn.disabled = isGenerating || (!msgInput.value.trim() && !pendingImage);
}

// ── Image upload (button + file picker) ──────────────────────────────────────
uploadBtn.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) loadImage(fileInput.files[0]);
  fileInput.value = '';
});

// ── Drag-and-drop ─────────────────────────────────────────────────────────────
mainEl.addEventListener('dragover', e => {
  e.preventDefault();
  dragOverlay.classList.add('active');
});
mainEl.addEventListener('dragleave', e => {
  if (!mainEl.contains(e.relatedTarget)) dragOverlay.classList.remove('active');
});
mainEl.addEventListener('drop', e => {
  e.preventDefault();
  dragOverlay.classList.remove('active');
  const f = e.dataTransfer.files[0];
  if (f && f.type.startsWith('image/')) loadImage(f);
});

function loadImage(file) {
  pendingFile = file;
  const reader = new FileReader();
  reader.onload = ev => {
    pendingImage = { dataUrl: ev.target.result, name: file.name, size: formatSize(file.size) };
    showImageStrip();
    updateSendBtn();
  };
  reader.readAsDataURL(file);
}

function formatSize(b) {
  if (b < 1024)        return b + ' B';
  if (b < 1024 * 1024) return (b / 1024).toFixed(1) + ' KB';
  return (b / (1024 * 1024)).toFixed(1) + ' MB';
}

function showImageStrip() {
  imgStrip.innerHTML = '';

  const wrap = document.createElement('div');
  wrap.className = 'img-thumb-wrap';

  const img = document.createElement('img');
  img.src = pendingImage.dataUrl;
  img.className = 'img-thumb';
  img.alt = pendingImage.name;

  const rm = document.createElement('button');
  rm.className = 'img-remove';
  rm.title = 'Remove';
  rm.innerHTML = '<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';
  rm.addEventListener('click', clearImage);

  wrap.appendChild(img);
  wrap.appendChild(rm);

  const meta = document.createElement('div');
  meta.className = 'img-meta';
  meta.innerHTML = '<span class="img-filename">' + pendingImage.name + '</span>' +
                   '<span class="img-filesize">'  + pendingImage.size + '</span>';

  imgStrip.appendChild(wrap);
  imgStrip.appendChild(meta);
  imgStrip.classList.add('has-image');
  imgStrip.style.padding = '10px 14px 0';
}

function clearImage() {
  pendingImage = null;
  pendingFile  = null;
  imgStrip.innerHTML = '';
  imgStrip.classList.remove('has-image');
  updateSendBtn();
}

// ── Send ──────────────────────────────────────────────────────────────────────
sendBtn.addEventListener('click', send);

function send() {
  if (isGenerating) return;
  const text = msgInput.value.trim();
  if (!text && !pendingImage) return;

  hideEmptyState();

  const img     = pendingImage;
  const file    = pendingFile;
  const message = text;

  clearImage();
  msgInput.value = '';
  msgInput.style.height = 'auto';
  updateSendBtn();

  appendUserMessage(message, img);

  // Update sidebar title on first message
  if (topbarTitle.textContent === 'New conversation') {
    const title = message || 'Image analysis';
    topbarTitle.textContent = title;
    const active = chatList.querySelector('.chat-item.active');
    if (active) active.querySelector('span').textContent = title;
  }

  callBackend(file, message);
}

function hideEmptyState() {
  if (emptyState) emptyState.style.display = 'none';
}

// ── Append user bubble ────────────────────────────────────────────────────────
function appendUserMessage(text, img) {
  const row    = document.createElement('div'); row.className = 'message-row user';
  const av     = document.createElement('div'); av.className  = 'msg-avatar user'; av.textContent = 'U';
  const body   = document.createElement('div'); body.className = 'msg-body';
  const name   = document.createElement('div'); name.className = 'msg-name'; name.textContent = 'You';
  const bubble = document.createElement('div'); bubble.className = 'bubble user clearfix';

  if (img) {
    const imgEl = document.createElement('img');
    imgEl.src = img.dataUrl;
    imgEl.className = 'img-preview';
    imgEl.alt = img.name;
    bubble.appendChild(imgEl);
  }
  if (text) {
    const span = document.createElement('span');
    span.className = 'bubble-text';
    span.textContent = text;
    bubble.appendChild(span);
  }

  body.appendChild(name);
  body.appendChild(bubble);
  row.appendChild(body);
  row.appendChild(av);
  messagesEl.appendChild(row);
  scrollBottom();
}

// ── Call /predict endpoint ────────────────────────────────────────────────────
async function callBackend(imageFile, userText) {
  isGenerating = true;
  updateSendBtn();

  // Build AI message row with typing dots
  const row    = document.createElement('div'); row.className = 'message-row';
  const av     = document.createElement('div'); av.className  = 'msg-avatar ai';
  av.innerHTML = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#9b9894" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>';

  const body   = document.createElement('div'); body.className  = 'msg-body';
  const name   = document.createElement('div'); name.className  = 'msg-name'; name.textContent = 'VisionChat';
  const bubble = document.createElement('div'); bubble.className = 'bubble ai';
  const dots   = document.createElement('div'); dots.className   = 'typing-dots';
  dots.innerHTML = '<span></span><span></span><span></span>';

  bubble.appendChild(dots);
  body.appendChild(name);
  body.appendChild(bubble);
  row.appendChild(av);
  row.appendChild(body);
  messagesEl.appendChild(row);
  scrollBottom();

  try {
    // Guard: must have an image
    if (!imageFile) {
      throw new Error('Please upload an image before sending.');
    }

    const formData = new FormData();
    formData.append('image',     imageFile);
    formData.append('user_text', userText || '');

    const response = await fetch('/predict', { method: 'POST', body: formData });
    const data     = await response.json();

    // Handle server-side error returned as JSON
    if (!response.ok || data.error) {
      throw new Error(data.error || 'Server error ' + response.status);
    }

    const enText = data.en || 'No description returned.';
    const frText = data.fr || 'Aucune traduction retournée.';

    dots.remove();
    bubble.style.width = '100%';
    renderLangCards(bubble, enText, frText);

  } catch (err) {
    dots.remove();
    const errEl = document.createElement('span');
    errEl.className   = 'bubble-text';
    errEl.style.color = '#fc8181';
    errEl.textContent = '⚠ ' + (err.message || 'Could not reach the server.');
    bubble.appendChild(errEl);
    isGenerating = false;
    updateSendBtn();
  }
}

// ── Language cards ────────────────────────────────────────────────────────────
function makeLangCard(lang) {
  const card  = document.createElement('div'); card.className  = 'lang-card ' + lang;
  const label = document.createElement('div'); label.className = 'lang-label';

  if (lang === 'en') {
    label.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg> English';
  } else {
    label.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 8l6 6"/><path d="M4 14l6-6 2-3"/><path d="M2 5h12"/><path d="M7 2h1"/><path d="M22 22l-5-10-5 10"/><path d="M14 18h6"/></svg> Français';
  }

  const spinner = document.createElement('div');
  spinner.className = 'spinner';
  spinner.innerHTML = '<span></span><span></span><span></span>';

  const textEl = document.createElement('span');
  textEl.className = 'lang-card-text';

  card.appendChild(label);
  card.appendChild(spinner);
  card.appendChild(textEl);
  return { card, spinner, textEl };
}

function typeIntoCard(textEl, spinnerEl, text, onDone) {
  spinnerEl.remove();
  const cursor = document.createElement('span');
  cursor.className = 'cursor';
  textEl.appendChild(cursor);
  let i = 0;
  const step = () => {
    if (i < text.length) {
      cursor.insertAdjacentText('beforebegin', text[i++]);
      scrollBottom();
      setTimeout(step, 14);
    } else {
      cursor.remove();
      if (onDone) onDone();
    }
  };
  step();
}

function renderLangCards(bubble, enText, frText) {
  const cards = document.createElement('div');
  cards.className = 'lang-cards';

  const en = makeLangCard('en');
  const fr = makeLangCard('fr');
  cards.appendChild(en.card);
  cards.appendChild(fr.card);
  bubble.appendChild(cards);
  scrollBottom();

  // Type English first, then French
  typeIntoCard(en.textEl, en.spinner, enText, function () {
    typeIntoCard(fr.textEl, fr.spinner, frText, function () {
      isGenerating = false;
      updateSendBtn();
    });
  });
}

function scrollBottom() { messagesEl.scrollTop = messagesEl.scrollHeight; }

// ── New chat ──────────────────────────────────────────────────────────────────
newChatBtn.addEventListener('click', () => {
  messagesEl.innerHTML = '';
  emptyState.style.display = '';
  messagesEl.appendChild(emptyState);
  topbarTitle.textContent = 'New conversation';
  clearImage();
  msgInput.value = '';
  msgInput.style.height = 'auto';
  updateSendBtn();

  chatList.querySelectorAll('.chat-item').forEach(el => el.classList.remove('active'));

  const item = document.createElement('div');
  item.className = 'chat-item active';
  item.setAttribute('data-id', chatCounter++);
  item.innerHTML = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg><span style="overflow:hidden;text-overflow:ellipsis;">New conversation</span>';
  chatList.insertBefore(item, chatList.firstChild);
  item.addEventListener('click', () => {
    chatList.querySelectorAll('.chat-item').forEach(e => e.classList.remove('active'));
    item.classList.add('active');
  });
});

// ── Chat list click ───────────────────────────────────────────────────────────
chatList.addEventListener('click', e => {
  const item = e.target.closest('.chat-item');
  if (!item) return;
  chatList.querySelectorAll('.chat-item').forEach(el => el.classList.remove('active'));
  item.classList.add('active');
});

// ── Init ──────────────────────────────────────────────────────────────────────
updateSendBtn();