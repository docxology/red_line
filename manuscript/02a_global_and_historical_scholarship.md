# Global and Historical Scholarship: Situated Questions, Not a Universal Lineage {#sec:scholarship}

The reading base is an audit surface, not an authority bundle. The selection
protocol prefers primary texts, scholarly editions, publisher pages, and
official institutional sources; includes pre-1900 materials when their
question remains useful; and records the boundary on every transfer. For every
one of its 45 sources, the ledger in `docs/research-method.md` records place,
period, the question carried into the audit, the non-transfer boundary, and a
verified publisher or primary-text URL. Those 45 sources sit in 44 table rows:
Kukutai and Taylor is listed in both tables, and the Cugoano row cites the
primary text alongside its *Stanford Encyclopedia* entry.

Genre, language or translation, and a stable locator are recorded only for the
22 sources in the deepened second table; the machine-readable ledger at
`data/source_claims.json` marks the remaining 23 `not recorded` rather than
filling the field with boilerplate, and `validate_source_claims` rejects any
locator derivable from a source's own citation key.

## Before 1900: refusal, rule, knowledge, and power

Sunzi's *Art of War* makes information, deception, timing, and judgment
operational questions [@sunzi1910artofwar]. Kauṭilya's *Arthaśāstra*, in Patrick
Olivelle's scholarly translation, joins law, administration, intelligence, and
the practical limits of rule [@kautilya2013arthasastra]. Aristotle's *Politics*
asks how constitutions distribute authority, while al-Fārābī's political
philosophy links knowledge, political order, and human flourishing
[@aristotle350politics; @mahdi2000farabipolitical]. Ibn Khaldūn's account of
`asabiyya and justice adds a historically situated analysis of cohesion and
power [@darling2007asabiyya].

These texts are not a single tradition. Machiavelli supplies an uncomfortable
test about incentives and power [@machiavelli1513prince]; Wollstonecraft asks
whether a discourse of reason can survive the denial of equal intellectual
standing [@wollstonecraft1792vindication]. Ottobah Cugoano's
late-eighteenth-century abolitionist work adds a Black Atlantic voice on
liberty, consent, responsibility, and the
self-deception that allows beneficiaries of coercion to call it legitimate
[@cugoano1787thoughts; @cugoano2025sep]. Cugoano is not used as a generic
representative of “African ethics”; he is read in his own Atlantic, religious,
abolitionist, and philosophical context.

The transfer from these sources is a set of questions: who acts, under what
authority, with what knowledge, toward whom, with what power to withdraw or
repair, and who bears the cost when a claim is wrong? None supplies a modern
rights framework, a universal AI policy, or an endorsement of this registry.

The Latin American record adds a necessary asymmetry. Bartolomé de las Casas's
account is a colonial-era Spanish cleric's polemic about violence in the
Americas, not Indigenous testimony and not a representative voice for the
region [@lascasas1552brief]. Its narrow use here is diagnostic: an institution
can describe its own authority as administration, improvement, or salvation
while affected people bear coercive costs. The source therefore sharpens the
intake questions about affected parties and power; it does not supply a
universal theory of consent or authorize the author's categories.

## Modern critical and institutional scholarship

Elinor Ostrom shifts attention from abstract market/state choices toward
rules-in-use, monitoring, graduated responses, and situated knowledge
[@ostrom1990commons]. James C. Scott shows how administrative legibility can
simplify a system while erasing local knowledge [@scott1998seeingstate]. Linda
Tuhiwai Smith makes research power and extraction part of method
[@smith1999decolonizing]. Helen Nissenbaum's contextual integrity rejects a
context-free account of information flow [@nissenbaum2004contextual]. Together
they require Red Line to treat provenance, affected parties, downstream use,
and public legibility as context-dependent rather than as checkboxes that
automatically confer legitimacy.

Jobin, Ienca, and Vayena show convergence and divergence among AI principles;
Selbst and colleagues warn that abstraction can sever technical categories from
their sociotechnical context [@jobin2019global; @selbst2019fairness]. Birhane,
and Mohamed, Png, and Isaac, put coloniality, dependence, local knowledge, and
critical technical practice into the AI governance conversation
[@birhane2020colonization; @mohamed2020decolonial]. These sources constrain
the project's temptation to call a readable registry universal or emancipatory.

The surveillance and classification literature makes the same warning more
concrete. Browne traces surveillance of Blackness through historical and
contemporary practices [@browne2015dark]; Noble shows how apparently neutral
search infrastructures can reproduce racialized hierarchy [@noble2018algorithms];
and Eubanks documents how automated administrative systems can concentrate
burdens on people with little power to contest them [@eubanks2018automating].
Fricker supplies a distinct epistemic question—who is treated as a credible
knower and who lacks interpretive resources [@fricker2007epistemic]—while
Couldry and Mejias frame data extraction as a relation of power rather than a
mere technical flow [@couldry2019costs]. Gray and Suri add hidden human labor
to the system boundary [@gray2019ghost]. Together these works justify keeping
affected parties, provenance, downstream transfer, and human control as
separate intake dimensions. They do not prove that any particular action is
unlawful or unsafe.

Four further works make the bridge from scholarship to operating intelligence
explicit. Haraway's account of situated knowledges requires the author to name
the standpoint and partial perspective behind a claim rather than perform a
view from nowhere [@haraway1988situated]. Jasanoff's “technologies of humility”
organize uncertainty around framing, vulnerability, distribution, and learning
[@jasanoff2003humility]. Costanza-Chock's design-justice practice asks who is
centered, burdened, excluded, or able to contest a design
[@costanzachock2020design]. D'Ignazio and Klein add a power-aware account of
data, classification, and invisible labor; data do not speak for themselves
[@dignazioklein2020data].

The transfer is operational, not ornamental. These questions attach to the
intake as follows: standpoint and missing perspective sharpen provenance and
affected parties; framing and vulnerability sharpen purpose, end use, and
unknowns; participation and contestability sharpen human control and downstream
transfer; and power, classification, and labor sharpen capability scope. None
of the four sources can turn a self-assertion into verified evidence or make a
local result a public authorization. Their value is that they make the operator
ask a better question before the evaluator returns a bounded answer.

Kukutai and Taylor add a collective-authority test that individual consent does
not settle: when data concern an Indigenous people or community, who has standing
to govern collection, interpretation, and downstream use?
[@kukutaitaylor2016ids] This is a question for `affected_parties`,
`data_provenance`, `legal_basis`, and `downstream_transfer`, not a new universal
permission rule. The source is especially relevant because it prevents the
intake from treating data sovereignty as a property of an individual record
alone; it does not replace the authority of the affected community or establish
that a particular data use is legitimate.

![Scholarship becomes intelligence only when it changes the intake. This bridge maps four added works to concrete questions about perspective, uncertainty, contestability, classification, and hidden labor. The red gap is deliberate: sources widen the audit surface but do not authorize an action, verify an intake field, or replace affected-party testimony.](../output/figures/scholarship_intake_bridge.png){#fig:scholarship-intake-bridge width=95%}

## Export control and the refusal of work

Two literatures sit closer to this artifact than any cited so far, and neither
of them flatters it. The first governs dual-use capability from above; the
second describes refusing work from below. Red Line is neither, and saying so
precisely is more useful than claiming kinship with both.

Export control is the mature institutional form of the question this registry
asks. The Wassenaar Arrangement maintains a list of dual-use goods and
technologies that participating states implement in national law
[@wassenaar2025duallist]. Its structure is instructive twice over. It keys
control to declared *capability categories* rather than to an assessment of the
person applying for a licence, which is the same lexical bet Red Line makes and
the same one [@sec:limitations] concedes is escapable by description. And its
2013 addition of "intrusion software" is the reference case for what goes wrong
when a capability definition is drawn slightly too wide: a category meant to
constrain commercial spyware also described the exchange of defensive research,
and the definition had to be revisited. A personal registry is smaller than a
multilateral regime in every respect that matters, but it
inherits that failure mode exactly, which is why the scope vocabulary in
[@sec:red-lines] is enumerable and printed in full rather than described.

Harris's comparative study of nuclear, biological, and cyber governance sets
out the layering these regimes depend on: treaty obligations, export controls,
institutional review, and the judgment of the researcher, each carrying part of
the load and none of them sufficient alone [@harris2016dualuse]. The Fink
report made the last of those layers explicit for the life sciences, naming
seven categories of experiment that should trigger review and arguing that the
scientific community's own screening is a governance layer rather than an
informal habit [@nrc2004biotechnology]. That is the strongest available warrant
for an instrument like this one, and it is also a bounded one: the report
proposed researcher judgment *alongside* institutional review boards, never
instead of them, and Red Line has no board. What transfers is the proposition
that a practitioner's pre-commitment is a recognized layer. What does not
transfer is any suggestion that the layer is adequate by itself.

The refusal literature supplies the vocabulary the registry was missing for its
own act. Zong and Matias give refusal a structure — autonomy, timing, power,
and cost — written deliberately from the standpoint of people refusing an
institution's data collection rather than the institution seeking compliance
[@zongmatias2024refusal]. Their four facets are the sharpest available test of
this instrument: it is individual rather than collective on autonomy,
proactive rather than reactive on timing, weak on power because it binds only
its author, and it redistributes cost onto that author alone. The transfer
stops firmly at standing. Refusal from below is refusal by those with the least
power in a relation; a practitioner declining paid work is not that, and
borrowing the term's moral weight would be exactly the authority-washing this
section exists to prevent. The same boundary applies with more force to
Simpson, whose account of refusal as a positive political stance — a
sovereignty claim with its own content, not the absence of consent — belongs to
Kahnawà:ke and to settler-colonial history [@simpson2014mohawk]. The concept
that a "no" can be generative rather than merely negative is what this project
takes; the standing is not available to be taken.

Between the two literatures sits the one documented case of collective refusal
in this industry. Crofts and van Rijswijk trace Google's Project Maven
episode: thousands of workers refused military AI work, the contract lapsed,
principles were published — and the corporate form absorbed the objection
intact [@crofts2020maven]. The episode is evidence that refusal is possible
and legible, not a base rate. For a single practitioner the lesson is
narrower still: refusal held collectively had leverage refusal held alone
does not, which is the honest reason this artifact claims auditability
rather than effect.

## Selection limits and positionality

This is a curated conceptual audit, not a systematic review, a representative
survey of world traditions, or a substitute for consultation with people
affected by a proposed system. The selection is constrained by sources available
in accessible editions and translations, the author's questions, and the need to
keep each transfer legible. Geographic variety is therefore a corrective to a
narrow lineage, not a coverage statistic. A source from a region is not a proxy
for everyone in that region; a translated text is not identical to its language
of composition; and placing sources in one figure does not make them equivalent.

The consequence is methodological restraint: the reading base can expand the
intake questions—about power, classification, labor, consent, and
contestability—but it cannot supply affected-party testimony, jurisdiction-specific
legal review, or independent verification of an evidence record. Those remain
separate obligations.

For dual-use security, Brundage and colleagues map malicious-use concerns
across digital, physical, and political domains and argue for prevention and
mitigation rather than a single prediction [@brundage2018malicious]. That
supports a capability-and-transfer question in Red Line, not a claim that a
lexical registry forecasts threat likelihood. Three engineering references sit
beside it and are taken up again in [@sec:canary], where they describe what
this project does and does not do: the NIST Secure Software Development
Framework, MITRE ATT&CK, and SLSA v1.2 [@souppaya2022ssdf; @mitre2026attack;
@slsa2026]. Here they enter the reading base for one reason only — they name
the questions to ask about provenance, adversary behavior, and build
attestation. Neither a standard nor a threat catalog is evidence that Red Line
is secure, legally compliant, or resistant to an advanced persistent threat.

UNESCO, the OECD, and the African Union provide policy comparison points; NIST
provides operational vocabularies for risk management and continuous
verification [@unesco2021recommendation; @oecd2019principles;
@au2022datapolicy; @tabassi2023airmf; @rose2020zerotrust]. They are not
certifications of Red Line and cannot substitute for the project's own evidence
gate.

![The method is assembled from many situated questions, not one universal lineage. The cards group pre-1900 primary texts, historical scholarship, critical methodology, collective data-governance work, and contemporary standards by broad period and region. Direct labels state the question carried into Red Line; placement does not imply direct influence, equivalence, or endorsement. The figure deliberately includes an interpretive boundary: a source can widen the audit surface without authorizing the personal refusal registry. It is a provenance and humility device, not a measurement of global coverage or scholarly quality.](../output/figures/scholarship_reading_map.png){#fig:scholarship-reading-map width=95%}

![Every source transfer carries a question and a stopping point. This deterministic matrix makes the claim discipline visible: descriptive, transfer, and implementation claims are separated, and each source row names the boundary beyond which it is not used. Collective data authority appears alongside individual consent and contextual privacy; the visual does not score traditions, demonstrate consensus, or make the reading base universal. It is designed for the PDF and narrow HTML layout with direct labels, repeated color-and-text encodings, and a caption that remains meaningful if the image is unavailable.](../output/figures/scholarship_transfer_matrix.png){#fig:scholarship-transfer-matrix width=95%}
