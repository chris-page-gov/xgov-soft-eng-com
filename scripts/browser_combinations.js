async (page) => {
  // Run with playwright-cli run-code --filename after opening the descriptor.
  // An explicit browser journey, with no test framework or repository execution.
  const descriptorUrl = await page.evaluate(() => new URL(location.href).searchParams.get('bundle'));
  if (!descriptorUrl) throw new Error('Open Explorer with the catalogue bundle parameter first');
  const read = async (path) => {
    const response = await page.request.get(descriptorUrl.slice(0, descriptorUrl.lastIndexOf('/') + 1) + path);
    if (!response.ok()) throw new Error(`Catalogue resource failed: ${path}`);
    return response.json();
  };
  const descriptorResponse = await page.request.get(descriptorUrl);
  const descriptorBytes = Array.from(await descriptorResponse.body());
  const descriptorHash = await page.evaluate(async bytes => Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', Uint8Array.from(bytes)))).map(value => value.toString(16).padStart(2, '0')).join(''), descriptorBytes);
  const descriptor = await descriptorResponse.json();
  const appRoot = await page.evaluate(() => new URL('../', location.href).href);
  const consumer = await (await page.request.get(appRoot + 'okf-publication-identity.json')).json();
  const app = await (await page.request.get(appRoot + 'okf-explorer-build-manifest.json')).json();
  if (descriptor.profile !== 'https://github.com/chris-page-gov/xgov-soft-eng-com/blob/main/docs/semantic-model.md') throw new Error('This journey applies only to the cross-government software catalogue');
  const definitions = (await read('data/facet-definitions.json')).facets;
  const distributions = await read('data/facets.json');
  const receipt = {schema: 'xgov-browser-acceptance.v1', observed_at: new Date().toISOString(), descriptor_url: descriptorUrl, snapshot_id: descriptor.snapshot_id, records: descriptor.counts.records, descriptor_sha256: descriptorHash, consumer_commit: consumer.commit, consumer_app_tree_sha256: app.tree_sha256, browser: page.context().browser()?.version(), checks: [], console_errors: [], page_errors: [], failed_requests: []};
  const consoleError = message => { if (message.type() === 'error') receipt.console_errors.push(message.text()); };
  const pageError = error => receipt.page_errors.push(error.message);
  const requestError = request => receipt.failed_requests.push({url: request.url(), error: request.failure()?.errorText});
  page.on('console', consoleError); page.on('pageerror', pageError); page.on('requestfailed', requestError);
  const require = (condition, message) => { if (!condition) throw new Error(message); };
  const content = page.getByRole('region', {name: 'Explorer content'});
  const matchCount = async expected => {
    await page.waitForFunction(n => {
      const text = document.querySelector('[aria-label="Explorer content"]')?.innerText || '';
      const match = text.match(/([\d,]+)\s+repositories matching/);
      return match && Number(match[1].replaceAll(',', '')) === n && !text.includes('Updating results');
    }, expected, {timeout: 20000});
  };
  const reset = async () => {
    const button = page.getByRole('button', {name: 'Reset view', exact: true});
    if (await button.count()) await button.click();
    const clear = page.getByRole('button', {name: 'Clear filters', exact: true});
    if (await clear.isEnabled()) await clear.click();
  };
  try {
    const clean = await page.evaluate(bundle => { const url = new URL(location.href); url.search = new URLSearchParams({bundle, view: 'reader'}).toString(); url.hash = 'overview'; return url.href; }, descriptorUrl);
    await page.goto(clean);
    await page.getByRole('textbox', {name: 'Search static index'}).waitFor();
    await page.locator('[aria-label="Facet visibility"]').getByRole('button', {name: 'All', exact: true}).click();
    const openFacet = async key => {
      const section = page.locator(`[data-facet-key=${JSON.stringify(key)}]`);
      if (await section.locator('.facet-toggle').getAttribute('aria-expanded') !== 'true') await section.locator('.facet-toggle').click();
      return section;
    };
    const choose = async (key, value, keep = false) => {
      const section = await openFacet(key);
      const button = section.locator(`button.facet-value[data-facet-value=${JSON.stringify(value)}]`);
      if (keep) await button.press('Alt+Enter'); else await button.click();
    };
    const language = (await read('data/search/filters/language.json')).values;
    const archived = (await read('data/search/filters/archived.json')).values;
    const union = new Set([...language.Python, ...language.JavaScript]);
    const intersection = archived.false.filter(id => union.has(id)).length;
    await page.getByRole('checkbox', {name: 'Select multiple values'}).check();
    await choose('language', 'Python'); await choose('language', 'JavaScript');
    await content.getByRole('button', {name: 'Keep highlighted', exact: true}).click(); await matchCount(union.size);
    receipt.checks.push({id:'or-within-facet', expected:union.size, passed:true});
    await choose('archived', 'false', true); await matchCount(intersection);
    receipt.checks.push({id:'and-across-facets', expected:intersection, passed:true});
    await reset();
    const unknown = distributions.is_fork.find(row => row.value === 'unknown').count;
    await choose('is_fork', 'unknown', true); await matchCount(unknown);
    receipt.checks.push({id:'unknown-fork-is-separate', expected:unknown, passed:true});
    await reset();
    const publisher = await openFacet('publisher');
    const find = publisher.getByRole('textbox', {name:'Find values in Hosting account'});
    await find.fill('hmrc');
    require(await publisher.locator('button.facet-value').count() === 1, 'High-cardinality value search must narrow to hmrc');
    require(await publisher.locator('button.facet-value').getAttribute('data-facet-value') === 'hmrc', 'Wrong hosting account found');
    await find.fill('');
    const before = await publisher.locator('button.facet-value').count();
    await publisher.getByRole('button', {name:'Show more values',exact:true}).click();
    const after = await publisher.locator('button.facet-value').count();
    require(after > before && after <= distributions.publisher.length, 'Value paging did not expand within the declared distribution');
    receipt.checks.push({id:'high-cardinality-search-and-paging', before, after, values:distributions.publisher.length, passed:true});
    const available = distributions.history_coverage.find(row => row.value === 'available').count;
    await choose('history_coverage', 'available', true); await matchCount(available);
    receipt.checks.push({id:'available-history-filter', expected:available, passed:true});
    require(!receipt.console_errors.length && !receipt.page_errors.length && !receipt.failed_requests.length, 'Browser errors or failed requests occurred');
    receipt.status = 'passed'; return receipt;
  } catch (error) {
    receipt.status = 'failed'; receipt.failure = error.message; return receipt;
  } finally {
    page.off('console', consoleError); page.off('pageerror', pageError); page.off('requestfailed', requestError);
  }
}
