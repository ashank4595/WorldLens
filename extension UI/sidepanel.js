/*            *
 * DISPLAY URL*
 *            */

//get url elem from sidepanel.html, <p id="url">Loading URL…</p>
const urlElement = document.getElementById("url");

// gets pageURL from local storage (saved there in background.js)
// sets urlElement to pageURL
function updateUrlElement() {
  chrome.storage.local.get(["pageUrl"], (res) => {
    const pageUrl = res.pageUrl ?? "undefined (nothing in storage yet)";

    urlElement.textContent = pageUrl;
    console.log("[PANEL] pageUrl =", pageUrl);
  });
}

updateUrlElement();

// Update the panel when background.js saves a new pageURL
// ie. new website and extension clicked again, this ensures url displayed updates
chrome.storage.onChanged.addListener((changes, area) => {
  if (area === "local" && changes.pageUrl) {
    const pageUrl = changes.pageUrl.newValue;

    urlElement.textContent = pageUrl;
    console.log("[PANEL] pageUrl =", pageUrl);
  }
});

/*              *
 * DISPLAY TITLE*
 *              */

const titleElement = document.getElementById("title"); //get elem from sidepanel.html

function updateTitleElement() {
  chrome.storage.local.get(["pageTitle"], (res) => {
    const pageTitle = res.pageTitle ?? "undefined (nothing in storage yet)";

    titleElement.textContent = pageTitle;
    console.log("[PANEL] pageTitle =", pageTitle);
  });
}

updateTitleElement();

// Update the panel when background.js saves a new pageTitle
chrome.storage.onChanged.addListener((changes, area) => {
  if (area === "local" && changes.pageTitle) {
    const pageTitle = changes.pageTitle.newValue;

    titleElement.textContent = pageTitle;
    console.log("[PANEL] pageTitle =", pageTitle);
  }
});
