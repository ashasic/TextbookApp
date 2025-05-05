document.addEventListener("DOMContentLoaded", () => {
    const usersList    = document.getElementById("usersList");
    const messagesList = document.getElementById("messagesList");
    const chatWith     = document.getElementById("chatWith");
    const newMsgInput  = document.getElementById("newMessage");
    const sendBtn      = document.getElementById("sendBtn");
  
    let selectedPeer = null;
  
    // helper to auth‑header
    const authHeaders = () => ({
      "Authorization": `Bearer ${localStorage.getItem("token")}`,
      "Content-Type":  "application/json"
    });
  
    // 1) Load all other users
    fetch("/api/users", { headers: authHeaders() })
      .then(r => r.json())
      .then(users => {
        usersList.innerHTML = "";
        users.forEach(u => {
          const li = document.createElement("li");
          li.textContent = u;
          li.className = "trade-item";
          li.style.cursor = "pointer";
          li.onclick = () => selectPeer(u);
          usersList.appendChild(li);
        });
      })
      .catch(console.error);
  
    // 2) when you choose somebody
    function selectPeer(user) {
      selectedPeer = user;
      chatWith.textContent = user;
      messagesList.innerHTML = "";
      fetch(`/api/messages/${user}`, { headers: authHeaders() })
        .then(r => r.json())
        .then(msgs => {
          msgs.forEach(m => {
            const d = document.createElement("div");
            d.className = m.from_user === selectedPeer
              ? "trade-text" 
              : "trade-text";
            d.style.alignSelf = m.from_user === selectedPeer ? "flex-start" : "flex-end";
            d.style.background = m.from_user === selectedPeer ? "#222" : "var(--uiowa-gold)";
            d.style.color = m.from_user === selectedPeer ? "var(--uiowa-white)" : "var(--uiowa-black)";
            d.style.padding = "0.5rem";
            d.style.borderRadius = "8px";
            d.style.margin = "0.25rem";
            d.textContent = m.content;
            messagesList.appendChild(d);
          });
          // scroll to bottom
          messagesList.scrollTop = messagesList.scrollHeight;
        })
        .catch(console.error);
    }
  
    // 3) Send button
    sendBtn.onclick = () => {
      if (!selectedPeer || !newMsgInput.value.trim()) return;
      fetch("/api/messages", {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({
          to_user: selectedPeer,
          content: newMsgInput.value.trim()
        })
      })
      .then(r => {
        if (!r.ok) throw new Error("Send failed");
        return r.json();
      })
      .then(() => {
        newMsgInput.value = "";
        selectPeer(selectedPeer);   // reload convo
      })
      .catch(console.error);
    };
  });  