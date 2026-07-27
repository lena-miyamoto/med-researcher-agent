"""Create / validate the therapy methodology reference in med-db/.

Idempotent — skips if files already exist (unless --force).
The methodology data is curated from primary texts, systematic reviews,
and authoritative clinical guidelines.  Each methodology entry includes
key figures, historical context, core concepts, therapeutic techniques,
evidence base, critique, and references.

Usage:
    uv run med-db-setup-therapy-methods           # create if missing
    uv run med-db-setup-therapy-methods --force    # regenerate
    uv run med-db-setup-therapy-methods --verify-only  # smoke test
"""

import argparse
import json
import sys
from pathlib import Path

import utils
from utils import REPO_ROOT, MED_DB
GUIDELINE_DIR = MED_DB / "guidelines" / "therapy-methodologies"
SOURCE_MD = GUIDELINE_DIR / "source.md"
METHODOLOGIES_JSON = GUIDELINE_DIR / "methodologies.json"


# ---------------------------------------------------------------------------
# Methodology data
# ---------------------------------------------------------------------------

def _build_methodologies_categorized():
    """Return the complete methodology reference data."""
    return {
        "title": "Clinical Therapy Methodology Guidelines",
        "publisher": "Compiled from primary texts, systematic reviews, and authoritative clinical guidelines",
        "access_date": "2026-07-17",
        "description": (
            "Comprehensive reference covering 11 therapy methodologies used by the "
            "psychotherapist agent. Grouped into four categories: Foundational Frameworks, "
            "Integrative Modalities, Broader Critical Canon, and Clinical Modalities."
        ),
        "license_note": (
            "Content is curated from publicly available academic and clinical sources. "
            "Individual methodology descriptions synthesize primary texts, systematic "
            "reviews, and recognized clinical practice guidelines."
        ),
        "categories": [
            {
                "name": "Foundational Frameworks",
                "description": (
                    "The theoretical ground on which the psychotherapist agent's practice stands. "
                    "These frameworks provide the critical lens through which all clinical work is viewed."
                ),
                "methodologies": [
                    _liberation_psychology(),
                    _critical_psychology(),
                ],
            },
            {
                "name": "Integrative Modalities",
                "description": (
                    "Therapeutic approaches that integrate directly with the foundational frameworks. "
                    "These modalities provide specific clinical techniques and conceptual tools."
                ),
                "methodologies": [
                    _narrative_therapy(),
                    _systemic_therapy(),
                ],
            },
            {
                "name": "Broader Critical Canon",
                "description": (
                    "Critical traditions that inform the psychotherapist agent's analysis of power, "
                    "identity, and social context. Drawn on as clinically relevant."
                ),
                "methodologies": [
                    _postcolonial_decolonial(),
                    _feminist_queer(),
                    _trauma_informed_care(),
                    _disability_justice_neurodiversity(),
                    _mad_studies(),
                ],
            },
            {
                "name": "Clinical Modalities",
                "description": (
                    "Evidence-based therapeutic modalities used for technique selection and "
                    "intervention planning within the critical framework."
                ),
                "methodologies": [
                    _cognitive_behavioral_therapy(),
                    _acceptance_commitment_therapy(),
                ],
            },
        ],
    }


# --- Foundational Frameworks ---

def _liberation_psychology():
    return {
        "name": "Liberation Psychology",
        "slug": "liberation-psychology",
        "key_figures": [
            {"name": "Ignacio Martín-Baró", "role": "Founder", "years": "1942–1989"},
            {"name": "Paulo Freire", "role": "Pedagogical foundation", "years": "1921–1997"},
        ],
        "origin": "El Salvador, 1970s–1980s",
        "historical_context": (
            "Liberation Psychology emerged in the context of the Salvadoran Civil War (1979–1992), "
            "extreme economic inequality, and U.S.-backed state violence. Martín-Baró, a Spanish-born "
            "Jesuit priest and social psychologist trained at the University of Chicago, developed the "
            "framework at the Universidad Centroamericana (UCA) in San Salvador. He was assassinated "
            "by a government-aligned death squad on November 16, 1989, alongside five fellow Jesuits, "
            "their housekeeper, and her daughter. His famous words to a North American colleague: "
            "'In your country, it's publish or perish. In ours, it's publish and perish.'"
        ),
        "key_texts": [
            "Martín-Baró, I. (1994). *Writings for a Liberation Psychology* (A. Aron & S. Corne, Eds.). Harvard University Press.",
            "Freire, P. (1970). *Pedagogy of the Oppressed*. Continuum.",
        ],
        "core_concepts": [
            {
                "name": "Preferential option for the oppressed",
                "description": (
                    "Psychology is not politically neutral. Mainstream psychology has historically "
                    "served dominant groups by locating distress within individuals and ignoring "
                    "structural violence. Liberation Psychology centers the experiences of oppressed "
                    "communities and works toward collective liberation, not just individual adjustment."
                ),
            },
            {
                "name": "De-ideologizing psychology",
                "description": (
                    "Everyday psychological concepts ('mental illness,' 'personality disorder,' "
                    "'maladaptive coping') can function as ideology — they naturalize conditions "
                    "produced by injustice and make them appear as individual pathology. The "
                    "psychologist's task includes examining which interests a given psychological "
                    "concept serves."
                ),
            },
            {
                "name": "Conscientization (concientización)",
                "description": (
                    "From Freire: the process by which people become aware of the social, political, "
                    "and economic contradictions that shape their lives and develop the capacity to "
                    "act against oppressive elements. A core therapeutic aim is helping clients "
                    "understand the social roots of their distress — not to minimize agency, but to "
                    "locate it accurately."
                ),
            },
            {
                "name": "Recovery of historical memory",
                "description": (
                    "Personal distress is often connected to collective trauma, historical injustice, "
                    "and intergenerational transmission of harm. Clinical formulation should consider "
                    "what has been silenced, erased, or disenfranchised."
                ),
            },
            {
                "name": "Virtues of the people (virtudes populares)",
                "description": (
                    "Martín-Baró's call to recognize the strengths, resilience, and knowledge present "
                    "in oppressed communities — not just deficits and symptoms. Every clinical "
                    "formulation includes a strengths assessment grounded in the client's cultural "
                    "and community context."
                ),
            },
        ],
        "therapeutic_stance": (
            "The therapist is not a neutral technician but an engaged participant in the struggle "
            "for liberation. The therapeutic relationship models solidarity rather than clinical "
            "detachment. The therapist works alongside the client to understand how structural "
            "forces shape their distress, reduce self-blame, and identify paths to collective as "
            "well as individual action."
        ),
        "techniques": [
            "Problem-posing dialogue (Freirean) instead of expert-led interpretation",
            "Mapping connections between personal distress and structural conditions",
            "Strengths assessment grounded in community and cultural resources",
            "Collective problem-solving and community connection as therapeutic intervention",
            "Critical analysis of diagnostic labels and their social functions",
        ],
        "evidence_base": (
            "Liberation Psychology emphasizes praxis — the integration of theory, action, and "
            "reflection — over controlled trials. Evidence is drawn from community-based participatory "
            "research, testimonio methodology, and documented outcomes in post-conflict and "
            "community mental health settings across Latin America, South Africa, and Ireland. "
            "Quantitative outcome research is limited and largely incompatible with the framework's "
            "epistemological commitments."
        ),
        "critique": (
            "Critics argue the framework is more political than clinical, risks imposing a political "
            "framework on clients who may not share it, and lacks systematic outcome research. "
            "Proponents respond that all therapy is political — Liberation Psychology is simply "
            "transparent about its commitments rather than hiding them behind claims of neutrality."
        ),
        "relationship_to_other_methods": (
            "Foundation for Critical Psychology and informs the entire broader critical canon. "
            "Shares with Narrative Therapy a focus on dominant stories and re-authoring. "
            "Compatible with CBT/ACT techniques when applied within a critical, context-aware frame. "
            "The preferential option for the oppressed is the ethical ground for Feminist, "
            "Postcolonial, Disability Justice, and Mad Studies approaches."
        ),
    }


def _critical_psychology():
    return {
        "name": "Critical Psychology",
        "slug": "critical-psychology",
        "key_figures": [
            {"name": "Klaus Holzkamp", "role": "Founder of German Critical Psychology", "years": "1927–1995"},
            {"name": "Ian Parker", "role": "British critical psychologist", "years": "b. 1956"},
        ],
        "origin": "Free University of West Berlin, 1960s–1970s",
        "historical_context": (
            "German Critical Psychology (Kritische Psychologie) emerged from the student movement "
            "at the Free University of West Berlin in the late 1960s. Holzkamp, initially a "
            "mainstream experimental psychologist, underwent a radical reorientation after engaging "
            "with Marx's social theory and the cultural-historical psychology of Vygotsky and "
            "Leontiev. His magnum opus, *Grundlegung der Psychologie* (Foundations of Psychology, "
            "1983), is a comprehensive attempt to reconstruct academic psychology on entirely new "
            "theoretical and methodological foundations. The approach is also known as Psychology "
            "from the Standpoint of the Subject (PSS). Ian Parker's work extended critical "
            "psychology into the Anglophone world, connecting it with discourse analysis, "
            "Foucauldian critique, and the broader critical tradition."
        ),
        "key_texts": [
            "Holzkamp, K. (1983). *Grundlegung der Psychologie*. Campus Verlag.",
            "Holzkamp, K. (2013). *Psychology from the Standpoint of the Subject: Selected Writings* (A. Boreham & E. Schraube, Eds.). Palgrave Macmillan.",
            "Parker, I. (2007). *Revolution in Psychology: Alienation to Emancipation*. Pluto Press.",
        ],
        "core_concepts": [
            {
                "name": "Subjectivity as socially mediated",
                "description": (
                    "Human experience is always constituted through social relations, material "
                    "conditions, and historical context. There is no 'inner' psyche separable from "
                    "its social world. Psychological phenomena — emotions, thoughts, symptoms — are "
                    "forms of social action and social meaning, not purely internal events."
                ),
            },
            {
                "name": "Agency (Handlungsfähigkeit)",
                "description": (
                    "The central psychological category: the human capacity to gain control over "
                    "the conditions of one's own life in cooperation with others. Agency mediates "
                    "between individual and societal life-sustaining activities. The quality of a "
                    "person's existential orientation is intrinsically linked to the type and degree "
                    "of agency they can exercise."
                ),
            },
            {
                "name": "Generalized vs. restrictive agency",
                "description": (
                    "Generalized agency: expanding influence over life conditions through forming "
                    "alliances and working with others to change restrictive circumstances. "
                    "Restrictive agency: accommodating oneself to existing power relations, seeking "
                    "short-term security at the cost of long-term life interests — a contradiction "
                    "Holzkamp calls 'self-hostility,' involving passing suppression on to others "
                    "who are even more dependent."
                ),
            },
            {
                "name": "Reason discourse vs. conditioning discourse",
                "description": (
                    "In contrast to traditional psychology's conditioning discourse (cause-effect, "
                    "stimulus-response), Critical Psychology proposes a reason discourse. Humans do "
                    "not merely react to stimuli; they have subjective reasons for action, grounded "
                    "in their first-person perspective. Research must be conducted from the standpoint "
                    "of the subject, recognizing intersubjectivity — all subjects are coequal centers "
                    "of intentionality whose reasons are communicable and negotiable."
                ),
            },
            {
                "name": "Critique of 'variable psychology'",
                "description": (
                    "Mainstream research that isolates variables (e.g., 'self-esteem,' 'rumination,' "
                    "'social support') from their social context produces decontextualized knowledge "
                    "that can obscure more than it reveals. Integrate nomothetic findings with "
                    "idiographic understanding of the specific person in their specific context."
                ),
            },
            {
                "name": "Power as central",
                "description": (
                    "Power differences — material, institutional, discursive — shape what can be "
                    "felt, said, and done. A clinical formulation that does not include power "
                    "analysis is incomplete."
                ),
            },
        ],
        "therapeutic_stance": (
            "The therapist works from the first-person standpoint, seeking to understand the "
            "client's subjective reasons for action rather than explaining behavior through "
            "external causal frameworks. The therapeutic relationship is collaborative and "
            "co-investigative — therapist and client together analyze how social conditions "
            "shape possibilities for agency. The therapist explicitly examines power dynamics "
            "within the therapeutic relationship itself."
        ),
        "techniques": [
            "Analysis of the client's possibilities for agency within their specific social context",
            "Identifying restrictive vs. generalized patterns of coping",
            "Deconstructing psychological concepts that serve ideological functions",
            "Connecting individual emotional experience to social-structural conditions",
            "Supporting the client's movement from restrictive to generalized agency",
        ],
        "evidence_base": (
            "Like Liberation Psychology, Critical Psychology prioritizes theoretical coherence "
            "and praxis over randomized controlled trials. The German tradition produced extensive "
            "theoretical scholarship and qualitative research. The framework is fundamentally "
            "critical of the RCT paradigm as decontextualized and ideologically loaded. Evidence "
            "is drawn from qualitative research, action research, and theoretical analysis."
        ),
        "critique": (
            "Often regarded as inaccessible due to dense theoretical language and Marxist "
            "foundations. Limited penetration into mainstream clinical training. The strong "
            "rejection of quantitative methods can make dialogue with mainstream research "
            "difficult. May be experienced as overly intellectualized in direct clinical work."
        ),
        "relationship_to_other_methods": (
            "Extends Liberation Psychology's political analysis with a rigorous theory of "
            "subjectivity and agency. The critique of 'variable psychology' informs the "
            "psychotherapist agent's approach to evidence. Connects with Systemic Therapy's "
            "emphasis on context over intrapsychic explanation. The reason discourse aligns "
            "with Narrative Therapy's emphasis on meaning-making."
        ),
    }


# --- Integrative Modalities ---

def _narrative_therapy():
    return {
        "name": "Narrative Therapy",
        "slug": "narrative-therapy",
        "key_figures": [
            {"name": "Michael White", "role": "Co-founder", "years": "1948–2008"},
            {"name": "David Epston", "role": "Co-founder", "years": "b. 1944"},
        ],
        "origin": "Australia and New Zealand, 1980s–1990s",
        "historical_context": (
            "Michael White, an Australian social worker, and David Epston, a New Zealand family "
            "therapist, developed narrative therapy through their collaboration beginning in the "
            "late 1980s. Their foundational text, *Narrative Means to Therapeutic Ends* (1990), "
            "established them as leaders in the postmodern turn in psychotherapy. The approach "
            "draws on diverse intellectual sources: literary theory, cultural anthropology, "
            "cybernetics, feminism, and particularly the work of Michel Foucault on knowledge, "
            "power, and the normalizing effects of modern institutions."
        ),
        "key_texts": [
            "White, M., & Epston, D. (1990). *Narrative Means to Therapeutic Ends*. W. W. Norton.",
            "White, M. (2007). *Maps of Narrative Practice*. W. W. Norton.",
        ],
        "core_concepts": [
            {
                "name": "Externalizing conversations",
                "description": (
                    "'The person is not the problem; the problem is the problem.' Externalizing "
                    "separates the client from the problem-saturated story. The therapist helps "
                    "the client objectify and sometimes personify the problem as a separate entity, "
                    "reducing blame and shame. This shifts the clinical question from 'what's wrong "
                    "with this person?' to 'how does this problem operate in this person's life, "
                    "and how has this person resisted it?'"
                ),
            },
            {
                "name": "Re-authoring",
                "description": (
                    "Helping clients identify unique outcomes — moments when the problem's influence "
                    "was weaker or absent — and build alternative narratives from these. The aim is "
                    "not to impose a 'healthy' story but to support the client in authoring a "
                    "preferred narrative grounded in their values and lived experience."
                ),
            },
            {
                "name": "Deconstructing dominant discourses",
                "description": (
                    "Exploring how cultural stories (about gender, success, family, normality) "
                    "shape the client's experience of distress. 'Where did this idea come from "
                    "that you're failing? Whose standards are these?' Problems are understood as "
                    "residing in discursive and cultural spaces that legitimize them, not inside "
                    "individuals."
                ),
            },
            {
                "name": "Therapeutic documents",
                "description": (
                    "White and Epston innovatively used personal letters to clients, contracts, "
                    "and certificates as therapeutic interventions — creating written reframes "
                    "that clients could revisit and that gave tangible form to new narratives."
                ),
            },
            {
                "name": "Text analogy",
                "description": (
                    "Human problems are conceptualized using literary metaphors — life as a 'text' "
                    "with multiple possible readings. The therapist helps the client discover "
                    "subjugated meanings and alternative readings of their experience."
                ),
            },
        ],
        "therapeutic_stance": (
            "The therapist is a collaborative co-author, not an expert diagnostician. The stance "
            "is decentered but influential — the therapist brings skills in asking questions that "
            "open space for alternative stories, but the client is the expert on their own life. "
            "The therapist actively refuses to locate problems within the person and works to "
            "make visible the cultural discourses that sustain problem-saturated stories."
        ),
        "techniques": [
            "Externalizing language: 'What does the anxiety convince you of?' not 'Why are you so anxious?'",
            "Mapping the problem's influence on the person's life and relationships",
            "Identifying and thickening unique outcomes through detailed questioning",
            "Therapeutic letters and documents that consolidate new narratives",
            "Outsider witness practices — recruiting supportive audiences for new stories",
            "Remembering conversations that reconnect clients with important figures from their history",
        ],
        "evidence_base": (
            "A growing body of outcome research supports narrative therapy, particularly for "
            "depression, trauma, eating disorders, and family conflict. The evidence base is "
            "smaller than for CBT due to the approach's epistemological stance — narrative "
            "therapists have historically prioritized qualitative and practice-based evidence "
            "over RCTs. Meta-analyses show moderate effect sizes; methodological quality of "
            "studies is variable."
        ),
        "critique": (
            "The strong social constructionist stance can be experienced as dismissive of "
            "biological and material realities. Some clients find the externalizing language "
            "contrived. Limited applicability with clients who have reduced verbal or abstract "
            "thinking capacity. The decentered therapist stance may not provide enough structure "
            "for clients in acute crisis."
        ),
        "relationship_to_other_methods": (
            "Highly compatible with Liberation and Critical Psychology — the deconstruction of "
            "dominant discourses directly serves conscientization. Complements Systemic Therapy's "
            "relational focus with attention to meaning-making. Techniques can be integrated with "
            "ACT (both emphasize distancing from problem-saturated cognitive content). Externalizing "
            "conversations are particularly useful for de-pathologizing neurodivergent experience."
        ),
    }


def _systemic_therapy():
    return {
        "name": "Systemic Therapy",
        "slug": "systemic-therapy",
        "key_figures": [
            {"name": "Mara Selvini-Palazzoli", "role": "Milan School founder", "years": "1916–1999"},
            {"name": "Gianfranco Cecchin", "role": "Milan School", "years": "1932–2004"},
            {"name": "Luigi Boscolo", "role": "Milan School", "years": "1932–2015"},
            {"name": "Gregory Bateson", "role": "Cybernetic/epistemological foundation", "years": "1904–1980"},
            {"name": "Tom Andersen", "role": "Reflecting team", "years": "1936–2007"},
        ],
        "origin": "Multiple centers, 1950s–1970s; Milan School 1970s",
        "historical_context": (
            "Systemic therapy emerged from multiple centers in the 1950s–1970s as therapists began "
            "working with families rather than individuals. The Milan School, founded by the 'Milan "
            "Four' (Selvini-Palazzoli, Boscolo, Cecchin, and Giuliana Prata), developed the most "
            "influential theoretical framework, grounded in Gregory Bateson's cybernetic epistemology. "
            "Selvini-Palazzoli abandoned individual therapy entirely around 1972 to focus on family "
            "systems. The approach evolved through phases: from strategic/pragmatic (influenced by "
            "the Mental Research Institute) to semantic/meaning-making, later incorporating social "
            "constructionist ideas. Reflecting teams (Andersen, 1987) made the therapeutic process "
            "more transparent and collaborative."
        ),
        "key_texts": [
            "Selvini-Palazzoli, M., Boscolo, L., Cecchin, G., & Prata, G. (1980). Hypothesizing — Circularity — Neutrality: Three Guidelines for the Conductor of the Session. *Family Process*, 19(1), 3–12.",
            "Cecchin, G. (1987). Hypothesizing, Circularity and Neutrality Revisited: An Invitation to Curiosity. *Family Process*, 26(4), 405–413.",
            "Bateson, G. (1972). *Steps to an Ecology of Mind*. Chandler.",
        ],
        "core_concepts": [
            {
                "name": "Circular causality over linear causality",
                "description": (
                    "Distress is maintained by relational patterns, not located in one person. "
                    "A client's 'symptom' may serve a function in a relationship system — "
                    "understanding that function is more clinically useful than labeling the "
                    "symptom pathological. The therapist traces reciprocal patterns rather than "
                    "asking 'who caused what?'"
                ),
            },
            {
                "name": "Context over intrapsychic explanation",
                "description": (
                    "Always ask: in what context does this pattern make sense? What conditions "
                    "produce and maintain it? The presenting problem is understood as embedded "
                    "in relational, familial, social, and cultural contexts — not as an isolated "
                    "intrapsychic phenomenon."
                ),
            },
            {
                "name": "Multi-partiality / curiosity",
                "description": (
                    "Evolved from the original Milan principle of 'neutrality.' The therapist "
                    "holds connection with all members of a system — genuinely curious about "
                    "each person's perspective as valid within their own frame, without requiring "
                    "consensus on a single truth. Rejects the position of detached expert in "
                    "favor of an engaged, curious, multi-partial stance."
                ),
            },
            {
                "name": "Hypothesizing",
                "description": (
                    "Forming systemic hunches about what maintains difficulties. A systemic "
                    "hypothesis connects the actions and beliefs of multiple people, avoids "
                    "linear/individualistic explanations, and is tested through circular "
                    "questioning. Hypotheses are treated as provisional, not as final truths."
                ),
            },
            {
                "name": "Circular questioning",
                "description": (
                    "Questions that explore relationships, differences, and connections between "
                    "family members' behaviors, beliefs, and feelings. These questions challenge "
                    "linear views, invite new perspectives, and reveal hidden patterns and rules. "
                    "Example: 'Who worries most when your mother is quiet?' rather than 'Why are "
                    "you depressed?'"
                ),
            },
            {
                "name": "Resource orientation",
                "description": (
                    "Every system has resources, competencies, and solutions that have not yet "
                    "been mobilized. Start there, not with deficits. The therapist looks for "
                    "exceptions, strengths, and existing coping strategies within the system."
                ),
            },
        ],
        "therapeutic_stance": (
            "The therapist is part of the observing system, not outside it. The stance is "
            "collaborative and curious rather than expert and prescriptive. The therapist "
            "attends to the therapeutic relationship as live data — what happens between "
            "therapist and client reflects broader relational patterns. The reflecting team "
            "or reflecting process makes the therapist's thinking transparent."
        ),
        "techniques": [
            "Circular questioning — exploring relational patterns and differences",
            "Reframing — offering alternative systemic meanings for behaviors",
            "Positive connotation — recognizing the adaptive function of seemingly problematic patterns",
            "Reflecting team/process — making therapeutic observations transparent",
            "Genograms — mapping multigenerational relational patterns",
            "Rituals and prescriptions — structured interventions that interrupt rigid patterns",
        ],
        "evidence_base": (
            "Systemic therapy has a robust evidence base, particularly for child and adolescent "
            "mental health, eating disorders, substance use disorders, and couple/family distress. "
            "In Germany, systemic therapy was recognized as a scientific psychotherapeutic method "
            "(Richtlinienverfahren) in 2020, joining psychoanalysis, psychodynamic therapy, and "
            "CBT for statutory health insurance reimbursement. Meta-analyses show effectiveness "
            "comparable to other evidence-based modalities."
        ),
        "critique": (
            "The emphasis on relational patterns can be experienced as minimizing individual "
            "responsibility (e.g., in cases of abuse). Earlier forms of the approach were "
            "criticized for being manipulative and opaque (the 'one-way screen' era). The "
            "concept of circular causality, applied uncritically, can obscure power differentials "
            "and structural violence. Contemporary systemic practice explicitly incorporates "
            "power analysis."
        ),
        "relationship_to_other_methods": (
            "The 'context over intrapsychic explanation' principle directly supports Liberation "
            "and Critical Psychology's social analysis. Multi-partiality provides a practical "
            "framework for holding multiple perspectives without requiring false neutrality about "
            "oppression. Circular questioning and externalizing (narrative) are complementary "
            "techniques for deconstructing problem-saturated stories. Resource orientation "
            "aligns with the strengths-based emphasis across the critical canon."
        ),
    }


# --- Broader Critical Canon ---

def _postcolonial_decolonial():
    return {
        "name": "Postcolonial and Decolonial Psychology",
        "slug": "postcolonial-decolonial-psychology",
        "key_figures": [
            {"name": "Frantz Fanon", "role": "Anticolonial psychiatrist and theorist", "years": "1925–1961"},
            {"name": "Aimé Césaire", "role": "Poet, theorist of négritude", "years": "1913–2008"},
            {"name": "W. E. B. Du Bois", "role": "Sociologist, double consciousness", "years": "1868–1963"},
        ],
        "origin": "Mid-20th century anticolonial movements; academic field 1980s–present",
        "historical_context": (
            "Postcolonial and decolonial psychology emerged from anticolonial movements of the "
            "mid-20th century and the postcolonial studies that followed. Fanon's psychiatric "
            "work in Algeria during the war of independence (1954–1962) provided foundational "
            "analyses of the psychological effects of colonialism and racism. The field critiques "
            "psychology's colonial history — the discipline's role in justifying racial hierarchy, "
            "cultural imposition of Western therapeutic models, and epistemic violence in defining "
            "'normal' and 'healthy.' Coloniality — the persistence of colonial ways of knowing, "
            "power, and being long after formal independence — is a central concept (Quijano, 2000; "
            "Maldonado-Torres, 2007)."
        ),
        "key_texts": [
            "Fanon, F. (1952). *Black Skin, White Masks*. Grove Press.",
            "Fanon, F. (1961). *The Wretched of the Earth*. Grove Press.",
            "APA (2024). *Decolonial Psychology* (L. Comas-Díaz & H. Y. Adames, Eds.).",
        ],
        "core_concepts": [
            {
                "name": "Sociogenic principle (Fanon)",
                "description": (
                    "Psychological disturbances in colonized peoples are not merely individual "
                    "pathologies but are socially generated through the structures of racism and "
                    "colonial oppression. The distinction between biogenic (biological), psychogenic "
                    "(individual psychological), and sociogenic (social-structural) causation is "
                    "foundational."
                ),
            },
            {
                "name": "Coloniality of psychology",
                "description": (
                    "Mainstream psychological science is not a neutral, universal body of knowledge "
                    "but a product of Eurocentric modernity that has served to uphold colonial "
                    "power structures. Western psychology's methods, values, and ways of knowing "
                    "have been imposed on non-Western peoples, often pathologizing their ways of "
                    "being — a process termed 'psycolonization.'"
                ),
            },
            {
                "name": "Epistemic violence",
                "description": (
                    "The harm caused when Eurocentric knowledge systems invalidate, erase, or "
                    "pathologize non-Western ways of knowing and being. This includes treating "
                    "WEIRD (Western, Educated, Industrialized, Rich, Democratic) individualist "
                    "lifestyles as universal developmental standards and judging other ways of "
                    "being as deviations."
                ),
            },
            {
                "name": "Double consciousness (Du Bois)",
                "description": (
                    "The experience of 'always looking at one's self through the eyes of others' — "
                    "the internalized split consciousness produced by living as a racialized person "
                    "in a society that devalues your identity. A foundational concept for "
                    "understanding the psychological effects of systemic racism."
                ),
            },
            {
                "name": "Decolonization of consciousness",
                "description": (
                    "The process of liberating the mind from Western ideological hold — understood "
                    "as both a psychological and political act. As Césaire insisted, 'it is equally "
                    "necessary to decolonize our minds, our inner life, at the same time that we "
                    "decolonize society.'"
                ),
            },
        ],
        "therapeutic_stance": (
            "The therapist recognizes that the therapeutic encounter itself is embedded in "
            "colonial history — the therapist-client relationship can reproduce colonial dynamics "
            "(expert/native, knower/known) or work to subvert them. Cultural 'competence' is "
            "reframed as structural competence and epistemic humility — not mastery of the Other's "
            "culture, but awareness of how coloniality shapes the therapeutic encounter and "
            "commitment to redistributing epistemic authority."
        ),
        "techniques": [
            "Examining how colonial histories shape presenting problems and therapeutic assumptions",
            "Centering the client's cultural knowledge and healing traditions",
            "Naming and deconstructing Eurocentric norms in diagnostic frameworks",
            "Supporting cultural reconnection and identity reclamation",
            "Applying the sociogenic principle in formulation: what social-structural conditions produce this distress?",
        ],
        "evidence_base": (
            "The evidence base is primarily theoretical, qualitative, and community-based. "
            "Quantitative outcome research is sparse and methodologically challenged by the "
            "framework's rejection of decontextualized measurement. Growing body of work on "
            "racial trauma, cultural adaptation of evidence-based treatments, and Indigenous "
            "healing practices provides converging evidence."
        ),
        "critique": (
            "Can be experienced as intellectually dense and inaccessible to clients. Risk of "
            "essentializing non-Western cultures as uniformly 'colonized' or 'oppressed.' "
            "Limited practical guidance for direct clinical work — the framework is stronger "
            "on critique than on technique. Tension between cultural sensitivity and universal "
            "human rights frameworks."
        ),
        "relationship_to_other_methods": (
            "Shares Liberation Psychology's critique of Western psychology's political neutrality "
            "and extends it to the global and historical dimension. The sociogenic principle "
            "is a core conceptual tool for all critical clinical work. Connects with Mad Studies' "
            "critique of psychiatric coercion in racialized communities. Informs culturally "
            "adapted applications of CBT, ACT, and other clinical modalities."
        ),
    }


def _feminist_queer():
    return {
        "name": "Feminist and Queer Psychology",
        "slug": "feminist-queer-psychology",
        "key_figures": [
            {"name": "Laura S. Brown", "role": "Feminist therapy theorist", "years": "b. 1952"},
            {"name": "Kimberlé Crenshaw", "role": "Intersectionality theorist", "years": "b. 1959"},
            {"name": "Judith Butler", "role": "Gender performativity theorist", "years": "b. 1956"},
        ],
        "origin": "Feminist therapy: late 1960s, USA; Queer theory: early 1990s",
        "historical_context": (
            "Feminist therapy emerged toward the end of the 1960s as a response to women's "
            "experiences of sexism in traditional therapy. It has no single founder but reflects "
            "the efforts of grassroots organizations and the Feminist Therapy Institute. Over "
            "decades, it evolved from a corrective against sexist therapeutic practices into a "
            "sophisticated, postmodern, technically integrative model. Queer psychology developed "
            "alongside queer theory in the early 1990s, challenging the heteronormative foundations "
            "of psychological knowledge and practice."
        ),
        "key_texts": [
            "Brown, L. S. (2018). *Feminist Therapy* (2nd ed.). APA Theories of Psychotherapy Series.",
            "Crenshaw, K. (1989). Demarginalizing the Intersection of Race and Sex. *University of Chicago Legal Forum*.",
            "Butler, J. (1990). *Gender Trouble*. Routledge.",
        ],
        "core_concepts": [
            {
                "name": "The personal is political",
                "description": (
                    "Individual psychological distress is connected to systemic gender oppression. "
                    "What appears as private suffering often has political roots — the therapeutic "
                    "task includes making these connections visible and supporting the client in "
                    "acting on them."
                ),
            },
            {
                "name": "Gender as social construction",
                "description": (
                    "Gender is not a fixed biological essence but a socially constructed and "
                    "performed category. The distress associated with gender often originates in "
                    "the rigid enforcement of gender norms, not in deviation from them. "
                    "Heteronormativity — the assumption that heterosexuality is the default and "
                    "normative orientation — is a clinical issue, not individual pathology."
                ),
            },
            {
                "name": "Intersectionality (Crenshaw)",
                "description": (
                    "Systems of oppression (racism, sexism, classism, ableism, heteronormativity, "
                    "cisnormativity) do not operate independently but intersect and compound. "
                    "A Black woman's experience of sexism cannot be understood separately from "
                    "racism. Clinical formulation must account for the full matrix of oppression "
                    "shaping a client's experience."
                ),
            },
            {
                "name": "Wisdom of the marginalized",
                "description": (
                    "A radical epistemological stance: silenced voices of oppressed people are "
                    "potentially the sources of the greatest wisdom. This shifts the value of "
                    "knowledge claims from culturally appointed experts to the expertise of the "
                    "oppressed. In practice, the margins become a new center."
                ),
            },
            {
                "name": "Subversion as therapeutic strategy",
                "description": (
                    "Therapist and client work together to undermine patriarchal and heteronormative "
                    "assumptions that prevent growth. Every component of therapy — including the "
                    "therapeutic frame itself — is treated as a potential site for challenging "
                    "oppressive norms."
                ),
            },
        ],
        "therapeutic_stance": (
            "Not neutral about gender oppression or heteronormativity. The therapist explicitly "
            "attends to power, inequality, and the societal structures that shape distress. "
            "Feminist therapy is for all genders — it analyzes how power and powerlessness "
            "relate to gender generally, not only to cis-women's experiences. The therapist "
            "practices reflexivity about their own social location and its impact on the "
            "therapeutic relationship."
        ),
        "techniques": [
            "Gender and power analysis of presenting problems",
            "Consciousness raising about the social roots of distress",
            "Deconstructing internalized sexism, heteronormativity, and cisnormativity",
            "Validating diverse gender identities, expressions, and sexualities",
            "Supporting the client in naming and acting against gender-based oppression",
            "Using inclusive language and intake practices that don't assume cisgender/heterosexual defaults",
        ],
        "evidence_base": (
            "Feminist therapy has a moderate outcome literature, with studies showing effectiveness "
            "for depression, eating disorders, trauma, and body image. Intersectionality is "
            "widely recognized as essential to culturally competent practice. Gender-affirming care "
            "for trans populations is supported by all major medical and psychological organizations "
            "(APA, AMA, AAP, WPATH). Sexual orientation change efforts are contraindicated — "
            "associated with increased depression and other harms."
        ),
        "critique": (
            "Can be experienced as politically prescriptive by clients who don't share feminist "
            "analysis. The strong emphasis on gender may feel exclusionary to clients whose "
            "primary concerns are in other domains. Risk of the therapist imposing their own "
            "political framework rather than exploring the client's meaning-making."
        ),
        "relationship_to_other_methods": (
            "Intersectionality is essential to Liberation and Critical Psychology's structural "
            "analysis. Gender and power analysis extend Narrative Therapy's deconstruction of "
            "dominant discourses. Feminist and queer frameworks directly inform the "
            "psychotherapist agent's specializations in gender-affirming care, sex therapy, "
            "and relationship diversity."
        ),
    }


def _trauma_informed_care():
    return {
        "name": "Trauma-Informed Care",
        "slug": "trauma-informed-care",
        "key_figures": [
            {"name": "Judith Herman", "role": "Foundational theorist of complex trauma", "years": "b. 1942"},
            {"name": "Bessel van der Kolk", "role": "Trauma researcher and clinician", "years": "b. 1943"},
            {"name": "Janina Fisher", "role": "Trauma and dissociation specialist", "years": "contemporary"},
        ],
        "origin": "USA, 1990s; rooted in feminist and veteran advocacy movements",
        "historical_context": (
            "The modern understanding of psychological trauma emerged from overlapping social "
            "movements: feminist advocacy against domestic and sexual violence, veterans' "
            "organizing around combat trauma, and Holocaust survivor testimony. Judith Herman's "
            "*Trauma and Recovery* (1992) synthesized these streams into a unified framework, "
            "proposing complex PTSD as a diagnosis for prolonged, repeated trauma (particularly "
            "in circumstances of captivity or entrapment). The trauma-informed care movement "
            "extended Herman's clinical framework into a systems-level approach for all human "
            "services."
        ),
        "key_texts": [
            "Herman, J. (1992). *Trauma and Recovery: The Aftermath of Violence — From Domestic Abuse to Political Terror*. Basic Books.",
            "van der Kolk, B. (2014). *The Body Keeps the Score*. Viking.",
            "Fisher, J. (2017). *Healing the Fragmented Selves of Trauma Survivors*. Routledge.",
        ],
        "core_concepts": [
            {
                "name": "Safety first",
                "description": (
                    "The first and non-negotiable stage of recovery. Establishing physical safety "
                    "(secure housing, protection from ongoing violence, medical stabilization) "
                    "and internal safety (grounding, affect regulation, coping skills). Herman "
                    "explicitly warns against exploring traumatic material before safety is "
                    "established — premature exploration risks retraumatization."
                ),
            },
            {
                "name": "Trauma as disempowerment and disconnection",
                "description": (
                    "The core experiences of psychological trauma are disempowerment and "
                    "disconnection from others. Recovery therefore must be built on empowerment "
                    "of the survivor and the creation of new connections. Trauma shatters basic "
                    "trust in self, others, and systems."
                ),
            },
            {
                "name": "Symptoms as adaptations",
                "description": (
                    "Psychological symptoms are understood as adaptations to overwhelming "
                    "experience, not as disorders. Hypervigilance was survival strategy; "
                    "dissociation was escape when physical escape was impossible; emotional "
                    "numbing was protection against unbearable pain. This reframe is itself "
                    "therapeutic."
                ),
            },
            {
                "name": "The healing relationship",
                "description": (
                    "'Recovery can take place only within the context of relationships; it cannot "
                    "occur in isolation.' The therapeutic relationship provides safety, bears "
                    "witness without judgment, and restores the survivor's capacity for trust "
                    "and connection. The therapist must be trustworthy — consistent, boundaried, "
                    "transparent, and respectful of the survivor's agency."
                ),
            },
            {
                "name": "Three-stage recovery model",
                "description": (
                    "Stage 1: Safety and stabilization. Stage 2: Remembrance and mourning "
                    "(processing the trauma narrative). Stage 3: Reconnection (integrating the "
                    "experience, rebuilding relationships, finding meaning). These stages are "
                    "not strictly linear — survivors may cycle through them."
                ),
            },
            {
                "name": "Systemic principles of trauma-informed care",
                "description": (
                    "Safety, trustworthiness and transparency, peer support, collaboration and "
                    "mutuality, empowerment and choice, cultural/historical/gender issues. These "
                    "principles apply not just to direct clinical work but to organizational "
                    "culture, physical environment, and service design."
                ),
            },
        ],
        "therapeutic_stance": (
            "The therapist's primary commitment is to the survivor's safety and empowerment. "
            "The therapeutic relationship models healthy power-sharing — the therapist is "
            "transparent, consistent, and boundaried. The therapist bears witness without "
            "imposing interpretation, respects the survivor's pacing, and actively works to "
            "avoid retraumatization. The therapist recognizes that trauma survivors have been "
            "harmed in relationships and that the therapeutic relationship is itself a site of "
            "potential healing or further harm."
        ),
        "techniques": [
            "Safety planning and stabilization before trauma processing",
            "Grounding and affect regulation skills (sensory, somatic, cognitive)",
            "Psychoeducation normalizing trauma responses as adaptations",
            "Graduated exposure / trauma narrative work (only after stabilization)",
            "Somatic approaches (recognizing trauma is held in the body)",
            "Parts work for structural dissociation (Fisher's TIST model)",
            "Peer support and group recovery models",
        ],
        "evidence_base": (
            "Robust evidence base. Trauma-focused CBT, EMDR, and prolonged exposure have strong "
            "RCT support for single-event trauma. The evidence for complex trauma is developing: "
            "phase-based approaches (stabilization before processing) are the clinical consensus "
            "though challenged by some recent trials. Somatic and body-based approaches have "
            "growing empirical support. The core principles of trauma-informed care are widely "
            "endorsed by health systems and regulatory bodies."
        ),
        "critique": (
            "Risk of trauma becoming a totalizing lens — not all distress is trauma-rooted. "
            "The trauma-informed label can be applied superficially without substantive practice "
            "change. Some critics argue the PTSD framework medicalizes normal responses to "
            "overwhelming experience. Phase-based treatment can delay evidence-supported "
            "trauma-focused work if stabilization becomes interminable."
        ),
        "relationship_to_other_methods": (
            "'Symptoms as adaptations, not disorders' aligns with Liberation Psychology's "
            "de-pathologizing stance and Mad Studies' critique of biomedical framing. The safety "
            "principle is foundational for all work with marginalized populations who experience "
            "systemic threat. Trauma-informed principles can be integrated with any clinical "
            "modality. The psychotherapist agent's neurodevelopmental specialization recognizes "
            "that growing up neurodivergent in a neuronormative world is often traumatic — "
            "trauma-informed principles are essential to neurodivergent-affirming practice."
        ),
    }


def _disability_justice_neurodiversity():
    return {
        "name": "Disability Justice and Neurodiversity Paradigm",
        "slug": "disability-justice-neurodiversity",
        "key_figures": [
            {"name": "Judy Singer", "role": "Sociologist, early neurodiversity theorist", "years": "b. 1951"},
            {"name": "Nick Walker", "role": "Neurodiversity paradigm scholar", "years": "contemporary"},
            {"name": "Sins Invalid", "role": "Disability justice performance collective", "years": "founded 2006"},
        ],
        "origin": "Disability rights: 1970s UK (social model); Neurodiversity: 1990s autistic activist communities; Disability Justice: 2000s USA",
        "historical_context": (
            "The social model of disability emerged from the UK disabled people's movement in the "
            "1970s (UPIAS, 1976), distinguishing impairment (biological difference) from disability "
            "(social oppression imposed on top of impairment). The neurodiversity paradigm was "
            "collectively developed by autistic activists in online communities in the mid-1990s, "
            "applying the social model to neurological difference. Disability Justice, articulated "
            "by Sins Invalid and other groups led by disabled people of color and queer/trans "
            "disabled people, extends the social model with an intersectional, cross-movement, "
            "leadership-of-the-most-impacted framework."
        ),
        "key_texts": [
            "Walker, N. (2021). *Neuroqueer Heresies*. Autonomous Press.",
            "Sins Invalid. (2019). *Skin, Tooth, and Bone: The Basis of Movement is Our People* (2nd ed.).",
            "Oliver, M. (1990). *The Politics of Disablement*. Macmillan.",
        ],
        "core_concepts": [
            {
                "name": "Social model: disablement as social process",
                "description": (
                    "Disability is not located in the individual body/mind but is produced by "
                    "social, environmental, and attitudinal barriers. The clinical goal is not "
                    "to 'fix' the disabled person but to identify and dismantle barriers, adapt "
                    "environments, and support the person's full participation as their authentic "
                    "self."
                ),
            },
            {
                "name": "Neurodiversity: natural variation, not pathology",
                "description": (
                    "ADHD, autism, dyslexia, dyspraxia, and other neurodevelopmental variations "
                    "are natural forms of human diversity — analogous to biodiversity — not "
                    "pathologies to be eliminated. The clinical goal is not to make someone "
                    "'less autistic' or 'less ADHD' — it is to reduce distress, build on "
                    "strengths, adapt environments, and support the person in living a "
                    "meaningful life as their full neurodivergent self."
                ),
            },
            {
                "name": "Critique of neuronormative standards",
                "description": (
                    "Many standards (40-hour work week, open-plan offices, fluorescent lighting, "
                    "indirect communication norms, eye contact expectations) are not neutral "
                    "benchmarks but specific demands designed for a narrow range of neurotypes. "
                    "The problem is often not the person's neurology but an environment designed "
                    "for neurotypical comfort."
                ),
            },
            {
                "name": "Accommodations are equity, not dependence",
                "description": (
                    "Noise-canceling headphones, fidget tools, written follow-ups, extended time, "
                    "stimming — these are tools for equitable access, not signs of weakness. The "
                    "goal is not to eliminate accommodations but to build a life where they are "
                    "naturally integrated without shame."
                ),
            },
            {
                "name": "No functioning labels",
                "description": (
                    "'High-functioning' erases support needs; 'low-functioning' erases agency. "
                    "Describe specific strengths and support needs instead. Recognize that "
                    "functioning varies contextually — the same person may function differently "
                    "in different environments and at different times."
                ),
            },
            {
                "name": "Critique of normalization-based approaches",
                "description": (
                    "ABA and other normalization-based behavioral interventions have caused harm "
                    "and are rejected by many autistic adults. The goal of intervention should be "
                    "to support the person's wellbeing and self-determination, not to make them "
                    "appear neurotypical or to reduce traits that make others uncomfortable."
                ),
            },
        ],
        "therapeutic_stance": (
            "The therapist actively unlearns neuronormative assumptions and challenges ableism "
            "in clinical thinking. The therapist's role is to support the client in understanding "
            "their neurotype, reducing distress, building on strengths, and navigating environments "
            "that were not designed for them — not to cure or normalize. Grief and identity work "
            "are central: late-diagnosed adults often cycle through relief, grief, and anger. "
            "Identity integration — what it means to be neurodivergent, not a broken neurotypical "
            "— is often the most important therapeutic work."
        ),
        "techniques": [
            "Identity-first or person-first language per client preference — ask, don't assume",
            "Sensory assessments and environmental adaptations as clinical intervention",
            "Reframing traits as differences not deficits (executive dysfunction not laziness, stimming not 'disruptive behavior')",
            "Support for unmasking in safe contexts (with awareness of safety risks)",
            "Burnout recognition and recovery planning (autistic burnout ≠ depression)",
            "Accommodation coaching: identifying and requesting what the client needs without shame",
            "Grief work for late-diagnosed adults processing 'who would I have been if I'd known sooner?'",
        ],
        "evidence_base": (
            "The neurodiversity paradigm is a conceptual framework, not an intervention to be "
            "tested. Supporting evidence comes from studies documenting harm from normalization-based "
            "approaches, benefits of neurodivergent-affirming environments, elevated trauma and "
            "mental health comorbidity in neurodivergent populations, and the effectiveness of "
            "accommodations. Adapted CBT, ACT, and DBT show effectiveness for neurodivergent "
            "populations when delivered with neurodiversity-affirming principles."
        ),
        "critique": (
            "Critics argue the paradigm minimizes the disabling aspects of neurodevelopmental "
            "conditions for those with high support needs. The tension between affirming "
            "neurodivergence and acknowledging disability is real and unresolved. Some families "
            "and clinicians feel the paradigm dismisses their experiences of significant "
            "functional impairment. Proponents emphasize that the paradigm does not deny "
            "disability — it locates the problem in the person-environment interaction, not "
            "solely in the individual."
        ),
        "relationship_to_other_methods": (
            "Extends the social model of disability into psychological practice. Directly "
            "parallels Mad Studies' critique of normalization and psychiatric coercion. "
            "Intersectional disability justice framework connects with Feminist and Postcolonial "
            "analyses. The psychotherapist agent's neurodevelopmental specialization is built "
            "on this foundation. The neurodiversity paradigm informs adaptation of CBT, ACT, "
            "and other modalities for neurodivergent clients."
        ),
    }


def _mad_studies():
    return {
        "name": "Mad Studies",
        "slug": "mad-studies",
        "key_figures": [
            {"name": "Brenda A. LeFrançois", "role": "Mad Studies scholar and editor", "years": "contemporary"},
            {"name": "Robert Menzies", "role": "Mad Studies scholar and editor", "years": "contemporary"},
            {"name": "Geoffrey Reaume", "role": "Mad historian and activist", "years": "contemporary"},
            {"name": "Richard A. Ingram", "role": "Coined 'Mad Studies' (2008)", "years": "contemporary"},
        ],
        "origin": "Canada (Ryerson/York Universities), 2000s; psychiatric survivor movement since 1960s–1970s",
        "historical_context": (
            "Mad Studies emerged from psychiatric survivor/consumer movements organized since the "
            "1960s–1970s in Canada, the US, the UK, Australia, and beyond. The movement's "
            "political evolution is reflected in its changing language: mental patient liberation "
            "→ consumer/survivor/ex-patient (c/s/x) → mad/Mad → psychiatric survivor. The term "
            "'Mad Studies' was coined by Richard Ingram in 2008 at Syracuse University. The "
            "field was pioneered at Ryerson and York Universities in Toronto. The foundational "
            "text, *Mad Matters* (2013), edited by LeFrançois, Menzies, and Reaume, is the first "
            "book officially declared as Mad Studies in Canada. Mad Studies is 'a project of "
            "inquiry, knowledge production, and political action devoted to the critique and "
            "transcendence of psy-centred ways of thinking, behaving, relating, and being.'"
        ),
        "key_texts": [
            "LeFrançois, B. A., Menzies, R., & Reaume, G. (Eds.). (2013). *Mad Matters: A Critical Reader in Canadian Mad Studies*. Canadian Scholars' Press.",
        ],
        "core_concepts": [
            {
                "name": "Centering the knowledge of psychiatric survivors",
                "description": (
                    "Moving from 'what's wrong with you?' to 'what happened to you?' and 'what "
                    "do you need?' Psychiatric survivors and mad-identified people are the experts "
                    "on their own experience. Their knowledge is not a data source to be interpreted "
                    "by professionals — it is the authoritative standpoint from which critique "
                    "and alternatives are generated."
                ),
            },
            {
                "name": "Critique of biomedical psychiatry",
                "description": (
                    "Mad Studies fundamentally rejects the biomedical model that reduces complex "
                    "human experiences to brain diseases and chemical imbalances. It critiques "
                    "involuntary confinement and enforced treatment, electroconvulsive therapy "
                    "without consent, the pharmaceutical industry's role in shaping diagnostic "
                    "expansion, and the system's function in social control."
                ),
            },
            {
                "name": "Sanism",
                "description": (
                    "The systemic discrimination and oppression of people labeled mentally ill — "
                    "analogous to racism, sexism, ableism, and heteronormativity. Sanism operates "
                    "at individual, institutional, and epistemological levels, including within "
                    "mental health professions themselves."
                ),
            },
            {
                "name": "Language reclamation",
                "description": (
                    "Following the example of queer, Black, and fat activism, Mad Studies reclaims "
                    "disparaged identities and restores pride and dignity to difference. 'Mad' is "
                    "used as a political identity, not a clinical descriptor. This is contested "
                    "within survivor communities — some find the term unreclaimable while others "
                    "find it empowering."
                ),
            },
            {
                "name": "Intersectionality with other oppressions",
                "description": (
                    "Mad Studies draws deliberate connections with Queer Studies, Critical Race "
                    "Studies, Disability Studies, and anti-colonial movements. Racialized "
                    "communities face disproportionate psychiatric coercion. Without attention "
                    "to race, class, and colonialism, Mad identity risks reproducing a white, "
                    "Western Mad subject."
                ),
            },
            {
                "name": "Peer support and mutual aid",
                "description": (
                    "Peer support is the foundation of the psychiatric survivor movement — "
                    "support by and for people with lived experience, outside (or alongside) "
                    "clinical hierarchies. There is ongoing debate about the institutionalization "
                    "and professionalization of peer support and whether it risks co-optation."
                ),
            },
        ],
        "therapeutic_stance": (
            "The therapist works from a position of solidarity with mad-identified people and "
            "psychiatric survivors. The therapeutic relationship must actively counter sanism: "
            "the therapist does not position themselves as the sane expert treating the mad "
            "patient, but as a collaborator who recognizes the client's experiential expertise. "
            "The therapist is transparent about the power they hold and works to redistribute "
            "it. Coercion in any form is rejected. The therapist supports the client in making "
            "meaning of their experiences in their own terms — not imposing a diagnostic framework."
        ),
        "techniques": [
            "Validating the client's own framework for understanding their experiences",
            "Supporting self-determination in treatment decisions (including declining treatment)",
            "Connecting clients with peer support and survivor communities",
            "Deconstructing diagnostic labels and their social functions",
            "Exploring alternatives to biomedical framing — trauma, oppression, spiritual emergency, meaningful human variation",
            "Advocating against coercive practices in mental health systems (as appropriate to role)",
        ],
        "evidence_base": (
            "Mad Studies prioritizes experiential knowledge and critical analysis over clinical "
            "trials. Supporting empirical evidence comes from research on iatrogenic harm, "
            "effectiveness of peer support, outcomes of coercion reduction initiatives, and "
            "qualitative research on survivor-defined recovery. The framework is fundamentally "
            "critical of the RCT paradigm as embedded in the biomedical model it critiques."
        ),
        "critique": (
            "Can be experienced as anti-psychiatry and alienating to people who find diagnosis "
            "and medication helpful. The strong rejection of biomedical framing may not resonate "
            "with clients who experience their condition as biologically based. Tension between "
            "the academic/theoretical nature of Mad Studies and the immediate needs of people in "
            "acute distress. Risk of romanticizing madness and underestimating genuine suffering."
        ),
        "relationship_to_other_methods": (
            "Shares with Liberation Psychology the centering of marginalized knowledge and "
            "critique of institutional power. Sanism analysis parallels Disability Justice's "
            "critique of neuronormativity. Extends Trauma-Informed Care's 'what happened to you?' "
            "to a systemic critique of the institutions that respond (and often compound) the "
            "distress. Informs the psychotherapist agent's de-pathologizing stance and critical "
            "use of diagnostic frameworks."
        ),
    }


# --- Clinical Modalities ---

def _cognitive_behavioral_therapy():
    return {
        "name": "Cognitive Behavioral Therapy (CBT)",
        "slug": "cognitive-behavioral-therapy",
        "key_figures": [
            {"name": "Aaron T. Beck", "role": "Founder of cognitive therapy", "years": "1921–2021"},
            {"name": "Albert Ellis", "role": "Founder of REBT", "years": "1913–2007"},
        ],
        "origin": "USA, 1960s (cognitive therapy); behavioral roots in 1950s",
        "historical_context": (
            "Aaron Beck, originally a psychoanalyst, developed cognitive therapy in the 1960s "
            "after finding that depressed patients experienced spontaneous negative thoughts "
            "(automatic thoughts) that maintained their depression. His empirical approach — "
            "testing cognitive models against clinical data — distinguished CBT from its "
            "psychoanalytic predecessors. Beck's cognitive therapy merged with behavioral "
            "techniques developed in the 1950s–60s (Wolpe, Skinner, Bandura) to become CBT. "
            "CBT is now the most extensively researched psychotherapy modality worldwide, "
            "with over 2,000 outcome studies."
        ),
        "key_texts": [
            "Beck, A. T. (1979). *Cognitive Therapy of Depression*. Guilford Press.",
            "Beck, J. S. (2020). *Cognitive Behavior Therapy: Basics and Beyond* (3rd ed.). Guilford Press.",
        ],
        "core_concepts": [
            {
                "name": "Cognitive model",
                "description": (
                    "Psychological distress is maintained by patterns of dysfunctional thinking. "
                    "Automatic thoughts (rapid, evaluative cognitions) arise from underlying "
                    "intermediate beliefs (rules, attitudes, assumptions) and core beliefs "
                    "(fundamental schemas about self, others, and world). Therapy works by "
                    "identifying, testing, and modifying these cognitive patterns."
                ),
            },
            {
                "name": "Collaborative empiricism",
                "description": (
                    "Therapist and client work together as co-investigators, treating thoughts "
                    "as hypotheses to be tested rather than facts to be accepted. The therapeutic "
                    "relationship is collaborative, structured, and focused on here-and-now "
                    "problem-solving."
                ),
            },
            {
                "name": "Behavioral activation",
                "description": (
                    "A core behavioral component: systematically increasing engagement in "
                    "positively reinforcing activities to counter the downward spiral of "
                    "depression (reduced activity → reduced reinforcement → worsened mood → "
                    "further reduced activity). BA is an effective standalone treatment for "
                    "depression."
                ),
            },
            {
                "name": "Exposure and response prevention",
                "description": (
                    "Graduated, systematic exposure to feared stimuli without engaging in "
                    "safety behaviors or compulsions. The gold-standard treatment for anxiety "
                    "disorders and OCD. Based on habituation and inhibitory learning principles."
                ),
            },
            {
                "name": "Cognitive restructuring",
                "description": (
                    "Identifying automatic thoughts, evaluating their accuracy and usefulness, "
                    "and generating more balanced, evidence-based alternatives. Distinct from "
                    "'positive thinking' — the goal is realistic appraisal, not forced optimism."
                ),
            },
            {
                "name": "Skills training and homework",
                "description": (
                    "CBT is structured and skill-building. Clients learn concrete techniques "
                    "(thought records, behavioral experiments, problem-solving, relaxation) "
                    "and practice them between sessions. The goal is for the client to become "
                    "their own therapist."
                ),
            },
        ],
        "therapeutic_stance": (
            "Active, directive, collaborative, and present-focused. The therapist structures "
            "sessions (agenda-setting, mood check, bridge from previous session, work on "
            "current agenda items, homework assignment, feedback). The therapeutic relationship "
            "is warm and genuine but not the primary mechanism of change — it is the necessary "
            "foundation for collaborative empirical work."
        ),
        "techniques": [
            "Socratic questioning — guided discovery rather than direct disputation",
            "Thought records — structured tool for catching, checking, and changing automatic thoughts",
            "Behavioral experiments — in-session or between-session tests of cognitive predictions",
            "Activity scheduling and behavioral activation",
            "Exposure hierarchies and systematic desensitization",
            "Problem-solving training",
            "Relapse prevention planning",
        ],
        "evidence_base": (
            "CBT has the most extensive evidence base of any psychotherapy. Strong empirical "
            "support for: depression, all anxiety disorders, OCD, PTSD, eating disorders, "
            "insomnia, chronic pain, substance use disorders, and psychosis (as adjunct). "
            "Effect sizes are moderate to large compared to no treatment, small to moderate "
            "compared to other bona fide treatments. The specificity debate continues — CBT "
            "consistently outperforms weak controls but the advantage over other active "
            "treatments narrows over time, raising questions about common vs. specific factors."
        ),
        "critique": (
            "The cognitive model can oversimplify: not all distress is maintained by distorted "
            "thinking, and the focus on individual cognition can obscure social-structural "
            "causes of distress. The structured, directive style may feel invalidating to "
            "clients who need to be heard before problem-solving. Evidence base overrepresents "
            "white, educated, high-income populations. CBT can be applied in ways that adjust "
            "the person to oppressive conditions rather than supporting them in changing those "
            "conditions — the 'adjustment to oppression' critique. The emphasis on 'distorted' "
            "thinking can be experienced as pathologizing by neurodivergent people and trauma "
            "survivors whose thinking patterns are rational adaptations to adverse environments."
        ),
        "relationship_to_other_methods": (
            "CBT techniques are used by the psychotherapist agent within a Liberation/Critical "
            "Psychology framework — behavioral activation, cognitive restructuring, and exposure "
            "are clinically useful when applied with awareness of social context and power. "
            "CBT adapted for neurodivergent clients (shorter sessions, written materials, "
            "concrete examples, sensory accommodations) integrates with neurodiversity-affirming "
            "practice. CBT's empirical rigor provides a valuable counterweight to the critical "
            "canon's theoretical emphasis — but the critical lens is essential to prevent CBT "
            "from becoming decontextualized technique application."
        ),
    }


def _acceptance_commitment_therapy():
    return {
        "name": "Acceptance and Commitment Therapy (ACT)",
        "slug": "acceptance-commitment-therapy",
        "key_figures": [
            {"name": "Steven C. Hayes", "role": "Founder", "years": "b. 1948"},
        ],
        "origin": "USA, 1980s–1990s; University of Nevada, Reno",
        "historical_context": (
            "ACT emerged from Steven Hayes's personal experience with panic disorder and his "
            "dissatisfaction with the cognitive restructuring approach. Drawing on Relational "
            "Frame Theory (RFT) — a behavioral account of human language and cognition — ACT "
            "proposed that the problem is not the content of thoughts but the context in which "
            "they are held. The goal is not to change thought content (as in CBT) but to change "
            "the person's relationship to their thoughts. ACT is part of the 'third wave' of "
            "behavioral therapies, alongside DBT, Functional Analytic Psychotherapy, and "
            "Mindfulness-Based Cognitive Therapy."
        ),
        "key_texts": [
            "Hayes, S. C., Strosahl, K. D., & Wilson, K. G. (2012). *Acceptance and Commitment Therapy: The Process and Practice of Mindful Change* (2nd ed.). Guilford Press.",
            "Harris, R. (2019). *ACT Made Simple* (2nd ed.). New Harbinger.",
        ],
        "core_concepts": [
            {
                "name": "Psychological flexibility",
                "description": (
                    "The central therapeutic target: the ability to contact the present moment "
                    "fully and consciously, and to persist or change behavior in the service of "
                    "chosen values. Psychological inflexibility — experiential avoidance, "
                    "cognitive fusion, dominance of the conceptualized past/future, attachment "
                    "to the conceptualized self, lack of values clarity, and inaction — is the "
                    "core pathological process across diagnoses."
                ),
            },
            {
                "name": "Cognitive fusion vs. defusion",
                "description": (
                    "Fusion: being entangled with thoughts, treating them as literal truths "
                    "rather than mental events. Defusion: creating distance from thoughts — "
                    "seeing them as passing mental events, not commands to be obeyed or threats "
                    "to be eliminated. A core distinction from CBT: ACT does not dispute or "
                    "restructure thought content but changes the context in which thoughts are held."
                ),
            },
            {
                "name": "Experiential avoidance",
                "description": (
                    "The attempt to avoid or escape unwanted private experiences (thoughts, "
                    "feelings, sensations, memories) — even when doing so causes harm and "
                    "prevents valued living. ACT teaches willingness to experience discomfort "
                    "in the service of what matters."
                ),
            },
            {
                "name": "Values and committed action",
                "description": (
                    "Values are chosen life directions, not goals to be achieved. Committed "
                    "action means taking concrete steps in valued directions, even in the "
                    "presence of difficult internal experience. This is the 'commitment' part "
                    "of ACT — the behavioral activation toward what matters."
                ),
            },
            {
                "name": "Self-as-context",
                "description": (
                    "A transcendent sense of self — the observing 'I' that notices thoughts, "
                    "feelings, and sensations without being defined by them. Distinct from "
                    "the conceptualized self (the story of who we are). Mindfulness and "
                    "perspective-taking exercises develop this capacity."
                ),
            },
            {
                "name": "The hexaflex model",
                "description": (
                    "Six interrelated processes: acceptance (opening to experience), defusion "
                    "(stepping back from thoughts), self-as-context (flexible perspective-taking), "
                    "present-moment awareness, values (chosen life directions), and committed "
                    "action (values-consistent behavior). These are not separate techniques but "
                    "facets of psychological flexibility."
                ),
            },
        ],
        "therapeutic_stance": (
            "The ACT therapist is compassionate, present-centered, and radically accepting of "
            "the client's experience. The therapeutic relationship models psychological "
            "flexibility — the therapist is willing to sit with difficult material without "
            "rushing to fix it. The therapist uses metaphor, experiential exercises, and "
            "mindfulness practices rather than logical disputation. The stance is egalitarian: "
            "'I'm not here to fix you — I'm here to help you build a richer, more meaningful "
            "life alongside the pain that comes with being human.'"
        ),
        "techniques": [
            "Metaphor (e.g., passengers on the bus, tug-of-war with a monster, quicksand)",
            "Mindfulness exercises (present-moment awareness, noticing without judgment)",
            "Defusion techniques (naming the story, thanking the mind, silly voices)",
            "Values clarification (e.g., the 80th birthday exercise, values card sort)",
            "Committed action planning (SMART goals in service of values)",
            "Creative hopelessness — exploring the unworkability of control-based strategies",
            "Acceptance exercises (physicalizing the emotion, expansion, willingness)",
        ],
        "evidence_base": (
            "ACT has a growing evidence base with over 300 RCTs across a wide range of "
            "conditions: depression, anxiety, chronic pain, substance use, eating disorders, "
            "psychosis, workplace stress, and more. Effect sizes are generally comparable to "
            "CBT. ACT is listed as an empirically supported treatment by APA Division 12 for "
            "chronic pain and has strong research support for depression and anxiety. The "
            "transdiagnostic approach is well-suited to the high comorbidity seen in clinical "
            "practice."
        ),
        "critique": (
            "Some argue ACT's differences from CBT are overstated — both involve changing "
            "relationship to thoughts, and defusion can function similarly to cognitive "
            "restructuring. The evidence base, while growing, is younger and smaller than "
            "CBT's, with concerns about methodological quality in some trials. The language "
            "can be abstract and jargon-heavy ('hexaflex,' 'self-as-context'). Some clients "
            "experience the emphasis on acceptance as invalidating — as though they should "
            "simply accept oppressive conditions rather than fight to change them."
        ),
        "relationship_to_other_methods": (
            "ACT's emphasis on values and committed action aligns well with Liberation "
            "Psychology's focus on agency and collective action — values work can surface "
            "what the client genuinely cares about, including social justice and community "
            "connection. Defusion techniques complement Narrative Therapy's externalizing: "
            "both create distance between the person and problem-saturated cognitive content. "
            "ACT is particularly well-suited for neurodivergent clients when delivered with "
            "neurodiversity-affirming adaptations — the concrete metaphors, experiential "
            "focus, and values-centered approach resonate with autistic and ADHD cognitive "
            "styles. The willingness/acceptance stance supports work with chronic conditions "
            "where cure is not the goal."
        ),
    }


# ---------------------------------------------------------------------------
# source.md generation
# ---------------------------------------------------------------------------

def _build_source_md_frontmatter():
    return """---
title: Clinical Therapy Methodology Guidelines
authors: >
  Compiled from primary texts, systematic reviews, and authoritative clinical
  guidelines covering 11 therapy methodologies used by the psychotherapist agent.
source: >
  Multiple authoritative sources (see individual methodology entries for
  specific references and primary texts).
source_url: "n/a — compiled clinical reference"
access_date: 2026-07-17
language: en
extraction_notes: >
  Comprehensive reference covering 11 therapy methodologies across four
  categories: Foundational Frameworks (Liberation Psychology, Critical
  Psychology), Integrative Modalities (Narrative Therapy, Systemic Therapy),
  Broader Critical Canon (Postcolonial/Decolonial Psychology, Feminist/Queer
  Psychology, Trauma-Informed Care, Disability Justice/Neurodiversity
  Paradigm, Mad Studies), and Clinical Modalities (CBT, ACT).  Each entry
  includes: key figures, historical context, core concepts, therapeutic
  stance, techniques, evidence base, critique, and relationship to other
  methodologies.  Content is curated from primary source texts, systematic
  reviews, and recognized clinical practice guidelines.
  Bootstrap tool: uv run med-db-setup-therapy-methods
  Verify: uv run med-db-setup-therapy-methods --verify-only
  Total methodologies: 11 across 4 categories.
---
"""


def _build_source_md_body(data):
    lines = []
    lines.append("## Clinical Therapy Methodology Guidelines")
    lines.append("")
    lines.append(
        "Comprehensive reference for the therapy methodologies used by the "
        "psychotherapist agent. These guidelines provide the theoretical "
        "foundation for clinical formulation, intervention planning, and "
        "technique selection within a Liberation/Critical Psychology framework."
    )
    lines.append("")
    lines.append("## Quick Reference")
    lines.append("")
    lines.append("```bash")
    lines.append("# Verify guidelines are present")
    lines.append("uv run med-db-setup-therapy-methods --verify-only")
    lines.append("")
    lines.append("# Regenerate if needed")
    lines.append("uv run med-db-setup-therapy-methods --force")
    lines.append("")
    lines.append("# Programmatic access (JSON)")
    lines.append(
        "uv run python -c \"import json; d=json.load(open("
        "'med-db/guidelines/therapy-methodologies/methodologies.json')); "
        "print([m['name'] for c in d['categories'] for m in c['methodologies']])\""
    )
    lines.append("```")
    lines.append("")

    for cat in data["categories"]:
        lines.append(f"## {cat['name']}")
        lines.append("")
        lines.append(cat["description"])
        lines.append("")

        for meth in cat["methodologies"]:
            lines.append(f"### {meth['name']}")
            lines.append("")

            # Key figures
            figures = ", ".join(
                f"{f['name']} ({f['role']}, {f['years']})"
                for f in meth["key_figures"]
            )
            lines.append(f"**Key Figures:** {figures}")
            lines.append("")
            lines.append(f"**Origin:** {meth['origin']}")
            lines.append("")

            # Historical context
            lines.append(f"**Historical Context:** {meth['historical_context']}")
            lines.append("")

            # Key texts
            lines.append("**Key Texts:**")
            for text in meth["key_texts"]:
                lines.append(f"- {text}")
            lines.append("")

            # Core concepts
            lines.append("**Core Concepts:**")
            for i, concept in enumerate(meth["core_concepts"], 1):
                lines.append(f"{i}. **{concept['name']}** — {concept['description']}")
            lines.append("")

            # Therapeutic stance
            lines.append(f"**Therapeutic Stance:** {meth['therapeutic_stance']}")
            lines.append("")

            # Techniques
            lines.append("**Key Techniques:**")
            for t in meth["techniques"]:
                lines.append(f"- {t}")
            lines.append("")

            # Evidence
            lines.append(f"**Evidence Base:** {meth['evidence_base']}")
            lines.append("")

            # Critique
            lines.append(f"**Critique and Limitations:** {meth['critique']}")
            lines.append("")

            # Relationships
            lines.append(f"**Relationship to Other Methodologies:** {meth['relationship_to_other_methods']}")
            lines.append("")

    lines.append("## Using These Guidelines")
    lines.append("")
    lines.append(
        "These methodology descriptions are reference documents — they do not "
        "prescribe specific interventions. In clinical practice, the psychotherapist "
        "agent integrates techniques across modalities guided by the formulation and "
        "the client's preferences. The foundational Liberation/Critical Psychology "
        "lens shapes how all modalities are applied: with attention to social context, "
        "power, and the de-pathologizing of distress."
    )
    lines.append("")

    return "\n".join(lines)


def _build_source_md(data):
    return _build_source_md_frontmatter() + "\n" + _build_source_md_body(data)


# ---------------------------------------------------------------------------
# index.json update
# ---------------------------------------------------------------------------

def _build_index_entry():
    return {
        "path": "guidelines/therapy-methodologies",
        "title": "Clinical Therapy Methodology Guidelines",
        "source": "Multiple authoritative sources (primary texts, systematic reviews, clinical guidelines)",
        "source_url": "n/a — compiled clinical reference",
        "access_date": "2026-07-17",
        "language": ["en"],
        "format": "Markdown reference + JSON data",
        "description": (
            "Comprehensive reference covering 11 therapy methodologies across 4 categories: "
            "Foundational Frameworks (Liberation Psychology, Critical Psychology), "
            "Integrative Modalities (Narrative Therapy, Systemic Therapy), "
            "Broader Critical Canon (Postcolonial/Decolonial Psychology, Feminist/Queer "
            "Psychology, Trauma-Informed Care, Disability Justice/Neurodiversity Paradigm, "
            "Mad Studies), and Clinical Modalities (CBT, ACT). Each entry includes key "
            "figures, historical context, core concepts, therapeutic stance, techniques, "
            "evidence base, critique, and cross-methodology relationships."
        ),
        "lookup_tool": "uv run med-db-setup-therapy-methods --verify-only",
    }


def _update_index_json(entry):
    """Add or update the therapy-methodologies entry in index.json."""
    index_path = MED_DB / "index.json"

    if index_path.exists():
        try:
            with open(index_path, encoding="utf-8") as fh:
                index_data = json.load(fh)
        except (json.JSONDecodeError, OSError):
            index_data = {}
    else:
        index_data = {}

    guidelines = index_data.get("guidelines", [])

    # Replace existing entry or append
    replaced = False
    for i, existing in enumerate(guidelines):
        if existing.get("path") == entry["path"]:
            guidelines[i] = entry
            replaced = True
            break
    if not replaced:
        guidelines.append(entry)

    index_data["guidelines"] = guidelines

    # Atomic write: write to temp file then rename to avoid corruption
    tmp_path = index_path.with_suffix(index_path.suffix + ".tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as fh:
            json.dump(index_data, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        tmp_path.replace(index_path)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink()
        raise


# ---------------------------------------------------------------------------
# setup / verify / main
# ---------------------------------------------------------------------------

def setup(force=False):
    """Create source.md, methodologies.json, and update index.json.

    Returns True if created, False if already present (and not forced).
    """
    if SOURCE_MD.exists() and METHODOLOGIES_JSON.exists() and not force:
        return False

    GUIDELINE_DIR.mkdir(parents=True, exist_ok=True)

    data = _build_methodologies_categorized()

    # Write source.md (atomic)
    source_content = _build_source_md(data)
    utils.atomic_write(SOURCE_MD, source_content)

    # Write methodologies.json (atomic)
    tmp_json = METHODOLOGIES_JSON.with_suffix(METHODOLOGIES_JSON.suffix + ".tmp")
    try:
        with open(tmp_json, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        tmp_json.replace(METHODOLOGIES_JSON)
    except Exception:
        if tmp_json.exists():
            tmp_json.unlink()
        raise

    # Update index.json
    _update_index_json(_build_index_entry())

    total = sum(
        len(cat["methodologies"]) for cat in data["categories"]
    )
    print(
        f"Created therapy methodology guidelines: "
        f"{len(data['categories'])} categories, {total} methodologies"
    )
    return True


def verify():
    """Quick smoke test."""
    if not SOURCE_MD.exists():
        return False, "source.md not found"
    if not METHODOLOGIES_JSON.exists():
        return False, "methodologies.json not found"

    with open(SOURCE_MD, encoding="utf-8") as fh:
        source_content = fh.read()
    if not source_content.strip():
        return False, "source.md is empty"

    with open(METHODOLOGIES_JSON, encoding="utf-8") as fh:
        try:
            json_data = json.load(fh)
        except json.JSONDecodeError as e:
            return False, f"methodologies.json is invalid: {e}"

    cats = len(json_data.get("categories", []))
    total = sum(
        len(cat.get("methodologies", []))
        for cat in json_data.get("categories", [])
    )
    return True, f"{cats} categories, {total} methodologies"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create/validate the therapy methodology reference in med-db/"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Regenerate all files even if they already exist.",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        default=False,
        help="Only verify; do not create or overwrite.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.verify_only:
        ok, msg = verify()
        if ok:
            print(f"Therapy methodology guidelines: {msg}")
        else:
            print(
                f"Therapy methodology guidelines: ERROR — {msg}",
                file=sys.stderr,
            )
            print(
                "Run 'uv run med-db-setup-therapy-methods' to bootstrap.",
                file=sys.stderr,
            )
            return 1
        return 0

    created = setup(force=args.force)
    if created:
        print("Therapy methodology guidelines ready.")
    else:
        print(
            "Therapy methodology guidelines already present "
            "(use --force to regenerate)."
        )

    # Always verify after setup
    ok, msg = verify()
    if ok:
        print(f"  Verify: {msg}")
    else:
        print(f"  Verify: ERROR — {msg}", file=sys.stderr)
        return 1

    if utils.verify_and_report_integrity(MED_DB) != 0:
        return 1
    return 0


if __name__ == "__main__":
    utils.run_cli(main)
