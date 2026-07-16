"""Create / validate the DSM-5-TR classification reference in med-db/.

Idempotent — skips if classification.json already exists (unless --force).
The classification data is curated from publicly available sources (ICD-10-CM
codes from CDC/WHO, disorder names and category structure from APA-published
materials, Wikipedia, and NIMH).  Diagnostic criteria are copyrighted by APA
and are NOT included.

Usage:
    uv run med-db-setup-dsm5           # create if missing
    uv run med-db-setup-dsm5 --force    # regenerate
"""

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MED_DB = REPO_ROOT / "med-db"
CLASSIFICATION_PATH = MED_DB / "guidelines" / "dsm-5-tr" / "classification.json"


def build_classification():
    """Return the complete DSM-5-TR classification data structure.

    The data is curated from public-domain sources.  When updating, ensure
    every disorder entry has at minimum ``code`` and ``name`` keys.
    """
    return {
        "title": "DSM-5-TR Diagnostic Classification",
        "publisher": "American Psychiatric Association",
        "edition": "5th Edition, Text Revision",
        "publication_date": "2022-03-18",
        "description": (
            "Diagnostic and Statistical Manual of Mental Disorders, Fifth "
            "Edition, Text Revision.  ICD-10-CM codes are used for clinical "
            "billing and administrative purposes in the United States."
        ),
        "license_note": (
            "Diagnostic criteria are copyrighted by APA.  ICD-10-CM codes "
            "and classification structure are in the public domain (WHO/CDC). "
            "Descriptions are from publicly available sources (NIMH, WHO, APA "
            "fact sheets)."
        ),
        "categories": _build_categories(),
        "other_conditions": _build_z_codes(),
        "section_iii_conditions": _build_section_iii(),
    }


def _build_categories():
    return [
        {
            "name": "Neurodevelopmental Disorders",
            "icd10cm_range": "F70-F98",
            "disorders": [
                {"code": "F70", "name": "Intellectual Disability (Intellectual Developmental Disorder)",
                 "specifiers": ["Mild", "Moderate", "Severe", "Profound"]},
                {"code": "F88", "name": "Global Developmental Delay"},
                {"code": "F79", "name": "Unspecified Intellectual Disability"},
                {"code": "F80.0", "name": "Language Disorder"},
                {"code": "F80.81", "name": "Social (Pragmatic) Communication Disorder"},
                {"code": "F80.1", "name": "Speech Sound Disorder"},
                {"code": "F80.81", "name": "Childhood-Onset Fluency Disorder (Stuttering)"},
                {"code": "F84.0", "name": "Autism Spectrum Disorder",
                 "specifiers": ["Level 1: Requiring support", "Level 2: Requiring substantial support",
                                "Level 3: Requiring very substantial support"]},
                {"code": "F81.0", "name": "Specific Learning Disorder",
                 "specifiers": ["With impairment in reading", "With impairment in written expression",
                                "With impairment in mathematics"]},
                {"code": "F82", "name": "Developmental Coordination Disorder"},
                {"code": "F90.9", "name": "Stereotypic Movement Disorder"},
                {"code": "F95.2", "name": "Tourette's Disorder"},
                {"code": "F95.1", "name": "Persistent (Chronic) Motor or Vocal Tic Disorder"},
                {"code": "F95.0", "name": "Provisional Tic Disorder"},
                {"code": "F95.8", "name": "Other Specified Tic Disorder"},
                {"code": "F95.9", "name": "Unspecified Tic Disorder"},
                {"code": "F90.2", "name": "Attention-Deficit/Hyperactivity Disorder",
                 "specifiers": ["Combined presentation", "Predominantly inattentive presentation",
                                "Predominantly hyperactive/impulsive presentation"]},
                {"code": "F90.8", "name": "Other Specified Attention-Deficit/Hyperactivity Disorder"},
                {"code": "F90.9", "name": "Unspecified Attention-Deficit/Hyperactivity Disorder"},
            ],
        },
        {
            "name": "Schizophrenia Spectrum and Other Psychotic Disorders",
            "icd10cm_range": "F20-F29",
            "disorders": [
                {"code": "F21", "name": "Schizotypal (Personality) Disorder"},
                {"code": "F22", "name": "Delusional Disorder",
                 "specifiers": ["Erotomanic type", "Grandiose type", "Jealous type", "Persecutory type",
                                "Somatic type", "Mixed type", "Unspecified type"]},
                {"code": "F23", "name": "Brief Psychotic Disorder"},
                {"code": "F20.81", "name": "Schizophreniform Disorder"},
                {"code": "F20.9", "name": "Schizophrenia"},
                {"code": "F25.0", "name": "Schizoaffective Disorder, Bipolar Type"},
                {"code": "F25.1", "name": "Schizoaffective Disorder, Depressive Type"},
                {"code": "F28", "name": "Other Specified Schizophrenia Spectrum and Other Psychotic Disorder"},
                {"code": "F29", "name": "Unspecified Schizophrenia Spectrum and Other Psychotic Disorder"},
                {"code": "F06.2", "name": "Psychotic Disorder Due to Another Medical Condition"},
                {"code": None, "name": "Catatonia Associated With Another Mental Disorder (Catatonia Specifier)"},
                {"code": "F06.1", "name": "Catatonic Disorder Due to Another Medical Condition"},
                {"code": "F20.2", "name": "Unspecified Catatonia"},
                {"code": "F1x.5", "name": "Substance/Medication-Induced Psychotic Disorder"},
            ],
        },
        {
            "name": "Bipolar and Related Disorders",
            "icd10cm_range": "F30-F39",
            "disorders": [
                {"code": "F31.11", "name": "Bipolar I Disorder, Current or most recent episode manic, Mild"},
                {"code": "F31.12", "name": "Bipolar I Disorder, Current or most recent episode manic, Moderate"},
                {"code": "F31.13", "name": "Bipolar I Disorder, Current or most recent episode manic, Severe"},
                {"code": "F31.2", "name": "Bipolar I Disorder, Current or most recent episode manic, With psychotic features"},
                {"code": "F31.73", "name": "Bipolar I Disorder, Current or most recent episode manic, In partial remission"},
                {"code": "F31.74", "name": "Bipolar I Disorder, Current or most recent episode manic, In full remission"},
                {"code": "F31.9", "name": "Bipolar I Disorder, Current or most recent episode manic, Unspecified"},
                {"code": "F31.81", "name": "Bipolar I Disorder, Current or most recent episode hypomanic"},
                {"code": "F31.31", "name": "Bipolar I Disorder, Current or most recent episode depressed, Mild"},
                {"code": "F31.32", "name": "Bipolar I Disorder, Current or most recent episode depressed, Moderate"},
                {"code": "F31.4", "name": "Bipolar I Disorder, Current or most recent episode depressed, Severe"},
                {"code": "F31.5", "name": "Bipolar I Disorder, Current or most recent episode depressed, With psychotic features"},
                {"code": "F31.75", "name": "Bipolar I Disorder, Current or most recent episode depressed, In partial remission"},
                {"code": "F31.76", "name": "Bipolar I Disorder, Current or most recent episode depressed, In full remission"},
                {"code": "F31.9", "name": "Bipolar I Disorder, Current or most recent episode depressed, Unspecified"},
                {"code": "F31.0", "name": "Bipolar II Disorder"},
                {"code": "F34.0", "name": "Cyclothymic Disorder"},
                {"code": "F31.89", "name": "Other Specified Bipolar and Related Disorder"},
                {"code": "F31.9", "name": "Unspecified Bipolar and Related Disorder"},
                {"code": "F06.33", "name": "Bipolar and Related Disorder Due to Another Medical Condition"},
                {"code": "F1x.5", "name": "Substance/Medication-Induced Bipolar and Related Disorder"},
            ],
        },
        {
            "name": "Depressive Disorders",
            "icd10cm_range": "F32-F39",
            "disorders": [
                {"code": "F34.8", "name": "Disruptive Mood Dysregulation Disorder"},
                {"code": "F32.0", "name": "Major Depressive Disorder, Single episode, Mild"},
                {"code": "F32.1", "name": "Major Depressive Disorder, Single episode, Moderate"},
                {"code": "F32.2", "name": "Major Depressive Disorder, Single episode, Severe"},
                {"code": "F32.3", "name": "Major Depressive Disorder, Single episode, With psychotic features"},
                {"code": "F32.4", "name": "Major Depressive Disorder, Single episode, In partial remission"},
                {"code": "F32.5", "name": "Major Depressive Disorder, Single episode, In full remission"},
                {"code": "F32.9", "name": "Major Depressive Disorder, Single episode, Unspecified"},
                {"code": "F33.0", "name": "Major Depressive Disorder, Recurrent episode, Mild"},
                {"code": "F33.1", "name": "Major Depressive Disorder, Recurrent episode, Moderate"},
                {"code": "F33.2", "name": "Major Depressive Disorder, Recurrent episode, Severe"},
                {"code": "F33.3", "name": "Major Depressive Disorder, Recurrent episode, With psychotic features"},
                {"code": "F33.41", "name": "Major Depressive Disorder, Recurrent episode, In partial remission"},
                {"code": "F33.42", "name": "Major Depressive Disorder, Recurrent episode, In full remission"},
                {"code": "F33.9", "name": "Major Depressive Disorder, Recurrent episode, Unspecified"},
                {"code": "F34.1", "name": "Persistent Depressive Disorder (Dysthymia)"},
                {"code": "N94.3", "name": "Premenstrual Dysphoric Disorder"},
                {"code": "F32.8", "name": "Other Specified Depressive Disorder"},
                {"code": "F32.9", "name": "Unspecified Depressive Disorder"},
                {"code": "F06.31", "name": "Depressive Disorder Due to Another Medical Condition"},
                {"code": "F1x.5", "name": "Substance/Medication-Induced Depressive Disorder"},
            ],
        },
        {
            "name": "Anxiety Disorders",
            "icd10cm_range": "F40-F48",
            "disorders": [
                {"code": "F93.0", "name": "Separation Anxiety Disorder"},
                {"code": "F94.0", "name": "Selective Mutism"},
                {"code": "F40.10", "name": "Specific Phobia"},
                {"code": "F40.00", "name": "Agoraphobia"},
                {"code": "F40.01", "name": "Panic Disorder"},
                {"code": "F41.0", "name": "Panic Attack Specifier"},
                {"code": "F41.1", "name": "Generalised Anxiety Disorder"},
                {"code": "F41.8", "name": "Other Specified Anxiety Disorder"},
                {"code": "F41.9", "name": "Unspecified Anxiety Disorder"},
                {"code": "F06.4", "name": "Anxiety Disorder Due to Another Medical Condition"},
                {"code": "F1x.5", "name": "Substance/Medication-Induced Anxiety Disorder"},
            ],
        },
        {
            "name": "Obsessive-Compulsive and Related Disorders",
            "icd10cm_range": "F42, F45.2, F63, L98.1",
            "disorders": [
                {"code": "F42.2", "name": "Obsessive-Compulsive Disorder"},
                {"code": "F45.22", "name": "Body Dysmorphic Disorder"},
                {"code": "F42.3", "name": "Hoarding Disorder"},
                {"code": "F63.3", "name": "Trichotillomania (Hair-Pulling Disorder)"},
                {"code": "L98.1", "name": "Excoriation (Skin-Picking) Disorder"},
                {"code": "F06.8", "name": "Obsessive-Compulsive and Related Disorder Due to Another Medical Condition"},
                {"code": "F1x.5", "name": "Substance/Medication-Induced Obsessive-Compulsive and Related Disorder"},
                {"code": "F42.8", "name": "Other Specified Obsessive-Compulsive and Related Disorder"},
                {"code": "F42.9", "name": "Unspecified Obsessive-Compulsive and Related Disorder"},
            ],
        },
        {
            "name": "Trauma- and Stressor-Related Disorders",
            "icd10cm_range": "F43-F94",
            "disorders": [
                {"code": "F94.1", "name": "Reactive Attachment Disorder"},
                {"code": "F94.2", "name": "Disinhibited Social Engagement Disorder"},
                {"code": "F43.10", "name": "Posttraumatic Stress Disorder"},
                {"code": "F43.11", "name": "Posttraumatic Stress Disorder, Dissociative subtype"},
                {"code": "F43.12", "name": "Posttraumatic Stress Disorder, Delayed expression"},
                {"code": "F43.0", "name": "Acute Stress Disorder"},
                {"code": "F43.2", "name": "Adjustment Disorders",
                 "specifiers": ["With depressed mood", "With anxiety",
                                "With mixed anxiety and depressed mood",
                                "With disturbance of conduct",
                                "With mixed disturbance of emotions and conduct",
                                "Unspecified"]},
                {"code": "F43.8", "name": "Other Specified Trauma- and Stressor-Related Disorder"},
                {"code": "F43.9", "name": "Unspecified Trauma- and Stressor-Related Disorder"},
                {"code": "F43.8", "name": "Prolonged Grief Disorder",
                 "dsm5tr_note": "New in DSM-5-TR (2022)"},
            ],
        },
        {
            "name": "Dissociative Disorders",
            "icd10cm_range": "F44, F48.1",
            "disorders": [
                {"code": "F44.0", "name": "Dissociative Amnesia"},
                {"code": "F44.1", "name": "Dissociative Identity Disorder"},
                {"code": "F48.1", "name": "Depersonalization/Derealization Disorder"},
                {"code": "F44.81", "name": "Other Specified Dissociative Disorder"},
                {"code": "F44.9", "name": "Unspecified Dissociative Disorder"},
            ],
        },
        {
            "name": "Somatic Symptom and Related Disorders",
            "icd10cm_range": "F44.4-F45, F54, F59",
            "disorders": [
                {"code": "F45.1", "name": "Somatic Symptom Disorder"},
                {"code": "F45.21", "name": "Illness Anxiety Disorder"},
                {"code": "F44.4", "name": "Conversion Disorder (Functional Neurological Symptom Disorder)"},
                {"code": "F54", "name": "Psychological Factors Affecting Other Medical Conditions"},
                {"code": "F68.1", "name": "Factitious Disorder",
                 "specifiers": ["Imposed on self", "Imposed on another"]},
                {"code": "F45.8", "name": "Other Specified Somatic Symptom and Related Disorder"},
                {"code": "F45.9", "name": "Unspecified Somatic Symptom and Related Disorder"},
            ],
        },
        {
            "name": "Feeding and Eating Disorders",
            "icd10cm_range": "F50",
            "disorders": [
                {"code": "F98.2", "name": "Pica"},
                {"code": "F98.21", "name": "Rumination Disorder"},
                {"code": "F50.82", "name": "Avoidant/Restrictive Food Intake Disorder"},
                {"code": "F50.01", "name": "Anorexia Nervosa",
                 "specifiers": ["Restricting type", "Binge-eating/purging type"]},
                {"code": "F50.02", "name": "Bulimia Nervosa"},
                {"code": "F50.81", "name": "Binge-Eating Disorder"},
                {"code": "F50.89", "name": "Other Specified Feeding or Eating Disorder"},
                {"code": "F50.9", "name": "Unspecified Feeding or Eating Disorder"},
            ],
        },
        {
            "name": "Elimination Disorders",
            "icd10cm_range": "F98-F98.1, R15, R32",
            "disorders": [
                {"code": "F98.0", "name": "Enuresis"},
                {"code": "F98.1", "name": "Encopresis"},
                {"code": "R15", "name": "Other Specified Elimination Disorder"},
                {"code": "R32", "name": "Unspecified Elimination Disorder"},
            ],
        },
        {
            "name": "Sleep-Wake Disorders",
            "icd10cm_range": "F51, G47, G25.8",
            "disorders": [
                {"code": "F51.01", "name": "Insomnia Disorder"},
                {"code": "G47.419", "name": "Hypersomnolence Disorder"},
                {"code": "G47.411", "name": "Narcolepsy"},
                {"code": "G47.33", "name": "Obstructive Sleep Apnea Hypopnea"},
                {"code": "R06.83", "name": "Central Sleep Apnea"},
                {"code": "G47.35", "name": "Sleep-Related Hypoventilation"},
                {"code": "G47.20", "name": "Circadian Rhythm Sleep-Wake Disorders"},
                {"code": "F51.3", "name": "Non-Rapid Eye Movement Sleep Arousal Disorders"},
                {"code": "F51.5", "name": "Nightmare Disorder"},
                {"code": "G47.52", "name": "Rapid Eye Movement Sleep Behavior Disorder"},
                {"code": "G25.81", "name": "Restless Legs Syndrome"},
                {"code": "G47.8", "name": "Other Specified Insomnia Disorder"},
                {"code": "G47.00", "name": "Unspecified Insomnia Disorder"},
                {"code": "G47.429", "name": "Other Specified Hypersomnolence Disorder"},
                {"code": "G47.419", "name": "Unspecified Hypersomnolence Disorder"},
                {"code": "G47.8", "name": "Other Specified Sleep-Wake Disorder"},
                {"code": "G47.9", "name": "Unspecified Sleep-Wake Disorder"},
                {"code": "F1x.5", "name": "Substance/Medication-Induced Sleep Disorder"},
            ],
        },
        {
            "name": "Sexual Dysfunctions",
            "icd10cm_range": "F52, N52-N53, N94",
            "disorders": [
                {"code": "F52.22", "name": "Female Sexual Interest/Arousal Disorder"},
                {"code": "F52.31", "name": "Female Orgasmic Disorder"},
                {"code": "F52.6", "name": "Genito-Pelvic Pain/Penetration Disorder"},
                {"code": "F52.32", "name": "Male Hypoactive Sexual Desire Disorder"},
                {"code": "F52.21", "name": "Erectile Disorder"},
                {"code": "F52.4", "name": "Premature (Early) Ejaculation"},
                {"code": "F52.31", "name": "Delayed Ejaculation"},
                {"code": "F52.8", "name": "Other Specified Sexual Dysfunction"},
                {"code": "F52.9", "name": "Unspecified Sexual Dysfunction"},
                {"code": "F1x.5", "name": "Substance/Medication-Induced Sexual Dysfunction"},
            ],
        },
        {
            "name": "Gender Dysphoria",
            "icd10cm_range": "F64",
            "disorders": [
                {"code": "F64.2", "name": "Gender Dysphoria in Children"},
                {"code": "F64.0", "name": "Gender Dysphoria in Adolescents and Adults"},
                {"code": "F64.8", "name": "Other Specified Gender Dysphoria"},
                {"code": "F64.9", "name": "Unspecified Gender Dysphoria"},
            ],
            "dsm5tr_note": (
                "ICD-11 reclassifies gender incongruence under 'Conditions "
                "Related to Sexual Health' (HA60-HA61), removed from mental "
                "disorders chapter. DSM-5-TR retains in mental disorders "
                "classification for clinical and access-to-care reasons."
            ),
        },
        {
            "name": "Disruptive, Impulse-Control, and Conduct Disorders",
            "icd10cm_range": "F63, F91",
            "disorders": [
                {"code": "F91.3", "name": "Oppositional Defiant Disorder"},
                {"code": "F63.81", "name": "Intermittent Explosive Disorder"},
                {"code": "F91.1", "name": "Conduct Disorder",
                 "specifiers": ["Childhood-onset type", "Adolescent-onset type",
                                "Unspecified onset", "With limited prosocial emotions"]},
                {"code": "Z60.4", "name": "Antisocial Personality Disorder",
                 "note": "Also listed in Personality Disorders chapter"},
                {"code": "F91.2", "name": "Pyromania"},
                {"code": "F63.2", "name": "Kleptomania"},
                {"code": "F91.8", "name": "Other Specified Disruptive, Impulse-Control, and Conduct Disorder"},
                {"code": "F91.9", "name": "Unspecified Disruptive, Impulse-Control, and Conduct Disorder"},
            ],
        },
        {
            "name": "Substance-Related and Addictive Disorders",
            "icd10cm_range": "F10-F19, F50.81, Z72.6, F63.0",
            "disorders": [
                {"code": "F10.10", "name": "Alcohol Use Disorder",
                 "specifiers": ["Mild", "Moderate", "Severe"]},
                {"code": "F10.20", "name": "Alcohol Intoxication"},
                {"code": "F10.239", "name": "Alcohol Withdrawal"},
                {"code": "F12.10", "name": "Cannabis Use Disorder"},
                {"code": "F12.20", "name": "Cannabis Intoxication"},
                {"code": "F12.288", "name": "Cannabis Withdrawal"},
                {"code": "F16.10", "name": "Hallucinogen Use Disorder (Phencyclidine, Other)"},
                {"code": "F16.20", "name": "Hallucinogen Intoxication"},
                {"code": "F18.10", "name": "Inhalant Use Disorder"},
                {"code": "F18.20", "name": "Inhalant Intoxication"},
                {"code": "F11.10", "name": "Opioid Use Disorder"},
                {"code": "F11.20", "name": "Opioid Intoxication"},
                {"code": "F11.23", "name": "Opioid Withdrawal"},
                {"code": "F15.10", "name": "Stimulant Use Disorder"},
                {"code": "F15.20", "name": "Stimulant Intoxication"},
                {"code": "F15.23", "name": "Stimulant Withdrawal"},
                {"code": "F17.200", "name": "Tobacco Use Disorder"},
                {"code": "F17.203", "name": "Tobacco Withdrawal"},
                {"code": "F13.10", "name": "Sedative, Hypnotic, or Anxiolytic Use Disorder"},
                {"code": "F13.20", "name": "Sedative, Hypnotic, or Anxiolytic Intoxication"},
                {"code": "F13.239", "name": "Sedative, Hypnotic, or Anxiolytic Withdrawal"},
                {"code": "F14.10", "name": "Cocaine Use Disorder — see also Stimulant Use Disorder"},
                {"code": "F63.0", "name": "Gambling Disorder"},
                {"code": "F19.10", "name": "Other (or Unknown) Substance Use Disorder"},
                {"code": "F19.20", "name": "Other (or Unknown) Substance Intoxication"},
                {"code": "F19.239", "name": "Other (or Unknown) Substance Withdrawal"},
            ],
        },
        {
            "name": "Neurocognitive Disorders",
            "icd10cm_range": "F01-F09, G30-G31",
            "disorders": [
                {"code": "F02.80", "name": "Delirium"},
                {"code": "F02.81", "name": "Major Neurocognitive Disorder Due to Alzheimer's Disease"},
                {"code": "G31.84", "name": "Mild Neurocognitive Disorder Due to Alzheimer's Disease"},
                {"code": "F02.80", "name": "Major Neurocognitive Disorder With Lewy Bodies"},
                {"code": "G31.84", "name": "Mild Neurocognitive Disorder With Lewy Bodies"},
                {"code": "F02.81", "name": "Major Vascular Neurocognitive Disorder"},
                {"code": "G31.84", "name": "Mild Vascular Neurocognitive Disorder"},
                {"code": "F02.81", "name": "Major Neurocognitive Disorder Due to Traumatic Brain Injury"},
                {"code": "G31.84", "name": "Mild Neurocognitive Disorder Due to Traumatic Brain Injury"},
                {"code": "F02.81", "name": "Major Neurocognitive Disorder Due to Parkinson's Disease"},
                {"code": "G31.84", "name": "Mild Neurocognitive Disorder Due to Parkinson's Disease"},
                {"code": "F02.81", "name": "Major Neurocognitive Disorder Due to HIV Infection"},
                {"code": "G31.84", "name": "Mild Neurocognitive Disorder Due to HIV Infection"},
                {"code": "F02.81", "name": "Major Neurocognitive Disorder Due to Huntington's Disease"},
                {"code": "G31.84", "name": "Mild Neurocognitive Disorder Due to Huntington's Disease"},
                {"code": "F02.81", "name": "Major Neurocognitive Disorder Due to Prion Disease"},
                {"code": "G31.84", "name": "Mild Neurocognitive Disorder Due to Prion Disease"},
                {"code": "F02.81", "name": "Major Frontotemporal Neurocognitive Disorder"},
                {"code": "G31.84", "name": "Mild Frontotemporal Neurocognitive Disorder"},
                {"code": "F02.81", "name": "Major Neurocognitive Disorder Due to Another Medical Condition"},
                {"code": "G31.84", "name": "Mild Neurocognitive Disorder Due to Another Medical Condition"},
                {"code": "F1x.5", "name": "Substance/Medication-Induced Major or Mild Neurocognitive Disorder"},
                {"code": "R41.9", "name": "Unspecified Neurocognitive Disorder"},
            ],
        },
        {
            "name": "Personality Disorders",
            "icd10cm_range": "F60-F69",
            "disorders": [
                {"code": "F60.0", "name": "Paranoid Personality Disorder"},
                {"code": "F60.1", "name": "Schizoid Personality Disorder"},
                {"code": "F21", "name": "Schizotypal Personality Disorder"},
                {"code": "F60.2", "name": "Antisocial Personality Disorder"},
                {"code": "F60.3", "name": "Borderline Personality Disorder"},
                {"code": "F60.4", "name": "Histrionic Personality Disorder"},
                {"code": "F60.5", "name": "Narcissistic Personality Disorder"},
                {"code": "F60.6", "name": "Avoidant Personality Disorder"},
                {"code": "F60.7", "name": "Dependent Personality Disorder"},
                {"code": "F60.81", "name": "Obsessive-Compulsive Personality Disorder"},
                {"code": "F60.89", "name": "Other Specified Personality Disorder"},
                {"code": "F60.9", "name": "Unspecified Personality Disorder"},
                {"code": "F07.0", "name": "Personality Change Due to Another Medical Condition"},
            ],
            "dsm5tr_note": (
                "Section III contains the Alternative DSM-5 Model for "
                "Personality Disorders (AMPD) — a dimensional-categorical "
                "hybrid covering 6 PD types. ICD-11 has adopted a fully "
                "dimensional model with severity levels and trait domain "
                "specifiers."
            ),
        },
        {
            "name": "Paraphilic Disorders",
            "icd10cm_range": "F65",
            "disorders": [
                {"code": "F65.81", "name": "Voyeuristic Disorder"},
                {"code": "F65.2", "name": "Exhibitionistic Disorder"},
                {"code": "F65.0", "name": "Frotteuristic Disorder"},
                {"code": "F65.51", "name": "Sexual Masochism Disorder"},
                {"code": "F65.52", "name": "Sexual Sadism Disorder"},
                {"code": "F65.4", "name": "Pedophilic Disorder"},
                {"code": "F65.81", "name": "Fetishistic Disorder"},
                {"code": "F65.1", "name": "Transvestic Disorder"},
                {"code": "F65.89", "name": "Other Specified Paraphilic Disorder"},
                {"code": "F65.9", "name": "Unspecified Paraphilic Disorder"},
            ],
        },
    ]


def _build_z_codes():
    return [
        {"code": "Z91.49", "name": "Other Personal History of Psychological Trauma"},
        {"code": "Z91.5", "name": "Personal History of Self-Harm"},
        {"code": "Z91.83", "name": "Wandering Associated with a Mental Disorder"},
        {"code": "Z91.89", "name": "Other Specified Personal Risk Factors (Suicidality, Nonsuicidal Self-Injury)"},
        {"code": "Z69", "name": "Problems Related to Living Alone"},
        {"code": "Z60", "name": "Acculturation Difficulty"},
        {"code": "Z62", "name": "Problems Related to Upbringing"},
        {"code": "Z63", "name": "Other Problems Related to Primary Support Group"},
        {"code": "Z64", "name": "Problems Related to Other Psychosocial Circumstances"},
        {"code": "Z65", "name": "Problems Related to Other Psychosocial, Personal, and Environmental Circumstances"},
        {"code": "Z72.811", "name": "Adult Antisocial Behavior"},
        {"code": "Z72.810", "name": "Child or Adolescent Antisocial Behavior"},
        {"code": "Z91.19", "name": "Nonadherence to Medical Treatment"},
        {"code": "Z76.5", "name": "Malingering"},
        {"code": "Z56", "name": "Problems Related to Employment or Unemployment"},
        {"code": "Z55", "name": "Problems Related to Education and Literacy"},
        {"code": "Z59", "name": "Problems Related to Housing and Economic Circumstances"},
    ]


def _build_section_iii():
    return [
        {"code": None, "name": "Attenuated Psychosis Syndrome", "status": "Further Study"},
        {"code": None, "name": "Depressive Episodes With Short-Duration Hypomania", "status": "Further Study"},
        {"code": None, "name": "Persistent Complex Bereavement Disorder",
         "status": "Further Study (replaced by Prolonged Grief Disorder in DSM-5-TR Section II)"},
        {"code": "F15.98", "name": "Caffeine Use Disorder", "status": "Further Study"},
        {"code": "F63.0", "name": "Internet Gaming Disorder", "status": "Further Study"},
        {"code": None, "name": "Neurobehavioral Disorder Associated With Prenatal Alcohol Exposure",
         "status": "Further Study"},
        {"code": None, "name": "Suicidal Behavior Disorder", "status": "Further Study"},
        {"code": None, "name": "Nonsuicidal Self-Injury", "status": "Further Study"},
    ]


def setup(force=False):
    """Create the DSM-5-TR classification.json if it doesn't exist.

    Returns True if created, False if already present (and not forced).
    """
    CLASSIFICATION_PATH.parent.mkdir(parents=True, exist_ok=True)

    if CLASSIFICATION_PATH.exists() and not force:
        return False

    data = build_classification()
    with open(CLASSIFICATION_PATH, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)

    total = sum(len(c["disorders"]) for c in data["categories"])
    print(f"Created DSM-5-TR classification: {len(data['categories'])} categories, {total} disorders")
    return True


def verify():
    """Quick smoke test."""
    if not CLASSIFICATION_PATH.exists():
        return False, "classification.json not found"
    with open(CLASSIFICATION_PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    cats = len(data.get("categories", []))
    total = sum(len(c.get("disorders", [])) for c in data.get("categories", []))
    return True, f"{cats} categories, {total} disorders"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create/validate the DSM-5-TR classification reference in med-db/"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Regenerate classification.json even if it already exists.",
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
            print(f"DSM-5-TR classification: {msg}")
        else:
            print(f"DSM-5-TR classification: ERROR — {msg}", file=sys.stderr)
            return 1
        return 0

    created = setup(force=args.force)
    if created:
        print("DSM-5-TR classification ready.")
    else:
        print("DSM-5-TR classification already present (use --force to regenerate).")

    # Always verify after setup
    ok, msg = verify()
    if ok:
        print(f"  Verify: {msg}")
    else:
        print(f"  Verify: ERROR — {msg}", file=sys.stderr)
        return 1

    # Ensure source.md exists
    source_md = CLASSIFICATION_PATH.parent / "source.md"
    if not source_md.exists():
        print()
        print("  source.md not found — it should be created separately "
              "(it ships with the repo under med-db/guidelines/dsm-5-tr/source.md)")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("cancelled", file=sys.stderr)
        raise SystemExit(130)
