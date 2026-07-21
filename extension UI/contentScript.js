// /*                 *
//  * EXTRACT WEBPAGE *
//  * TEXT            *
//  *                 */

// (() => {
//   const articleElement =
//     document.querySelector("article") ||
//     document.querySelector("main") ||
//     document.querySelector('[role="main"]') ||
//     document.body;

//   const pageText = articleElement.innerText || "";

//   console.log("[CONTENT] pageText length =", pageText.length);

//   chrome.runtime.sendMessage({
//     type: "PAGE_TEXT_EXTRACTED",
//     pageText,
//   });
// })();

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
