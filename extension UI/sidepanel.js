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
// Launch Engine clicked
// → sidepanel creates requestBody
// → sidepanel POSTs requestBody to FastAPI
// → FastAPI receives request as Python dict
// → FastAPI returns fake article JSON
// → sidepanel receives JSON as data
// → sidepanel maps data.articles into cards
function setupLaunchEngineButton() {
  const button = document.getElementById("launch-engine-btn");
  const results = document.getElementById("global-results");

  button.addEventListener("click", () => {
    console.log("[PANEL] Launch Engine clicked");

    // Read the extracted page data saved by background.js
    chrome.storage.local.get(
      ["pageUrl", "pageTitle", "pageHeadline", "pageText"],
      async (res) => {
        const pageUrl = res.pageUrl ?? "";
        const pageTitle = res.pageTitle ?? "";
        const pageHeadline = res.pageHeadline ?? "";
        const pageText = res.pageText ?? "";

        // Create the request object that will be sent to FastAPI.
        // searchQuery prioritizes the real article headline, then browser title, then URL.
        const requestBody = {
          pageUrl,
          pageTitle,
          pageHeadline,
          searchQuery: pageHeadline || pageTitle || pageUrl,
          pageTextPreview: pageText.slice(0, 1000),
        };

        console.log("[PANEL] API requestBody =", requestBody);

        // Send the requestBody object to the FastAPI backend
        const response = await fetch("http://127.0.0.1:8001/api/search", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(requestBody), //Convert requestBody object to a JSON
        });

        // Store main.py return in data
        const data = await response.json();
        console.log("[PANEL] backend response =", data);

        results.innerHTML = `
        <h3>Global Coverage</h3>
        ${data.articles
          .map(
            (article) => `
              <div class="country-card">
                <strong>${article.country}</strong>
                <p>${article.source}</p>
                <p>${article.title}</p>
                <a href="${article.url}" target="_blank">Open article</a>
              </div>
            `,
          )
          .join("")}
      `;
      },
    );
  });
}

setupLaunchEngineButton();
