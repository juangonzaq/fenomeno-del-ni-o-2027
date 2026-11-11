// Mapa de áreas inundadas con radar Sentinel-1 (Google Earth Engine)
// ------------------------------------------------------------------
// Para qué: construir la "etiqueta" observada (dónde se inundó de verdad) para
// 2017 (Niño Costero) y 2023 (ciclón Yaku), y después para 2027 con los mismos pasos.
//
// Cómo usarlo:
//   1. Entra a https://code.earthengine.google.com (cuenta gratuita para uso académico).
//   2. Sube datos/2_limpios/territorio/distritos_costa_norte.geojson como asset
//      (Assets > New > Table upload) y pon su ruta en DISTRITOS. Ya trae solo los
//      364 distritos de Tumbes a Áncash, todos con polígono.
//   3. Elige el EVENTO y presiona Run. En la pestaña Tasks aparecen dos exportaciones:
//      un GeoTIFF con la máscara de inundación y un CSV con hectáreas inundadas por distrito.
//
// Método (detección de cambio, como en la guía UN-SPIDER):
//   inundado = (VV_después - VV_antes) < -3 dB  y  VV_después < -15 dB
//   y se descartan agua permanente (JRC), pendientes > 5° y zonas sobre 400 m.
// Los umbrales son puntos de partida: revísalos con imágenes ópticas o fotos.

var DISTRITOS = 'users/TU_USUARIO/peru_distritos';   // <- cambia esto
var EVENTO = '2017';                                 // '2017' o '2023'

var FECHAS = {
  '2017': {antes: ['2016-11-01', '2017-01-10'], despues: ['2017-03-15', '2017-04-05']},
  '2023': {antes: ['2022-11-01', '2023-01-15'], despues: ['2023-03-05', '2023-03-25']}
};

// Caja de Tumbes a Áncash
var caja = ee.Geometry.Rectangle([-81.5, -10.9, -76.6, -3.3]);
var distritos = ee.FeatureCollection(DISTRITOS);

function s1(inicio, fin) {
  return ee.ImageCollection('COPERNICUS/S1_GRD')
    .filterBounds(caja)
    .filterDate(inicio, fin)
    .filter(ee.Filter.eq('instrumentMode', 'IW'))
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
    .select('VV')
    .map(function (img) { return img.focalMedian(50, 'circle', 'meters'); }) // reduce el moteado
    .median()
    .clip(caja);
}

var f = FECHAS[EVENTO];
var antes = s1(f.antes[0], f.antes[1]);
var despues = s1(f.despues[0], f.despues[1]);
var cambio = despues.subtract(antes);

var aguaPermanente = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('seasonality').gte(10);
var dem = ee.Image('USGS/SRTMGL1_003');
var pendiente = ee.Terrain.slope(dem);

var inundado = cambio.lt(-3)
  .and(despues.lt(-15))
  .and(aguaPermanente.unmask(0).not())
  .and(pendiente.lt(5))
  .and(dem.lt(400))
  .selfMask()
  .rename('inundado');

// Quita pixeles sueltos (menos de 8 conectados)
inundado = inundado.updateMask(inundado.connectedPixelCount(8, true).gte(8));

Map.centerObject(caja, 7);
Map.addLayer(antes, {min: -25, max: 0}, 'VV antes', false);
Map.addLayer(despues, {min: -25, max: 0}, 'VV después', false);
Map.addLayer(inundado, {palette: ['0000FF']}, 'Inundado ' + EVENTO);
Map.addLayer(distritos.style({color: '555555', fillColor: '00000000', width: 0.5}), {}, 'Distritos');

// Hectáreas inundadas por distrito
var area = inundado.multiply(ee.Image.pixelArea()).divide(1e4).rename('ha_inundadas');
var porDistrito = area.reduceRegions({
  collection: distritos, reducer: ee.Reducer.sum(), scale: 20, tileScale: 8
}).map(function (ft) {
  return ft.set('evento', EVENTO).set('ha_inundadas', ee.Number(ft.get('sum')));
});

Export.table.toDrive({
  collection: porDistrito.select(['ubigeo', 'distrito', 'provincia', 'departamento', 'evento', 'ha_inundadas']),
  description: 'ha_inundadas_por_distrito_' + EVENTO,
  fileFormat: 'CSV'
});
Export.image.toDrive({
  image: inundado.unmask(0).toByte(),
  description: 'mascara_inundacion_s1_' + EVENTO,
  region: caja, scale: 30, maxPixels: 1e13
});
