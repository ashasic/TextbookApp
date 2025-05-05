// called from each book entry’s “Trade” button
window.addTrade = function(isbn) {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Please log in to trade.");
      return window.location.href = "/login";
    }
    fetch("/api/trades", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({ isbn })
    })
    .then(res => {
      if (!res.ok) return res.json().then(j => Promise.reject(j.detail||res.statusText));
      return res.json();
    })
    .then(data => {
      alert("Trade created!");
    })
    .catch(err => {
      console.error(err);
      alert("Error: " + err);
    });
  };