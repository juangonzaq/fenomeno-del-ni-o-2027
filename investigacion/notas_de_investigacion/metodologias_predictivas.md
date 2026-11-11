# Predictive and analytical methodologies for flood-prone zones in Peru (ENSO-driven floods, northern coast, El Niño 2027)

Research date: 2026-11-10. Note: about 17 search/fetch calls. Items marked "UNVERIFIED" come from background knowledge and were not confirmed against a source in this session. The report writer should not state them as fact without checking.

**Critical context found during research (affects the whole project framing):** As of autumn 2026, ENFEN has an active **"Alerta de El Niño Costero"**. Comunicado Oficial ENFEN N° 16-2026 (14 Sep 2026) forecast that El Niño Costero (Niño 1+2) has its highest probability of **extraordinary** magnitude from Sep 2026 to Jan 2027, stays **between strong and extraordinary in Feb–Mar 2027**, and lasts until mid-autumn 2027. It also forecast Niño 3.4 as "very strong" from Sep 2026 to Jan 2027 and "strong" in Feb–Mar 2027. It expects above-normal rainfall on the northern coast in summer 2027, above-normal river flows in the northern Pacific basins mainly from November 2026, and possible moderate-to-strong rain episodes from November — [ENFEN Comunicado 16-2026](https://enfen.imarpe.gob.pe/download/comunicado-oficial-enfen-n-16-2026/). A search summary reports Comunicado N° 19-2026 (30 Oct 2026) keeps the alert in place and urges decision-makers to use updated risk-scenario studies. I did not verify its full text — [ENFEN home](https://enfen.imarpe.gob.pe/). So the "El Niño 2027" scenario is an event that is already under way, not a hypothetical one. The project can be framed as a real-time forecast for the Jan–Apr 2027 rainy season.

---

## 1. Flood susceptibility mapping methods (MCDA, ML, DL, ensembles): features, metrics, Peru/Ecuador studies

### Takeaway
The best Peru-specific ML study (Badillo-Rivera et al., 2025, Piura basin, 2017 Coastal El Niño) found Random Forest hybridized with Weights of Evidence (RF-WoE) best: test AUC 0.907, 5-fold CV AUC 0.936. RF beat linear SVM in every variant. Geology and geomorphology were the top SHAP features. Across the literature, random-split AUCs of 0.85–0.99 are typical but inflated. Spatial CV and held-out events lower performance, and the non-flood sampling design changes AUC more than the choice of algorithm does.

### Cited Findings
**Peru – Piura (key reference study)**
- Badillo-Rivera, E., Santiago, R., Poma, I., Chávez, T., Arroyo-Paz, A., Aucahuasi-Almidón, A., Hinostroza, E., Segura, E., Eyzaguirre, L., León, H., … Virú-Vásquez, P. (2025). "Flood susceptibility mapping in El Niño Phenomenon integrating multitemporal radar analysis, GIS and machine learning techniques, Piura river basin, Peru." *Frontiers in Environmental Science* 13, published 18 Sep 2025. DOI: 10.3389/fenvs.2025.1672107 — [Frontiers](https://www.frontiersin.org/journals/environmental-science/articles/10.3389/fenvs.2025.1672107/full)
  - Study area: Piura department (~4.09°–6.37° S, 35,837.6 km²), focused on the lower Piura basin — [Frontiers](https://www.frontiersin.org/journals/environmental-science/articles/10.3389/fenvs.2025.1672107/full)
  - Flood inventory: Sentinel-1 SAR flood extent for 20 Mar–4 Apr 2017 (2017 Coastal El Niño), 1,637.2 km² flooded. Processed in SNAP with a 3×3 Lee filter and the Normalized Difference Flood Index (NDFI, threshold 0.35). Positive samples were flood-polygon centroids. Negative samples came from INGEMMET's heuristic susceptibility model plus random points in high, steep areas. 182 samples in total (balanced 91/91), 80/20 split — [Frontiers](https://www.frontiersin.org/journals/environmental-science/articles/10.3389/fenvs.2025.1672107/full)
  - Conditioning factors: geology, geomorphology (INGEMMET), NDVI (Landsat-8, March 2017, via GEE), and DEM-derived slope, aspect, TRI, TWI, SPI, flow accumulation, and general/plan/profile curvature. TRI and slope had VIF 56.4 and 55.5, so PCA was applied (4 PCs explained 75.4% of variance). The DEM source is inconsistent in the paper (Copernicus 30 m in the methods vs ALOS PALSAR in Table 1) — [Frontiers](https://www.frontiersin.org/journals/environmental-science/articles/10.3389/fenvs.2025.1672107/full)
  - Models: RF and SVM (linear kernel), each with three variable encodings: quantiles (q), Frequency Ratio (FR), and Weights of Evidence (WoE) — [Frontiers](https://www.frontiersin.org/journals/environmental-science/articles/10.3389/fenvs.2025.1672107/full)
  - Metrics (Table 5): RF-q AUC train/test/CV 0.994/0.932/0.917, F1-CV 0.847. RF-WoE 0.998/0.907/0.936, F1-CV 0.851, Acc-CV 0.848. RF-FR 0.995/0.919/0.911. SVM-WoE 0.945/0.866/0.910. SVM-q 0.868/0.821/0.828. SVM-FR 0.858/0.805/0.833. RF-WoE was selected as best. The abstract gives a training AUC of 0.988 while the table gives 0.998, an internal inconsistency — [Frontiers](https://www.frontiersin.org/journals/environmental-science/articles/10.3389/fenvs.2025.1672107/full)
  - SHAP (RF-WoE): geology > geomorphology > PC-3 (linked to aspect). PC-1 and NDVI had little effect. Flat surfaces were associated with higher flood probability — [Frontiers](https://www.frontiersin.org/journals/environmental-science/articles/10.3389/fenvs.2025.1672107/full)
  - Validation: 80/20 holdout, 5-fold CV, and a visual comparison with the 1983/84 and 1997/98 flood footprints. Output: 19 settlements (~21,264 people, 6,524 households) in the "very high" class. Stated limitations are the small sample, dependence on Sentinel-1, and limited transferability outside Piura — [Frontiers](https://www.frontiersin.org/journals/environmental-science/articles/10.3389/fenvs.2025.1672107/full)
- Other Peru items found: HAZUS-MH flood model adapted to Piura in a data-scarce setting (UTEC) — [UTEC CRIS](https://cris.utec.edu.pe/en/publications/application-of-hazus-mh-flood-model-in-developing-countries-the-c/). A Peruvian ML model for flood/landslide vulnerability of schools trained on MINEDU records (Universidad de Lima, CIIS) — [Revista ULima](https://revistas.ulima.edu.pe/index.php/CIIS/article/download/5637/5480/)

**Ecuador**
- I found no peer-reviewed ML flood-susceptibility study with AUC for coastal Ecuador or Guayas. The closest results: an ESPOL thesis on *landslide* susceptibility in the Andes (RF AUC 0.947, accuracy 94.86%, which beat a hybrid AHP-FR/SMCE model at AUC 0.843) — [ESPOL thesis](https://dspace.espol.edu.ec/bitstream/123456789/67908/1/T-115795%20MATE-213%20BOLA%c3%91OS-RODRIGUEZ.pdf). An ESPOL study used RF to predict flood damage by sector in Guayaquil — [ESPOL](https://www.dspace.espol.edu.ec/bitstream/123456789/67999/1/T-115877%20POSTG169%20COLMONT%20VILLACRES.pdf). There is also a GIS flood hazard assessment for three Ecuadorian cities at 1:5000 (Revista Geográfica, UNA) — [UNA](https://revistas.una.ac.cr/index.php/geografica/article/view/19684). An Ecuador flash flood susceptibility index (FFSI) is based on catchment hypsometry, drainage and surface characteristics — [Columbia NCDP](https://ncdp.columbia.edu/library/publications/ecuador-flash-flood-susceptibility-index-ffsi-based-on-catchment-hypsometry-drainage-and-surface-characteristics/)

**General literature on performance and validation**
- Guangzhou study (Remote Sensing 15(22):5384): AUC differences from the learning algorithm were 0.04–0.09, while differences from the sampling approach (how non-flood points are chosen) were 0.15–0.22 — [MDPI / Crossref](https://api.crossref.org/works/10.3390%2FRS15225384)
- Kunming, China (mountain-urban floods): RF AUC 0.87 > XGBoost 0.84 — [Crossref record](https://api.crossref.org/works/10.3390%2FRS16020320) (attribution per the search summary; verify the exact paper)
- Himachal Pradesh RF with nested leave-one-block-out spatial CV (5 km blocks): outer-fold ROC-AUC 0.919–0.973 (mean 0.944), balanced accuracy 87.8–96.4%. Slope had near-zero permutation importance — [Research Square preprint](https://www.researchsquare.com/article/rs-11363913) (preprint, not peer-reviewed)
- A non-peer-reviewed preprint reports spatial CV pushing flood-risk classifiers toward chance (RF mean spatial AUC 0.590) — [Preprints.org](https://www.preprints.org/manuscript/202608.0577) (treat with caution)
- A literature review of ML/DL hazard susceptibility mapping (Remote Sensing 16(18):3374) and an ML flood-susceptibility review covering 2013–2023 exist. Neither pools AUC quantitatively — [MDPI mirror](https://p.gyb.elementfx.com/2072-4292/16/18/3374); [review record](https://library.kab.ac.ug/Record/doaj-art-0773c04f090b4eb3b7d31a5c0b7dde20/Description)

**Deep learning on SAR (CNN/U-Net) for flood extent (used to build the target/inventory)**
- Sen1Floods11 benchmark (Bonafilia et al., 2020): the baseline was a fully convolutional network on S1 and S2 separately. Attentive U-Net on S1 (VV, VH, VV/VH) reached 67% IoU, ~3% above the benchmark, and a fusion variant gave +4.5% IoU (Yadav et al., 2022, *Frontiers in Remote Sensing*, DOI 10.3389/frsen.2022.1060144) — [Frontiers](https://www.frontiersin.org/journals/remote-sensing/articles/10.3389/frsen.2022.1060144/full)
- A controlled comparison (Remote Sensing 2026, GeoHybridNet paper): U-Net, Attention U-Net, wide U-Net and SegFormer differ by ≤1.4 IoU points with no significant differences across 5 seeds. On 3 held-out flood events, IoU drops 24–26 points for every model — [MDPI PDF](https://mdpi-res.com/d_attachment/remotesensing/remotesensing-18-03769/article_deploy/remotesensing-18-03769.pdf)
- An AlbuNet-34 benchmark found a dual-polarization CNN beat the operational rule-based Sentinel-1 chain by ~5% IoU. FCN, DeepLabV3+, U-Net and U-Net++ were not significantly different from it — per the same search results ([Frontiers](https://www.frontiersin.org/journals/remote-sensing/articles/10.3389/frsen.2022.1060144/full) cluster; exact paper not fetched)

### Inferences
- For a student project, RF (plus XGBoost/LightGBM as a challenger) on a 30 m grid with SHAP is the defensible core. MCDA (AHP/FR/WoE) is best used as a baseline or as feature encoding (the FR/WoE transforms in Badillo-Rivera et al.), not as the final model.
- The near-perfect training AUCs in the Piura study (0.99+) with only 182 points suggest overfitting and spatial autocorrelation. A student project should report spatial-block CV and a held-out event, not just random splits.
- Geology and geomorphology ranking above slope/TWI in Piura probably reflects the lower-basin alluvial plain and quebradas: the INGEMMET geomorphology class already encodes "llanura inundable / terraza". Distance to river, height above nearest drainage (HAND) and elevation are standard top features elsewhere but were not in the Piura factor set. Adding HAND and distance-to-drainage is a clear improvement opportunity.
- Do not use a DL segmentation model (U-Net) as the susceptibility model. Use it, or simple SAR thresholding (NDFI, Otsu), to build the label (flood extent per event). Its accuracy degrades on unseen events, so validate the label maps visually and against INDECI reports.

### Gaps
- No Lambayeque, Tumbes, Trujillo (La Libertad) or Chimbote ML susceptibility study with metrics was found in this session. Peruvian repositories (UDEP, UNP, UNPRG, UNT, ALICIA) likely hold theses but were not reached.
- No peer-reviewed coastal-Ecuador (Guayas/Manabí/El Oro) ML susceptibility study with AUC was found.
- No AHP-only Peru study with reported metrics was retrieved.
- XGBoost/LightGBM, ANN and logistic regression results for Peru were not found. The general literature values above (RF 0.87 vs XGB 0.84 in Kunming) are from other regions.
- I could not confirm whether the companion "HFPS-RSTree" flash-flood paper by overlapping Piura authors is peer-reviewed. It appeared only in a search summary.

---

## 2. Hydrological and hydraulic modeling used in Peru (HEC-HMS, HEC-RAS, Iber, GloFAS) and how it complements ML

### Takeaway
HEC-HMS (rainfall-runoff) plus HEC-RAS 1D/2D (inundation) is the standard in Peru. The Autoridad para la Reconstrucción con Cambios / Plan Río Piura calibrated an HEC-HMS model and a 1D-2D HEC-RAS model on the March 2017 flood (peak 3,468 m³/s at Los Ejidos). Iber appears in student theses. Physical models give return-period flood depths and extents that can serve as features or as validation for ML susceptibility maps. Seasonal ENSO-based statistical streamflow forecasts have outperformed global physical models for Piura.

### Cited Findings
- 2017 Piura flood: heaviest rain on 22 Mar 2017 (90.4 mm). Piura River discharge peaked at 3,468 m³/s on 27 Mar 2017, against a usual average below 100 m³/s (weather radar analysis, *Remote Sensing* 14(4):824, 2022) — [MDPI](https://www.mdpi.com/2072-4292/14/4/824)
- A Plan Río Piura progress presentation to the Congress (8 Jul 2022) includes HEC-HMS hydrological modeling of the March 2017 event and a 1D-2D HEC-RAS hydraulic calibration with the March 2017 peak at Los Ejidos — [Congreso del Perú PDF](https://www.congreso.gob.pe/Docs/comisiones2021/pro-inversion/files/presentaciones/3_presentación_avances_plan_rio_piura-8.07.2022.pdf)
- UDEP thesis (2019), Los Ejidos–Puente Independencia reach: HEC-RAS levels, velocities and Froude numbers before and after the 2017 FEN costero. Simulated depths were similar to those observed at Q = 3,468 m³/s — [Repositorios Latinoamericanos](https://repositorioslatinoamericanos.uchile.cl/handle/2250/6503203)
- 2019 thesis, Los Ejidos–Puente Cáceres: HEC-RAS 5.0.7 flow profiles, scour and bridge effects. It concludes a stable channel section could control flooding for Q > 4,500 m³/s — [Repositorios Latinoamericanos](https://repositorioslatinoamericanos.uchile.cl/handle/2250/6616783)
- PUCP work combines hydrological and inundation models for design hydrographs and flood zones by return period in Piura city — [PUCP repository](https://repositorio.pucp.edu.pe/index/handle/123456789/175079)
- UCV thesis, Tambogrande bridge (Piura River), HEC-HMS + Iber: Q(TR10) = 1,736.2 m³/s, Q(TR50) = 3,483.5 m³/s, Q(TR100) = 4,299.7 m³/s — [UCV](https://repositorio.ucv.edu.pe/bitstream/handle/20.500.12692/35629/Cotrado_ANY-SD.pdf?sequence=5)
- HEC-RAS vs Iber comparison on the same section (Tambo River, Arequipa; UCSM) — [UCSM](https://repositorio.ucsm.edu.pe/bitstreams/462deeef-943e-483f-b389-f06456811fb2/download)
- Seasonal forecasting: Keating, Lee, Bazo & Block (2021), "Leveraging multi-model season-ahead streamflow forecasts to trigger advanced flood preparedness in Peru," *NHESS* 21, 2215–2231, DOI 10.5194/nhess-21-2215-2021 — [NHESS](https://nhess.copernicus.org/articles/21/2215/2021/)
  - Compares a locally tuned statistical model (seasonal streamflow ~ ENSO predictors) with global physical models and a multi-model combination, for the Piura and Marañón rivers — [NHESS](https://nhess.copernicus.org/articles/21/2215/2021/)
  - Trigger rule: act if forecast P(exceed 80th percentile of streamflow) ≥ 75%. In Piura the statistical model performed best and triggered ~28% more often in the hindcast, with an 86% hit rate at one threshold (per search summary). Lowering the trigger to 50% captured all 4 historical events with only 1 false alarm. For the Marañón, the statistical model triggered correctly in 3 of 4 cases — [NHESS](https://nhess.copernicus.org/articles/21/2215/2021/nhess-21-2215-2021.pdf)

### Inferences
- ML and physical modeling complement each other in three ways. (a) HEC-RAS 2D flood-depth rasters for TR50/TR100 (Q ≈ 3,480–4,300 m³/s at Tambogrande) can be used as a feature or a physically based prior in the ML model. (b) They can provide an independent validation map for the ML susceptibility map. (c) They turn a scenario discharge (for example, "2017-like peak 3,468 m³/s") into an inundation footprint for the 2027 scenario.
- A student project likely cannot run calibrated HEC-RAS 2D for several basins. A practical path is to use HAND-based inundation (thresholding HAND by the stage for a scenario discharge) as a cheap proxy. This is a methods suggestion, not sourced.

### Gaps
- GloFAS: I found no Peru-specific GloFAS skill evaluation in this session. Keating et al. compared "global physical models", which likely include GloFAS-Seasonal, but this was not verified.
- No SENAMHI operational hydrological model documentation (e.g., GR4J/GR2M, SWAT, or SENAMHI's own flood early-warning chain) was retrieved.
- Lambayeque (La Leche, Chancay-Lambayeque), Tumbes, Moche (Trujillo) and Lacramarca/Santa (Chimbote) HEC-RAS studies were not searched.

---

## 3. Forecasting El Niño and its rainfall (statistical, ML/DL, ENFEN/SENAMHI practice, lead-time limits, scenario approach)

### Takeaway
Ham et al. (2019) showed a CNN trained on CMIP5 simulations and then reanalysis gives skilful Niño 3.4 forecasts up to ~1.5 years ahead, beating dynamical systems. But Peru's floods depend on **coastal** (Niño 1+2) warming, which can decouple from Niño 3.4 (2017). The 2017 Coastal El Niño was poorly anticipated: NOAA gave only ~30% weak-El Niño odds in mid-January. ENFEN combines national and international model output into categorical ICEN-magnitude forecasts. For a student project, the robust design is a **conditional scenario**: P(flood | ICEN category) for Jan–Apr 2027, using ENFEN's official magnitude outlook as the input.

### Cited Findings
- Ham, Y.-G., Kim, J.-H. & Luo, J.-J. (2019). "Deep learning for multi-year ENSO forecasts." *Nature* 573, 568–572. DOI 10.1038/s41586-019-1559-7. The CNN used transfer learning (trained on historical CMIP simulations, then reanalysis 1871–1973). Validated over 1984–2017, its all-season correlation skill for the Nino3.4 index was higher than state-of-the-art dynamical systems at leads up to ~1.5 years — [NASA ADS](https://ui.adsabs.harvard.edu/abs/2019Natur.573..568H); [phys.org](https://phys.org/news/2019-09-deep-application-el-nio-events.amp)
- Slides summarizing Ham et al. say the CNN beat SINTEX-F for almost all target seasons. The correlation-skill figure marks forecasts > 0.5 — [SlideShare](https://www.slideshare.net/slideshow/deep-learning-for-multi-year-enso-forecasts-fnl/225390438) (secondary source)
- 2017 Coastal El Niño forecasting problems (Ramírez & Briones, 2017, "Understanding the El Niño Costero of 2017: The Definition Problem and Challenges of Climate Forecasting and Disaster Responses," *Int. J. Disaster Risk Science*, DOI 10.1007/s13753-017-0151-8). The event developed in mid-January and faded by May 2017. NOAA ENSO diagnostic discussions did not acknowledge it, though the February report noted a +1.5 °C Niño 1+2 anomaly. As of 16 Jan 2017, guidance gave about a 30% chance of a weak El Niño. ICEN captured the timing but classified the event as weak compared with the strong anomalies observed nearer the coast — [Springer](https://link.springer.com/article/10.1007/s13753-017-0151-8)
- Dynamics: the 2017 event was driven by coastal wind forcing and is described as extreme because of the rapid rise in rainfall off Ecuador and Peru without basin-wide warming (*Nature Communications* 2018, as summarized by IGP's Ciencia Climática) — [IGP Ciencia Climática](https://cienciaclimatica.igp.gob.pe/interpretaciones/1049319246/descargar-docx). Hypothesized atmospheric trigger: weakened trade winds — [CR2 PDF](https://www.cr2.cl/wp-content/uploads/2018/03/A-plausible-atmospheric-trigger-for-the-2017-coastal-El-Nin%CC%83o.pdf)
- ICEN: a 3-month running mean of the Niño 1+2 SST anomaly, with categories set by ENFEN (2012) and technical basis in Takahashi et al. (2014). A relative ICEN (ICENr) uses the 1991–2020 climatology (Reupo et al., 2024). Event magnitude depends on the SST dataset: 2017 was "weak" with ERSSTv3 but "moderate" with ERSSTv5 — [IGP repository](https://repositorio.igp.gob.pe/bitstreams/bc31de02-1c79-476d-a28f-c48a6a02e2c0/download); [IGP repository](https://repositorio.igp.gob.pe/bitstreams/e686f729-70e2-4b52-afb1-fe808a4cb07e/download)
- A recent IGP report says current ICEN categories follow **ENFEN (2024)**. Its table lists May 2026 ICEN 1.98 as "Cálida Moderada", June 2026 2.66 as "Cálida Fuerte", and a provisional August 2026 value of 3.61 as "Cálida Extraordinaria". A 2023 report in the same series classified Nov 2023 at 1.90 as "Cálida Fuerte", which shows the thresholds changed between versions — [IGP repository](https://repositorio.igp.gob.pe/bitstreams/c90f7225-a84a-4921-b8b1-ceb45bcec7f5/download) (from search snippet; the file was too large to fetch, so verify)
- ONI category thresholds used by ENFEN for Niño 3.4: ±0.5, ±1.0, ±1.5, ±2.0 for weak, moderate, strong and very strong (ENFEN 2015) — [IGP repository](https://repositorio.igp.gob.pe/bitstreams/9c7e7326-e846-436e-8bfd-1385f4a8ccd7/download)
- ENFEN method (2026 bulletin): forecasts draw on national and international climate and seasonal forecasts, with continuous monitoring of oceanic, atmospheric, hydrological and biological-fisheries conditions. Outlooks are given as the most probable magnitude category per period (detailed probability tables are in the bulletin's Tables 1–2) — [ENFEN 16-2026](https://enfen.imarpe.gob.pe/download/comunicado-oficial-enfen-n-16-2026/)
- Current outlook (14 Sep 2026): Niño 1+2 extraordinary (Sep 2026–Jan 2027), strong-to-extraordinary (Feb–Mar 2027), declining toward neutral in autumn 2027. Niño 3.4 very strong, then strong. Above-normal summer-2027 rainfall on the northern coast — [ENFEN 16-2026](https://enfen.imarpe.gob.pe/download/comunicado-oficial-enfen-n-16-2026/)

### Inferences
- The 2017 case shows that Niño 3.4-based forecasts (including Ham-style CNNs targeting Niño 3.4) are not sufficient for Peru's coastal rainfall. A project should forecast or condition on Niño 1+2/ICEN and the Niño 1+2 minus western-Pacific gradient (see section 4).
- Lead-time realism: coastal rainfall extremes in Piura depend on intraseasonal SST and wind variability, and the 2017 event emerged within ~1 month. Even in an ongoing strong event (2026–27), exact flood timing and location are only predictable at weather-to-subseasonal leads. The defensible output is therefore a seasonal **probabilistic/scenario** map, updated monthly with ENFEN bulletins.
- Scenario approach for 2027: (1) take ENFEN's probability per ICEN category for Feb–Mar 2027; (2) for each category, take the rainfall/discharge anomaly from historical analog years (for example, strong/extraordinary 1982–83 and 1997–98, coastal 2017, moderate 2023); (3) feed the scenario rainfall into the susceptibility/hazard model; (4) combine as P(flood) = Σ P(category) × P(flood | category).
- Spring predictability barrier: the event is already established as of Nov 2026, so the barrier is less limiting for the 2027 peak season than for forecasting its onset. Explain this distinction in the project.

### Gaps
- UNVERIFIED (background knowledge, not confirmed): the "classic" ICEN categories (ENFEN 2012) were Cálida Débil 0.4–1.0, Moderada 1.0–1.7, Fuerte 1.7–3.0, Extraordinaria >3.0, and Fría Débil −1.0 to −1.2, Moderada −1.2 to −1.4, Fuerte < −1.4. The 2023 IGP snippet (1.90 = Fuerte) is consistent with this. The ENFEN (2024) update appears to have changed the thresholds (2026 values of 1.98 = Moderada, 2.66 = Fuerte). The exact ENFEN (2024) thresholds were not retrieved and must be checked in the ENFEN 2024 technical note.
- Exact Ham et al. correlation values by lead month (e.g., correlation > 0.5 at 17 months) were not verified from the full text.
- The spring predictability barrier was not specifically sourced in this session.
- Which models ENFEN/IGP use (NMME ensemble members such as CFSv2, ECMWF SEAS5, and IGP's own coupled models) was not confirmed from a primary document.
- No ML forecasting study specific to Niño 1+2 or ICEN was found.

---

## 4. Studies linking ICEN / Niño 1+2 to rainfall and discharge in Piura and the northern coast

### Takeaway
Coastal-Peru rainfall is significantly correlated with eastern-Pacific (E-index / Niño 1+2) warming, and northern lowland rainfall rises sharply in extreme El Niños. Piura River discharge is **nonlinear (roughly exponential)** in the Niño 1+2 minus western/central-Pacific SST difference, which predicts it better than Niño 1+2 alone. Coupling is not guaranteed: 2015–16 Niño 1+2 warming did not produce comparable discharge.

### Cited Findings
- Takahashi & Martínez (2017, IGP): annual Piura River discharge is modeled as a function of the Feb–Mar SST difference between Niño 1+2 and a central-western Pacific region ("Tw"). The flow is better estimated with this difference than with Niño 1+2 alone, and the relationship is approximately exponential. Takahashi's CLIVAR presentation calls the link "nonlinear and nonlocal" — [IGP bulletin Vol. 4 Nº 4, Apr 2017](https://repositorio.igp.gob.pe/server/api/core/bitstreams/30cc7fd2-c5d2-46f0-bb35-8a5448ef7ab4/content); [IGP divulgación PPR El Niño 2017](http://met.igp.gob.pe/publicaciones/Divulgacion_PPR_El_Nino_IGP_201704.pdf); [Takahashi CLIVAR 2018 slides](https://www.clivar.org/sites/default/files/20181016%20Takahashi%20El%20Ni%C3%B1o.pdf)
- Lavado-Casimiro, W. & Espinoza, J.C. (2014). "Impactos de El Niño y La Niña en las lluvias del Perú (1965–2007)." *Revista Brasileira de Meteorologia* (Jun 2014). The study used 155 stations, Troup SOI event classification, and the E and C indices. It found a significant (95%) direct correlation between the E index (coastal warming) and rainfall along the whole Peruvian coast — [DOAJ](https://doaj.org/article/e3ab38ae1e6b4ba38fbf1ce931f73aaf); [SENAMHI repository](https://repositorio.senamhi.gob.pe/handle/20.500.12542/93?show=full)
- Sulca et al. (2018, *Int. J. Climatology*): positive E enhances wet conditions along the coasts of Ecuador and northern Peru. Positive C induces dry anomalies in the tropical Andes and northern South America — [IGP repository](https://repositorio.igp.gob.pe/bitstreams/f4cf9d7e-5ece-48b0-83b2-ee8881e605dc/download)
- Bourrel et al. (2014, with Lavado-Casimiro): the ENSO–precipitation link on the Peruvian coast shifted. Before 2000, El Niño increased precipitation, while in the 2000s ENSO was associated with drier conditions — [core.ac.uk](https://core.ac.uk/download/250077354.pdf)
- Rau, P., Bourrel, L., Labat, D., Melo, P., Dewitte, B., Frappart, F., Lavado, W. & Felipe, O. (2017). "Regionalization of rainfall over the Peruvian Pacific slope and coast." *Int. J. Climatology* 37(1), 143–158. DOI 10.1002/joc.4693. Using k-means plus the regional vector method on 145 stations (1964–2011), it identified 9 homogeneous regions. Rainfall increases in downstream northern Peru during extreme El Niño and decreases upstream on the Pacific slope during central-Pacific El Niño — [SENAMHI repository](https://repositorio.senamhi.gob.pe/handle/20.500.12542/50?show=full); [core.ac.uk](https://core.ac.uk/download/250077266.pdf)
- Coupling varies by event: Piura discharge, rainfall and Niño 1+2 were strongly coupled in 1983 and 1997–98. In 2015–16, Niño 1+2 warming did not produce comparable rainfall-driven discharge. In 1925 and 2017, monthly flow peaks coincided with Niño 1+2 SST peaks (PLOS ONE 2023, "Reflections on the impact and response to the Peruvian 2017 Coastal El Niño event") — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10522041/)
- ENSO-based statistical streamflow model for Piura (Keating et al., 2021) outperformed global physical models for triggering — [NHESS](https://nhess.copernicus.org/articles/21/2215/2021/)

### Inferences
- Feature engineering for a temporal model: use Niño 1+2 (or ICEN) and the gradient (Niño 1+2 − western Pacific) for Feb–Mar, possibly log-transformed or with an exponential link. Use station or CHIRPS/PISCO rainfall anomalies per Rau et al. region as an intermediate target.
- Because the relationship is nonlinear and has few extreme samples (1925, 1983, 1998, 2017, 2023), simple models (log-linear or quantile regression, GLM with a log link) are more defensible than deep learning for the climate-to-rainfall/discharge step.
- The Bourrel et al. decadal shift and the 2015–16 non-event mean the model should express uncertainty, for example with prediction intervals or analog spread.

### Gaps
- Woodman (1999) on the Piura rainfall–SST relationship was not retrieved or verified.
- Takahashi & Martínez (2017) regression coefficients and fit statistics were not obtained.
- Quantitative correlations (r values) between ICEN and rainfall per station or district for Tumbes, Lambayeque, La Libertad and Áncash were not found.
- The PISCO (SENAMHI gridded precipitation) dataset documentation was not retrieved, although it is the natural rainfall source.

---

## 5. Validation design (spatial CV, temporal hold-out, imbalance, metrics, SHAP)

### Takeaway
Random-split AUCs overstate skill. Use spatial-block CV and a temporal/event hold-out (for example, train on 1998 + 2017 footprints, test on 2023). Sampling of negatives can shift AUC by 0.15–0.22, more than the choice of algorithm. Report AUC-ROC, PR-AUC/F1/recall for the flood class, and the Brier score for probabilistic outputs, and use SHAP for explainability.

### Cited Findings
- Spatial block CV (5 km blocks, leave-one-block-out, nested) gave RF ROC-AUC 0.919–0.973 in Himachal — [Research Square](https://www.researchsquare.com/article/rs-11363913) (preprint)
- Spatial CV can drive performance toward chance (RF spatial AUC 0.59 in one preprint) — [Preprints.org](https://www.preprints.org/manuscript/202608.0577) (not peer-reviewed)
- Non-flood sampling strategy changes AUC by 0.15–0.22, against 0.04–0.09 for the algorithm choice — [Remote Sensing 15:5384](https://api.crossref.org/works/10.3390%2FRS15225384)
- Held-out flood events drop SAR segmentation IoU by 24–26 points for every architecture — [Remote Sensing 2026](https://mdpi-res.com/d_attachment/remotesensing/remotesensing-18-03769/article_deploy/remotesensing-18-03769.pdf)
- Piura study practice: balanced 91/91 sampling, 80/20 split, 5-fold CV, AUC/F1/accuracy, SHAP, and a visual check against 1983/84 and 1997/98 footprints — [Frontiers](https://www.frontiersin.org/journals/environmental-science/articles/10.3389/fenvs.2025.1672107/full)
- Operational trigger-style evaluation (hit rate, false alarms at probability thresholds of 50% and 75% on the 80th-percentile flow) — [NHESS Keating et al.](https://nhess.copernicus.org/articles/21/2215/2021/)

### Inferences
- Recommended design: (a) spatial-block CV, with blocks of about 2–5 km or by sub-basin or district, to tune; (b) an event hold-out: train on the 1998 and 2017 flood labels, test on the 2023 (Yaku / ENFEN coastal event) footprint, and if possible later check against the 2026–27 event as it unfolds; (c) a leave-one-basin-out test (train on Piura + Lambayeque, test on Tumbes) to measure transferability.
- Class imbalance: do not artificially balance the test set. Use class_weight / scale_pos_weight or balanced sampling only in training, and report PR-AUC and recall at a fixed false-alarm rate. For grid cells, flooded cells may be under 5% of the area.
- Calibration: report the Brier score and reliability diagrams, because the final product is a probability. Apply isotonic or Platt calibration on the hold-out.
- Explainability: SHAP global (beeswarm) plus local explanations for top-risk districts. Check for leakage (for example, NDVI from the flood month itself reflects flooding).
- Negative sampling: draw non-flood points from areas observed as dry in the same SAR scenes, not only from steep highlands (the Piura study's choice), which makes the task too easy.

### Gaps
- No Peru study using temporal hold-out across El Niño events was found.
- No source on Brier-score use in flood-susceptibility studies was retrieved. The recommendation rests on general forecast-verification practice.
- The 2023 flood extent (Cyclone Yaku plus the 2023 coastal El Niño) is not documented here as a ready dataset. Students would need to build it from Sentinel-1.

---

## 6. Proposed step-by-step project pipeline (high-flood-incidence zones, northern coast, El Niño 2027)

### Takeaway
A two-stage design is supported by the evidence. (1) A static, event-trained ML susceptibility/hazard model (RF/XGBoost on a 30 m grid, labels from Sentinel-1 flood maps of 2017 and 2023, plus 1998 if Landsat/ERS data are available). (2) A climate-conditioning layer that maps ENFEN's ICEN-category probabilities for Feb–Mar 2027 to rainfall/discharge scenarios via historical analogs and the Niño 1+2 gradient relationship. Then combine with exposure and vulnerability (risk = hazard × exposure × vulnerability) and aggregate to districts for a dashboard.

### Cited Findings (building blocks with sources)
- SAR flood labeling method (Sentinel-1, Lee filter, NDFI threshold 0.35) and GEE use for Landsat NDVI — [Frontiers Badillo-Rivera 2025](https://www.frontiersin.org/journals/environmental-science/articles/10.3389/fenvs.2025.1672107/full)
- Predictors from INGEMMET geology/geomorphology plus DEM derivatives (TWI, SPI, TRI, curvatures, flow accumulation), with VIF/PCA for collinearity — [Frontiers](https://www.frontiersin.org/journals/environmental-science/articles/10.3389/fenvs.2025.1672107/full)
- Climate driver: Niño 1+2 minus Tw gradient (Feb–Mar), with an exponential discharge relationship — [IGP Apr 2017 bulletin](https://repositorio.igp.gob.pe/server/api/core/bitstreams/30cc7fd2-c5d2-46f0-bb35-8a5448ef7ab4/content)
- Seasonal trigger logic: P(exceed Q80) ≥ 50–75% — [NHESS Keating et al. 2021](https://nhess.copernicus.org/articles/21/2215/2021/)
- Current ENFEN scenario for Feb–Mar 2027 (strong to extraordinary coastal El Niño) — [ENFEN 16-2026](https://enfen.imarpe.gob.pe/download/comunicado-oficial-enfen-n-16-2026/)
- Hydraulic reference (Piura 2017 peak 3,468 m³/s; TR50 ≈ 3,484 and TR100 ≈ 4,300 m³/s at Tambogrande) — [MDPI Remote Sensing 2022](https://www.mdpi.com/2072-4292/14/4/824); [UCV thesis](https://repositorio.ucv.edu.pe/bitstream/handle/20.500.12692/35629/Cotrado_ANY-SD.pdf?sequence=5)
- Exposure example: the Piura very-high class held 19 settlements, ~21,264 people and 6,524 households — [Frontiers](https://www.frontiersin.org/journals/environmental-science/articles/10.3389/fenvs.2025.1672107/full)

### Inferences (proposed pipeline; methods guidance, not sourced findings)
1. **Problem framing:** "Which districts and 30 m cells of Tumbes, Piura, Lambayeque, La Libertad and Áncash (coastal) have the highest probability of flooding in Jan–Apr 2027, given ENFEN's coastal El Niño outlook?" Output a probability map plus a district ranking. State that this is a seasonal scenario product, not a deterministic forecast.
2. **Unit of analysis:** a 30 m grid (matching the DEM, Sentinel-1 at 10 m resampled) for modeling, aggregated to **districts** (INEI ubigeo) for decisions and the dashboard. A coarser option is a 250–500 m grid if compute in GEE or a laptop is limited.
3. **Target definition:** binary "flooded in event e" from Sentinel-1 (2017: Mar–Apr; 2023: Mar). Optionally add the 1998 footprint from historical maps (INGEMMET or Landsat-5) and validate with INDECI/SINPAD emergency records. At district level, the alternative target is "flood emergencies per 1,000 inhabitants (SINPAD) in El Niño years", a count model.
4. **Features:** static (elevation, HAND, distance to river/drainage, slope, TWI, SPI, curvature, flow accumulation, geology, geomorphology, soil, land cover/ESA WorldCover, imperviousness, distance to quebradas and dry riverbeds) and event-dynamic (event-total rainfall from PISCO/CHIRPS/GPM IMERG, max 1-, 3- and 5-day rainfall, antecedent rainfall, upstream discharge). Climate (for the scenario layer): Niño 1+2/ICEN, the Niño 1+2 − western Pacific gradient, ONI.
5. **Models:** baselines are FR/WoE or AHP and logistic regression. Main models are RF and XGBoost/LightGBM. Optionally add a stacked ensemble. For the scenario layer, fit a GLM/quantile regression of rainfall/discharge on Niño 1+2 indices and analog resampling.
6. **Validation:** spatial-block CV, event hold-out (train 2017, test 2023, or vice versa), leave-one-region-out. Metrics: AUC-ROC, PR-AUC, F1/recall at fixed precision, Brier score with a reliability diagram. Use SHAP for explanation.
7. **2027 scenario:** substitute scenario rainfall fields (analog-year composites for "fuerte" and "extraordinario") into the dynamic features. Weight by ENFEN category probabilities. Optionally compare with a HEC-RAS/HAND inundation for Q = 3,468 m³/s (2017) and 4,300 m³/s (TR100) on the Piura River.
8. **Risk = hazard × exposure × vulnerability:** hazard is the calibrated P(flood). Exposure: population (INEI 2017 census / WorldPop / GHSL), housing, roads, health facilities and schools. Vulnerability: poverty, housing material, access to services (INEI, MIDIS), possibly CENEPRED indices. Normalize and combine, then rank districts.
9. **Outputs:** GeoTIFF maps, a district table with uncertainty, and a dashboard (Streamlit/Dash/Power BI or GEE App) with ENFEN scenario toggles (moderado / fuerte / extraordinario).
10. **Tools:** Python (geopandas, rasterio, xarray, scikit-learn, xgboost/lightgbm, shap, scikit-learn GroupKFold or spatial blocks), Google Earth Engine (Sentinel-1 GRD, CHIRPS, GPM, SRTM/Copernicus DEM, MERIT Hydro HAND), QGIS (cartography, INGEMMET layers), HEC-RAS (optional).

### Gaps
- Availability of a ready 1998 flood footprint for the northern coast was not verified.
- SINPAD/INDECI emergency database access and format were not checked.
- CENEPRED vulnerability layers and the SIGRID platform were not checked for downloadable data.
- PISCO precipitation and MERIT Hydro/HAND availability in GEE were not verified in this session (UNVERIFIED: background knowledge says CHIRPS, GPM IMERG, Sentinel-1 GRD, Copernicus DEM and MERIT Hydro are in the GEE catalog).
