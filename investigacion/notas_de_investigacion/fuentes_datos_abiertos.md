# Open datasets and data access for a flood-prone-zone model (El Niño, northern coast of Peru: Tumbes, Piura, Lambayeque, La Libertad, Áncash)

How I checked: on 2026-11-10 I sent HTTP requests (curl, desktop user agent) to every URL below. "Verified 200" means the page loaded. "Unreachable (000)" means the request timed out or the connection was refused from outside Peru. Several Peruvian government sites did this (enfen.gob.pe, inei.gob.pe, met.igp.gob.pe, geo.midis.gob.pe). They may block foreign IPs or be down, so they are not necessarily gone. For Google Earth Engine (GEE), an ID counts as verified only if its official catalog page (developers.google.com/earth-engine/datasets/catalog/<ID>) loaded and showed the snippet.

## Q1. Climate/ocean predictors, rainfall and river discharge (ICEN, Niño 1+2, ONI, SOI, SENAMHI, PISCO, CHIRPS, IMERG, ERA5/ERA5-Land, ANA, GloFAS)

### Takeaway
All the predictors are free. Ocean indices are plain-text files from NOAA (PSL/CPC). Rainfall grids are in GEE (CHIRPS v2 and v3, IMERG V07, ERA5-Land) or come from SENAMHI's PISCOp v2.1 at 0.1°. The two weak links are the ICEN download, whose historical IGP URL now returns 404, and station data from SENAMHI and ANA, which comes through web portals or formal requests rather than an API. GloFAS reanalysis (0.05°, daily, 1979 to near real time, now v5.0) is the most practical source for discharge features.

### Cited Findings
**Ocean/ENSO indices**
- The ICEN is computed from NOAA ERSSTv5 sea surface temperature averaged over the Niño 1+2 region. The official, definitive statement comes from the ENFEN multisectoral commission. IGP also publishes an "ICEN relativo" (ICENr) that uses the 1991–2020 climatology — [IGP repository (technical reports)](https://repositorio.igp.gob.pe/bitstreams/93965b32-761c-474c-99bc-7f8cb317876b/download)
- An older IGP report gave `http://www.met.igp.gob.pe/datos/icen.txt` as the download. On 2026-11-10 that URL returned an Apache "404 Not Found", and https://www.met.igp.gob.pe and https://www.enfen.gob.pe were unreachable (000) — [IGP report referencing icen.txt](https://repositorio.igp.gob.pe/bitstreams/93965b32-761c-474c-99bc-7f8cb317876b/download); checked directly at [met.igp.gob.pe/datos/icen.txt](http://met.igp.gob.pe/datos/icen.txt)
- The latest ICEN value a search turned up was from October 2025: Neutral, –0.42. It is out of date as of Nov 2026 — [IGP repository](https://repositorio.igp.gob.pe/bitstreams/c90f7225-a84a-4921-b8b1-ceb45bcec7f5/download)
- ERSST v5 (monthly, 2°, 1854–present) is distributed by NOAA NCEI and NOAA PSL (NetCDF via THREDDS/OPeNDAP). It is not in the official GEE catalog: the `NOAA_ERSST_V5` catalog page returns 404 — [NCEI ERSST](https://www.ncei.noaa.gov/products/extended-reconstructed-sst); [PSL ERSST v5](https://psl.noaa.gov/data/gridded/data.noaa.ersst.v5.html)
- NOAA OISST v2.1 (daily, 1/4°, pixel ~27.8 km, 1981-09-01 to 2026-11-07 at time of check, bands `sst` and `anom`) is in GEE as `ee.ImageCollection("NOAA/CDR/OISST/V2_1")` — [GEE catalog](https://developers.google.com/earth-engine/datasets/catalog/NOAA_CDR_OISST_V2_1); [NCEI OISST](https://www.ncei.noaa.gov/products/optimum-interpolation-sst)
- Ready-made monthly index files (verified 200):
  - CPC Niño 1+2/3/3.4/4 with anomalies: https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices
  - CPC ONI: https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt
  - CPC SOI: https://www.cpc.ncep.noaa.gov/data/indices/soi
  - PSL Niño 1+2 (from 1948): https://psl.noaa.gov/data/correlation/nina1.data
  - PSL ONI: https://psl.noaa.gov/data/correlation/oni.data
  - PSL SOI: https://psl.noaa.gov/data/correlation/soi.data
  - [PSL climate index list](https://www.psl.noaa.gov/data/climateindices/list/); [CPC ONI table](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ONI_v5.php)
- Current conditions as fetched on 2026-11-10:
  - The CPC ONI file's last row is ASO 2026 with an anomaly of +2.46 °C.
  - CPC `sstoi.indices` lists October 2026 at 26.12 °C, a +5.25 °C anomaly, in Niño 1+2, and at 30.01 °C (+3.25) in Niño 3.4.
  - So a strong, ongoing El Niño event is in the data the model would use for 2027 — [CPC oni.ascii.txt](https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt); [CPC sstoi.indices](https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices)

**Rainfall**
- PISCOp V2.1 (Aybar et al. 2020, *Hydrological Sciences Journal*, DOI 10.1080/02626667.2019.1649411) covers 1981 to the present at 0.1°, with about 8 weeks of latency. It merges:
  - quality-controlled, gap-filled national gauges
  - radar-gauge climatologies
  - CHIRP satellite estimates

  — [SENAMHI repository](https://repositorio.senamhi.gob.pe/handle/20.500.12542/288)
- The PISCO project site links to Spanish and English pages and to the gap-filling code on GitHub — [piscoprec.github.io](https://piscoprec.github.io/) → [webPISCO EN](https://piscoprec.github.io/webPISCO/en/); [gap-fill code](https://github.com/csaybar/PISCOp)
- PISCO in the IRI Data Library:
  - v2p1 is mirrored at https://iridl.ldeo.columbia.edu/SOURCES/.SENAMHI/.HSR/.PISCO/.Prec/.v2p1/
  - Per the IRIDL overview, the "stable" daily series covers 1 Jan 1981–31 Dec 2016 and the "unstable" monthly series ran to May 2025.
  - On 2026-11-10 IRIDL showed "The Data Library now requires all users to sign in" (free account).

  — [IRIDL PISCO v2p1 overview](https://iridl.ldeo.columbia.edu/SOURCES/.SENAMHI/.HSR/.PISCO/.Prec/.v2p1/overview.html)
- The SENAMHI PISCO landing page loads (200) — [senamhi.gob.pe/?p=pisco](https://www.senamhi.gob.pe/?p=pisco)
- Rainfall in GEE (all catalog pages verified):
  - CHIRPS v2 daily: `UCSB-CHG/CHIRPS/DAILY`. Pixel ~5.6 km (0.05°), 1981-01-01 to 2026-09-30.
  - CHIRPS v2 pentad: `UCSB-CHG/CHIRPS/PENTAD`.
  - CHIRPS v3 daily: `UCSB-CHC/CHIRPS/V3/DAILY_RNL` (reanalysis, 1981-01-01 to 2026-09-30, public domain) and `UCSB-CHC/CHIRPS/V3/DAILY_SAT` (near real time).
  - GPM IMERG V07 half-hourly: `NASA/GPM_L3/IMERG_V07`, ~11 km (0.1°), 1998-01-01 to near real time. V06 is deprecated.
  - IMERG monthly: `NASA/GPM_L3/IMERG_MONTHLY_V07`.
  - ERA5-Land daily: `ECMWF/ERA5_LAND/DAILY_AGGR`, ~11 km, 1950 to about 1 week ago. Hourly is `ECMWF/ERA5_LAND/HOURLY` and monthly is `ECMWF/ERA5_LAND/MONTHLY_AGGR`.
  - ERA5: `ECMWF/ERA5/DAILY` and `ECMWF/ERA5/MONTHLY`.

  — [CHIRPS daily](https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHG_CHIRPS_DAILY); [CHIRPS v3 RNL](https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHC_CHIRPS_V3_DAILY_RNL); [IMERG V07](https://developers.google.com/earth-engine/datasets/catalog/NASA_GPM_L3_IMERG_V07); [ERA5-Land daily](https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_LAND_DAILY_AGGR)
- Downloading CHIRPS outside GEE:
  - The v3 directory loads: https://data.chc.ucsb.edu/products/CHIRPS/v3.0/daily/
  - The old v2 path `https://data.chc.ucsb.edu/products/CHIRPS-2.0/` returned 404 on 2026-11-10, so it has been moved or reorganized.

  — [CHC CHIRPS3 page](https://www.chc.ucsb.edu/data/chirps3)
- ERA5-Land and ERA5 originals are on the new Copernicus CDS (free account, licence acceptance, `cdsapi`). ERA5-Land is subject to the Copernicus C3S/CAMS licence, which requires attribution — [CDS ERA5-Land](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land); [GEE ERA5-Land terms](https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_LAND_DAILY_AGGR)
- GPM IMERG originals are on NASA GES DISC (Earthdata login) — [gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/](https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/); [GPM IMERG](https://gpm.nasa.gov/data/imerg)
- SENAMHI station data is reachable through three routes:
  - Station viewer "Datos hidrometeorológicos": https://www.senamhi.gob.pe/?p=estaciones (200)
  - Formal request form: https://www.senamhi.gob.pe/?p=solicitud-servicio
  - Spatial data infrastructure IDESEP: https://idesep.senamhi.gob.pe/portalidesep/ (200)

  The "Descarga de datos" page itself showed only a heading and no file list — [SENAMHI descarga](https://www.senamhi.gob.pe/site/descarga-datos/)

**River discharge**
- GloFAS historical reanalysis on EWDS:
  - v5.0 is operational, released 2026-07-15. Each major release republishes the reanalysis.
  - Resolution is 0.05° (v4 and v5), daily, 1 Jan 1979 to near real time.
  - Variables: river discharge (m³/s), runoff, snow depth water equivalent, soil wetness index. Ancillary elevation and upstream area are included.
  - Formats are GRIB2 and NetCDF-4, under the CEMS-FLOODS licence.
  - It is modeled data (LISFLOOD forced by ERA5), with an "intermediate" stream (ERA5T, daily update) and a "consolidated" stream (monthly update).

  — [EWDS cems-glofas-historical](https://ewds.climate.copernicus.eu/datasets/cems-glofas-historical); [GloFAS portal](https://www.globalfloods.eu/)
- ANA's SNIRH (Sistema Nacional de Información de Recursos Hídricos) and its observatory both load: https://snirh.ana.gob.pe/ and https://snirh.ana.gob.pe/onrh/ (200). An older visor path, `/visors2/`, returns 404 — [SNIRH](https://snirh.ana.gob.pe/); [ANA](https://www.ana.gob.pe/)

### Inferences
- **ICEN target or predictor:** Rebuild ICEN yourself. Take the 3-month running mean of ERSSTv5 Niño 1+2 anomalies from PSL or NCEI rather than relying on the dead IGP text file. Cross-check the official monthly values against ENFEN's "Comunicado Oficial" PDFs, and access those from a Peruvian IP if needed.
- **Feature mapping:**
  - Use ICEN, Niño 1+2 anomaly, ONI and SOI as event-level or seasonal features (Dec–Apr) shared by all grid cells in a season.
  - Use PISCO, CHIRPS or IMERG accumulations (max 1/3/5-day, seasonal total, anomaly vs. climatology) as cell-level hazard drivers.
  - Use GloFAS discharge maximum and return-period exceedance at the nearest river cell as a riverine driver.
- **Which rainfall product:** IMERG's half-hourly data suits flash-flood timing. PISCO best matches SENAMHI gauges. CHIRPS v2 and v3 give the longest consistent satellite series in GEE. Using two products and comparing them makes the model more robust.

### Gaps
- I could not confirm a current, machine-readable official ICEN download URL. ENFEN and met.igp.gob.pe were unreachable, and the old icen.txt is 404.
- Official ENFEN ICEN category thresholds (débil/moderado/fuerte/extraordinario) were not retrieved in this session. Check the ENFEN Nota Técnica before using them as labels.
- I did not confirm whether PISCOp v2.1 daily data after 2016 or any newer version (e.g., a v2.2/v3) is publicly downloadable beyond IRIDL. The piscoprec.github.io root page did not list products.
- The format and download mechanics of SENAMHI and ANA hydrometric station data (CSV per station? daily discharge for the Chira, Piura, Tumbes, Zaña, Chancay-Lambayeque, Moche and Santa rivers?) were not verified. The viewers load, but their content was not inspected.
- The EWDS cdsapi endpoint and request syntax for GloFAS were not shown on the dataset page.
- A Peru/Ecuador watershed rainfall dataset (1981–2015, likely RAIN4PE) appears in the GEE community catalog navigation. Its asset ID was not checked.

## Q2. Terrain/hydrology features (DEMs, HydroSHEDS/MERIT Hydro, HAND, flow accumulation, distance to river, slope, TWI, soils, land cover, NDVI)

### Takeaway
Every terrain layer is available in GEE. Use the Copernicus GLO-30 2024 release, SRTM, ALOS v4.1 or FABDEM (community catalog) for 30 m elevation, and MERIT Hydro (~90 m) for flow direction, upstream area and HAND-type features. Two IDs have changed: `COPERNICUS/DEM/GLO30` is deprecated in favor of `COPERNICUS/DEM/GLO30_2024_1`, and the old WorldPop IDs are deprecated too (see Q3).

### Cited Findings
- **DEMs:**
  - `USGS/SRTMGL1_003` is SRTM 30 m — [GEE](https://developers.google.com/earth-engine/datasets/catalog/USGS_SRTMGL1_003)
  - `COPERNICUS/DEM/GLO30` is marked "[deprecated]… superseded by COPERNICUS/DEM/GLO30_2024_1". The new collection, `ee.ImageCollection("COPERNICUS/DEM/GLO30_2024_1")`, covers acquisitions from 2010-12 to 2020-11. GLO-30 is a Digital Surface Model, free worldwide except Armenia and Azerbaijan. Its auxiliary bands are EDM (edit mask) and FLM (filling mask) — [GEE GLO30 (deprecated)](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_DEM_GLO30); [GEE GLO30_2024_1](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_DEM_GLO30_2024_1)
  - `JAXA/ALOS/AW3D30/V4_1` is a 30 m DSM from 2006–2011 acquisitions, heights relative to the EGM96 geoid. V3_2 is deprecated — [GEE ALOS V4.1](https://developers.google.com/earth-engine/datasets/catalog/JAXA_ALOS_AW3D30_V4_1)
  - FABDEM (Copernicus DEM with forests and buildings removed) is in the GEE community catalog as `projects/sat-io/open-datasets/FABDEM`. Licence CC BY-NC-SA 4.0 (non-commercial, share-alike). The original is hosted at the University of Bristol data repository — [GEE community catalog: FABDEM](https://gee-community-catalog.org/projects/fabdem/); [Bristol data.bris](https://data.bris.ac.uk/data/dataset/s5hqmjcdj8yo2ibzi9b4ew3sn)
- **Hydrography:**
  - `MERIT/Hydro/v1_0_1` (pixel 92.77 m) has the bands `elv`, `dir` (D8 flow direction), upstream drainage area, river width and HAND. It is free; citation is enough for ordinary use — [GEE MERIT Hydro](https://developers.google.com/earth-engine/datasets/catalog/MERIT_Hydro_v1_0_1); [MERIT Hydro site](https://hydro.iis.u-tokyo.ac.jp/~yamadai/MERIT_Hydro/)
  - `MERIT/DEM/v1_0_3` is also in GEE — [GEE](https://developers.google.com/earth-engine/datasets/catalog/MERIT_DEM_v1_0_3)
  - HydroSHEDS in GEE includes:
    - `WWF/HydroSHEDS/03VFDEM` (void-filled DEM, 3″)
    - `WWF/HydroSHEDS/15ACC` (flow accumulation, 15″)
    - `WWF/HydroSHEDS/v1/FreeFlowingRivers` (river network)
    - `WWF/HydroSHEDS/v1/Basins/hybas_12` (basins)
    - `WWF/HydroATLAS/v1/Basins/level12` (basin attributes)

    — [GEE 03VFDEM](https://developers.google.com/earth-engine/datasets/catalog/WWF_HydroSHEDS_03VFDEM); [15ACC](https://developers.google.com/earth-engine/datasets/catalog/WWF_HydroSHEDS_15ACC); [FreeFlowingRivers](https://developers.google.com/earth-engine/datasets/catalog/WWF_HydroSHEDS_v1_FreeFlowingRivers); [HydroATLAS L12](https://developers.google.com/earth-engine/datasets/catalog/WWF_HydroATLAS_v1_Basins_level12); [hydrosheds.org](https://www.hydrosheds.org/)
- **HAND:** Global HAND is in the community catalog as `users/gena/GlobalHAND/30m/hand-1000`, `users/gena/GlobalHAND/90m-global/hand-1000` and `users/gena/global-hand/hand-100`, under CC BY 4.0 — [GEE community catalog: HAND](https://gee-community-catalog.org/projects/hand/)
- **Soils:** SoilGrids is in the community catalog under `projects/soilgrids-isric/<property>_mean`, with clay, sand, silt, bdod, cec, cfvo, soc, ocd, ocs, phh2o and nitrogen. OpenLandMap soil texture class is in the official catalog as `OpenLandMap/SOL/SOL_TEXTURE-CLASS_USDA-TT_M/v02`. Originals come from ISRIC — [GEE community catalog: ISRIC](https://gee-community-catalog.org/projects/isric/); [OpenLandMap texture](https://developers.google.com/earth-engine/datasets/catalog/OpenLandMap_SOL_SOL_TEXTURE-CLASS_USDA-TT_M_v02); [soilgrids.org](https://soilgrids.org); [maps.isric.org (WCS/WMS)](https://maps.isric.org/)
- **Land cover:**
  - ESA WorldCover 10 m: `ESA/WorldCover/v100` for 2020 and `ESA/WorldCover/v200` for 2021 — [GEE v200](https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v200); [esa-worldcover.org](https://esa-worldcover.org/en)
  - Dynamic World (`GOOGLE/DYNAMICWORLD/V1`) is a near-real-time 10 m alternative — [GEE](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1)
  - MapBiomas Perú Collection 3 covers 1985–2024 with 26 classes and was published in June 2025. Its GEE assets are `projects/mapbiomas-public/assets/peru/collection3/mapbiomas_peru_collection3_integration_v1` (one band per year, `classification_<year>`) and `…_transitions_v1`. Annual GeoTIFFs can be downloaded from Google Storage — [MapBiomas Perú collections/downloads](https://peru.mapbiomas.org/en/colecciones-de-mapbiomas-peru/); [factsheet](https://peru.mapbiomas.org/wp-content/uploads/sites/14/2025/06/FACTSHEET-GENERAL-COBERTURA-Y-USO-DE-SUELO-.pdf); [GEE tools page](https://peru.mapbiomas.org/en/?p=121)
- **NDVI and imagery:**
  - MODIS `MODIS/061/MOD13Q1` (16-day, 250 m) and `MODIS/061/MOD13A1` (500 m) — [GEE MOD13Q1](https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD13Q1)
  - Sentinel-2 L2A `COPERNICUS/S2_SR_HARMONIZED` for 10 m NDVI — [GEE](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED)
- **Permanent water / distance to water:** JRC Global Surface Water v1.4 has two layers: `JRC/GSW1_4/GlobalSurfaceWater` (occurrence, seasonality) and `JRC/GSW1_4/MonthlyHistory` — [GEE GSW](https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_GlobalSurfaceWater); [MonthlyHistory](https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_MonthlyHistory)
- **Official geological susceptibility:** INGEMMET publishes an ArcGIS REST service, "Susceptibilidad a inundación fluvial" — [geocatmin MapServer](https://geocatmin.ingemmet.gob.pe/arcgis/rest/services/SERV_SUSCEPTIBILIDAD_INUNDACION_FLUVIAL_MIL1/MapServer)

### Inferences
- **Deriving the features:**
  - **slope** = `ee.Terrain.slope(DEM)`
  - **flow accumulation / upstream area** comes from MERIT Hydro `upa` or HydroSHEDS 15ACC.
  - **TWI** = ln(upa / tan(slope)), computed at a common 30 m or 90 m grid.
  - **distance to river** = `fastDistanceTransform` on a channel mask (MERIT `upa` > threshold, or OSM waterways).
  - **HAND** comes from MERIT Hydro or the community HAND layers.
  - **elevation above sea level / distance to coast** catches coastal pluvial ponding in Piura and Lambayeque.
- **Choosing a DEM:** All the 30 m products except FABDEM are DSMs. On the irrigated, urban coastal plain, buildings and tree lines distort low-relief drainage. FABDEM fixes this but is non-commercial, which is acceptable for a student project. SRTM is a fine baseline for a coastal desert.
- **What land cover adds:** Impervious or urban classes (WorldCover/MapBiomas) affect runoff. Agricultural classes help explain flood labels along the Chira and Piura valleys.
- **Static vs. dynamic:** Pre-event NDVI is mostly a static land-use proxy. A post-event NDVI drop can serve as a weak flood label.

### Gaps
- I did not verify inside GEE that the MapBiomas Perú Collection 3 asset IDs are publicly readable. That needs an authenticated GEE session.
- The exact resolution and units of the community-catalog HAND and SoilGrids layers were not extracted beyond their asset paths and licences.
- INGEMMET's service scale ("MIL1" suggests 1:1,000,000) and attribute meaning were not inspected.

## Q3. Exposure/vulnerability (INEI Censos 2017 & 2025, poverty, WorldPop, GHSL, OSM/buildings, MIDIS, GeoPerú, IDEP)

### Takeaway
Use the 2017 census through REDATAM or microdata for district and block attributes. The 2025 census released its first results on 29 May 2026 and is publishing district results in stages. For population grids, use the current WorldPop R2025A (2015–2030) and GHSL P2023A in GEE. For buildings and roads, use Google Open Buildings plus OSM from Geofabrik or HOT Export. Several INEI and MIDIS hosts did not respond from outside Peru.

### Cited Findings
- **2017 census:** Census 2017 REDATAM (https://censos2017.inei.gob.pe/redatam/) and the INEI microdata portal (https://proyectos.inei.gob.pe/microdatos/) both load (200) — [REDATAM](https://censos2017.inei.gob.pe/redatam/); [Microdatos](https://proyectos.inei.gob.pe/microdatos/)
- **Censos Nacionales 2025:**
  - First results were presented on 29 May 2026: total population 34,157,732 — [INEI note on gob.pe](https://www.gob.pe/institucion/inei/noticias/1399446-inei-poblacion-del-peru-totalizo-34-millones-157-mil-732-habitantes-al-2025); [El Peruano](https://www.elperuano.pe/noticia/296656-inei-primeros-resultados-de-los-censos-nacionales-2025-se-daran-a-conocer-este-viernes-29-de-mayo)
  - A provincial/district results presentation is dated July 2026 — [INEI presentation](https://sistemas.inei.gob.pe/dir-segmentacion-ci/postcensal/prod/adjuntos/publicaciones/Presentacion_resultados.pdf)
  - Regional releases continue, e.g., Cusco on 4 Aug 2026 — [INEI Cusco](https://www.gob.pe/institucion/inei/noticias/1426058-inei-poblacion-de-cusco-registro-1-millon-379-mil-habitantes-segun-resultados-de-los-censos-nacionales-2025)
  - The census site https://censos2025.inei.gob.pe loads (200), but https://www.inei.gob.pe timed out (000). Earlier timelines (results within ~5 months of fieldwork) slipped — [RPP](https://rpp.pe/peru/actualidad/censo-2025-resultados-preliminares-se-conoceran-en-marzo-del-proximo-ano-noticia-1630391)
- **WorldPop:**
  - `WorldPop/GP/100m/pop` (2000–2020) is now "[deprecated]… superseded by WorldPop/GP/100m/R2025A/v1/pop".
  - The new `ee.ImageCollection("WorldPop/GP/100m/R2025A/v1/pop")` covers 2015 to 2030 (availability listed 2015-01-01 to 2031-01-01).
  - Licence CC BY 4.0. Age/sex structure is in `WorldPop/GP/100m/pop_age_sex`.

  — [GEE WorldPop (deprecated)](https://developers.google.com/earth-engine/datasets/catalog/WorldPop_GP_100m_pop); [GEE R2025A](https://developers.google.com/earth-engine/datasets/catalog/WorldPop_GP_100m_R2025A_v1_pop); [WorldPop hub](https://hub.worldpop.org/geodata/listing?id=29)
- **GHSL:** `JRC/GHSL/P2023A/GHS_POP` (1975–2030) and `JRC/GHSL/P2023A/GHS_BUILT_S` (built-up surface) — [GEE GHS_POP](https://developers.google.com/earth-engine/datasets/catalog/JRC_GHSL_P2023A_GHS_POP); [GHS_BUILT_S](https://developers.google.com/earth-engine/datasets/catalog/JRC_GHSL_P2023A_GHS_BUILT_S); [GHSL download](https://human-settlement.emergency.copernicus.eu/download.php)
- **Buildings:** Google Open Buildings V3 polygons are `GOOGLE/Research/open-buildings/v3/polygons` (CC BY 4.0, dated 2023-05-30). There is also Open Buildings Temporal V1 — [GEE V3](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_Research_open-buildings_v3_polygons); [Temporal V1](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_Research_open-buildings-temporal_v1)
- **OSM:** Geofabrik Peru extract (https://download.geofabrik.de/south-america/peru.html) and HOT Export Tool (https://export.hotosm.org/), both 200 — [Geofabrik](https://download.geofabrik.de/south-america/peru.html); [HOT Export](https://export.hotosm.org/)
- **Admin boundaries:**
  - FAO GAUL 2015 level 2 in GEE: `FAO/GAUL/2015/level2` — [GEE](https://developers.google.com/earth-engine/datasets/catalog/FAO_GAUL_2015_level2)
  - HDX COD-AB Peru: https://data.humdata.org/dataset/cod-ab-per
  - geoBoundaries: https://www.geoboundaries.org/
- **Peruvian geo-portals:**
  - GeoPerú (https://www.geoperu.gob.pe), IDEP (https://www.idep.gob.pe), datosabiertos.gob.pe and MINAM's Geoservidor (https://geoservidor.minam.gob.pe) all load (200).
  - MIDIS's geo.midis.gob.pe and REDinforma (sdv.midis.gob.pe) timed out (000).

  — [GeoPerú](https://www.geoperu.gob.pe); [IDEP](https://www.idep.gob.pe); [Datos Abiertos](https://www.datosabiertos.gob.pe)

### Inferences
- **Mapping to the model:** Exposure and vulnerability usually do not belong among the hazard predictors for a "flood-prone zone" model. They are used to:
  - (a) weight or interpret risk (hazard × exposure)
  - (b) correct label bias, since emergency records cluster where people and assets are.

  Useful district features are 2017/2025 population, % precarious housing materials, % without piped drainage and poverty rate. Useful cell features are WorldPop/GHSL population and building density from Open Buildings.
- **Joining census data:** Use the 6-digit INEI UBIGEO code as the key to join census, poverty and INDECI records. GAUL 2015 is older and lacks UBIGEO. Prefer INEI or GeoPerú district limits, or HDX COD-AB.

### Gaps
- I could not reach INEI's poverty map publication (*Mapa de Pobreza Monetaria Provincial y Distrital 2018*) because inei.gob.pe timed out. Its URL and availability, and whether a newer district poverty map exists, are unverified.
- Whether 2025 census microdata or REDATAM are already public by district, and under what terms, was not confirmed.
- I did not verify whether Open Buildings V3 actually covers coastal Peru. Check the coverage layer in GEE.
- The MIDIS datasets (e.g., Padrón General de Hogares / SISFOH, REDinforma district indicators) could not be accessed or described.

## Q4. Flood ground truth / labels (INDECI SINPAD, CENEPRED SIGRID, DesInventar, Sentinel-1/Copernicus EMS/UNOSAT/Charter, Global Flood Database, DFO)

### Takeaway
No single clean label set exists, and you have to put one together:

- **Polygons (maps of flooded areas):**
  - 2017 Copernicus EMS EMSR199
  - 2023 International Charter activation 811 (Cyclone Yaku) and the UNOSAT FL20230315PER report
  - Global Flood Database (MODIS, 2000–2018, CC BY-NC)
  - your own Sentinel-1 flood maps in GEE
- **District-event counts:** INDECI and DesInventar.

CENEPRED SIGRID has the best official susceptibility layers, but layer download needs a registered SIGRID user. Old SINPAD URLs now return 404.

### Cited Findings
- **Global Flood Database:**
  - `ee.ImageCollection("GLOBAL_FLOOD_DB/MODIS_EVENTS/V1")` covers 2000-02-17 to 2018-12-10 and was produced by Cloud to Street and the Dartmouth Flood Observatory.
  - Bands: `flooded` (maximum extent, 0/1) and `duration` (days).
  - Licence CC BY-NC 4.0. Cite Tellman et al.

  — [GEE GFD](https://developers.google.com/earth-engine/datasets/catalog/GLOBAL_FLOOD_DB_MODIS_EVENTS_V1); [GFD site](https://global-flood-database.cloudtostreet.ai/)
- **Dartmouth Flood Observatory:** The DFO home page loads (https://floodobservatory.colorado.edu/), but the historical archive paths `/Archives/index.html` and `/Archives/MasterListrev.htm` returned 404 on 2026-11-10, so the event archive has moved or is unreliable — [DFO](https://floodobservatory.colorado.edu/)
- **Copernicus EMS EMSR199:** Peru flood activation, event time 2017-03-22, status closed. The current portal page is https://mapping.emergency.copernicus.eu/activations/EMSR199/ (200), with legacy https://rapidmapping.emergency.copernicus.eu/EMSR199 (200). The old `emergency.copernicus.eu/mapping/list-of-components/EMSR199` URL now returns 404 — [CEMS activations](https://mapping.emergency.copernicus.eu/activations/); [EMSR199](https://mapping.emergency.copernicus.eu/activations/EMSR199/)
- **2023 EMS activation:** A search found no Copernicus EMS rapid-mapping activation for Peru floods in 2023 — [search context: copernicus.eu](https://www.copernicus.eu/en/node/853)
- **International Charter activation 811, "Flood large in Peru" (Cyclone Yaku):**
  - Activated 14 March 2023, requested by USGS on behalf of INDECI and CONIDA; project manager José Pasapera (CONIDA).
  - 24 products dated 22–24 March and 11 April 2023, including "Preliminary Flood Mapping after Cyclone Yaku in North Peru", "Areas affected by flooding in Tumbes" and "Identification of flooded areas in Changoyape, Lambayeque".
  - Context: a state of emergency in 400 districts of Lambayeque, Piura and Tumbes.

  — [Disasters Charter activation 811](https://disasterscharter.org/web/guest/activations/-/article/flood-large-in-peru-activation-811-); [UN-SPIDER note](https://un-spider.org/es/node/10947)
- **UNOSAT FL20230315PER:** A preliminary assessment report dated 21 March 2023 covers Tumbes, Piura, Lambayeque and La Libertad. It notes flooded farmland along the Chira river in Paita and Sullana — [UNOSAT PDF](https://unosat.org/static/unosat_filesystem/3539/UNOSAT_Preliminary_Assessment_Report_FL20230315PER_20230221.pdf); [UNOSAT products](https://unosat.org/products/)
- **Sentinel-1 for your own flood maps:** `COPERNICUS/S1_GRD` (C-band GRD, log scale) is in GEE — [GEE S1 GRD](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD)
- **CENEPRED SIGRID:**
  - SIGRID v3 loads at https://sigrid.cenepred.gob.pe/sigridv3/ with a map viewer at /sigridv3/mapa (both 200).
  - According to the SIGRID user manual, public users are limited to downloading 5 administrative records per day and cannot download layers. Downloading layers needs a SIGRID user profile, which you request on the platform.
  - The library groups layers as "Cartografía riesgos", "Cartografía peligros", "Información complementaria", etc.

  — [SIGRID](https://sigrid.cenepred.gob.pe/sigridv3/); [Manual de usuario SIGRID (PDF)](https://sigrid.cenepred.gob.pe/sigridv3/docs/MANUAL-DE-USUARIO-DEL-SIGRID.pdf)
- **INDECI:**
  - Legacy SINPAD hosts return 404 (`https://sinpad.indeci.gob.pe`, `/PortalSINPAD/`, `/sinpad/emergencias/`).
  - INDECI's current emergencies portal https://portal.indeci.gob.pe/emergencias/ loads (200), as does https://www.gob.pe/indeci.
  - A datosabiertos.gob.pe search for "emergencias y daños" returned no INDECI-attributed dataset.

  — [INDECI emergencias](https://portal.indeci.gob.pe/emergencias/); [gob.pe/indeci](https://www.gob.pe/indeci); [datosabiertos search](https://www.datosabiertos.gob.pe/dataset/emergencias-y-da%C3%B1os)
- **DesInventar Perú:** The profile page loads (https://www.desinventar.net/DesInventar/profiletab.jsp?countrycode=per). The download page (`download_base.jsp?countrycode=per`) timed out — [DesInventar Perú](https://www.desinventar.net/DesInventar/profiletab.jsp?countrycode=per)
- **INGEMMET fluvial flood susceptibility layer** (see Q2): an alternative official "prone-zone" layer that is openly served — [geocatmin](https://geocatmin.ingemmet.gob.pe/arcgis/rest/services/SERV_SUSCEPTIBILIDAD_INUNDACION_FLUVIAL_MIL1/MapServer)

### Inferences
- **Suggested label strategy:**
  - (1) Pixel/cell label: flooded = 1 if Sentinel-1 change detection shows new water during the Mar 2017 (Niño Costero) or Mar 2023 (Yaku) peaks, minus JRC permanent water. Validate against the EMSR199 and Charter 811 polygons and UNOSAT.
  - (2) District label: number or occurrence of INDECI/DesInventar "inundación" events per season, to train or validate an aggregated model.
  - (3) CENEPRED or INGEMMET susceptibility maps should be a benchmark to compare against, not training labels, to avoid learning a prior map.
- **Gaps in GFD coverage:** GFD starts in 2000 and ends in 2018. It cannot include the 1997–98 El Niño, might include the 2017 Niño Costero (not checked), and misses 2023 entirely. MODIS (250 m native) also misses narrow riverine and urban flooding. Treat it as supplementary.
- **Sentinel-1 timing:** Sentinel-1A began in 2014, so the 1983 and 1997–98 extreme El Niño floods cannot be mapped with SAR. Labels for those events would have to come from DesInventar/INDECI records or historical reports.

### Gaps
- No direct-download format or URL for EMSR199 vector packages was inspected, and neither were the Charter 811 product files. The Charter page lists products but not download links.
- An open bulk export of INDECI emergency records by district (CSV/API) was not found. One may exist on the new INDECI portal or via a transparency request.
- Whether GFD includes a mapped event for Peru in 2017 was not checked.
- The DesInventar Peru database's temporal coverage and last update were not retrieved (the download page timed out).

## Q5. Access methods: Google Earth Engine IDs, Python (xarray, rasterio, geopandas, earthengine-api, cdsapi), R

### Takeaway
GEE alone covers most predictors, terrain features and SAR labels, using the verified IDs listed in Q1–Q4. Use cdsapi for CDS (ERA5/ERA5-Land) and EWDS (GloFAS), plain HTTP for the NOAA index text files, and manual or registered portal downloads for SENAMHI, ANA, SIGRID and INDECI.

### Cited Findings
- **Verified official GEE IDs** (catalog pages returned 200 on 2026-11-10):
  - `NOAA/CDR/OISST/V2_1`
  - `UCSB-CHG/CHIRPS/DAILY`
  - `UCSB-CHG/CHIRPS/PENTAD`
  - `UCSB-CHC/CHIRPS/V3/DAILY_RNL`
  - `UCSB-CHC/CHIRPS/V3/DAILY_SAT`
  - `NASA/GPM_L3/IMERG_V07`
  - `NASA/GPM_L3/IMERG_MONTHLY_V07`
  - `ECMWF/ERA5_LAND/DAILY_AGGR`
  - `ECMWF/ERA5_LAND/HOURLY`
  - `ECMWF/ERA5_LAND/MONTHLY_AGGR`
  - `ECMWF/ERA5/DAILY`
  - `ECMWF/ERA5/MONTHLY`
  - `USGS/SRTMGL1_003`
  - `COPERNICUS/DEM/GLO30_2024_1`
  - `JAXA/ALOS/AW3D30/V4_1`
  - `MERIT/Hydro/v1_0_1`
  - `MERIT/DEM/v1_0_3`
  - `WWF/HydroSHEDS/03VFDEM`
  - `WWF/HydroSHEDS/15ACC`
  - `WWF/HydroSHEDS/v1/FreeFlowingRivers`
  - `WWF/HydroSHEDS/v1/Basins/hybas_12`
  - `WWF/HydroATLAS/v1/Basins/level12`
  - `ESA/WorldCover/v200`
  - `ESA/WorldCover/v100`
  - `GOOGLE/DYNAMICWORLD/V1`
  - `MODIS/061/MOD13Q1`
  - `MODIS/061/MOD13A1`
  - `COPERNICUS/S2_SR_HARMONIZED`
  - `COPERNICUS/S1_GRD`
  - `OpenLandMap/SOL/SOL_TEXTURE-CLASS_USDA-TT_M/v02`
  - `GLOBAL_FLOOD_DB/MODIS_EVENTS/V1`
  - `JRC/GSW1_4/GlobalSurfaceWater`
  - `JRC/GSW1_4/MonthlyHistory`
  - `WorldPop/GP/100m/R2025A/v1/pop`
  - `WorldPop/GP/100m/pop_age_sex`
  - `JRC/GHSL/P2023A/GHS_POP`
  - `JRC/GHSL/P2023A/GHS_BUILT_S`
  - `GOOGLE/Research/open-buildings/v3/polygons`
  - `GOOGLE/Research/open-buildings-temporal/v1`
  - `FAO/GAUL/2015/level2`

  — [GEE Data Catalog](https://developers.google.com/earth-engine/datasets/catalog)
- **Deprecated official IDs:**
  - `COPERNICUS/DEM/GLO30` → use `GLO30_2024_1`
  - `WorldPop/GP/100m/pop` → use `R2025A/v1/pop`
  - `NASA/GPM_L3/IMERG_V06` → use V07
  - `JAXA/ALOS/AW3D30/V3_2` → use V4_1

  — [GEE GLO30](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_DEM_GLO30); [GEE WorldPop](https://developers.google.com/earth-engine/datasets/catalog/WorldPop_GP_100m_pop)
- **Not in the official catalog** (catalog 404): ERSST v5, FABDEM, HAND, SoilGrids and PISCO. FABDEM, HAND and SoilGrids are in the community catalog (`projects/sat-io/open-datasets/FABDEM`, `users/gena/GlobalHAND/30m/hand-1000`, `projects/soilgrids-isric/*_mean`). I found no community-catalog page for PISCO or GloFAS — [GEE community catalog](https://gee-community-catalog.org/)
- **Community MapBiomas Perú asset** (from MapBiomas): `projects/mapbiomas-public/assets/peru/collection3/mapbiomas_peru_collection3_integration_v1` — [MapBiomas Perú](https://peru.mapbiomas.org/en/colecciones-de-mapbiomas-peru/)
- **Non-GEE sources:**
  - CDS ERA5-Land (needs a CDS account and licence acceptance) — [CDS](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land)
  - GloFAS on EWDS (GRIB2/NetCDF4) — [EWDS](https://ewds.climate.copernicus.eu/datasets/cems-glofas-historical)
  - IRIDL PISCO, which now requires a free sign-in — [IRIDL](https://iridl.ldeo.columbia.edu/SOURCES/.SENAMHI/.HSR/.PISCO/)
  - NASA GES DISC IMERG (Earthdata login) — [GES DISC](https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/)

### Inferences
- **Python stack:**
  - `earthengine-api` (`ee.Initialize(project=...)`; `ee.Image.reduceRegions` for zonal stats per district; `ee.batch.Export` to GeoTIFF or CSV) or `geemap`/`xee` to pull GEE data straight into xarray.
  - `cdsapi` for ERA5/ERA5-Land, and for GloFAS from the EWDS endpoint.
  - `xarray` + `netCDF4`/`cfgrib` for PISCO, ERSST, OISST and GloFAS.
  - `rioxarray`/`rasterio` for DEMs and SoilGrids COGs.
  - `geopandas` for SIGRID, OSM and INEI shapefiles.
  - `pysheds`, `whitebox` or `richdem` for local TWI/HAND/flow accumulation.
  - `pandas.read_fwf` for the CPC and PSL index text files.
- **R stack:** `rgee` for GEE, `ecmwfr` for CDS/EWDS, `terra`/`stars` for rasters, `sf` for vectors, `exactextractr` for zonal statistics.
- **Suggested modelling unit:** A 90 m or 250 m grid over the coastal strip of the five departments (e.g., below about 500 m elevation). Attach static terrain features and event-season rainfall/ENSO features, with 2017 and 2023 SAR-derived labels. Hold out one event for validation (train on 2017, test on 2023).

### Gaps
- The `xee`, `geemap` and EWDS API usage above is standard practice, but I did not verify it against current documentation in this session.

## Q6. Data quality issues (station gaps, PISCO biases, district aggregation, label imbalance)

### Takeaway
The main risks:

- Sparse and gappy gauges on the coast and foothills, which PISCO fills by merging with CHIRP.
- Version and stability splits in PISCO (stable daily only to 2016 on IRIDL).
- Modeled rather than observed discharge (GloFAS).
- DSM artifacts in DEMs.
- Labels that are biased toward populated districts and heavily imbalanced (flooded pixels are rare).
- Unreliable Peruvian portals (404s and timeouts).

### Cited Findings
- PISCOp merges gap-filled gauge data with radar-gauge climatologies and the CHIRP satellite product, so the gauges are incomplete and filled in. New data arrives about 8 weeks late — [SENAMHI repository, Aybar et al. 2020](https://repositorio.senamhi.gob.pe/handle/20.500.12542/288); [gap-fill code](https://github.com/csaybar/PISCOp)
- IRIDL separates "stable" daily PISCO (1981–2016) from an "unstable" monthly series (to May 2025), so a recent PISCO series is not homogeneous — [IRIDL v2p1 overview](https://iridl.ldeo.columbia.edu/SOURCES/.SENAMHI/.HSR/.PISCO/.Prec/.v2p1/overview.html)
- GloFAS discharge is model output (LISFLOOD + ERA5). Its "intermediate" ERA5T data is later superseded by consolidated data — [EWDS GloFAS](https://ewds.climate.copernicus.eu/datasets/cems-glofas-historical)
- Copernicus GLO-30 and ALOS AW3D30 are Digital Surface Models that include buildings and vegetation — [GEE GLO30](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_DEM_GLO30); [GEE ALOS](https://developers.google.com/earth-engine/datasets/catalog/JAXA_ALOS_AW3D30_V4_1)
- The GFD time window (2000–2018) excludes the 2023 Yaku floods, and its licence is non-commercial — [GEE GFD](https://developers.google.com/earth-engine/datasets/catalog/GLOBAL_FLOOD_DB_MODIS_EVENTS_V1)
- **Access limits:** SIGRID public users can download only 5 records per day and no layers — [SIGRID manual](https://sigrid.cenepred.gob.pe/sigridv3/docs/MANUAL-DE-USUARIO-DEL-SIGRID.pdf). Broken or changed URLs: legacy SINPAD (404), IGP icen.txt (404), DFO archive (404), CHIRPS-2.0 directory (404), plus enfen.gob.pe, inei.gob.pe and MIDIS timing out from outside Peru (my HTTP checks on 2026-11-10).

### Inferences
- **Station gaps:** Coastal desert gauges record near-zero rain in most years and extreme totals in El Niño years (1983, 1998, 2017, 2023). Gap-filling with climatology will damp extremes. Use max-N-day rainfall from at least two products (PISCO + IMERG/CHIRPS) and check them against raw SENAMHI station records for Piura, Chulucanas, Tumbes and Chiclayo where available.
- **Satellite and merged-product bias:** The infrared CHIRP component used by CHIRPS and PISCO tends to misrepresent warm-rain convection on the hyper-arid coast. Expect underestimation of El Niño coastal extremes. This is an inference to validate; I found no quantified source in this session.
- **District aggregation:** INDECI and DesInventar records are by district. Coastal districts mix flooded valley floors with dry desert, so a district label assigned to every pixel inflates false positives. Either model at district level, or use district counts only for weak supervision or validation.
- **Label imbalance:** SAR-flooded pixels will likely be below 5% of a coastal grid. Use stratified or balanced sampling, class weights, focal loss, or PR-AUC and F1 rather than accuracy, plus spatial cross-validation (block by basin) to avoid spatial leakage.
- **Reporting and exposure bias:** Emergency records reflect where people live and where reporting happens. Include population density as a covariate or apply an offset, and do not read "no record" as "no flood".
- **Mismatched scales and dates:** Resolutions range from 30 m DEMs to 0.25° OISST, and land cover, buildings and population grids are each from different years. Pick a target grid and document the resampling.

### Gaps
- I found no published, quantified PISCO bias for the northern coast during El Niño in this session. It needs a literature search (e.g., validation studies of PISCOp v2.1 and RAIN4PE).
- No source was retrieved on the share of missing data at specific SENAMHI coastal stations.
