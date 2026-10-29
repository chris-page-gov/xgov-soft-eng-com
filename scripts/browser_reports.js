async (page) => {
  // Start on Explorer with this catalogue loaded; no model or repository code runs.
  const initialUrl=page.url();
  const descriptorUrl=await page.evaluate(()=>new URL(location.href).searchParams.get('bundle'));
  if(!descriptorUrl)throw Error('Open Explorer with the catalogue bundle first');
  const base=await page.evaluate(url=>new URL('./',url).href,descriptorUrl);
  const hash=async bytes=>page.evaluate(async data=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',Uint8Array.from(data)))).map(x=>x.toString(16).padStart(2,'0')).join(''),Array.from(bytes));
  const descriptorResponse=await page.request.get(descriptorUrl);
  const descriptorBytes=await descriptorResponse.body();const descriptor=JSON.parse(descriptorBytes.toString());
  const appRoot=await page.evaluate(()=>new URL('../',location.href).href);
  const consumer=await(await page.request.get(appRoot+'okf-publication-identity.json')).json();
  const app=await(await page.request.get(appRoot+'okf-explorer-build-manifest.json')).json();
  const receipt={schema:'xgov-browser-acceptance.v1',observed_at:new Date().toISOString(),descriptor_url:descriptorUrl,snapshot_id:descriptor.snapshot_id,descriptor_sha256:await hash(descriptorBytes),records:descriptor.counts.records,consumer_commit:consumer.commit,consumer_app_tree_sha256:app.tree_sha256,browser:page.context().browser()?.version(),checks:[],console_errors:[],page_errors:[],failed_requests:[]};
  const onConsole=m=>{if(m.type()==='error')receipt.console_errors.push(m.text());};
  const onPageError=e=>receipt.page_errors.push(e.message);
  const onRequest=r=>receipt.failed_requests.push({url:r.url(),error:r.failure()?.errorText});
  page.on('console',onConsole);page.on('pageerror',onPageError);page.on('requestfailed',onRequest);
  const check=(id,detail)=>receipt.checks.push({id,passed:true,detail});
  try {
    if(descriptor.profile!=='https://github.com/chris-page-gov/xgov-soft-eng-com/blob/main/docs/semantic-model.md')throw Error('Unexpected producer');
    await page.setViewportSize({width:1440,height:1000});
    const declared=descriptor.related_links?.find(link=>link.kind==='evaluation-reports');
    if(!declared||declared.url!==base+'reports/')throw Error('Report link is not bound to this catalogue');
    const link=page.getByRole('navigation',{name:'Related material',exact:true}).getByRole('link',{name:'AI evaluation reports',exact:true});
    if(await link.getAttribute('href')!==declared.url)throw Error('Explorer report URL differs');
    const popupPromise=page.waitForEvent('popup');await link.click();const popup=await popupPromise;
    await popup.waitForLoadState('domcontentloaded');
    if(popup.url()!==declared.url||await popup.title()!=='Public Claude and Gemini evaluation reports')throw Error('Explorer report navigation failed');
    await popup.close();check('explorer-report-link','Producer-declared report link opens the collection');
    await page.goto(base);await page.getByRole('link',{name:'Claude and Gemini evaluation reports',exact:true}).click();
    if(page.url()!==base+'reports/')throw Error('Catalogue report navigation failed');check('catalogue-report-link','Catalogue links to reports');
    const routes=[['','Public Claude and Gemini evaluation reports'],['claude.html','Claude Opus 5.5 evaluation: public edition'],['gemini.html','Gemini 4 Argon evaluation: public edition'],['corrections.html','Editorial corrections and disposition'],['claude-capture-review.html','Claude UI capture: editorial review']];
    for(const [route,title]of routes){const response=await page.goto(base+'reports/'+route);if(response.status()!==200||await page.title()!==title||!await page.getByRole('heading',{name:title,exact:true}).isVisible())throw Error('Report identity failed: '+route);}
    check('report-collection-five-pages','Five HTML report pages return 200 with matching headings');
    await page.goto(base+'reports/claude.html');await page.locator('main').getByRole('link',{name:'editorial review',exact:true}).click();
    if(!page.url().endsWith('claude-capture-review.html')||await page.locator('tbody tr').count()!==35)throw Error('Claude supplement navigation or inventory failed');
    check('claude-capture-update','Claude links to the later UI capture review with 35 requests');
    const manifest=await(await page.request.get(base+'build-manifest.json')).json();
    if(manifest.build_id!==descriptor.snapshot_id)throw Error('Reports build differs');
    const reports=Object.entries(manifest.outputs).filter(([name])=>name.startsWith('reports/'));
    if(reports.length!==14)throw Error('Report output inventory differs');
    for(const [name,sha]of reports){const response=await page.request.get(base+name);if(!response.ok()||await hash(await response.body())!==sha)throw Error('Report output hash differs: '+name);}
    check('report-source-hashes','All 14 report HTML/source/provenance outputs match the frozen build manifest');
    const publication=await(await page.request.get(base+'reports/publication-manifest.json')).json();
    for(const [name,sha]of Object.entries(publication.supporting_files)){const response=await page.request.get(base+'reports/'+name);if(!response.ok()||await hash(await response.body())!==sha)throw Error('Public source hash differs: '+name);}
    check('report-provenance-hashes','Public-edition supporting-file hashes match');
    await page.setViewportSize({width:390,height:844});
    for(const [route]of routes){await page.goto(base+'reports/'+route);if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('Mobile overflow: '+route);}
    check('report-mobile-layout','Five pages fit a 390px viewport');
    for(const name of ['claude.md','gemini.md','claude-capture-review.json']){const text=await(await page.request.get(base+'reports/'+name)).text();if(/file:\/\/|\/Users\/|\/home\/claude|\/root\/\.claude/.test(text))throw Error('Private path in public source: '+name);}
    check('report-no-private-paths','Reviewed report and capture-index sources contain no local paths');
    if(receipt.console_errors.length||receipt.page_errors.length||receipt.failed_requests.length)throw Error('Browser errors or failed requests');
    receipt.status='passed';
  } catch(error){receipt.status='failed';receipt.failure=String(error?.message||error);}
  finally{page.off('console',onConsole);page.off('pageerror',onPageError);page.off('requestfailed',onRequest);await page.setViewportSize({width:1440,height:1000});await page.goto(initialUrl);}
  return receipt;
}
