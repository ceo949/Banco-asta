/* Banco d'asta — service worker.

   Pagina: prima la RETE. Con la connessione vedi sempre l'ultima versione pubblicata;
   senza connessione (o se la rete non risponde entro 4 secondi) parte la copia salvata.
   Icone e manifest: prima la cache, si aggiornano in background.

   Cambia CACHE a ogni aggiornamento dei file. */
const CACHE = "bancoasta-v2-9";
const ASSETS = ["./", "./index.html", "./manifest.webmanifest",
  "./icon-192.png", "./icon-512.png", "./apple-touch-icon.png"];
const ATTESA_RETE_MS = 4000;

self.addEventListener("install", e => {
  // cache:"reload" scavalca la memoria del browser: in cache finisce la versione vera del server
  e.waitUntil(caches.open(CACHE)
    .then(c => c.addAll(ASSETS.map(u => new Request(u, {cache: "reload"}))))
    .then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

function ePagina(req, url){
  return req.mode === "navigate" || url.pathname.endsWith("/") || url.pathname.endsWith("/index.html");
}

self.addEventListener("fetch", e => {
  const req = e.request;
  const url = new URL(req.url);
  if (url.hostname === "api.anthropic.com") return;   // gli agenti non passano mai dalla cache
  if (req.method !== "GET") return;

  if (ePagina(req, url)) {
    e.respondWith(new Promise(resolve => {
      let chiuso = false;
      const daCache = () => caches.match("./index.html", {ignoreSearch: true})
        .then(h => h || caches.match(req, {ignoreSearch: true}));
      const timer = setTimeout(() => {
        daCache().then(h => { if (h && !chiuso) { chiuso = true; resolve(h); } });
      }, ATTESA_RETE_MS);
      // per URL e non per Request: una richiesta di navigazione non accetta opzioni
      fetch(url.href, {cache: "no-store"}).then(res => {
        if (res && res.ok) {
          const copia = res.clone();
          caches.open(CACHE).then(c => c.put("./index.html", copia));
        }
        clearTimeout(timer);
        if (!chiuso) { chiuso = true; resolve(res); }
      }).catch(() => {
        clearTimeout(timer);
        daCache().then(h => { if (!chiuso) { chiuso = true;
          resolve(h || new Response("Offline e nessuna copia salvata.", {status: 503})); } });
      });
    }));
    return;
  }

  // icone, manifest e il resto: prima la cache, aggiornamento in background
  e.respondWith(
    caches.match(req).then(hit => {
      const net = fetch(req).then(res => {
        if (res && res.status === 200 && res.type === "basic") {
          const copia = res.clone();
          caches.open(CACHE).then(c => c.put(req, copia));
        }
        return res;
      }).catch(() => hit);
      return hit || net;
    })
  );
});
