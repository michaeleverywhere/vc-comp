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
**529 firm datasets (68,442 companies in all_companies.json) after the 2026-10-16 VC 50 (FJ Labs/In-Q-Tel/Celesta Capital/Creathor Ventures/Canvas Ventures/Astella/Fin Capital/Founders Future/Harpoon Ventures/Adara Ventures/HealthCap/Aisling Capital/Better Capital/Fenbushi Capital/ParaFi Capital/Sanofi Ventures/Spring Camp/Standard Crypto/Mission BioCapital/Beyond Next Ventures/Cervin Ventures/Hatteras Venture Partners/Mashup Ventures/Parkwalk Advisors/Manhattan Venture Partners/COMETA/Inflexor Ventures/Sauce.vc/K5 Global/G2 Venture Partners/Axeleo Capital/Raed Ventures/Smartfin/Future Africa/Dell Technologies Capital/Main Sequence/Next Frontier Capital/Album VC/Norrsken VC/Blue Bear Capital/Azolla Ventures/Symbolic Capital/Foxmont Capital Partners/Prime Movers Lab/Aavishkaar Capital/coparion/Material Impact/Saama Capital/Jeito Capital/Kurma Partners); previous: 479 firms / 62,694 (62,726 after the Hustle Fund refresh) after the 2026-10-16 High-Value 50 (Silver Lake/Vista Equity Partners/HongShan/TA Associates/Summit Partners/Bosch Ventures/Avenir Growth/Globis Capital Partners/BlueYard Capital/Innovation Endeavors/Felix Capital/Accel-KKR/S2G Ventures/Ventech/DBL Partners/SoftBank Vision Fund/BDMI/EQT/Samsung Catalyst Fund/Kinnevik/ZhenFund/Owl Ventures/SR One/Abingworth/Animoca Brands/Endeit Capital/Lattice Fund/Greenfield Capital/Activant Capital/Human Capital/DOMO Invest/Novartis Venture Fund/Premji Invest/Z47/Arrington Capital/Francisco Partners/Advent International/Hellman & Friedman/Leonard Green & Partners/Genstar Capital/Roark Capital/Stonepeak/Montagu Private Equity/BC Partners/Berkshire Partners/Investcorp/Vestar Capital Partners/H.I.G. Capital/New Mountain Capital/Clayton, Dubilier & Rice); previous: 429 firms / 55,774 after the 2026-10-16 Extra 50 (Cota/DCG/Garage/Designer Fund/Hashed/Teamworthy/Lightstone/RA Capital/Longitude/K Fund/Voyager/GreatPoint/Microtraction/Lumira/Vendep/Prime VP/Inovo/Frst/F2/N49P/Alta/Sawari/Gaingels/Passion/P101/Augmentum/Kae/Alpha Partners/Glasswing/Portage/M Ventures/Bain Capital Life Sciences/World Fund/Frazier/Algebra/Rally/10D/Eight Roads/Hyperplane/EVP/Magma Partners/Inventure/La Famiglia/Extantia/OSE/HOF/Knife/Georgian/Conviction/Maven 11); previous: 379 firms / 48,941 after the 2026-10-16 Daily 20 (Boost VC/Dragonfly/Multicoin/Betaworks/Cherry/Chiratae/IQ Capital/Flybridge/Long Journey/Ada/Section 32/Accomplice/Character/Weekend Fund/Hiro/CoinFund/Monashees/Electric/Breega/Griffin); previous: 359 firms / 47,628 after the 2026-10-15 Daily 20 (Bonfire/TenOneTen/Contour/Valor Capital Group/FTV/Polaris/Forgepoint/Evolution Equity/Glilot/G Squared/Fifth Wall/Orange Collective/VestedVC/Fly Ventures/BTV/QED/Third Rock/Flare Capital/Hetz/Peak XV); previous: 339 firms / 45,974 after the 2026-10-14 Daily 20 (OCA/Moxxie/Kibo/Lifeline/Peak/JMI/Energize/Play Ventures/Point72 Ventures/Ten Eleven/Spectrum Equity/Five Elms/Edison/Space Capital/Makers Fund/Monk's Hill/Jump Capital/Castle Island/7wire/Crosscut); previous: 319 firms / 44,292 after the 2026-10-13 Daily 20 (Wellington/Creandum/Sony Innovation Fund/Blume/Shrug/Joyance/Commerce Ventures/Hg/Day One/Higher Ground Labs/Version One/Compound/Origin Ventures/1confirmation/Valor/Corazon/Fuel/Round13/Relay/Ludlow); previous: 299 firms / 42,338 after the 2026-10-12 Daily 20 (Intel Capital/360 Capital/Hack VC/Equal/StandUp/Flagship/Liquid 2/Flourish/ffVC/United Ventures/TLV/Quona/Molten/BMW i Ventures/Framework/MPM BioImpact/IDG/Team8/HV Capital/DCM); previous: 279 firms / 41,154 after the 2026-10-11 Daily 20 (Stage 2/5AM/Next Coast/Converge/1kx/Variant/Mantis/Clean Energy Ventures/Drive/HTGF/PSL/Qiming/AlleyCorp/Samsara/Chicago Ventures/Foresite/Revolution/Trinity/Endiya/AgFunder); see all_companies.json for live totals.**

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
