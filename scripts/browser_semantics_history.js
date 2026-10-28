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
    const unpack = async path => {
      const response = await page.request.get(descriptorUrl.slice(0,descriptorUrl.lastIndexOf('/')+1)+path);
      if (!response.ok()) throw new Error('Resource failed: '+path);
      return page.evaluate(async bytes => {
        let stream = new Blob([Uint8Array.from(bytes)]).stream();
        if (bytes[0] === 31 && bytes[1] === 139) stream = stream.pipeThrough(new DecompressionStream('gzip'));
        return JSON.parse(await new Response(stream).text());
      }, Array.from(await response.body()));
    };
    const locator = await read('data/record-locator.json');
    const route = 'repositories/111online%2Fnhs111-resources.md';
    let hash = 2166136261;
    for (const char of route) hash = Math.imul(hash ^ char.charCodeAt(0),16777619) >>> 0;
    const locations = await read(locator.buckets[hash.toString(16).padStart(8,'0').slice(0,2)].path);
    const location = locations[route];
    const records = await unpack(locator.record_chunks[location[0]].path);
    const repository = records[location[1]];
    require(repository.route === route && repository.activity, 'History example must have a bound available observation');
    const activity = repository.activity;
    const actor = activity.contributors.find(row => row.login && row.recent_reported_commits > 0);
    require(actor, 'History example must retain a recent contributor account');
    const clean = await page.evaluate(bundle => { const url = new URL(location.href); url.search = new URLSearchParams({bundle, view:'reader'}).toString(); url.hash='overview'; return url.href; }, descriptorUrl);
    await page.goto(clean);
    const openRepository = async record => {
      await page.getByRole('navigation',{name:'Views'}).getByRole('button',{name:'Reader',exact:true}).click();
      await page.getByRole('textbox',{name:'Search static index'}).fill(record.title);
      await content.getByText(record.title,{exact:true}).first().click();
      await page.getByRole('navigation',{name:'Views'}).getByRole('button',{name:'Narrative',exact:true}).click();
      await content.getByRole('heading',{name:record.title,exact:true}).first().waitFor();
      await content.getByText('Repository activity, contributors and evidence',{exact:true}).first().waitFor();
    };
    await openRepository(repository);
    const narrative = await content.innerText();
    require(narrative.includes(activity.historical_reported_commits.toLocaleString('en-GB')+' historical commits'), 'Historical total missing');
    require(narrative.includes(activity.recent_reported_commits.toLocaleString('en-GB')+' recent commits'), 'Recent total missing');
    require(narrative.includes(activity.window.start) && narrative.includes(activity.window.end_exclusive), 'Exact recent period missing');
    require(narrative.includes(activity.source.sha256), 'Observation hash missing');
    const actorRow = content.getByRole('row').filter({hasText:'@'+actor.login});
    const cells = await actorRow.getByRole('cell').allTextContents();
    require(Number(cells[1].replaceAll(',','')) === actor.historical_reported_commits && Number(cells[2].replaceAll(',','')) === actor.recent_reported_commits, 'Contributor counts differ from the observation');
    require(await content.getByRole('table').count() >= 3, 'Contributor, annual and weekly tables must render');
    receipt.checks.push({id:'history-counts-period-tables-and-provenance', historical:activity.historical_reported_commits, recent:activity.recent_reported_commits, contributor:actor.login, observation_sha256:activity.source.sha256, passed:true});
    const details = page.getByRole('complementary',{name:'Record details'});
    await details.getByRole('tab',{name:'Evidence',exact:true}).click();
    await details.getByText(/^Relationships \(/).click();
    const relationshipName = repository.title+' → recent_contributor → @'+actor.login;
    await details.getByRole('button',{name:relationshipName,exact:true}).click();
    require((await details.innerText()).includes('reported recent contributor to'), 'Inverse relationship label missing');
    await details.getByText('Relationship JSON',{exact:true}).click();
    const raw = JSON.parse(await details.getByText('Relationship JSON',{exact:true}).locator('..').locator('pre').innerText());
    require(raw.source_iri === repository.id && raw.predicate === 'urn:okf:xgov:reportedRecentContributor', 'Semantic assertion identity differs');
    const adjacency = await read('data/adjacency.json');
    const incident = (await unpack(adjacency.buckets[hash.toString(16).padStart(8,'0').slice(0,2)].path))[route];
    const assertion = incident.find(row => row.id === raw.id);
    require(assertion && assertion.measurement.reported_commits === actor.recent_reported_commits, 'Published assertion contribution count differs');
    require(raw.evidence.some(row => row.sourceSha256 === activity.source.sha256), 'Assertion observation hash differs');
    require(raw.assertion_status === 'normalized' && raw.assertion_scope === 'real-world', 'Assertion authority plane changed');
    require(await details.getByRole('link',{name:'Source evidence',exact:true}).getAttribute('href') === raw.evidence[0].url, 'Source evidence link differs');
    receipt.checks.push({id:'semantic-assertion-inverse-measurement-and-source', assertion_id:raw.id, passed:true});
    await details.getByRole('tab',{name:'Target',exact:true}).click();
    await details.getByRole('button',{name:'Inspect target card',exact:true}).click();
    await details.getByRole('heading',{name:'@'+actor.login,exact:true}).waitFor();
    await details.getByRole('button',{name:relationshipName,exact:true}).waitFor();
    require(await details.getByRole('button',{name:relationshipName,exact:true}).count() === 1, 'Contributor incoming relationship missing');
    await details.getByRole('button',{name:relationshipName,exact:true}).click();
    await details.getByRole('tab',{name:'Source',exact:true}).click();
    await details.getByRole('button',{name:'Inspect source card',exact:true}).click();
    await content.getByRole('heading',{name:repository.title,exact:true}).first().waitFor();
    receipt.checks.push({id:'contributor-target-and-inverse-source-navigation', passed:true});
    const absent = records.find(row => !row.activity);
    require(absent, 'Missing-history example required');
    await openRepository(absent);
    require((await content.innerText()).includes('Statistics are not available in this snapshot. This does not mean no activity or no contributors.'), 'Missing history must remain explicit');
    receipt.checks.push({id:'missing-history-is-not-zero', repository:absent.title, passed:true});
    await page.setViewportSize({width:390,height:844});
    await page.getByRole('button',{name:'Search & facets',exact:true}).click();
    await page.getByRole('textbox',{name:'Search static index'}).waitFor();
    await page.getByRole('button',{name:'Details',exact:true}).click();
    await details.waitFor();
    await page.getByRole('button',{name:'Results',exact:true}).click();
    const box = await content.getByRole('heading',{name:absent.title,exact:true}).first().boundingBox();
    require(box && box.x >= 0 && box.x+box.width <= 391, 'Repository heading is outside the narrow viewport');
    receipt.checks.push({id:'narrow-viewport-navigation-and-reading', width:390, passed:true});
    await page.setViewportSize({width:1440,height:1000});
    const navigation = page.getByRole('button',{name:'Toggle navigation',exact:true});
    if (await navigation.getAttribute('aria-expanded') !== 'true') await navigation.click();
    await openRepository(repository);
    const link = page.url();
    await page.reload();
    await content.getByRole('heading',{name:repository.title,exact:true}).first().waitFor({timeout:15000});
    await page.waitForFunction(sha => document.querySelector('[aria-label="Explorer content"]')?.innerText.includes(sha),activity.source.sha256,{timeout:15000});
    require((await content.innerText()).includes(activity.source.sha256), 'Reloaded route lost its observation');
    receipt.checks.push({id:'repository-deep-link-reload', url:link, passed:true});
    require(!receipt.console_errors.length && !receipt.page_errors.length && !receipt.failed_requests.length, 'Browser errors or failed requests occurred');
    receipt.status='passed'; return receipt;
  } catch (error) {
    receipt.status='failed'; receipt.failure=error.message; return receipt;
  } finally {
    page.off('console',consoleError);page.off('pageerror',pageError);page.off('requestfailed',requestError);
  }
}
