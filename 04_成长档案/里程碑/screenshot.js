const puppeteer = require('puppeteer');

async function takeScreenshot() {
  console.log('启动浏览器...');
  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: '/root/.cache/ms-playwright/chromium-1208/chrome-linux64/chrome',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });

  const page = await browser.newPage();

  await page.setViewport({
    width: 1260,
    height: 1700,
    deviceScaleFactor: 2
  });

  const htmlPath = '/root/.openclaw/workspace/04_成长档案/里程碑/三大工程诗经咏怀.html';
  console.log('加载HTML:', htmlPath);
  await page.goto(`file://${htmlPath}`, {
    waitUntil: 'networkidle0',
    timeout: 60000
  });

  console.log('等待渲染...');
  await page.evaluateHandle('document.fonts.ready');
  await new Promise(resolve => setTimeout(resolve, 3000));

  const screenshotPath = '/root/.openclaw/workspace/04_成长档案/里程碑/三大工程诗经咏怀.png';
  console.log('截图保存:', screenshotPath);
  await page.screenshot({
    path: screenshotPath,
    fullPage: true
  });

  console.log('截图完成！');

  await browser.close();
}

takeScreenshot().catch(err => {
  console.error('错误:', err);
  process.exit(1);
});
