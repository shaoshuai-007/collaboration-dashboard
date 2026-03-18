const puppeteer = require('puppeteer');
const path = require('path');

const htmlPath = process.argv[2] || '/root/.openclaw/workspace/03_输出成果/Token采集需求分析/arch_diagrams/总体架构图_呈彩设计.html';
const outputPath = process.argv[3] || '/root/.openclaw/workspace/03_输出成果/Token采集需求分析/arch_diagrams/总体架构图_呈彩设计.png';

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  await page.setViewport({ width: 1600, height: 1200 });
  
  await page.goto('file://' + htmlPath, {
    waitUntil: 'networkidle0',
    timeout: 30000
  });
  
  // 等待渲染完成
  await page.waitForTimeout(3000);
  
  await page.screenshot({
    path: outputPath,
    fullPage: true
  });
  
  await browser.close();
  console.log('截图完成: ' + outputPath);
})();
