const { chromium } = require('/usr/lib/node_modules/openclaw/node_modules/playwright-core');

const htmlPath = process.argv[2] || '/root/.openclaw/workspace/03_输出成果/Token采集需求分析/arch_diagrams/总体架构图_呈彩设计.html';
const outputPath = process.argv[3] || '/root/.openclaw/workspace/03_输出成果/Token采集需求分析/arch_diagrams/总体架构图_呈彩设计.png';

(async () => {
  console.log('启动浏览器...');
  const browser = await chromium.launch({
    headless: true
  });
  
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1600, height: 1200 });
  
  console.log('加载页面: file://' + htmlPath);
  await page.goto('file://' + htmlPath, {
    waitUntil: 'networkidle',
    timeout: 30000
  });
  
  // 等待渲染完成
  console.log('等待渲染...');
  await page.waitForTimeout(5000);
  
  console.log('截图...');
  await page.screenshot({
    path: outputPath,
    fullPage: true
  });
  
  await browser.close();
  console.log('截图完成: ' + outputPath);
})();
