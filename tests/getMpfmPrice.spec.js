// @ts-check
import { test, expect } from '@playwright/test';
const fs = require('fs');
const path = require('path');

test.setTimeout(0); // 0 = 不限制；或设 2 小时：test.setTimeout(2 * 60 * 60 * 1000)

test('getMFPMData', async ({ page }) => {
	await page.goto('https://mpfm.com.mo/cn/index.php');
	
	const USER = process.env.MPFM_USER;
	const PASS = process.env.MPFM_PASS;
	if (!USER || !PASS) {
		throw new Error('缺少环境变量 MPFM_USER / MPFM_PASS');
	}
	const page1Promise = page.waitForEvent('popup');
	await page.getByRole('link').nth(2).click();
	const page1 = await page1Promise;

	await page1.waitForLoadState();
	await page1.getByRole('textbox', { name: '登入名稱' }).click();
	await page1.getByRole('textbox', { name: '登入名稱' }).fill(USER);
	await page1.getByRole('textbox', { name: '密碼' }).click();
	await page1.getByRole('textbox', { name: '密碼' }).fill(PASS);
	await page1.getByRole('button', { name: '登入' }).click(); // whatever triggers window #2

	await page1.waitForLoadState();

	await page1.getByRole('tab', { name: '基金資料' }).click();

	await page1.getByRole('radio').nth(1).check();


	const seenDates = new Set();

	const START = process.env.START_DATE || '2026-09-30';
	const END   = process.env.END_DATE   || '2026-10-02';

	const DATA_DIR = 'priceData';
	if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });

	let lastPriceDate = null;

	for (let d = new Date(START); d <= new Date(END); d.setDate(d.getDate() + 1)) {
		if (d.getDay() === 0 || d.getDay() === 6) continue;

		const dateStr = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
		await page1.locator('#priceDate').fill(dateStr);
		await page1.getByRole('button', { name: '確定' }).click();

		await expect.poll(
		async () => {
		  const t = await page1.locator('#unitPrice').innerText();
		  return (t.match(/截至\s*(\d{4}-\d{2}-\d{2})/) || [])[1] || null;
		},
		{ timeout: 15000, intervals: [300, 500, 1000] }
		).not.toBe(lastPriceDate);

		const unitPriceText = await page1.locator('#unitPrice').innerText();
		const priceDate = (unitPriceText.match(/截至\s*(\d{4}-\d{2}-\d{2})/) || [])[1];
		if (!priceDate) continue;

		// 等价格行也渲染完（8 只基金 = 8 行，行数稳定后再读）
		const priceTable = page1.locator('table#balance_table')
		.filter({ hasNotText: '累計供款' })
		.filter({ hasNotText: '成份基金' });
		await expect(priceTable.locator('tbody tr')).toHaveCount(9, { timeout: 15000 });

	
		const m = unitPriceText.match(/截至\s*(\d{4}-\d{2}-\d{2})/);
		if (!m) throw new Error(`找不到截至日期：${unitPriceText.slice(0, 80)}`);


		if (seenDates.has(priceDate)) continue; // 同一辦公日已抓過（週末/假期會重複）
		seenDates.add(priceDate);

		// ⬇️ 每个日期一个文件：fund_prices_2026-09-01.csv
		const fileName = path.join(DATA_DIR, `fund_prices_${priceDate}.csv`);

		if (fs.existsSync(fileName)) {
			const lines = fs.readFileSync(fileName, 'utf8').trim().split('\n').length - 1; // 去掉表头
			if (lines >= 8) { console.log(`跳过 ${priceDate}`); continue; }
			console.log(`${priceDate} 只有 ${lines} 行，重新抓取`);
		}

		const dayOut = fs.createWriteStream(fileName, { encoding: 'utf8' });
		dayOut.write('\ufeffprice_date,fund_name,price\n'); // BOM + 表头

		const rows = priceTable.locator('tbody tr');
		for (let i = 0; i < await rows.count(); i++) {
		  const name  = (await rows.nth(i).locator('td').first().innerText()).trim();
		  const price = (await rows.nth(i).locator('td[align="right"]').innerText()).trim();
		  if (name && price) dayOut.write(`${priceDate},${csvEscape(name)},${csvEscape(price)}\n`);
		}

		await new Promise(res => dayOut.end(res));
		
  }
 
});

function csvEscape(s) {
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}