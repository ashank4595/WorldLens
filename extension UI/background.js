//Saves

// Side panel appears only on the tab where user clicked World Lens
// Switch tabs → panel hides
// Return to original tab → panel comes back
// TODO: Store page data separately for each tab so reopening an older tab shows
// its own URL and results. For now, storage is shared globally, so opening
// the extension on a new tab overwrites the previous tab's data.

/* DISABLE      *
 * AUTO OPENING *
 * SIDE PANEL   */
// This is for hiding panel when switching tabs in onclicked

//Do not automatically open the side panel when the extension icon is clicked
//We open it with the on clicked function and change behaviour
chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: false });

// Disable the panel by default for every tab.
// We will enable it only for the tab where the user clicks the extension.
chrome.sidePanel.setOptions({ enabled: false });

// Keep the side panel disabled by default after install/reload.
chrome.runtime.onInstalled.addListener(() => {
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: false });

  chrome.sidePanel.setOptions({ enabled: false });
});

//ON CLICKED FUNCTION, RUNS WHEN EXTENSION ICON IS CLICKED
//chrome returns tab object containing id, url, title
chrome.action.onClicked.addListener((tab) => {
  // Set sidepanel's optiona
  // Enable the panel only for this specific tab.
  chrome.sidePanel.setOptions({
    tabId: tab.id,
    path: "sidepanel.html",
    enabled: true,
  });

  /* SAVE PAGE URL *
   * , TITLE,     *
   * TO LOCAL      */
  const pageUrl = tab.url
    ? tab.url
    : "NO_URL — restricted page or no activeTab grant";

  // let pageUrl;
  // if (tab.url) {
  //   pageUrl = tab.url;
  // } else {
  //   pageUrl = "NO_URL — restricted page or no activeTab grant";
  // }

  const pageTitle = tab.title ? tab.title : "NO_TITLE";

  // Prints to service worker console for debugging.
  console.log("[BACKGROUND] tab.url =", tab.url);
  console.log("[BACKGROUND] full tab =", tab);

  // Saves URL and page title to local storage as pageUrl and pageTitle
  // contentScript.js executes and later updates pageHeadline and pageText
  // sidepanel.js reads what is saved to local
  chrome.storage.local.set(
    {
      pageUrl,
      pageTitle,
      pageHeadline: "Extracting headline...",
      pageText: "Extracting page text...",
    },
    () => {
      console.log("[BACKGROUND] saved pageUrl =", pageUrl);
      console.log("[BACKGROUND] saved pageTitle =", pageTitle);
      console.log("[BACKGROUND] reset pageHeadline and pageText");
    },
  );

  // Execute contentScript.js inside the tab
  // Background.js is not so cannot read or write
  chrome.scripting.executeScript(
    {
      target: { tabId: tab.id },
      files: ["contentScript.js"],
    },
    () => {
      if (chrome.runtime.lastError) {
        console.log(
          "[BACKGROUND] content script injection failed:",
          chrome.runtime.lastError.message,
        );

        chrome.storage.local.set({
          pageText: "Could not extract text from this page.",
          pageHeadline: "Could not extract headline from this page.",
        });
      } else {
        console.log("[BACKGROUND] contentScript.js injected");
      }
    },
  );

  // Open side panel
  chrome.sidePanel.open({ tabId: tab.id });
});

/*                         *
 * RECEIVE PAGE CONTENT    *
 * FROM CONTENT SCRIPT     *
 * SAVE TO LOCAL           */

//Listens for contentScript.js to send PAGE_CONTENT_EXTRACTED
chrome.runtime.onMessage.addListener((message) => {
  if (message.type === "PAGE_CONTENT_EXTRACTED") {
    chrome.storage.local.set(
      {
        pageHeadline: message.pageHeadline,
        pageText: message.pageText,
      },
      () => {
        console.log("[BACKGROUND] saved pageHeadline =", message.pageHeadline);
        console.log(
          "[BACKGROUND] saved pageText length =",
          message.pageText.length,
        );
      },
    );
  }
});
