document.addEventListener("DOMContentLoaded", () => {
  const tradesList = document.getElementById("tradesList");

  // Navigation buttons
  document.getElementById("seeMsgsBtn").onclick = () =>
    (window.location.href = "/dashboard/messages");
  document.getElementById("seePaysBtn").onclick = () =>
    (window.location.href = "/dashboard/payments");

  // Fetch and render trades
  fetch("/api/trades", {
    headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
  })
    .then((r) => {
      if (!r.ok) throw new Error("Not authorized");
      return r.json();
    })
    .then((list) => {
      tradesList.innerHTML = "";
      list.forEach((t) => {
        const li = document.createElement("li");
        li.className = "trade-item";
        li.dataset.id = t.id;

        const imgSrc = t.thumbnail || "/static/images/default_book_cover.jpg";

        li.innerHTML = `
          <img src="${imgSrc}" class="trade-icon" alt="Cover of ${
          t.title || t.isbn
        }"/>
          <div class="trade-text">
            <p class="trade-detail"><strong>${
              t.title || "No Title"
            }</strong></p>
            <p class="trade-detail"><strong>ISBN:</strong> ${t.isbn}</p>
            <p class="trade-detail"><strong>Status:</strong> ${t.status}</p>
          </div>
          <div class="review-actions">
            <button class="small-btn editTradeBtn">Edit</button>
            <button class="small-btn deleteTradeBtn">Delete</button>
            <button class="small-btn messageBtn">Message</button>
          </div>
        `;

        tradesList.appendChild(li);

        // Delete handler
        li.querySelector(".deleteTradeBtn").addEventListener("click", () => {
          if (!confirm("Delete this trade?")) return;
          fetch(`/api/trades/${t.id}`, {
            method: "DELETE",
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          })
            .then((res) => {
              if (!res.ok) throw new Error("Delete failed");
              li.remove();
            })
            .catch((err) => {
              console.error(err);
              alert("Could not delete trade.");
            });
        });

        // Edit handler
        li.querySelector(".editTradeBtn").addEventListener("click", () => {
          const newStatus = prompt("Enter new status:", t.status);
          if (!newStatus) return;
          fetch(`/api/trades/${t.id}`, {
            method: "PUT",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
            body: JSON.stringify({ status: newStatus }),
          })
            .then((res) => {
              if (!res.ok) throw new Error("Update failed");
              li.querySelectorAll(
                ".trade-detail"
              )[2].textContent = `Status: ${newStatus}`;
            })
            .catch((err) => {
              console.error(err);
              alert("Could not update trade.");
            });
        });

        // Message handler
        li.querySelector(".messageBtn").addEventListener("click", () => {
          window.location.href = `/dashboard/messages?peer=${encodeURIComponent(
            t.other_user
          )}`;
        });
      });
    })
    .catch((err) => {
      console.error(err);
      tradesList.textContent = "Failed to load trades.";
    });
});
