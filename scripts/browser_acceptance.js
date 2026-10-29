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
    await page.waitForFunction(() => document.querySelectorAll('[data-facet-key]').length === 25, undefined, {timeout: 20000});
    require(await page.locator('[data-facet-key]').count() === 25 && definitions.length === 25, 'All 25 facets must be available');
    for (const facet of definitions) {
      await reset();
      const section = page.locator(`[data-facet-key=${JSON.stringify(facet.key)}]`);
      const toggle = section.locator('.facet-toggle');
      if (await toggle.getAttribute('aria-expanded') !== 'true') await toggle.click();
      const row = distributions[facet.key][0];
      const value = section.locator(`button.facet-value[data-facet-value=${JSON.stringify(row.value)}]`);
      await value.waitFor();
      await page.waitForFunction(({key, value, expected}) => {
        const section = Array.from(document.querySelectorAll('[data-facet-key]')).find(node => node.getAttribute('data-facet-key') === key);
        const button = Array.from(section?.querySelectorAll('button.facet-value') || []).find(node => node.getAttribute('data-facet-value') === value);
        const total = button?.querySelector('small')?.textContent?.split('/').at(-1).replaceAll(',', '').trim();
        return total && Number(total) === expected;
      }, {key: facet.key, value: row.value, expected: row.count}, {timeout: 20000});
      const displayed = Number((await value.locator('small').innerText()).split('/').at(-1).replaceAll(',', '').trim());
      require(displayed === row.count, `${facet.key}: displayed distribution differs from the checked catalogue`);
      await value.press('Alt+Enter'); await matchCount(row.count);
      receipt.checks.push({id: `facet-${facet.key}`, value: row.value, expected: row.count, observed: displayed, passed: true});
    }
    await reset();
    const search = page.getByRole('textbox', {name: 'Search static index'});
    await search.fill('nhs111-resources'); await matchCount(1);
    require(await content.getByText('111Online/nhs111-resources', {exact: true}).count() > 0, 'Full hyphenated name must find its repository');
    receipt.checks.push({id: 'hyphenated-repository-search', expected: 1, passed: true});
    await search.fill('xgov-no-such-repository-931785'); await matchCount(0);
    receipt.checks.push({id: 'zero-result-search', expected: 0, passed: true});
    require(!receipt.console_errors.length && !receipt.page_errors.length && !receipt.failed_requests.length, 'Browser errors or failed requests occurred');
    receipt.status = 'passed'; return receipt;
  } catch (error) {
    receipt.status = 'failed'; receipt.failure = error.message; return receipt;
  } finally {
    page.off('console', consoleError); page.off('pageerror', pageError); page.off('requestfailed', requestError);
  }
}
