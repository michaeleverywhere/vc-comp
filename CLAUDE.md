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
| 14 Peaks Capital | `peaks14_companies.json` | 23 | 14peaks.capital/portfolio — Portfolio flip cards: company name, sector, description, stage, country, year and website. (`peaks14_scraper.py`) |
| Qumra Capital | `qumra_companies.json` | 27 | qumracapital.com/portfolio — Portfolio cards: company name and tagline. (`qumra_scraper.py`) |
| Bailador Technology Investments | `bailador_companies.json` | 18 | bailador.com.au/portfolio — Portfolio tiles: company name, sectors and description. (`bailador_scraper.py`) |
| Tenacious Ventures | `tenacious_companies.json` | 13 | tenacious.ventures/investments — Investments list: company name, theme, description and website. (`tenacious_scraper.py`) |
| Casdin Capital | `casdin_companies.json` | 10 | casdincapital.com — Homepage portfolio cards: company name and description. (`casdin_scraper.py`) |
| Syncona | `syncona_companies.json` | 22 | synconaltd.com/portfolio — Portfolio list: company name, description and stage category (from the company page path). (`syncona_scraper.py`) |
| Hi Ventures (formerly ALLVP) | `hiventures_companies.json` | 50 | hi.vc/portfolio — Portfolio list: company name, year invested and website. (`hiventures_scraper.py`) |
| Activate Capital | `activate_companies.json` | 34 | activatecap.com/portfolio — Portfolio cards: company name, description and website. (`activate_scraper.py`) |
| Acme Capital | `acme_companies.json` | 33 | acme.vc/highlighted-portfolio — Framer portfolio cards: company name, description and website. (`acme_scraper.py`) |
| Finch Capital | `finch_companies.json` | 47 | finchcapital.com/portfolio — Portfolio cards: company name, description, headquarters and website. (`finch_scraper.py`) |
| Valia Ventures | `valia_companies.json` | 45 | valia.vc/portfolioindex — Portfolio index: company name, sectors, description and website. (`valia_scraper.py`) |
| Source Code Capital | `sourcecode_companies.json` | 104 | sourcecodecap.com/companies — Companies page: company name (often Chinese), sector, Chinese description and website. (`sourcecode_scraper.py`) |
| Alpha JWC Ventures | `alphajwc_companies.json` | 14 | alphajwc.com/portfolios — Portfolio cards: company name, description and website. (`alphajwc_scraper.py`) |
| Phoenix Court (LocalGlobe / Latitude / Solar) | `phoenixcourt_companies.json` | 50 | phoenixcourt.vc/companies — Companies table: company name, description, sector, funds (LocalGlobe, Latitude, Solar) and year. (`phoenixcourt_scraper.py`) |
| Porsche Ventures | `porscheventures_companies.json` | 34 | porsche.ventures/portfolio — Portfolio grid: company name (site logo alt), region, status, sectors, short description and website. (`porscheventures_scraper.py`) |
| Bain Capital Crypto | `baincapitalcrypto_companies.json` | 18 | baincapitalcrypto.com/portfolio — Portfolio list: company name, website and exited flag. (`baincapitalcrypto_scraper.py`) |
| Beta Boom | `betaboom_companies.json` | 29 | betaboom.com/portfolio — Webflow companies list: company name, sectors and acquired status. (`betaboom_scraper.py`) |
| Defy Partners | `defy_companies.json` | 78 | defy.vc/companies — Companies list: company name and description. (`defy_scraper.py`) |
| Elefund | `elefund_companies.json` | 24 | elefund.com/portfolio — Portfolio grid: company name (site logo alt). (`elefund_scraper.py`) |
| Ironspring Ventures | `ironspring_companies.json` | 25 | ironspring.com/portfolio-companies — Portfolio grid: company name and one-line description. (`ironspring_scraper.py`) |
| Night Ventures | `nightventures_companies.json` | 15 | nightventures.com — NV1 Fund portfolio list: company name and website. (`nightventures_scraper.py`) |
| Operator Collective | `operatorcollective_companies.json` | 60 | operatorcollective.com/portfolio-companies — Webflow portfolio list: company name, sector and website. (`operatorcollective_scraper.py`) |
| Scribble Ventures | `scribble_companies.json` | 25 | scribble.vc — Wix homepage portfolio: company name and one-line description (* = later-stage investment). (`scribble_scraper.py`) |
| Calm/Storm Ventures | `calmstorm_companies.json` | 90 | calmstorm.vc/portfolio — Webflow portfolio cards: company name and one-line description. (`calmstorm_scraper.py`) |
| NAP | `nap_companies.json` | 34 | nap.vc/build/companies — Companies table: company name, sector, location and website; exited companies flagged. (`nap_scraper.py`) |
| Redstone | `redstone_companies.json` | 96 | redstone.vc/portfolio — Webflow portfolio list: company name, sectors and exited flag. (`redstone_scraper.py`) |
| Voima Ventures | `voima_companies.json` | 52 | voimaventures.com/portfolio — Portfolio grid: company name, fund, sector and description. (`voima_scraper.py`) |
| YZR Capital | `yzr_companies.json` | 12 | yzr-capital.com/portfolio — Elementor portfolio blocks: company name, theme and one-line description. (`yzr_scraper.py`) |
| Practica Capital | `practica_companies.json` | 12 | practica.vc/en/investments — Investments cards: company name, sector and stage. (`practica_scraper.py`) |
| Ysios Capital | `ysios_companies.json` | 38 | ysioscapital.com/our-portfolio — Portfolio list: company name and description. (`ysios_scraper.py`) |
| Asabys Partners | `asabys_companies.json` | 26 | asabys.com/portfolio — Portfolio grid: company names. (`asabys_scraper.py`) |
| Outliers VC | `outliers_companies.json` | 24 | outliers.vc/portfolio — Portfolio accordion: company name, country, theme and website. (`outliers_scraper.py`) |
| Orios Venture Partners | `orios_companies.json` | 30 | oriosvp.com/portfolio1 — Portfolio grid: company names. (`orios_scraper.py`) |
| Ideaspring Capital | `ideaspring_companies.json` | 33 | ideaspringcap.com/portfolio — Portfolio cards: company name, sector and tagline. (`ideaspring_scraper.py`) |
| Luge Capital | `luge_companies.json` | 27 | luge.vc/portfolio — Divi portfolio blocks: company name and tagline. (`luge_scraper.py`) |
| Arboretum Ventures | `arboretum_companies.json` | 43 | arboretumvc.com/portfolio — Portfolio grid: company name and description. (`arboretum_scraper.py`) |
| Seventure Partners | `seventure_companies.json` | 129 | seventure.fr/expertise/?company=498 — Portfolio list (French): company name, description, sectors and country. (`seventure_scraper.py`) |
| Haatch | `haatch_companies.json` | 100 | haatch.com/portfolio — Portfolio cards: company name, year founded, year invested and note (exits flagged). (`haatch_scraper.py`) |
| ACT Venture Capital | `actvc_companies.json` | 53 | actventure.capital/portfolio — Webflow portfolio grid: company names. (`actvc_scraper.py`) |
| Atlantic Bridge | `atlanticbridge_companies.json` | 33 | abven.com/portfolio — Portfolio grid: company name and description. (`atlanticbridge_scraper.py`) |
| Boston Seed Capital | `bostonseed_companies.json` | 36 | bostonseed.com/portfolio — Portfolio details: company name, founders, ticker, description, round invested, expertise and website. (`bostonseed_scraper.py`) |
| Bon Angels Venture Partners | `bonangels_companies.json` | 20 | bonangels.net/portfolio — Wix portfolio list (Korean): company name, Korean description and website. (`bonangels_scraper.py`) |
| Decasonic | `decasonic_companies.json` | 20 | decasonic.com/companies — Companies list: company name and sector. (`decasonic_scraper.py`) |
| MizMaa Ventures | `mizmaa_companies.json` | 26 | mizmaa.com/portfolio — Portfolio cards: company name, tagline, sector and exited flag. (`mizmaa_scraper.py`) |
| Senovo | `senovo_companies.json` | 41 | senovo.vc/portfolio — Portfolio grid: company name, tagline, year, locations, founders and website. (`senovo_scraper.py`) |
| Two Bear Capital | `twobear_companies.json` | 22 | twobearcapital.com/portfolio — Portfolio cards: company name and description. (`twobear_scraper.py`) |
| Vorwerk Ventures | `vorwerk_companies.json` | 60 | vorwerkventures.com — Elementor flip-box portfolio: company name, tagline and website. (`vorwerk_scraper.py`) |
| Newfund | `newfund_companies.json` | 117 | newfundcap.com/portfolio/1 — Portfolio cards: company name and tagline. (`newfund_scraper.py`) |
| Builders VC | `buildersvc_companies.json` | 11 | builders.vc/companies.html — Companies slider: company name, sector, stage and description. (`buildersvc_scraper.py`) |
| Highland Europe | `highlandeurope_companies.json` | 12 | highlandeurope.com/companies — Companies page: company name, tagline, description, website and exited flag. (`highlandeurope_scraper.py`) |
| Jackson Square Ventures | `jsv_companies.json` | 56 | jsv.com/portfolio — Portfolio grid: company name (site logo alt), one-line description and website. (`jsv_scraper.py`) |
| Shine Capital | `shinecapital_companies.json` | 52 | shine.vc/portfolio — Portfolio logo grid: company name (site logo alt), website and exited flag. (`shinecapital_scraper.py`) |
| Dalus Capital | `dalus_companies.json` | 24 | daluscapital.com/portfolio — Wix portfolio gallery: company name (site logo alt). (`dalus_scraper.py`) |
| Lightbox Ventures | `lightboxvc_companies.json` | 20 | lightbox.vc/investments — Investments grid: company name (site logo alt). (`lightboxvc_scraper.py`) |
| Coral Capital | `coralcapital_companies.json` | 97 | coralcap.co/portfolio — Portfolio logo grid: company name (site logo alt, some in Japanese) and website. (`coralcapital_scraper.py`) |
| Incubate Fund | `incubatefund_companies.json` | 19 | incubatefund.com/portfolio — Portfolio logo list: company name (site logo alt, mostly Japanese). (`incubatefund_scraper.py`) |
| GD1 | `gd1_companies.json` | 41 | gd1.vc/portfolio — Portfolio grid: company name (site logo alt). (`gd1_scraper.py`) |
| Launch Capital | `launchcapital_companies.json` | 160 | launchcapital.com/companies — Squarespace logo gallery: company name (site logo alt) and website. (`launchcapital_scraper.py`) |
| Acrew Capital | `acrew_companies.json` | 88 | acrewcapital.com/companies-archive — Webflow companies list: company name (site logo alt), website. (`acrew_scraper.py`) |
| Alliance Venture | `allianceventure_companies.json` | 62 | alliance.vc/portfolio — Portfolio logo grid: company name (site logo alt), website and exited flag. (`allianceventure_scraper.py`) |
| Glynn Capital | `glynn_companies.json` | 97 | glynncapital.com/companies — Squarespace logo gallery: company name (site logo alt) and website. (`glynn_scraper.py`) |
| Lumia Capital | `lumia_companies.json` | 29 | lumiacapital.com/companies — Portfolio grid: company name (site logo alt). (`lumia_scraper.py`) |
| Forge VC | `forgevc_companies.json` | 16 | forge.vc/portfolio — Webflow portfolio grid: company name (site logo alt). (`forgevc_scraper.py`) |
| Calibrate Ventures | `calibrate_companies.json` | 28 | calibratevc.com/portfolio — Portfolio logo grid: company name (site logo alt) and website. (`calibrate_scraper.py`) |
| Boehringer Ingelheim Venture Fund | `bivf_companies.json` | 50 | boehringer-ingelheim-venture.com/portfolio — Portfolio cards: company names. (`bivf_scraper.py`) |
| imec.xpand | `imecxpand_companies.json` | 31 | imecxpand.com/en/portfolio — Portfolio cards: company name and one-line description. (`imecxpand_scraper.py`) |
| Keen Venture Partners | `keen_companies.json` | 40 | keenventurepartners.com/portfolio — Portfolio cards: company name, description, investment round, year established and website. (`keen_scraper.py`) |
| Qbic | `qbic_companies.json` | 21 | qbic.be/portfolio — Portfolio list: company name, fund, sector and description. (`qbic_scraper.py`) |
| Brightstone Venture Capital | `brightstone_companies.json` | 20 | brightstonevc.com — Portfolio grid: company names. (`brightstone_scraper.py`) |
| Cultivian Sandbox Ventures | `cultivian_companies.json` | 20 | cultiviansbx.com/portfolio — Squarespace portfolio summary: company name and description. (`cultivian_scraper.py`) |
| Ripple Ventures | `ripple_companies.json` | 49 | rippleventures.com — Portfolio list: company name and website. (`ripple_scraper.py`) |
| Vibe Capital | `vibecapital_companies.json` | 50 | vibe.vc/portfolio — Notion portfolio gallery: company name, sector, region and website. (`vibecapital_scraper.py`) |
| Linear Capital | `linearcapital_companies.json` | 72 | linear.vc/portfolio — Portfolio cards: company name, tagline, description, year and website. (`linearcapital_scraper.py`) |
| Emerald Technology Ventures | `emerald_companies.json` | 49 | emerald.vc/portfolio — Portfolio cards: company name, tagline and exited flag. (`emerald_scraper.py`) |
| Bee Partners | `beepartners_companies.json` | 95 | beepartners.vc/portfolio — Portfolio grid: company name and one-line description. (`beepartners_scraper.py`) |
| SET Ventures | `setventures_companies.json` | 35 | setventures.com/portfolio — Portfolio list: company name (site logo alt), sector and country. (`setventures_scraper.py`) |
| Chemistry | `chemistry_companies.json` | 34 | chemistry.vc/portfolio — Webflow portfolio list: company name (site logo alt), one-line description, website and pre-Chemistry flag. (`chemistry_scraper.py`) |
| Atlanta Ventures | `atlantaventures_companies.json` | 40 | atlantaventures.com/companies — Company cards: company name, sector, exit note, description and website. (`atlantaventures_scraper.py`) |
| Catapult Ventures | `catapult_companies.json` | 29 | catapult.vc/portfolio — Portfolio modals: company name and one-line description. (`catapult_scraper.py`) |
| Seven Stars | `sevenstars_companies.json` | 12 | sevenstars.vc — Homepage companies grid: company name, one-line description and website. (`sevenstars_scraper.py`) |
| Dynamo Ventures | `dynamo_companies.json` | 19 | dynamo.vc/startup-investment-portfolio — Portfolio cards: company name (site logo alt), description, stage and website. (`dynamo_scraper.py`) |
| ONEVC | `onevc_companies.json` | 39 | onevc.vc/companies/aro — Portfolio logo grid: company name (site logo alt) and exit flag. (`onevc_scraper.py`) |
| Archetype | `archetype_companies.json` | 65 | archetype.fund/portfolio — Webflow portfolio list: company name, website and acquisition note. (`archetype_scraper.py`) |
| Collab+Currency | `collabcurrency_companies.json` | 136 | collabcurrency.com/portfolio — Portfolio list: company name, status, sector and website. (`collabcurrency_scraper.py`) |
| Eos Venture Partners | `eos_companies.json` | 22 | eosvc.com/portfolio — Portfolio gallery: company names. (`eos_scraper.py`) |
| FinTLV Ventures | `fintlv_companies.json` | 23 | fintlv.com/portfolio — Elementor portfolio grid: company names. (`fintlv_scraper.py`) |
| Hypersphere | `hypersphere_companies.json` | 19 | hypersphere.capital/portfolio — Investment cards: company name, round, date invested and website. (`hypersphere_scraper.py`) |
| Love Ventures | `loveventures_companies.json` | 29 | loveventures.co.uk/portfolio — Portfolio cards: company name, sector and one-line description. (`loveventures_scraper.py`) |
| Twin Path Ventures | `twinpath_companies.json` | 38 | twinpath.vc/portfolio — Framer portfolio list: company name and website. (`twinpath_scraper.py`) |
| Altara Ventures | `altara_companies.json` | 17 | altaraventures.com/portfolio — Portfolio list: company name, sector, stage, country and description. (`altara_scraper.py`) |
| Atinum Investment | `atinum_companies.json` | 262 | atinuminvest.co.kr/portfolio-type — Portfolio modals (Korean): company name, sector, website and Korean description. (`atinum_scraper.py`) |
| Blue Wire Capital | `bluewire_companies.json` | 43 | bluewirecapital.com/portfolio — Portfolio list: company name, one-line description and status. (`bluewire_scraper.py`) |
| First Cheque | `firstcheque_companies.json` | 131 | firstcheque.vc/portfolio — Webflow portfolio list: company name and website. (`firstcheque_scraper.py`) |
| Lok Capital | `lokcapital_companies.json` | 43 | lokcapital.com/portfolio — Webflow portfolio blocks: company name, sector, fund and status. (`lokcapital_scraper.py`) |
| Mandiri Capital Indonesia | `mandiri_companies.json` | 19 | mandiri-capital.co.id/portfolio — Portfolio list: company name, website, sector, description (Indonesian), city and year. (`mandiri_scraper.py`) |
| Rainmatter | `rainmatter_companies.json` | 39 | rainmatter.com/portfolio — Portfolio cards: company name, one-line description and website. (`rainmatter_scraper.py`) |
| Yellowdog | `yellowdog_companies.json` | 35 | yellowdog.kr/portfolios — Portfolio grid: company name (English with Korean in parentheses). (`yellowdog_scraper.py`) |
| SaaSholic | `saasholic_companies.json` | 29 | saasholic.com/companies — Portfolio modals: company name, tagline, description and website. (`saasholic_scraper.py`) |
| Ankur Capital | `ankur_companies.json` | 36 | ankurcapital.com/portfolio — Portfolio blocks: company name (site logo alt) and website. (`ankur_scraper.py`) |
| TruStage Ventures (formerly CMFG Ventures) | `trustageventures_companies.json` | 16 | trustage.com/ventures/portfolio — Portfolio logo table: company name (site logo alt) and website. (`trustageventures_scraper.py`) |
| Heartfelt | `heartfelt_companies.json` | 159 | heartfelt.vc/portfolio — portfolio list (`li.min-w-0`): company name, sector tag, one-line description and website. (`heartfelt_scraper.py`) |
| BAM Ventures | `bamventures_companies.json` | 102 | bam.vc/companies — Webflow CMS company grid (`div.work-sample`): company name, category and website. (`bamventures_scraper.py`) |
| Green Egg Ventures | `greenegg_companies.json` | 44 | greenegg.vc — homepage portfolio flip cards (`div.port-card`): company name, description and website. (`greenegg_scraper.py`) |
| SHAKTI | `shakti_companies.json` | 46 | shaktivc.com/companies — portfolio table (`tr.hover-color`): company name, description, sector, year and stage of investment, SHAKTI fund and detail page. (`shakti_scraper.py`) |
| Unruly Capital | `unrulycapital_companies.json` | 57 | unrulycap.com — homepage deal log (`div.deal`): company name, investment amount, date, one-line description, sectors, country and fund. (`unrulycapital_scraper.py`) |
| Virtue | `virtuevc_companies.json` | 25 | virtuevc.com/portfolio — Webflow CMS portfolio cards: company name, subheading (what the company does) and website. (`virtuevc_scraper.py`) |
| Propeller | `propellervc_companies.json` | 22 | propellervc.com/portfolio — HubSpot portfolio rows (`.propeller-list-row`): company name, description, sector/stage tags and profile page. (`propellervc_scraper.py`) |
| Reign Ventures | `reignvc_companies.json` | 13 | reignvc.com/our-portfolio — portfolio cards (`li.w-64`): company name (logo alt), founder names and profile page. (`reignvc_scraper.py`) |
| Brainstorm Ventures | `brainstormvc_companies.json` | 65 | brainstorm.vc/portfolio — portfolio grid (`div.brve-filter-item`): company name, one-line description, fund (from the filter class) and website. (`brainstormvc_scraper.py`) |
| WaterBridge Ventures | `waterbridge_companies.json` | 25 | waterbridge.vc/portfolio — portfolio cards (`.port-card`): company name (logo alt), founders, stage journey, year, description, exit status and case-study page. (`waterbridge_scraper.py`) |
| Dundee Venture Capital | `dundeevc_companies.json` | 39 | dundeeventurecapital.com/portfolio — Squarespace accordion (`li.accordion-item`): company name, acquisition note, one-line description, website, founder and location. (`dundeevc_scraper.py`) |
| Vertical Venture Partners | `verticalvp_companies.json` | 31 | vvp.vc/portfolio — portfolio list (`div.faq-item`): company name, sector label and description. (`verticalvp_scraper.py`) |
| Marathon Venture Capital | `marathonvc_companies.json` | 24 | marathon.vc/portfolio — portfolio cells (`.company-cell`): company name, description, year and profile page. (`marathonvc_scraper.py`) |
| Stride VC | `stridevc_companies.json` | 20 | stride.vc — homepage portfolio logo wall: company name (site-authored logo alt text) and website where linked. (`stridevc_scraper.py`) |
| Adapt Ventures | `adaptvc_companies.json` | 63 | adaptvc.com/companies — Framer portfolio cards: company name, one-line description, HQ, stage invested, current stage. (`adaptvc_scraper.py`) |
| Plum Alley | `plumalley_companies.json` | 29 | plumalley.co/spv-portfolio — Webflow CMS SPV portfolio list: company name and description. (`plumalley_scraper.py`) |
| Elysium Venture Capital | `elysiumvc_companies.json` | 19 | elysium.vc — Tilda portfolio cards (`.t774__content`): company name and description. (`elysiumvc_scraper.py`) |
| Chamaeleon | `chamaeleon_companies.json` | 58 | chamaeleon.vc/portfolio — Next.js portfolio page: current company boxes (name from logo alt, status line such as 'Sold Sensor Tower') and the 'prior investments' logo wall (site-authored logo alt text). (`chamaeleon_scraper.py`) |
| Duro Ventures | `duroventures_companies.json` | 88 | duro.vc — single-page portfolio list: company name, website and sector heading (Enterprise / Consumer / Commerce / Health / Education ...). (`duroventures_scraper.py`) |
| Demea Invest (formerly Demeter) | `demea_companies.json` | 169 | demea-si.com/fr/portfolio — portfolio cards (`a.portfolio-card`, including the hidden past holdings): company name, sector and profile page. (`demea_scraper.py`) |
| Bertha Capital | `berthacapital_companies.json` | 37 | berthacapital.com.br/portfolio-1 — Elementor call-to-action cards: company name, sector and website. (`berthacapital_scraper.py`) |
| 359 Capital | `capital359_companies.json` | 34 | 359capital.com — homepage Webflow portfolio logo list: company name (site-authored logo alt), category, status (e.g. acquired) and website. (`capital359_scraper.py`) |
| IOSG Ventures | `iosg_companies.json` | 193 | iosg.vc — homepage Webflow portfolio list (`div.portfolio-wrap`): project name. (`iosg_scraper.py`) |
| All In Capital | `allincapital_companies.json` | 22 | allincapital.vc/portfolio — portfolio cards with popups: company name, sectors, notes and website; plus the 'Past Portfolio Companies' names. (`allincapital_scraper.py`) |
| Trihill Capital | `trihill_companies.json` | 25 | trihillcapital.com/portfolio — Elementor portfolio cards: company name, sector tags, description and profile page. (`trihill_scraper.py`) |
| CDP Venture Capital | `cdpvc_companies.json` | 155 | cdpventurecapital.it/it/portfolio.page — portfolio flip cards (`div.blocks-portfolio__card`): company name (front), sector and website. Investee funds (fund-of-funds positions such as 'United Ventures III', 'Sofinnova Capital XI', 'Programma 103') are skipped. (`cdpvc_scraper.py`) |
| Axon Partners Group | `axonpartners_companies.json` | 70 | axonpartnersgroup.com/portfolio — portfolio company grid (`div.blog-post`): company name, one-line description and website. (`axonpartners_scraper.py`) |
| Abac Nest | `abacnest_companies.json` | 36 | abacnest.abaccapital.com/es — homepage portfolio tiles (Spanish): company name, description, exit marker ('Desinvertida') and website. (`abacnest_scraper.py`) |
| SpeedUp Venture Capital Group | `speedupvc_companies.json` | 40 | speedupgroup.com — homepage portfolio grid (Polish): company name, one-line description and website. (`speedupvc_scraper.py`) |
| WI Harper Group | `wiharper_companies.json` | 16 | wiharper.com/our-companies/?sector=deeptech — portfolio logo grid: company name (site-authored logo alt), website and 'Exited' marker. (`wiharper_scraper.py`) |
| Avaana Capital | `avaana_companies.json` | 21 | avaanacapital.com — homepage portfolio slider: company name (site-authored logo alt), one-line description and profile page. (`avaana_scraper.py`) |
| Puzzle Ventures | `puzzleventures_companies.json` | 19 | puzzle.ventures/portfolio — portfolio list: project name, sector and one-line description, website. (`puzzleventures_scraper.py`) |
| Aglaé Ventures | `aglae_companies.json` | 85 | aglaeventures.com/companies — companies logo wall (`div.companies a`): company name (site-authored title / aria-label) and website. (`aglae_scraper.py`) |
| 2045 Ventures | `v2045vc_companies.json` | 16 | 2045vc.com/2045-portfolio-investments — Wix portfolio columns: company name, category headline, description and website. (`v2045vc_scraper.py`) |
| Stout Street Capital | `stoutstreet_companies.json` | 58 | stoutstreetcapital.com — homepage 'portfolio, by fund' lists (`div.pf-group`): company name, website, Stout Street fund and current/past heading. (`stoutstreet_scraper.py`) |
| MATH Venture Partners | `mathvp_companies.json` | 70 | mathventurepartners.com/portfolio — portfolio cards (`li.pf-card`): company name (site-authored logo alt), founder, description, MATH fund and active/exited section. (`mathvp_scraper.py`) |
| Firebolt Ventures | `firebolt_companies.json` | 24 | fireboltventures.com — homepage 'IPOs and Acquisitions' outcome cards: company name, outcome (acquirer / IPO), description, headline value and date. (`firebolt_scraper.py`) |
| Team Builder Ventures | `teambuilder_companies.json` | 16 | teambuilderventures.com — homepage 'Companies' logo wall: company name (site-authored logo alt text); the co-investor wall after it is ignored. (`teambuilder_scraper.py`) |
| UTEC (University of Tokyo Edge Capital Partners) | `utecvc_companies.json` | 106 | ut-ec.co.jp/english/our_companies — 'Our Companies' list (`li.box_link`): company name, profile link, sector category, UTEC fund and exit status. Entries categorised 'fund' (fund LP commitments) are excluded. (`utecvc_scraper.py`) |
| Scrum Ventures | `scrumvc_companies.json` | 119 | scrum.vc/investment — portfolio grid (`li.portfolio-item`) under Featured / IPO / M&A / Portfolio headings: company name (site-authored logo alt) and profile link; IPO and M&A sections are marked exited. (`scrumvc_scraper.py`) |
| G20 Ventures | `g20vc_companies.json` | 17 | g20vc.com/portfolio — portfolio page 'Here's who we're behind so far': company name (h3), opening description paragraph and website ('Learn more' link). (`g20vc_scraper.py`) |
| BlueTree Venture Fund | `bluetreevc_companies.json` | 60 | bluetreevc.com/portfolio — portfolio page: current BTVC Fund I logo wall (site-authored logo alt, website, acquisition note) plus the 'From earlier BlueTree funds' ticker (`span.ticker-item`, exited flag). (`bluetreevc_scraper.py`) |
| MissionOG | `missionog_companies.json` | 37 | missionog.com/partner-companies — partner companies page: company name (h2), description and website. (`missionog_scraper.py`) |
| Alpaca VC | `alpacavc_companies.json` | 32 | alpaca.vc/portfolio — portfolio page: company name (site-authored link aria-label 'Open X website' / logo alt), website and thesis section (Energy Abundance, Foundational Industries, ..., Notable Exits). (`alpacavc_scraper.py`) |
| Vertex Ventures Israel | `vertexisrael_companies.json` | 97 | vertexventures.co.il/portfolio — portfolio carousel cards (`div[class*=projectWrapper]`): company name (site-authored logo alt), screen- reader description and Exited / Recent badge. 'Stealth' entries are skipped. (`vertexisrael_scraper.py`) |
| Thin Air Labs | `thinairlabs_companies.json` | 35 | thinairlabs.ca — homepage portfolio logo wall: company name (site-authored logo alt) and website. (`thinairlabs_scraper.py`) |
| NTT Docomo Ventures | `nttdocomov_companies.json` | 173 | nttdocomo-v.com/en/portfolio — English portfolio list (`section.pList li`): company name (site-authored logo alt), profile link, region, categories, investment year and exit flag. (`nttdocomov_scraper.py`) |
| CoVentures | `coventures_companies.json` | 16 | coventures.vc/founders-we-work-for — 'founders we work for' cards (`div.founder-card`): company name (site-authored 'Try X' link text), tagline, founders line, website and status (Closed / Pivot / Acquired). (`coventures_scraper.py`) |
| Detroit Venture Partners | `detroitvp_companies.json` | 21 | detroit.vc — homepage 'portfolio' gallery: company name (site-authored logo alt, with 'logo' / 'tile' / 'wordmark' stripped) and website. Tiles without alt text are skipped; the 'our mission' affiliate gallery is ignored. (`detroitvp_scraper.py`) |
| Artis Ventures | `artisvc_companies.json` | 57 | av.co/portfolio — 'Our Companies' cards (`a.portfolio-item`): company name, one-line description, founder(s), status tag and profile link. (`artisvc_scraper.py`) |
| Omega Funds | `omegafunds_companies.json` | 147 | omegafunds.com/companies — companies grid (`article.product-listed`): company name, description and website. (`omegafunds_scraper.py`) |
| Grit Capital Partners | `gritvc_companies.json` | 32 | grit.vc/portfolio — portfolio popups: company name (h2), category, website ('see the website'), 'About' description, year since and exited flag. (`gritvc_scraper.py`) |
| Apple Tree Partners | `appletree_companies.json` | 30 | appletreepartners.com/portfolio — portfolio items (`#column-right .item`): company name (site-authored logo alt, 'Logo' stripped) and website. (`appletree_scraper.py`) |
| Shadow Ventures | `shadowvc_companies.json` | 31 | shadow.vc/investments — investments grid (`div.collection-item-6`): company name (site-authored logo alt), category, profile link and exit flag. (`shadowvc_scraper.py`) |
| Selva Ventures | `selvavc_companies.json` | 19 | selvaventures.com/portfolio — portfolio grid: company name, one-line description and website (Framer cards). (`selvavc_scraper.py`) |
| Preston-Werner Ventures | `pwv_companies.json` | 37 | pwv.com/showcase/companies — showcase companies: company name and website (header link of each company card). (`pwv_scraper.py`) |
| August Capital | `augustcap_companies.json` | 135 | augustcap.com/portfolio/active-funds — portfolio tooltips: company name (bold label, '(acquired by X)' split into exit note), description, industry sector, headquarters and lead investment professional. (`augustcap_scraper.py`) |
| ZAKA VC | `zakavc_companies.json` | 75 | zaka.vc/portfolio — portfolio cards (`a.card--portfolio`): company name (h3), one-line description, location and website. (`zakavc_scraper.py`) |
| aMoon Fund | `amoon_companies.json` | 48 | amoon.fund — homepage portfolio grid (`div.item`): company name (site-authored logo alt / link title), profile link and listing note (e.g. ticker). (`amoon_scraper.py`) |
| 25madison | `madison25_companies.json` | 36 | 25madison.com/portfolio — portfolio blocks (`a.investments-blocks`): company name (h5), one-line description and website. (`madison25_scraper.py`) |
| TheVentures | `theventures_companies.json` | 209 | theventures.vc/companies — companies table: company name, sector, country and website (one row link per company). (`theventures_scraper.py`) |
| Taurus Ventures | `taurusvc_companies.json` | 49 | taurus.vc/portfolio — portfolio logo wall: company name (site- authored logo alt) and website. (`taurusvc_scraper.py`) |
| LoftyInc Capital | `loftyinc_companies.json` | 108 | loftyinc.vc/portfolio — portfolio gallery captions: company name (h2), industry, country, status, investment year and website. (`loftyinc_scraper.py`) |
| MGV | `mgvvc_companies.json` | 66 | mgv.vc/portfolio — portfolio cards: company name (h2), one-line description and website. (`mgvvc_scraper.py`) |
| Chengwei Capital | `chengwei_companies.json` | 49 | chengwei.com — homepage portfolio wall: company name (site- authored logo alt; hover-state ' w' duplicates collapsed) and website. (`chengwei_scraper.py`) |
| FGV Capital | `fgvcap_companies.json` | 40 | fgv.vc/portfolio — portfolio table: company name (h5), one-line description, sector and location. (`fgvcap_scraper.py`) |
| Akkadian Ventures | `akkadian_companies.json` | 42 | akkadian.vc/portfolio — portfolio cards: company name (h3), one-line description, status (e.g. IPO / Acquired) and website. (`akkadian_scraper.py`) |
| NightDragon | `nightdragon_companies.json` | 18 | nightdragon.com/portfolio — portfolio grid: company name (h4), current / exited status and description. (`nightdragon_scraper.py`) |
| Twine Ventures | `twinevc_companies.json` | 32 | twineventures.com — homepage portfolio list: company name (h3), one-line description, sector and website. (`twinevc_scraper.py`) |
| Betatron Venture Group | `betatron_companies.json` | 12 | betatron.co/portfolio — portfolio accordion: company name (h4) and description, plus website where linked. (`betatron_scraper.py`) |
| KOMPAS VC | `kompasvc_companies.json` | 28 | kompas.vc/portfolio — portfolio cards: company name (site-authored logo alt), sector, exited flag, description and profile link. (`kompasvc_scraper.py`) |
| Switch Ventures | `switchvc_companies.json` | 20 | switch.vc/companies — companies grid: company name (h4) and one-line description. (`switchvc_scraper.py`) |
| Supermoon Capital | `supermoon_companies.json` | 24 | supermooncapital.com/portfolio — portfolio cards: company name (site-authored logo alt), sector, one-line description and website ('Visit Site'). (`supermoon_scraper.py`) |
| Cadenza Ventures | `cadenzavc_companies.json` | 25 | cadenza.vc/portfolio — portfolio logo wall: company name (site-authored logo alt) and website. (`cadenzavc_scraper.py`) |
| Vocap Partners | `vocap_companies.json` | 13 | vocap.vc/portfolio — portfolio (Current Companies / Select Exits): company name (site-authored logo alt), category and website. (`vocap_scraper.py`) |
| Alix Ventures | `alixvc_companies.json` | 17 | alix.vc/portfolio-1 — 'Current Investments' list: company name (heading) and description; 'Stealth' placeholders skipped. (`alixvc_scraper.py`) |
| Capria Ventures | `capriavc_companies.json` | 18 | capria.vc/entire-portfolio — entire-portfolio cards: company name, one-line description, sector, region, country, investing partner and round. (`capriavc_scraper.py`) |
| Jump Crypto | `jumpcrypto_companies.json` | 19 | jumpcrypto.com/invest — investments grid: project name (h2), one-line description and website. (`jumpcrypto_scraper.py`) |
| First Star Ventures | `firststarvc_companies.json` | 34 | firststar.vc/companies — companies list: company name, one-line description, website and 'acquired' tag (shown only when set). (`firststarvc_scraper.py`) |
| Ibex Investors | `ibexinv_companies.json` | 63 | ibexinvestors.com/private-portfolio — private (venture) portfolio logo wall: company name (site-authored logo alt). (`ibexinv_scraper.py`) |
| Social Leverage | `socialleverage_companies.json` | 17 | socialleverage.com/portfolio — portfolio logo wall: company name (site-authored logo alt). (`socialleverage_scraper.py`) |
| Socii Capital | `sociicap_companies.json` | 17 | sociicapital.com — homepage portfolio grid: company name (h3), status label (e.g. IPO / Acquired). (`sociicap_scraper.py`) |
| Kayyak Ventures | `kayyak_companies.json` | 29 | kayyakventures.com — homepage portfolio blocks: company name (h3) and the founder quote shown under it. (`kayyak_scraper.py`) |
| Meridian Ventures | `meridianvc_companies.json` | 22 | meridianvc.com/portfolio — portfolio logo wall: company name (site-authored logo alt; 'Stealth' placeholders skipped) and website. (`meridianvc_scraper.py`) |
| Silas Capital | `silascap_companies.json` | 36 | silascapital.com/portfolio — portfolio brand tiles (Growth / Venture Investments): brand name (site-authored alt) and website. (`silascap_scraper.py`) |
| Utopian Ventures | `utopianvc_companies.json` | 99 | utopian.vc/portfolio — portfolio table: company name, status flag (IPO / listed / acquired), description, entry stage and year, website. (`utopianvc_scraper.py`) |
| Modus Capital | `modusvc_companies.json` | 14 | modus.vc/portfolio — portfolio cards: company name, sector, fund, country, description and website. (`modusvc_scraper.py`) |
| PJC | `pjcvc_companies.json` | 52 | pjc.vc — homepage portfolio blocks (AI / Consumer / Enterprise): company name, one-line description, website and exit note (website omitted for exited companies, whose link points at the acquirer). (`pjcvc_scraper.py`) |
| Headwater Ventures | `headwatervc_companies.json` | 40 | headwater.vc — homepage portfolio grid: company name (link text) and website. (`headwatervc_scraper.py`) |
| Rarebreed Ventures | `rarebreedvc_companies.json` | 42 | rarebreed.vc/companies — companies page: company name (h2 link text) and website. (`rarebreedvc_scraper.py`) |
| Ankona Capital | `ankona_companies.json` | 19 | ankona.com — homepage portfolio: company name (site-authored logo alt), category / one-line description and website. (`ankona_scraper.py`) |
| Northstar Ventures | `northstarvc_companies.json` | 30 | northstar.vc/portfolio — portfolio logo wall: company name (site-authored logo alt). (`northstarvc_scraper.py`) |
| Expeditions Fund | `expeditionsfund_companies.json` | 39 | expeditionsfund.com/portfolio — portfolio grid: company name, website and 'Acquired' label (shown only when set). (`expeditionsfund_scraper.py`) |
| Gotham Ventures | `gothamvc_companies.json` | 34 | gothamvc.com/portfolio — portfolio list: company name (h2) and profile link. (`gothamvc_scraper.py`) |
| CyberAgent Capital | `cyberagentcap_companies.json` | 12 | cyberagentcapital.com/portfolio — portfolio page: company name (site-authored logo alt; Japanese legal names as written). (`cyberagentcap_scraper.py`) |
| Begin Capital | `begincap_companies.json` | 34 | begin.capital/portfolio — portfolio list: company name (link text), website and fund 'season'. (`begincap_scraper.py`) |
| Naver D2SF | `naverd2sf_companies.json` | 87 | naverd2sf.com/ko — homepage portfolio carousel: company name (site- authored logo alt, Korean as written) and profile link. (`naverd2sf_scraper.py`) |
| Equinor Ventures | `equinorvc_companies.json` | 49 | equinor.com/energy/equinor-ventures-portfolio — portfolio accordions: company name (h3) grouped by theme; fund-of-fund commitments (AP Ventures, Counteract, Energize, Volta) excluded. (`equinorvc_scraper.py`) |
| MongoDB Ventures | `mongodbvc_companies.json` | 19 | mongodb.com/company/ventures — 'Portfolio Companies' logo wall: company name (site-authored 'X logo' alt). (`mongodbvc_scraper.py`) |
| Lightbank | `lightbank_companies.json` | 139 | lightbank.com/companies — 'Our Companies' list: company name (one paragraph per company in the site's text block; links where present). (`lightbank_scraper.py`) |
| SemperVirens | `sempervirens_companies.json` | 73 | sempervirensvc.com/portfolio — portfolio grid: company name (site-authored logo alt) and website. (`sempervirens_scraper.py`) |
| iSelect Fund | `iselectfund_companies.json` | 68 | iselectfund.com/portfolio-companies — portfolio table: company name (link text), website, year established, location and prior funding round. (`iselectfund_scraper.py`) |
| Droia Ventures | `droiavc_companies.json` | 25 | droiaventures.com — homepage portfolio gallery: company name (site- authored image alt), description caption and website. (`droiavc_scraper.py`) |
| Earthshot Ventures | `earthshotvc_companies.json` | 28 | earthshot.vc/companies — companies table: company name, sector and website (featured cards add a one-line description). (`earthshotvc_scraper.py`) |
| AENU | `aenu_companies.json` | 41 | aenu.com/portfolio — portfolio gallery: company name and profile slug from the page's own company list (also shown as image alts). (`aenu_scraper.py`) |
| Xontogeny | `xontogeny_companies.json` | 27 | xontogeny.com/portfolio — portfolio logo grid: company name (site-authored logo alt) and website ('Visit Site'). (`xontogeny_scraper.py`) |
| Seroba | `seroba_companies.json` | 22 | serobavc.com/portfolio — portfolio list: company name (site-authored link title), description and website. (`seroba_scraper.py`) |
| Generator Ventures | `generatorvc_companies.json` | 14 | generatorvc.com/portfolio — portfolio blocks: company name (h2, '- exited' suffix -> status), description and website. (`generatorvc_scraper.py`) |
| Cultivate Next | `cultivatenext_companies.json` | 17 | cultivatenext.vc/portfolio.html — portfolio cards: company name (h2), one-line description and website. (`cultivatenext_scraper.py`) |
| Martin Ventures | `martinvc_companies.json` | 26 | martinventures.com/portfolio — portfolio (Active Portfolio / Exits): company name (link text) and website. (`martinvc_scraper.py`) |
| Sound Bioventures | `soundbio_companies.json` | 12 | soundbioventures.com/portfolio — portfolio list: company name (entry title) and profile link. (`soundbio_scraper.py`) |
| Blue Venture Fund | `blueventurefund_companies.json` | 60 | blueventurefund.com/portfolio — portfolio logo wall: company name (site-authored logo alt; news-card images skipped). (`blueventurefund_scraper.py`) |
| Acre Venture Partners | `acrevp_companies.json` | 28 | acre.vc — homepage investments: company name (site-authored logo alt), one-line description and website. (`acrevp_scraper.py`) |
| WEH Ventures | `wehvc_companies.json` | 24 | wehventures.com — homepage portfolio wall: company name (site- authored logo alt). (`wehvc_scraper.py`) |
| Taiwania Capital | `taiwaniacap_companies.json` | 100 | taiwaniacapital.com/en/portfolios/category — portfolio table: company name, one-line description and sector. (`taiwaniacap_scraper.py`) |
| Eximius Ventures | `eximiusvc_companies.json` | 32 | eximiusvc.com/portfolio-all — portfolio grid: company name (heading) and one- line description. (`eximiusvc_scraper.py`) |
| Service Provider Capital | `serviceprovidercap_companies.json` | 95 | serviceprovidercapital.com/portfolio — portfolio buttons: company name (button label) and website. (`serviceprovidercap_scraper.py`) |
| PsyMed Ventures | `psymed_companies.json` | 20 | psymed.ventures — homepage portfolio: company name (link text), one- line description and website. (`psymed_scraper.py`) |
| Big Sur Ventures | `bigsurventures_companies.json` | 57 | bigsurventures.vc/portfolio — portfolio grid: company name and category. (`bigsurventures_scraper.py`) |
| Flyer One Ventures | `flyerone_companies.json` | 58 | flyerone.vc/portfolio — portfolio table: company name, industry, description, model and website. (`flyerone_scraper.py`) |
| Skyland Ventures | `skylandvc_companies.json` | 51 | skyland.vc/companies — portfolio wall: company name (site-authored logo alt) and website. (`skylandvc_scraper.py`) |
| Radian Capital | `radiancapital_companies.json` | 34 | radiancapital.com/companies — company pop-ups: name, status, theme and description. (`radiancapital_scraper.py`) |
| Robin Hood Ventures | `robinhoodvc_companies.json` | 35 | robinhoodventures.com/portfolio — portfolio wall: company name (site-authored logo alt) and website. (`robinhoodvc_scraper.py`) |
| Telstra Ventures | `telstraventures_companies.json` | 38 | ti.vc/portfolio — portfolio grid: company name (site-authored logo alt), status label and website. (`telstraventures_scraper.py`) |
| Digital Horizon | `digitalhorizon_companies.json` | 28 | digitalhorizon.com/portfolio — portfolio cards: company name, founders, description and website. (`digitalhorizon_scraper.py`) |
| Caffeinated Capital | `caffeinatedcapital_companies.json` | 13 | caffeinated.com — homepage cards: company cards (name and one-line mission) plus founder cards (company from the card's role line, e.g. 'CEO & Co-Founder / Airtable'). (`caffeinatedcapital_scraper.py`) |
| PhotonVentures | `photonvc_companies.json` | 21 | photonventures.vc/portfolio.php — portfolio descriptions: company name (heading) and description. (`photonvc_scraper.py`) |
| TechOperators | `techoperators_companies.json` | 20 | techoperators.com/portfolio — portfolio reviews: company name and one-line description. (`techoperators_scraper.py`) |
| Bungalow | `bungalow_companies.json` | 15 | bungalow.vc — homepage portfolio list: company name (link text) and website. (`bungalow_scraper.py`) |
| Outlander VC | `outlandervc_companies.json` | 19 | outlander.vc/portfolio — portfolio grid: company name. (`outlandervc_scraper.py`) |
| Eminence Ventures | `eminencevc_companies.json` | 16 | eminence.vc/portfolio — portfolio grid: company name and description. (`eminencevc_scraper.py`) |
| Xfund | `xfund_companies.json` | 12 | xfund.com/portfolio — portfolio list: company name. (`xfund_scraper.py`) |
| Nordic Alpha Partners | `nordicalpha_companies.json` | 10 | nordicalpha.com — homepage portfolio tags: company name and status (Active / Exited). (`nordicalpha_scraper.py`) |
| Blue Ashva Capital | `blueashva_companies.json` | 13 | blueashvacapital.com/portfolio — portfolio cards: company name, sector line, status and website. (`blueashva_scraper.py`) |
| Flucas Ventures | `flucasventures_companies.json` | 271 | flucasvc.com/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`flucasventures_scraper.py`) |
| Social Starts | `socialstarts_companies.json` | 174 | socialstarts.com/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`socialstarts_scraper.py`) |
| Metaplanet | `metaplanet_companies.json` | 175 | metaplanet.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`metaplanet_scraper.py`) |
| Borderless Capital | `borderlessventure_companies.json` | 121 | borderlesscapital.io/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`borderlessventure_scraper.py`) |
| Karista | `karista_companies.json` | 74 | karista.vc/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`karista_scraper.py`) |
| Norte Ventures | `norteventures_companies.json` | 125 | norte.ventures/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`norteventures_scraper.py`) |
| Olive Tree Capital | `olivetreecapital_companies.json` | 127 | olivetreecapital.com/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`olivetreecapital_scraper.py`) |
| Nazca | `nazca_companies.json` | 66 | nazca.vc/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`nazca_scraper.py`) |
| Red Beard Ventures | `redbeardventures_companies.json` | 111 | redbeard.ventures/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`redbeardventures_scraper.py`) |
| Breyer Capital | `breyercapital_companies.json` | 110 | breyercapital.com/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`breyercapital_scraper.py`) |
| BIP Ventures | `bipventures_companies.json` | 99 | bipventures.vc/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`bipventures_scraper.py`) |
| NGP Capital | `ngpcapital_companies.json` | 100 | ngpcap.com/companies/anybotics — company page whose sidebar lists the full portfolio: company name (site-authored heading/label text) and website where linked. (`ngpcapital_scraper.py`) |
| The Chernin Group | `thecherningroup_companies.json` | 95 | tcg.co/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`thecherningroup_scraper.py`) |
| GRIDX | `gridx_companies.json` | 86 | gridexponential.com/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`gridx_scraper.py`) |
| Wayfinder Ventures | `wayfinderventures_companies.json` | 88 | wayfinder.com/companies — portfolio page: company name (site-authored text / logo alt) and website where linked. (`wayfinderventures_scraper.py`) |
| Sora Ventures | `soraventures_companies.json` | 86 | sora.vc/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`soraventures_scraper.py`) |
| GSV Ventures | `gsvventures_companies.json` | 87 | gsv.ventures/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`gsvventures_scraper.py`) |
| EMV Capital | `emvcapital_companies.json` | 61 | emvcapital.com/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`emvcapital_scraper.py`) |
| Front Row Ventures | `frontrowventures_companies.json` | 81 | frontrow.ventures/en/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`frontrowventures_scraper.py`) |
| Paladin Capital Group | `paladincapitalgroup_companies.json` | 77 | paladincapgroup.com/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`paladincapitalgroup_scraper.py`) |
| Icon Ventures | `iconventures_companies.json` | 78 | iconventures.com/companies — portfolio page: company name (site-authored heading/label text) and website where linked. (`iconventures_scraper.py`) |
| Draper Dragon | `draperdragon_companies.json` | 81 | draperdragon.com/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`draperdragon_scraper.py`) |
| DAG Ventures | `dagventures_companies.json` | 83 | dagventures.com/investments — portfolio page: company name (site-authored heading/label text) and website where linked. (`dagventures_scraper.py`) |
| VTF Capital | `vtfcapital_companies.json` | 77 | vtfcapital.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`vtfcapital_scraper.py`) |
| New Ground Ventures | `newgroundventures_companies.json` | 75 | newground.vc/investments/#Filterable-Portfolio%7C1-current%7C1%7C%7CPortfolio%7Chighlights%7C1 — portfolio page: company name (site-authored text / logo alt) and website where linked. (`newgroundventures_scraper.py`) |
| Jenson Ventures | `jensonventures_companies.json` | 73 | jensonventures.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`jensonventures_scraper.py`) |
| Bow Capital | `bowcapital_companies.json` | 54 | bowcapital.com — portfolio page: company name (site-authored text / logo alt) and website where linked. (`bowcapital_scraper.py`) |
| Base Ventures | `baseventure_companies.json` | 73 | base.ventures/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`baseventure_scraper.py`) |
| LongHash Ventures | `longhashventures_companies.json` | 72 | longhash.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`longhashventures_scraper.py`) |
| Dholakia Ventures | `dholakiaventures_companies.json` | 67 | dholakiaventures.com/portfolios — portfolio page: company name (site-authored text / logo alt) and website where linked. (`dholakiaventures_scraper.py`) |
| UK Innovation & Science Seed Fund | `uki2s_companies.json` | 70 | ukinnovationscienceseedfund.co.uk/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`uki2s_scraper.py`) |
| Upsparks Capital | `upsparkscapital_companies.json` | 69 | upsparks.vc/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`upsparkscapital_scraper.py`) |
| Eoniq | `eoniqfund_companies.json` | 79 | eoniq.fund/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`eoniqfund_scraper.py`) |
| BOLD Capital Partners | `boldcapitalpartners_companies.json` | 70 | boldcapitalpartners.com/companies — portfolio page: company name (site-authored heading/label text) and website where linked. (`boldcapitalpartners_scraper.py`) |
| AIX Ventures | `aixventures_companies.json` | 72 | aixventures.com/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`aixventures_scraper.py`) |
| Yolo Investments | `yoloinvestments_companies.json` | 71 | yolo.io — portfolio page: company name (site-authored text / logo alt) and website where linked. (`yoloinvestments_scraper.py`) |
| Emles Venture Partners | `emlesventurepartners_companies.json` | 67 | emlesventure.com/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`emlesventurepartners_scraper.py`) |
| Dreamers VC | `dreamersvc_companies.json` | 68 | dreamers.vc — portfolio page: company name (site-authored heading/label text) and website where linked. (`dreamersvc_scraper.py`) |
| Able Partners | `ablepartners_companies.json` | 68 | ablepartners.nyc — portfolio page: company name (site-authored text / logo alt) and website where linked. (`ablepartners_scraper.py`) |
| ClearSky | `clearsky_companies.json` | 66 | clear-sky.com/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`clearsky_scraper.py`) |
| Flori Ventures | `floriventures_companies.json` | 67 | floriventures.com/companies — portfolio page: company name (site-authored heading/label text) and website where linked. (`floriventures_scraper.py`) |
| Civilization Ventures | `civilizationventures_companies.json` | 66 | civilizationventures.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`civilizationventures_scraper.py`) |
| Celtic House Asia Partners | `celtichouseasiapartners_companies.json` | 66 | celticvc.com/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`celtichouseasiapartners_scraper.py`) |
| Peregrine Ventures | `peregrineventures_companies.json` | 64 | peregrinevc.com/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`peregrineventures_scraper.py`) |
| 7percent Ventures | `7percentventures_companies.json` | 60 | 7pc.vc/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`7percentventures_scraper.py`) |
| Pacific Channel | `pacificchannel_companies.json` | 64 | pacificchannel.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`pacificchannel_scraper.py`) |
| Early Light Ventures | `earlylightventures_companies.json` | 61 | earlylight.vc/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`earlylightventures_scraper.py`) |
| Open Opportunity Fund | `openopportunityfund_companies.json` | 66 | theopportunityfund.com/companies — portfolio page: company name (site-authored link text) and website where linked. (`openopportunityfund_scraper.py`) |
| Mars Shot Ventures | `marsshotventures_companies.json` | 50 | marsshot.vc — portfolio page: company name (site-authored text / logo alt) and website where linked. (`marsshotventures_scraper.py`) |
| Miton | `miton_companies.json` | 59 | miton.cz/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`miton_scraper.py`) |
| Merus Capital | `meruscapital_companies.json` | 62 | meruscap.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`meruscapital_scraper.py`) |
| Cortado Ventures | `cortadoventures_companies.json` | 54 | cortado.ventures/portfolio-new — portfolio page: company name (site-authored text / logo alt) and website where linked. (`cortadoventures_scraper.py`) |
| Flyover Capital | `flyovercapital_companies.json` | 49 | flyovercapital.com/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`flyovercapital_scraper.py`) |
| Black Jays Ventures | `blackjaysventures_companies.json` | 59 | blackjays.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`blackjaysventures_scraper.py`) |
| Green Park & Golf Ventures | `greenparkgolfventures_companies.json` | 56 | gpgventures.com/investments — portfolio page: company name (site-authored heading/label text) and website where linked. (`greenparkgolfventures_scraper.py`) |
| Earl Grey Capital | `earlgreycapital_companies.json` | 49 | earlgrey.capital/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`earlgreycapital_scraper.py`) |
| Gemba Capital | `gembacapital_companies.json` | 45 | gembacapital.in/portfolio.php — portfolio page: company name (site-authored logo alt) and website where linked. (`gembacapital_scraper.py`) |
| Auxxo | `auxxo_companies.json` | 47 | auxxo.de/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`auxxo_scraper.py`) |
| Construct Capital | `constructcapital_companies.json` | 44 | constructcap.com/companies — portfolio page: company name (site-authored logo alt) and website where linked. (`constructcapital_scraper.py`) |
| Hartmann Capital | `hartmanncapital_companies.json` | 33 | hartmanncapital.com/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`hartmanncapital_scraper.py`) |
| Pix Vine Capital | `pixvinecapital_companies.json` | 38 | pixvc.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`pixvinecapital_scraper.py`) |
| Outbound Ventures | `outboundventures_companies.json` | 36 | outboundventures.com — portfolio page: company name (site-authored text / logo alt) and website where linked. (`outboundventures_scraper.py`) |
| UVC Partners | `uvcpartners_companies.json` | 25 | uvcpartners.com — portfolio page: company name (site-authored text / logo alt) and website where linked. (`uvcpartners_scraper.py`) |
| Millennium New Horizons | `millenniumnewhorizons_companies.json` | 26 | mnh.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`millenniumnewhorizons_scraper.py`) |
| Juniper VC | `juniper_companies.json` | 50 | junipervc.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`juniper_scraper.py`) |
| DSG Consumer Partners | `dsgconsumer_companies.json` | 14 | dsgcp.com — homepage brand cards: company name (site-authored image alt). (`dsgconsumer_scraper.py`) |
| Alumni Ventures | `alumniventures_companies.json` | 1731 | av.vc/portfolio — Next.js `__NEXT_DATA__` full portfolio list: name, description, website, co-investors, AV region/stage/sector tags, AV funds holding the company. (`alumniventures_scraper.py`) |
| Precursor Ventures | `precursor_companies.json` | 184 | precursorvc.com/portfolio — site's own JS bundle arrays: company name, website, sector; founders list. (`precursor_scraper.py`) |
| Upfront Ventures | `upfront_companies.json` | 166 | upfront.com/portfolio — Angular app via headless Chrome (`_chrome_dom.py`): name, one-liner, status badge (Acquired/IPO/active), CEO, location, website. (`upfront_scraper.py`) |
| firstminute capital | `firstminute_companies.json` | 139 | firstminute.capital/portfolio — headless Chrome render: name, sector label, geography (no descriptions/websites/status published). (`firstminute_scraper.py`) |
| Offline Ventures | `offlineventures_companies.json` | 136 | offline.vc/portfolio — site's own Vite JS bundle array: name, website, short/long description, sector, featured flag, acquisition note (status). (`offlineventures_scraper.py`) |
| Freestyle Capital | `freestyle_companies.json` | 108 | freestyle.vc/companies — site's public tRPC `companies.list`: description, website, portfolio label, status (firm's own Acquired labels). (`freestyle_scraper.py`) |
| FinTech Collective | `fintechcollective_companies.json` | 79 | fintech.io/portfolio — headless Chrome render: name, one-liner + long description, industry, CEO, "Investor Since" stage, website, Exited label. (`fintechcollective_scraper.py`) |
| Moonfire Ventures | `moonfire_companies.json` | 74 | moonfire.com/portfolio — Next.js RSC payload (short desc, website, founders, HQ, founded/backed dates, sectors, lead) + Chrome DOM to drop 8 "Prior Investments"; names from description prefix/logo alt. (`moonfire_scraper.py`) |
| Promus Ventures | `promus_companies.json` | 73 | promusventures.com/portfolio — headless Chrome rows (name, active/exited chip) + static /project/ pages (website, description, founded, location, team). (`promus_scraper.py`) |
| Harlem Capital | `harlem_companies.json` | 58 | harlem.capital/portfolio — site's own public WPGraphQL query: name, description, founder(s), website, category labels, Exited label. (`harlem_scraper.py`) |
| Jetstream | `jetstream_companies.json` | 52 | jetstream.io/startups — "Our investments include" list: name, one-liner, website. (`jetstream_scraper.py`) |
| Forward Venture Capital | `forwardvc_companies.json` | 51 | forwardvc.com — Current / Past journeys grids: name, city/country, website (current), status active/exited; no descriptions. (`forwardvc_scraper.py`) |
| AfterWork Ventures | `afterwork_companies.json` | 47 | afterwork.vc/portfolio — Webflow CMS: name, website, sector label, invested year (first invested), Acquired badge, investment memo link. (`afterwork_scraper.py`) |
| Angel Invest | `angelinvest_companies.json` | 46 | angelinvest.ventures/portfolio — portfolio highlights + company pages: location, description, sector, website, founders, Angel Invest partner, co-investors. (`angelinvest_scraper.py`) |
| Catalyst Investors | `catalystinvestors_companies.json` | 39 | catalyst.com/portfolios — WP admin-ajax loadmore (Current/Exited): description, website, first invested, exit note/acquirer/year, status. (`catalystinvestors_scraper.py`) |
| TFX Capital | `tfxcapital_companies.json` | 25 | tfxcap.com/tfxportfolio/companies — Active/Exited/Inactive sections: name, HQ, founders/leadership, description, website, exit note. (`tfxcapital_scraper.py`) |
| Distributed Ventures | `distributedventures_companies.json` | 22 | distributedvc.com/portfolio — Webflow cards: description, website, fund (current vs Prior Investments), Acquired badge, categories from company pages; names from description/slug. (`distributedventures_scraper.py`) |
| Overlook Ventures | `overlook_companies.json` | 18 | overlook.vc/portfolio — headless Chrome render: name, one-liner, website, stage, year (first invested), city. (`overlook_scraper.py`) |
| Cake Ventures | `cakeventures_companies.json` | 16 | cake.vc/companies — Webflow CMS: name, one-liner, long description, status, website, categories, location; founders from company pages. (`cakeventures_scraper.py`) |
| Zenda | `zenda_companies.json` | 12 | zenda.vc/portfolio — WP grid: name, one-liner, HQ, co-investors, website, exit note (STEALTH tiles skipped). (`zenda_scraper.py`) |
| Laguna Investment | `lagunainvestment_companies.json` | 120 | lagunai.com/Portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`lagunainvestment_scraper.py`) |
| mint VC | `mintvc_companies.json` | 105 | mint-vc.com/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`mintvc_scraper.py`) |
| Delight Ventures | `delightventures_companies.json` | 71 | delight-ventures.com/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`delightventures_scraper.py`) |
| ShangBay Capital | `shangbaycapital_companies.json` | 71 | shangbaycapital.com/portfolio-companies — portfolio page: company name (site-authored text / logo alt) and website where linked. (`shangbaycapital_scraper.py`) |
| Peercheque | `peercheque_companies.json` | 50 | peercheque.com/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`peercheque_scraper.py`) |
| TRGC | `trgc_companies.json` | 57 | trgc.io/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`trgc_scraper.py`) |
| Groove Capital | `groovecapital_companies.json` | 103 | groovecap.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`groovecapital_scraper.py`) |
| AAF Management | `aaf_companies.json` | 27 | aaf.vc/investments — portfolio page: company name (site-authored heading/label text) and website where linked. (`aaf_scraper.py`) |
| bmp Ventures | `bmpventures_companies.json` | 38 | bmp.com/portfolio — portfolio page: company name (site-authored text / logo alt) and website where linked. (`bmpventures_scraper.py`) |
| Samos Investments | `samosinvestments_companies.json` | 90 | samos.vc — portfolio page: company name (site-authored text / logo alt) and website where linked. (`samosinvestments_scraper.py`) |
| Delphi Ventures | `delphiventures_companies.json` | 10 | delphiventures.io/portfolio-crypto — Framer portfolio table: project name, year invested, sector and website. (`delphiventures_scraper.py`) |
| Unovis Asset Management | `unovis_companies.json` | 33 | unovis.vc/portfolio — portfolio module items (`div.module__item`): company name (site-authored logo alt, before ' - '), description, location, website, founders, initial investment stage, category and geography. (`unovis_scraper.py`) |
| Haven Ventures | `havenventures_companies.json` | 11 | haven.vc — homepage portfolio: company name (site-authored logo alt) and website where linked. (`havenventures_scraper.py`) |
| Align Ventures | `alignventures_companies.json` | 15 | align.vc — homepage portfolio: company name (site-authored logo alt) and website where linked. (`alignventures_scraper.py`) |
| Silicon Gardens | `silicongardens_companies.json` | 98 | silicongardens.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`silicongardens_scraper.py`) |
| Aster Capital | `astercapital_companies.json` | 72 | aster.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`astercapital_scraper.py`) |
| Merak Ventures | `merakventures_companies.json` | 43 | merakventures.com/portfolio.html — portfolio page: company name (site-authored logo alt) and website where linked. (`merakventures_scraper.py`) |
| MAGIC Fund | `magicfund_companies.json` | 67 | magic.fund — portfolio page: company name (site-authored heading/label text) and website where linked. (`magicfund_scraper.py`) |
| DEPO Ventures | `depoventures_companies.json` | 62 | depoventures.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`depoventures_scraper.py`) |
| One Planet Capital | `oneplanetcapital_companies.json` | 58 | oneplanet.capital/portfolio — portfolio page: company name (site-authored link text) and website where linked. (`oneplanetcapital_scraper.py`) |
| PruVen Capital Partners | `pruvencapitalpartners_companies.json` | 56 | pruvencap.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`pruvencapitalpartners_scraper.py`) |
| Faction | `faction_companies.json` | 60 | faction.vc — portfolio page: company name (site-authored logo alt) and website where linked. (`faction_scraper.py`) |
| Trilogy Equity Partners | `trilogyequitypartners_companies.json` | 57 | trilogyequity.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`trilogyequitypartners_scraper.py`) |
| Texas HALO Fund | `texashalofund_companies.json` | 52 | texashalofund.com/texas-halo-fund-ii/halo-ii-portfolio — portfolio page: company name (site-authored link text) and website where linked. (`texashalofund_scraper.py`) |
| OIF Ventures | `oifventures_companies.json` | 56 | oifventures.com.au/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`oifventures_scraper.py`) |
| Ryze Labs | `ryzelabs_companies.json` | 47 | ryzelabs.io/en/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`ryzelabs_scraper.py`) |
| R136 Ventures | `r136ventures_companies.json` | 52 | r136.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`r136ventures_scraper.py`) |
| Vela Partners | `velapartners_companies.json` | 50 | vela.partners/portfolio — portfolio page: company name (site-authored link text) and website where linked. (`velapartners_scraper.py`) |
| MPower Partners | `mpower_companies.json` | 52 | mpower-partners.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`mpower_scraper.py`) |
| Soundboard Venture Fund | `soundboardventurefund_companies.json` | 54 | soundboardventurefund.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`soundboardventurefund_scraper.py`) |
| Future Perfect Ventures | `futureperfectventures_companies.json` | 53 | futureperfectventures.com/invest — portfolio page: company name (site-authored heading/label text) and website where linked. (`futureperfectventures_scraper.py`) |
| Moonstone Venture Capital | `moonstoneventurecapital_companies.json` | 50 | moonstone.fund/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`moonstoneventurecapital_scraper.py`) |
| Lobster Capital | `lobstercapital_companies.json` | 49 | lobstercap.com/companies — portfolio page: company name (site-authored logo alt) and website where linked. (`lobstercapital_scraper.py`) |
| Keshif Ventures | `keshifventures_companies.json` | 50 | keshif.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`keshifventures_scraper.py`) |
| Andromeda Capital | `andromedacapital_companies.json` | 48 | andromedavc.io — portfolio page: company name (site-authored logo alt) and website where linked. (`andromedacapital_scraper.py`) |
| AIN Ventures | `ainventures_companies.json` | 51 | ainventures.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`ainventures_scraper.py`) |
| Modi Ventures | `modiventures_companies.json` | 49 | modivc.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`modiventures_scraper.py`) |
| Lince Capital | `lincecapital_companies.json` | 51 | lince-capital.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`lincecapital_scraper.py`) |
| Denver Ventures | `denverventures_companies.json` | 24 | denverventures.co/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`denverventures_scraper.py`) |
| The Raba Partnership | `therabapartnership_companies.json` | 48 | rabacap.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`therabapartnership_scraper.py`) |
| SBXi | `sbxi_companies.json` | 48 | sbxi.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`sbxi_scraper.py`) |
| NuVentures | `nuventures_companies.json` | 47 | nuventures.vc/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`nuventures_scraper.py`) |
| NovaCapital | `novacapital_companies.json` | 44 | novacapital.eu/it/portfolio.html — portfolio page: company name (site-authored logo alt) and website where linked. (`novacapital_scraper.py`) |
| JK&B Capital | `jkbcapital_companies.json` | 49 | jkbcapital.com/portfolio-companies — portfolio page: company name (site-authored heading/label text) and website where linked. (`jkbcapital_scraper.py`) |
| Carbide Ventures | `carbideventures_companies.json` | 49 | carbideventures.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`carbideventures_scraper.py`) |
| Alpana Ventures | `alpanaventures_companies.json` | 47 | alpana-ventures.ch/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`alpanaventures_scraper.py`) |
| LRVHealth | `lrvhealth_companies.json` | 50 | lrvhealth.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`lrvhealth_scraper.py`) |
| Netrix Ventures | `netrixventures_companies.json` | 63 | netrix.ventures/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`netrixventures_scraper.py`) |
| Two Culture Capital | `twoculturecapital_companies.json` | 45 | twoculturecap.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`twoculturecapital_scraper.py`) |
| Rebel Fund | `rebelfund_companies.json` | 48 | rebelfund.vc — portfolio page: company name (site-authored heading/label text) and website where linked. (`rebelfund_scraper.py`) |
| New Science Ventures | `newscienceventures_companies.json` | 47 | newscienceventures.com/our-companies — portfolio page: company name (site-authored heading/label text) and website where linked. (`newscienceventures_scraper.py`) |
| L2 Iterative Ventures | `l2iterativeventures_companies.json` | 47 | l2iterative.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`l2iterativeventures_scraper.py`) |
| Fourth Realm | `fourthrealm_companies.json` | 47 | fourthrealm.vc — portfolio page: company name (site-authored link text) and website where linked. (`fourthrealm_scraper.py`) |
| Champion Hill Ventures | `championhillventures_companies.json` | 45 | championhillventures.com/investments — portfolio page: company name (site-authored heading/label text) and website where linked. (`championhillventures_scraper.py`) |
| TDV Partners | `tdvpartners_companies.json` | 44 | tdv.partners/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`tdvpartners_scraper.py`) |
| Bankless Ventures | `banklessventures_companies.json` | 45 | bankless.ventures — portfolio page: company name (site-authored heading/label text) and website where linked. (`banklessventures_scraper.py`) |
| BADideas.fund | `badideasfund_companies.json` | 44 | badideas.fund/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`badideasfund_scraper.py`) |
| 11.2 Capital | `112capital_companies.json` | 43 | 112capital.com/companies.html — portfolio page: company name (site-authored heading/label text) and website where linked. (`112capital_scraper.py`) |
| Trind Ventures | `trindventures_companies.json` | 43 | trind.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`trindventures_scraper.py`) |
| Serpentine Ventures | `serpentineventures_companies.json` | 43 | serpentine.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`serpentineventures_scraper.py`) |
| Maxpro Ventures | `maxproventures_companies.json` | 42 | maxproventures.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`maxproventures_scraper.py`) |
| Deep Future | `deepfuture_companies.json` | 42 | deepfuture.tech/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`deepfuture_scraper.py`) |
| 1818 Venture Capital | `1818venturecapital_companies.json` | 44 | 1818venturecapital.com/our-portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`1818venturecapital_scraper.py`) |
| NVP Capital | `nvpcapital_companies.json` | 40 | nvpcap.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`nvpcapital_scraper.py`) |
| FreshTracks Capital | `freshtrackscapital_companies.json` | 42 | freshtrackscap.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`freshtrackscapital_scraper.py`) |
| Dig Ventures | `digventures_companies.json` | 43 | dig.ventures/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`digventures_scraper.py`) |
| Capital Midwest Fund | `capitalmidwestfund_companies.json` | 41 | capitalmidwest.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`capitalmidwestfund_scraper.py`) |
| Braemar Energy Ventures | `braemarenergyventures_companies.json` | 42 | braemarenergy.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`braemarenergyventures_scraper.py`) |
| Windham Capital Partners | `windhamcapitalpartners_companies.json` | 40 | windhamcap.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`windhamcapitalpartners_scraper.py`) |
| Swift Ventures | `swiftventures_companies.json` | 40 | swift.vc/companies — portfolio page: company name (site-authored logo alt) and website where linked. (`swiftventures_scraper.py`) |
| UDHC | `udhc_companies.json` | 39 | udhc.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`udhc_scraper.py`) |
| Plum Ventures | `plumventures_companies.json` | 40 | plumventures.cn — portfolio page: company name (site-authored heading/label text) and website where linked. (`plumventures_scraper.py`) |
| Emblem | `emblem_companies.json` | 36 | emblem.vc — portfolio page: company name (site-authored logo alt) and website where linked. (`emblem_scraper.py`) |
| Wellstreet | `wellstreet_companies.json` | 37 | wellstreet.se/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`wellstreet_scraper.py`) |
| Venista Ventures | `venistaventures_companies.json` | 38 | venista-ventures.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`venistaventures_scraper.py`) |
| Red Building Capital | `redbuildingcapital_companies.json` | 39 | rbcap.io/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`redbuildingcapital_scraper.py`) |
| Lumis Partners | `lumispartners_companies.json` | 37 | lumispartners.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`lumispartners_scraper.py`) |
| Kogito Ventures | `kogitoventures_companies.json` | 38 | kogito-ventures.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`kogitoventures_scraper.py`) |
| Interlace Ventures | `interlaceventures_companies.json` | 37 | interlacevc.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`interlaceventures_scraper.py`) |
| Innovation Industries | `innovationindustries_companies.json` | 41 | innovationindustries.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`innovationindustries_scraper.py`) |
| Early Game Ventures | `earlygameventures_companies.json` | 38 | earlygame.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`earlygameventures_scraper.py`) |
| Cosmic Venture Partners | `cosmicventurepartners_companies.json` | 39 | cosmicvp.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`cosmicventurepartners_scraper.py`) |
| AI Seed | `aiseed_companies.json` | 39 | aiseedfund.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`aiseed_scraper.py`) |
| Virescent Ventures | `virescentventures_companies.json` | 37 | virescent.vc — portfolio page: company name (site-authored heading/label text) and website where linked. (`virescentventures_scraper.py`) |
| Start Capital | `startcapital_companies.json` | 37 | start-capital.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`startcapital_scraper.py`) |
| Sondo Capital | `sondocapital_companies.json` | 37 | sondo.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`sondocapital_scraper.py`) |
| Second Alpha Partners | `secondalphapartners_companies.json` | 40 | secondalpha.com/companies — portfolio page: company name (site-authored heading/label text) and website where linked. (`secondalphapartners_scraper.py`) |
| ScOp Venture Capital | `scopventurecapital_companies.json` | 39 | scopvc.com/companies — portfolio page: company name (site-authored heading/label text) and website where linked. (`scopventurecapital_scraper.py`) |
| Nuwa Capital | `nuwacapital_companies.json` | 37 | nuwacapital.io/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`nuwacapital_scraper.py`) |
| Eterna Capital | `eternacapital_companies.json` | 38 | eternacapital.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`eternacapital_scraper.py`) |
| Athera Venture Partners | `atheraventurepartners_companies.json` | 37 | atheravp.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`atheraventurepartners_scraper.py`) |
| SuperSeed | `superseed_companies.json` | 36 | superseed.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`superseed_scraper.py`) |
| Naples Technology Ventures | `naplestechnologyventures_companies.json` | 37 | naplestechnologyventures.com/companies — portfolio page: company name (site-authored logo alt) and website where linked. (`naplestechnologyventures_scraper.py`) |
| ISA Ventures | `isaventures_companies.json` | 36 | isaventures.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`isaventures_scraper.py`) |
| Form Ventures | `formventures_companies.json` | 35 | formventures.vc — portfolio page: company name (site-authored logo alt) and website where linked. (`formventures_scraper.py`) |
| E2MC Ventures | `e2mcventures_companies.json` | 36 | e2mc.space/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`e2mcventures_scraper.py`) |
| Cyber Mentor Fund | `cybermentorfund_companies.json` | 36 | cybermentorfund.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`cybermentorfund_scraper.py`) |
| Balerion Space Ventures | `balerionspaceventures_companies.json` | 35 | balerionspace.com/companies — portfolio page: company name (site-authored logo alt) and website where linked. (`balerionspaceventures_scraper.py`) |
| 3cubed Ventures | `3cubedventures_companies.json` | 36 | 3cubed.vc/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`3cubedventures_scraper.py`) |
| Sherpalo Ventures | `sherpaloventures_companies.json` | 35 | sherpalo.com/investments — portfolio page: company name (site-authored heading/label text) and website where linked. (`sherpaloventures_scraper.py`) |
| Linden Capital | `lindencapital_companies.json` | 35 | lindencapital.de — portfolio page: company name (site-authored link text) and website where linked. (`lindencapital_scraper.py`) |
| Infinity Ventures | `infinityventures_companies.json` | 36 | infinityvc.capital/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`infinityventures_scraper.py`) |
| Groom Investment | `groominvestment_companies.json` | 35 | groominvest.co.kr/all — portfolio page: company name (site-authored heading/label text) and website where linked. (`groominvestment_scraper.py`) |
| Positive Sum Capital | `positivesumcapital_companies.json` | 40 | positivesum.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`positivesumcapital_scraper.py`) |
| Polymorphic Capital | `polymorphiccapital_companies.json` | 34 | polymorphic.capital — portfolio page: company name (site-authored heading/label text) and website where linked. (`polymorphiccapital_scraper.py`) |
| PHX Ventures | `phxventures_companies.json` | 34 | phxventures.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`phxventures_scraper.py`) |
| NOEMIS Ventures | `noemisventures_companies.json` | 33 | noemisventures.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`noemisventures_scraper.py`) |
| Failup Ventures | `failupventures_companies.json` | 33 | failup.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`failupventures_scraper.py`) |
| Ev3 Ventures | `ev3ventures_companies.json` | 35 | ev3.xyz/portfolio — portfolio page: company name (site-authored link text) and website where linked. (`ev3ventures_scraper.py`) |
| EQ2 Ventures | `eq2ventures_companies.json` | 33 | eq2ventures.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`eq2ventures_scraper.py`) |
| Color Capital | `colorcapital_companies.json` | 35 | color.capital/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`colorcapital_scraper.py`) |
| Asia2G Capital | `asia2gcapital_companies.json` | 36 | asia2gcapital.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`asia2gcapital_scraper.py`) |
| Arctic Digital | `arcticdigital_companies.json` | 33 | arcticdigital.xyz/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`arcticdigital_scraper.py`) |
| Stacked Capital | `stackedcapital_companies.json` | 33 | stacked.capital/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`stackedcapital_scraper.py`) |
| Position Ventures | `positionventures_companies.json` | 32 | positionventures.com/companies — portfolio page: company name (site-authored logo alt) and website where linked. (`positionventures_scraper.py`) |
| Oxonian Ventures | `oxonianventures_companies.json` | 33 | oxonianventures.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`oxonianventures_scraper.py`) |
| NextFab Ventures | `nextfabventures_companies.json` | 33 | nextfabventures.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`nextfabventures_scraper.py`) |
| J17 Capital | `j17capital_companies.json` | 33 | j17vc.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`j17capital_scraper.py`) |
| Harmonix Fund | `harmonixfund_companies.json` | 33 | harmonixfund.com/companies — portfolio page: company name (site-authored heading/label text) and website where linked. (`harmonixfund_scraper.py`) |
| GreenSky Ventures | `greenskyventures_companies.json` | 33 | greensky.vc/our-portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`greenskyventures_scraper.py`) |
| ECONA | `econa_companies.json` | 36 | econa.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`econa_scraper.py`) |
| Crucible Capital | `cruciblecapital_companies.json` | 33 | cruciblecap.xyz/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`cruciblecapital_scraper.py`) |
| Conductive Ventures | `conductiveventures_companies.json` | 36 | conductive.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`conductiveventures_scraper.py`) |
| Bisk Ventures | `biskventures_companies.json` | 34 | biskventures.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`biskventures_scraper.py`) |
| Amino Collective | `aminocollective_companies.json` | 31 | aminocollective.com/companies — portfolio page: company name (site-authored heading/label text) and website where linked. (`aminocollective_scraper.py`) |
| Pebblebed | `pebblebed_companies.json` | 32 | pebblebed.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`pebblebed_scraper.py`) |
| Paper Ventures | `paperventures_companies.json` | 31 | paper.ventures/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`paperventures_scraper.py`) |
| MESH | `mesh_companies.json` | 40 | mesh.vc — portfolio page: company name (site-authored logo alt) and website where linked. (`mesh_scraper.py`) |
| Cottonwood Technology Fund | `cottonwoodtechnologyfund_companies.json` | 33 | cottonwood.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`cottonwoodtechnologyfund_scraper.py`) |
| Undeterred Capital | `undeterredcapital_companies.json` | 29 | undeterredcapital.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`undeterredcapital_scraper.py`) |
| Red & Blue Ventures | `redblueventures_companies.json` | 33 | redandblue.vc/companies — portfolio page: company name (site-authored logo alt) and website where linked. (`redblueventures_scraper.py`) |
| Outset Ventures | `outsetventures_companies.json` | 31 | outset.ventures/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`outsetventures_scraper.py`) |
| MoreVC | `morevc_companies.json` | 30 | morevc.com/companies — portfolio page: company name (site-authored heading/label text) and website where linked. (`morevc_scraper.py`) |
| LEAP Global Partners | `leapglobalpartners_companies.json` | 31 | leapglobalpartners.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`leapglobalpartners_scraper.py`) |
| First Circle | `firstcircle_companies.json` | 31 | firstcircle.capital/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`firstcircle_scraper.py`) |
| California Innovation Fund | `californiainnovation_companies.json` | 30 | californiainnovationfund.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`californiainnovation_scraper.py`) |
| Beliade | `beliade_companies.json` | 31 | beliade.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`beliade_scraper.py`) |
| AdBio Partners | `adbiopartners_companies.json` | 30 | adbio.partners/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`adbiopartners_scraper.py`) |
| TCP Venture Capital | `tcpventurecapital_companies.json` | 34 | tcp.vc — portfolio page: company name (site-authored logo alt) and website where linked. (`tcpventurecapital_scraper.py`) |
| Significant Ventures | `significantventures_companies.json` | 31 | significant.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`significantventures_scraper.py`) |
| Pavestone | `pavestone_companies.json` | 31 | pavestone.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`pavestone_scraper.py`) |
| Oktogon Ventures | `oktogonventures_companies.json` | 32 | oktogon.vc — portfolio page: company name (site-authored heading/label text) and website where linked. (`oktogonventures_scraper.py`) |
| Northern Gritstone | `northerngritstone_companies.json` | 31 | northern-gritstone.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`northerngritstone_scraper.py`) |
| Mento VC | `mentovc_companies.json` | 30 | mento.vc — portfolio page: company name (site-authored heading/label text) and website where linked. (`mentovc_scraper.py`) |
| Heal Capital | `healcapital_companies.json` | 29 | healcapital.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`healcapital_scraper.py`) |
| Gabriel Venture Partners | `gabrielventurepartners_companies.json` | 30 | gabrielvp.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`gabrielventurepartners_scraper.py`) |
| Enzo Ventures | `enzoventures_companies.json` | 30 | enzoventures.eu/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`enzoventures_scraper.py`) |
| Chattanooga Renaissance Fund | `chattanoogarenaissancefu_companies.json` | 31 | chattanoogarenaissancefund.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`chattanoogarenaissancefu_scraper.py`) |
| Virta Ventures | `virtaventures_companies.json` | 29 | virtaventures.co/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`virtaventures_scraper.py`) |
| Tenmile | `tenmile_companies.json` | 29 | tenmile.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`tenmile_scraper.py`) |
| Techstart Ventures | `techstartventures_companies.json` | 30 | techstart.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`techstartventures_scraper.py`) |
| Tanglin Venture Partners | `tanglinventurepartners_companies.json` | 29 | tanglinvp.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`tanglinventurepartners_scraper.py`) |
| Syndicate One | `syndicateone_companies.json` | 29 | syndicate.one/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`syndicateone_scraper.py`) |
| Saviu Ventures | `saviuventures_companies.json` | 32 | saviu.vc/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`saviuventures_scraper.py`) |
| OVNI Capital | `ovnicapital_companies.json` | 28 | ovni.capital/portfolio — portfolio page: company name (site-authored link text) and website where linked. (`ovnicapital_scraper.py`) |
| Mythos Ventures | `mythosventures_companies.json` | 30 | mythos.vc/portfolio — portfolio page: company name (site-authored link text) and website where linked. (`mythosventures_scraper.py`) |
| Kairos Venture Investments | `kairosventureinvestments_companies.json` | 29 | kairosventures.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`kairosventureinvestments_scraper.py`) |
| Innovation Global Capital | `innovationglobalcapital_companies.json` | 28 | innovationglobal.com/our-portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`innovationglobalcapital_scraper.py`) |
| Ineffable Ventures | `ineffableventures_companies.json` | 29 | ineffableventures.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`ineffableventures_scraper.py`) |
| GroundBreak Ventures | `groundbreakventures_companies.json` | 28 | groundbreakventures.com/investments — portfolio page: company name (site-authored logo alt) and website where linked. (`groundbreakventures_scraper.py`) |
| GreyMatter | `greymatter_companies.json` | 32 | greymattercapital.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`greymatter_scraper.py`) |
| Galion.exe | `galionexe_companies.json` | 30 | galion-exe.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`galionexe_scraper.py`) |
| Eastlink Capital Partners | `eastlinkcapitalpartners_companies.json` | 30 | eastlinkcap.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`eastlinkcapitalpartners_scraper.py`) |
| Brass Ring Ventures | `brassringventures_companies.json` | 27 | brassring.vc/portfolio-2 — portfolio page: company name (site-authored heading/label text) and website where linked. (`brassringventures_scraper.py`) |
| Ajim Capital | `ajimcapital_companies.json` | 29 | ajimcapital.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`ajimcapital_scraper.py`) |
| Zanichelli Venture | `zanichelliventure_companies.json` | 28 | zanichelliventure.it/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`zanichelliventure_scraper.py`) |
| Neulogy Ventures | `neulogyventures_companies.json` | 28 | neulogy.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`neulogyventures_scraper.py`) |
| Debut Capital | `debutcapital_companies.json` | 28 | debutcapital.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`debutcapital_scraper.py`) |
| Baroda Ventures | `barodaventures_companies.json` | 28 | barodaventures.com/companies — portfolio page: company name (site-authored logo alt) and website where linked. (`barodaventures_scraper.py`) |
| Tamarak Capital | `tamarakcapital_companies.json` | 27 | tmrk.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`tamarakcapital_scraper.py`) |
| Tamarack Global | `tamarackglobal_companies.json` | 27 | tamarackglobal.com/investments — portfolio page: company name (site-authored logo alt) and website where linked. (`tamarackglobal_scraper.py`) |
| Melt Ventures | `meltventures_companies.json` | 28 | melt.ventures/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`meltventures_scraper.py`) |
| INCE Capital | `incecapital_companies.json` | 25 | incecap.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`incecapital_scraper.py`) |
| Impatient Ventures | `impatientventures_companies.json` | 27 | impatient.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`impatientventures_scraper.py`) |
| Fundamental Ventures | `fundamentalventures_companies.json` | 27 | fundamentalventures.com/companies — portfolio page: company name (site-authored heading/label text) and website where linked. (`fundamentalventures_scraper.py`) |
| Caruso Ventures | `carusoventures_companies.json` | 26 | carusoventures.com/investments — portfolio page: company name (site-authored logo alt) and website where linked. (`carusoventures_scraper.py`) |
| Also Capital | `alsocapital_companies.json` | 28 | alsocapital.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`alsocapital_scraper.py`) |
| Varana Capital | `varana_companies.json` | 27 | varanacapital.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`varana_scraper.py`) |
| SWaN & Legend Venture Partners | `swanlegendventurepartner_companies.json` | 27 | swanandlegend.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`swanlegendventurepartner_scraper.py`) |
| Progress Ventures | `progressventures_companies.json` | 26 | progressventures.com/portfolio-of-companies — portfolio page: company name (site-authored heading/label text) and website where linked. (`progressventures_scraper.py`) |
| LongeVC | `longevc_companies.json` | 25 | longevc.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`longevc_scraper.py`) |
| JAL Ventures | `jalventures_companies.json` | 26 | jalventures.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`jalventures_scraper.py`) |
| Hemi Ventures | `hemiventures_companies.json` | 26 | hemi.vc/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`hemiventures_scraper.py`) |
| Helium-3 Ventures | `helium3ventures_companies.json` | 28 | helium-3ventures.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`helium3ventures_scraper.py`) |
| Department of XYZ | `departmentofxyz_companies.json` | 25 | theventuredept.vc/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`departmentofxyz_scraper.py`) |
| Vala Capital | `valacapital_companies.json` | 25 | valacap.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`valacapital_scraper.py`) |
| Tracxn Labs | `tracxnlabs_companies.json` | 25 | tracxnlabs.com — portfolio page: company name (site-authored logo alt) and website where linked. (`tracxnlabs_scraper.py`) |
| TIRTA Ventures | `tirtaventures_companies.json` | 25 | tirta.io/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`tirtaventures_scraper.py`) |
| Series Ventures | `seriesventures_companies.json` | 23 | s-ventures.co.kr — portfolio page: company name (site-authored logo alt) and website where linked. (`seriesventures_scraper.py`) |
| Joa Capital | `joacapital_companies.json` | 25 | joa.capital/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`joacapital_scraper.py`) |
| JDS Sports | `jdssports_companies.json` | 28 | jdssports.co — portfolio page: company name (site-authored logo alt) and website where linked. (`jdssports_scraper.py`) |
| Eudemian Ventures | `eudemianventures_companies.json` | 25 | eudemian.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`eudemianventures_scraper.py`) |
| Charlotte Street Capital | `charlottestreetcapital_companies.json` | 25 | charlottestreetcapital.com/portfolio-1-1 — portfolio page: company name (site-authored heading/label text) and website where linked. (`charlottestreetcapital_scraper.py`) |
| Keiki Capital | `keikicapital_companies.json` | 25 | keikicapital.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`keikicapital_scraper.py`) |
| Mount VC | `mountvc_companies.json` | 24 | mountfund.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`mountvc_scraper.py`) |
| Fulcrum Venture Group | `fulcrumventure_companies.json` | 24 | fulcrumvg.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`fulcrumventure_scraper.py`) |
| Dnipro VC | `dnipro_companies.json` | 26 | dnipro.vc — portfolio page: company name (site-authored link text) and website where linked. (`dnipro_scraper.py`) |
| MPG Fund | `mpgfund_companies.json` | 29 | mpgfund.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`mpgfund_scraper.py`) |
| Henq | `henq_companies.json` | 25 | henq.vc — portfolio page: company name (site-authored logo alt) and website where linked. (`henq_scraper.py`) |
| Amador Holdings | `amadorholdings_companies.json` | 33 | amador.holdings/portfolio.html — portfolio page: company name (site-authored heading/label text) and website where linked. (`amadorholdings_scraper.py`) |
| Juvo Ventures | `juvoventures_companies.json` | 25 | juvovc.org — portfolio page: company name (site-authored logo alt) and website where linked. (`juvoventures_scraper.py`) |
| Sarah Smith Fund | `sarahsmith_companies.json` | 48 | sarahsmith.fund — portfolio page: company name (site-authored link text) and website where linked. (`sarahsmith_scraper.py`) |
| DG Daiwa Ventures | `dgdaiwaventures_companies.json` | 152 | dg-daiwa-v.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`dgdaiwaventures_scraper.py`) |
| BioGenerator Ventures | `biogeneratorventures_companies.json` | 104 | biogeneratorventures.com/biogenerator-ventures/investment-portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`biogeneratorventures_scraper.py`) |
| Hiroshima Venture Capital | `hiroshimaventurecapitalc_companies.json` | 92 | hiroshima.ventures/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`hiroshimaventurecapitalc_scraper.py`) |
| Jam Fund | `jamfund_companies.json` | 56 | jamfund.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`jamfund_scraper.py`) |
| Mighty Capital | `mightycapital_companies.json` | 51 | mighty.capital/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`mightycapital_scraper.py`) |
| Access Venture Partners | `accessventurepartners_companies.json` | 51 | accessvp.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`accessventurepartners_scraper.py`) |
| Spiral Ventures | `spiralventures_companies.json` | 46 | spiral-ventures.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`spiralventures_scraper.py`) |
| Muse Capital | `musecapital_companies.json` | 41 | musecapital.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`musecapital_scraper.py`) |
| Baukunst | `baukunst_companies.json` | 39 | baukunst.co/investments — portfolio page: company name (site-authored heading/label text) and website where linked. (`baukunst_scraper.py`) |
| Muirwoods Ventures | `muirwoodsventures_companies.json` | 38 | muirwoodsvc.com — portfolio page: company name (site-authored logo alt) and website where linked. (`muirwoodsventures_scraper.py`) |
| Hivemind Ventures | `hivemindventuresllc_companies.json` | 34 | hivemind.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`hivemindventuresllc_scraper.py`) |
| Solari Capital | `solaricapital_companies.json` | 32 | solaricap.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`solaricapital_scraper.py`) |
| Seae Ventures | `seaeventures_companies.json` | 33 | seaeventures.com/portfolio/bloomwell-behavioral-health — portfolio page: company name (site-authored heading/label text) and website where linked. (`seaeventures_scraper.py`) |
| 13books Capital | `13bookscapital_companies.json` | 30 | 13bookscapital.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`13bookscapital_scraper.py`) |
| Render Capital | `rendercapital_companies.json` | 30 | render.capital — portfolio page: company name (site-authored logo alt) and website where linked. (`rendercapital_scraper.py`) |
| NAV.VC | `navvc_companies.json` | 29 | nav.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`navvc_scraper.py`) |
| Accord Ventures | `accordventures_companies.json` | 27 | accordventures.co.jp/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`accordventures_scraper.py`) |
| Windrose Capital | `windrosecapital_companies.json` | 27 | windrose.capital/Portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`windrosecapital_scraper.py`) |
| Optic Capital | `opticcapital_companies.json` | 26 | optic.capital/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`opticcapital_scraper.py`) |
| Marram Ventures | `marramventures_companies.json` | 25 | marram.vc — portfolio page: company name (site-authored logo alt) and website where linked. (`marramventures_scraper.py`) |
| Inspiration Ventures | `inspirationventures_companies.json` | 26 | inspirationvc.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`inspirationventures_scraper.py`) |
| Xeed Ventures | `xeedventures_companies.json` | 23 | xeed.vc/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`xeedventures_scraper.py`) |
| Valo Ventures | `valoventures_companies.json` | 25 | valoventures.org/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`valoventures_scraper.py`) |
| Tyche Partners | `tychepartners_companies.json` | 24 | tychepartners.com — portfolio page: company name (site-authored logo alt) and website where linked. (`tychepartners_scraper.py`) |
| Privilège Ventures | `privilgeventures_companies.json` | 26 | privilege-ventures.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`privilgeventures_scraper.py`) |
| ON&BOARD | `onboard_companies.json` | 25 | onboardvc.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`onboard_scraper.py`) |
| Treeo VC | `treeovc_companies.json` | 25 | treeo.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`treeovc_scraper.py`) |
| Semilla Ventures | `semillaventures_companies.json` | 26 | semilla.ventures/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`semillaventures_scraper.py`) |
| Midnight | `midnight_companies.json` | 24 | midnightvp.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`midnight_scraper.py`) |
| Daft Capital | `daftcapital_companies.json` | 25 | daftcapital.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`daftcapital_scraper.py`) |
| CSA Partners | `csapartnersllc_companies.json` | 24 | csapartners.com/investments — portfolio page: company name (site-authored logo alt) and website where linked. (`csapartnersllc_scraper.py`) |
| Creator Ventures | `creatorventures_companies.json` | 25 | creator.ventures — portfolio page: company name (site-authored heading/label text) and website where linked. (`creatorventures_scraper.py`) |
| Aura Ventures | `auraventures_companies.json` | 24 | aura.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`auraventures_scraper.py`) |
| Amplifica Capital | `amplificacapital_companies.json` | 24 | amplifica.capital/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`amplificacapital_scraper.py`) |
| SciFi VC | `scifivc_companies.json` | 25 | scifi.vc — portfolio page: company name (site-authored logo alt) and website where linked. (`scifivc_scraper.py`) |
| Nabventures | `nabventures_companies.json` | 22 | nabventures.in/portfolio-companies.aspx — portfolio page: company name (site-authored logo alt) and website where linked. (`nabventures_scraper.py`) |
| Chakra Growth Fund | `chakragrowthfund_companies.json` | 24 | chakragrowthcapital.com/portfolio.html — portfolio page: company name (site-authored heading/label text) and website where linked. (`chakragrowthfund_scraper.py`) |
| Hike Capital | `hikecapital_companies.json` | 21 | hikecapital.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`hikecapital_scraper.py`) |
| Ethos VC | `ethosvc_companies.json` | 22 | ethos.vc/portfolio — portfolio page: company name (site-authored link text) and website where linked. (`ethosvc_scraper.py`) |
| DigiTx Partners | `digitxpartnersllc_companies.json` | 22 | digitxpartners.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`digitxpartnersllc_scraper.py`) |
| Chartline Capital Partners | `chartlinecapitalpartners_companies.json` | 22 | chartline.com/companies.html — portfolio page: company name (site-authored logo alt) and website where linked. (`chartlinecapitalpartners_scraper.py`) |
| Beat Ventures | `beatventures_companies.json` | 22 | beatventures.com/portfolio-1 — portfolio page: company name (site-authored heading/label text) and website where linked. (`beatventures_scraper.py`) |
| Alante Capital | `alantecapital_companies.json` | 22 | alantecapital.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`alantecapital_scraper.py`) |
| 97212 Ventures | `97212ventures_companies.json` | 21 | 97212.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`97212ventures_scraper.py`) |
| Reverie | `reverie_companies.json` | 21 | reverie.ooo/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`reverie_scraper.py`) |
| Oval Park Capital | `ovalparkcapital_companies.json` | 20 | ovalpark.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`ovalparkcapital_scraper.py`) |
| Long Venture Partners | `longventurepartners_companies.json` | 20 | longvp.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`longventurepartners_scraper.py`) |
| Cloquet Capital Partners | `cloquetcapitalpartnersll_companies.json` | 21 | cloquetcapital.com/portfolio.html — portfolio page: company name (site-authored heading/label text) and website where linked. (`cloquetcapitalpartnersll_scraper.py`) |
| age1 | `age1_companies.json` | 21 | age1.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`age1_scraper.py`) |
| Vesalius Biocapital Partners | `vesaliusbiocapitalpartne_companies.json` | 20 | vesaliusbiocapital.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`vesaliusbiocapitalpartne_scraper.py`) |
| Starship Ventures | `starshipventures_companies.json` | 20 | starship.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`starshipventures_scraper.py`) |
| Spiral Sun Ventures | `spiralsunventures_companies.json` | 19 | spiralsunventures.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`spiralsunventures_scraper.py`) |
| Signature Ventures | `signatureventures_companies.json` | 20 | signatureventures.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`signatureventures_scraper.py`) |
| MiH Ventures | `mihventures_companies.json` | 21 | mih.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`mihventures_scraper.py`) |
| Impetus Capital | `impetuscapital_companies.json` | 20 | impetus.capital — portfolio page: company name (site-authored heading/label text) and website where linked. (`impetuscapital_scraper.py`) |
| GOAL Ventures | `goalventures_companies.json` | 22 | goalventurepartners.com/companies — portfolio page: company name (site-authored heading/label text) and website where linked. (`goalventures_scraper.py`) |
| Cove Fund | `covefund_companies.json` | 20 | covefund.com/investments-cfi — portfolio page: company name (site-authored heading/label text) and website where linked. (`covefund_scraper.py`) |
| Aurelia Foundry | `aureliafoundry_companies.json` | 21 | aureliafoundry.com — portfolio page: company name (site-authored link text) and website where linked. (`aureliafoundry_scraper.py`) |
| ACVC Partners | `acvcpartners_companies.json` | 20 | acvc.partners/portfoliocos — portfolio page: company name (site-authored heading/label text) and website where linked. (`acvcpartners_scraper.py`) |
| VC 414 | `vc414_companies.json` | 19 | vc414.com/our-portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`vc414_scraper.py`) |
| Skywood Capital | `skywoodcapital_companies.json` | 20 | skywoodcapital.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`skywoodcapital_scraper.py`) |
| Sentiero Ventures | `sentieroventures_companies.json` | 19 | sentiero.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`sentieroventures_scraper.py`) |
| Saturn Partners | `saturnpartners_companies.json` | 20 | saturnpartnersvc.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`saturnpartners_scraper.py`) |
| Leaders Fund | `leadersfund_companies.json` | 17 | leaders.vc — portfolio page: company name (site-authored logo alt) and website where linked. (`leadersfund_scraper.py`) |
| FemHealth Ventures | `femhealthventures_companies.json` | 20 | femhealthventures.com/portfolio2 — portfolio page: company name (site-authored heading/label text) and website where linked. (`femhealthventures_scraper.py`) |
| InHealth Ventures | `inhealthventures_companies.json` | 18 | inhealth.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`inhealthventures_scraper.py`) |
| Citta Capital | `cittacapital_companies.json` | 18 | cittacapital.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`cittacapital_scraper.py`) |
| Cade Ventures | `cadeventures_companies.json` | 17 | cadeventure.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`cadeventures_scraper.py`) |
| Brave Capital | `bravecapital_companies.json` | 18 | bravecap.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`bravecapital_scraper.py`) |
| Anthropy Partners | `anthropypartners_companies.json` | 18 | anthropypartners.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`anthropypartners_scraper.py`) |
| Shoreline Venture Management | `shorelineventuremanageme_companies.json` | 18 | shorelineventures.com/portfolio/#other — portfolio page: company name (site-authored logo alt) and website where linked. (`shorelineventuremanageme_scraper.py`) |
| Onsight Ventures | `onsightventures_companies.json` | 18 | onsight.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`onsightventures_scraper.py`) |
| Category Ventures | `categoryventures_companies.json` | 16 | categoryvc.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`categoryventures_scraper.py`) |
| Bloc Ventures | `blocventures_companies.json` | 17 | blocventures.com/our-portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`blocventures_scraper.py`) |
| Targeted Technology Funds | `targetedtechnologyfunds_companies.json` | 17 | targetedtech.com/portfolio.html — portfolio page: company name (site-authored heading/label text) and website where linked. (`targetedtechnologyfunds_scraper.py`) |
| Cardinia Ventures | `cardiniaventures_companies.json` | 16 | cardiniaventures.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`cardiniaventures_scraper.py`) |
| Clover Vitality | `clovervitality_companies.json` | 15 | clovervitality.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`clovervitality_scraper.py`) |
| Two Ravens | `tworavens_companies.json` | 11 | tworavens.vc — portfolio page: company name (site-authored heading/label text) and website where linked. (`tworavens_scraper.py`) |
| Blue Hour Ventures | `bluehourventures_companies.json` | 15 | bluehour.ventures — portfolio page: company name (site-authored heading/label text) and website where linked. (`bluehourventures_scraper.py`) |
| ETFS Capital | `etfscapital_companies.json` | 17 | etfscapital.com/companies — portfolio page: company name (site-authored heading/label text) and website where linked. (`etfscapital_scraper.py`) |
| ExSight Ventures | `exsightventures_companies.json` | 13 | exsightventures.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`exsightventures_scraper.py`) |
| ZBS CAPITAL | `zbscapital_companies.json` | 12 | zbs.capital/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`zbscapital_scraper.py`) |
| Jerusalem Global Ventures | `jerusalemglobalventures_companies.json` | 16 | jgv.com — portfolio page: company name (site-authored link text) and website where linked. (`jerusalemglobalventures_scraper.py`) |
| Think+ Ventures | `thinkventuresmanagementl_companies.json` | 60 | thinkplus.vc — portfolio page: company name (site-authored logo alt) and website where linked. (`thinkventuresmanagementl_scraper.py`) |
| DIMENSION | `dimension_companies.json` | 62 | dimensionfund.co.jp/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`dimension_scraper.py`) |
| Stepchange | `stepchange_companies.json` | 22 | stepchange.vc/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`stepchange_scraper.py`) |
| IDEO CoLab Ventures | `ideocolabventures_companies.json` | 34 | ideocolab.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`ideocolabventures_scraper.py`) |
| Polytechnique Ventures | `polytechniqueventures_companies.json` | 23 | polytechnique-ventures.fr/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`polytechniqueventures_scraper.py`) |
| Tamarisc Ventures | `tamariscventures_companies.json` | 23 | tamarisc.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`tamariscventures_scraper.py`) |
| Lanai | `lanai_companies.json` | 63 | lanai.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`lanai_scraper.py`) |
| Locus Ventures | `locusventures_companies.json` | 58 | locus.vc — portfolio page: company name (site-authored heading/label text) and website where linked. (`locusventures_scraper.py`) |
| Vox Capital | `voxcapital_companies.json` | 41 | voxcapital.com.br/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`voxcapital_scraper.py`) |
| Global Hands-On VC | `globalhandsonvc_companies.json` | 39 | ghovc.com/ja/investment — portfolio page: company name (site-authored heading/label text) and website where linked. (`globalhandsonvc_scraper.py`) |
| Rabbit Ventures | `rabbitventures_companies.json` | 35 | rabbitvc.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`rabbitventures_scraper.py`) |
| Signia Venture Partners | `signiaventurepartners_companies.json` | 36 | signiaventurepartners.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`signiaventurepartners_scraper.py`) |
| Tioga Capital Partners | `tiogacapitalpartners_companies.json` | 28 | tioga.capital/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`tiogacapitalpartners_scraper.py`) |
| Red Dog Capital | `reddogcapital_companies.json` | 27 | reddogcap.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`reddogcapital_scraper.py`) |
| Ravelin Capital | `ravelincapital_companies.json` | 23 | ravelincap.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`ravelincapital_scraper.py`) |
| Middleland Capital | `middlelandcapital_companies.json` | 26 | middlelandcapital.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`middlelandcapital_scraper.py`) |
| Grid Capital | `gridcapital_companies.json` | 24 | gridcap.com/investments — portfolio page: company name (site-authored heading/label text) and website where linked. (`gridcapital_scraper.py`) |
| Miramar Venture Partners | `miramarventurepartners_companies.json` | 21 | miramarvp.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`miramarventurepartners_scraper.py`) |
| Pender Ventures | `penderventures_companies.json` | 20 | penderventures.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`penderventures_scraper.py`) |
| New North Ventures | `newnorthventures_companies.json` | 20 | newnorthvc.com — portfolio page: company name (site-authored logo alt) and website where linked. (`newnorthventures_scraper.py`) |
| Xandex Ventures | `xandexventures_companies.json` | 21 | xandexventures.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`xandexventures_scraper.py`) |
| Transition VC | `transitionvc_companies.json` | 19 | transitionventurecapital.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`transitionvc_scraper.py`) |
| Freigeist Capital | `freigeistcapital_companies.json` | 20 | freigeist.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`freigeistcapital_scraper.py`) |
| Curitas Ventures | `curitasventures_companies.json` | 20 | curitasventures.com — portfolio page: company name (site-authored logo alt) and website where linked. (`curitasventures_scraper.py`) |
| Clearance Venture Partners | `clearanceventurepartners_companies.json` | 17 | clearancevp.com — portfolio page: company name (site-authored link text) and website where linked. (`clearanceventurepartners_scraper.py`) |
| EFung Capital | `efungcapital_companies.json` | 74 | efungcapital.com — portfolio page: company name (site-authored logo alt) and website where linked. (`efungcapital_scraper.py`) |
| Wocstar Capital | `wocstarcapital_companies.json` | 11 | wocstar.com — portfolio page: company name (site-authored logo alt) and website where linked. (`wocstarcapital_scraper.py`) |
| Gaia Ventures | `gaiaventures_companies.json` | 15 | gaiavc.co — portfolio page: company name (site-authored logo alt) and website where linked. (`gaiaventures_scraper.py`) |
| Ballpark Ventures | `ballparkventures_companies.json` | 19 | ballparkventures.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`ballparkventures_scraper.py`) |
| Ankaa Ventures | `ankaaventures_companies.json` | 20 | ankaa.ventures — portfolio page: company name (site-authored heading/label text) and website where linked. (`ankaaventures_scraper.py`) |
| Agaeti Ventures | `agaetiventures_companies.json` | 20 | agaeti.vc — portfolio page: company name (site-authored heading/label text) and website where linked. (`agaetiventures_scraper.py`) |
| Villhard Growth Partners | `villhardgrowthpartners_companies.json` | 19 | villhardgrowth.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`villhardgrowthpartners_scraper.py`) |
| Urania Ventures | `uraniaventures_companies.json` | 19 | urania.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`uraniaventures_scraper.py`) |
| Steel Atlas | `steelatlas_companies.json` | 19 | steelatlas.vc — portfolio page: company name (site-authored heading/label text) and website where linked. (`steelatlas_scraper.py`) |
| Parceiro Ventures | `parceiroventures_companies.json` | 18 | parceiroventures.com — portfolio page: company name (site-authored logo alt) and website where linked. (`parceiroventures_scraper.py`) |
| Linse Capital | `linsecapital_companies.json` | 19 | linsecapital.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`linsecapital_scraper.py`) |
| Factorial Funds | `factorialfunds_companies.json` | 19 | factorialfunds.com/investments — portfolio page: company name (site-authored logo alt) and website where linked. (`factorialfunds_scraper.py`) |
| Excelerate Health Ventures | `exceleratehealthventures_companies.json` | 19 | exceleratehealth.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`exceleratehealthventures_scraper.py`) |
| Seaplane Ventures | `seaplaneventures_companies.json` | 17 | seaplaneventures.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`seaplaneventures_scraper.py`) |
| Prevail Venture Capital | `prevailventurecapital_companies.json` | 16 | prevailventurecapital.com — portfolio page: company name (site-authored logo alt) and website where linked. (`prevailventurecapital_scraper.py`) |
| Prediction Capital | `predictioncapital_companies.json` | 18 | predictioncapital.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`predictioncapital_scraper.py`) |
| Novalis LifeSciences | `novalislifesciences_companies.json` | 18 | novalislifesciences.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`novalislifesciences_scraper.py`) |
| Newton Biocapital | `newtonbiocapital_companies.json` | 18 | newtonbiocapital.com/en/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`newtonbiocapital_scraper.py`) |
| Antigravity Capital | `antigravitycapital_companies.json` | 18 | antigravity.capital/companies — portfolio page: company name (site-authored heading/label text) and website where linked. (`antigravitycapital_scraper.py`) |
| Verb Ventures | `verbventures_companies.json` | 16 | verb.ventures/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`verbventures_scraper.py`) |
| Reflexive Capital | `reflexivecapital_companies.json` | 17 | reflexive.xyz — portfolio page: company name (site-authored heading/label text) and website where linked. (`reflexivecapital_scraper.py`) |
| Nazare Ventures | `nazareventures_companies.json` | 17 | nazare.io — portfolio page: company name (site-authored heading/label text) and website where linked. (`nazareventures_scraper.py`) |
| Intonation Ventures | `intonationventures_companies.json` | 17 | intonationventures.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`intonationventures_scraper.py`) |
| Flex Capital Partners | `flexcapitalpartners_companies.json` | 19 | flexcapital.com — portfolio page: company name (site-authored logo alt) and website where linked. (`flexcapitalpartners_scraper.py`) |
| Camp One Ventures | `camponeventures_companies.json` | 16 | camponeventures.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`camponeventures_scraper.py`) |
| Bettor Capital | `bettorcapital_companies.json` | 16 | bettorcapital.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`bettorcapital_scraper.py`) |
| Triatomic Capital | `triatomiccapital_companies.json` | 15 | triatomic.ai — portfolio page: company name (site-authored logo alt) and website where linked. (`triatomiccapital_scraper.py`) |
| Leitmotif | `leitmotif_companies.json` | 16 | leitmotif.vc — portfolio page: company name (site-authored heading/label text) and website where linked. (`leitmotif_scraper.py`) |
| Innospark Ventures | `innosparkventures_companies.json` | 16 | innospark.vc/portfolio-category/enterprise — portfolio page: company name (site-authored heading/label text) and website where linked. (`innosparkventures_scraper.py`) |
| Even Capital | `evencapital_companies.json` | 18 | evencapital.nz/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`evencapital_scraper.py`) |
| Callapina Capital | `callapinacapital_companies.json` | 16 | callapina.com/angel-portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`callapinacapital_scraper.py`) |
| WXR Fund | `wxrfund_companies.json` | 14 | wxrfund.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`wxrfund_scraper.py`) |
| Vocal Ventures | `vocalventures_companies.json` | 15 | vocalventures.co — portfolio page: company name (site-authored heading/label text) and website where linked. (`vocalventures_scraper.py`) |
| Sadu Capital | `saducapital_companies.json` | 13 | sadu.vc/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`saducapital_scraper.py`) |
| NGEN Partners | `ngenpartners_companies.json` | 15 | ngenpartners.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`ngenpartners_scraper.py`) |
| Longley Capital | `longleycapital_companies.json` | 16 | longleycapital.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`longleycapital_scraper.py`) |
| Gigafund | `gigafund_companies.json` | 18 | gigafund.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`gigafund_scraper.py`) |
| Daybreak Partners | `daybreakpartners_companies.json` | 15 | daybreakpartners.com/our-investment — portfolio page: company name (site-authored heading/label text) and website where linked. (`daybreakpartners_scraper.py`) |
| Bronze Investments | `bronzeinvestments_companies.json` | 15 | bronze.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`bronzeinvestments_scraper.py`) |
| ZORA | `zora_companies.json` | 15 | zora.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`zora_scraper.py`) |
| Xploration Capital | `xplorationcapital_companies.json` | 14 | xplorationcapital.com/our-portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`xplorationcapital_scraper.py`) |
| Thursday Ventures | `thursdayventures_companies.json` | 18 | thursday.xyz — portfolio page: company name (site-authored link text) and website where linked. (`thursdayventures_scraper.py`) |
| Stellifi | `stellifi_companies.json` | 14 | stellifivc.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`stellifi_scraper.py`) |
| SPiCE VC | `spicevc_companies.json` | 14 | spicevc.com/portfolio.html — portfolio page: company name (site-authored logo alt) and website where linked. (`spicevc_scraper.py`) |
| Eastend Ventures | `eastendventures_companies.json` | 15 | eastend.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`eastendventures_scraper.py`) |
| Carbon Silicon | `carbonsilicon_companies.json` | 13 | carbonsilicon.vc — portfolio page: company name (site-authored link text) and website where linked. (`carbonsilicon_scraper.py`) |
| BreakOrbit | `breakorbit_companies.json` | 14 | breakorbit.vc — portfolio page: company name (site-authored heading/label text) and website where linked. (`breakorbit_scraper.py`) |
| The SidebySide Partnership | `thesidebysidepartnership_companies.json` | 13 | thesidebysidepartnership.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`thesidebysidepartnership_scraper.py`) |
| Sanctor Capital | `sanctorcapital_companies.json` | 14 | sanctor.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`sanctorcapital_scraper.py`) |
| Rhinevall Capital | `rhinevallcapital_companies.json` | 12 | rhinevall.capital — portfolio page: company name (site-authored logo alt) and website where linked. (`rhinevallcapital_scraper.py`) |
| Kuorrokveik Adventure Capital | `kuorrokveikadventurecapi_companies.json` | 12 | adventurecapital.se/investments — portfolio page: company name (site-authored logo alt) and website where linked. (`kuorrokveikadventurecapi_scraper.py`) |
| Interlock Partners | `interlockpartners_companies.json` | 12 | interlock.vc — portfolio page: company name (site-authored logo alt) and website where linked. (`interlockpartners_scraper.py`) |
| GOVO Venture Partners | `govoventurepartners_companies.json` | 12 | govovp.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`govoventurepartners_scraper.py`) |
| Crypto Discover | `cryptodiscover_companies.json` | 14 | cryptodiscover.io — portfolio page: company name (site-authored heading/label text) and website where linked. (`cryptodiscover_scraper.py`) |
| Vickers Venture Partners | `vickersventurepartners_companies.json` | 12 | vickersventure.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`vickersventurepartners_scraper.py`) |
| Team Ignite Ventures | `teamigniteventures_companies.json` | 12 | teamignite.vc — portfolio page: company name (site-authored logo alt) and website where linked. (`teamigniteventures_scraper.py`) |
| Overeasy Ventures | `overeasyventures_companies.json` | 12 | overeasyventures.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`overeasyventures_scraper.py`) |
| 2050 Capital | `2050capital_companies.json` | 12 | 2050cap.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`2050capital_scraper.py`) |
| What If Ventures | `whatifventures_companies.json` | 12 | whatif.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`whatifventures_scraper.py`) |
| Tin Alley Ventures | `tinalleyventures_companies.json` | 12 | tinalleyventures.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`tinalleyventures_scraper.py`) |
| Stratified Capital | `stratifiedcapital_companies.json` | 17 | stratified.capital — portfolio page: company name (site-authored heading/label text) and website where linked. (`stratifiedcapital_scraper.py`) |
| Dynamism Capital | `dynamismcapital_companies.json` | 12 | dynamism.capital — portfolio page: company name (site-authored logo alt) and website where linked. (`dynamismcapital_scraper.py`) |
| Kesha Ventures | `keshaventures_companies.json` | 14 | keshaventures.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`keshaventures_scraper.py`) |
| Island Capital | `islandcapital_companies.json` | 15 | islandcapital.vc — portfolio page: company name (site-authored heading/label text) and website where linked. (`islandcapital_scraper.py`) |
| GAA Investments | `gaainvestments_companies.json` | 14 | gaainvestments.com/en — portfolio page: company name (site-authored heading/label text) and website where linked. (`gaainvestments_scraper.py`) |
| Unbounded Capital | `unboundedcapital_companies.json` | 12 | unboundedcapital.com/our-portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`unboundedcapital_scraper.py`) |
| Multifaceted Capital | `multifacetedcapital_companies.json` | 12 | multifaceted.capital — portfolio page: company name (site-authored heading/label text) and website where linked. (`multifacetedcapital_scraper.py`) |
| Encomenda VC | `encomendavc_companies.json` | 12 | encomenda.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`encomendavc_scraper.py`) |
| MSW Ventures | `mswventures_companies.json` | 12 | mettlesaltwealth.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`mswventures_scraper.py`) |
| Brace Pharma | `bracepharma_companies.json` | 11 | bracepharma.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`bracepharma_scraper.py`) |
| First Rays Venture Partners | `firstraysventurepartners_companies.json` | 15 | firstraysvc.com — portfolio page: company name (site-authored logo alt) and website where linked. (`firstraysventurepartners_scraper.py`) |
| aws Gründungsfonds | `awsgrndungsfonds_companies.json` | 55 | gruendungsfonds.at/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`awsgrndungsfonds_scraper.py`) |
| o2h Ventures | `o2hventures_companies.json` | 43 | o2hventures.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`o2hventures_scraper.py`) |
| ABCDE Capital | `abcdecapital_companies.json` | 35 | abcde.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`abcdecapital_scraper.py`) |
| Capital Today | `capitaltoday_companies.json` | 33 | capitaltoday.com/portfolios — portfolio page: company name (site-authored logo alt) and website where linked. (`capitaltoday_scraper.py`) |
| Green Bay Ventures | `greenbayventures_companies.json` | 30 | greenbayventures.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`greenbayventures_scraper.py`) |
| VitalStage Ventures | `vitalstageventures_companies.json` | 22 | vitalstage.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`vitalstageventures_scraper.py`) |
| Provence Partners | `provencepartners_companies.json` | 16 | provencepartners.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`provencepartners_scraper.py`) |
| DGF | `dgf_companies.json` | 14 | dgf.com.br — portfolio page: company name (site-authored heading/label text) and website where linked. (`dgf_scraper.py`) |
| Ensemble VC | `ensemblevc_companies.json` | 12 | ensemble.vc/company/chaos-industries — portfolio page: company name (site-authored heading/label text) and website where linked. (`ensemblevc_scraper.py`) |
| HCS Capital | `hcscapital_companies.json` | 11 | hcscapital.com/companies — portfolio page: company name (site-authored heading/label text) and website where linked. (`hcscapital_scraper.py`) |
| BIP32 Venture | `bip32venture_companies.json` | 14 | bip32.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`bip32venture_scraper.py`) |
| Strange Ventures | `strangeventures_companies.json` | 11 | strangevc.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`strangeventures_scraper.py`) |
| Palette Ventures | `paletteventures_companies.json` | 21 | palettevc.com — portfolio page: company name (site-authored link text) and website where linked. (`paletteventures_scraper.py`) |
| Ventura BioMed Investors | `venturabiomedinvestors_companies.json` | 16 | ventura-biomed.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`venturabiomedinvestors_scraper.py`) |
| Pure Ventures | `pureventures_companies.json` | 23 | pureventuresvc.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`pureventures_scraper.py`) |
| 8090 Industries | `8090industries_companies.json` | 30 | 8090industries.com/companies — portfolio page: company name (site-authored logo alt) and website where linked. (`8090industries_scraper.py`) |
| Avalon BioVentures | `avalonbioventures_companies.json` | 16 | avalonbioventures.com — portfolio page: company name (site-authored logo alt) and website where linked. (`avalonbioventures_scraper.py`) |
| Calculus Capital | `calculuscapitalltd_companies.json` | 38 | calculuscapital.com/investment/laverock-therapeutics — portfolio page: company name (site-authored heading/label text) and website where linked. (`calculuscapitalltd_scraper.py`) |
| Astir Ventures | `astirventures_companies.json` | 475 | astir.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`astirventures_scraper.py`) |
| Rainfall Ventures | `rainfallventures_companies.json` | 112 | rainfall.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`rainfallventures_scraper.py`) |
| IBB Ventures | `ibbventures_companies.json` | 100 | ibbventures.de/en/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`ibbventures_scraper.py`) |
| SixThirty Ventures | `sixthirtyventures_companies.json` | 99 | sixthirty.co/startup-portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`sixthirtyventures_scraper.py`) |
| AQC Capital | `aqccapital_companies.json` | 79 | aqccapital.ca/portfolio/?lang=en — portfolio page: company name (site-authored heading/label text) and website where linked. (`aqccapital_scraper.py`) |
| Comma3 Ventures | `comma3ventures_companies.json` | 70 | comma3.co/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`comma3ventures_scraper.py`) |
| Spot VC | `spotvc_companies.json` | 69 | spot.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`spotvc_scraper.py`) |
| Media Ventures | `mediaventuresgmbh_companies.json` | 69 | mediaventures.de/index.php/startseite.html — portfolio page: company name (site-authored heading/label text) and website where linked. (`mediaventuresgmbh_scraper.py`) |
| Four Rivers Group | `fourriversgroup_companies.json` | 66 | fourriversgroup.com/m/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`fourriversgroup_scraper.py`) |
| Sugar Capital | `sugarcapital_companies.json` | 63 | sugarcap.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`sugarcapital_scraper.py`) |
| SignalRank | `signalrank_companies.json` | 61 | signalrank.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`signalrank_scraper.py`) |
| FunFair Ventures | `funfairventures_companies.json` | 58 | funfair.ventures — portfolio page: company name (site-authored heading/label text) and website where linked. (`funfairventures_scraper.py`) |
| Anti Fund | `antifundvc_companies.json` | 56 | antifund.com — portfolio page: company name (site-authored link text) and website where linked. (`antifundvc_scraper.py`) |
| TDF Ventures | `tdfventures_companies.json` | 56 | tdfventures.com/companies — portfolio page: company name (site-authored heading/label text) and website where linked. (`tdfventures_scraper.py`) |
| Cofounders Capital | `cofounderscapital_companies.json` | 53 | cofounderscapital.com/companies — portfolio page: company name (site-authored heading/label text) and website where linked. (`cofounderscapital_scraper.py`) |
| Magna Investment | `magnainvestment_companies.json` | 50 | mgni.co.kr — portfolio page: company name (site-authored logo alt) and website where linked. (`magnainvestment_scraper.py`) |
| Innovation Nest | `innovationnest_companies.json` | 47 | innovationnest.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`innovationnest_scraper.py`) |
| 99 Startups | `99startups_companies.json` | 47 | 99startups.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`99startups_scraper.py`) |
| Hawk Hill Ventures | `hawkhillventures_companies.json` | 46 | hawkhill.vc/investments — portfolio page: company name (site-authored heading/label text) and website where linked. (`hawkhillventures_scraper.py`) |
| Active Impact Investments | `activeimpactinvestments_companies.json` | 45 | activeimpactinvestments.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`activeimpactinvestments_scraper.py`) |
| Cycle Capital | `cyclecapital_companies.json` | 45 | cyclecapital.com/investissement-2 — portfolio page: company name (site-authored heading/label text) and website where linked. (`cyclecapital_scraper.py`) |
| Quantumlight Capital | `quantumlightcapital_companies.json` | 43 | quantumlightcapital.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`quantumlightcapital_scraper.py`) |
| Formic Ventures | `formicventures_companies.json` | 42 | formic.vc/investments.html — portfolio page: company name (site-authored heading/label text) and website where linked. (`formicventures_scraper.py`) |
| Pack Ventures | `packventures_companies.json` | 42 | packvc.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`packventures_scraper.py`) |
| APEX Ventures | `apexventures_companies.json` | 42 | apex.ventures/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`apexventures_scraper.py`) |
| Stakez Capital | `stakezcapital_companies.json` | 41 | stakez.capital — portfolio page: company name (site-authored logo alt) and website where linked. (`stakezcapital_scraper.py`) |
| 0BS | `0bs_companies.json` | 39 | 0bs.mx — portfolio page: company name (site-authored logo alt) and website where linked. (`0bs_scraper.py`) |
| Acacia Venture Capital Partners | `acaciaventurecapitalpart_companies.json` | 36 | acaciainvest.com/portfolio.html — portfolio page: company name (site-authored heading/label text) and website where linked. (`acaciaventurecapitalpart_scraper.py`) |
| GBS Venture Partners | `gbsventurepartnersltd_companies.json` | 34 | gbsventures.com.au/portfolio-companies — portfolio page: company name (site-authored link text) and website where linked. (`gbsventurepartnersltd_scraper.py`) |
| Core91.vc | `core91vc_companies.json` | 33 | core91.vc — portfolio page: company name (site-authored logo alt) and website where linked. (`core91vc_scraper.py`) |
| Dangerous Ventures | `dangerousventures_companies.json` | 33 | dangerous.co — portfolio page: company name (site-authored logo alt) and website where linked. (`dangerousventures_scraper.py`) |
| Tenzor Capital | `tenzorcapital_companies.json` | 33 | tenzor.capital — portfolio page: company name (site-authored heading/label text) and website where linked. (`tenzorcapital_scraper.py`) |
| Asymmetric | `asymmetric_companies.json` | 32 | asymmetric.financial — portfolio page: company name (site-authored logo alt) and website where linked. (`asymmetric_scraper.py`) |
| BFG Partners | `bfgpartners_companies.json` | 32 | bfgpartners.com — portfolio page: company name (site-authored logo alt) and website where linked. (`bfgpartners_scraper.py`) |
| Slingshot Ventures | `slingshotventures_companies.json` | 32 | slingshot.ventures/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`slingshotventures_scraper.py`) |
| Breed VC | `breedvc_companies.json` | 32 | breed.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`breedvc_scraper.py`) |
| Breakpoint Capital | `breakpointcapital_companies.json` | 32 | breakpointcap.com — portfolio page: company name (site-authored logo alt) and website where linked. (`breakpointcapital_scraper.py`) |
| Leap Forward Ventures | `leapforwardventures_companies.json` | 31 | leapforward.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`leapforwardventures_scraper.py`) |
| Fireroad Ventures | `fireroadventures_companies.json` | 30 | fireroad.io/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`fireroadventures_scraper.py`) |
| Aroa Venture Partners | `aroaventurepartners_companies.json` | 30 | aroaventures.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`aroaventurepartners_scraper.py`) |
| Morningstar Ventures | `morningstarventures_companies.json` | 30 | morningstar.ventures — portfolio page: company name (site-authored heading/label text) and website where linked. (`morningstarventures_scraper.py`) |
| Mobility Ventures | `mobilityventures_companies.json` | 30 | mobilityventures.com/companies-article — portfolio page: company name (site-authored heading/label text) and website where linked. (`mobilityventures_scraper.py`) |
| Fall Line Capital | `falllinecapital_companies.json` | 29 | fall-line-capital.com/venture — portfolio page: company name (site-authored logo alt) and website where linked. (`falllinecapital_scraper.py`) |
| Great Circle Ventures | `greatcircleventures_companies.json` | 29 | greatcircle.vc — portfolio page: company name (site-authored logo alt) and website where linked. (`greatcircleventures_scraper.py`) |
| Grant Park Ventures | `grantparkventures_companies.json` | 29 | grantparkventures.com — portfolio page: company name (site-authored logo alt) and website where linked. (`grantparkventures_scraper.py`) |
| Eindhoven Venture Capital | `eindhovenventurecapital_companies.json` | 27 | ecfg.nl/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`eindhovenventurecapital_scraper.py`) |
| Formulate Ventures | `formulateventures_companies.json` | 27 | formulateventures.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`formulateventures_scraper.py`) |
| Venture to Future Fund | `venturetofuturefund_companies.json` | 26 | vff.sk — portfolio page: company name (site-authored logo alt) and website where linked. (`venturetofuturefund_scraper.py`) |
| Brain-Too-Free Ventures | `braintoofreeventures_companies.json` | 26 | btfv.vc — portfolio page: company name (site-authored link text) and website where linked. (`braintoofreeventures_scraper.py`) |
| Futury Capital | `futurycapital_companies.json` | 26 | futurycapital.vc — portfolio page: company name (site-authored heading/label text) and website where linked. (`futurycapital_scraper.py`) |
| SWC Global | `swcglobal_companies.json` | 26 | swcglobal.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`swcglobal_scraper.py`) |
| Kalei Ventures | `kaleiventures_companies.json` | 25 | kaleiventures.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`kaleiventures_scraper.py`) |
| Prequel Ventures | `prequelventures_companies.json` | 25 | prequelvc.com — portfolio page: company name (site-authored logo alt) and website where linked. (`prequelventures_scraper.py`) |
| Thuja Capital | `thujacapital_companies.json` | 24 | thujacapital.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`thujacapital_scraper.py`) |
| LUN Partners Group | `lunpartnersgroup_companies.json` | 24 | lunpartners.com/en/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`lunpartnersgroup_scraper.py`) |
| Socially Financed | `sociallyfinanced_companies.json` | 24 | sociallyfinanced.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`sociallyfinanced_scraper.py`) |
| SymBiosis | `symbiosis_companies.json` | 23 | symbiosis.vc/investments — portfolio page: company name (site-authored heading/label text) and website where linked. (`symbiosis_scraper.py`) |
| Ondine Capital | `ondinecapital_companies.json` | 23 | ondinecap.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`ondinecapital_scraper.py`) |
| Blank Space Ventures | `blankspaceventures_companies.json` | 23 | blankspace.vc — portfolio page: company name (site-authored logo alt) and website where linked. (`blankspaceventures_scraper.py`) |
| Uma Ventures | `umaventures_companies.json` | 23 | uma.inc/portfolio.html — portfolio page: company name (site-authored heading/label text) and website where linked. (`umaventures_scraper.py`) |
| Lanchi Ventures | `lanchiventures_companies.json` | 22 | lanchiventures.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`lanchiventures_scraper.py`) |
| SpringCapital Investment | `springcapitalinvestment_companies.json` | 22 | springcapital.com.au — portfolio page: company name (site-authored heading/label text) and website where linked. (`springcapitalinvestment_scraper.py`) |
| Rumbo Ventures | `rumboventures_companies.json` | 22 | rumbo.ventures/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`rumboventures_scraper.py`) |
| MedMountain Ventures | `medmountainventures_companies.json` | 20 | mmv.vc — portfolio page: company name (site-authored logo alt) and website where linked. (`medmountainventures_scraper.py`) |
| Terpsi Capital | `terpsicapital_companies.json` | 20 | terpsicapital.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`terpsicapital_scraper.py`) |
| Monoceros | `monoceros_companies.json` | 20 | monoceros.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`monoceros_scraper.py`) |
| Clay Capital | `claycapital_companies.json` | 20 | claycapital.vc — portfolio page: company name (site-authored heading/label text) and website where linked. (`claycapital_scraper.py`) |
| ASIF Ventures | `asifventures_companies.json` | 20 | asif.ventures — portfolio page: company name (site-authored heading/label text) and website where linked. (`asifventures_scraper.py`) |
| SV Latam Fund | `svlatamfund_companies.json` | 20 | svlatamfund.co/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`svlatamfund_scraper.py`) |
| BRC Innovation | `brcinnovation_companies.json` | 20 | brainrobotcap.com — portfolio page: company name (site-authored logo alt) and website where linked. (`brcinnovation_scraper.py`) |
| Citrino Ventures | `citrinoventures_companies.json` | 19 | citrino.vc — portfolio page: company name (site-authored logo alt) and website where linked. (`citrinoventures_scraper.py`) |
| devlabs | `devlabs_companies.json` | 19 | devlabs.vc — portfolio page: company name (site-authored heading/label text) and website where linked. (`devlabs_scraper.py`) |
| SMO Capital | `smocapital_companies.json` | 19 | smocapital.net/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`smocapital_scraper.py`) |
| Laude Ventures | `laudeventures_companies.json` | 19 | laude.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`laudeventures_scraper.py`) |
| Alive Ventures | `aliveventures_companies.json` | 19 | alive-ventures.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`aliveventures_scraper.py`) |
| Wild Basin Investments | `wildbasininvestments_companies.json` | 18 | wildbasininv.com/selected-portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`wildbasininvestments_scraper.py`) |
| Veryearly Ventures | `veryearlyventures_companies.json` | 18 | veryearly.xyz — portfolio page: company name (site-authored logo alt) and website where linked. (`veryearlyventures_scraper.py`) |
| Metropolis VC | `metropolisvc_companies.json` | 17 | metropolis.vc — portfolio page: company name (site-authored link text) and website where linked. (`metropolisvc_scraper.py`) |
| First Ascent Ventures | `firstascentventures_companies.json` | 17 | firstascentventures.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`firstascentventures_scraper.py`) |
| Sandpiper Ventures | `sandpiperventures_companies.json` | 16 | sandpiper.vc/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`sandpiperventures_scraper.py`) |
| Open Circle Capital | `opencirclecapital_companies.json` | 16 | opencirclecapital.lt — portfolio page: company name (site-authored heading/label text) and website where linked. (`opencirclecapital_scraper.py`) |
| Zentynel Frontier Investments | `zentynelfrontierinvestme_companies.json` | 16 | zentynel.com/portafolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`zentynelfrontierinvestme_scraper.py`) |
| JSW Ventures | `jswventures_companies.json` | 16 | jswvc.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`jswventures_scraper.py`) |
| Fortitude Ventures | `fortitudeventures_companies.json` | 15 | fortitudevc.com — portfolio page: company name (site-authored link text) and website where linked. (`fortitudeventures_scraper.py`) |
| A-Force Ventures | `aforceventures_companies.json` | 15 | aforceventures.com — portfolio page: company name (site-authored logo alt) and website where linked. (`aforceventures_scraper.py`) |
| Venture Development Partners | `venturedevelopmentpartne_companies.json` | 15 | vdpartners.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`venturedevelopmentpartne_scraper.py`) |
| Sustainable Future Ventures | `sustainablefutureventure_companies.json` | 15 | sfv.vc — portfolio page: company name (site-authored heading/label text) and website where linked. (`sustainablefutureventure_scraper.py`) |
| Concord Health Partners | `concordhealthpartners_companies.json` | 15 | concordhp.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`concordhealthpartners_scraper.py`) |
| Dadneo Capital | `dadneo_companies.json` | 14 | dadneo.capital — portfolio page: company name (site-authored logo alt) and website where linked. (`dadneo_scraper.py`) |
| Bios Partners | `biospartners_companies.json` | 14 | biospartners.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`biospartners_scraper.py`) |
| Javis Ventures | `javisventures_companies.json` | 14 | javis-ventures.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`javisventures_scraper.py`) |
| Giant Step Capital | `giantstepcapital_companies.json` | 14 | giantstep.vc — portfolio page: company name (site-authored logo alt) and website where linked. (`giantstepcapital_scraper.py`) |
| Detonate Ventures | `detonateventures_companies.json` | 14 | d2n8.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`detonateventures_scraper.py`) |
| Suneight Investment | `suneightinvestment_companies.json` | 14 | sun-8.jp — portfolio page: company name (site-authored logo alt) and website where linked. (`suneightinvestment_scraper.py`) |
| Apollo Health Ventures | `apollohealthventures_companies.json` | 13 | apollo.vc/what-we-invest-in — portfolio page: company name (site-authored heading/label text) and website where linked. (`apollohealthventures_scraper.py`) |
| i2i Ventures | `i2iventures_companies.json` | 13 | i2iventures.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`i2iventures_scraper.py`) |
| QBIT Capital | `qbitcapital_companies.json` | 12 | qbitcapital.xyz/how-we-invest — portfolio page: company name (site-authored heading/label text) and website where linked. (`qbitcapital_scraper.py`) |
| Darkmode Ventures | `darkmodeventures_companies.json` | 12 | darkmode.vc — portfolio page: company name (site-authored heading/label text) and website where linked. (`darkmodeventures_scraper.py`) |
| Nucleus Capital | `nucleuscapital_companies.json` | 12 | nucleus-capital.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`nucleuscapital_scraper.py`) |
| Omni Ventures | `omniventures_companies.json` | 12 | omnivl.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`omniventures_scraper.py`) |
| Future Planet Capital | `futureplanetcapital_companies.json` | 201 | futureplanetcapital.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`futureplanetcapital_scraper.py`) |
| D3 Jubilee | `d3jubilee_companies.json` | 82 | d3jubilee.com/Portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`d3jubilee_scraper.py`) |
| APY Ventures | `apyventures_companies.json` | 76 | apyventures.com/tr — portfolio page: company name (site-authored logo alt) and website where linked. (`apyventures_scraper.py`) |
| Growth Engine | `growthengine_companies.json` | 58 | growthengine.it — portfolio page: company name (site-authored logo alt) and website where linked. (`growthengine_scraper.py`) |
| Ship2B Ventures | `ship2bventures_companies.json` | 54 | ship2bventures.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`ship2bventures_scraper.py`) |
| Arc Ventures | `arcventures_companies.json` | 52 | arc-vc.com — portfolio page: company name (site-authored logo alt) and website where linked. (`arcventures_scraper.py`) |
| Visible Ventures | `visibleventures_companies.json` | 43 | visibleventures.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`visibleventures_scraper.py`) |
| LOI Venture | `loiventure_companies.json` | 42 | loi.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`loiventure_scraper.py`) |
| VestedWorld | `vestedworld_companies.json` | 37 | vestedworld.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`vestedworld_scraper.py`) |
| Cento Ventures | `centoventures_companies.json` | 34 | cento.vc/portfolio-company/#all — portfolio page: company name (site-authored logo alt) and website where linked. (`centoventures_scraper.py`) |
| Transform Capital Management | `transformcapitalmanageme_companies.json` | 33 | transform.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`transformcapitalmanageme_scraper.py`) |
| JDRF T1D Fund | `jdrft1dfund_companies.json` | 33 | t1dfund.org/our-portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`jdrft1dfund_scraper.py`) |
| Primitive Ventures | `primitiveventures_companies.json` | 32 | primitive.ventures — portfolio page: company name (site-authored logo alt) and website where linked. (`primitiveventures_scraper.py`) |
| Difference Capital | `differencecapital_companies.json` | 30 | differencepartners.com/portfolio — portfolio page: company name (site-authored link text) and website where linked. (`differencecapital_scraper.py`) |
| Terra Venture Partners | `terraventurepartners_companies.json` | 26 | terravp.com — portfolio page: company name (site-authored heading/label text) and website where linked. (`terraventurepartners_scraper.py`) |
| Mito Technology | `mitotechnology_companies.json` | 26 | mitotech.eu — portfolio page: company name (site-authored logo alt) and website where linked. (`mitotechnology_scraper.py`) |
| TRIREC | `trirec_companies.json` | 25 | trirec.co/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`trirec_scraper.py`) |
| NewBuild.VC | `newbuildvc_companies.json` | 24 | newbuildvc.com/companies — portfolio page: company name (site-authored logo alt) and website where linked. (`newbuildvc_scraper.py`) |
| Atesis Capital | `atesiscapital_companies.json` | 24 | atesis.vc — portfolio page: company name (site-authored logo alt) and website where linked. (`atesiscapital_scraper.py`) |
| Esplanade Ventures | `esplanadeventures_companies.json` | 23 | esplanadeventures.com — portfolio page: company name (site-authored logo alt) and website where linked. (`esplanadeventures_scraper.py`) |
| Tensor Ventures | `tensorventures_companies.json` | 22 | tensor.ventures — portfolio page: company name (site-authored logo alt) and website where linked. (`tensorventures_scraper.py`) |
| Novalis Biotech | `novalisbiotech_companies.json` | 21 | noval.is/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`novalisbiotech_scraper.py`) |
| Tilia Impact Ventures | `tiliaimpactventures_companies.json` | 20 | tilia.vc — portfolio page: company name (site-authored heading/label text) and website where linked. (`tiliaimpactventures_scraper.py`) |
| South Loop Ventures | `southloopventures_companies.json` | 20 | southloop.vc/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`southloopventures_scraper.py`) |
| BONVENTURE | `bonventure_companies.json` | 19 | bonventure.de/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`bonventure_scraper.py`) |
| Belle Impact Fund | `belleimpactfund_companies.json` | 18 | bellefunds.com — portfolio page: company name (site-authored logo alt) and website where linked. (`belleimpactfund_scraper.py`) |
| Dipalo Ventures | `dipaloventures_companies.json` | 17 | dipaloventures.com — portfolio page: company name (site-authored logo alt) and website where linked. (`dipaloventures_scraper.py`) |
| Interactive Venture Partners | `interactiveventurepartne_companies.json` | 15 | interactivevp.com/en/our-portfolio.php — portfolio page: company name (site-authored logo alt) and website where linked. (`interactiveventurepartne_scraper.py`) |
| Cactus Venture Partners | `cactusventurepartners_companies.json` | 15 | cactuspartners.in/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`cactusventurepartners_scraper.py`) |
| Clanton Capital | `clantoncapital_companies.json` | 15 | clantoncapital.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`clantoncapital_scraper.py`) |
| Auxano | `auxano_companies.json` | 14 | auxano.in — portfolio page: company name (site-authored logo alt) and website where linked. (`auxano_scraper.py`) |
| 49 Palms Ventures | `49palmsventures_companies.json` | 14 | 49palmsvc.com — portfolio page: company name (site-authored logo alt) and website where linked. (`49palmsventures_scraper.py`) |
| Potencia Ventures | `potenciaventures_companies.json` | 14 | potenciaventures.net/companies — portfolio page: company name (site-authored logo alt) and website where linked. (`potenciaventures_scraper.py`) |
| GET Fund | `getfund_companies.json` | 13 | getfund.eu — portfolio page: company name (site-authored heading/label text) and website where linked. (`getfund_scraper.py`) |
| CRIVO Ventures | `crivoventures_companies.json` | 13 | crivo.ventures — portfolio page: company name (site-authored logo alt) and website where linked. (`crivoventures_scraper.py`) |
| SRI Capital | `sricapital_companies.json` | 12 | sricapital.com — portfolio page: company name (site-authored logo alt) and website where linked. (`sricapital_scraper.py`) |
| TransPacific Venture Partners | `transpacificventurepartn_companies.json` | 12 | transpacificvc.com/portfolio.html — portfolio page: company name (site-authored link text) and website where linked. (`transpacificventurepartn_scraper.py`) |
| Synthesis Capital | `synthesiscapital_companies.json` | 12 | synthesis.capital/our-portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`synthesiscapital_scraper.py`) |
| TEXO Ventures | `texoventures_companies.json` | 12 | texoventures.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`texoventures_scraper.py`) |
| Neo Kuma Ventures | `neokumaventures_companies.json` | 12 | neokuma.co — portfolio page: company name (site-authored heading/label text) and website where linked. (`neokumaventures_scraper.py`) |
| Burnt Island Ventures | `burntislandventures_companies.json` | 12 | burntislandventures.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`burntislandventures_scraper.py`) |
| Grizzly Capital | `grizzlycapital_companies.json` | 12 | grizzly.capital — portfolio page: company name (site-authored heading/label text) and website where linked. (`grizzlycapital_scraper.py`) |
| Lexi Ventures | `lexiventures_companies.json` | 11 | lexi.vc — portfolio page: company name (site-authored logo alt) and website where linked. (`lexiventures_scraper.py`) |
| Camford Capital | `camfordcapital_companies.json` | 11 | camford.com/companies — portfolio page: company name (site-authored logo alt) and website where linked. (`camfordcapital_scraper.py`) |
| Game Changers Ventures | `gamechangersventures_companies.json` | 11 | gamechangers.vc — portfolio page: company name (site-authored logo alt) and website where linked. (`gamechangersventures_scraper.py`) |
| Forepont Capital Partners | `forepontcapitalpartners_companies.json` | 11 | forepont.com/portfolio — portfolio page: company name (site-authored logo alt) and website where linked. (`forepontcapitalpartners_scraper.py`) |
| Dream Machine | `dreammachine_companies.json` | 11 | dreammachine.vc — portfolio page: company name (site-authored link text) and website where linked. (`dreammachine_scraper.py`) |
| CRE Venture Capital | `creventurecapital_companies.json` | 11 | cre.vc/our-companies — portfolio page: company name (site-authored logo alt) and website where linked. (`creventurecapital_scraper.py`) |
| Catalyst Health Ventures | `catalysthealthventures_companies.json` | 11 | chv.vc/portfolios — portfolio page: company name (site-authored logo alt) and website where linked. (`catalysthealthventures_scraper.py`) |
| Rubix Ventures | `rubixventures_companies.json` | 11 | rubix-partners.com/portfolio — portfolio page: company name (site-authored heading/label text) and website where linked. (`rubixventures_scraper.py`) |
**1758 firm datasets (125,781 companies in all_companies.json) after the 2026-10-18 VC 200c chunk 3 (Future Planet Capital/D3 Jubilee/APY Ventures/Growth Engine/Ship2B Ventures/Arc Ventures/Visible Ventures/LOI Venture/VestedWorld/Cento Ventures/Transform Capital Management/JDRF T1D Fund/Primitive Ventures/Difference Capital/Terra Venture Partners/Mito Technology/TRIREC/NewBuild.VC/Atesis Capital/Esplanade Ventures/Tensor Ventures/Novalis Biotech/Tilia Impact Ventures/South Loop Ventures/BONVENTURE/Belle Impact Fund/Dipalo Ventures/Interactive Venture Partners/Cactus Venture Partners/Clanton Capital/Auxano/49 Palms Ventures/Potencia Ventures/GET Fund/CRIVO Ventures/SRI Capital/TransPacific Venture Partners/Synthesis Capital/TEXO Ventures/Neo Kuma Ventures/Burnt Island Ventures/Grizzly Capital/Lexi Ventures/Camford Capital/Game Changers Ventures/Forepont Capital Partners/Dream Machine/CRE Venture Capital/Catalyst Health Ventures/Rubix Ventures); previous: 1708 firms / 124,404 after the 2026-10-18 VC 200c chunk 2 (SWC Global/Kalei Ventures/Prequel Ventures/Thuja Capital/LUN Partners Group/Socially Financed/SymBiosis/Ondine Capital/Blank Space Ventures/Uma Ventures/Lanchi Ventures/SpringCapital Investment/Rumbo Ventures/MedMountain Ventures/Terpsi Capital/Monoceros/Clay Capital/ASIF Ventures/SV Latam Fund/BRC Innovation/Citrino Ventures/devlabs/SMO Capital/Laude Ventures/Alive Ventures/Wild Basin Investments/Veryearly Ventures/Metropolis VC/First Ascent Ventures/Sandpiper Ventures/Open Circle Capital/Zentynel Frontier Investments/JSW Ventures/Fortitude Ventures/A-Force Ventures/Venture Development Partners/Sustainable Future Ventures/Concord Health Partners/Dadneo Capital/Bios Partners/Javis Ventures/Giant Step Capital/Detonate Ventures/Suneight Investment/Apollo Health Ventures/i2i Ventures/QBIT Capital/Darkmode Ventures/Nucleus Capital/Omni Ventures); previous: 1658 firms / 123,496 after the 2026-10-18 VC 200c chunk 1 (Astir Ventures/Rainfall Ventures/IBB Ventures/SixThirty Ventures/AQC Capital/Comma3 Ventures/Spot VC/Media Ventures/Four Rivers Group/Sugar Capital/SignalRank/FunFair Ventures/Anti Fund/TDF Ventures/Cofounders Capital/Magna Investment/Innovation Nest/99 Startups/Hawk Hill Ventures/Active Impact Investments/Cycle Capital/Quantumlight Capital/Formic Ventures/Pack Ventures/APEX Ventures/Stakez Capital/0BS/Acacia Venture Capital Partners/GBS Venture Partners/Core91.vc/Dangerous Ventures/Tenzor Capital/Asymmetric/BFG Partners/Slingshot Ventures/Breed VC/Breakpoint Capital/Leap Forward Ventures/Fireroad Ventures/Aroa Venture Partners/Morningstar Ventures/Mobility Ventures/Fall Line Capital/Great Circle Ventures/Grant Park Ventures/Eindhoven Venture Capital/Formulate Ventures/Venture to Future Fund/Brain-Too-Free Ventures/Futury Capital); previous: 1608 firms / 120,782 after the 2026-10-18 VC 200b chunk 4 (ZORA/Xploration Capital/Thursday Ventures/Stellifi/SPiCE VC/Eastend Ventures/Carbon Silicon/BreakOrbit/The SidebySide Partnership/Sanctor Capital/Rhinevall Capital/Kuorrokveik Adventure Capital/Interlock Partners/GOVO Venture Partners/Crypto Discover/Vickers Venture Partners/Team Ignite Ventures/Overeasy Ventures/2050 Capital/What If Ventures/Tin Alley Ventures/Stratified Capital/Dynamism Capital/Kesha Ventures/Island Capital/GAA Investments/Unbounded Capital/Multifaceted Capital/Encomenda VC/MSW Ventures/Brace Pharma/First Rays Venture Partners/aws Gründungsfonds/o2h Ventures/ABCDE Capital/Capital Today/Green Bay Ventures/VitalStage Ventures/Provence Partners/DGF/Ensemble VC/HCS Capital/BIP32 Venture/Strange Ventures/Palette Ventures/Ventura BioMed Investors/Pure Ventures/8090 Industries/Avalon BioVentures/Calculus Capital); previous: 1558 firms / 119,918 after the 2026-10-18 VC 200b chunk 3 (Ravelin Capital/Middleland Capital/Grid Capital/Miramar Venture Partners/Pender Ventures/New North Ventures/Xandex Ventures/Transition VC/Freigeist Capital/Curitas Ventures/Clearance Venture Partners/EFung Capital/Wocstar Capital/Gaia Ventures/Ballpark Ventures/Ankaa Ventures/Agaeti Ventures/Villhard Growth Partners/Urania Ventures/Steel Atlas/Parceiro Ventures/Linse Capital/Factorial Funds/Excelerate Health Ventures/Seaplane Ventures/Prevail Venture Capital/Prediction Capital/Novalis LifeSciences/Newton Biocapital/Antigravity Capital/Verb Ventures/Reflexive Capital/Nazare Ventures/Intonation Ventures/Flex Capital Partners/Camp One Ventures/Bettor Capital/Triatomic Capital/Leitmotif/Innospark Ventures/Even Capital/Callapina Capital/WXR Fund/Vocal Ventures/Sadu Capital/NGEN Partners/Longley Capital/Gigafund/Daybreak Partners/Bronze Investments); previous: 1508 firms / 118,971 after the 2026-10-18 VC 200b chunk 2 (Cloquet Capital Partners/age1/Vesalius Biocapital Partners/Starship Ventures/Spiral Sun Ventures/Signature Ventures/MiH Ventures/Impetus Capital/GOAL Ventures/Cove Fund/Aurelia Foundry/ACVC Partners/VC 414/Skywood Capital/Sentiero Ventures/Saturn Partners/Leaders Fund/FemHealth Ventures/InHealth Ventures/Citta Capital/Cade Ventures/Brave Capital/Anthropy Partners/Shoreline Venture Management/Onsight Ventures/Category Ventures/Bloc Ventures/Targeted Technology Funds/Cardinia Ventures/Clover Vitality/Two Ravens/Blue Hour Ventures/ETFS Capital/ExSight Ventures/ZBS CAPITAL/Jerusalem Global Ventures/Think+ Ventures/DIMENSION/Stepchange/IDEO CoLab Ventures/Polytechnique Ventures/Tamarisc Ventures/Lanai/Locus Ventures/Vox Capital/Global Hands-On VC/Rabbit Ventures/Signia Venture Partners/Tioga Capital Partners/Red Dog Capital); previous: 1458 firms / 117,770 after the 2026-10-18 VC 200b chunk 1 (Amador Holdings/Juvo Ventures/Sarah Smith Fund/DG Daiwa Ventures/BioGenerator Ventures/Hiroshima Venture Capital/Jam Fund/Mighty Capital/Access Venture Partners/Spiral Ventures/Muse Capital/Baukunst/Muirwoods Ventures/Hivemind Ventures/Solari Capital/Seae Ventures/13books Capital/Render Capital/NAV.VC/Accord Ventures/Windrose Capital/Optic Capital/Marram Ventures/Inspiration Ventures/Xeed Ventures/Valo Ventures/Tyche Partners/Privilège Ventures/ON&BOARD/Treeo VC/Semilla Ventures/Midnight/Daft Capital/CSA Partners/Creator Ventures/Aura Ventures/Amplifica Capital/SciFi VC/Nabventures/Chakra Growth Fund/Hike Capital/Ethos VC/DigiTx Partners/Chartline Capital Partners/Beat Ventures/Alante Capital/97212 Ventures/Reverie/Oval Park Capital/Long Venture Partners); previous: 1408 firms / 116,071 after removing Fernbrook Capital on 2026-10-18 (hedge fund, not a VC firm; scraper, dataset, metadata and Airtable row deleted); previous: 1409 firms / 116,101 after the 2026-10-18 VC 200 chunk 4 (Tenmile/Techstart Ventures/Tanglin Venture Partners/Syndicate One/Saviu Ventures/OVNI Capital/Mythos Ventures/Kairos Venture Investments/Innovation Global Capital/Ineffable Ventures/GroundBreak Ventures/GreyMatter/Galion.exe/Eastlink Capital Partners/Brass Ring Ventures/Ajim Capital/Zanichelli Venture/Neulogy Ventures/Debut Capital/Baroda Ventures/Tamarak Capital/Tamarack Global/Melt Ventures/INCE Capital/Impatient Ventures/Fundamental Ventures/Caruso Ventures/Also Capital/Varana Capital/SWaN & Legend Venture Partners/Progress Ventures/LongeVC/JAL Ventures/Hemi Ventures/Helium-3 Ventures/Department of XYZ/Vala Capital/Tracxn Labs/TIRTA Ventures/Series Ventures/Joa Capital/JDS Sports/Eudemian Ventures/Charlotte Street Capital/Keiki Capital/Mount VC/Fulcrum Venture Group/Dnipro VC/MPG Fund/Henq); previous: 1359 firms / 114,741 after the 2026-10-18 VC 200 chunk 3 (Linden Capital/Infinity Ventures/Groom Investment/Positive Sum Capital/Polymorphic Capital/PHX Ventures/NOEMIS Ventures/Failup Ventures/Ev3 Ventures/EQ2 Ventures/Color Capital/Asia2G Capital/Arctic Digital/Stacked Capital/Position Ventures/Oxonian Ventures/NextFab Ventures/J17 Capital/Harmonix Fund/GreenSky Ventures/ECONA/Crucible Capital/Conductive Ventures/Bisk Ventures/Amino Collective/Pebblebed/Paper Ventures/MESH/Cottonwood Technology Fund/Undeterred Capital/Red & Blue Ventures/Outset Ventures/MoreVC/LEAP Global Partners/First Circle/California Innovation Fund/Beliade/AdBio Partners/TCP Venture Capital/Significant Ventures/Pavestone/Oktogon Ventures/Northern Gritstone/Mento VC/Heal Capital/Gabriel Venture Partners/Enzo Ventures/Chattanooga Renaissance Fund/Virta Ventures); previous: 1309 firms / 113,109 after the 2026-10-18 VC 200 chunk 2 (New Science Ventures/L2 Iterative Ventures/Fourth Realm/Champion Hill Ventures/TDV Partners/Bankless Ventures/BADideas.fund/11.2 Capital/Trind Ventures/Serpentine Ventures/Maxpro Ventures/Deep Future/1818 Venture Capital/NVP Capital/FreshTracks Capital/Dig Ventures/Capital Midwest Fund/Braemar Energy Ventures/Windham Capital Partners/Swift Ventures/UDHC/Plum Ventures/Emblem/Wellstreet/Venista Ventures/Red Building Capital/Lumis Partners/Kogito Ventures/Interlace Ventures/Innovation Industries/Early Game Ventures/Cosmic Venture Partners/AI Seed/Virescent Ventures/Start Capital/Sondo Capital/Second Alpha Partners/ScOp Venture Capital/Nuwa Capital/Eterna Capital/Athera Venture Partners/SuperSeed/Naples Technology Ventures/ISA Ventures/Form Ventures/E2MC Ventures/Cyber Mentor Fund/Balerion Space Ventures/3cubed Ventures/Sherpalo Ventures); previous: 1259 firms / 111,123 after the 2026-10-18 VC 200 chunk 1 (Laguna Investment/mint VC/Delight Ventures/ShangBay Capital/Peercheque/TRGC/Groove Capital/AAF Management/bmp Ventures/Samos Investments/Delphi Ventures/Unovis Asset Management/Haven Ventures/Align Ventures/Silicon Gardens/Aster Capital/Merak Ventures/MAGIC Fund/DEPO Ventures/One Planet Capital/PruVen Capital Partners/Faction/Trilogy Equity Partners/Texas HALO Fund/OIF Ventures/Ryze Labs/R136 Ventures/Vela Partners/MPower Partners/Soundboard Venture Fund/Future Perfect Ventures/Moonstone Venture Capital/Lobster Capital/Keshif Ventures/Andromeda Capital/AIN Ventures/Modi Ventures/Lince Capital/Denver Ventures/The Raba Partnership/SBXi/NuVentures/NovaCapital/JK&B Capital/Carbide Ventures/Alpana Ventures/LRVHealth/Netrix Ventures/Two Culture Capital/Rebel Fund); previous: 1209 firms / 108,423 after the 2026-10-18 Daily 20 (Alumni Ventures/Precursor Ventures/Upfront Ventures/firstminute capital/Offline Ventures/Freestyle Capital/FinTech Collective/Moonfire Ventures/Promus Ventures/Harlem Capital/Jetstream/Forward Venture Capital/AfterWork Ventures/Angel Invest/Catalyst Investors/TFX Capital/Distributed Ventures/Overlook Ventures/Cake Ventures/Zenda); previous: 1189 firms / 105,347 after the 2026-10-17 Queue 200b chunk 4 (Flucas Ventures/Social Starts/Metaplanet/Borderless Capital/Karista/Norte Ventures/Olive Tree Capital/Nazca/Red Beard Ventures/Breyer Capital/BIP Ventures/NGP Capital/The Chernin Group/GRIDX/Wayfinder Ventures/Sora Ventures/GSV Ventures/EMV Capital/Front Row Ventures/Paladin Capital Group/Icon Ventures/Draper Dragon/DAG Ventures/VTF Capital/New Ground Ventures/Jenson Ventures/Bow Capital/Base Ventures/LongHash Ventures/Dholakia Ventures/UK Innovation & Science Seed Fund/Upsparks Capital/Eoniq/BOLD Capital Partners/AIX Ventures/Yolo Investments/Emles Venture Partners/Dreamers VC/Able Partners/ClearSky/Flori Ventures/Civilization Ventures/Celtic House Asia Partners/Peregrine Ventures/7percent Ventures/Pacific Channel/Early Light Ventures/Open Opportunity Fund/Mars Shot Ventures/Miton/Merus Capital/Cortado Ventures/Flyover Capital/Black Jays Ventures/Green Park & Golf Ventures/Earl Grey Capital/Gemba Capital/Auxxo/Construct Capital/Hartmann Capital/Pix Vine Capital/Outbound Ventures/UVC Partners/Millennium New Horizons/Juniper VC/DSG Consumer Partners); previous: 1123 firms / 100,390 after the 2026-10-17 Queue 200b chunk 3 (SemperVirens/iSelect Fund/Droia Ventures/Earthshot Ventures/AENU/Xontogeny/Seroba/Generator Ventures/Cultivate Next/Martin Ventures/Sound Bioventures/Blue Venture Fund/Acre Venture Partners/WEH Ventures/Taiwania Capital/Eximius Ventures/Service Provider Capital/PsyMed Ventures/Big Sur Ventures/Flyer One Ventures/Skyland Ventures/Radian Capital/Robin Hood Ventures/Telstra Ventures/Digital Horizon/Caffeinated Capital/PhotonVentures/TechOperators/Bungalow/Outlander VC/Eminence Ventures/Xfund/Nordic Alpha Partners/Blue Ashva Capital); previous: 1089 firms / 99,238 after the 2026-10-17 Queue 200b chunk 2 (Omega Funds/Grit Capital Partners/Apple Tree Partners/Shadow Ventures/Selva Ventures/Preston-Werner Ventures/August Capital/ZAKA VC/aMoon Fund/25madison/TheVentures/Taurus Ventures/LoftyInc Capital/MGV/Chengwei Capital/FGV Capital/Akkadian Ventures/NightDragon/Twine Ventures/Betatron Venture Group/KOMPAS VC/Switch Ventures/Supermoon Capital/Cadenza Ventures/Vocap Partners/Alix Ventures/Capria Ventures/Jump Crypto/First Star Ventures/Ibex Investors/Social Leverage/Socii Capital/Kayyak Ventures/Meridian Ventures/Silas Capital/Utopian Ventures/Modus Capital/PJC/Headwater Ventures/Rarebreed Ventures/Ankona Capital/Northstar Ventures/Expeditions Fund/Gotham Ventures/CyberAgent Capital/Begin Capital/Naver D2SF/Equinor Ventures/MongoDB Ventures/Lightbank); previous: 1039 firms / 96,932 after the 2026-10-17 Queue 200b chunk 1 (Heartfelt/BAM Ventures/Green Egg Ventures/SHAKTI/Unruly Capital/Virtue/Propeller/Reign Ventures/Brainstorm Ventures/WaterBridge Ventures/Dundee Venture Capital/Vertical Venture Partners/Marathon Venture Capital/Stride VC/Adapt Ventures/Plum Alley/Elysium Venture Capital/Chamaeleon/Duro Ventures/Demea Invest (formerly Demeter)/Bertha Capital/359 Capital/IOSG Ventures/All In Capital/Trihill Capital/CDP Venture Capital/Axon Partners Group/Abac Nest/SpeedUp Venture Capital Group/WI Harper Group/Avaana Capital/Puzzle Ventures/Aglaé Ventures/2045 Ventures/Stout Street Capital/MATH Venture Partners/Firebolt Ventures/Team Builder Ventures/UTEC (University of Tokyo Edge Capital Partners)/Scrum Ventures/G20 Ventures/BlueTree Venture Fund/MissionOG/Alpaca VC/Vertex Ventures Israel/Thin Air Labs/NTT Docomo Ventures/CoVentures/Detroit Venture Partners/Artis Ventures); previous: 989 firms / 94,127 after the 2026-10-17 Queue 200 chunk 4 (Jackson Square Ventures/Shine Capital/Dalus Capital/Lightbox Ventures/Coral Capital/Incubate Fund/GD1/Launch Capital/Acrew Capital/Alliance Venture/Glynn Capital/Lumia Capital/Forge VC/Calibrate Ventures/Boehringer Ingelheim Venture Fund/imec.xpand/Keen Venture Partners/Qbic/Brightstone Venture Capital/Cultivian Sandbox Ventures/Ripple Ventures/Vibe Capital/Linear Capital/Emerald Technology Ventures/Bee Partners/SET Ventures/Chemistry/Atlanta Ventures/Catapult Ventures/Seven Stars/Dynamo Ventures/ONEVC/Archetype/Collab+Currency/Eos Venture Partners/FinTLV Ventures/Hypersphere/Love Ventures/Twin Path Ventures/Altara Ventures/Atinum Investment/Blue Wire Capital/First Cheque/Lok Capital/Mandiri Capital Indonesia/Rainmatter/Yellowdog/SaaSholic/Ankur Capital/TruStage Ventures (formerly CMFG Ventures)); previous: 939 firms / 91,631 after the 2026-10-17 Queue 200 chunk 3 (14 Peaks Capital/Qumra Capital/Bailador Technology Investments/Tenacious Ventures/Casdin Capital/Syncona/Hi Ventures (formerly ALLVP)/Activate Capital/Acme Capital/Finch Capital/Valia Ventures/Source Code Capital/Alpha JWC Ventures/Phoenix Court (LocalGlobe / Latitude / Solar)/Porsche Ventures/Bain Capital Crypto/Beta Boom/Defy Partners/Elefund/Ironspring Ventures/Night Ventures/Operator Collective/Scribble Ventures/Calm/Storm Ventures/NAP/Redstone/Voima Ventures/YZR Capital/Practica Capital/Ysios Capital/Asabys Partners/Outliers VC/Orios Venture Partners/Ideaspring Capital/Luge Capital/Arboretum Ventures/Seventure Partners/Haatch/ACT Venture Capital/Atlantic Bridge/Boston Seed Capital/Bon Angels Venture Partners/Decasonic/MizMaa Ventures/Senovo/Two Bear Capital/Vorwerk Ventures/Newfund/Builders VC/Highland Europe); previous: 889 firms / 89,636 after the 2026-10-17 Queue 200 chunk 2 (Mouro Capital/Ascend Venture Capital/Blue Collective/2150/AltaIR Capital/ISAI/PROfounders Capital/Altos Ventures/Manta Ray Ventures/Nextech Invest/SHIFT Invest/Regeneration.VC/Everywhere Ventures/Maniv Mobility/HCVC/Singular/Cleveland Avenue/Blossom Street Ventures/42CAP/FoodLabs/PT1 Ventures/IAG Firemark Ventures/Tidal Ventures/iGlobe Partners/Bison Ventures/Pi Labs/Embark Ventures/Anzu Partners/SeaChange/Sky9 Capital/Ocean Azul Partners/Gobi Partners/InReach Ventures/UpHonest Capital/Shunwei Capital/Motion Ventures/TRIVE VC/Overline/growX ventures/Boreal Ventures/Flux Capital/Earth Foundry/Concrete Venture Capital/BioGeneration Ventures/SV Health Investors/Building Ventures/Vida Ventures/Truffle Capital/DOT Capital/Amex Ventures); previous: 839 firms / 86,946 after the 2026-10-17 Queue 200 chunk 1 (Expansion VC/Pathbreaker Ventures/Musha Ventures/Reshape Ventures/Nido Ventures/Swizzle Ventures/RiverPark Ventures/Kokopelli Capital/Outrun Ventures/C4 Ventures/Brick & Mortar Ventures/MAYA Capital/Shilling/TheVentureCity/Optum Ventures/OpenOcean/PeakBridge/Wireframe Ventures/Ignition Partners/Thomvest Ventures/Illumina Ventures/Camber Creek/OTB Ventures/Rocketship.vc/KdT Ventures/seed + speed Ventures/Skyfall Ventures/MEVP/One Way Ventures/Eka Ventures/Riot Ventures/JME Ventures/Autotech Ventures/Momenta Ventures/NZVC/Movens Capital/Shorooq/Indico Capital Partners/Squadra Ventures/Fireside Ventures/Rockaway Ventures/Silverton Partners/Volta Energy Technologies/LUMO Labs/Cisco Investments/Tech Square Ventures/Stripes/Fuse/BlueRun Ventures/MCJ Collective); previous: 789 firms / 83,838 after the 2026-10-17 Queue 50b (DASH Ventures/Valuestream Labs/Beyond Capital Ventures/Humbition/Airwing/Blue 9 Capital/Cartography Capital/OCV Partners/Primo Capital/JumpStart Ventures/Eutopia Ventures/Lumir Ventures/1Flourish Capital/Tenacity Venture Capital/SUM Ventures/Stage Venture Partners/Secocha Ventures/Archangel Ventures/Ascension Ventures/CSC Upshot Ventures/1955 Capital/Gutter Capital/Taram Capital/Endurance28/Streetlife Ventures/Outward VC/Investible/Kadan Capital/Emerging Ventures/Brooklyn Bridge Ventures/Future Positive Capital/Italian Founders Fund/Wavemaker 360/Elevate Capital/S4S Ventures/Haymaker Ventures/Lytical Ventures/Waarde Capital/Valor Ventures/Sarmayacar/K3 Ventures/Big Brain Holdings/Tantauco Ventures/IGNIA/Verge HealthTech Fund/Deviation Capital/South Central Ventures/Nascent VC/Flair Ventures/Uncommon Denominator); previous: 739 firms / 81,789 after the 2026-10-17 Queue 50a (Scout Ventures/Lobby Capital/Humba Ventures/Primetime Partners/The Venture Collective/Incisive Ventures/Wonder Ventures/Rosecliff Ventures/SGH Capital/The MBA Fund/Acurio Ventures/Very Serious Ventures/Newtopia VC/PointOne Capital/GFR Fund/Sandalphon Capital/Acadian Ventures/Emergent Ventures/Royal Street Ventures/HealthX Ventures/TNB Aura/ManchesterStory/Motivate Ventures/Noetic Fund/LongJump VC/Orvel Ventures/Bay Wharf Capital/Moderne Ventures/Lightscape Partners/Abstraction Capital/Mission One Capital/Roo Capital/Keyhorse Capital/Emmeline Ventures/Hemisphere Ventures/RunwayVC/Kopa Ventures/Noveus Capital/Altari Ventures/Blue Lion Global/BroadLight Capital/BoutiqueVC/NuMundo Ventures/Firsthand VC/Cutting Horse/Behind Genius Ventures/Argon Ventures/Fjor Founders Fund/OpenSky Ventures/Blitzscaling Ventures); previous: 689 firms / 79,203 after the 2026-10-17 Queue 20b (Toyota Ventures/NewView Capital/Galaxy Ventures/137 Ventures/Type One Ventures/Struck Capital/Avid Ventures/Leo Capital/TMV/Zeal Capital Partners/Silicon Badia/Story Ventures/True Global Ventures/Lakehouse Ventures/Tera Ventures/Scrub Capital/Refract Ventures/Acronym VC/Nava Ventures/Five Four Ventures); previous: 669 firms / 78,253 after the 2026-10-17 Queue 20 (FirstMile Ventures/DFS Lab/Symphonic Capital/Rho Capital Partners/Tectonic Ventures/Array Ventures/Connetic Ventures/Room40 Ventures/Hilltop Venture Partners/Companyon Ventures/Laconia/XRC Ventures/Morningside Ventures/Impact America Fund/The Artemis Fund/XFactor Ventures/Sidecut Ventures/Myriad Venture Partners/Footwork/Rev1 Ventures); previous: 649 firms / 77,283 after the 2026-10-17 Daily 20 (Western Technology Investment/Titan Capital/GTMfund/645 Ventures/Verve Ventures/Millennium Technology Value Partners/Tribeca Venture Partners/Verissimo Ventures/Alpha Edison/Collide Capital/Irregular Expressions/Act One Ventures/Hearst Ventures/Ingressive Capital/Kearny Jackson/Echo Health Ventures/LDV Capital/Differential Ventures/Rampersand/Rebright Partners); previous: 629 firms / 74,430 after the 2026-10-16 Queue 50 (Hitachi Ventures/Chevron Technology Ventures/Grotech Ventures/Moonshots Capital/Trucks VC/Lorimer Ventures/V1 VC/Golden Seeds/SoGal Ventures/Foundamental/NextGen Venture Partners/HLM Venture Partners/Data Point Capital/Elevate Ventures/Coalition Operators/VentureSouq/Fluent Ventures/Blackhorn Ventures/Urban Innovation Fund/Leadout Capital/Vitalize VC/Kaya Ventures/Ubiquity Ventures/Fresco Capital/Industrious Ventures/Vine Ventures/Right Click Capital/Pathlight Ventures/Trust Fund/January Ventures/Hypothesis/Script Capital/Seaside Ventures/Supernode Ventures/Great North Ventures/True Wealth Ventures/Matterscale Ventures/Savannah Fund/Trousdale Ventures/Era Ventures/Playfair Capital/Avalanche VC/How Women Invest/Sancus Ventures/Resilience Reserve/Asylum Ventures/Prototype Capital/SNÖCAP/Parameter Ventures/Planet A Ventures); previous: 579 firms / 71,793 after the 2026-10-16 List 50 (LifeX Ventures/Garuda Ventures/Breakout Ventures/SKY VC/Refactor Capital/Courtside Ventures/TEN13/Twelve Below/Theory Ventures/Matchstick Ventures/Collab Capital/Mercato Partners/Z Venture Capital/Backstage Capital/SJF Ventures/Geodesic Capital/TTV Capital/Interplay/E14 Fund/Dorm Room Fund/Oak Investment Partners/Third Sphere/Sterling Road/Draft Ventures/Untapped Capital/M25/Human Ventures/Canapi Ventures/Yes VC/6th Man Ventures/Arbor Ventures/Revel Partners/JLL Spark/Necessary Ventures/Kepple Africa Ventures/Tau Ventures/Next Ventures/Valar Ventures/Zetta Ventures/Runa Capital/Swell VC/Link Ventures/Remarkable Ventures/Focal VC/Path Ventures/Moment Ventures/Charge VC/Haystack/Mozilla Ventures/Lead Edge Capital); previous: 529 firms / 68,442 after the 2026-10-16 VC 50 (FJ Labs/In-Q-Tel/Celesta Capital/Creathor Ventures/Canvas Ventures/Astella/Fin Capital/Founders Future/Harpoon Ventures/Adara Ventures/HealthCap/Aisling Capital/Better Capital/Fenbushi Capital/ParaFi Capital/Sanofi Ventures/Spring Camp/Standard Crypto/Mission BioCapital/Beyond Next Ventures/Cervin Ventures/Hatteras Venture Partners/Mashup Ventures/Parkwalk Advisors/Manhattan Venture Partners/COMETA/Inflexor Ventures/Sauce.vc/K5 Global/G2 Venture Partners/Axeleo Capital/Raed Ventures/Smartfin/Future Africa/Dell Technologies Capital/Main Sequence/Next Frontier Capital/Album VC/Norrsken VC/Blue Bear Capital/Azolla Ventures/Symbolic Capital/Foxmont Capital Partners/Prime Movers Lab/Aavishkaar Capital/coparion/Material Impact/Saama Capital/Jeito Capital/Kurma Partners); previous: 479 firms / 62,694 (62,726 after the Hustle Fund refresh) after the 2026-10-16 High-Value 50 (Silver Lake/Vista Equity Partners/HongShan/TA Associates/Summit Partners/Bosch Ventures/Avenir Growth/Globis Capital Partners/BlueYard Capital/Innovation Endeavors/Felix Capital/Accel-KKR/S2G Ventures/Ventech/DBL Partners/SoftBank Vision Fund/BDMI/EQT/Samsung Catalyst Fund/Kinnevik/ZhenFund/Owl Ventures/SR One/Abingworth/Animoca Brands/Endeit Capital/Lattice Fund/Greenfield Capital/Activant Capital/Human Capital/DOMO Invest/Novartis Venture Fund/Premji Invest/Z47/Arrington Capital/Francisco Partners/Advent International/Hellman & Friedman/Leonard Green & Partners/Genstar Capital/Roark Capital/Stonepeak/Montagu Private Equity/BC Partners/Berkshire Partners/Investcorp/Vestar Capital Partners/H.I.G. Capital/New Mountain Capital/Clayton, Dubilier & Rice); previous: 429 firms / 55,774 after the 2026-10-16 Extra 50 (Cota/DCG/Garage/Designer Fund/Hashed/Teamworthy/Lightstone/RA Capital/Longitude/K Fund/Voyager/GreatPoint/Microtraction/Lumira/Vendep/Prime VP/Inovo/Frst/F2/N49P/Alta/Sawari/Gaingels/Passion/P101/Augmentum/Kae/Alpha Partners/Glasswing/Portage/M Ventures/Bain Capital Life Sciences/World Fund/Frazier/Algebra/Rally/10D/Eight Roads/Hyperplane/EVP/Magma Partners/Inventure/La Famiglia/Extantia/OSE/HOF/Knife/Georgian/Conviction/Maven 11); previous: 379 firms / 48,941 after the 2026-10-16 Daily 20 (Boost VC/Dragonfly/Multicoin/Betaworks/Cherry/Chiratae/IQ Capital/Flybridge/Long Journey/Ada/Section 32/Accomplice/Character/Weekend Fund/Hiro/CoinFund/Monashees/Electric/Breega/Griffin); previous: 359 firms / 47,628 after the 2026-10-15 Daily 20 (Bonfire/TenOneTen/Contour/Valor Capital Group/FTV/Polaris/Forgepoint/Evolution Equity/Glilot/G Squared/Fifth Wall/Orange Collective/VestedVC/Fly Ventures/BTV/QED/Third Rock/Flare Capital/Hetz/Peak XV); previous: 339 firms / 45,974 after the 2026-10-14 Daily 20 (OCA/Moxxie/Kibo/Lifeline/Peak/JMI/Energize/Play Ventures/Point72 Ventures/Ten Eleven/Spectrum Equity/Five Elms/Edison/Space Capital/Makers Fund/Monk's Hill/Jump Capital/Castle Island/7wire/Crosscut); previous: 319 firms / 44,292 after the 2026-10-13 Daily 20 (Wellington/Creandum/Sony Innovation Fund/Blume/Shrug/Joyance/Commerce Ventures/Hg/Day One/Higher Ground Labs/Version One/Compound/Origin Ventures/1confirmation/Valor/Corazon/Fuel/Round13/Relay/Ludlow); previous: 299 firms / 42,338 after the 2026-10-12 Daily 20 (Intel Capital/360 Capital/Hack VC/Equal/StandUp/Flagship/Liquid 2/Flourish/ffVC/United Ventures/TLV/Quona/Molten/BMW i Ventures/Framework/MPM BioImpact/IDG/Team8/HV Capital/DCM); previous: 279 firms / 41,154 after the 2026-10-11 Daily 20 (Stage 2/5AM/Next Coast/Converge/1kx/Variant/Mantis/Clean Energy Ventures/Drive/HTGF/PSL/Qiming/AlleyCorp/Samsara/Chicago Ventures/Foresite/Revolution/Trinity/Endiya/AgFunder); see all_companies_index.json (parts: all_companies.json + all_companies_2.json …) for live totals.**

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
│   ├── all_companies.json + all_companies_2.json (+ _3 …)  ← combined master,
│   │     SPLIT into parts of ≤ ~40 MB (see §Combined master below)
│   ├── all_companies_index.json        ← lists the master parts + firm/company counts
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
### Combined master (`all_companies*.json`, split since 2026-10-18)
`automation/master_builder.py` combines every `<firm>_companies.json` into one normalized row
list (firm, firm_slug, name, url, description, everywhere_tags, exited, primary_investor,
location, stage, first_invested, status), ordered by sorted dataset filename. GitHub/raw
handling degrades past ~50 MB, so the list is **split on whole-firm boundaries, in order**:
`data/all_companies.json` is filled up to `PART_LIMIT_BYTES` (40,000,000 bytes), then the
overflow spills into `all_companies_2.json`, then `_3`, … (a firm is never split across
files; every part is the same JSON list-of-rows format). `data/all_companies_index.json`
lists the parts in order with `firms`, `companies`, `bytes`, `first_firm`, `last_firm`, plus
`total_firms` / `total_companies`.
- **Rebuild:** `python3 automation/master_builder.py` (writes all parts + index, deletes stale
  higher-numbered parts). The nightly pipeline (`_build_all_companies`) does the same via the
  GitHub store: commits each changed part, deletes stale parts, commits the index.
- **Read ALL parts — never just `all_companies.json`** (it is no longer the whole master):
  `from master_builder import load_all; rows = load_all()` (follows the index, falls back to
  globbing `all_companies*.json`), or for dashboards/raw consumers fetch the index and then
  each `file` it lists from `https://raw.githubusercontent.com/michaeleverywhere/vc-comp/main/data/`.
  Totals: read `total_firms` / `total_companies` from the index.
- Part files and the index are never firm datasets: `master_builder.is_master_file(name)`;
  the `*_companies.json` globs used by scrapers / fill / tagging scripts don't match them.
- The split is lossless: concatenating the parts in index order reproduces exactly the rows
  a single-file build would contain (verified 2026-10-18: 108,423 rows / 1,209 firms,
  identical content + order).

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
