/* Local stand-in for the claude.ai dashboard runtime ("dash").
   Loads output/data/<dataset id>.csv on first use and redraws when data arrives. */
(function () {
  const cache = {};
  const listeners = [];
  let queued = false;
  const fire = () => {
    if (queued) return;
    queued = true;
    requestAnimationFrame(() => {
      queued = false;
      listeners.forEach((fn) => { try { fn(); } catch (e) { console.error(e); } });
    });
  };
  const load = (id) => {
    if (cache[id]) return;
    cache[id] = { status: 'loading', data: [], columns: [], meta: [], refreshing: false };
    d3.csv(`../data/${id}.csv`)
      .then((rows) => { cache[id] = { status: 'ok', data: rows, columns: rows.columns, meta: [], refreshing: false }; fire(); })
      .catch((e) => { cache[id] = { status: 'error', data: [], columns: [], meta: [], message: String(e) }; console.error('dataset', id, e); fire(); });
  };
  window.dash = {
    data(id) { load(id); return cache[id]; },
    onData(fn) { listeners.push(fn); try { fn(); } catch (e) { console.error(e); } },
    colors: [1, 2, 3, 4, 5, 6, 7, 8].map((i) => `var(--cds-chart-${i})`),
    setLink(name) { try { history.replaceState(null, '', '#' + name); } catch (e) { /* ignore */ } },
    params() { return {}; }, setParams() {}, resetParams() {}, refresh() {}, calc() {}, loader() {},
  };
  let w = window.innerWidth;
  window.addEventListener('resize', () => { if (window.innerWidth !== w) { w = window.innerWidth; fire(); } });
})();
