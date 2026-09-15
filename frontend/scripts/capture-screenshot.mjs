import { chromium } from "playwright";


const baseUrl = process.env.CX_SCREENSHOT_URL || "http://localhost:8080";
const outputPath = new URL("../../screenshots/dashboard.png", import.meta.url).pathname;
const demoPrompts = [
  "Where can I view my invoice?",
  "My internet connection is offline",
  "I want to cancel my contract",
  "Can you recommend a movie tonight?",
];


for (const message of demoPrompts) {
  const response = await fetch(`${baseUrl}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, language: "en" }),
  });
  if (!response.ok) {
    throw new Error(`Could not seed screenshot data: ${response.status}`);
  }
}

const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1024 },
    deviceScaleFactor: 1,
  });
  const pageErrors = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));
  await page.goto(baseUrl, { waitUntil: "networkidle" });
  await page.screenshot({ path: outputPath, fullPage: true });
  if (pageErrors.length) {
    throw new Error(`Browser errors: ${pageErrors.join("; ")}`);
  }
  console.log(`Screenshot saved to ${outputPath}`);
} finally {
  await browser.close();
}
