/*                 *
 * EXTRACT WEBPAGE *
 * TEXT            *
 *                 */

const pageText = document.body.innerText || "";

console.log("[CONTENT] extracted pageText length =", pageText.length);

chrome.runtime.sendMessage({
  type: "PAGE_TEXT_EXTRACTED",
  pageText,
});
