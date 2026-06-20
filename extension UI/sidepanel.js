const urlElement = document.getElementById("url"); //get elem from sidepanel.html

function updateUrlElement() {
  chrome.storage.local.get(["pageUrl"], (res) => {
    const pageUrl = res.pageUrl ?? "undefined (nothing in storage yet)";

    urlElement.textContent = pageUrl;
    console.log("[PANEL] pageUrl =", pageUrl);
  });
}

updateUrlElement();

// Update the panel when background.js saves a new URL.
chrome.storage.onChanged.addListener((changes, area) => {
  if (area === "local" && changes.pageUrl) {
    showUrl(changes.pageUrl.newValue);
  }
});
