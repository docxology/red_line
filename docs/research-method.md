# Research method and source ledger

This project uses scholarship as an audit surface, not as an authority bundle.
The method asks what a source makes visible about scope, authority, information,
power, consent, institutional practice, or accountability; it does not infer
that the source endorses the author's personal red lines.

## Selection protocol

For each added source, the research pass records:

1. the source's place, period, genre, and scholarly or institutional status;
2. the narrow question transferred into this project;
3. the claim the source is *not* being used to establish;
4. a URL verified against a publisher, library, primary-text, or official
   institutional page on the date recorded in the bibliography or source note;
5. a stable locator (page, section, chapter, or paragraph) for the claim; and
6. the manuscript paragraph or visualization that uses the source.

The auditable ledger record is therefore:

`source_id | geography | period | language / translation | genre / edition |
stable locator | claim class | question transferred | non-transfer boundary |
verified URL | manuscript or figure use`

**How much of that record actually exists today.** Items 1-4 and 6 are recorded
for all 45 sources. Item 5 — and the language/translation and genre/edition
fields — are recorded only for the 22 sources in the second table below, which
is the one carrying a `Language, edition, genre, stable locator` column. The
first table's 23 rows are the human-readable index and were never backfilled
into the seven-column schema. In the machine-readable ledger
(`data/source_claims.json`) those 23 records carry the explicit sentinel
`not recorded` in `edition_locator`; the sentinel is enumerated, the counts are
published in the ledger's `locator_coverage` block, and
`red_line.contracts.source_claims` re-derives both counts from the records and
rejects any locator that merely restates a source's own citation key. The gap
is therefore a counted, checkable number rather than a uniform placeholder.

The short table below is a human-readable index. The project does not claim
that every row has the same evidentiary status: a primary text, a scholarly
interpretation, and an implementation standard answer different questions and
must remain labeled as such.

The source set is intentionally heterogeneous. It includes primary texts before
1900 where a historically situated question remains useful; scholarship from
China, India, the Islamic world, North Africa, Europe, Latin America, Aotearoa,
Kahnawà:ke, Africa, and global institutions; and contemporary work on
surveillance, epistemic justice, Indigenous data sovereignty, labor, data
governance, dual-use capability, export control, refusal, and software
supply-chain integrity. “Global” here means plural and
traceable, not a claim that the set is exhaustive or that all traditions converge.

## Verified source ledger

| Source | Place / period | Question carried into the audit | Boundary on interpretation | URL verified |
|---|---|---|---|---|
| Sunzi, *Art of War* | China, ancient | information, deception, strategic judgment | not a modern ethics code | [Chinese Text Project](https://ctext.org/art-of-war/laying-plans/ens) |
| Kauṭilya, trans. Olivelle | India, ancient text / 2013 edition | administration, intelligence, law, statecraft | not a universal model of legitimate rule | [Oxford Academic](https://academic.oup.com/book/8486) |
| Aristotle, *Politics* | Greece, ancient | law, constitutions, distribution of authority | historically exclusionary civic frame | [MIT Classics](https://classics.mit.edu/Aristotle/politics.html) |
| al-Fārābī, political philosophy | Central Asia / Islamic world, 10th c. | political order, knowledge, human flourishing | not a democratic or rights-equivalent framework | [Encyclopaedia Iranica](https://www.iranicaonline.org/articles/farabi-vi/) |
| Ibn Khaldūn, via Darling | North Africa / late medieval Middle East | social cohesion, justice, political power | historically situated theory of dynastic rule | [Cambridge Core](https://www.cambridge.org/core/journals/comparative-studies-in-society-and-history/article/abs/social-cohesion-asabiyya-and-justice-in-the-late-medieval-middle-east/3117D292647ECD6472E9C77AA294D2A2) |
| Machiavelli, *The Prince* | Italy, 1513 | incentives, power, institutional realism | diagnostic realism is not endorsement | [Project Gutenberg](https://www.gutenberg.org/ebooks/1232) |
| Wollstonecraft, *Vindication* | England, 1792 | education, reason, equal standing | not a complete account of intersectional justice | [Project Gutenberg](https://www.gutenberg.org/ebooks/3420) |
| Cugoano, *Thoughts and Sentiments* | Gold Coast / Black British abolitionist thought, 1787 | liberty, consent, responsibility, and the danger of self-serving moral blindness | not a generic “African ethics” representative; read through its own Atlantic context | [Stanford Encyclopedia of Philosophy](https://plato.stanford.edu/entries/cugoano/) and [University of Michigan text](https://quod.lib.umich.edu/e/eccodemo/K046227.0001.001/1%3A3?rgn=div1&view=fulltext) |
| Ostrom, *Governing the Commons* | US / global casework, 1990 | rules-in-use, monitoring, self-governance | commons cases do not automatically generalize to AI | [Cambridge University Press](https://www.cambridge.org/core/books/governing-the-commons/7AB7AE11BADA84409C34815CC288CD79) |
| Scott, *Seeing Like a State* | US / Southeast Asia, 1998 | legibility, simplification, local knowledge | legibility is a risk as well as a capability | [Yale University Press](https://yalebooks.yale.edu/book/9780300246759/seeing-like-a-state/) |
| Smith, *Decolonizing Methodologies* | Aotearoa New Zealand / Māori scholarship, 1999 | research power, extraction, self-determination | not a decorative “diversity” citation | [Royal Society Te Apārangi](https://www.royalsociety.org.nz/150th-anniversary/tetakarangi/decolonizing-methodologieslinda-tuhiwai-smith-1999) |
| Kukutai and Taylor, *Indigenous Data Sovereignty* | Aotearoa / CANZUS data governance, 2016 | collective data authority, governance, self-determined interests | not a universal consent shortcut or substitute for community authority | [ANU Press](https://press.anu.edu.au/publications/series/caepr/indigenous-data-sovereignty) |
| Nissenbaum, contextual integrity | US, 2004 | context-specific information norms | not a substitute for jurisdiction-specific law | [Washington Law Review](https://digitalcommons.law.uw.edu/wlr/vol79/iss1/10/) |
| Turner, red-line framework | organization-to-government, 2026 | precommitment, retained oversight, review, durability | source mechanism, not this project's institutional authority | [The Pond](https://turntrout.com/red-line-framework) |
| Jobin, Ienca, Vayena | global corpus, 2019 | convergence and divergence in AI principles | survey finding, not consensus proof | [Nature Machine Intelligence](https://doi.org/10.1038/s42256-019-0088-2) |
| Selbst et al., sociotechnical fairness | US / international authors, 2019 | abstraction can sever system context | not a complete fairness taxonomy | [ACM DOI](https://doi.org/10.1145/3287560.3287598) |
| Birhane, algorithmic colonization | Africa / global technology, 2020 | dependency, local needs, coloniality | not evidence that all imported systems have one effect | [DOI](https://doi.org/10.2966/scrip.170220.389) |
| Mohamed, Png, Isaac, decolonial AI | UK / US / global, 2020 | critical technical practice and power | proposal, not a certification standard | [Springer](https://doi.org/10.1007/s13347-020-00405-8) |
| African Union Data Policy Framework | Africa, 2022 | regional data governance, collective interests, and digital rights | regional policy is not interchangeable with global policy | [African Union](https://au.int/fr/node/42078) |
| UNESCO AI ethics Recommendation | global member states, 2021 | rights, dignity, and policy action | recommendation, not project compliance | [UNESCO](https://www.unesco.org/en/legal-affairs/recommendation-ethics-artificial-intelligence?hub=1063) |
| OECD AI Principles | intergovernmental, 2019 | values plus implementation guidance | principles are flexible and non-exhaustive | [OECD](https://www.oecd.org/en/topics/ai-principles.html) |
| NIST AI RMF | US public standard, 2023 | operational risk management | voluntary framework, not a legal approval | [NIST](https://www.nist.gov/itl/ai-risk-management-framework) |
| NIST Zero Trust Architecture | US public standard, 2020 | continuous verification and least privilege | network trust model, not a human-governance solution | [NIST CSRC](https://csrc.nist.gov/pubs/sp/800/207/final) |

## Claim discipline

The manuscript separates three research claim classes, with release claims
tracked separately in the publication register. Descriptive claims report what
a source says and remain source-bounded. Transfer claims state why a question is
useful for this artifact, but are explicitly interpretive. Implementation claims
state what the repository can demonstrate through code, tests, generated figures,
or rendered outputs. Release claims state what a validated source-to-render
chain demonstrates for a particular artifact. A source cannot upgrade an
interpretive transfer claim into an implementation fact, a green test suite
cannot prove a source's moral or historical adequacy, and a successful build
cannot establish an external certification.

This discipline is also the red-team response to authority-washing. Cugoano is
included as a situated primary voice and philosophical problem, not as evidence
that a single historical author represents a continent. The project
does not say that a global reading list makes a personal framework universal,
that a public beacon is automatically emancipatory, or that historical
statecraft texts are safe design templates. It says only that a broader and more
critical reading base changes which failure modes the author must confront.

## Added and deepened scholarship

The following additions strengthen the ledger where the earlier index was too
thin: situated knowledge, humility under uncertainty, community-led design,
power-aware data practice, Indigenous data sovereignty, Latin American colonial
encounter, racialized surveillance, algorithmic classification, epistemic
injustice, data colonialism, hidden labor, dual-use capability, export control,
refusal, and software supply-chain integrity. The
records are deliberately not interchangeable. A historical primary text, a
critical monograph, a preprint, and an implementation specification can each
support a different kind of claim.

| Source | Geography / period | Language, edition, genre, stable locator | Claim class | Question transferred | Non-transfer boundary | URL verified |
|---|---|---|---|---|---|---|
| Bartolomé de las Casas, *A Short Account of the Destruction of the Indies* | Spanish colonial Americas, composed 1542 / published 1552 | Spanish primary polemic; Griffin and Pagden ed./trans., Penguin 1992; Prologue and regional accounts | descriptive → transfer | how administrative and moral language can conceal violence to affected people | a Spanish cleric's account is not Indigenous testimony and does not represent Latin American consensus | [Penguin](https://www.penguin.co.uk/books/35187/a-short-account-of-the-destruction-of-the-indies-by-bartolome-de-las-casas-ed-and-trans-by-nigel-griffin-intro-anthony-pagden/9780140445626) |
| Simone Browne, *Dark Matters* | Black Atlantic / United States, 2015 | English critical monograph; Duke University Press; Introduction and chapters on racializing surveillance | descriptive → transfer | surveillance techniques have histories and distribute visibility unevenly | Black feminist surveillance analysis is not a universal risk taxonomy or a substitute for affected-community testimony | [Duke University Press](https://read.dukeupress.edu/books/book/147/Dark-MattersOn-the-Surveillance-of-Blackness) |
| Safiya Umoja Noble, *Algorithms of Oppression* | United States / global search infrastructures, 2018 | English critical monograph; NYU Press; Introduction and chapter 1 | descriptive → transfer | classification and retrieval systems can reproduce racialized hierarchy while appearing neutral | search-engine casework does not by itself establish how every model or jurisdiction behaves | [NYU Press](https://nyupress.org/9781479837243/algorithms-of-oppression/) |
| Virginia Eubanks, *Automating Inequality* | United States, 2018 | English investigative scholarship; St. Martin's Press; case studies of automated welfare and risk systems | descriptive → transfer | administrative automation can move burdens onto people with least power to contest them | United States case studies do not decide another jurisdiction's law or every automated decision | [Macmillan](https://us.macmillan.com/books/9781250074317/automatinginequality) |
| Miranda Fricker, *Epistemic Injustice* | United Kingdom / analytic philosophy, 2007 | English philosophical monograph; Oxford University Press; chapters on testimonial and hermeneutical injustice | descriptive → transfer | credibility, testimony, and interpretive resources are distributed through power | a philosophical account does not independently verify an evidence record or resolve institutional remedy | [Oxford Academic](https://academic.oup.com/book/32817) |
| Nick Couldry and Ulises A. Mejias, *The Costs of Connection* | United Kingdom, United States, and global data relations, 2019 | English critical monograph; Stanford University Press; chapters on data colonialism and political participation | descriptive → transfer | data extraction can be understood as a power relation, not only an information flow | “data colonialism” is an interpretive framework, not proof that all collection has identical effects | [Stanford University Press](https://www.sup.org/books/sociology/costs-connection) |
| Mary L. Gray and Siddharth Suri, *Ghost Work* | United States and India, 2019 | English ethnographic/technical labor study; Houghton Mifflin Harcourt; case studies of hidden platform labor | descriptive → transfer | apparently automated systems can depend on invisible human judgment and precarious labor | the studied platforms do not exhaust global labor arrangements or prove a particular project's labor conditions | [Author resource](https://marylgray.org/bio/on-demand/) |
| Miles Brundage et al., *The Malicious Use of Artificial Intelligence* | global dual-use security debate, 2018 | English research report/preprint; arXiv:1802.07228; threat taxonomy and mitigation recommendations | descriptive → transfer | dual-use capability should be evaluated across digital, physical, and political domains | a forecast is not an incident report, probability estimate, or safety guarantee for this registry | [arXiv](https://arxiv.org/abs/1802.07228) |
| Souppaya, Scarfone, and Dodson, NIST SP 800-218 SSDF 1.1 | United States public standard, 2022 | English implementation standard; final publication; practices and tasks by SSDF outcome | implementation context | software provenance, review, and build integrity are part of a security boundary | NIST vocabulary is voluntary implementation context, not Red Line compliance or APT resistance | [NIST CSRC](https://csrc.nist.gov/pubs/sp/800/218/final) |
| MITRE ATT&CK Enterprise | global public threat knowledge base, maintained/current | English technical knowledge base; Enterprise tactics and techniques pages; `T1195`, `T1078`, `T1565`, `T1491` | implementation context | name plausible adversary behavior and defensive coverage without inventing a live incident | ATT&CK mapping is not evidence that an actor targeted this project and does not replace system-specific telemetry | [MITRE ATT&CK](https://attack.mitre.org/techniques/) |
| SLSA Specification v1.2 | global open-source security collaboration, current | English implementation specification; approved v1.2; build/source tracks and provenance sections | implementation context | provenance, attestations, and source/build separation can structure future release controls | a specification page is not a signed attestation and this project does not claim SLSA level achievement | [SLSA v1.2](https://slsa.dev/spec/v1.2/) |
| Donna Haraway, “Situated Knowledges” | United States / feminist science studies, 1988 | English journal article; *Feminist Studies* 14(3), pp. 575–599 | descriptive → transfer | name the standpoint and partial perspective behind a claim | situated perspective is not relativism and does not replace reviewable evidence | [JSTOR](https://www.jstor.org/stable/3178066) |
| Sheila Jasanoff, “Technologies of Humility” | United States / science and technology studies, 2003 | English journal article; *Minerva* 41(3), pp. 223–244 | descriptive → transfer | keep framing, vulnerability, distribution, and learning visible under uncertainty | a humility lens is not a local evaluator, public mandate, or legal finding | [DOI](https://doi.org/10.1023/A:1025557512320) |
| Sasha Costanza-Chock, *Design Justice* | United States / community-led design, 2020 | English open-access monograph; MIT Press; chapters on power and participation | descriptive → transfer | ask who is centered, burdened, excluded, and able to contest a design | community-led design questions do not establish consent, safety, or a universal process | [MIT Press](https://mitpress.mit.edu/9780262043458/design-justice) |
| Catherine D’Ignazio and Lauren F. Klein, *Data Feminism* | United States / data studies, 2020 | English monograph; MIT Press; introduction and principles | descriptive → transfer | expose power, classification, and invisible labor hidden by “the data” | power-aware data practice is not an exhaustive ethics standard or proof about this action | [MIT Press](https://mitpress.mit.edu/9780262044004/data-feminism/) |
| Tahu Kukutai and John Taylor, eds., *Indigenous Data Sovereignty* | Aotearoa / CANZUS Indigenous data governance, 2016 | English edited research monograph; ANU Press; opening agenda and governance chapters | descriptive → transfer | name collective authority, governance, and self-determined interests when data are collected or reused | collective data sovereignty is not a universal consent shortcut or substitute for the affected community's authority | [ANU Press](https://press.anu.edu.au/publications/series/caepr/indigenous-data-sovereignty) |
| The Wassenaar Arrangement, *List of Dual-Use Goods and Technologies and Munitions List* | multilateral export-control regime, 1996–present; lists as amended December 2025 | English control list; Category 5 Part 2 information-security entries and the 2013 intrusion-software addition | descriptive → transfer | a capability-keyed control list is a category boundary maintained by states, and its definitions can sweep in the defensive work they were meant to spare | a control list is not a personal ethics, does not bind this project, and its categories are not evidence that any capability here is controlled | [Wassenaar Arrangement](https://www.wassenaar.org/control-lists/) |
| Elisa D. Harris, ed., *Governance of Dual-Use Technologies: Theory and Practice* | United States / nuclear, biological, and cyber comparison, 2016 | English edited policy study; American Academy of Arts and Sciences; introductory and concluding chapters | descriptive → transfer | dual-use governance is layered — treaty regimes, export controls, institutional review, and researcher judgment each carry a different part of the load | a comparative policy study does not evaluate this artifact and does not establish that a personal layer is sufficient | [American Academy of Arts and Sciences](https://www.amacad.org/publication/governance-dual-use-technologies-theory-and-practice) |
| National Research Council, *Biotechnology Research in an Age of Terrorism* (Fink report) | United States public science policy, 2004 | English consensus committee report; National Academies Press; the seven experiments of concern and the self-governance recommendations | descriptive → transfer | researcher-level judgment before a project starts is a named governance layer, not a substitute for institutional review | a biosecurity report is not a warrant for a software refusal registry, and self-governance was proposed there alongside institutional review, never instead of it | [National Academies Press](https://nap.nationalacademies.org/catalog/10827/biotechnology-research-in-an-age-of-terrorism) |
| Jonathan Zong and J. Nathan Matias, “Data Refusal from Below” | United States / responsible computing, 2024 | English peer-reviewed article; *ACM Journal on Responsible Computing* 1(1), pp. 1–23 | descriptive → transfer | refusal has structure worth naming: autonomy, timing, power, and who bears its cost | the framework is written from the standpoint of people refusing an institution's collection; a practitioner declining paid work is not refusal from below and must not borrow its moral standing | [ACM DOI](https://doi.org/10.1145/3630107) |
| Penny Crofts and Honni van Rijswijk, “Negotiating ‘Evil’: Google, Project Maven and the Corporate Form” | Australia / United States technology-sector case, 2020 | English peer-reviewed article; *Law, Technology and Humans* 2(1), pp. 75–90 | descriptive → transfer | collective refusal of military AI work is documented, effective in the moment, and readily absorbed back into a corporate form | a single documented episode is not a base rate for refusal, and a company's stated principles are not evidence of what it later built | [DOI](https://doi.org/10.5204/lthj.v2i1.1313) |
| Audra Simpson, *Mohawk Interruptus* | Kahnawà:ke / settler-colonial North America, 2014 | English ethnographic and political monograph; Duke University Press; chapters developing refusal and ethnographic refusal | descriptive → transfer | refusal can be a positive political stance with its own content, not merely the absence of consent | ethnographic and Indigenous refusal answers to sovereignty and settler-colonial history; it is cited here for the concept and explicitly not as a template for a practitioner declining work | [Duke University Press](https://www.dukeupress.edu/mohawk-interruptus) |

The additions change the method in two ways. First, affected parties are not
treated as a single abstract “user”: racialized surveillance, administrative
classification, hidden labor, data extraction, and collective data authority make
power and contestability explicit questions for the intake. Second, security is
not reduced to a green test suite: software provenance and artifact integrity become release
questions, while NIST, ATT&CK, and SLSA remain implementation vocabularies
rather than evidence that the personal boundary is legally or operationally
complete.

The export-control and refusal sources are the two that most directly test this
project's own framing, and they cut in opposite directions. Wassenaar, Harris,
and the Fink report describe governance that is institutional, negotiated, and
enforceable, which makes the personal layer look small; Zong and Matias, Crofts
and van Rijswijk, and Simpson describe refusal as a structured act with costs
and standing, which makes the personal layer look like something other than a
private preference. Red Line sits between them and claims neither. It is not a
control regime and does not bind anyone; it is not refusal from below and does
not carry that moral standing. What it takes from both is the demand to say who
refuses, on what evidence, at what cost, and with what power to be overruled.

The new scholarship makes the translation layer more intelligent rather than
merely longer. Haraway supplies a discipline of situated perspective; Jasanoff
turns humility into four review questions—framing, vulnerability, distribution,
and learning; Costanza-Chock makes participation and contestability design
requirements; D’Ignazio and Klein keep classification, power, and invisible
labor inside the data boundary; and Kukutai and Taylor add collective authority
and self-determined governance to the data question. Red Line does not import
these works as policy. It uses them to sharpen what an operator must ask before
claiming that a local record is enough: whose perspective is missing, who bears
the cost, who can contest the decision, what collective authority applies, and
what labor or classification the artifact hides.
