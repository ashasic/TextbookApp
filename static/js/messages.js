document.addEventListener("DOMContentLoaded", () => {
  const contactsList = document.getElementById("contactsList");
  const chatList = document.getElementById("chatList");
  const chatWithName = document.getElementById("chatWithName");
  const chatWithAvatar = document.getElementById("chatWithAvatar");
  const payNowBtn = document.getElementById("payNowBtn");
  const msgInput = document.getElementById("messageInput");
  const sendMsgBtn = document.getElementById("sendMsgBtn");

  let selectedUser = null;

  // load list of all users (contacts)
  fetch("/api/users", {
    headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
  })
    .then((r) => {
      if (!r.ok) throw new Error("Not authorized");
      return r.json();
    })
    .then((usernames) => {
      contactsList.innerHTML = "";
      usernames.forEach((username) => {
        const li = document.createElement("li");
        li.className = "contact-item";
        li.innerHTML = `
          <img src="/static/images/default_profile_picture.jpg"
               class="profile-icon"
               alt="Avatar of ${username}" />
          <button class="contact-btn" data-user="${username}">
            ${username}
          </button>
        `;
        contactsList.appendChild(li);
      });
    })
    .catch(console.error);

  // click handler to open a conversation
  contactsList.addEventListener("click", (e) => {
    const li = e.target.closest(".contact-item");
    if (!li) return;

    // clear previous highlight
    document
      .querySelectorAll(".contact-item")
      .forEach((item) => item.classList.remove("active"));
    // highlight this one
    li.classList.add("active");

    // figure out who we clicked
    const btn = li.querySelector(".contact-btn");
    selectedUser = btn.dataset.user;
    chatWithName.textContent = selectedUser;
    payNowBtn.style.display = "inline-block";
    sendMsgBtn.disabled = false;

    loadChat();
  });

  function loadChat() {
    fetch(`/api/messages/${selectedUser}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
    })
      .then((r) => (r.ok ? r.json() : Promise.reject("Not authorized")))
      .then((msgs) => {
        chatList.innerHTML = "";
        msgs.forEach((m) => {
          const bubble = document.createElement("div");
          // if from me, it's "sent", else "received"
          bubble.className =
            m.from_user === selectedUser ? "bubble received" : "bubble sent";
          bubble.textContent = m.content;
          chatList.appendChild(bubble);
        });
        chatList.scrollTop = chatList.scrollHeight;
      })
      .catch(console.error);
  }

  sendMsgBtn.addEventListener("click", () => {
    const content = msgInput.value.trim();
    if (!content || !selectedUser) return;
    fetch("/api/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
      body: JSON.stringify({ to_user: selectedUser, content }),
    })
      .then((r) => {
        if (!r.ok) throw new Error("Send failed");
        msgInput.value = "";
        loadChat();
      })
      .catch(console.error);
  });
  payNowBtn.addEventListener("click", () => {
    window.location.href = `/dashboard/payments?peer=${encodeURIComponent(
      selectedUser
    )}`;
  });
});
