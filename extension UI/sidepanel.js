function showUrl(pageUrl) {
  const el = document.getElementById("url");

  if (el) {
    el.textContent = pageUrl ?? "undefined (nothing in storage yet)";
  }

  console.log("[PANEL] pageUrl =", pageUrl);
}

// Read URL saved by background.js when panel loads.
chrome.storage.local.get(["pageUrl"], ({ pageUrl }) => {
  showUrl(pageUrl);
});

// Update the panel when background.js saves a new URL.
chrome.storage.onChanged.addListener((changes, area) => {
  if (area === "local" && changes.pageUrl) {
    showUrl(changes.pageUrl.newValue);
  }
});
