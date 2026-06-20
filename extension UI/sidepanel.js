function showUrl(pageUrl) {
  const el = document.getElementById("url");
  if (el)
    el.textContent = pageUrl ? pageUrl : "undefined (nothing in storage yet)";
  console.log("[PANEL] pageUrl =", pageUrl);
}

// Read whatever the background stored, on panel load
chrome.storage.local.get("pageUrl", ({ pageUrl }) => showUrl(pageUrl));

// Update live whenever the background stores a new URL
// (covers the case where the panel is already open when you click the icon)
chrome.storage.onChanged.addListener((changes, area) => {
  if (area === "local" && changes.pageUrl) {
    showUrl(changes.pageUrl.newValue);
  }
});

chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
  const currentTab = tabs[0];

  chrome.storage.local.set({
    siteLink: currentTab.url,
  });
});
