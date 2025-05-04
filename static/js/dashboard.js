document.addEventListener("DOMContentLoaded", () => {
  const tradesList = document.getElementById("tradesList");

  document.getElementById("seeMsgsBtn").onclick = () =>
    window.location.href = "/dashboard/messages";
  document.getElementById("seePaysBtn").onclick = () =>
    window.location.href = "/dashboard/payments";

  fetch("/api/trades", {
    headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` }
  })
    .then(r => {
      if (!r.ok) throw new Error("Not authorized");
      return r.json();
    })
    .then(list => {
      tradesList.innerHTML = "";
      list.forEach(t => {
        const li = document.createElement("li");
        li.className = "trade-item";

        // use "imgSrc" consistently, or rename to "src"
        const imgSrc = t.thumbnail || "/static/images/default_book_cover.jpg";

        li.innerHTML = `
          <img src="${imgSrc}" class="trade-icon" alt="Cover of ${t.title || t.isbn}"/>
          <div class="trade-text">
            <p class="trade-detail"><strong>${t.title || "No Title"}</strong></p>
            <p class="trade-detail"><strong>ISBN:</strong> ${t.isbn}</p>
            <p class="trade-detail"><strong>Status:</strong> ${t.status}</p>
          </div>
        `;
        tradesList.appendChild(li);
      });
    })
    .catch(console.error);
});