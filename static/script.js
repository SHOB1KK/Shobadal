const chatBox = document.getElementById('chat-box');
const input = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const voiceBtn = document.getElementById('voice-btn');

let voiceEnabled = true;

sendBtn.addEventListener('click', sendMessage);
input.addEventListener('keydown', e => {
  if (e.key === 'Enter') sendMessage();
});

voiceBtn.addEventListener('click', () => {
  voiceEnabled = !voiceEnabled;
  voiceBtn.textContent = voiceEnabled ? "🔊 Голос: Вкл" : "🔇 Голос: Выкл";
});

function appendMessage(role, text) {
  const div = document.createElement('div');
  div.className = `message ${role}`;
  chatBox.appendChild(div);
  let i = 0;
  const interval = setInterval(() => {
    div.textContent += text.charAt(i);
    i++;
    if (i >= text.length) clearInterval(interval);
    chatBox.scrollTop = chatBox.scrollHeight;
  }, 20);
}

async function sendMessage() {
  const text = input.value.trim();
  if (!text) return;
  appendMessage("user", text);
  input.value = "";

  const res = await fetch('/ask', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ prompt: text, voice: voiceEnabled })
  });
  const data = await res.json();
  appendMessage("bot", data.response);
}
