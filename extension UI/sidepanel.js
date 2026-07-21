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

/*                  *
 * DISPLAY HEADLINE *
 *                  */

const headlineElement = document.getElementById("headline");

function updateHeadlineElement() {
  chrome.storage.local.get(["pageHeadline"], (res) => {
    const pageHeadline = res.pageHeadline ?? "No headline extracted yet.";

    headlineElement.textContent = pageHeadline;
    console.log("[PANEL] pageHeadline =", pageHeadline);
  });
}

/*                  *
 * DISPLAY PAGE TEXT*
 *                  */

const pageTextElement = document.getElementById("page-text");

function updatePageTextElement() {
  chrome.storage.local.get(["pageText"], (res) => {
    const pageText = res.pageText ?? "No page text extracted yet.";

    pageTextElement.textContent = pageText.slice(0, 3000);
    console.log("[PANEL] pageText length =", pageText.length);
  });
}

updateUrlElement();
updateTitleElement();
updateHeadlineElement();
updatePageTextElement();
/*                          *
 * LISTEN FOR STORAGE UPDATE*
 *                          */

chrome.storage.onChanged.addListener((changes, area) => {
  // Update sidepanel when background.js saves a new pageURL
  // ie. new website and extension clicked again, this ensures url displayed updates
  if (area === "local" && changes.pageUrl) {
    const pageUrl = changes.pageUrl.newValue;

    urlElement.textContent = pageUrl;
    console.log("[PANEL] pageUrl =", pageUrl);
  }

  // Update sidepanel when background.js saves a new pageTitle
  if (area === "local" && changes.pageTitle) {
    const pageTitle = changes.pageTitle.newValue;

    titleElement.textContent = pageTitle;
    console.log("[PANEL] pageTitle =", pageTitle);
  }

  // Update sidepanel when background.js saves a new pageText
  if (area === "local" && changes.pageText) {
    const pageText = changes.pageText.newValue;
    // First 3000 characters of pageText
    pageTextElement.textContent = pageText.slice(0, 3000);
    console.log("[PANEL] pageText length =", pageText.length);
  }

  // Update sidepanel when background.js saves a new pageHeadline
  if (area === "local" && changes.pageHeadline) {
    const pageHeadline = changes.pageHeadline.newValue;

    headlineElement.textContent = pageHeadline;
    console.log("[PANEL] pageHeadline =", pageHeadline);
  }
});

/*                       *
 * LAUNCH ENGINE BUTTON  *
 *                       */

const launchEngineButton = document.getElementById("launch-engine-btn");
const globalResultsElement = document.getElementById("global-results");

console.log("[PANEL] launchEngineButton =", launchEngineButton);
console.log("[PANEL] globalResultsElement =", globalResultsElement);

launchEngineButton.addEventListener("click", () => {
  console.log("[PANEL] Launch Engine clicked");

  globalResultsElement.innerHTML = `
  <h3>Global Coverage</h3>

  <div class="country-card">
    <strong>🇮🇳 India</strong>
    <p>3 related articles found</p>
  </div>

  <div class="country-card">
    <strong>🇯🇵 Japan</strong>
    <p>2 related articles found</p>
  </div>

  <div class="country-card">
    <strong>🇩🇪 Germany</strong>
    <p>1 related article found</p>
  </div>
`;
});
