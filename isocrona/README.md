# Isócrona de carro a partir de Como San Giovanni

Área alcançável de carro (sem trânsito) em 30, 60, 90 e 105 min a partir da estação Como San Giovanni (45.80889, 9.07222), com foco nas localidades suíças.

- `mapa.html` — mapa interativo (abre direto no navegador).
- `data/localidades_ch_105min.csv` — localidades suíças até 105 min, com tempo e km de carro.
- `data/ch_places.json` — todas as 526 localidades suíças a até 148 km em linha reta, com tempo calculado.
- `data/grid.json` — grade (~3,3 km) com o tempo de carro até cada ponto, em segundos.
- `data/it_cities.json` — tempos até as maiores cidades italianas da região.
- `data/mapdata.json` — polígonos e camadas usados pelo mapa.
- `scripts/` — scripts usados (Python 3 + shapely).

## Método
- Motor de rotas Valhalla (servidor público `valhalla1.openstreetmap.de`, dados OpenStreetMap), perfil `auto`.
- `country_crossing_cost` e `country_crossing_penalty` zerados (o padrão soma 10 min por fronteira).
- O servidor público limita isócronas a 60 min e a matriz a 150 km de rota; por isso a grade usa a matriz e completa os pontos sem tempo com rotas individuais (`fill.py`).
- Localidades: GeoNames (`CH.zip`, lugares povoados com população > 0). Fronteiras: `world-atlas` (Natural Earth) e `swiss-maps` (swisstopo/FSO).

## Limites
- O Valhalla parece lento nas autoestradas italianas (ex.: Como→Milão 60 min, Como→Bergamo 82 min), por isso existe a faixa de 105 min. Não foi confrontado com o Google.
- Espera na alfândega não está incluída. Borda com ~3 km de precisão.
