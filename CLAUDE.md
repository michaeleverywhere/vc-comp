# CLAUDE.md — VC portfolio datasets & scrapers

Guidance for working in this repo. Read this first; deeper build methodology is in
[`scripts/PLAYBOOK.md`](scripts/PLAYBOOK.md).

## What this repo is
Structured JSON datasets of VC firms' portfolio companies, plus the reusable Python
scrapers that produce them. Each dataset is one JSON array, one object per company.

Current datasets (in `data/`):
| firm | file | records | source |
|---|---|---|---|
| Lightspeed | `companies.json` | 672 | lsvp.com/companies — `lightspeed_scraper.py` (listing + detail pages; includes LSIP rows flagged `lsvp_investor_flag`) |
| USV | `usv_companies.json` | 214 | usv.com/companies (`usv_scraper.py`) |
| Menlo Ventures | `menlo_companies.json` | 239 | menlovc.com/portfolio (`menlo_scraper.py`) |
| Insight Partners | `insight_companies.json` | 847 | insightpartners.com/portfolio (`insight_scraper.py`) |
| RRE Ventures | `rre_companies.json` | 250 | rre.com/portfolio (`rre_scraper.py`) |
| Founders Fund | `foundersfund_companies.json` | 62 | foundersfund.com/portfolio (`foundersfund_scraper.py`) |
| ICONIQ Growth | `iconiq_companies.json` | 100 | iconiq.com/growth/companies (`iconiq_scraper.py`) |
| Sequoia Capital | `sequoia_companies.json` | 412 | sequoiacap.com/our-companies (`sequoia_scraper.py`) |
| Andreessen Horowitz | `a16z_companies.json` | 849 | a16z.com/portfolio (`a16z_scraper.py`) |
| Accel | `accel_companies.json` | 766 | accel.com — own Sanity CMS API (`accel_scraper.py`) |
| Index Ventures | `index_companies.json` | 311 | indexventures.com/companies (`index_scraper.py`) |
| Kleiner Perkins | `kleinerperkins_companies.json` | 385 | kleinerperkins.com/partnerships (`kleinerperkins_scraper.py`) |
| NEA | `nea_companies.json` | 903 | nea.com — Statamic GraphQL (`nea_scraper.py`) |
| Greylock | `greylock_companies.json` | 159 | greylock.com/portfolio (`greylock_scraper.py`) |
| Bessemer | `bessemer_companies.json` | 516 | bvp.com/companies (`bessemer_scraper.py`) |
| Khosla Ventures | `khosla_companies.json` | 132 | khoslaventures.com sector pages (`khosla_scraper.py`) |
| General Catalyst | `generalcatalyst_companies.json` | 584 | generalcatalyst.com — own Algolia index (`generalcatalyst_scraper.py`) |
| Ribbit Capital | `ribbit_companies.json` | 148 | ribbitcap.com/rebels (`ribbit_scraper.py`) |
| Parkway VC | `parkway_companies.json` | 25 | parkway.vc/portfolio (`parkway_scraper.py`) |
| General Atlantic | `generalatlantic_companies.json` | 405 | generalatlantic.com/investments (`generalatlantic_scraper.py`) |
| Notable Capital | `notable_companies.json` | 127 | notablecap.com/companies (`notable_scraper.py`) |
| IVP | `ivp_companies.json` | 156 | ivp.com/portfolio `_payload.json` (`ivp_scraper.py`) |
| Dragoneer | `dragoneer_companies.json` | 29 | dragoneer.com/companies — curated subset (`dragoneer_scraper.py`) |
| Mayfield | `mayfield_companies.json` | 135 | mayfield.com/meet-our-founders (`mayfield_scraper.py`) |
| OrbiMed | `orbimed_companies.json` | 200 | orbimed.com/portfolio (`orbimed_scraper.py`) |
| Coatue | `coatue_companies.json` | 372 | coatue.com/portfolio API (`coatue_scraper.py`) |
| Spark Capital | `spark_companies.json` | 48 | sparkcapital.com/companies (`spark_scraper.py`) |
| SV Angel | `svangel_companies.json` | 150 | svangel.com/portfolio (`svangel_scraper.py`) |
| Battery Ventures | `battery_companies.json` | 343 | battery.com/company admin-ajax (`battery_scraper.py`) |
| Bedrock | `bedrock_companies.json` | 6 | bedrockcap.com/investments — full disclosure (`bedrock_scraper.py`) |
| Paradigm | `paradigm_companies.json` | 105 | paradigm.xyz/investments (`paradigm_scraper.py`) |
| Oak HC/FT | `oakhcft_companies.json` | 107 | oakhcft.com/portfolio (`oakhcft_scraper.py`) |
| Atlas Venture | `atlas_companies.json` | 79 | atlasventure.com/portfolio (`atlas_scraper.py`) |
| Venrock | `venrock_companies.json` | 250 | venrock.com — WP REST (`venrock_scraper.py`) |
| Meritech | `meritech_companies.json` | 48 | meritechcapital.com/companies (`meritech_scraper.py`) |
| Norwest | `norwest_companies.json` | 514 | norwest.com/companies (`norwest_scraper.py`) |
| CRV | `crv_companies.json` | 183 | crv.com/companies — RSC payload (`crv_scraper.py`) |
| Bain Capital Ventures | `baincapital_companies.json` | 269 | baincapitalventures.com — own Sanity API (`baincapital_scraper.py`) |
| Inflection Ventures | `inflection_companies.json` | 16 | inflectionvc.com/portfolio (`inflection_scraper.py`) |
| First Round Capital | `firstround_companies.json` | 190 | firstround.com/companies (`firstround_scraper.py`) |
| 8VC | `8vc_companies.json` | 172 | 8vc.com/companies (`8vc_scraper.py`) |
| TCV | `tcv_companies.json` | 151 | tcv.com/partnerships (`tcv_scraper.py`) |
| Lux Capital | `lux_companies.json` | 215 | luxcapital.com/companies via sitemap (`lux_scraper.py`) |
| ARCH Venture Partners | `arch_companies.json` | 128 | archventure.com/portfolio (`arch_scraper.py`) |
| Afore Capital | `afore_companies.json` | 100 | afore.vc/portfolio (`afore_scraper.py`) |
| Lerer Hippeau | `lererhippeau_companies.json` | 305 | lererhippeau.com/portfolio (`lererhippeau_scraper.py`) |
| 2048 Ventures | `2048_companies.json` | 75 | 2048.vc/companies (`2048_scraper.py`) |
| Hustle Fund | `hustlefund_companies.json` | 367 | hustlefund.vc/founders — Airtable shared-view embed ("full roster", fully deployed funds only; description, industry, geography, URL) (`hustlefund_scraper.py`) |
| Eclipse Ventures | `eclipseventures_companies.json` | 53 | eclipse.capital — own Sanity CMS (`eclipseventures_scraper.py`) |
| Amplify Partners | `amplifypartners_companies.json` | 114 | amplifypartners.com/portfolio/company (auto-gen `amplifypartners_scraper.py`) |
| Felicis | `felicis_companies.json` | 275 | felicis.com/portfolio (auto-gen `felicis_scraper.py`) |
| Foundry Group | `foundrygroup_companies.json` | 56 | foundrygroup.com/portfolio (auto-gen `foundrygroup_scraper.py`) |
| Homebrew | `homebrew_companies.json` | 162 | homebrew.co (auto-gen `homebrew_scraper.py`) |
| Wing VC | `wingvc_companies.json` | 99 | wing.vc (auto-gen `wingvc_scraper.py`) |
| Matrix Partners | `matrixpartners_companies.json` | 45 | matrixpartners.com (auto-gen `matrixpartners_scraper.py`) |
| True Ventures | `trueventures_companies.json` | 50 | trueventures.com (auto-gen `trueventures_scraper.py`) |
| Notation Capital | `notationcapital_companies.json` | 77 | notation.vc (auto-gen `notationcapital_scraper.py`) |
| Gradient Ventures | `gradientventures_companies.json` | 130 | gradientventures.com (auto-gen `gradientventures_scraper.py`) |
| Mosaic Ventures | `mosaicventures_companies.json` | 79 | mosaicventures.com (auto-gen `mosaicventures_scraper.py`) |
| Storm Ventures | `stormventures_companies.json` | 100 | stormventures.com (auto-gen `stormventures_scraper.py`) |
| Primary Venture Partners | `primaryventurepartners_companies.json` | 25 | primary.vc (auto-gen `primaryventurepartners_scraper.py`) |
| Point Nine Capital | `pointninecapital_companies.json` | 185 | pointnine.com/companies (`pointninecapital_scraper.py` — hand-written 2026-08-03, replacing a factory scraper whose 25 records were all junk) |

| Redpoint Ventures | `redpoint_companies.json` | 234 | redpoint.com/companies — Gatsby page-data (`redpoint_scraper.py`) |
| Scale Venture Partners | `scalevp_companies.json` | 117 | scalevp.com/portfolio (`scalevp_scraper.py`) |
| Emergence Capital | `emergence_companies.json` | 86 | emcap.com/portfolio (`emergence_scraper.py`) |
| Initialized Capital | `initialized_companies.json` | 184 | initialized.com/companies — __NEXT_DATA__ (`initialized_scraper.py`) |
| Craft Ventures | `craft_companies.json` | 40 | craftventures.com/portfolio (`craft_scraper.py`) |
| Uncork Capital | `uncork_companies.json` | 175 | uncorkcapital.com/companies — Framer (`uncork_scraper.py`) |
| Pear VC | `pear_companies.json` | 211 | pear.vc/company (`pear_scraper.py`) |
| Balderton Capital | `balderton_companies.json` | 205 | balderton.com/companies — FacetWP via Chrome (`balderton_scraper.py`) |
| Lowercarbon Capital | `lowercarbon_companies.json` | 101 | lowercarbon.com — WP REST (`lowercarbon_scraper.py`) |
| Canaan | `canaan_companies.json` | 345 | canaan.com/companies — Rails modal API (`canaan_scraper.py`; substitute for Atomico — atomico.com HTTP 429) |
| Sapphire Ventures | `sapphire_companies.json` | 196 | sapphireventures.com/companies (`sapphire_scraper.py`) |
| Threshold Ventures | `threshold_companies.json` | 90 | threshold.vc/companies — Webflow (`threshold_scraper.py`) |
| Unusual Ventures | `unusual_companies.json` | 63 | unusual.vc/portfolio (`unusual_scraper.py`) |
| Earlybird | `earlybird_companies.json` | 118 | earlybird.com/companies — Framer (`earlybird_scraper.py`) |
| Boldstart Ventures | `boldstart_companies.json` | 26 | boldstart.vc/companies (`boldstart_scraper.py`) |
| Tribe Capital | `tribe_companies.json` | 68 | tribecap.co/portfolio — Webflow (`tribe_scraper.py`) |
| SignalFire | `signalfire_companies.json` | 100 | signalfire.com/portfolio — Webflow (`signalfire_scraper.py`; re-armed 2026-10-02) |
| Project A | `projecta_companies.json` | 114 | project-a.vc — Sanity API (`projecta_scraper.py`) |
| Northzone | `northzone_companies.json` | 112 | northzone.com/portfolio — Webflow (`northzone_scraper.py`) |
| Costanoa Ventures | `costanoa_companies.json` | 97 | costanoa.vc — Prismic API (`costanoa_scraper.py`) |
| BITKRAFT | `bitkraft_companies.json` | 144 | bitkraft.vc/portfolio — __NEXT_DATA__ (`bitkraft_scraper.py`) |
| DCVC | `dcvc_companies.json` | 297 | dcvc.com/companies (`dcvc_scraper.py`) |
| FirstMark | `firstmark_companies.json` | 149 | firstmark.com/portfolio (`firstmark_scraper.py`) |
| Healthy Ventures | `healthyventures_companies.json` | 26 | healthy.vc/portfolio — Webflow (`healthyventures_scraper.py`) |
| Left Lane Capital | `leftlane_companies.json` | 110 | leftlane.com/companies — Webflow (`leftlane_scraper.py`) |
| Westly Group | `westlygroup_companies.json` | 41 | westlygroup.com — WP REST (`westlygroup_scraper.py`) |
| Heavybit | `heavybit_companies.json` | 114 | heavybit.com — Sanity API (`heavybit_scraper.py`) |
| Nyca Partners | `nyca_companies.json` | 115 | nyca.com/companies (`nyca_scraper.py`) |
| Konvoy | `konvoy_companies.json` | 51 | konvoy.vc/portfolio — Webflow (`konvoy_scraper.py`) |
| Inspired Capital | `inspiredcapital_companies.json` | 51 | inspiredcapital.com/portfolio — Webflow+JSON-LD (`inspiredcapital_scraper.py`) |
| MaC Venture Capital | `mac_companies.json` | 175 | macventurecapital.com/portfolio — HTML + WP REST status (`mac_scraper.py`) |
| .406 Ventures | `406ventures_companies.json` | 92 | 406ventures.com/companies (`406ventures_scraper.py`) |
| Kalaari Capital | `kalaari_companies.json` | 71 | kalaari.com/portfolio — Webflow + detail pages (`kalaari_scraper.py`) |
| Congruent Ventures | `congruent_companies.json` | 61 | congruentvc.com/portfolio — Webflow + detail pages (`congruent_scraper.py`) |
| Golden Gate Ventures | `goldengate_companies.json` | 110 | goldengate.vc/portfolio — Webflow + detail pages (`goldengate_scraper.py`) |
| Picus Capital | `picus_companies.json` | 168 | picuscap.com/portfolio (`picus_scraper.py`) |
| Prelude Ventures | `prelude_companies.json` | 61 | preludeventures.com/portfolio — Craft CMS + detail pages (`prelude_scraper.py`) |
| Daphni | `daphni_companies.json` | 101 | daphni.com/portfolio — Webflow paginated (`daphni_scraper.py`) |
| Jungle Ventures | `jungle_companies.json` | 71 | jungle.vc/portfolio — Webflow (`jungle_scraper.py`) |
| Openspace Ventures | `openspace_companies.json` | 48 | openspacecapital.com/companies — Webflow + detail pages (`openspace_scraper.py`) |
| 83North | `83north_companies.json` | 74 | 83north.com/companies (`83north_scraper.py`) |
| Abstract Ventures | `abstractventures_companies.json` | 262 | abstract.com/companies-list (`abstractventures_scraper.py`) |
| Air Street Capital | `airstreetcapital_companies.json` | 66 | airstreet.com/portfolio (`airstreetcapital_scraper.py`) |
| Albion VC | `albionvc_companies.json` | 12 | albion.vc/companies (`albionvc_scraper.py`) |
| Backed VC | `backedvc_companies.json` | 93 | backed.vc/portfolio (`backedvc_scraper.py`) |
| Basis Set Ventures | `basisset_companies.json` | 68 | basisset.com/portfolio (`basisset_scraper.py`) |
| Blockchain Capital | `blockchaincapital_companies.json` | 100 | blockchain.capital/portfolio (`blockchaincapital_scraper.py`) |
| Blossom Capital | `blossomcapital_companies.json` | 38 | blossomcap.com/portfolio (`blossomcapital_scraper.py`) |
| Bowery Capital | `bowerycapital_companies.json` | 47 | bowerycap.com/portfolio (`bowerycapital_scraper.py`) |
| BoxGroup | `boxgroup_companies.json` | 294 | boxgroup.com/portfolio (`boxgroup_scraper.py`) |
| Brighteye Ventures | `brighteye_companies.json` | 53 | brighteyevc.com/portfolio (`brighteye_scraper.py`) |
| Bullpen Capital | `bullpencapital_companies.json` | 99 | bullpencap.com/companies (`bullpencapital_scraper.py`) |
| Cambridge Innovation Capital | `cambridgeinnovationcapital_companies.json` | 24 | cic.vc/portfolio (`cambridgeinnovationcapital_scraper.py`) |
| CapitalG | `capitalg_companies.json` | 96 | capitalg.com/portfolio/stripe (`capitalg_scraper.py`) |
| Collaborative Fund | `collaborativefund_companies.json` | 615 | collabfund.com/portfolio (`collaborativefund_scraper.py`) |
| Colle Capital | `collecapital_companies.json` | 58 | collecapital.com/portfolio (`collecapital_scraper.py`) |
| Comcast Ventures | `comcastventures_companies.json` | 212 | comcastventures.com/portfolio (`comcastventures_scraper.py`) |
| Cowboy Ventures | `cowboyventures_companies.json` | 17 | cowboy.vc/portfolio (`cowboyventures_scraper.py`) |
| Crane Venture Partners | `cranevp_companies.json` | 108 | crane.vc/portfolio (`cranevp_scraper.py`) |
| Crosslink Capital | `crosslinkcapital_companies.json` | 147 | crosslinkcapital.com/portfolio (`crosslinkcapital_scraper.py`) |
| Draper Associates | `draperassociates_companies.json` | 100 | draper.vc/portfolio (`draperassociates_scraper.py`) |
| Eniac Ventures | `eniacventures_companies.json` | 100 | eniac.vc/companies (`eniacventures_scraper.py`) |
| Entrée Capital | `entreecapital_companies.json` | 155 | entreecap.com/companies (`entreecapital_scraper.py`) |
| Episode 1 Ventures | `episode1ventures_companies.json` | 84 | episode1.com/portfolio (`episode1ventures_scraper.py`) |
| Fika Ventures | `fikaventures_companies.json` | 94 | fika.vc/portfolio (`fikaventures_scraper.py`) |
| Floodgate | `floodgate_companies.json` | 116 | floodgate.com/companies (`floodgate_scraper.py`) |
| Forerunner Ventures | `forerunnerventures_companies.json` | 81 | forerunnerventures.com/investments (`forerunnerventures_scraper.py`) |
| Founder Collective | `foundercollective_companies.json` | 225 | foundercollective.com/portfolio (`foundercollective_scraper.py`) |
| F-Prime Capital | `fprimecapital_companies.json` | 371 | fprimecapital.com/portfolio (`fprimecapital_scraper.py`) |
| Frontline Ventures | `frontlineventures_companies.json` | 111 | frontline.vc/companies (`frontlineventures_scraper.py`) |
| Global Brain | `globalbrain_companies.json` | 539 | globalbrains.com/en/portfolio (`globalbrain_scraper.py`) |
| Great Oaks Venture Capital | `greatoaksventurecapital_companies.json` | 100 | greatoaksvc.com/portfolio (`greatoaksventurecapital_scraper.py`) |
| Greycroft | `greycroft_companies.json` | 245 | greycroft.com/portfolio (`greycroft_scraper.py`) |
| GV | `gv_companies.json` | 646 | gv.com/portfolio (`gv_scraper.py`) |
| Headline | `headline_companies.json` | 177 | headline.com/portfolio (`headline_scraper.py`) |
| High Alpha | `highalpha_companies.json` | 93 | highalpha.com/companies (`highalpha_scraper.py`) |
| Hoxton Ventures | `hoxtonventures_companies.json` | 95 | hoxtonventures.com/portfolio (`hoxtonventures_scraper.py`) |
| Hummingbird VC | `hummingbirdvc_companies.json` | 69 | hummingbird.vc/portfolio (`hummingbirdvc_scraper.py`) |
| Hyde Park Venture Partners | `hydeparkventurepartners_companies.json` | 53 | hydeparkvp.com/companies.html (`hydeparkventurepartners_scraper.py`) |
| Iris Capital | `iriscapital_companies.json` | 52 | iriscapital.com/portfolio (`iriscapital_scraper.py`) |
| Kindred Capital | `kindredcapital_companies.json` | 73 | kindredcapital.vc/portfolio (`kindredcapital_scraper.py`) |
| Kindred Ventures | `kindredventures_companies.json` | 129 | kindredventures.com/portfolio (`kindredventures_scraper.py`) |
| Lunar Ventures | `lunarventures_companies.json` | 23 | lunar.vc/portfolio (`lunarventures_scraper.py`) |
| M12 | `m12_companies.json` | 141 | m12.vc/portfolio (`m12_scraper.py`) |
| Madrona Venture Group | `madronaventuregroup_companies.json` | 213 | madrona.com/companies (`madronaventuregroup_scraper.py`) |
| Mubadala Capital | `mubadalacapital_companies.json` | 85 | mubadalacapital.com/portfolio (`mubadalacapital_scraper.py`) |
| Mucker Capital | `mucker_companies.json` | 107 | mucker.com/companies (`mucker_scraper.py`) |
| NFX | `nfx_companies.json` | 235 | nfx.com/companies (`nfx_scraper.py`) |
| Notation | `notation_companies.json` | 78 | notation.vc/companies (`notation_scraper.py`) |
| Notion Capital | `notioncapital_companies.json` | 100 | notion.vc/portfolio (`notioncapital_scraper.py`) |
| Obvious Ventures | `obviousventures_companies.json` | 91 | obvious.com/portfolio (`obviousventures_scraper.py`) |
| Partech | `partech_companies.json` | 274 | partechpartners.com/companies (`partech_scraper.py`) |
| Pillar VC | `pillarvc_companies.json` | 78 | pillar.vc/companies (`pillarvc_scraper.py`) |
| Propel Venture Partners | `propelventurepartners_companies.json` | 44 | propel.vc/portfolio (`propelventurepartners_scraper.py`) |
| Prosus Ventures | `prosusventures_companies.json` | 125 | prosus.com/portfolio (`prosusventures_scraper.py`) |
| Quest Venture Partners | `questventurepartners_companies.json` | 29 | questvp.com/portfolio.html (`questventurepartners_scraper.py`) |
| Radical Ventures | `radicalventures_companies.json` | 59 | radical.vc/portfolio (`radicalventures_scraper.py`) |
| Reach Capital | `reachcapital_companies.json` | 133 | reachcapital.com/companies (`reachcapital_scraper.py`) |
| Redalpine | `redalpine_companies.json` | 92 | redalpine.com/portfolio (`redalpine_scraper.py`) |
| Renegade Partners | `renegadepartners_companies.json` | 25 | renegadepartners.com/companies (`renegadepartners_scraper.py`) |
| Resolute Ventures | `resoluteventures_companies.json` | 112 | resolute.vc/companies (`resoluteventures_scraper.py`) |
| Ridge Ventures | `ridge_companies.json` | 39 | ridge.vc/ridge-portfolio (`ridge_scraper.py`) |
| Rocket Internet | `rocketinternet_companies.json` | 18 | rocket-internet.com/companies (`rocketinternet_scraper.py`) |
| RTP Global | `rtpglobal_companies.json` | 122 | rtp.vc/our-companies (`rtpglobal_scraper.py`) |
| Seedcamp | `seedcamp_companies.json` | 327 | seedcamp.com/our-companies (`seedcamp_scraper.py`) |
| Serena Ventures | `serenaventures_companies.json` | 42 | serenaventures.com/portfolio (`serenaventures_scraper.py`) |
| Slow Ventures | `slowventures_companies.json` | 328 | slow.co/portfolio (`slowventures_scraper.py`) |
| Speedinvest | `speedinvest_companies.json` | 56 | speedinvest.com/portfolio (`speedinvest_scraper.py`) |
| Target Global | `targetglobal_companies.json` | 119 | targetglobal.vc/portfolio (`targetglobal_scraper.py`) |
| Third Prime | `thirdprime_companies.json` | 78 | thirdprime.vc/portfolio (`thirdprime_scraper.py`) |
| Titanium Ventures | `titaniumventures_companies.json` | 101 | ti.vc/portfolio (`titaniumventures_scraper.py`) |
| TMT Investments | `tmtinvestments_companies.json` | 56 | tmtinvestments.com (`tmtinvestments_scraper.py`) |
| Underscore VC | `underscorevc_companies.json` | 56 | underscore.vc/portfolio (`underscorevc_scraper.py`) |
| Upwest | `upwest_companies.json` | 48 | upwest.vc/portfolio (`upwest_scraper.py`) |
| Village Global | `villageglobal_companies.json` | 54 | villageglobal.com/portfolio (`villageglobal_scraper.py`) |
| White Star Capital | `whitestarcapital_companies.json` | 98 | whitestarcapital.com/portfolio (`whitestarcapital_scraper.py`) |
| Work-Bench | `workbench_companies.json` | 39 | work-bench.com/portfolio (`workbench_scraper.py`) |
| 3one4 Capital | `3one4capital_companies.json` | 63 | 3one4capital.com/portfolio — Webflow (Finsweet) + detail pages (`3one4capital_scraper.py`) |
| AirTree Ventures | `airtree_companies.json` | 118 | airtree.vc/companies — Webflow (Finsweet) + detail pages (`airtree_scraper.py`) |
| Blackbird Ventures | `blackbird_companies.json` | 142 | blackbird.vc/portfolio — Webflow paginated + detail pages (`blackbird_scraper.py`) |
| byFounders | `byfounders_companies.json` | 79 | byfounders.vc/portfolio — embedded serialized data (no site descriptions; filled from company sites) (`byfounders_scraper.py`) |
| Capnamic | `capnamic_companies.json` | 71 | capnamic.com/portfolio — Webflow rows (`capnamic_scraper.py`) |
| Elevation Capital | `elevationcapital_companies.json` | 114 | elevationcapital.com/portfolio — __NEXT_DATA__ (`elevationcapital_scraper.py`) |
| Fabric Ventures | `fabricventures_companies.json` | 156 | fabric.vc/portfolio — Webflow (Finsweet) paginated + detail pages (`fabricventures_scraper.py`) |
| Golden Ventures | `goldenventures_companies.json` | 121 | golden.ventures/portfolio — Webflow paginated + detail pages (`goldenventures_scraper.py`) |
| Mercury Fund | `mercuryfund_companies.json` | 80 | mercuryfund.com/portfolio — Webflow lists + modals (`mercuryfund_scraper.py`) |
| MMC Ventures | `mmcventures_companies.json` | 93 | mmc.vc/portfolio — WP + detail pages (`mmcventures_scraper.py`) |
| Nauta Capital | `nautacapital_companies.json` | 92 | nautacapital.com/portfolio — Webflow paginated (`nautacapital_scraper.py`) |
| Next47 | `next47_companies.json` | 58 | n47.com/portfolio — Webflow + detail pages (`next47_scraper.py`) |
| Qualcomm Ventures | `qualcommventures_companies.json` | 257 | qualcommventures.com — WP REST companies + taxonomies (`qualcommventures_scraper.py`) |
| Real Ventures | `realventures_companies.json` | 117 | realventures.com/portfolio — WP grid + modals (`realventures_scraper.py`) |
| Samaipata | `samaipata_companies.json` | 42 | samaipata.vc/our-portfolio — Webflow (Finsweet) + detail pages (`samaipata_scraper.py`) |
| Spero Ventures | `spero_companies.json` | 28 | spero.vc/portfolio — WP cards (displayed companies only) (`spero_scraper.py`) |
| Square Peg | `squarepeg_companies.json` | 81 | squarepeg.vc/portfolio — Webflow (Finsweet) + detail pages (`squarepeg_scraper.py`) |
| Stellaris Venture Partners | `stellaris_companies.json` | 53 | stellarisvp.com/portfolio — Webflow (Finsweet) + detail pages (`stellaris_scraper.py`) |
| Volition Capital | `volitioncapital_companies.json` | 57 | volitioncapital.com/portfolio — WP HTML + detail pages (`volitioncapital_scraper.py`) |
| XAnge | `xange_companies.json` | 147 | xange.vc — Prismic API (`xange_scraper.py`) |
| 4DX Ventures | `4dxventures_companies.json` | 52 | 4dxventures.com/portfolio — Webflow (Finsweet) modals; exited cards remapped to the acquired company (`4dxventures_scraper.py`) |
| Aleph | `aleph_companies.json` | 64 | aleph.vc/companies — Webflow grid + list-js data (`aleph_scraper.py`) |
| BEENEXT | `beenext_companies.json` | 141 | beenext.com/portfolio — WP + Search & Filter Pro paged list (`beenext_scraper.py`) |
| Cyberstarts | `cyberstarts_companies.json` | 27 | cyberstarts.com/portfolio — Webflow (Finsweet) + detail pages (`cyberstarts_scraper.py`) |
| East Ventures | `eastventures_companies.json` | 380 | east.vc/portfolio — WP REST portfolio CPT + taxonomies (no company websites on-site) (`eastventures_scraper.py`) |
| Elaia | `elaia_companies.json` | 201 | elaia.com/portfolio — Payload CMS public REST (`elaia_scraper.py`) |
| Folklore Ventures | `folklore_companies.json` | 33 | folklore.vc/companies — Webflow list (`folklore_scraper.py`) |
| Heartcore Capital | `heartcore_companies.json` | 93 | heartcore.com/companies — Webflow (Finsweet) paginated table; some descriptions filled from company sites (`heartcore_scraper.py`) |
| Kapor Capital | `kaporcapital_companies.json` | 188 | kaporcapital.com/portfolio — WP grid (?current_page=N) + detail pages (`kaporcapital_scraper.py`) |
| Kaszek | `kaszek_companies.json` | 125 | kaszek.com/companies — WP REST company CPT + detail pages (`kaszek_scraper.py`) |
| Maveron | `maveron_companies.json` | 81 | maveron.com/portfolio — Webflow (Finsweet) active/exits; some descriptions filled from company sites (`maveron_scraper.py`) |
| Octopus Ventures | `octopusventures_companies.json` | 306 | octopusventures.com/portfolio — WP archive pages (current/exited) (`octopusventures_scraper.py`) |
| Panache Ventures | `panache_companies.json` | 83 | panache.vc/portfolio — Wix repeater (`panache_scraper.py`) |
| Pitango | `pitango_companies.json` | 142 | pitango.com/portfolio — WP cards + inline detail data (`pitango_scraper.py`) |
| Seaya | `seaya_companies.json` | 58 | seaya.vc/portfolio — WP (Salient) grid + detail pages (`seaya_scraper.py`) |
| Sierra Ventures | `sierraventures_companies.json` | 165 | sierraventures.com/portfolio — HubSpot inline JS array (`sierraventures_scraper.py`) |
| TLcom Capital | `tlcomcapital_companies.json` | 32 | tlcomcapital.com/portfolio — Webflow (Finsweet) list (`tlcomcapital_scraper.py`) |
| Viola Group | `viola_companies.json` | 118 | viola-group.com/portfolio — site JSON endpoint (portfolio-filter.php) (`viola_scraper.py`) |
| Vsquared Ventures | `vsquared_companies.json` | 38 | vsquared.vc/portfolio — WP + Search & Filter Pro cards (`vsquared_scraper.py`) |
| Wavemaker Ventures | `wavemaker_companies.json` | 219 | wavemaker.vc/portfolio — WP REST portfolio CPT + detail pages (`wavemaker_scraper.py`) |
| YL Ventures | `ylventures_companies.json` | 32 | ylventures.com/portfolio — WP HTML cards (HQ, founded, acquirer text) (`ylventures_scraper.py`) |
| Expa | `expa_companies.json` | 96 | expa.com/companies — HTML list; acquirer parsed from "Acquired by X" text (`expa_scraper.py`) |
| Ventures Platform | `venturesplatform_companies.json` | 80 | venturesplatform.com/portfolio — Webflow (Finsweet); Initial Investment -> stage (`venturesplatform_scraper.py`) |
| lool ventures | `lool_companies.json` | 38 | lool.vc/portfolio — WP HTML cards (invested-in year, acquirer, exit year) (`lool_scraper.py`) |
| Giant Leap | `giantleap_companies.json` | 36 | giantleap.com.au/portfolio — Webflow (Finsweet) list (`giantleap_scraper.py`) |
| Industrifonden | `industrifonden_companies.json` | 90 | industrifonden.com/portfolio — Webflow list (Active / Selected exits) (`industrifonden_scraper.py`) |
| Concept Ventures | `concept_companies.json` | 36 | concept.vc/portfolio — Webflow (Finsweet) + detail pages (`concept_scraper.py`) |
| Beringea | `beringea_companies.json` | 138 | beringea.com/portfolio — Next.js `__NEXT_DATA__` investments (UK/US fund kept as `fund`, not location) (`beringea_scraper.py`) |
| Visionaries Club | `visionaries_companies.json` | 59 | visionaries.vc — single-page HTML (thesis, published ARR / acquisitions only) (`visionaries_scraper.py`) |
| M13 | `m13_companies.json` | 163 | m13.co/portfolio — Webflow paginated list (no company websites on-site) (`m13_scraper.py`) |
| Luminar Ventures | `luminar_companies.json` | 39 | luminarventures.com/portfolio — Webflow (Finsweet) + detail pages (`luminar_scraper.py`) |
| B Capital | `bcapital_companies.json` | 135 | b.capital/portfolio — WP page's embedded `orig_data` JS array (region, status, website) (`bcapital_scraper.py`) |
| Novastar Ventures | `novastar_companies.json` | 24 | novastarventures.com/portfolio — WP grid + case-study pages (timeline -> first_invested / entry round) (`novastar_scraper.py`) |
| b2venture | `b2venture_companies.json` | 193 | b2venture.vc/portfolio (btov) — Webflow (Finsweet) paginated table (Since, Region; Trade Sale/IPO labels) (`b2venture_scraper.py`) |
| Grove Ventures | `grove_companies.json` | 35 | grovevc.com/grove-portfolio-companies — WP grid (names from card classes; detail pages WAF-blocked; stealth cards skipped) (`grove_scraper.py`) |
| Vertex Ventures US | `vertexus_companies.json` | 60 | vvus.com/portfolio — Gatsby page-data static query (Storyblok projects) (`vertexus_scraper.py`) |
| NordicNinja | `nordicninja_companies.json` | 27 | nordicninja.com/portfolio — WP cards (industry, series) + detail pages (`nordicninja_scraper.py`) |
| Bling Capital | `bling_companies.json` | 213 | blingcap.com/portfolio — Next.js SSR cards (Acquired by X / Public: TICKER) (`bling_scraper.py`) |
| Newion | `newion_companies.json` | 58 | newion.com/portfolio — Webflow rows + popups (city, investment year, active/exited) (`newion_scraper.py`) |
| GroundUp Ventures | `groundup_companies.json` | 58 | groundup.vc/portfolio — Webflow lightboxes (current stage, stage invested, location, acquirer) (`groundup_scraper.py`) |
| Acton Capital | `acton_companies.json` | 80 | actoncapital.com/portfolio — Webflow list + detail pages (founders, HQ, investment year, acquirer) (`acton_scraper.py`) |
| Connect Ventures | `connect_companies.json` | 109 | connectventures.co/companies — Webflow (Finsweet) paginated + detail pages (country, founders, first investment year; retired kept as site_status) (`connect_scraper.py`) |
| Chrysalix Venture Capital | `chrysalix_companies.json` | 23 | chrysalix.com/portfolio — Framer HTML (fund, sector, active/exited) (`chrysalix_scraper.py`) |
| VentureFriends | `venturefriends_companies.json` | 63 | venturefriends.vc/portfolio — Webflow paginated + detail pages (founded, location, last funding round, exits) (`venturefriends_scraper.py`) |
| Astanor | `astanor_companies.json` | 57 | astanor.com/portfolio — WP cards + detail pages (location, Seed stage; Venture/Growth kept as investment_stage) (`astanor_scraper.py`) |
| Cathay Innovation | `cathay_companies.json` | 117 | cathayinnovation.com/portfolio — co-card data attributes (entry round, investment year, acquired/IPO) (`cathay_scraper.py`) |
| Maki.vc | `maki_companies.json` | 58 | maki.vc — WP REST `case` type + detail pages (stage, latest round amount, industry, acquirer) (`maki_scraper.py`) |
| Salesforce Ventures | `salesforceventures_companies.json` | 613 | salesforceventures.com/portfolio — WP REST `companies` + detail pages (focus areas, sales region kept as region not location, Acquired text; CMS duplicates merged by name+domain) (`salesforceventures_scraper.py`) |
| Sofinnova Partners | `sofinnova_companies.json` | 143 | sofinnovapartners.com/portfolio — Next.js `__NEXT_DATA__` list + detail pages (live/acquired, acquirer) (`sofinnova_scraper.py`) |
| Nexus Venture Partners | `nexus_companies.json` | 149 | nexusvp.com/companies — Webflow (Finsweet) hidden list fields (country, outcome, sectors, stage; no websites on-site) (`nexus_scraper.py`) |
| Contrary | `contrary_companies.json` | 42 | contrary.com/companies — Next.js/Prismic SSR (curated list only) (`contrary_scraper.py`) |
| Dawn Capital | `dawn_companies.json` | 49 | dawncapital.com/companies — Next.js (Sanity) list + detail pages (founders, founded, invested year, HQ, sector, Exited / Acquired by) (`dawn_scraper.py`) |
| OMERS Ventures | `omers_companies.json` | 77 | omersventures.com/companies — Next.js RSC Contentful entries (industry, region, current/former); descriptions filled from company sites/Wikidata (`omers_scraper.py`) |
| Samsung Next | `samsungnext_companies.json` | 352 | samsungnext.com/portfolio — Webflow page's CDN JSON (`_pf-companies-v2.json`: name, sector, website); descriptions filled from company sites/Wikidata (`samsungnext_scraper.py`) |
| Illuminate Ventures | `illuminate_companies.json` | 33 | illuminate.com/portfolio-2 — WP isotope grid (current/exited) + project pages (acquirer, exit year) (`illuminate_scraper.py`) |
| Amadeus Capital Partners | `amadeus_companies.json` | 66 | amadeuscapital.com/our-companies — WP REST `company` (situation, area) + detail pages (About copy, acquirer/exit year, IPO) (`amadeus_scraper.py`) |
| Blumberg Capital | `blumberg_companies.json` | 114 | blumbergcapital.com/portfolio-companies — Beaver Builder grid (Acquired/IPO badges, fund type) + detail pages (`blumberg_scraper.py`) |
| Root Ventures | `rootventures_companies.json` | 68 | root.vc (#tldr) — static page JSON-LD Organizations with funder = Root (name, one-liner, website) (`rootventures_scraper.py`) |
| 3VC | `threevc_companies.json` | 24 | three.vc/portfolio — server-rendered cards (Alumni badge, Acquired by X in YYYY) + detail pages (`threevc_scraper.py`) |
| Kima Ventures | `kima_companies.json` | 982 | kimaventures.com/portfolio — Next.js `__NEXT_DATA__` companies (description, Kima sectors, country) (`kima_scraper.py`) |
| Stage 2 Capital | `stage2_companies.json` | 106 | stage2.capital/portfolio — HubSpot card data-* attrs (why-invested blurb, HQ location, founders, industry, entry round, year invested) (`stage2_scraper.py`) |
| 5AM Ventures | `fiveam_companies.json` | 87 | 5amventures.com/portfolio — WP list data-attrs (description, website, facts: based in / founded / IPO / acquired, therapeutic focus) (`fiveam_scraper.py`) |
| Next Coast Ventures | `nextcoast_companies.json` | 77 | nextcoastventures.com/portfolio — Webflow CMS (description, website, sector, Sold → acquired) (`nextcoast_scraper.py`) |
| Converge | `converge_companies.json` | 68 | converge.vc/portfolio — WP blocks (one-line description, website) (`converge_scraper.py`) |
| 1kx | `onekx_companies.json` | 84 | 1kx.capital/portfolio — SSR cards (year invested, description, website, Invested/Exited label) (`onekx_scraper.py`) |
| Variant | `variant_companies.json` | 48 | variant.fund/portfolio — WP cards (entry round + year, category, website); descriptions from company sites via fill_descriptions_web (`variant_scraper.py`) |
| Mantis VC | `mantis_companies.json` | 134 | mantisvc.com/portfolio — Webflow slides (description, website) (`mantis_scraper.py`) |
| Clean Energy Ventures | `cleanenergyventures_companies.json` | 31 | cleanenergyventures.com/portfolio — Webflow cards (sector badge, description, website, co-investors) (`cleanenergyventures_scraper.py`) |
| Drive Capital | `drivecapital_companies.json` | 83 | drivecapital.com/portfolio — Next.js `__NEXT_DATA__` list + detail pages (description, website, HQ city, status, industry) (`drivecapital_scraper.py`) |
| High-Tech Gründerfonds | `htgf_companies.json` | 540 | htgf.de/en/portfolio — WP REST `portfolio` list + detail pages (about text, website, invested-since year, based-in city, sectors; "(Exit)" → site_status) (`htgf_scraper.py`) |
| Pioneer Square Labs | `psl_companies.json` | 54 | psl.com/companies — Webflow grid + detail pages (description, website, year + vehicle, founders, ACQUIRED flag) (`psl_scraper.py`) |
| Qiming Venture Partners | `qiming_companies.json` | 426 | qimingvc.com/en/portfolio — server-rendered list (sector, one-line description, website) (`qiming_scraper.py`) |
| AlleyCorp | `alleycorp_companies.json` | 152 | alleycorp.com/companies — WP post grid (Incubation/Investment, status, description, website; incubation detail pages add founders) (`alleycorp_scraper.py`) |
| Samsara BioCapital | `samsara_companies.json` | 75 | samsaracap.com/portfolio — Elementor blocks (name, description only) (`samsara_scraper.py`) |
| Chicago Ventures | `chicagoventures_companies.json` | 105 | chicagoventures.com/companies — Webflow table (current round, CV-invested year + entry round, status, industry, description) (`chicagoventures_scraper.py`) |
| Foresite Capital | `foresite_companies.json` | 183 | foresitecapital.com/portfolio — WP list + detail pages (description, website, ticker, alumni flag, category) (`foresite_scraper.py`) |
| Revolution | `revolution_companies.json` | 251 | revolution.com/portfolio — Webflow/Finsweet paginated list (description, website, HQ, fund, sector, Active/Realized, acquirer) (`revolution_scraper.py`) |
| Trinity Ventures | `trinity_companies.json` | 41 | trinityventures.com/portfolio — grid + detail pages (description, website, Acquired/IPO badge) (`trinity_scraper.py`) |
| Endiya Partners | `endiya_companies.json` | 36 | endiya.com/portfolio — Webflow list + detail pages (description, website, founders, milestones → partnered year + latest round, status) (`endiya_scraper.py`) |
| AgFunder | `agfunder_companies.json` | 78 | agfunder.com/portfolio — WP archive + detail pages (summary, region, sector labels, [EXITED] flag) (`agfunder_scraper.py`) |
| Intel Capital | `intelcapital_companies.json` | 137 | intelcapital.com/portfolio — SSR .company cards (name via a[alt]/company-title, spotlight blurb, sector CSS classes, region) (`intelcapital_scraper.py`) |
| 360 Capital | `threesixtycapital_companies.json` | 95 | 360cap.vc/portfolio — Webflow CMS + detail pages (sector, HQ, description, Exited/Current, Visit website) (`threesixtycapital_scraper.py`) |
| Hack VC | `hackvc_companies.json` | 100 | hack.vc/portfolio — SSR .hc_portfolio-post cards (name, description, sector tags) (`hackvc_scraper.py`) |
| Equal Ventures | `equal_companies.json` | 24 | equal.vc/portfolio — Webflow .portfolio-item + detail pages (description, website) (`equal_scraper.py`) |
| StandUp Ventures | `standup_companies.json` | 38 | standupvc.com/portfolio — Webflow + detail pages (description, founders, sector, location, status, website) (`standup_scraper.py`) |
| Flagship Pioneering | `flagship_companies.json` | 37 | flagshippioneering.com/companies — grid + detail pages (launch year, description, website) (`flagship_scraper.py`) |
| Liquid 2 Ventures | `liquid2_companies.json` | 15 | liquid2.vc/portfolio — Webflow cards (description, website) (`liquid2_scraper.py`) |
| Flourish Ventures | `flourish_companies.json` | 113 | flourishventures.com/portfolio — WP REST portfolio (excerpt, investment-themes / region / funding-series class_list) (`flourish_scraper.py`) |
| ff Venture Capital | `ffvc_companies.json` | 123 | ffvc.com/portfolio — WP REST portfolio titles (detail pages logo-only; descriptions not published) (`ffvc_scraper.py`) |
| United Ventures | `unitedventures_companies.json` | 30 | unitedventures.com/portfolio — WP REST content HTML (website, Sector, Founder, description) (`unitedventures_scraper.py`) |
| TLV Partners | `tlv_companies.json` | 64 | tlv.partners/portfolio — SSR .tlv_company drawers (sector, entry-stage, website, tagline, description) (`tlv_scraper.py`) |
| Quona Capital | `quona_companies.json` | 58 | quona.com/portfolio — on-page company blocks (tagline, description, website, region) (`quona_scraper.py`) |
| Molten Ventures | `molten_companies.json` | 105 | moltenventures.com/portfolio/all — .portfolio-row (sector, description, Invested In year, website) (`molten_scraper.py`) |
| BMW i Ventures | `bmwiventures_companies.json` | 89 | bmwiventures.com/portfolio — Webflow cards (description, HQ, sector, status/IPO/acquired, website) (`bmwiventures_scraper.py`) |
| Framework Ventures | `framework_companies.json` | 17 | framework.ventures/portfolio — list items (name, website; crypto fund — descriptions not on index) (`framework_scraper.py`) |
| MPM BioImpact | `mpmbioimpact_companies.json` | 20 | mpmbioimpact.com/portfolio — logo grid (names from img alt; bio fund) (`mpmbioimpact_scraper.py`) |
| IDG Capital | `idgcapital_companies.json` | 77 | idgcapital.com/portfolio — WP REST English permalinks (sector + region taxonomies; descriptions not in REST) (`idgcapital_scraper.py`) |
| Team8 | `team8_companies.json` | 12 | team8.vc/portfolio — .portfolio-card + detail pages (tagline, founded year, website) (`team8_scraper.py`) |
| HV Capital | `hvcapital_companies.json` | 10 | hvcapital.com/portfolio — Framer companies table SSR featured set (name, description, sector, Early/Growth label) (`hvcapital_scraper.py`) |
| DCM Ventures | `dcm_companies.json` | 16 | dcm.com/companies — Webflow featured cards (name, sector, website) (`dcm_scraper.py`) |
| Wellington Management | `wellington_companies.json` | 215 | wellington.com/.../our-investments — AEM content-fragment data-layer (description, sector, URL, realized/unrealized) (`wellington_scraper.py`) |
| Creandum | `creandum_companies.json` | 155 | creandum.com/commitments — Contentful/Vue .portfolio-card (logo alt name, description, exited class; websites not on index) (`creandum_scraper.py`) |
| Sony Innovation Fund | `sonyinnovation_companies.json` | 196 | sonyinnovationfund.com/portfolio — .portfolio-item (name, website, category CSS; descriptions not on index) (`sonyinnovation_scraper.py`) |
| Blume Ventures | `blume_companies.json` | 161 | blume.vc/startups — schema.org ItemList + detail pages (description, website, Active/Exited) (`blume_scraper.py`) |
| Shrug Capital | `shrug_companies.json` | 97 | shrug.vc/portfolio — Webflow CMS (name, description, website) (`shrug_scraper.py`) |
| Joyance Partners | `joyance_companies.json` | 177 | joyancepartners.com/portfolio — Webflow cards (name + description; websites not on index) (`joyance_scraper.py`) |
| Commerce Ventures | `commerceventures_companies.json` | 113 | commerce.vc/portfolio — .portfolio anchors (website; names from domain; fintech focus) (`commerceventures_scraper.py`) |
| Hg | `hg_companies.json` | 100 | hgcapital.com/portfolio — Next.js `__NEXT_DATA__` total.items (+ featured shortDescription/country/partnered year) (`hg_scraper.py`) |
| Day One Ventures | `dayone_companies.json` | 83 | dayoneventures.com — Next.js `__NEXT_DATA__` companies (domain→name, mission, category, exit) (`dayone_scraper.py`) |
| Higher Ground Labs | `higherground_companies.json` | 80 | highergroundlabs.com/portfolio — JetEngine grid + detail pages (description, website, ACQUIRED) (`higherground_scraper.py`) |
| Version One Ventures | `versionone_companies.json` | 82 | versionone.vc/portfolio — WP gallery captions/alts (names; websites/descriptions not on index) (`versionone_scraper.py`) |
| Compound | `compound_companies.json` | 68 | compound.vc/portfolio — Webflow cards (name, website; descriptions not on index) (`compound_scraper.py`) |
| Origin Ventures | `originventures_companies.json` | 55 | originventures.com/portfolio — Squarespace gallery (caption description, website) (`originventures_scraper.py`) |
| 1confirmation | `oneconfirmation_companies.json` | 51 | 1confirmation.com/portfolio — Squarespace gallery (website, Initial Investment date; crypto fund) (`oneconfirmation_scraper.py`) |
| Valor Equity Partners | `valor_companies.json` | 50 | valorep.com/growth-investments — Squarespace slides (img alt name, website; descriptions not on index) (`valor_scraper.py`) |
| Corazon Capital | `corazon_companies.json` | 96 | corazon.com/portfolio — Wix repeater (company websites; names from domain) (`corazon_scraper.py`) |
| Fuel Capital | `fuelcapital_companies.json` | 34 | fuelcapital.com/portfolio — Squarespace slides (img alt name, website) (`fuelcapital_scraper.py`) |
| Round13 Capital | `round13_companies.json` | 35 | round13.com/portfolio — Elementor grid + detail pages (description, website) (`round13_scraper.py`) |
| Relay Ventures | `relayventures_companies.json` | 35 | relayventures.com/portfolio — .team-block website links (names from domain) (`relayventures_scraper.py`) |
| Ludlow Ventures | `ludlow_companies.json` | 34 | ludlowventures.com — homepage logo grid (img alt names; websites/descriptions not published) (`ludlow_scraper.py`) |
| OCA Ventures | `ocaventures_companies.json` | 75 | ocaventures.com/portfolio — .card-reveal cards (description, website, location, entry round from "Partnered since", acquirer) (`ocaventures_scraper.py`) |
| Moxxie Ventures | `moxxie_companies.json` | 69 | moxxie.vc homepage CMS logo collection + featured slider (description, website, category, acquired) (`moxxie_scraper.py`) |
| Kibo Ventures | `kibo_companies.json` | 67 | kiboventures.com/portfolio — Webflow hidden data fields (website, unlabeled date kept as first_invested, fund, exits); descriptions filled from company sites (`kibo_scraper.py`) |
| Lifeline Ventures | `lifeline_companies.json` | 140 | lifelineventures.com/companies — .companies__item funding timeline (entry round, first invested, last financing, current/exited) (`lifeline_scraper.py`) |
| Peak Capital | `peakcapital_companies.json` | 69 | peak.capital WP REST /wp-json/wp/v2/founders + businessmodel taxonomy (website = root domain of jobs link, founders) (`peakcapital_scraper.py`) |
| JMI Equity | `jmi_companies.json` | 135 | jmi.com/portfolio — #results items + popups (description, website, current/acquired, IPO detail) (`jmi_scraper.py`) |
| Energize Capital | `energize_companies.json` | 40 | energize.vc/portfolio — Webflow grid (names from why-we-invested slug/logo file, website, SINCE year) (`energize_scraper.py`) |
| Play Ventures | `playventures_companies.json` | 89 | playventures.vc/portfolio — Webflow + Finsweet (description, website, stage, location, active/exit) (`playventures_scraper.py`) |
| Point72 Ventures | `point72ventures_companies.json` | 162 | p72.vc/portfolio — .c-portfolio__accordion (description, website, location, stage, first invested, active) (`point72ventures_scraper.py`) |
| Ten Eleven Ventures | `teneleven_companies.json` | 66 | 1011vc.com/portfolio — Webflow CMS (description, website, location, first invested, status) (`teneleven_scraper.py`) |
| Spectrum Equity | `spectrumequity_companies.json` | 97 | spectrumequity.com/portfolio — Nuxt _payload.json landing + per-company payloads (website from ctaLink; some point to acquirer) (`spectrumequity_scraper.py`) |
| Five Elms Capital | `fiveelms_companies.json` | 70 | fiveelms.com/portfolio — grid descriptors, location, active/exited (no websites; detail pages bot-walled) (`fiveelms_scraper.py`) |
| Edison Partners | `edison_companies.json` | 56 | edisonpartners.com/portfolio — detail pages (description, website, location, first invested, status) (`edison_scraper.py`) |
| Space Capital | `spacecapital_companies.json` | 65 | spacecapital.com/portfolio — Webflow CMS (description, website, location, year founded) (`spacecapital_scraper.py`) |
| Makers Fund | `makersfund_companies.json` | 92 | makersfund.com/portfolio — Next.js __NEXT_DATA__ companies (founders, location, active/exited + acquirer); no descriptions/websites published, some filled from company sites (`makersfund_scraper.py`) |
| Monk's Hill Ventures | `monkshill_companies.json` | 38 | monkshill.com/portfolio — Webflow grid sector + /portfolio/<slug> title/meta description (no websites) (`monkshill_scraper.py`) |
| Jump Capital | `jumpcapital_companies.json` | 97 | jumpcap.com/portfolio — modal stubs (active/exited, vertical) + site's public fetch_modal_content admin-ajax (description, founders; no websites) (`jumpcapital_scraper.py`) |
| Castle Island Ventures | `castleisland_companies.json` | 68 | castleisland.vc WP REST /wp-json/wp/v2/portfolios (description, category) + /portfolio/ loop pages for website (acquirer links kept as linked_site) (`castleisland_scraper.py`) |
| 7wireVentures | `sevenwire_companies.json` | 31 | 7wireventures.com/portfolio — WPBakery grid + detail pages (overview, website, founded, HQ, CEO, exited) (`sevenwire_scraper.py`) |
| Crosscut Ventures | `crosscut_companies.json` | 90 | crosscut.vc/companies — cards + site's loadmorebutton admin-ajax (description, founder/CEO, location, sector, website) (`crosscut_scraper.py`) |
| Bonfire Ventures | `bonfire_companies.json` | 133 | bonfirevc.com/companies — Webflow CMS (tagline, website, location, industry, partnered year) (`bonfire_scraper.py`) |
| TenOneTen | `tenoneten_companies.json` | 100 | tenoneten.net/portfolio — Webflow CMS list (name, one-line description) (`tenoneten_scraper.py`) |
| Contour Venture Partners | `contour_companies.json` | 83 | contourventures.com/portfolio — Elementor portfolio popups (description, website, acquired) (`contour_scraper.py`) |
| Valor Capital Group | `valorcapital_companies.json` | 125 | valorcapitalgroup.com/companies — SSR data-* cards (description, website, location, Exit badge) (`valorcapital_scraper.py`) |
| FTV Capital | `ftvcapital_companies.json` | 120 | ftvcapital.com WP REST portfolio_item + detail pages (website when published) (`ftvcapital_scraper.py`) |
| Polaris Partners | `polaris_companies.json` | 144 | polarispartners.com WP REST company-api ACF (description, website, location, healthcare/tech, exit_info) (`polaris_scraper.py`) |
| Forgepoint Capital | `forgepoint_companies.json` | 79 | forgepointcap.com WP REST company + sector/status/location taxonomies + detail websites (`forgepoint_scraper.py`) |
| Evolution Equity Partners | `evolutionequity_companies.json` | 61 | evolutionequity.com WP REST companies + theme/status/stage taxonomies (`evolutionequity_scraper.py`) |
| Glilot Capital | `glilot_companies.json` | 57 | glilotcapital.com WP REST clubs + clubs-category (`glilot_scraper.py`) |
| G Squared | `gsquared_companies.json` | 44 | gsquared.com/portfolio — SSR article cards (names; detail pages thin) (`gsquared_scraper.py`) |
| Fifth Wall | `fifthwall_companies.json` | 16 | fifthwall.com/portfolio — Webflow CMS (description, website; exit/IPO in name suffix). Page shows a featured subset (`fifthwall_scraper.py`) |
| Orange Collective | `orangecollective_companies.json` | 122 | orangecollective.vc/portfolio — JSON-LD ItemList + detail pages (YC batch, description) (`orangecollective_scraper.py`) |
| VestedVC | `vestedvc_companies.json` | 30 | vestedvc.com/portfolio — SSR cards (description, website, Active/Exit) (`vestedvc_scraper.py`) |
| Fly Ventures | `flyventures_companies.json` | 6 | fly.vc/portfolio — SSR company→website links (small published set) (`flyventures_scraper.py`) |
| Better Tomorrow Ventures | `btv_companies.json` | 8 | btv.vc homepage — portfolio name→website links (small published set) (`btv_scraper.py`) |
| QED Investors | `qed_companies.json` | 100 | qedinvestors.com/companies — Webflow CMS (status, sector, location/country) (`qed_scraper.py`) |
| Third Rock Ventures | `thirdrock_companies.json` | 74 | thirdrockventures.com/portfolio — SSR cards via data-slug (biotech; detail pages JS-only) (`thirdrock_scraper.py`) |
| Flare Capital Partners | `flarecapital_companies.json` | 84 | flarecapital.com WP REST company (status/stage/sector via class_list) (`flarecapital_scraper.py`) |
| Hetz Ventures | `hetz_companies.json` | 37 | hetz.vc/our-portfolio — Webflow CMS (tagline, website, sector, partnered year, acquired) (`hetz_scraper.py`) |
| Peak XV Partners | `peakxv_companies.json` | 94 | peakxv.com/our-companies — Webflow CMS (logo alt name, one-line description) (`peakxv_scraper.py`) |
| Boost VC | `boostvc_companies.json` | 270 | boost.vc/companies — Airtable proxy API (one-liner, website, location, year, category) (`boostvc_scraper.py`) |
| Dragonfly | `dragonfly_companies.json` | 123 | dragonfly.com Nuxt __NUXT_DATA__ Sanity portfolioItem (description, category, website) (`dragonfly_scraper.py`) |
| Multicoin Capital | `multicoin_companies.json` | 155 | multicoin.capital Gatsby page-data Contentful projects (description, category, website) (`multicoin_scraper.py`) |
| Betaworks | `betaworks_companies.json` | 119 | betaworks.com/companies — Webflow logo grid (website; name from domain) (`betaworks_scraper.py`) |
| Cherry Ventures | `cherry_companies.json` | 96 | cherry.vc founder-companies detail pages via sitemap (description, website) (`cherry_scraper.py`) |
| Chiratae Ventures | `chiratae_companies.json` | 85 | chiratae.com/companies — Elementor cards (website, first year) (`chiratae_scraper.py`) |
| IQ Capital | `iqcapital_companies.json` | 76 | iqcapital.vc/companies — Webflow feed cards (one-liner, stage/status) (`iqcapital_scraper.py`) |
| Flybridge | `flybridge_companies.json` | 72 | flybridge.com/portfolio — Squarespace logo grid (website; name from domain) (`flybridge_scraper.py`) |
| Long Journey Ventures | `longjourney_companies.json` | 63 | longjourney.vc/portfolio — Squarespace logo grid (website; name from domain) (`longjourney_scraper.py`) |
| Ada Ventures | `ada_companies.json` | 55 | adaventures.com Webflow /company details (website, theme, stage) (`ada_scraper.py`) |
| Section 32 | `section32_companies.json` | 29 | s32.com Select Companies links (featured subset) (`section32_scraper.py`) |
| Accomplice | `accomplice_companies.json` | 25 | accomplice.co homepage portfolio links (`accomplice_scraper.py`) |
| Character | `character_companies.json` | 28 | character.vc homepage portfolio links (`character_scraper.py`) |
| Weekend Fund | `weekend_companies.json` | 29 | weekend.fund homepage cards (one-liner, website) (`weekend_scraper.py`) |
| Hiro Capital | `hiro_companies.json` | 33 | hiro.capital/companies cards (sectors, year, website) (`hiro_scraper.py`) |
| CoinFund | `coinfund_companies.json` | 13 | coinfund.io/portfolio featured Visit Website links (subset) (`coinfund_scraper.py`) |
| Monashees | `monashees_companies.json` | 13 | monashees.com/portfolio Framer featured companies (subset) (`monashees_scraper.py`) |
| Electric Capital | `electric_companies.json` | 12 | electriccapital.com __NEXT_DATA__ homeLogoCompanies (featured subset) (`electric_scraper.py`) |
| Breega | `breega_companies.json` | 9 | breega.com homepage featured company headings (subset) (`breega_scraper.py`) |
| Griffin Gaming Partners | `griffin_companies.json` | 8 | griffingp.com homepage Our Portfolio logo links (featured subset) (`griffin_scraper.py`) |
| Cota Capital | `cota_companies.json` | 137 | cotacapital.com/companies embedded JSON (description, website, sectors) (`cota_scraper.py`) |
| Digital Currency Group | `dcg_companies.json` | 316 | dcg.co/portfolio Webflow (description, website, category) (`dcg_scraper.py`) |
| Garage Capital | `garage_companies.json` | 159 | garage.vc Webflow list (description, website) (`garage_scraper.py`) |
| Designer Fund | `designerfund_companies.json` | 88 | designerfund.com Framer tiles (description, website) (`designerfund_scraper.py`) |
| Hashed | `hashed_companies.json` | 159 | hashed.com/portfolio Gatsby HTML (description, website, category) (`hashed_scraper.py`) |
| Teamworthy Ventures | `teamworthy_companies.json` | 103 | teamworthy.com/portfolio cards (description, website, exits; names from description/domain) (`teamworthy_scraper.py`) |
| Lightstone Ventures | `lightstone_companies.json` | 60 | lightstonevc.com WP REST portfolio (description, status) (`lightstone_scraper.py`) |
| RA Capital Management | `racapital_companies.json` | 251 | racap.com/portfolio + detail pages (description, website, exits) (`racapital_scraper.py`) |
| Longitude Capital | `longitude_companies.json` | 104 | longitudecapital.com portfolio pages (description, website, status) (`longitude_scraper.py`) |
| K Fund | `kfund_companies.json` | 127 | kfund.vc homepage list (website, exits/acquirer, closed; no descriptions) (`kfund_scraper.py`) |
| Voyager Ventures | `voyager_companies.json` | 39 | voyagervc.com/portfolio Webflow paginated (description, website) (`voyager_scraper.py`) |
| GreatPoint Ventures | `greatpoint_companies.json` | 83 | gpv.com/companies Webflow (description, website) (`greatpoint_scraper.py`) |
| Microtraction | `microtraction_companies.json` | 66 | microtraction.com/portfolio Webflow (description, website) (`microtraction_scraper.py`) |
| Lumira Ventures | `lumira_companies.json` | 56 | lumiraventures.com/portfolio (description, website, status) (`lumira_scraper.py`) |
| Vendep Capital | `vendep_companies.json` | 35 | vendep.com/portfolio Webflow (description, website, latest funding) (`vendep_scraper.py`) |
| Prime Venture Partners | `primevp_companies.json` | 54 | primevp.in __NEXT_DATA__ (description, website, funding rounds) (`primevp_scraper.py`) |
| Inovo VC | `inovo_companies.json` | 45 | inovo.vc Notion table (website, entry round, acquirer; no descriptions) (`inovo_scraper.py`) |
| Frst | `frst_companies.json` | 37 | frst.vc Webflow (description, website) (`frst_scraper.py`) |
| F2 Venture Capital | `f2_companies.json` | 24 | f2vc.com/companies Webflow (description, website) (`f2_scraper.py`) |
| N49P | `n49p_companies.json` | 87 | n49p.com/portfolio Webflow paginated (description, website) (`n49p_scraper.py`) |
| Alta Partners | `alta_companies.json` | 28 | altapartners.com/portfolio modals (bio, location, industry, status, fund) (`alta_scraper.py`) |
| Sawari Ventures | `sawari_companies.json` | 19 | sawariventures.com/portfolio Elementor (description, website) (`sawari_scraper.py`) |
| Gaingels | `gaingels_companies.json` | 2867 | gaingels.com WP REST company (description, website, rounds, status; merged by name) (`gaingels_scraper.py`) |
| Passion Capital | `passion_companies.json` | 112 | passioncapital.com WP REST fund-portfolio + pages (description, website) (`passion_scraper.py`) |
| P101 Ventures | `p101_companies.json` | 69 | p101.it WP REST cwp_company (description, website, sector) (`p101_scraper.py`) |
| Augmentum Fintech | `augmentum_companies.json` | 34 | augmentum.vc WP REST portfolio (description, website) (`augmentum_scraper.py`) |
| Kae Capital | `kae_companies.json` | 47 | kae-capital.com WP REST investments + pages (description, year founded/invested, partner) (`kae_scraper.py`) |
| Alpha Partners | `alphapartners_companies.json` | 42 | alphapartners.com WP REST portfolio-item + pages (description, website, status, founded/partnered) (`alphapartners_scraper.py`) |
| Glasswing Ventures | `glasswing_companies.json` | 75 | glasswing.vc/our-companies cards (description, website, partner, acquirer) (`glasswing_scraper.py`) |
| Portage | `portage_companies.json` | 111 | portageinvest.com/portfolio Webflow paginated (description, website, sector, region, fund) (`portage_scraper.py`) |
| M Ventures | `mventures_companies.json` | 86 | m-ventures.com/portfolio + pages (description, website, investment lead, exit) (`mventures_scraper.py`) |
| Bain Capital Life Sciences | `baincapitalls_companies.json` | 79 | baincapitallifesciences.com/portfolio + pages (description, website, year, current/former) (`baincapitalls_scraper.py`) |
| World Fund | `worldfund_companies.json` | 23 | worldfund.vc/portfolio + pages (description, website, location, founded, rounds) (`worldfund_scraper.py`) |
| Frazier Life Sciences | `frazier_companies.json` | 122 | frazierls.com/portfolio modals (description, website, status, therapeutic area, modality, year invested) (`frazier_scraper.py`) |
| Algebra Ventures | `algebra_companies.json` | 33 | algebraventures.com project offcanvas (story, website, fund, team) (`algebra_scraper.py`) |
| Rally Ventures | `rally_companies.json` | 16 | rallyventures.com investment panes (description, website, acquirer/IPO) (`rally_scraper.py`) |
| 10D | `tend_companies.json` | 49 | 10d.vc WP REST investments + portfolio cards (description/website for current cards) (`tend_scraper.py`) |
| Eight Roads | `eightroads_companies.json` | 253 | eightroads.com page JSON feed (description, website, sectors, investment dates, exited, region) (`eightroads_scraper.py`) |
| Hyperplane | `hyperplane_companies.json` | 47 | hyperplane.vc/companies Webflow table + pages (description, website, entry stage, acquirer) (`hyperplane_scraper.py`) |
| Equity Venture Partners | `evp_companies.json` | 54 | evp.com.au/companies Webflow pages (description, website, founders, round/year, fund, exit) (`evp_scraper.py`) |
| Magma Partners | `magmapartners_companies.json` | 114 | magmapartners.com/companies Webflow + pages (one-liner, year, stage, website, founders, location) (`magmapartners_scraper.py`) |
| Inventure | `inventure_companies.json` | 56 | inventure.vc/portfolio Webflow + pages (description, website, country, entry round/year, partner) (`inventure_scraper.py`) |
| La Famiglia | `lafamiglia_companies.json` | 64 | lafamiglia.vc/founders Webflow list (description, website) (`lafamiglia_scraper.py`) |
| Extantia Capital | `extantia_companies.json` | 32 | extantia.com/pioneers + pages (sector, stage, country, website; no descriptions) (`extantia_scraper.py`) |
| Oxford Science Enterprises | `ose_companies.json` | 87 | oxfordscienceenterprises.com/portfolio pages (description, website, sector, stage/exited) (`ose_scraper.py`) |
| HOF Capital | `hofcapital_companies.json` | 85 | hofcapital.com Gatsby page-data (website, sectors, listed; no descriptions) (`hofcapital_scraper.py`) |
| Knife Capital | `knife_companies.json` | 24 | knifecap.com/portfolio + /exits (description, website, fund, acquirer) (`knife_scraper.py`) |
| Georgian | `georgian_companies.json` | 85 | georgian.io/portfolio Next flight payload (description, website, industries, status) (`georgian_scraper.py`) |
| Conviction | `conviction_companies.json` | 22 | conviction.com portfolio list (website, founders; no descriptions) (`conviction_scraper.py`) |
| Maven 11 | `maven11_companies.json` | 68 | maven11.com/portfolios Webflow (website, partial bio/year/category) (`maven11_scraper.py`) |
| Silver Lake | `silverlake_companies.json` | 176 | silverlake.com/portfolio — WP REST portfolio (`silverlake_scraper.py`) |
| Vista Equity Partners | `vista_companies.json` | 150 | vistaequitypartners.com/about/companies — WP REST companies (`vista_scraper.py`) |
| HongShan | `hongshan_companies.json` | 130 | hongshan.com/companies — WP REST companies (Chinese-language descriptions) (`hongshan_scraper.py`) |
| TA Associates | `ta_companies.json` | 322 | ta.com/portfolio — server-rendered portfolio grid (`ta_scraper.py`) |
| Summit Partners | `summit_companies.json` | 412 | summitpartners.com/portfolio — Webflow portfolio (status incl. merger→acquired) (`summit_scraper.py`) |
| Bosch Ventures | `bosch_companies.json` | 112 | bosch.ventures/portfolio — portfolio page (UTF-8 bytes decode) (`bosch_scraper.py`) |
| Avenir Growth | `avenir_companies.json` | 89 | avenirgrowth.com/portfolio — Next.js HTML portfolio (`avenir_scraper.py`) |
| Globis Capital Partners | `globis_companies.json` | 159 | globiscapital.co.jp/en/companies — companies list (English site) (`globis_scraper.py`) |
| BlueYard Capital | `blueyard_companies.json` | 72 | blueyard.com — Nuxt HTML portfolio (`blueyard_scraper.py`) |
| Innovation Endeavors | `innovationendeavors_companies.json` | 77 | innovationendeavors.com/companies — companies page (`innovationendeavors_scraper.py`) |
| Felix Capital | `felix_companies.json` | 74 | felixcap.com — Squarespace portfolio (names + websites) (`felix_scraper.py`) |
| Accel-KKR | `accelkkr_companies.json` | 168 | accel-kkr.com/portfolio — portfolio grid (Chrome UA) (`accelkkr_scraper.py`) |
| S2G Ventures | `s2g_companies.json` | 113 | s2ginvestments.com/companies — Wix HTML companies (Chrome UA) (`s2g_scraper.py`) |
| Ventech | `ventech_companies.json` | 178 | ventechvc.com/our-companies — Webflow companies (`ventech_scraper.py`) |
| DBL Partners | `dbl_companies.json` | 46 | dbl.vc/portfolio — WP REST portfolio (`dbl_scraper.py`) |
| SoftBank Vision Fund | `visionfund_companies.json` | 339 | visionfund.com/portfolio — __NEXT_DATA__ portfolio (`visionfund_scraper.py`) |
| BDMI | `bdmi_companies.json` | 159 | bdmifund.com/portfolio — Squarespace portfolio (`bdmi_scraper.py`) |
| EQT | `eqt_companies.json` | 357 | eqtgroup.com/about/current-portfolio — Next.js RSC flight payload (current portfolio only) (`eqt_scraper.py`) |
| Samsung Catalyst Fund | `samsungcatalyst_companies.json` | 46 | samsungcatalyst.com — portfolio page (LP fund investments excluded) (`samsungcatalyst_scraper.py`) |
| Kinnevik | `kinnevik_companies.json` | 37 | kinnevik.com/investments — investments page (prior strategies kept as strategy) (`kinnevik_scraper.py`) |
| ZhenFund | `zhenfund_companies.json` | 95 | zhenfund.com/portfolio — portfolio page (Chinese-language) (`zhenfund_scraper.py`) |
| Owl Ventures | `owl_companies.json` | 98 | owlvc.com/portfolio — Webflow portfolio (`owl_scraper.py`) |
| SR One | `srone_companies.json` | 64 | srone.com/portfolio — __NEXT_DATA__ portfolio (`srone_scraper.py`) |
| Abingworth | `abingworth_companies.json` | 147 | abingworth.com/portfolio — __NEXT_DATA__ portfolio (`abingworth_scraper.py`) |
| Animoca Brands | `animoca_companies.json` | 568 | animocabrands.com/our-portfolio — Webflow portfolio (names + websites) (`animoca_scraper.py`) |
| Endeit Capital | `endeit_companies.json` | 37 | endeit.com/portfolio — Webflow portfolio (`endeit_scraper.py`) |
| Lattice Fund | `lattice_companies.json` | 40 | lattice.fund/portfolio — portfolio page (`lattice_scraper.py`) |
| Greenfield Capital | `greenfield_companies.json` | 40 | greenfieldcapital.com/portfolio — portfolio page (names + websites) (`greenfield_scraper.py`) |
| Activant Capital | `activant_companies.json` | 36 | activantcapital.com — homepage portfolio section (`activant_scraper.py`) |
| Human Capital | `humancapital_companies.json` | 56 | human.capital/portfolio — Webflow portfolio (names + websites) (`humancapital_scraper.py`) |
| DOMO Invest | `domo_companies.json` | 106 | domo.vc/portfolio — WP REST portfolio (`domo_scraper.py`) |
| Novartis Venture Fund | `nvfund_companies.json` | 31 | nvfund.com/portfolio — portfolio page (`nvfund_scraper.py`) |
| Premji Invest | `premji_companies.json` | 100 | premjiinvest.com/portfolio — Webflow portfolio (`premji_scraper.py`) |
| Z47 | `z47_companies.json` | 71 | z47.com/portfolio — Webflow portfolio (formerly Matrix Partners India) (`z47_scraper.py`) |
| Arrington Capital | `arrington_companies.json` | 124 | arringtoncapital.com/portfolio — portfolio page (`arrington_scraper.py`) |
| Francisco Partners | `francisco_companies.json` | 179 | franciscopartners.com/investments — Nuxt __NUXT__ payload (node vm) (`francisco_scraper.py`) |
| Advent International | `advent_companies.json` | 455 | adventinternational.com/portfolio — WP REST portfolio (no status/website) (`advent_scraper.py`) |
| Hellman & Friedman | `hf_companies.json` | 83 | hf.com/portfolio — WP REST portfolio + taxonomies (`hf_scraper.py`) |
| Leonard Green & Partners | `leonardgreen_companies.json` | 105 | leonardgreen.com/portfolio — portfolio grid (sector, deal type, status) (`leonardgreen_scraper.py`) |
| Genstar Capital | `genstar_companies.json` | 82 | gencap.com/companies — company popups (status, year, sector) (`genstar_scraper.py`) |
| Roark Capital | `roark_companies.json` | 86 | roarkcapital.com/portfolio — portfolio dialogs (no status published) (`roark_scraper.py`) |
| Stonepeak | `stonepeak_companies.json` | 78 | stonepeak.com/investments — investments panels + WP REST terms (`stonepeak_scraper.py`) |
| Montagu Private Equity | `montagu_companies.json` | 56 | montagu.com/portfolio — WP REST portfolio (no websites/status) (`montagu_scraper.py`) |
| BC Partners | `bcpartners_companies.json` | 135 | bcpartners.com/portfolio — WP REST portfolio + investment history (names only for history) (`bcpartners_scraper.py`) |
| Berkshire Partners | `berkshire_companies.json` | 116 | berkshirepartners.com/private-equity/portfolio — portfolio grid + detail pages (`berkshire_scraper.py`) |
| Investcorp | `investcorp_companies.json` | 90 | investcorp.com/what-we-do/portfolio — portfolio grid + detail pages (no status) (`investcorp_scraper.py`) |
| Vestar Capital Partners | `vestar_companies.json` | 87 | vestarcapital.com/portfolio-companies — WP REST portfolio + detail pages (`vestar_scraper.py`) |
| H.I.G. Capital | `hig_companies.json` | 399 | hig.com/portfolio — portfolio grid (status/strategy/sector classes) (`hig_scraper.py`) |
| New Mountain Capital | `newmountain_companies.json` | 96 | newmountaincapital.com/our-strategies/private-equity/portfolio — WP REST nmc-portfolio (no websites) (`newmountain_scraper.py`) |
| Clayton, Dubilier & Rice | `cdr_companies.json` | 44 | cdr.com/portfolio — portfolio cards + detail pages (current only) (`cdr_scraper.py`) |
| FJ Labs | `fjlabs_companies.json` | 1316 | fjlabs.com/portfolio — Webflow paginated (status, stage, year, geo, industry; names + URLs mostly) (`fjlabs_scraper.py`) |
| In-Q-Tel | `iqt_companies.json` | 480 | iqt.org/portfolio — Webflow 32 pages (categories, region, active/exited) (`iqt_scraper.py`) |
| Celesta Capital | `celesta_companies.json` | 84 | celesta.vc/portfolio — Webflow (sector, status) (`celesta_scraper.py`) |
| Creathor Ventures | `creathor_companies.json` | 66 | creathor.com/companies — Webflow (`creathor_scraper.py`) |
| Canvas Ventures | `canvas_companies.json` | 66 | canvas.vc/portfolio — Webflow (detail URLs; few websites) (`canvas_scraper.py`) |
| Astella | `astella_companies.json` | 59 | astella.com.br/en/portfolio — Webflow (names + websites only) (`astella_scraper.py`) |
| Fin Capital | `fincapital_companies.json` | 130 | fin.capital/portfolio — Webflow 2 pages (description, category/stage/status; no websites) (`fincapital_scraper.py`) |
| Founders Future | `foundersfuture_companies.json` | 135 | foundersfuture.com/en/portfolio — Webflow 3 pages (sector, stage, founded year, exits; no websites) (`foundersfuture_scraper.py`) |
| Harpoon Ventures | `harpoon_companies.json` | 59 | harpoon.vc/portfolio — Webflow portco cards (acquired/IPO pills; no websites) (`harpoon_scraper.py`) |
| Adara Ventures | `adara_companies.json` | 49 | adara.vc/portfolios — Webflow (tagline, industry, status; no websites) (`adara_scraper.py`) |
| HealthCap | `healthcap_companies.json` | 134 | healthcap.eu/portfolio — #panel-companies + overlays (current/former) (`healthcap_scraper.py`) |
| Aisling Capital | `aisling_companies.json` | 120 | aislingcapital.com/portfolio — portfolio grid (`aisling_scraper.py`) |
| Better Capital | `bettercapital_companies.json` | 183 | bettercapital.vc/portfolio — portfolio table (`bettercapital_scraper.py`) |
| Fenbushi Capital | `fenbushi_companies.json` | 94 | fenbushi.vc/projects — project tiles (region categories; names + URLs) (`fenbushi_scraper.py`) |
| ParaFi Capital | `parafi_companies.json` | 98 | parafi.com/portfolio — Next.js-rendered portfolio (`parafi_scraper.py`) |
| Sanofi Ventures | `sanofiventures_companies.json` | 84 | sanofiventures.com/portfolio — Drupal modals (`sanofiventures_scraper.py`) |
| Spring Camp | `springcamp_companies.json` | 186 | springcamp.co/portfolio — Angular SSR cards (names only) (`springcamp_scraper.py`) |
| Standard Crypto | `standardcrypto_companies.json` | 53 | standardvc.com/portfolio — Astro data-portfolio-item list (category, website) (`standardcrypto_scraper.py`) |
| Mission BioCapital | `missionbio_companies.json` | 70 | missionbiocapital.com/portfolio — logo-carousel modals (description, industry, status, initial investment year) (`missionbio_scraper.py`) |
| Beyond Next Ventures | `beyondnext_companies.json` | 75 | beyondnextventures.com/portfolio — WP card list (description, website) (`beyondnext_scraper.py`) |
| Cervin Ventures | `cervin_companies.json` | 91 | cervinventures.com/portfolio — HubSpot cards (stages, tagline) (`cervin_scraper.py`) |
| Hatteras Venture Partners | `hatteras_companies.json` | 76 | hatterasvp.com/portfolio — WP grid (description, detail URL) (`hatteras_scraper.py`) |
| Mashup Ventures | `mashup_companies.json` | 193 | mashupventures.co/portfolio — static catalog cards (Korean names/descriptions, tags) (`mashup_scraper.py`) |
| Parkwalk Advisors | `parkwalk_companies.json` | 201 | parkwalk.vc/portfolio — WP REST company (sector, university institution) (`parkwalk_scraper.py`) |
| Manhattan Venture Partners | `mvp_companies.json` | 70 | mvp.vc/portfolio — Webflow CMS names + detail pages (`mvp_scraper.py`) |
| COMETA | `cometa_companies.json` | 30 | cometa.vc/portfolio — Webflow Finsweet (sector, model, geography, stage) (`cometa_scraper.py`) |
| Inflexor Ventures | `inflexor_companies.json` | 30 | inflexor.vc/portfolio — Webflow Finsweet (sector, fund, stage) (`inflexor_scraper.py`) |
| Sauce.vc | `sauce_companies.json` | 33 | sauce.vc/portfolio — WP grid (description, website, fund) (`sauce_scraper.py`) |
| K5 Global | `k5_companies.json` | 298 | k5global.com/companies — Webflow 12 pages (website, ticker/acquisition) (`k5_scraper.py`) |
| G2 Venture Partners | `g2vp_companies.json` | 28 | g2vp.com/portfolio — Webflow (website, industry) (`g2vp_scraper.py`) |
| Axeleo Capital | `axeleo_companies.json` | 72 | axc.vc/portfolio — Astro grid (website, sector, running/exit + acquirer) (`axeleo_scraper.py`) |
| Raed Ventures | `raed_companies.json` | 53 | raed.vc/portfolio — list cards (description, country, category, year) (`raed_scraper.py`) |
| Smartfin | `smartfin_companies.json` | 36 | smartfinvc.com/portfolio — FacetWP grid (country, stage, website) (`smartfin_scraper.py`) |
| Future Africa | `futureafrica_companies.json` | 88 | future.africa/companies — Webflow paginated (names + status) (`futureafrica_scraper.py`) |
| Dell Technologies Capital | `delltech_companies.json` | 155 | delltechnologiescapital.com/companies — Webflow 4 pages (status/acquirer, focus area, lead, region, first investment) (`delltech_scraper.py`) |
| Main Sequence | `mainsequence_companies.json` | 58 | mseq.vc/all-companies — Webflow cards (description) (`mainsequence_scraper.py`) |
| Next Frontier Capital | `nextfrontier_companies.json` | 62 | nextfrontiercapital.com/portfolio — Framer cards (sector, fund, invested year, exited badge) (`nextfrontier_scraper.py`) |
| Album VC | `album_companies.json` | 83 | album.vc — home-page list (names + websites) (`album_scraper.py`) |
| Norrsken VC | `norrsken_companies.json` | 62 | norrsken.vc/portfolio — Webflow Finsweet (description, country, sector, stage, year) (`norrsken_scraper.py`) |
| Blue Bear Capital | `bluebear_companies.json` | 40 | bluebearcap.com/portfolio-companies — WP panels (description, website) (`bluebear_scraper.py`) |
| Azolla Ventures | `azolla_companies.json` | 35 | azollaventures.com/our-portfolio — JetElements grid (description, website) (`azolla_scraper.py`) |
| Symbolic Capital | `symbolic_companies.json` | 41 | symbolic.capital/portfolio — Webflow (names + websites) (`symbolic_scraper.py`) |
| Foxmont Capital Partners | `foxmont_companies.json` | 41 | foxmontcapital.com — Framer cards (one-line description) (`foxmont_scraper.py`) |
| Prime Movers Lab | `primemoverslab_companies.json` | 29 | primemoverslab.com/portfolio — team-pml cards (specialty, website, exits section) (`primemoverslab_scraper.py`) |
| Aavishkaar Capital | `aavishkaar_companies.json` | 32 | aavishkaarcapital.in/portfolios — The Grid tiles (names only) (`aavishkaar_scraper.py`) |
| coparion | `coparion_companies.json` | 52 | coparion.vc — home-page modals (names + websites) (`coparion_scraper.py`) |
| Material Impact | `materialimpact_companies.json` | 34 | materialimpact.com/companies — popouts (description, website) (`materialimpact_scraper.py`) |
| Saama Capital | `saama_companies.json` | 62 | saama.vc/portfolio — tiles + quick-view bios (sector, description, founders, founded/investment year, website) (`saama_scraper.py`) |
| Jeito Capital | `jeito_companies.json` | 23 | jeito.life/en/portfolio — Divi blurbs (therapeutic area, financing note) (`jeito_scraper.py`) |
| Kurma Partners | `kurma_companies.json` | 67 | kurmapartners.com/en/portfolio — flip cards (fund, partner, website) (`kurma_scraper.py`) |
| LifeX Ventures | `lifex_companies.json` | 145 | lifex.vc/founders — Webflow paginated founder cards (logo-alt name, description, website, exit note) (`lifex_scraper.py`) |
| Garuda Ventures | `garuda_companies.json` | 51 | garuda.vc/portfolio — Webflow rows (category, tagline, status, exit note, website) (`garuda_scraper.py`) |
| Breakout Ventures | `breakout_companies.json` | 28 | breakout.vc/portfolio — Next.js/Prismic company list (description, website) (`breakout_scraper.py`) |
| SKY VC | `skyvc_companies.json` | 37 | sky-vc.com/portfolio — Webflow/Finsweet cards (summary, status, category, detail page) — formerly JetBlue Ventures (`skyvc_scraper.py`) |
| Refactor Capital | `refactor_companies.json` | 61 | refactor.com — Webflow/Finsweet list + info panels (category, description, website) (`refactor_scraper.py`) |
| Courtside Ventures | `courtside_companies.json` | 73 | courtsidevc.com/portfolio — Webflow cards (country, vertical, fund, series, acquisition, detail page) (`courtside_scraper.py`) |
| TEN13 | `ten13_companies.json` | 51 | ten13.vc/portfolio — Webflow cards (sector, description, website) (`ten13_scraper.py`) |
| Twelve Below | `twelvebelow_companies.json` | 34 | twelvebelow.co/portfolio — Webflow items (founders, description, website) (`twelvebelow_scraper.py`) |
| Theory Ventures | `theory_companies.json` | 15 | theoryvc.com/portfolio — Webflow/Finsweet cards (description, stage, theme, detail page) (`theory_scraper.py`) |
| Matchstick Ventures | `matchstick_companies.json` | 83 | matchstick.vc/companies — Webflow overview cards (description, detail page) (`matchstick_scraper.py`) |
| Collab Capital | `collabcapital_companies.json` | 42 | collab.capital/portfolio — Webflow/Finsweet cards (sector, founder, location, fund, detail page) — distinct from Collaborative Fund (`collabcapital_scraper.py`) |
| Mercato Partners | `mercato_companies.json` | 23 | mercatopartners.com/portfolio — Webflow cards + modal fields (location, synopsis, website, fund, status, year, series) (`mercato_scraper.py`) |
| Z Venture Capital | `zvc_companies.json` | 235 | zvc.vc/portfolio — WP list (region/fund/sector hashtags, website) (`zvc_scraper.py`) |
| Backstage Capital | `backstage_companies.json` | 171 | backstagecapital.com/headliners — WP headliner modals (description, founders, website) (`backstage_scraper.py`) |
| SJF Ventures | `sjf_companies.json` | 92 | sjfventures.com/our-portfolio — WP grid (description, website) (`sjf_scraper.py`) |
| Geodesic Capital | `geodesic_companies.json` | 81 | geodesiccap.com/portfolio — WP flip cards (category, description, website) (`geodesic_scraper.py`) |
| TTV Capital | `ttv_companies.json` | 78 | ttvcapital.com/portfolio — WP PowerPack grid (fund, status categories, website, detail page) (`ttv_scraper.py`) |
| Interplay | `interplay_companies.json` | 100 | interplay.vc/portfolio — Webflow/Finsweet cards (description, website, relationship tags, detail page) (`interplay_scraper.py`) |
| E14 Fund | `e14_companies.json` | 100 | e14.vc/companies — Webflow cards (tagline, status, website) (`e14_scraper.py`) |
| Dorm Room Fund | `dormroom_companies.json` | 100 | dormroomfund.com/portfolio — Webflow/Finsweet name list (category, website) (`dormroom_scraper.py`) |
| Oak Investment Partners | `oak_companies.json` | 207 | oakvc.com/investments — WP grid + modals (status, sector, website, description) (`oak_scraper.py`) |
| Third Sphere | `thirdsphere_companies.json` | 96 | thirdsphere.com/portfolio/all — WP grid (name, website) (`thirdsphere_scraper.py`) |
| Sterling Road | `sterlingroad_companies.json` | 89 | sterlingroad.com/portfolio — tiles by year (category, since-year, website) (`sterlingroad_scraper.py`) |
| Draft Ventures | `draft_companies.json` | 72 | draftvc.com — Notion page toggles (description, IPO/acquired marker, website) (`draft_scraper.py`) |
| Untapped Capital | `untapped_companies.json` | 54 | untapped.vc — SSR cards (category, description, tags, website) (`untapped_scraper.py`) |
| M25 | `m25_companies.json` | 97 | m25vc.com/portfolio — Webflow/Finsweet logo grid (description from alt, status, detail page) (`m25_scraper.py`) |
| Human Ventures | `humanventures_companies.json` | 68 | human.vc/portfolio — featured cards + company list (tagline, founders, website) — distinct from Human Capital (`humanventures_scraper.py`) |
| Canapi Ventures | `canapi_companies.json` | 45 | canapi.com/portfolio — Webflow/Finsweet cards (description, status, detail page) (`canapi_scraper.py`) |
| Yes VC | `yesvc_companies.json` | 41 | yes.vc/portfolio — WP list (description, exit note, website) (`yesvc_scraper.py`) |
| 6th Man Ventures | `sixthman_companies.json` | 56 | 6thman.ventures/portfolio — portfolio rows (tagline, category, website) (`sixthman_scraper.py`) |
| Arbor Ventures | `arbor_companies.json` | 36 | arborventures.com/our-portfolio — Webflow cards (logo-alt name, status, description, website) (`arbor_scraper.py`) |
| Revel Partners | `revel_companies.json` | 47 | revelpartners.com/companies — B12 grid captions (CEO, location, website, description, exit note) (`revel_scraper.py`) |
| JLL Spark | `jllspark_companies.json` | 41 | spark.jllt.com/portfolio — WP boxes (description, website, exit tag) (`jllspark_scraper.py`) |
| Necessary Ventures | `necessary_companies.json` | 39 | necessary.vc/portfolio — Framer cards (description, website) (`necessary_scraper.py`) |
| Kepple Africa Ventures | `kepple_companies.json` | 17 | vkav.vc/portfolio — Bricks popups (stage, description, website) — Verod-Kepple Africa Ventures (`kepple_scraper.py`) |
| Tau Ventures | `tau_companies.json` | 84 | tauventures.com/portfolio — cards (category, exited flag, stage, website) (`tau_scraper.py`) |
| Next Ventures | `nextventures_companies.json` | 15 | nextventures.com/portfolio — Webflow/Finsweet cards (logo-alt name, description, category, website) (`nextventures_scraper.py`) |
| Valar Ventures | `valar_companies.json` | 30 | valar.com — homepage cards (description, website) (`valar_scraper.py`) |
| Zetta Ventures | `zetta_companies.json` | 49 | zettavp.com/companies — __NEXT_DATA__ companies grid (short description, detail page) (`zetta_scraper.py`) |
| Runa Capital | `runa_companies.json` | 92 | runacap.com/companies — WP grid data attributes (status, theme, location, subtitle, detail page) (`runa_scraper.py`) |
| Swell VC | `swell_companies.json` | 23 | swell.vc — homepage cards (description, sector, website) (`swell_scraper.py`) |
| Link Ventures | `link_companies.json` | 86 | linkventures.com/portfolio — Webflow/Finsweet rows (category, fund, year) (`link_scraper.py`) |
| Remarkable Ventures | `remarkable_companies.json` | 84 | remarkable.vc/portfolio — Webflow/Finsweet cards (category, stage, detail page) (`remarkable_scraper.py`) |
| Focal VC | `focal_companies.json` | 45 | focal.vc/portfolio — Next.js table (description, website) (`focal_scraper.py`) |
| Path Ventures | `pathventures_companies.json` | 25 | path.vc/portfolio — list rows (description, website) (`pathventures_scraper.py`) |
| Moment Ventures | `moment_companies.json` | 42 | momentventures.com/portfolio — WP boxes (description/exit note, acquired badge, detail page) (`moment_scraper.py`) |
| Charge VC | `charge_companies.json` | 20 | charge.vc/portfolio — Framer cards (description, detail page) (`charge_scraper.py`) |
| Haystack | `haystack_companies.json` | 18 | haystack.vc/portfolio — Framer cards, server-rendered subset (description, exit note, website) (`haystack_scraper.py`) |
| Mozilla Ventures | `mozilla_companies.json` | 40 | mozilla.vc/portfolio — WP logo grid (name, website) (`mozilla_scraper.py`) |
| Lead Edge Capital | `leadedge_companies.json` | 93 | leadedge.com/portfolio — Nuxt grid (names, detail pages) (`leadedge_scraper.py`) |
| Hitachi Ventures | `hitachi_companies.json` | 60 | hitachi-ventures.com/portfolio — WP portfolio modals + embedded post JSON (name, tagline, description, website, CEO, sectors, stage, HQ, exited) (`hitachi_scraper.py`) |
| Chevron Technology Ventures | `chevron_companies.json` | 63 | chevron.com/what-we-do/technology-and-innovation/technology-ventures — portfolio link list (name, website) (`chevron_scraper.py`) |
| Grotech Ventures | `grotech_companies.json` | 148 | grotech.com/portfolio — Webflow CMS dropdowns (name, description, website) (`grotech_scraper.py`) |
| Moonshots Capital | `moonshots_companies.json` | 106 | moonshotscapital.com/portfolios — WP grid (name, vehicle, exit/unicorn/veteran labels, exit note, website) (`moonshots_scraper.py`) |
| Trucks VC | `trucks_companies.json` | 63 | trucks.vc/portfolio — Webflow rows (name, focus, exit note, website, press link) (`trucks_scraper.py`) |
| Lorimer Ventures | `lorimer_companies.json` | 65 | lorimerventures.com/portfolio — Webflow cards (name, category, location, description, website) (`lorimer_scraper.py`) |
| V1 VC | `v1vc_companies.json` | 53 | v1.vc — homepage logo slider (name, website) (`v1vc_scraper.py`) |
| Golden Seeds | `goldenseeds_companies.json` | 40 | goldenseeds.com/our-companies — portfolio cards, first server-rendered page (name, sector, description, website) (`goldenseeds_scraper.py`) |
| SoGal Ventures | `sogal_companies.json` | 30 | sogalventures.com/portfolio — Webflow logo wall (name, website) (`sogal_scraper.py`) |
| Foundamental | `foundamental_companies.json` | 59 | foundamental.com/portfolio — Webflow/Finsweet rows (name, stage, year, country, description, sector, market, exit tag, website) (`foundamental_scraper.py`) |
| NextGen Venture Partners | `nextgen_companies.json` | 65 | nextgenvp.com/portfolio — logo grid (name, description, website, exited) (`nextgen_scraper.py`) |
| HLM Venture Partners | `hlm_companies.json` | 55 | hlmvp.com/portfolio — WP postcards (name, description, status, website) (`hlm_scraper.py`) |
| Data Point Capital | `datapoint_companies.json` | 44 | datapointcapital.com/datapoint-portfolio — Elementor flip boxes (name, description, DPC lead, website) (`datapoint_scraper.py`) |
| Elevate Ventures | `elevatevent_companies.json` | 331 | elevateventures.com/portfolio — WP table (name, website, stage, sector, status) (`elevatevent_scraper.py`) |
| Coalition Operators | `coalition_companies.json` | 59 | coalitionoperators.com/portfolio — Webflow/Finsweet popups (name, description, year, industries, website) (`coalition_scraper.py`) |
| VentureSouq | `venturesouq_companies.json` | 100 | venturesouq.com/portfolio — Webflow/Finsweet cards (name, fund, region, sector, description, website) (`venturesouq_scraper.py`) |
| Fluent Ventures | `fluent_companies.json` | 24 | fluent.vc/portfolio — Webflow/Finsweet cards (name, fund, year, current/historical, country, model tags) (`fluent_scraper.py`) |
| Blackhorn Ventures | `blackhorn_companies.json` | 68 | blackhornvc.com/portfolio — Webflow/Finsweet rows (name, description, industry, vintage, detail) (`blackhorn_scraper.py`) |
| Urban Innovation Fund | `urbaninnovation_companies.json` | 65 | urban.vc/portfolio — Squarespace summaries (name, description, website) (`urbaninnovation_scraper.py`) |
| Leadout Capital | `leadout_companies.json` | 46 | leadoutcapital.com/portfolio — Webflow list (name, year, description, sector, status, website) (`leadout_scraper.py`) |
| Vitalize VC | `vitalize_companies.json` | 63 | vitalize.vc/portfolio — portfolio cards (name, description, vehicle, website) (`vitalize_scraper.py`) |
| Kaya Ventures | `kaya_companies.json` | 54 | kaya.vc/portfolio — Next list rows (name, description, Exited/RIP pill, website) (`kaya_scraper.py`) |
| Ubiquity Ventures | `ubiquity_companies.json` | 41 | ubiquity.vc/portfolio — Next cards (name, category, stage, city, description, website) (`ubiquity_scraper.py`) |
| Fresco Capital | `fresco_companies.json` | 55 | fresco.vc/portfolio — WP flip cards (name, slogan, region, sector, website) (`fresco_scraper.py`) |
| Industrious Ventures | `industrious_companies.json` | 50 | industrious.vc/portfolio — WP cards (name, sector, summary, acquired, website) (`industrious_scraper.py`) |
| Vine Ventures | `vine_companies.json` | 57 | vineventures.com — homepage panels (name, sectors, location, description, founders, website) (`vine_scraper.py`) |
| Right Click Capital | `rightclick_companies.json` | 40 | rightclickcapital.com/portfolio — WP grid (name, website) (`rightclick_scraper.py`) |
| Pathlight Ventures | `pathlight_companies.json` | 43 | pathlight.vc/portfolio — list rows (name, description, theme, website) (`pathlight_scraper.py`) |
| Trust Fund | `trustfund_companies.json` | 37 | trustfund.vc/portfolio — cards (name, description, website) (`trustfund_scraper.py`) |
| January Ventures | `january_companies.json` | 15 | january.ventures — Webflow founder grid (name, description, website) (`january_scraper.py`) |
| Hypothesis | `hypothesis_companies.json` | 39 | hypothesis.studio/portfolio — Webflow lists (name, description, website) (`hypothesis_scraper.py`) |
| Script Capital | `script_companies.json` | 92 | script.capital — homepage grid (name, description, tags, acquisition note, detail) (`script_scraper.py`) |
| Seaside Ventures | `seaside_companies.json` | 23 | seasideventures.com/portfolio — Webflow cards (name, category, description, stage, year, detail) (`seaside_scraper.py`) |
| Supernode Ventures | `supernode_companies.json` | 50 | supernode.vc/portfolio — Squarespace list (name, description, rounds, stage, status) (`supernode_scraper.py`) |
| Great North Ventures | `greatnorth_companies.json` | 51 | greatnorthventures.com/our-portfolio — Elementor tiles (name, fund, website) (`greatnorth_scraper.py`) |
| True Wealth Ventures | `truewealth_companies.json` | 23 | truewealthvc.com/portfolio — WP blocks (name, description, founders, HQ, website) (`truewealth_scraper.py`) |
| Matterscale Ventures | `matterscale_companies.json` | 35 | matterscale.com/portfolio — WP cards (name, description, detail) (`matterscale_scraper.py`) |
| Savannah Fund | `savannah_companies.json` | 24 | savannah.vc/startups — WP cards (name, country, description, detail) (`savannah_scraper.py`) |
| Trousdale Ventures | `trousdale_companies.json` | 66 | trousdale.vc/portfolio — WP logo tiles (name, detail) (`trousdale_scraper.py`) |
| Era Ventures | `era_companies.json` | 13 | eraventures.com/companies — expandable list (name, tagline, description, industries, website) (`era_scraper.py`) |
| Playfair Capital | `playfair_companies.json` | 31 | playfair.vc/portfolio.php — grid + /companies/<slug> pages (name, meta description, stage, website) (`playfair_scraper.py`) |
| Avalanche VC | `avalanche_companies.json` | 31 | avalanche.vc/portfolio — Webflow grid (names only) (`avalanche_scraper.py`) |
| How Women Invest | `howwomeninvest_companies.json` | 32 | howwomeninvest.com/portfolio — Wix repeater (name, category, exited) (`howwomeninvest_scraper.py`) |
| Sancus Ventures | `sancus_companies.json` | 30 | sancus.vc/portfolio — Wix grid (name, website) (`sancus_scraper.py`) |
| Resilience Reserve | `resilience_companies.json` | 15 | resilience.vc/portfolio — Webflow cards (name, description, website) (`resilience_scraper.py`) |
| Asylum Ventures | `asylum_companies.json` | 14 | asylum.vc/companies — Webflow company sentences (name, description, exit note, stage, website) (`asylum_scraper.py`) |
| Prototype Capital | `prototype_companies.json` | 12 | prototypecap.com/index.html — grid (name, description, first-check year, website) (`prototype_scraper.py`) |
| SNÖCAP | `snocap_companies.json` | 13 | snocap.vc — Astro cards (name, sectors, website) (`snocap_scraper.py`) |
| Parameter Ventures | `parameter_companies.json` | 17 | parameter.vc/portfolio — Wix gallery alts (name, description, website) (`parameter_scraper.py`) |
| Planet A Ventures | `planeta_companies.json` | 27 | planet-a.com/portfolio — WP startup grid (name, claim, sector, impact assessment, website) (`planeta_scraper.py`) |
| Western Technology Investment | `wti_companies.json` | 1545 | westerntech.com/companies — Webflow CMS list, paginated (name, website, initial investment year, description, region, sector, status); venture lender (`wti_scraper.py`) |
| Titan Capital | `titancapital_companies.json` | 199 | titancapital.vc/portfolio — firm's public Sanity API portfolioGrid (name, description, website, founders, stage, partnered year, status) (`titancapital_scraper.py`) |
| GTMfund | `gtmfund_companies.json` | 133 | gtmfund.com/portfolio — WP REST portfolio + taxonomies (name, description, entry stage, current stage, co-investors, acquired flag; no websites) (`gtmfund_scraper.py`) |
| 645 Ventures | `645ventures_companies.json` | 106 | 645ventures.com/portfolio — records decoded from Next.js JS chunks (name, description, website, stage, first invested, status) (`645ventures_scraper.py`) |
| Verve Ventures | `verve_companies.json` | 96 | verve.vc/portfolio — WP REST verve_portfolio_new + detail pages (name, description, website, location, invested since, topic, status) (`verve_scraper.py`) |
| Millennium Technology Value Partners | `mtvp_companies.json` | 84 | mtvlp.com/portfolio — flip cards (name, description, website, sectors, exit note/year, status) (`mtvp_scraper.py`) |
| Tribeca Venture Partners | `tribecavp_companies.json` | 74 | tribecavp.com/companies — embedded Alpine JSON (name, description, website, stage, first investment, location, capital raised, status) (`tribecavp_scraper.py`) |
| Verissimo Ventures | `verissimo_companies.json` | 74 | verissimo.vc/portfolio — Super.so Notion detail pages (name, description, website, founders, first invested, stage, location, fund, status) (`verissimo_scraper.py`) |
| Alpha Edison | `alphaedison_companies.json` | 55 | alphaedison.com/portfolio — Squarespace image blocks + category pages (name, description, website, category) (`alphaedison_scraper.py`) |
| Collide Capital | `collide_companies.json` | 54 | collidecap.com/portfolio — Webflow paginated cards (name, description, website, location, first invested, CEO, acquired flag) (`collide_scraper.py`) |
| Irregular Expressions | `irregex_companies.json` | 54 | irregex.vc/portfolio — Webflow fs-list (name, description, website, founded year, fund vehicle, founders, status) (`irregex_scraper.py`) |
| Act One Ventures | `actone_companies.json` | 53 | actoneventures.com/portfolio — Framer cards (name, category, description, theme, website, acquired badge) (`actone_scraper.py`) |
| Hearst Ventures | `hearstventures_companies.json` | 52 | hearst.com/ventures — brand cards (name, location, description, website) (`hearstventures_scraper.py`) |
| Ingressive Capital | `ingressive_companies.json` | 45 | ingressivecapital.com — WP REST cpt_services (name, description, founders, fund, location, website, sector) (`ingressive_scraper.py`) |
| Kearny Jackson | `kearnyjackson_companies.json` | 45 | kearnyjackson.com — Webflow paginated cards (name, industry, description; no websites) (`kearnyjackson_scraper.py`) |
| Echo Health Ventures | `echohealth_companies.json` | 43 | echohealthventures.com — WP REST companies + current-section websites (name, description, website, active/alumni status) (`echohealth_scraper.py`) |
| LDV Capital | `ldv_companies.json` | 40 | ldv.co/capital — company panels (overview, location, founded, first partnered year/round, LDV-led, co-investors, acquirer) (`ldv_scraper.py`) |
| Differential Ventures | `differential_companies.json` | 34 | differential.vc/portfolio — Squarespace ?format=json posts (name, description, website, status from categories) (`differential_scraper.py`) |
| Rampersand | `rampersand_companies.json` | 34 | rampersand.vc/portfolio.html — inline JS array (name, description, stage, first invested year, Rampersand role, status) (`rampersand_scraper.py`) |
| Rebright Partners | `rebright_companies.json` | 33 | rebright.partners/portfolio — WP grid (name, website, sector, country, description) (`rebright_scraper.py`) |
| FirstMile Ventures | `firstmile_companies.json` | 55 | firstmilevc.com/portfolio.html — Weebly gallery (name from logo alt, caption description, website) (`firstmile_scraper.py`) |
| DFS Lab | `dfslab_companies.json` | 39 | dfs.vc/portfolio.html — portfolio cards (name, website, sector tags, description) (`dfslab_scraper.py`) |
| Symphonic Capital | `symphonic_companies.json` | 23 | symphoniccapital.com/portfolio-companies — Webflow/Finsweet cards (name, industry, description, website) (`symphonic_scraper.py`) |
| Rho Capital Partners | `rhocap_companies.json` | 30 | rho.com/portfolio — Squarespace summary grid (name, website, excerpt) (`rhocap_scraper.py`) |
| Tectonic Ventures | `tectonic_companies.json` | 41 | tectonicventures.com — homepage Webflow company directory (name, descriptor, website) (`tectonic_scraper.py`) |
| Array Ventures | `arrayvc_companies.json` | 79 | array.vc/portfolio — Astro tiles (name, sector, stage, description, latest news, detail page; no websites) (`arrayvc_scraper.py`) |
| Connetic Ventures | `connetic_companies.json` | 100 | conneticventures.com/portfolio — cards (name, website, theme, description, location, year) (`connetic_scraper.py`) |
| Room40 Ventures | `room40_companies.json` | 11 | room40.xyz — investment list (name, description, website, acquisition notes) (`room40_scraper.py`) |
| Hilltop Venture Partners | `hilltop_companies.json` | 49 | hilltopventurepartners.com/portfolio — Divi blurbs (name, description, status: active/bought by/IPO/died, detail page) (`hilltop_scraper.py`) |
| Companyon Ventures | `companyon_companies.json` | 16 | companyon.vc/portfolio — founder cards, image alt 'founder | company' (name, founders only) (`companyon_scraper.py`) |
| Laconia | `laconia_companies.json` | 52 | laconiacapitalgroup.com/portfolio — Squarespace lightbox captions (name, website, description) (`laconia_scraper.py`) |
| XRC Ventures | `xrc_companies.json` | 83 | xrcventures.com/portfolio — logo grid (names only) (`xrc_scraper.py`) |
| Morningside Ventures | `morningside_companies.json` | 68 | morningside.com/today/portfolio/venture — sector tree pages (name, tagline, description, website, sector path) (`morningside_scraper.py`) |
| Impact America Fund | `impactamerica_companies.json` | 30 | impactamericafund.com/portfolio — cards (name, description, exited marker) (`impactamerica_scraper.py`) |
| The Artemis Fund | `artemis_companies.json` | 32 | theartemisfund.com — homepage cards (name, founder) (`artemis_scraper.py`) |
| XFactor Ventures | `xfactor_companies.json` | 99 | xfactor.ventures/portfolio — Squarespace name list (name, detail page) (`xfactor_scraper.py`) |
| Sidecut Ventures | `sidecut_companies.json` | 18 | sidecut.vc — homepage cards (name from logo alt, description, Sidecut investment note) (`sidecut_scraper.py`) |
| Myriad Venture Partners | `myriad_companies.json` | 32 | myriadventures.com/portfolio — Webflow/Finsweet paginated accordion (name, website, sector, stage, status, description) (`myriad_scraper.py`) |
| Footwork | `footwork_companies.json` | 22 | footwork.vc — named companies in the homepage 'Who we are' paragraph (name, Footwork substack investment post / website) (`footwork_scraper.py`) |
| Rev1 Ventures | `rev1_companies.json` | 91 | rev1ventures.com/portfolio — logo grid (name, one-line description, detail page) (`rev1_scraper.py`) |
| Toyota Ventures | `toyotaventures_companies.json` | 98 | toyota.ventures/portfolio.html — portfolio sections (name, description, website) (`toyotaventures_scraper.py`) |
| NewView Capital | `newview_companies.json` | 86 | nvc.vc/portfolio — Webflow logo index + detail pages (name, description, founded year, CEO, focus, website, exit tag/status) (`newview_scraper.py`) |
| Galaxy Ventures | `galaxyventures_companies.json` | 86 | ventures.galaxy.com/portfolio — modal entries (name, description, website, category) (`galaxyventures_scraper.py`) |
| 137 Ventures | `137ventures_companies.json` | 67 | 137ventures.com/portfolio — Webflow grid + detail pages (name, description, website) (`137ventures_scraper.py`) |
| Type One Ventures | `typeone_companies.json` | 39 | type1ventures.com/portfolio — site's public Prismic API (name, vertical, stage, summary, description, website, founded year) (`typeone_scraper.py`) |
| Struck Capital | `struck_companies.json` | 62 | struckcapital.com/portfolio — cards (name, category, description, website) (`struck_scraper.py`) |
| Avid Ventures | `avid_companies.json` | 29 | avidventures.com — Framer Companies section (name, description, website, current/exited) (`avid_scraper.py`) |
| Leo Capital | `leocapital_companies.json` | 76 | leo.capital/portfolio — cards + detail pages (name, blurb, country, sector tags, target market, website) (`leocapital_scraper.py`) |
| TMV | `tmv_companies.json` | 57 | tmv.vc/companies — investment table (name, industry, website; no descriptions) (`tmv_scraper.py`) |
| Zeal Capital Partners | `zeal_companies.json` | 52 | zealcapitalpartners.com/portfolio — flip cards (name, status, description, website) (`zeal_scraper.py`) |
| Silicon Badia | `siliconbadia_companies.json` | 73 | siliconbadia.com/portfolio — WP grid + detail pages (name, description, industries, location, fund, website, acquired flag) (`siliconbadia_scraper.py`) |
| Story Ventures | `storyvc_companies.json` | 40 | storyventures.vc/portfolio — Webflow table (name, description, category, leaders, website) (`storyvc_scraper.py`) |
| True Global Ventures | `trueglobal_companies.json` | 22 | trueglobalventures.com/portfolio — tiles (name, description, website) (`trueglobal_scraper.py`) |
| Lakehouse Ventures | `lakehouse_companies.json` | 39 | lakehouse.vc/portfolio — Astro list + detail pages (name, tagline, description, stage, invested date, location, founders, website) (`lakehouse_scraper.py`) |
| Tera Ventures | `tera_companies.json` | 38 | tera.vc — homepage portfolio items (name, description, location, website) (`tera_scraper.py`) |
| Scrub Capital | `scrub_companies.json` | 20 | scrubcapital.com — homepage cards (name, investment date, round, syndicate, description, fund, website) (`scrub_scraper.py`) |
| Refract Ventures | `refract_companies.json` | 20 | refract.vc — homepage paragraph (name, website, acquirer; no descriptions) (`refract_scraper.py`) |
| Acronym VC | `acronym_companies.json` | 17 | acronym.vc/portfolio — Squarespace accordions (name, description, Acronym role, post-investment note; no websites) (`acronym_scraper.py`) |
| Nava Ventures | `nava_companies.json` | 17 | nava.vc/portfolio — Webflow project items (name, description, website) (`nava_scraper.py`) |
| Five Four Ventures | `fivefour_companies.json` | 12 | fivefourventures.com — homepage rows (name, category, website, acquisition note) (`fivefour_scraper.py`) |
| Scout Ventures | `scout_companies.json` | 54 | scout.vc/companies — companies list (name, description, tagline, industry, fund, exit flag, website) (`scout_scraper.py`) |
| Lobby Capital | `lobby_companies.json` | 41 | lobby.vc/portfolio — Elementor investment cards (name, status, sector, sub-sector, location, investment lead, about, website) (`lobby_scraper.py`) |
| Humba Ventures | `humba_companies.json` | 39 | humbaventures.com — homepage PORTFOLIO section by theme (name, one-line description, theme, website; unnamed stealth entries skipped) (`humba_scraper.py`) |
| Primetime Partners | `primetime_companies.json` | 34 | primetimepartners.com/portfolio — Webflow cards (name, description, website) (`primetime_scraper.py`) |
| The Venture Collective | `venturecollective_companies.json` | 57 | theventurecollective.com/portfolio — cards (name, tag, description, sector, website) (`venturecollective_scraper.py`) |
| Incisive Ventures | `incisive_companies.json` | 81 | incisive.vc/investments — investment cards (name, vehicle, description, memo, website) (`incisive_scraper.py`) |
| Wonder Ventures | `wonder_companies.json` | 72 | wondervc.com/portfolio — portfolio grid (name, description, categories, exit flag, website) (`wonder_scraper.py`) |
| Rosecliff Ventures | `rosecliff_companies.json` | 103 | rosecliff.com/portfolio — portfolio grid (name, description, website) (`rosecliff_scraper.py`) |
| SGH Capital | `sgh_companies.json` | 100 | sghcapital.com/portfolio — Webflow grid (name, category, website) (`sgh_scraper.py`) |
| The MBA Fund | `mbafund_companies.json` | 100 | thembafund.com/portfolio — Webflow cards (name, exit indicator; names only) (`mbafund_scraper.py`) |
| Acurio Ventures | `acurio_companies.json` | 95 | acurio.vc/portfolio — Webflow items + pop-ups (name, status, business model, sector, HQ, city, founded, initial/latest round, description, website) (`acurio_scraper.py`) |
| Very Serious Ventures | `veryserious_companies.json` | 83 | veryseriousventures.com — homepage Investments paragraph (names; angel vs fund, acquired flags) (`veryserious_scraper.py`) |
| Newtopia VC | `newtopia_companies.json` | 69 | newtopia.vc/portfolio — Elementor portfolio grid (name, one-line description, sector filter, detail page) (`newtopia_scraper.py`) |
| PointOne Capital | `pointone_companies.json` | 68 | pointone.capital/portfolio.html — portfolio cards (name, description, website) (`pointone_scraper.py`) |
| GFR Fund | `gfr_companies.json` | 64 | gfrfund.com/portfolio — portfolio grid (name, description, category, exit flag, website) (`gfr_scraper.py`) |
| Sandalphon Capital | `sandalphon_companies.json` | 48 | sandalphoncapital.com/portfolio — portfolio grid (name, sector/fund/stage tags, website) (`sandalphon_scraper.py`) |
| Acadian Ventures | `acadian_companies.json` | 46 | acadianventures.com/companies — Finsweet list (name, category, location, current/entry stage, description, website) (`acadian_scraper.py`) |
| Emergent Ventures | `emergentvc_companies.json` | 48 | emergent.vc/startups — startups list (name, description, category, website) (`emergentvc_scraper.py`) |
| Royal Street Ventures | `royalstreet_companies.json` | 48 | royalstreet.vc/portfolio — accordion (name, description, website) (`royalstreet_scraper.py`) |
| HealthX Ventures | `healthx_companies.json` | 36 | healthxventures.com/portfolio — Squarespace text blocks (name, description) (`healthx_scraper.py`) |
| TNB Aura | `tnbaura_companies.json` | 39 | tnbaura.vc/portfolio — Next.js cards (name, tagline, Scout/Exit/M&A/Closed label) (`tnbaura_scraper.py`) |
| ManchesterStory | `manchesterstory_companies.json` | 39 | manchesterstory.com/portfolio — Webflow pop-ups (name, description, website) (`manchesterstory_scraper.py`) |
| Motivate Ventures | `motivate_companies.json` | 62 | motivate.vc/portfolio — grid + detail pages (name, description, location, website) (`motivate_scraper.py`) |
| Noetic Fund | `noetic_companies.json` | 30 | noeticfund.com — Elementor CTA tiles (name, description, website) (`noetic_scraper.py`) |
| LongJump VC | `longjump_companies.json` | 33 | longjump.vc/portfolio — Webflow cards (name, founders, description, website) (`longjump_scraper.py`) |
| Orvel Ventures | `orvel_companies.json` | 32 | orvel.vc/portfolio — cards (name, country, description, website) (`orvel_scraper.py`) |
| Bay Wharf Capital | `baywharf_companies.json` | 36 | baywharfcapital.com/portfolio — grid (name, description, website) (`baywharf_scraper.py`) |
| Moderne Ventures | `moderne_companies.json` | 30 | moderneventures.com/portfolio — Finsweet cards (name, tagline, description, programme, exit tag, website) (`moderne_scraper.py`) |
| Lightscape Partners | `lightscape_companies.json` | 31 | lightscape.vc/portfolio — companies table (name, description, tags, location, year) (`lightscape_scraper.py`) |
| Abstraction Capital | `abstraction_companies.json` | 36 | abstraction.vc/portfolio — portfolio table (name, description, investment date, acquired flag, website) (`abstraction_scraper.py`) |
| Mission One Capital | `m1c_companies.json` | 30 | m1c.vc/portfolio — Squarespace accordion (name, category, geography, description, website) (`m1c_scraper.py`) |
| Roo Capital | `roo_companies.json` | 24 | roocapital.com/companies — Next.js cards (name, stage, sector, description, website) (`roo_scraper.py`) |
| Keyhorse Capital | `keyhorse_companies.json` | 229 | keyhorse.vc/portfolio — portfolio table (name, sector, Direct/Programmatic, exit flag) (`keyhorse_scraper.py`) |
| Emmeline Ventures | `emmeline_companies.json` | 25 | emmelineventures.vc/portfolio — Squarespace summary blocks (name, description, website) (`emmeline_scraper.py`) |
| Hemisphere Ventures | `hemisphere_companies.json` | 214 | hemisphere.com/companies.html — companies grid (name, category) (`hemisphere_scraper.py`) |
| RunwayVC | `runwayvc_companies.json` | 22 | runway.vc/portfolio — portfolio tiles (name, fund, one-liner, website) (`runwayvc_scraper.py`) |
| Kopa Ventures | `kopa_companies.json` | 23 | kopa.vc/portfolio — Wix repeater (name, description, website) (`kopa_scraper.py`) |
| Noveus Capital | `noveus_companies.json` | 29 | noveus.vc — homepage list (name, website; names only) (`noveus_scraper.py`) |
| Altari Ventures | `altari_companies.json` | 33 | altariventures.com — homepage logos (name from alt, website) (`altari_scraper.py`) |
| Blue Lion Global | `bluelion_companies.json` | 28 | bluelion.co — Finsweet grid (name from alt, Current/Prior status, industry, website) (`bluelion_scraper.py`) |
| BroadLight Capital | `broadlight_companies.json` | 14 | broadlightcapital.com/portfolio — portfolio cards (name, description, website) (`broadlight_scraper.py`) |
| BoutiqueVC | `boutiquevc_companies.json` | 22 | boutiquevc.com/portfolio — Webflow cards (name, subtitle, stage badge) (`boutiquevc_scraper.py`) |
| NuMundo Ventures | `numundo_companies.json` | 19 | numundoventures.com/portfolio — companies table (name, website) (`numundo_scraper.py`) |
| Firsthand VC | `firsthand_companies.json` | 12 | firsthand.vc — homepage cards (name, one-liner, website) (`firsthand_scraper.py`) |
| Cutting Horse | `cuttinghorse_companies.json` | 15 | cuttinghorse.com/portfolio — portfolio cards (name, category, Active/Exited) (`cuttinghorse_scraper.py`) |
| Behind Genius Ventures | `behindgenius_companies.json` | 29 | behindgeniusventures.com/portfolio — Webflow grid (name, sector, acquisition note) (`behindgenius_scraper.py`) |
| Argon Ventures | `argon_companies.json` | 37 | argon.vc/companies — companies grid (name, description) (`argon_scraper.py`) |
| Fjor Founders Fund | `fjor_companies.json` | 55 | fjor.co/portfolio — Wix portfolio (name; description/website where shown) (`fjor_scraper.py`) |
| OpenSky Ventures | `opensky_companies.json` | 28 | opensky.vc — Wix homepage (name, one-liner, website) (`opensky_scraper.py`) |
| Blitzscaling Ventures | `blitzscaling_companies.json` | 44 | blitzscalingvc.com/portfolio — Wix repeater (name, one-liner, website) (`blitzscaling_scraper.py`) |
| DASH Ventures | `dashventures_companies.json` | 40 | dashventures.com — Webflow portfolio pop-up cards: name, industries, markets, investment date / stage / status, website and description (each company appears twice in the markup; deduped) (`dashventures_scraper.py`) |
| Valuestream Labs | `valuestreamlabs_companies.json` | 47 | valuestreamventures.com/portfolio — portfolio grid: company name, one-line description and website (`valuestreamlabs_scraper.py`) |
| Beyond Capital Ventures | `beyondcapital_companies.json` | 17 | beyondcapitalventures.com/portfolio — Squarespace accordion: company name, location (italic line), description and LEARN MORE website link (`beyondcapital_scraper.py`) |
| Humbition | `humbition_companies.json` | 35 | humbition.com/portfolio — numbered portfolio list: company name with website link, description and founder name(s) (`humbition_scraper.py`) |
| Airwing | `airwing_companies.json` | 18 | airwing.vc/portfolio — portfolio tiles: company name, one-line description and website (the server sometimes returns a truncated page, so it is re-fetched) (`airwing_scraper.py`) |
| Blue 9 Capital | `blue9capital_companies.json` | 30 | blue9capital.com/portfolio — Wix portfolio repeater: company name, description and website (`blue9capital_scraper.py`) |
| Cartography Capital | `cartography_companies.json` | 16 | cartographycapital.com/portfolio — Webflow rows: company name with website link, description and sector (`cartography_scraper.py`) |
| OCV Partners | `ocvpartners_companies.json` | 16 | ocvpartners.com/portfolio — Divi portfolio grid: company name (h3) and the site-written description beneath it (`ocvpartners_scraper.py`) |
| Primo Capital | `primocapital_companies.json` | 79 | primo.capital/portfolio — Webflow/Finsweet list: company name, description, strategy (Digital / Space / Health / Climate) and detail page (`primocapital_scraper.py`) |
| JumpStart Ventures | `jumpstartventures_companies.json` | 107 | jumpstart.vc/portfolio — Avada portfolio grid: company name, category and detail page; description and website from each company page (`jumpstartventures_scraper.py`) |
| Eutopia Ventures | `eutopia_companies.json` | 32 | eutopia.vc/portfolio — Webflow portfolio cards: company name, category and detail page (`eutopia_scraper.py`) |
| Lumir Ventures | `lumir_companies.json` | 14 | lumir.vc/companies — Webflow company rows: name, category, description, founders and detail page (`lumir_scraper.py`) |
| 1Flourish Capital | `oneflourish_companies.json` | 19 | 1flourish.com/portfolio — portfolio cards: company name, sector, description, stage and status badge (`oneflourish_scraper.py`) |
| Tenacity Venture Capital | `tenacity_companies.json` | 21 | tenacity.vc/portfolio — Webflow portfolio list: company name, description, sector, stage / year and detail page (`tenacity_scraper.py`) |
| SUM Ventures | `sumvc_companies.json` | 47 | sum.vc/portfolio — portfolio cards: company name, fund, sector tag and description (`sumvc_scraper.py`) |
| Stage Venture Partners | `stagevp_companies.json` | 13 | stage.vc/companies — Webflow case-study cards: company name, sector, tagline, exit badge and detail page (`stagevp_scraper.py`) |
| Secocha Ventures | `secocha_companies.json` | 59 | secocha.com — homepage portfolio marquee: company names (the marquee repeats each name; deduped) (`secocha_scraper.py`) |
| Archangel Ventures | `archangel_companies.json` | 73 | archangel.vc/our-portfolio — Astro portfolio grid: company name (screen-reader label) and detail page (`archangel_scraper.py`) |
| Ascension Ventures | `ascension_companies.json` | 147 | ascension.vc/portfolio — Next.js portfolio grid: company name (data-company-name) and Exited badge (`ascension_scraper.py`) |
| CSC Upshot Ventures | `upshot_companies.json` | 12 | csc-upshot.vc/portfolio — portfolio tiles (paginated): company name, description and website (`upshot_scraper.py`) |
| 1955 Capital | `capital1955_companies.json` | 12 | 1955.capital/portfolio — portfolio image captions: company name, sector and one-line description (`capital1955_scraper.py`) |
| Gutter Capital | `guttercapital_companies.json` | 26 | gutter.cc/companies — portfolio lists grouped by fund: company name with website link and fund (`guttercapital_scraper.py`) |
| Taram Capital | `taramcapital_companies.json` | 13 | taramcapital.com/companies — portfolio cards: company name, sector, description (Spanish) and detail page (`taramcapital_scraper.py`) |
| Endurance28 | `endurance28_companies.json` | 33 | endurance28.com/portfolio — founder gallery: each tile links to a company page giving the company name (page title), sector, description and website (`endurance28_scraper.py`) |
| Streetlife Ventures | `streetlife_companies.json` | 12 | streetlifeventures.com — homepage Portfolio section (Squarespace text blocks): company name with website link (`streetlife_scraper.py`) |
| Outward VC | `outwardvc_companies.json` | 34 | outwardvc.com/companies — company tiles: name, one-line description, category tags, exited flag and detail page (`outwardvc_scraper.py`) |
| Investible | `investible_companies.json` | 100 | investible.com/portfolio — Webflow/Finsweet portfolio grid: company name, status and detail page (Lorem-ipsum placeholder fields ignored) (`investible_scraper.py`) |
| Kadan Capital | `kadancapital_companies.json` | 18 | kadan.vc/portfolio — Webflow portfolio table: year, company name, sector, stage, region and detail page (`kadancapital_scraper.py`) |
| Emerging Ventures | `emergingventures_companies.json` | 50 | emerging.vc/portfolio — portfolio cards: description, tags, status and location; company name from each company page heading (`emergingventures_scraper.py`) |
| Brooklyn Bridge Ventures | `brooklynbridge_companies.json` | 100 | brooklynbridge.vc/portfolio — Gatsby page-data JSON for the Full Portfolio page: company name, summary and sector tags (`brooklynbridge_scraper.py`) |
| Future Positive Capital | `futurepositive_companies.json` | 15 | futurepositivecapital.com/companies — companies grid: company name, tagline and detail page (`futurepositive_scraper.py`) |
| Italian Founders Fund | `italianfounders_companies.json` | 32 | italianfoundersfund.com — homepage portfolio pop-ups: company name, country, sector, stage, description, website and founders (`italianfounders_scraper.py`) |
| Wavemaker 360 | `wavemaker360_companies.json` | 60 | wavemaker360.com/portfolio — Wix portfolio repeater: tagline and LEARN MORE link; company name from each company page title (`wavemaker360_scraper.py`) |
| Elevate Capital | `elevatecapital_companies.json` | 96 | elevate.vc/portfolio — Elementor portfolio archive (paginated): status badge and detail page; company name (page heading) and description from each page (`elevatecapital_scraper.py`) |
| S4S Ventures | `s4sventures_companies.json` | 11 | s4sventures.com — homepage portfolio logo list: company name (logo alt text) and website; acquisition notes where shown (`s4sventures_scraper.py`) |
| Haymaker Ventures | `haymaker_companies.json` | 32 | haymaker.com/portfolio — portfolio page: current Portfolio and Previous Investments grids of company names linking to their websites (`haymaker_scraper.py`) |
| Lytical Ventures | `lytical_companies.json` | 40 | lyticalventures.com/companies — Wix companies repeater: company name (logo alt text), description and detail page (`lytical_scraper.py`) |
| Waarde Capital | `waardecapital_companies.json` | 16 | waardecapital.com — homepage holdings: company name with website, country label, tagline, description and exit note (`waardecapital_scraper.py`) |
| Valor Ventures | `valorventures_companies.json` | 28 | valor.vc/portfolio — portfolio logo grid: company name (logo alt text) (`valorventures_scraper.py`) |
| Sarmayacar | `sarmayacar_companies.json` | 25 | sarmayacar.com/portfolio — Webflow portfolio modals: company name, website, CEO, founded and partnered dates, description (`sarmayacar_scraper.py`) |
| K3 Ventures | `k3ventures_companies.json` | 57 | k3.co/portfolio — Webflow portfolio tabs: company name, one-line description, website and sector (tab) (`k3ventures_scraper.py`) |
| Big Brain Holdings | `bigbrain_companies.json` | 78 | bigbrain.holdings — homepage portfolio grid: company name, sector tag, one-line description and website (`bigbrain_scraper.py`) |
| Tantauco Ventures | `tantauco_companies.json` | 28 | tantauco.vc/portfolio — Wix portfolio repeater: company name and website (`tantauco_scraper.py`) |
| IGNIA | `ignia_companies.json` | 51 | ignia.vc/portfolio — Webflow portfolio list: company name, fund, status, year, sectors, description and website (`ignia_scraper.py`) |
| Verge HealthTech Fund | `vergehealthtech_companies.json` | 37 | verge.fund/portfolio — portfolio cards: company name, stage, country, description and website (`vergehealthtech_scraper.py`) |
| Deviation Capital | `deviation_companies.json` | 110 | deviation.com — homepage Companies list from the embedded Next.js page data (names only; '(acq: X)' → exited with acquirer) (`deviation_scraper.py`) |
| South Central Ventures | `southcentral_companies.json` | 34 | sc-ventures.com/portfolio — portfolio grid: company name (logo alt text), website, one-line description and sector (`southcentral_scraper.py`) |
| Nascent VC | `nascentvc_companies.json` | 7 | nascent.vc — Framer homepage portfolio: company name with website link (repeated per breakpoint; deduped) (`nascentvc_scraper.py`) |
| Flair Ventures | `flairventures_companies.json` | 9 | flairvc.com/portfolio — Framer portfolio: company name (logo alt text) and website (`flairventures_scraper.py`) |
| Uncommon Denominator | `uncommondenominator_companies.json` | 43 | uncommonvc.com — homepage investments logo grid: company names from logo alt text ("Logo" / "Portfolio:" wording stripped; non-name alts skipped) (`uncommondenominator_scraper.py`) |
| Expansion VC | `expansionvc_companies.json` | 100 | expansionvc.com/portfolio — Webflow portfolio grid: company name, one-line description, website, category filters and acquired badge. (`expansionvc_scraper.py`) |
| Pathbreaker Ventures | `pathbreaker_companies.json` | 49 | pathbreakervc.com/companies — Squarespace companies page: each company block opens with the company name in bold (linked to its website) followed by the site's one-line description; co-investor lines kept; acquisition banners give exits. (`pathbreaker_scraper.py`) |
| Musha Ventures | `musha_companies.json` | 175 | mushaventures.com — homepage portfolio logo wall: company name (logo alt text, "logo" suffix removed), country, year and status badge. (`musha_scraper.py`) |
| Reshape Ventures | `reshape_companies.json` | 109 | reshape.co/portfolio — Squarespace accordion by sector: company name (link text, arrow removed) and website. (`reshape_scraper.py`) |
| Nido Ventures | `nido_companies.json` | 22 | desdeelnido.com/portfolio — Webflow portfolio cards: company name, fund, sector, year, one-line description and website. (`nido_scraper.py`) |
| Swizzle Ventures | `swizzle_companies.json` | 27 | swizzle.vc/portfolio — Framer portfolio cards: company name, sector, one-line description and website. (`swizzle_scraper.py`) |
| RiverPark Ventures | `riverpark_companies.json` | 136 | riverparkvc.com/portfolio — Cube Portfolio grid: company name, sector filters and detail page; description, location, stage, sector line and website from each company page. (`riverpark_scraper.py`) |
| Kokopelli Capital | `kokopelli_companies.json` | 30 | kokopelli.vc/the-portfolio — "Kokofolio" grid: company name and detail page; website from each company page's Visit Site link. (`kokopelli_scraper.py`) |
| Outrun Ventures | `outrun_companies.json` | 24 | outrunventures.com/blank — Wix Pro Gallery: company name (item title) and its website link. (`outrun_scraper.py`) |
| C4 Ventures | `c4ventures_companies.json` | 48 | c4v.com/companies — WordPress REST company records: company name, first paragraph of the site's write-up, fund, location, sector, theme and status taxonomies. (`c4ventures_scraper.py`) |
| Brick & Mortar Ventures | `brickmortar_companies.json` | 50 | brickmortar.vc/portfolio — Squarespace gallery: company name (image label) and website link. (`brickmortar_scraper.py`) |
| MAYA Capital | `maya_companies.json` | 45 | maya.capital/portfolio — Portfolio table: company name, description, sector, website, co-investors and founders. (`maya_scraper.py`) |
| Shilling | `shilling_companies.json` | 98 | shilling.vc/portfolio — Webflow portfolio grid: company name (logo alt text), sector, year, one-line description, fund and detail page. (`shilling_scraper.py`) |
| TheVentureCity | `theventurecity_companies.json` | 114 | theventure.city/companies — Webflow company grid: company name, region, founder(s), industry, description and detail page. (`theventurecity_scraper.py`) |
| Optum Ventures | `optumventures_companies.json` | 77 | optumventures.com/portfolio — Webflow portfolio table + panels: company name, description, founded and invested years, stage (incl. Exited), leaders, location and website. (`optumventures_scraper.py`) |
| OpenOcean | `openocean_companies.json` | 50 | openocean.vc/portfolio — Webflow portfolio cards: company name, description, website, themes, stage, location and investment status. (`openocean_scraper.py`) |
| PeakBridge | `peakbridge_companies.json` | 35 | peakbridge.vc/portfolio — JetEngine portfolio listing: company name, one-line description and detail page. (`peakbridge_scraper.py`) |
| Wireframe Ventures | `wireframe_companies.json` | 45 | wireframevc.com/portfolio — Webflow portfolio flip cards: company name, stage, investment date, description and website. (`wireframe_scraper.py`) |
| Ignition Partners | `ignition_companies.json` | 45 | ignition.vc/portfolio — Squarespace summary grid: company name and website link. (`ignition_scraper.py`) |
| Thomvest Ventures | `thomvest_companies.json` | 37 | thomvest.com/portfolio — Framer portfolio cards: company name, one-line description and profile page. (`thomvest_scraper.py`) |
| Illumina Ventures | `illuminaventures_companies.json` | 40 | illuminaventures.com/portfolio — Portfolio cards with modals: company name, sector and status tags, intro and website. (`illuminaventures_scraper.py`) |
| Camber Creek | `cambercreek_companies.json` | 49 | cambercreek.com/portfolio — Portfolio overlay items: company name, description and website. (`cambercreek_scraper.py`) |
| OTB Ventures | `otb_companies.json` | 36 | otb.vc/portfolio — Portfolio accordion: company name, tagline, about text, investment year, founders and OTB investors. (`otb_scraper.py`) |
| Rocketship.vc | `rocketship_companies.json` | 66 | rocketship.vc/portfolio — Portfolio list: company name (link text), website and Acquired badges. (`rocketship_scraper.py`) |
| KdT Ventures | `kdt_companies.json` | 71 | kdtvc.com/portfolio — Portfolio table: company name, sector, stage and website. (`kdt_scraper.py`) |
| seed + speed Ventures | `seedspeed_companies.json` | 46 | seedandspeed.com/portfolio — Webflow portfolio cards: company name (logo alt text), one-liner, year, stage, sector and detail page. (`seedspeed_scraper.py`) |
| Skyfall Ventures | `skyfall_companies.json` | 45 | skyfall.vc/portfolio — Webflow portfolio list (all paginated pages): company name, description, co-investors, initial investment year, status and website. (`skyfall_scraper.py`) |
| MEVP | `mevp_companies.json` | 59 | mevp.com/portfolio — Webflow portfolio cards: company name, description, location, sector, stage (incl. Exited) and detail page. (`mevp_scraper.py`) |
| One Way Ventures | `oneway_companies.json` | 56 | onewayvc.com/portfolio — Webflow portfolio table: company name, one-line description, category, investment stage, year partnered, status label and detail page. (`oneway_scraper.py`) |
| Eka Ventures | `eka_companies.json` | 24 | ekavc.com/portfolio — Webflow portfolio modals: company name, tagline, founders, first investment date, about, impact statement and website. (`eka_scraper.py`) |
| Riot Ventures | `riot_companies.json` | 28 | riot.vc — Webflow portfolio cards: company name (card title), one-line description and website. (`riot_scraper.py`) |
| JME Ventures | `jme_companies.json` | 20 | jme.vc — Webflow companies list: company name, investment date, status, fund and website. (`jme_scraper.py`) |
| Autotech Ventures | `autotech_companies.json` | 30 | autotechvc.com/portfolio — Squarespace summary grid: company name, excerpt and detail page. (`autotech_scraper.py`) |
| Momenta Ventures | `momenta_companies.json` | 71 | momenta.vc/portfolio-v2 — Portfolio page: company name and focus line from both the featured cards and the full logo grid. (`momenta_scraper.py`) |
| NZVC | `nzvc_companies.json` | 77 | nzvc.co.nz/portfolio — Portfolio cards: company name, category, blurb and detail page. (`nzvc_scraper.py`) |
| Movens Capital | `movens_companies.json` | 33 | movenscapital.com/our-portfolio — Portfolio accordion: company name, one-line description, sector, entry date, fund and website. (`movens_scraper.py`) |
| Shorooq | `shorooq_companies.json` | 97 | shorooq.com/portfolio — Portfolio list: company name, category, country and tagline. (`shorooq_scraper.py`) |
| Indico Capital Partners | `indico_companies.json` | 18 | indicocapital.com/our-companies — Webflow companies grid: company name, year, description, category, Past/Unicorn/Pre-Indico/RIP badges and detail page. (`indico_scraper.py`) |
| Squadra Ventures | `squadra_companies.json` | 26 | squadra.vc/pages/companies — Webflow companies page: company name, description and detail page. (`squadra_scraper.py`) |
| Fireside Ventures | `fireside_companies.json` | 69 | firesideventures.com/blogs/portfolio — Portfolio card grid: company name and portfolio page. (`fireside_scraper.py`) |
| Rockaway Ventures | `rockaway_companies.json` | 33 | rockawayventures.com/portfolio — Portfolio cards: company name, description and website. (`rockaway_scraper.py`) |
| Silverton Partners | `silverton_companies.json` | 109 | silvertonpartners.com/portfolio — Portfolio archive: company name (link title), first investment stage, status and sector tags, founders, description, location and detail page. (`silverton_scraper.py`) |
| Volta Energy Technologies | `voltaenergy_companies.json` | 25 | volta.vc/portfolio — Portfolio modals: company name, description and website. (`voltaenergy_scraper.py`) |
| LUMO Labs | `lumolabs_companies.json` | 35 | lumolabs.io/portfolio — Portfolio company list: company names. (`lumolabs_scraper.py`) |
| Cisco Investments | `ciscoinvestments_companies.json` | 281 | ciscoinvestments.com/portfolio — Portfolio cards: company name (logo alt text), investment status (Active/Exit), investment type and detail page. (`ciscoinvestments_scraper.py`) |
| Tech Square Ventures | `techsquare_companies.json` | 138 | techsquareventures.com/portfolio — Portfolio list: company name, founder, description, website and fund/program group (Engage, Early Stage Fund, Exited). (`techsquare_scraper.py`) |
| Stripes | `stripes_companies.json` | 93 | stripes.co/investments — Investment cards: company name, one-line description, status (Current/Realized) and detail page. (`stripes_scraper.py`) |
| Fuse | `fuse_companies.json` | 53 | fuse.vc/investments — Investments list: company name, category and website. (`fuse_scraper.py`) |
| BlueRun Ventures | `bluerun_companies.json` | 34 | brv.com/portfolio — Squarespace portfolio grid: company name and detail page. (`bluerun_scraper.py`) |
| MCJ Collective | `mcj_companies.json` | 30 | mcj.vc/capital — Squarespace portfolio grid: company name, excerpt, tags, category and detail page. (`mcj_scraper.py`) |
| Mouro Capital | `mouro_companies.json` | 53 | mourocapital.com/our-portfolio — Portfolio grid: company name, description, website and exit tag. (`mouro_scraper.py`) |
| Ascend Venture Capital | `ascend_companies.json` | 75 | ascend.vc/portfolio — Portfolio gallery: company name, one-line description and website. (`ascend_scraper.py`) |
| Blue Collective | `bluecollective_companies.json` | 89 | bluecollective.com/portfolio — Portfolio list: company name, website, founders and investment year. (`bluecollective_scraper.py`) |
| 2150 | `v2150_companies.json` | 29 | 2150.vc/investments — Framer investments page: company name and description. (`v2150_scraper.py`) |
| AltaIR Capital | `altair_companies.json` | 53 | altair.vc/portfolio — Tilda portfolio accordion: company name, description and website. (`altair_scraper.py`) |
| ISAI | `isai_companies.json` | 118 | isai.vc/portfolio — Squarespace portfolio logo wall: company name (site logo alt), status (exited) and fund category. (`isai_scraper.py`) |
| PROfounders Capital | `profounders_companies.json` | 61 | profounderscapital.com/portfolio — Webflow portfolio cards: company name (site logo alt), problem area, country, status tag, description and website. (`profounders_scraper.py`) |
| Altos Ventures | `altos_companies.json` | 158 | altos.vc — Framer portfolio list: company names. (`altos_scraper.py`) |
| Manta Ray Ventures | `mantaray_companies.json` | 64 | mantaray.vc/portfolio — Portfolio grid: company name, mission, stage, description, region and website. (`mantaray_scraper.py`) |
| Nextech Invest | `nextech_companies.json` | 66 | nextechinvest.com/portfolio — Portfolio modals: company name, type (private / public / acquired), description and website. (`nextech_scraper.py`) |
| SHIFT Invest | `shiftinvest_companies.json` | 73 | shiftinvest.com/portfolio — Portfolio grid: company name (site logo alt), one-line description and website. (`shiftinvest_scraper.py`) |
| Regeneration.VC | `regenerationvc_companies.json` | 36 | regeneration.vc/portfolio — Portfolio cards: fund, company name, description, location and website. (`regenerationvc_scraper.py`) |
| Everywhere Ventures | `everywherevc_companies.json` | 100 | everywhere.vc — Webflow portfolio list: company name, city, summary and category label. (`everywherevc_scraper.py`) |
| Maniv Mobility | `maniv_companies.json` | 37 | maniv.com/portfolio — Webflow portfolio popups: company name, sectors, tagline, description, region and website. (`maniv_scraper.py`) |
| HCVC | `hcvc_companies.json` | 53 | hcvc.co/pages/portfolio — Portfolio table: company name, website, country, year, stage and status. (`hcvc_scraper.py`) |
| Singular | `singular_companies.json` | 10 | singular.vc — Portfolio table: company name, one-line description and website. (`singular_scraper.py`) |
| Cleveland Avenue | `clevelandavenue_companies.json` | 67 | clevelandavenue.com/portfolio — Webflow portfolio grid: company name, description, website, type tags and exit date. (`clevelandavenue_scraper.py`) |
| Blossom Street Ventures | `blossomstreet_companies.json` | 33 | blossomstreetventures.com — Webflow portfolio cards: company name (linked in the write-up), description, date of investment, amount, fund, role and co-investors. (`blossomstreet_scraper.py`) |
| 42CAP | `cap42_companies.json` | 55 | 42cap.com/portfolio — Portfolio table: company name, what they do, year partnered, country, layer and status. (`cap42_scraper.py`) |
| FoodLabs | `foodlabs_companies.json` | 49 | foodlabs.com/portfolio — Webflow portfolio cards: company name (logo alt), categories, stage, tagline and website. (`foodlabs_scraper.py`) |
| PT1 Ventures | `pt1_companies.json` | 35 | pt1.vc/portfolio — Webflow portfolio list: company name, fund/exit tag, theme, description and website. (`pt1_scraper.py`) |
| IAG Firemark Ventures | `firemark_companies.json` | 35 | iagfiremarkventures.com/portfolio — Portfolio flip cards: company name, founded year, founders, CEO, country, year invested, sector and website. (`firemark_scraper.py`) |
| Tidal Ventures | `tidal_companies.json` | 31 | tidalvc.com/portfolio — Webflow companies accordion: company name, tagline, initial partnership stage, current milestone, location, investment manager and website. (`tidal_scraper.py`) |
| iGlobe Partners | `iglobe_companies.json` | 51 | iglobepartners.com/portfolio — Portfolio cards: company name, exit note (acquired / listed), one-line description and website (omitted when it points to an acquirer). (`iglobe_scraper.py`) |
| Bison Ventures | `bison_companies.json` | 19 | bison.vc — Portfolio list: company name, description, leadership, focus area and website. (`bison_scraper.py`) |
| Pi Labs | `pilabs_companies.json` | 30 | pilabs.vc/portfolio — Squarespace portfolio grid: company name, tagline, founding details and website. (`pilabs_scraper.py`) |
| Embark Ventures | `embark_companies.json` | 34 | embark.vc — Wix portfolio gallery: company name, description (with acquisition notes) and website (omitted when it points to an acquirer). (`embark_scraper.py`) |
| Anzu Partners | `anzu_companies.json` | 56 | anzupartners.com/portfolio — Filterable portfolio gallery: company name, description, location, investment date, sector and status filters. (`anzu_scraper.py`) |
| SeaChange | `seachange_companies.json` | 51 | seachangeventures.com/portfolio — Portfolio grid: company name, exit flag and website (omitted for exits, where the link points to news coverage). (`seachange_scraper.py`) |
| Sky9 Capital | `sky9_companies.json` | 109 | sky9.vc/portfolio — Portfolio page (Chinese): company names grouped by category, with exit/listing markers (stock tickers, acquisition badges). (`sky9_scraper.py`) |
| Ocean Azul Partners | `oceanazul_companies.json` | 40 | oceanazulpartners.com/portfolio — Portfolio blurbs: company name, website and one-line description. (`oceanazul_scraper.py`) |
| Gobi Partners | `gobi_companies.json` | 202 | gobi.vc/portfolio — Webflow paginated portfolio list: company name, description, location, region, industry and status. (`gobi_scraper.py`) |
| InReach Ventures | `inreach_companies.json` | 27 | inreachventures.com/portfolio — Portfolio tiles: company name, space, description, founder, location and website. (`inreach_scraper.py`) |
| UpHonest Capital | `uphonest_companies.json` | 74 | uphonestcapital.com/portfolios — Webflow portfolio: featured company cards (name, category) and accordion list (name, description, category, founder, year invested, website). (`uphonest_scraper.py`) |
| Shunwei Capital | `shunwei_companies.json` | 49 | en.shunwei.com/portfolio — Portfolio grid (English site): company name, description and website. (`shunwei_scraper.py`) |
| Motion Ventures | `motion_companies.json` | 16 | motion.vc/portfolio — Framer portfolio page: company name and one-line description. (`motion_scraper.py`) |
| TRIVE VC | `trive_companies.json` | 36 | trive.vc — Portfolio cards: company name, industry, description, fund, status and website. (`trive_scraper.py`) |
| Overline | `overline_companies.json` | 45 | overline.vc — Portfolio logo grid: company name (site logo alt), location and latest stage. (`overline_scraper.py`) |
| growX ventures | `growx_companies.json` | 20 | growx.vc — Portfolio grid: company name and one-line description. (`growx_scraper.py`) |
| Boreal Ventures | `boreal_companies.json` | 17 | boreal.vc — Webflow portfolio modals: company name, description, founders, investment date, investment focus and website. (`boreal_scraper.py`) |
| Flux Capital | `fluxcapital_companies.json` | 28 | fluxcapital.com/portfolio — Portfolio list: company name, stage(s) invested and website. (`fluxcapital_scraper.py`) |
| Earth Foundry | `earthfoundry_companies.json` | 23 | earthfoundry.com/portfolio — Webflow portfolio grid: company name, description, status and categories. (`earthfoundry_scraper.py`) |
| Concrete Venture Capital | `concrete_companies.json` | 21 | concrete.vc — Portfolio grid: company name (site logo alt), sector, one-line description and website. (`concrete_scraper.py`) |
| BioGeneration Ventures | `biogeneration_companies.json` | 42 | biogenerationventures.com/en/portfolio — Portfolio grid: company name and teaser description (current and archived companies). (`biogeneration_scraper.py`) |
| SV Health Investors | `svhealth_companies.json` | 75 | svhealthinvestors.com/portfolio — Portfolio logo grid: company name (card title) and country. (`svhealth_scraper.py`) |
| Building Ventures | `buildingventures_companies.json` | 43 | buildingventures.com/companies — Portfolio grid: company name and description. (`buildingventures_scraper.py`) |
| Vida Ventures | `vida_companies.json` | 31 | vidaventures.com/portfolio — Portfolio grid: company name and description. (`vida_scraper.py`) |
| Truffle Capital | `truffle_companies.json` | 24 | truffle.com/portfolio — Portfolio cards: company name, excerpt and exit tag. (`truffle_scraper.py`) |
| DOT Capital | `dotcapital_companies.json` | 21 | dotcapital.com — Portfolio popups: company name (site logo alt), summary and website (omitted when it links to a Dot Capital news post). (`dotcapital_scraper.py`) |
| Amex Ventures | `amexventures_companies.json` | 126 | americanexpress.com/us/business/american-express-ventures/portfolio.html — Portfolio logo wall: company names (site-authored logo alt text). (`amexventures_scraper.py`) |
**889 firm datasets (89,636 companies in all_companies.json) after the 2026-10-17 Queue 200 chunk 2 (Mouro Capital/Ascend Venture Capital/Blue Collective/2150/AltaIR Capital/ISAI/PROfounders Capital/Altos Ventures/Manta Ray Ventures/Nextech Invest/SHIFT Invest/Regeneration.VC/Everywhere Ventures/Maniv Mobility/HCVC/Singular/Cleveland Avenue/Blossom Street Ventures/42CAP/FoodLabs/PT1 Ventures/IAG Firemark Ventures/Tidal Ventures/iGlobe Partners/Bison Ventures/Pi Labs/Embark Ventures/Anzu Partners/SeaChange/Sky9 Capital/Ocean Azul Partners/Gobi Partners/InReach Ventures/UpHonest Capital/Shunwei Capital/Motion Ventures/TRIVE VC/Overline/growX ventures/Boreal Ventures/Flux Capital/Earth Foundry/Concrete Venture Capital/BioGeneration Ventures/SV Health Investors/Building Ventures/Vida Ventures/Truffle Capital/DOT Capital/Amex Ventures); previous: 839 firms / 86,946 after the 2026-10-17 Queue 200 chunk 1 (Expansion VC/Pathbreaker Ventures/Musha Ventures/Reshape Ventures/Nido Ventures/Swizzle Ventures/RiverPark Ventures/Kokopelli Capital/Outrun Ventures/C4 Ventures/Brick & Mortar Ventures/MAYA Capital/Shilling/TheVentureCity/Optum Ventures/OpenOcean/PeakBridge/Wireframe Ventures/Ignition Partners/Thomvest Ventures/Illumina Ventures/Camber Creek/OTB Ventures/Rocketship.vc/KdT Ventures/seed + speed Ventures/Skyfall Ventures/MEVP/One Way Ventures/Eka Ventures/Riot Ventures/JME Ventures/Autotech Ventures/Momenta Ventures/NZVC/Movens Capital/Shorooq/Indico Capital Partners/Squadra Ventures/Fireside Ventures/Rockaway Ventures/Silverton Partners/Volta Energy Technologies/LUMO Labs/Cisco Investments/Tech Square Ventures/Stripes/Fuse/BlueRun Ventures/MCJ Collective); previous: 789 firms / 83,838 after the 2026-10-17 Queue 50b (DASH Ventures/Valuestream Labs/Beyond Capital Ventures/Humbition/Airwing/Blue 9 Capital/Cartography Capital/OCV Partners/Primo Capital/JumpStart Ventures/Eutopia Ventures/Lumir Ventures/1Flourish Capital/Tenacity Venture Capital/SUM Ventures/Stage Venture Partners/Secocha Ventures/Archangel Ventures/Ascension Ventures/CSC Upshot Ventures/1955 Capital/Gutter Capital/Taram Capital/Endurance28/Streetlife Ventures/Outward VC/Investible/Kadan Capital/Emerging Ventures/Brooklyn Bridge Ventures/Future Positive Capital/Italian Founders Fund/Wavemaker 360/Elevate Capital/S4S Ventures/Haymaker Ventures/Lytical Ventures/Waarde Capital/Valor Ventures/Sarmayacar/K3 Ventures/Big Brain Holdings/Tantauco Ventures/IGNIA/Verge HealthTech Fund/Deviation Capital/South Central Ventures/Nascent VC/Flair Ventures/Uncommon Denominator); previous: 739 firms / 81,789 after the 2026-10-17 Queue 50a (Scout Ventures/Lobby Capital/Humba Ventures/Primetime Partners/The Venture Collective/Incisive Ventures/Wonder Ventures/Rosecliff Ventures/SGH Capital/The MBA Fund/Acurio Ventures/Very Serious Ventures/Newtopia VC/PointOne Capital/GFR Fund/Sandalphon Capital/Acadian Ventures/Emergent Ventures/Royal Street Ventures/HealthX Ventures/TNB Aura/ManchesterStory/Motivate Ventures/Noetic Fund/LongJump VC/Orvel Ventures/Bay Wharf Capital/Moderne Ventures/Lightscape Partners/Abstraction Capital/Mission One Capital/Roo Capital/Keyhorse Capital/Emmeline Ventures/Hemisphere Ventures/RunwayVC/Kopa Ventures/Noveus Capital/Altari Ventures/Blue Lion Global/BroadLight Capital/BoutiqueVC/NuMundo Ventures/Firsthand VC/Cutting Horse/Behind Genius Ventures/Argon Ventures/Fjor Founders Fund/OpenSky Ventures/Blitzscaling Ventures); previous: 689 firms / 79,203 after the 2026-10-17 Queue 20b (Toyota Ventures/NewView Capital/Galaxy Ventures/137 Ventures/Type One Ventures/Struck Capital/Avid Ventures/Leo Capital/TMV/Zeal Capital Partners/Silicon Badia/Story Ventures/True Global Ventures/Lakehouse Ventures/Tera Ventures/Scrub Capital/Refract Ventures/Acronym VC/Nava Ventures/Five Four Ventures); previous: 669 firms / 78,253 after the 2026-10-17 Queue 20 (FirstMile Ventures/DFS Lab/Symphonic Capital/Rho Capital Partners/Tectonic Ventures/Array Ventures/Connetic Ventures/Room40 Ventures/Hilltop Venture Partners/Companyon Ventures/Laconia/XRC Ventures/Morningside Ventures/Impact America Fund/The Artemis Fund/XFactor Ventures/Sidecut Ventures/Myriad Venture Partners/Footwork/Rev1 Ventures); previous: 649 firms / 77,283 after the 2026-10-17 Daily 20 (Western Technology Investment/Titan Capital/GTMfund/645 Ventures/Verve Ventures/Millennium Technology Value Partners/Tribeca Venture Partners/Verissimo Ventures/Alpha Edison/Collide Capital/Irregular Expressions/Act One Ventures/Hearst Ventures/Ingressive Capital/Kearny Jackson/Echo Health Ventures/LDV Capital/Differential Ventures/Rampersand/Rebright Partners); previous: 629 firms / 74,430 after the 2026-10-16 Queue 50 (Hitachi Ventures/Chevron Technology Ventures/Grotech Ventures/Moonshots Capital/Trucks VC/Lorimer Ventures/V1 VC/Golden Seeds/SoGal Ventures/Foundamental/NextGen Venture Partners/HLM Venture Partners/Data Point Capital/Elevate Ventures/Coalition Operators/VentureSouq/Fluent Ventures/Blackhorn Ventures/Urban Innovation Fund/Leadout Capital/Vitalize VC/Kaya Ventures/Ubiquity Ventures/Fresco Capital/Industrious Ventures/Vine Ventures/Right Click Capital/Pathlight Ventures/Trust Fund/January Ventures/Hypothesis/Script Capital/Seaside Ventures/Supernode Ventures/Great North Ventures/True Wealth Ventures/Matterscale Ventures/Savannah Fund/Trousdale Ventures/Era Ventures/Playfair Capital/Avalanche VC/How Women Invest/Sancus Ventures/Resilience Reserve/Asylum Ventures/Prototype Capital/SNÖCAP/Parameter Ventures/Planet A Ventures); previous: 579 firms / 71,793 after the 2026-10-16 List 50 (LifeX Ventures/Garuda Ventures/Breakout Ventures/SKY VC/Refactor Capital/Courtside Ventures/TEN13/Twelve Below/Theory Ventures/Matchstick Ventures/Collab Capital/Mercato Partners/Z Venture Capital/Backstage Capital/SJF Ventures/Geodesic Capital/TTV Capital/Interplay/E14 Fund/Dorm Room Fund/Oak Investment Partners/Third Sphere/Sterling Road/Draft Ventures/Untapped Capital/M25/Human Ventures/Canapi Ventures/Yes VC/6th Man Ventures/Arbor Ventures/Revel Partners/JLL Spark/Necessary Ventures/Kepple Africa Ventures/Tau Ventures/Next Ventures/Valar Ventures/Zetta Ventures/Runa Capital/Swell VC/Link Ventures/Remarkable Ventures/Focal VC/Path Ventures/Moment Ventures/Charge VC/Haystack/Mozilla Ventures/Lead Edge Capital); previous: 529 firms / 68,442 after the 2026-10-16 VC 50 (FJ Labs/In-Q-Tel/Celesta Capital/Creathor Ventures/Canvas Ventures/Astella/Fin Capital/Founders Future/Harpoon Ventures/Adara Ventures/HealthCap/Aisling Capital/Better Capital/Fenbushi Capital/ParaFi Capital/Sanofi Ventures/Spring Camp/Standard Crypto/Mission BioCapital/Beyond Next Ventures/Cervin Ventures/Hatteras Venture Partners/Mashup Ventures/Parkwalk Advisors/Manhattan Venture Partners/COMETA/Inflexor Ventures/Sauce.vc/K5 Global/G2 Venture Partners/Axeleo Capital/Raed Ventures/Smartfin/Future Africa/Dell Technologies Capital/Main Sequence/Next Frontier Capital/Album VC/Norrsken VC/Blue Bear Capital/Azolla Ventures/Symbolic Capital/Foxmont Capital Partners/Prime Movers Lab/Aavishkaar Capital/coparion/Material Impact/Saama Capital/Jeito Capital/Kurma Partners); previous: 479 firms / 62,694 (62,726 after the Hustle Fund refresh) after the 2026-10-16 High-Value 50 (Silver Lake/Vista Equity Partners/HongShan/TA Associates/Summit Partners/Bosch Ventures/Avenir Growth/Globis Capital Partners/BlueYard Capital/Innovation Endeavors/Felix Capital/Accel-KKR/S2G Ventures/Ventech/DBL Partners/SoftBank Vision Fund/BDMI/EQT/Samsung Catalyst Fund/Kinnevik/ZhenFund/Owl Ventures/SR One/Abingworth/Animoca Brands/Endeit Capital/Lattice Fund/Greenfield Capital/Activant Capital/Human Capital/DOMO Invest/Novartis Venture Fund/Premji Invest/Z47/Arrington Capital/Francisco Partners/Advent International/Hellman & Friedman/Leonard Green & Partners/Genstar Capital/Roark Capital/Stonepeak/Montagu Private Equity/BC Partners/Berkshire Partners/Investcorp/Vestar Capital Partners/H.I.G. Capital/New Mountain Capital/Clayton, Dubilier & Rice); previous: 429 firms / 55,774 after the 2026-10-16 Extra 50 (Cota/DCG/Garage/Designer Fund/Hashed/Teamworthy/Lightstone/RA Capital/Longitude/K Fund/Voyager/GreatPoint/Microtraction/Lumira/Vendep/Prime VP/Inovo/Frst/F2/N49P/Alta/Sawari/Gaingels/Passion/P101/Augmentum/Kae/Alpha Partners/Glasswing/Portage/M Ventures/Bain Capital Life Sciences/World Fund/Frazier/Algebra/Rally/10D/Eight Roads/Hyperplane/EVP/Magma Partners/Inventure/La Famiglia/Extantia/OSE/HOF/Knife/Georgian/Conviction/Maven 11); previous: 379 firms / 48,941 after the 2026-10-16 Daily 20 (Boost VC/Dragonfly/Multicoin/Betaworks/Cherry/Chiratae/IQ Capital/Flybridge/Long Journey/Ada/Section 32/Accomplice/Character/Weekend Fund/Hiro/CoinFund/Monashees/Electric/Breega/Griffin); previous: 359 firms / 47,628 after the 2026-10-15 Daily 20 (Bonfire/TenOneTen/Contour/Valor Capital Group/FTV/Polaris/Forgepoint/Evolution Equity/Glilot/G Squared/Fifth Wall/Orange Collective/VestedVC/Fly Ventures/BTV/QED/Third Rock/Flare Capital/Hetz/Peak XV); previous: 339 firms / 45,974 after the 2026-10-14 Daily 20 (OCA/Moxxie/Kibo/Lifeline/Peak/JMI/Energize/Play Ventures/Point72 Ventures/Ten Eleven/Spectrum Equity/Five Elms/Edison/Space Capital/Makers Fund/Monk's Hill/Jump Capital/Castle Island/7wire/Crosscut); previous: 319 firms / 44,292 after the 2026-10-13 Daily 20 (Wellington/Creandum/Sony Innovation Fund/Blume/Shrug/Joyance/Commerce Ventures/Hg/Day One/Higher Ground Labs/Version One/Compound/Origin Ventures/1confirmation/Valor/Corazon/Fuel/Round13/Relay/Ludlow); previous: 299 firms / 42,338 after the 2026-10-12 Daily 20 (Intel Capital/360 Capital/Hack VC/Equal/StandUp/Flagship/Liquid 2/Flourish/ffVC/United Ventures/TLV/Quona/Molten/BMW i Ventures/Framework/MPM BioImpact/IDG/Team8/HV Capital/DCM); previous: 279 firms / 41,154 after the 2026-10-11 Daily 20 (Stage 2/5AM/Next Coast/Converge/1kx/Variant/Mantis/Clean Energy Ventures/Drive/HTGF/PSL/Qiming/AlleyCorp/Samsara/Chicago Ventures/Foresite/Revolution/Trinity/Endiya/AgFunder); see all_companies.json for live totals.**

**Previously retired, now re-armed (2026-10-02):** SignalFire — factory attempts failed on description coverage in 2026-07; re-added with hand-written Webflow scraper (`signalfire_scraper.py`). Wing VC graduated bespoke on the same 2026-07 re-armed burst.

**Firms verified to publish NO portfolio on their own site** (no dataset possible under the
no-third-party-sources rule): Benchmark, Thrive Capital, DST Global, Tiger Global, Altimeter,
Sutter Hill Ventures, Greenoaks. Each was exhaustively checked (sitemaps, guessed paths,
embedded JS) — their sites are minimal brochures / gated LP portals.

**Network note (2026-07-01):** this machine intermittently cannot route to Webflow's current
CDN IP (`cdn.webflow.com` → 198.202.211.1). Affected scrapers (`parkway`, `khosla`, `spark`,
`oakhcft`, `8vc`, `lux`, `dragoneer`, also existing `rre`/`iconiq`) implement a fallback chain:
direct HTTPS → legacy-IP pin (75.2.70.75) → `r.jina.ai` read-only relay of the same page. On a
healthy network they use the direct route. Datasets fetched relay-only at build time: 8VC, Lux,
Dragoneer, Spark (spot-checked correct; re-run to refresh when routing is healthy). Afore
(`afore_companies.json`, added 2026-07-22) was transcribed from afore.vc's own portfolio page via
a read-only fetch relay for the same reason — its `afore_scraper.py` carries the standard
direct→legacy-IP→r.jina.ai fallback chain and re-derives straight from the source HTML on a
healthy network (verify the Finsweet card selectors against live markup on the first clean re-run).

## Layout
```
VC comps/
├── CLAUDE.md                 ← this file
├── railway.toml              ← Railway build/cron config (repo root; see §Automation)
├── requirements.txt          ← repo-root deps for Railway (requests, bs4)
├── data/                     ← ALL JSON (datasets + reports)
│   ├── companies.json + 51× <firm>_companies.json   (one per firm — see table above)
│   ├── + 2 thin datasets left: wingvc + signalfire — both RE-ARMED 2026-07-28
│   │     with a burst of 2 strong-model tries each (attempts set to 2 in
│   │     gen_attempts.json); bespoke-or-nothing: if they fail again, dataset,
│   │     Airtable row and all are deleted
│   ├── gen_attempts.json               ← factory attempt memory (see §Automation)
│   ├── discovered_candidates.json      ← auto-found firm queue (see §Automation);
│   │     in data/ NOT automation/ on purpose — Watch Paths would self-redeploy
│   ├── scrape_attempts.json            ← generic-scrape memory (§Automation)
│   ├── spend.json                      ← month-to-date API spend (§Automation)
│   ├── enrichment_report.json          ← provenance for enrich.py fills
│   └── everywhere_tagging_report.json  ← Lightspeed tagging report
├── scripts/                  ← per-firm scrapers (51 bespoke, 4 of them factory
│                               auto-generated; source in each docstring)
│   ├── enrich.py             ← Wikidata back-fill of empty fields
│   └── PLAYBOOK.md           ← how to scrape a new firm / per-source cheat-sheet
└── automation/               ← nightly Railway pipeline (see §Automation below)
```
Scripts resolve `../data` relative to their own file, so run from the repo root:
`python3 scripts/usv_scraper.py` (writes `data/usv_companies.json`). Each scraper has a
`--limit N` flag for quick test runs. Deps: `pip install requests beautifulsoup4`.

## Core principles (do not violate)
- **Site-tailored schema.** Only include fields the source actually exposes. Don't force
  every firm into the same shape; each `*_companies.json` has its own field set.
- **Never fabricate.** Missing scalar → `null`; missing list → `[]`. If the site doesn't
  publish it, leave it empty.
- **`scraped_at`** = the real run timestamp (ISO-8601 UTC). If genuinely unknown, `null` —
  never a guessed/today's date passed off as the scrape time. (Lightspeed `companies.json`
  has `scraped_at = null` for this reason.)
- **No Crunchbase / LinkedIn / PitchBook / investor databases.** External enrichment is
  Wikidata-only (see below).
- Most empty cells are **legitimately N/A** (e.g. exit/acquirer/ticker for active
  companies; sector when the firm never tags it). That is not "missing data" to invent.
- **Empty ≠ absent.** Before declaring a field N/A, check whether the data is *denormalized*
  into the **name suffix** (`Foo (Acquired)`, `Bar (NYSE: TICK)`) or **description prose**
  ("Acquired by X in YYYY"). A structured field that's empty for *every* record is a cue to
  go look there, not proof the site omits it. (See PLAYBOOK §Recon "Empty ≠ absent".)

## `everywhere_tags` taxonomy (exactly these 17 — verbatim spelling)
```
BioTech
Health
Cybersecurity
Dev Tools / Cloud
Consumer
Future of Work
Transportation / Mobility
FinTech / Insurance
RegTech/Gov/Legal
Deeptech / Robotics / AR/VR
Data & Analytics
Logistics / Supply Chain
Web3 / Crypto
PropTech
Gaming / Media / Entertainment
CPG
Climate / Sustainability
```
Rules:
- **AI alone is not a category** — classify an AI company by the *market it serves*
  (AI for devs → Dev Tools / Cloud; for work → Future of Work; for health → Health; etc.).
- Include a **vertical + enabling-tech** tag only when both clearly apply (e.g. health data
  → `Health` + `Data & Analytics`); if one is much weaker, drop it.
- Don't use **Consumer** or **Future of Work** as catch-alls.
- Order most→least relevant; **cap at 4**; no duplicates; every value must be one of the 17.
- Derive from the firm's own sector tags first (when present), else keyword-classify the
  name + description. Tagging is keyword-based (no LLM) and intentionally coarse — a few
  untagged stragglers / over-tags are acceptable.
- **The tags are the product** (user, 2026-07-27): the manager's dashboard agent builds
  comps by looking up `everywhere_tags`, so an untagged dataset is dead weight to the
  system's main consumer. Shared implementation: `automation/tags.py`
  (`classify`/`fill_empty`, keyword map lifted from `lererhippeau_scraper.py`), applied
  by the pipeline to every scrape result and by the factory before persist — fills ONLY
  empty tags, so a hand-written scraper's own tagging always wins. The pipeline also
  runs `tags.carry_forward` first (fresh records with empty tags inherit the previous
  dataset's tags, matched on company_url then name), so one-off enrichment survives
  weekly refreshes instead of being silently wiped. ONE sanctioned exception to
  "no LLM": `automation/llm_tag_backfill.py` (user decision 2026-07-27) — a one-off
  Haiku pass over companies with NO text signal, unknown→[] (never guess), verbatim-tag
  validation, provenance in `data/llm_tag_report.json`, spend booked to the ledger as
  `tag-backfill`. Recurring tagging stays keyword-based.

## Enrichment (`scripts/enrich.py`)
Back-fills empty fields in `companies.json`, `menlo_companies.json`, `usv_companies.json`
from **Wikidata** (free + attributable):
- **Fills ONLY empty fields; never overwrites** a non-empty value.
- Matches a company to its Wikidata item by **verified official-website (P856) domain** —
  ambiguous name-only matches are skipped (prevents wrong data).
- Pulls founders (P112), founding year (P571), industry→sectors (P452), ticker (P414/P249).
- Records every fill + source Q-id in `data/enrichment_report.json`.
- Coverage is partial by design (well-known companies match; long-tail private startups
  won't). Re-runnable and idempotent.

## Conventions
- Politeness: custom User-Agent, timeouts, retries/back-off, small sleeps between requests.
- **Remote: `https://github.com/michaeleverywhere/vc-comp` (public) — the manager's
  account, since 2026-07-24.** `ruszinn` is a Write collaborator; `origin` points there
  and plain `git push` works. The old `ruszinn/vc-comp` still exists but is retired —
  don't push to it. Because Railway commits data nightly, the remote is often ahead:
  **always `git pull origin main --no-rebase --no-edit` before pushing.**
- **Commit and push only when the user asks.** Concise message; NO co-author trailer
  (user preference, 2026-07-24). Commits use
  `git -c user.email="ruszinfilay@gmail.com" -c user.name="rus.perish"`.
- Use `/tmp` (or the session scratchpad) for recon HTML/temp files, not the repo.

## Quickstart: add a new VC firm
Usually nobody has to: `candidate_finder.py` tops the queue up on every discovery run
(§Automation). To force a specific firm, add `{firm_name, homepage}` to
`automation/candidates.json`, push, and let the discovery service handle it (finds the
portfolio page, scrapes, adds to Airtable, and the scraper factory attempts a bespoke
scraper). Manual path (for hard sites):
1. Recon the portfolio page (`curl` raw HTML; identify the data source). See PLAYBOOK §Recon.
2. Write `scripts/<firm>_scraper.py` following the shared template (PLAYBOOK §Template);
   output `data/<firm>_companies.json` with a site-tailored schema + `everywhere_tags`.
3. Test with `--limit`, then full run; validate (PLAYBOOK §Validation).
4. Optionally `python3 scripts/enrich.py` (add the file to its list) to Wikidata-fill gaps.

## Automation (`automation/` — Railway → Airtable, built 2026-07-23/24)
One self-contained pipeline; **no Zapier anywhere** (evaluated, then removed). Core idea:
a new firm is just a firm whose previous dataset is empty, so one loop handles both
discovery and refresh. Modes: `python3 automation/pipeline.py --mode discover|refresh|all`.

**Data flow:** candidate finder (discover mode only — tops up the queue) → roster (dedup
once, keyed on `data/<slug>_companies.json` filenames) →
per firm: scrape (bespoke script | generic extractor — **but new firms are
FACTORY-ONLY since 2026-07-28**, user decision: a dataset-less candidate is never
generic-scraped; it waits for the factory, so its first dataset is bespoke. Accepted
costs, chosen knowingly: no day-one data if the burst fails, and the
≥50%-of-baseline validation gate has no reference for new firms — the generic
extractor now only ever runs for dataset-bearing scraperless firms) → diff vs GitHub
(added/dropped/exited + health; `safe_to_commit` guard blocks empty/>20%-crater
overwrites) → commit to GitHub → **direct Airtable upsert** (`airtable_writer.py`, matched on `Data file`) with
auto-fill of every blank metadata cell (Name, Source URL, Notes, Source type, Scraper
module — via `names.py`; nothing is ever entered by hand, existing values never overwritten).

**Airtable:** base `Comps - Automations` (`appdSRg0657zG3oef`), table **`Private Comps`**
(NOT "Portfolio Companies" — that table exists but was cut from scope; `backfill_airtable.py`
is legacy). Table = 1 row per firm: registry metadata + Record/Prev/Delta count, `Scraper
health` (new/grew/same/shrank/count-drop/broke), Status (+`needs-scraper`,`broke`), Last
run/commit, and **17 per-tag Number columns**
(A firm that retires with NO dataset is DELETED from the table, not labelled — Airtable
is "firms with data", not a graveyard of attempts; user decision 2026-07-27, replacing
a needs-scraper→retired status flip that shipped and was superseded the same day.
`airtable_writer.delete_firms` removes the row on retirement night, and a
`delete_strays` reconcile pass on every discovery run backstops anything stranded —
keep-set = repo datasets + tonight's graduates + still-eligible firms, guarded by
`_MIN_KEEP` so an upstream glob bug can never empty the table. **Bespoke-or-nothing
(2026-07-28, user decision "I would like a bespoke script for every eligible firm"
+ "if the EV tags are missing, I do not need the data", superseding the previous
day's thin-is-not-failed stance):** a factory-failed firm now loses its thin
dataset too — `pipeline._retire_fully` drops the registry row, queues the Airtable
delete AND deletes the dataset from the repo (`gh.delete_json`; git history is the
undo). Lightspeed's hand-built `companies.json` can never get here — factory
`targets()` excludes it by construction. Repo-side memory files are unaffected by
all of this — they are what stops re-proposing/re-scraping.) (exact taxonomy names; note `Health` the tag
≠ `Scraper health`) holding how many portfolio companies carry each tag (double-counting
across tags is intended). `create_at_fields.py` created the schema; `fix_dupes.py`/`audit_at.py`
repaired a dup incident (trailing-whitespace Data-file keys — root cause fixed).

**Railway** (project on the MANAGER's account — corrected 2026-08-03; an earlier note here
said "user's account", which was wrong and would have sent a leaving intern hunting for a
project transfer that isn't needed. Michael owns the Railway org, the GitHub repo and the
dashboard agent; the only things that were ever intern-side are API keys minted on intern
accounts. Deploys from `michaeleverywhere/vc-comp`, root dir = repo root): service 1 "discovery" — `--mode discover`, cron daily `0 7 * * *`, LIVE and
verified (added Amplify 124 / Homebrew 106 / SignalFire 103 / Foundry Group / Wing VC;
9 JS-heavy sites correctly flagged needs-scraper: emergence, foundation, uncork, craft,
boldstart, costanoa, susa, bullpen, scaleventurepartners — as of the scrape memory they
are scraped once, fail, and are never scraped again, instead of every run forever).
Railway vars: GITHUB_TOKEN (fine-grained, **must be created on michaeleverywhere**,
Contents r/w on the one repo), GITHUB_REPO=michaeleverywhere/vc-comp, GITHUB_BRANCH,
GITHUB_DATA_DIR, AIRTABLE_PAT (data.records read+write), AIRTABLE_BASE_ID, AIRTABLE_TABLE.
Local `automation/.env` mirrors these (git-ignored; Airtable schema-write PAT stays
laptop-only). Data commits from Railway land as `Nightly: <slug> …`.

**Candidate finder** (`candidate_finder.py`, added 2026-07-27; runs FIRST in discover/all
mode, before the roster is built, so a firm found tonight is scraped — and possibly
factory-generated — the same night). Fixes the queue's dead end: `candidates.json` was a
hand-written starter list, so once the factory drained it discovery had nothing left to do.
Each run asks the Claude API for VC firms not already covered (`FIND_PROPOSALS`, default 12
per call; the exclude list is every repo firm + both candidate lists + the no-portfolio 7),
then **verifies every proposal against its live site before queueing it** — a model can
invent a firm or misattribute a domain, so a proposal is a LEAD, not data. Gates:
homepage must serve HTML; the PAGE (not the domain — that would be circular, since a
made-up firm gets a domain spun from its own name) must carry the firm name; the site must
read like a VC firm. Portfolio-URL resolution is a HARD gate (2026-07-27 — it was soft
for exactly one night, and the one firm the soft gate queued, LocalGlobe, was dead
within a single run: terminal no-url retirement means the factory can never rescue a
firm the resolver can't see, so a null-portfolio candidate is a guaranteed tombstone):
no resolvable portfolio page → rejected permanently, and the loop keeps testing that
night's remaining proposals, so a run queues a firm with a real path to a dataset or
queues nothing. Every queued entry now carries a portfolio URL. Per user
decision **`FIND_MAX_PER_RUN=1`** (one new firm per run), with `FIND_MAX_OPEN=25` pausing
the finder while the backlog is deep; `FIND_MODEL` defaults to claude-sonnet-4-5.
**That backlog count excludes FINISHED firms** (`_pending`): a factory-retired or
scrape-dead firm never gains a dataset, so counting it as "unprocessed" made the number
rise monotonically — measured, the finder shut itself off on night 16 and stayed off.
Retired ≠ pending. Regression-tested with a 30-night simulation.
State is `data/discovered_candidates.json` (a JSON list, repo-committed like
`gen_attempts.json` so ephemeral containers read it back). **Rejected entries are kept on
purpose** — they stop the model re-proposing and re-verifying the same dead domain nightly.
`roster.py` reads both candidate lists as one; `names.py` reads the queue too, so
discovered firms get real Airtable names instead of title-cased slugs. Failures are caught
and printed — the finder must never break the run. Test locally:
`python3 automation/candidate_finder.py --dry-run`.

**Spend ceiling + model escalation** (`budget.py` + `data/spend.json`, added 2026-07-27,
user requirement "under $5/month **with one firm per day**"). The only variable cost is
the Claude API — the factory is ~97% of it, the finder ~$0.006/run. `GEN_MAX_PER_RUN`
caps FIRMS per night, not dollars, so it cannot enforce a budget. Two changes:

1. **Escalation** (`scraper_gen.model_for`): a burst runs the CHEAP model
   (`GEN_MODEL_CHEAP`, default claude-haiku-4-5) for its early tries and the strong one
   (`GEN_MODEL`, default claude-sonnet-4-5) for the last `GEN_STRONG_TRIES` (**2**).
   Rationale: the guard rejects bad output rather than committing it, so a cheap first
   attempt risks nothing but a retry. A 1-try burst goes straight to strong. Set the two
   model vars equal to disable. Firm cost fell ~$0.21 → ~$0.10; **a firm a day now costs
   ~$3.09/month**. TWO strong tries, not one, and `GEN_MAX_ATTEMPTS` default went 3 → 4
   to pay for it: escalation initially left Sonnet a single shot where it previously had
   the firm's whole budget with failure feedback between tries (the loop that got
   foundrygroup through on try 2) — a quality regression smuggled in as a cost saving.
   At the observed mix the extra try is free, since most firms finish on try 1.
   Relatedly, `_feedback_block` now LABELS each attempt with the model that produced it
   and, when the code being shown came from a different model, tells the reader it was a
   smaller one and to discard rather than patch a wrong approach — unlabelled, Sonnet
   read Haiku's broken code as its own prior reasoning.
2. **Ledger**: every response's `usage` is priced (cache writes 1.25x, reads 0.1x —
   folding those into base input would overstate a burst ~3x) and accumulated per
   calendar month. `MONTHLY_BUDGET_USD` default **4.50**. NOTE the prompt cache is
   PER-MODEL, so the escalated Sonnet try pays a fresh cache write, not a 0.1x read —
   a worst-case 3-try burst is ~$0.24, not ~$0.11.

`can_generate()` requires the burst estimate PLUS a `_FINDER_RESERVE` ($0.25): without
it the factory spends to the line and the finder's remaining nights push the month over
(observed in test: $4.53 against a $4.50 budget). The finder itself stops only when the
budget is truly gone. Month rolls over on its own — a different `month` key loads a fresh
ledger, no cron. Unknown model strings are charged at the dearest known rate, so a model
swap throttles early rather than overspending silently. Ledger is repo-committed (data/,
outside Watch Paths) and saved BEFORE the factory flush, like the scrape memory, for the
same redeploy-kills-the-container reason. Measured over a simulated 30-night month:
**observed mix = 30/30 firms for $3.09; worst case (every firm fails all 3 tries) =
17/30 firms for $4.29** — throttles rather than overspends. Residual leak: a container
killed mid-burst loses ≤$0.24 unrecorded. The Anthropic Console spend limit is still the
real wall; this guard is cooperative. Tests: `automation/test_budget.py`.

**Scrape memory** (`scrape_state.py` + `data/scrape_attempts.json`, added 2026-07-27).
Closes the last memoryless stage: a candidate the generic extractor couldn't read was
re-scraped IN FULL every night forever (homepage + ~15 guessed portfolio URLs ≈ 16
fetches × 9 stuck candidates ≈ **144 requests/night** to reproduce 9 known failures,
plus 9 `needs-scraper` Airtable writes). **Per user decision: one failure and the firm is
never scraped again** (`next_attempt: null`). A widening 1→3→7→30-day retry was built
first and rejected as too fiddly to reason about — it survives as the
`SCRAPE_BACKOFF_DAYS="1,3,7,30"` env override, and deleting a firm's entry re-arms it.
Accepted cost: a site that merely happened to be down that night is written off, and the
way back is manual. A successful scrape deletes the entry. Kept SEPARATE from
`gen_attempts.json` on purpose: different question ("can the extractor read this page?"
vs "can Claude write a scraper?"), different retirement terms, and merging them would let
a factory retry silently reset the scrape memory.
**Factory retirement now also stops the scraping** — `gen_state.eligible()` is checked in
the scrape loop, which is what CLAUDE.md always claimed but the code never did
(`gen_state` was imported only inside the factory block). Measured over 30 simulated
nights: 4320 → 144 fetches, **97% fewer** — one night's worth, then zero forever.
Two implementation constraints, both load-bearing: the skip runs BEFORE any network call
and does NOT remove the firm from `firms` (the factory iterates that list, so filtering
it would delay generation); and the state is committed right after the scrape loop, not
at the end — the factory's flush pushes to `scripts/` and redeploys Railway, killing the
container before any later write lands. Bespoke firms are exempt — a broken hand-written
scraper is real breakage and must never be silenced. Tests:
`automation/test_scrape_backoff.py` (offline; includes the 30-night request-count
simulation — a backoff that looks right but still fetches nightly would pass every unit
test and fix nothing).

**Scraper factory** (`scraper_gen/guard/runner/factory.py`, wired into discover mode):
auto-generates BESPOKE rich scrapers via Claude API — user chose **no human approval**, so
three machine gates replace review: AST allowlist (no env/subprocess/eval/open/getattr…),
sandboxed run with token-scrubbed env, output validation (≥10 recs, ≥50% of generic
baseline, ≥95% names, ≥60% urls, ≥30% descriptions, no stringified lists/dicts). Pass → commit scraper (trusted
runnable footer) + rich dataset; the push triggers Railway rebuild so the firm becomes
bespoke. Generate-once per firm; `GEN_MAX_PER_RUN=3`; targets = the 6 thin datasets first
(proven scrapeable), then needs-scraper candidates. Accepted residual risk: subtly-wrong
values can pass validation (revert the firm's commit if so). **Live since 2026-07-27**,
first runs validated everything in production: amplify (114 recs, try 1), felicis (275,
try 1), foundrygroup (56, try 2 — the feedback loop's first win), homebrew (162, try 1)
graduated bespoke; signalfire retired after 3 tries all failing "description coverage
< 30%" (the legitimately-thin case working as designed). Cache write→read visible in
`[gen]` token log lines; a full 3-try burst ran ~$0.26.
**Attempt memory + burst retries (added 2026-07-26, burst 2026-07-27;**
`automation/gen_state.py`**):** per user decision, a firm gets its WHOLE generation
budget the first night it's tried: `attempt()` bursts up to `GEN_MAX_ATTEMPTS` (default 3)
tries in one run — site context fetched once, each retry prompted with the burst's
earlier failure reasons + last code so it varies its approach; the context block is
cache-marked (prompt caching: retries pay ~10% input on it, usage printed per call)
— and if none passes the
gates the firm is **retired the same night** (no rolling backlog; every targeted firm
leaves the queue as bespoke or retired). Failures are logged to `data/gen_attempts.json`
(committed via the store like a dataset, so ephemeral Railway runs read it back; local
runs use the file directly); retired/`"skip": true` firms are filtered out of `targets()`
*before* the `[:GEN_MAX_PER_RUN]` slice (`GEN_MAX_PER_RUN` still caps FIRMS per run).
`generation error:` API-transport flukes abort the burst uncounted (firm retries next
run). Manual `"skip": true` = "legitimately thin, leave it alone"; success deletes the
firm's entry; re-arm a retired firm by deleting/editing its entry.
**Terminal no-url retirement (2026-07-27, user decision "if no portfolio page resolves
on step 1 — retire the firm"):** `attempt()` marks a "no portfolio url" result
`terminal: True`, and `gen_state.record_failure(..., terminal=True)` sets
`"retired": true` on the entry — the firm is retired the SAME night, whatever its
attempt count. Rationale: the 4-try budget exists for generation failures, where
feedback between tries helps; a no-url failure shares nothing with that — there is no
page to generate against, so each "retry" was one counted no-op per night (~2 weeks of
`needs-scraper` in Airtable for the 9 JS-heavy candidates). Recorded as a FLAG, not
`attempts = max`, so the count stays honest; guarded by `counted`, so a transport fluke
can never retire a firm. The flag lives inside `eligible()`, so it propagates to all
three consumers at once: factory `targets()`, the scrape-loop skip, and the finder's
`_pending` backlog count. `"portfolio page unreachable"` (URL resolved, fetch failed)
stays NON-terminal on purpose — that shape is transient network, not structural.
Fixing this exposed a latent Airtable hole: a firm retiring on a night the
scrape memory had SKIPPED it had no registry row, so the needs-scraper→retired status
flip found nothing and the status stranded at `needs-scraper` forever. The first fix
synthesized a minimal `retired` row; hours later the user chose deletion over
labelling, so the retire branch now calls `pipeline._retire_from_airtable` instead —
in-run row dropped before the upsert, prior nights' row deleted after it (see the
Airtable section). Net effect as it actually played out: emergence/foundation/uncork
retired on the first live run ($0), and the remaining six were pre-retired by hand
the same evening rather than burning three more nights. Tests:
`automation/test_factory_retire.py` (offline; includes a 30-night simulation proving
exactly ONE attempt is ever recorded — a flag that looked right but left the firm in
`targets()` would pass every unit test and fix nothing).
**Self-redeploy guard (2026-07-27):** a mid-run GitHub push makes Railway redeploy the
service and STOP the running container (observed: felicis's success commit killed the
foundrygroup burst). Factory commits are therefore deferred to end-of-run
(`pipeline._flush_factory_commits`, after the Airtable upsert; scraper before dataset so
a kill between them self-heals). Pair with **Watch Paths** on both Railway services
(`automation/**`, `scripts/**`, `requirements.txt`, `railway*.toml`) so data-only
commits — incl. the refresh service's per-firm `Nightly:` commits — never rebuild.

**State at session end (2026-07-27):**
- DONE (2026-07-26/27 session): factory LIVE and validated end-to-end in production —
  burst retries w/ failure feedback, prompt caching, type-integrity gate, attempt
  memory + same-night retirement, deferred end-of-run commits (self-redeploy guard),
  Watch Paths set on discovery. 4 firms graduated bespoke (amplify, felicis,
  foundrygroup, homebrew — see table), signalfire retired. `ANTHROPIC_API_KEY` + spend
  limit live on the discovery service. Refresh service CREATED (named "monthly refresh"
  but cadence is WEEKLY per user decision; settings partially verified — item 1). Laptop `automation/.env` repaired (PAT was comment-mangled).
- DONE (2026-07-27, later): **candidate finder** written + wired (see above), so the
  discovery queue refills itself and `candidates.json` stops being a dead end. Gates are
  covered by `automation/test_candidate_finder.py` (offline, no key/network/cost —
  injected fetchers + stubbed proposals; run it after touching `_PROMPT`, `verify()` or
  `identity.py`). First live `--dry-run` proposed Canaan + Matrix (genuinely new, good)
  and **Lightspeed — a firm the repo already has**, which exposed a latent bug in the
  system's only dedup gate: `companies.json` predates the `<slug>_companies.json`
  convention, so `identity.slug_from_file()` returned None for it and Lightspeed had NO
  slug — invisible to `is_known()` and absent from the finder's exclude list. Any
  candidate named Lightspeed would have been scraped into a competing
  `lightspeed_companies.json`. FIXED via `identity._FILE_ALIASES` (bidirectional
  file↔slug map) + `_excludes` now asking identity what counts as a dataset instead of
  doing its own `endswith` test. Regression-tested.
- DONE (2026-07-28): **first live run, and it worked** — `spend.json` created
  ($0.3907 / 6 calls), 10 firms written to the scrape memory, 3 retirements logged,
  10 Airtable rows upserted, run cost $0.39. Escalation confirmed in the logs
  (wingvc: Haiku $0.0347 → Haiku $0.0113 → **Sonnet** $0.1154 → **Sonnet** $0.0476)
  and with it the PER-MODEL cache: `cache_write` on try 1, `cache_read` on try 2,
  then `cache_write` AGAIN on the switch to Sonnet — the cost model was right.
  Two defects found and fixed:
  (a) **the finder queued "Andreessen Horowitz"** though `a16z_companies.json` holds
  852 of its companies. Lightspeed's bug in a new guise — the slug is a NICKNAME, so
  `is_known()` slugified to "andreessenhorowitz" and never reached "a16z", AND
  `firm_names.json`'s single display name is "a16z", so the model was never told the
  full name. Fixed with `identity._ALT_NAMES` (a16z, usv, nea, crv, ivp, tcv, svangel,
  8vc, lightspeed), which feeds BOTH the dedup gate and the exclude list. Self-heals:
  the stale queue entry is now filtered out by the roster. **Add to `_ALT_NAMES`
  whenever a dataset slug cannot be spelled out from the firm's name.**
  (b) signalfire's generated code had a duplicate kwarg — `ast.parse` ACCEPTS that
  (it's a bytecode-compile error), so it passed `static_check` and died in the
  sandbox instead. Nothing shipped; defence in depth worked. `static_check` now also
  runs `compile()`, so it fails in milliseconds with a clear reason.
- DONE (2026-07-27, later session): **terminal no-url retirement** (see the factory
  section above): "no portfolio url" now retires a firm the same night via a
  `"retired": true` flag in `gen_attempts.json`, instead of burning 4 counted no-ops
  across ~2 weeks; the retire branch synthesizes a minimal Airtable row when the
  scrape-skip meant none existed (latent stranded-at-needs-scraper bug). The 9 stuck
  JS-heavy candidates should flip to `retired` in Airtable over the next ~3 nights
  (≤3/night). Takes effect on Railway once pushed (the push rebuilds discovery via
  Watch Paths on `automation/**`); sandbox commits work but the push runs from the
  Mac terminal.
  Wingvc + signalfire had already exhausted the 4-attempt path the old way; with both
  retired, the factory queue is empty except emergencecapital (now retires on its next
  pass) and whatever the finder adds. Tests: `automation/test_factory_retire.py`.
- DONE (2026-07-27, same evening — first live run of the terminal path, plus user
  feedback "no failed firms piling up in Airtable/GitHub; a day should add a REAL
  firm"): the deploy-run retired emergence/foundation/uncork same-night at $0
  (terminal path verified live) but also queued LocalGlobe — verified real, no
  portfolio page — which was dead within the run: the soft finder gate was
  manufacturing tombstones. Three changes, all offline-tested: (1) the finder's
  portfolio gate is now HARD (see finder section; regression test
  `test_no_portfolio_is_hard_gate`); (2) Airtable tombstones are deleted, not
  labelled — delete-on-retire + per-run `delete_strays` reconcile (see Airtable
  section; supersedes both the `retired` status flip and the synthesized-row fix
  from earlier the same day); (3) one-time cleanup: the six never-factory-tried
  JS-heavy firms pre-retired via `"retired": true` with `attempts: 0` (honest — no
  try ran), and the LocalGlobe + stale a16z queue entries flipped to `rejected`.
  The ~11 tombstone rows vanish on the next discovery run via the reconcile (the
  Cowork sandbox cannot reach api.airtable.com; Railway does it). Factory queue is
  now EMPTY; the finder starts clean, and every firm it queues carries a portfolio
  URL. Watch the first hard-gate `[find]` lines for over-rejection: if too many
  real firms bounce on "no portfolio page resolved", the resolver (not the gate)
  is the thing to improve.
- DONE (2026-07-28): **Notes column now carries the RAW dataset URL.**
  `names.notes_url` returned the github.com *blob* form from when a private repo
  was assumed; blob serves HTML, so the manager's dashboard couldn't read it —
  first seen on matrixpartners, the finder's first hard-gate graduate (queued →
  generic 110 recs → bespoke 45 the same night; the 110 included footer junk like
  "Matrix Press Kit", so the drop is a cleanup, not a crater). Rows seeded by
  `populate_registry` already had raw links; only auto-filled rows were affected.
  Fixed + `_fill_blank_meta` upgrades stale blob Notes in place (exact blob-prefix
  match only — hand-written notes untouched). Data quirks in
  `matrixpartners_companies.json` to revisit: the generated scraper pads
  descriptions/founders from each company's OWN homepage (gate-gaming the ≥30%
  description rule — founders caught junk like "Join Our" / "Claude Code");
  sectors/stage/status/profile_url are all-null stubs; two names have trailing
  commas. Consider a factory-prompt rule (firm's own pages only) + a founders
  plausibility gate. Also note the ≥50%-of-baseline gate is vacuous for same-night
  graduates (generic result isn't written locally, so baseline reads 0).
- DONE (2026-07-28, "I would like a bespoke script for every eligible firm"): three
  user decisions, offline-tested: (1) **new firms are FACTORY-ONLY** — the scrape
  loop skips dataset-less generic candidates entirely (no fetches, no needs-scraper
  row, no scrape-memory entry); their first dataset is the bespoke one. The generic
  extractor's remaining role is refreshing dataset-bearing scraperless firms, a
  class that is now only wingvc/signalfire (transiently) + protected Lightspeed.
  (2) **bespoke-or-nothing retirement** — `_retire_fully` (renamed from
  `_retire_from_airtable`) also deletes a retiree's thin dataset from the repo via
  new `gh.delete_json` (git-recoverable; data/ is outside Watch Paths so the
  deletion never redeploys). (3) **wingvc + signalfire re-armed** with `attempts: 2`
  in gen_attempts.json = a burst of exactly 2 strong-model (Sonnet) tries each on
  the next discovery run, ~$0.50 worst case; if either fails both, it vanishes
  fully per (2). Watch that run's `[factory]` lines. NOTE the ≥50%-of-baseline
  validation gate is now permanently vacuous for new firms (no generic result to
  compare against) — absolute thresholds (≥10 recs, ≥95% names, ≥60% urls,
  ≥30% descriptions) are the whole gate; if a generated scraper ever ships a
  suspiciously small portfolio, that's the hole it walked through.
- PENDING (next session picks up here):
  0. Supervise the finder's first LIVE discovery run: check the `[find]` lines, confirm
     the queued firm is real and its site genuinely publishes a portfolio, and confirm
     `data/discovered_candidates.json` was committed. If the model's suggestions skew
     junky, tighten `_PROMPT` or raise the bar in `verify()`. No new Railway var is
     required (`ANTHROPIC_API_KEY` is already on discovery).
  1. ~~Finish refresh service settings.~~ **RESOLVED 2026-07-27 (evidence, not a
     dashboard check):** the repo received `Nightly:` commits for **32 firms that have
     a bespoke scraper** — a16z, accel, bessemer, insight, nea, sequoia, norwest and the
     rest. Discovery mode filters bespoke firms out before it starts, so only
     `--mode refresh` can produce those; the service therefore ran a full pass and it
     worked (small sensible deltas, no `held back` lines, no breakage). Config-as-code
     path = `railway.refresh.toml` is LOAD-BEARING (file config overrides dashboard);
     cron `0 8 * * 1` (WEEKLY, Mondays 08:00 UTC). Remaining caveat, unchanged: without
     a cron schedule set Railway runs the start command on EVERY deploy, so any push
     touching `automation/**` can launch an unscheduled ~30-60 min refresh. Harmless,
     but that is why an unexpected run appears after a deploy.
  2. ~~Factory queue drains at `GEN_MAX_PER_RUN=3`/night.~~ **RESOLVED 2026-07-27:**
     wingvc + signalfire exhausted their bursts; the 9 JS-heavy candidates and
     LocalGlobe are retired (terminal/manual). Queue is empty — from here it holds
     only what the finder adds (1/night, portfolio URL guaranteed).
  3. ~~`everywhere_tags` gap: auto-generated datasets ship `[]`.~~ **RESOLVED
     2026-07-27 (user: "the tags are the main value — the dashboard agent builds
     comps from them"):** shared keyword tagger in `automation/tags.py`, applied in
     the pipeline scrape loop (covers weekly refreshes of factory scrapers) and in
     the factory before persist; 7 untagged datasets backfilled in place
     (415/836 companies tagged — matrix 68%, amplify 84%, felicis 65%, foundry 60%,
     homebrew 40%; wingvc 0% and signalfire 8% are STRUCTURAL, no descriptions to
     classify, which is why the factory retired them). Airtable tag counts refresh
     per firm on its next scrape night (Monday refresh for bespoke firms); wingvc +
     signalfire never scrape again, so their Airtable columns stay 0 — but the
     dashboard reads the raw JSON, which now carries every tag that exists. If
     their coverage matters, the options are a Wikidata sector fill (`enrich.py`)
     or a one-off LLM pass (breaks the no-LLM convention; would stick, since both
     datasets are frozen). Tests: `automation/test_tags.py`.
     **Follow-up, same day:** keyword backfill extended to ALL datasets (+276 more
     companies; hand-written scrapers' stragglers). The ~1,900 companies with no
     text signal at all (coatue 322, generalcatalyst 187, ribbit 130…) → user
     chose the one-off LLM pass: `automation/llm_tag_backfill.py` (see the
     taxonomy section for its honesty rules) + `tags.carry_forward` in the
     pipeline so the enrichment survives refreshes. The script must run on the
     Mac (Cowork sandbox cannot reach api.anthropic.com); est. ~$0.2 of the
     $3.94 July headroom. Re-runnable: touches only still-empty tags.
     **Ran 2026-07-28 (name-only): 1,314 of 1,902 tagged, $0.14.** The 568 the
     model didn't recognize → script upgraded to FETCH-FIRST (user decision
     "if the EV tags are missing, I do not need the data"): each remaining
     company's own homepage is fetched ($0, we already hold company_url),
     parked-domain/JS-shell guards, keyword pass on the fetched text free,
     and only the still-unresolved go to Haiku WITH the homepage snippet as
     grounding. Fetched text is classification input + report provenance
     ONLY — never written into `description` (the line matrixpartners
     blurred). Keyword fills are banked to disk before any LLM spend.
     Re-run the same command to finish the job.
  4. ~~Eyeball signalfire.com.~~ **RESOLVED 2026-07-30:** it failed all 4 attempts on
     description coverage and `_retire_fully` deleted the dataset. Permanent unless
     someone hand-writes a scraper.
  5. Laptop `.env` `GITHUB_TOKEN` is ruszinn-minted → cannot write to the
     michaeleverywhere repo (fine-grained PATs are resource-owner-bound; push through
     it fails "denied to ruszinn"). Replace with a michaeleverywhere-created PAT if
     commit-capable local runs are wanted; Railway has the correct token.
  6. Optional cleanup (carried over): retire `backfill_airtable.py` + "Portfolio
     Companies" table; prune stale candidates from `candidates.json`.
  7. Finish the tag backfill: 287 companies still carry `[]` after the keyword pass
     (gradientventures 37, mosaicventures 26, coatue 22, homebrew 22, ribbit 22,
     stormventures 21, nea 17…). 134 of them have no `company_url`, so the
     fetch-first path can't ground them and they go to the model on name alone.
     Run `python3 automation/llm_tag_backfill.py` FROM THE MAC (the Cowork sandbox
     cannot reach api.anthropic.com). Re-runnable; touches only still-empty tags.
- DONE (2026-08-03): **the working copy was 41 commits behind and 44 files dirty** —
  the fetch-first tag backfill had been run locally and never committed, while Railway
  kept committing nightly. Merged with `sync_and_push.sh` (deleted after use): remote
  datasets won every collision, local tags were re-applied on top with
  `tags.carry_forward`, which is precisely what that function exists for. Pushed as
  `a3d2650`. **Watch for this pattern** — carry_forward can only inherit tags it can
  SEE, and uncommitted enrichment is invisible to Railway, so a weekly refresh will
  silently rebuild those records without them. Commit enrichment the day it is made.
  The merge also surfaced a `modify/delete` on signalfire: `git checkout --theirs`
  cannot take a version that no longer exists, so the file survived into the merge
  commit and would have resurrected a deliberately-deleted dataset. Caught before the
  push and removed in `593f0ff`. Any future merge-after-retirement has this same trap.
- DONE (2026-08-03): **pointninecapital rewritten by hand, 25 junk records → 185 clean.**
  The factory scraper called `get_text()` on a row whose name/year/flag/city/country/
  status are SEPARATE elements, gluing them into `15Five2013🇺🇸San FranciscoUSAActive`;
  when the listing gave it nothing it fell back to fetching each COMPANY'S OWN homepage
  for description and sectors, which is where "Download logo pack" came from. It also
  read 1 of 8 pages. The replacement reads `stripped_strings`, identifies fields by what
  they ARE (year pattern, membership in Point Nine's own country/sector/stage filter
  vocabularies) rather than by position, walks `?<hash>_page=N` by picking the next page
  NUMBER (taking the first matching link grabbed the *previous*-page link and stopped the
  walk at 49 records), and never leaves pointnine.com. 100% coverage on every field.
  NOTE the stage label lives in the row, NOT the anchor — worth checking on other
  Finsweet/Webflow sites.
- DONE (2026-08-03): **four new factory gates** in `scraper_guard.validate_output`,
  because every existing gate measured COVERAGE and the pointnine junk was 100% covered:
  (a) name plausibility — flag emoji, a status word welded to the previous field
  (`...USAActive`), or a year with letters both sides; verified not to fire on
  ActiveCampaign / 15Five / 2048 Ventures / Studio 2049;
  (b) self-sourcing — boilerplate like "request a demo" / "accept all cookies" in
  descriptions, the signature of a scraper that wandered onto portfolio companies'
  own sites to clear the ≥30% description bar;
  (c) stub fields — **3 or more** fields empty on every record. The threshold is
  load-bearing: ONE all-empty field is the legitimate N/A case this file already
  describes (sequoia `ticker_symbol`, menlo `sectors`, arch `acquirer`), and failing
  it would retire a firm over the site's editorial choices — which under
  bespoke-or-nothing DELETES the dataset. Measured: every dataset at 3+ is
  factory-generated, no hand-written one reaches it;
  (d) founders plausibility — a vocabulary test, not a structural one, since nothing
  structural separates "Bea Patricia" from "Park Ave".
  Six datasets were cleaned to match (matrixpartners, gradientventures, mosaicventures,
  trueventures, notationcapital, foundrygroup): stub fields dropped, 11 junk founder
  entries removed, 2 trailing-comma names fixed. All now pass.
- DONE (2026-08-03): `test_candidate_finder.py` "seed list still intact" fixed. Its
  `before` set was built from the REAL discovered queue, so it mixed seed-list firms
  with discovered ones (bcapitalgroup); the test then swaps that queue for a fake and
  the discovered firms legitimately vanish. The assertion is about `candidates.json`
  surviving the merge, so the discovered side is now stubbed empty while measuring it.
  A test bug that passed only while the finder had queued nothing — it broke the moment
  the finder started working.
- Docs debt: `automation/PIPELINE.md`/`README.md` still describe the retired Zapier flow
  in places; this section is authoritative where they conflict.
- Sandbox note (Cowork sessions): the sandbox mount can CREATE but not UNLINK files in
  `.git`, so merges strand `*.lock` files (sweep them into `_git_lock_trash/`).
  Commits from the sandbox work; `git pull` merges and pushes run on the Mac terminal
  (`rm -f` the stranded locks first).
- Context: repo stays **public** (dashboard agent reads raw.githubusercontent.com links
  tokenlessly; raw links + private repo are incompatible). The user's manager (Michael)
  owns the repo + a dashboard agent that consumes the raw JSON links.
