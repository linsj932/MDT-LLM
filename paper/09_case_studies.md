# Appendix E: Case Studies


Three illustrative cases chosen to highlight qualitative differences across conditions. All responses are from Claude Sonnet 4.5.


## Case A — Largest MDT+RAG benefit: Q049 (D4_Subsequent_Resistance, Easy)

### Vignette
> A 63-year-old female with stage IV NSCLC, KRAS G12C mutation, progresses after first-line carboplatin/pemetrexed/pembrolizumab. ECOG PS 1.

### Question
> What targeted therapy option is available for this patient?

### Gold-standard answer
> KRAS G12C-targeted therapy in the second-line setting: (1) Sotorasib 960mg daily (CodeBreaK 200, ORR ~28%, Category 1) or adagrasib 600mg BID (KRYSTAL-1, ORR ~43%, Category 2A) are both approved options; (2) Both are oral agents with manageable toxicity profiles; (3) Sotorasib has PFS benefit vs. docetaxel in phase III; (4) Choice between agents depends on availability, toxicity profile, and patient preference; (5) Common side effects: GI toxicity, liver enzyme elevations; (6) Ongoing combinations (sotorasib + chemo or IO) are in trials but not yet standard.

### Model responses (Claude Sonnet across 4 conditions)

#### Single Zeroshot — mean score **3.25/5**, hallucination=1
```
# Targeted Therapy Recommendation for KRAS G12C-Mutated NSCLC

## Recommendation
**Sotorasib (240 mg PO daily)** or **Adagrasib (600 mg PO twice daily)** are FDA-approved targeted therapy options for this patient.

## Clinical Reasoning

### Patient Context
- Stage IV NSCLC with **KRAS G12C mutation** (present in ~13% of lung adenocarcinomas)
- Progression after platinum-based chemotherapy plus immunotherapy
- Good performance status (ECOG PS 1) - suitable for further therapy

### Evidence Base

**Sotorasib (CodeBreaK 100 trial):**
- ORR: 37.1%
- Median PFS: 6.8 months
- Median OS: 12.5 months
- FDA approved May 2021 for previously treated KRAS G12C-mutated NSCLC

**Adagrasib (KRYSTAL-1 trial):**
- ORR: 42.9%
- Median PFS: 6.5 months
- Median OS: 12.6 months
- FDA approved December 2022

### Key Considerations

1. **Sequencing**: Both agents are approved after ≥1 prior systemic therapy
2. **Selection**: No head-to-head comparison; choice based on:
   - Dosing convenience (once vs. twice daily)
   - Side effect profile
   - CNS involvement (adagrasib has demonstrated CNS activity)
3. **Monitoring**: LFTs, GI toxicity, QTc prolongation

This represents a significant advance in precision oncology for previously "undruggable" KRAS mutations.
```

#### Single Rag — mean score **4.50/5**, hallucination=0
```
# Clinical Recommendation for KRAS G12C-Mutated NSCLC After First-Line Progression

## Answer
**Two targeted therapy options are available for this patient:**
1. **Sotorasib**
2. **Adagrasib**

## Reasoning

### Patient Context
- Stage IV NSCLC with **KRAS G12C mutation**
- Progressed after first-line platinum-based chemotherapy plus immunotherapy
- Good performance status (ECOG PS 1) - suitable for targeted therapy

### Evidence-Based Rationale

1. **FDA-Approved Indications**: Both sotorasib and adagrasib have received **accelerated FDA approval** for adults with KRAS G12C-mutated locally advanced or metastatic NSCLC who have received **at least one prior systemic therapy**.

2. **Clinical Trial Support**: The **CodeBreaK 200 trial** (phase 3, randomized) demonstrated efficacy of sotorasib versus docetaxel in patients with KRAS G12C mutation-positive advanced NSCLC who had previously received systemic therapy.

3. **Guideline Recommendation**: Per NCCN guidelines (NSCL-K), both agents are listed as **subsequent therapy options** specifically for KRAS G12C-mutated NSCLC.

### Important Considerations
- These are **oral small molecule inhibitors** that specifically target KRAS G12C
- **Do not switch between sotorasib and adagrasib** at progression, as they share similar mechanisms of action
- After progression on KRAS G12C-targeted therapy, consider standard systemic therapy options

## Conclusion
Either sotorasib or adagrasib represents an appropriate evidence-based targeted

[... truncated ...]
```

#### Mdt Zeroshot — mean score **5.00/5**, hallucination=0
```
# MULTIDISCIPLINARY TUMOR BOARD CONSENSUS RECOMMENDATION
## Stage IV NSCLC with KRAS G12C Mutation - Post-First-Line Progression

---

## CASE SUMMARY
**Patient:** 63-year-old female  
**Diagnosis:** Stage IV NSCLC with KRAS G12C mutation  
**Prior Treatment:** Carboplatin/pemetrexed/pembrolizumab (first-line) - progressed  
**Performance Status:** ECOG PS 1 (suitable for further therapy)  
**Treatment Decision Point:** Second-line systemic therapy selection

---

## CONSENSUS TREATMENT RECOMMENDATION

### **PRIMARY RECOMMENDATION: KRAS G12C Inhibitor Therapy**

**Preferred Agent: SOTORASIB (Lumakras®)**
- **Dosing:** 960 mg orally once daily continuously
- **FDA Approval:** May 2021 for KRAS G12C-mutated locally advanced/metastatic NSCLC after ≥1 prior systemic therapy
- **Evidence Base:** CodeBreaK 100 trial (N=126)
  - ORR: 37.1% (95% CI: 28.6-46.2%)
  - Median PFS: 6.8 months
  - Median OS: 12.5 months
  - Disease control rate: 80.6%
  - Grade ≥3 AEs: 19.8% (favorable toxicity profile)

**Alternative Agent: ADAGRASIB (Krazati®)**
- **Dosing:** 600 mg orally twice daily continuously
- **FDA Approval:** December 2022 for same indication
- **Evidence Base:** KRYSTAL-1 trial (N=112)
  - ORR: 42.9% (95% CI: 33.6-52.5%)
  - Median PFS: 6.5 months
  - Median OS: 12.6 months
  - Grade ≥3 AEs: 44.9%
- **Specific Advantage:** CNS penetration (preferred if brain metastases present)

### **Rationale for KRAS G12C Inhibitor Selection:**

1. **Molecular-directed therapy principle:** Ta

[... truncated ...]
```

#### Mdt Rag — mean score **5.00/5**, hallucination=0
```
# MULTIDISCIPLINARY TUMOR BOARD CONSENSUS RECOMMENDATION

**Patient:** 63-year-old female with stage IV NSCLC, KRAS G12C mutation  
**Clinical Status:** Progression after first-line carboplatin/pemetrexed/pembrolizumab, ECOG PS 1  
**Date:** [Current Date]

---

## I. UNIFIED TREATMENT RECOMMENDATION

### **Primary Treatment Plan: KRAS G12C-Targeted Therapy**

**CONSENSUS:** The MDT unanimously recommends initiation of **KRAS G12C-targeted therapy** as the preferred subsequent treatment approach.

#### **Agent Selection:**

**First Choice: Sotorasib 960 mg orally once daily**

**Rationale for Selection:**
- **Level 1 Evidence:** CodeBreaK 200 Phase 3 randomized trial demonstrated superiority over docetaxel (PFS 5.6 vs 4.5 months, HR 0.66, p=0.002; ORR 28.1% vs 13.2%)
- **FDA Approval:** Approved for KRAS G12C-mutated locally advanced/metastatic NSCLC after ≥1 prior systemic therapy
- **NCCN Category 1 Recommendation:** Highest level of evidence and consensus
- **Practical Advantages:** Once-daily dosing may improve adherence
- **Quality of Life:** Superior patient-reported outcomes vs. chemotherapy

**Alternative: Adagrasib 600 mg orally twice daily**

**Consider if:**
- CNS metastases present (demonstrated intracranial activity in KRYSTAL-1 trial)
- Patient preference for potentially higher response rates (ORR 42.9% treatment-naïve, 34.3% previously treated)
- Patient can reliably manage twice-daily dosing

---

## II. CRITICAL TREATMENT PRINCIPLES

### **Pre-Treatment Requi

[... truncated ...]
```


## Case B — Clearest RAG harm: Q029 (D1_Diagnosis_Screening, Easy)

### Vignette
> A 57-year-old male undergoes LDCT screening and is found to have a 4mm solid nodule in the left lower lobe. No prior imaging. He has a 22 pack-year smoking history and continues to smoke.

### Question
> What follow-up is recommended for this small nodule?

### Gold-standard answer
> For a solid nodule <6mm detected on LDCT screening, this is classified as Lung-RADS category 2 (benign appearance or behavior). Recommendation: continue annual LDCT screening. No short-interval follow-up CT is needed for nodules <6mm. Smoking cessation counseling remains essential.

### Model responses (Claude Sonnet across 4 conditions)

#### Single Zeroshot — mean score **4.38/5**, hallucination=0
```
# Recommended Follow-up for 4mm Solid Nodule on LDCT Screening

## Recommendation
**12-month follow-up LDCT is recommended** for this 4mm solid nodule.

## Reasoning

Based on **Lung-RADS version 2022** (ACR Lung CT Screening Reporting & Data System), which provides standardized management for lung screening findings:

### Nodule Classification
- **Size**: 4mm solid nodule
- **Category**: Lung-RADS 2 (Benign appearance or behavior)
- Solid nodules <6mm in baseline screening are considered low risk

### Evidence-Based Rationale

1. **Low Malignancy Risk**: Solid nodules <6mm have a very low probability of malignancy (<1%)

2. **Lung-RADS 2 Management**: 
   - Continue annual screening (12-month follow-up LDCT)
   - No additional short-interval imaging needed
   - No need for PET/CT or biopsy at this size

3. **Risk Factors Present**:
   - Active smoker (22 pack-years meets screening criteria)
   - Age 57 (within screening age range 50-80)
   - These factors warrant continued surveillance rather than dismissal

### Additional Recommendations

1. **Smoking Cessation Counseling**: Critical intervention - reduces lung cancer risk by 30-50% over time
2. **Annual LDCT Screening**: Continue as long as patient remains eligible
3. **Document Baseline**: This establishes baseline for future comparison
4. **Patient Education**: Discuss low-risk nature while emphasizing importance of follow-up compliance

**No immediate intervention is needed** - routine annual surveillance is appropriate

[... truncated ...]
```

#### Single Rag — mean score **2.00/5**, hallucination=1
```
# Recommended Follow-Up for 4mm Solid Nodule on LDCT Screening

## Recommendation:
**LDCT in 6 months** is the recommended follow-up for this patient.

## Reasoning:

Based on the NCCN Lung Cancer Screening Guidelines Version 1.2026:

1. **Nodule Classification**: The patient has a **4mm solid nodule**, which falls into the **<8mm category** for solid nodules detected on screening LDCT.

2. **Guideline-Based Management**: According to the algorithm for "Solid nodule(s) on follow-up or annual LDCT":
   - Nodules **<8mm** → **LDCT in 6 months**
   - Nodules ≥8mm to <15mm → LDCT in 6 months
   - Nodules ≥15mm → LDCT in 6 months or FDG-PET/CT

3. **Risk Stratification**: While this is a small nodule with relatively low risk of malignancy, the patient has:
   - Active smoking status
   - Adequate smoking history (22 pack-years)
   - No prior imaging for comparison

4. **Rationale for 6-Month Follow-up**: 
   - Allows assessment for growth or stability
   - Avoids unnecessary invasive procedures for likely benign findings
   - Maintains appropriate surveillance for the small possibility of early-stage lung cancer
   - If unchanged at 6 months, would typically transition to annual screening

## Additional Considerations:
- Smoking cessation counseling should be provided
- Patient should continue in the annual screening program if nodule remains stable
- Any growth or change in characteristics would prompt reassessment per guidelines
```

#### Mdt Zeroshot — mean score **5.00/5**, hallucination=0
```
# MULTIDISCIPLINARY TUMOR BOARD CONSENSUS RECOMMENDATION

## Case Summary
57-year-old male, active smoker (22 pack-years), screening-detected 4mm solid nodule in left lower lobe, no prior imaging available.

---

## CONSENSUS TREATMENT PLAN

### Primary Recommendation: **SURVEILLANCE WITHOUT INTERVENTION**

**Imaging Follow-up:**
- **12-month follow-up LDCT** (annual screening interval)
- Continue annual LDCT screening thereafter if nodule remains stable
- **Lung-RADS Category 2** classification

**Critical Concurrent Intervention:**
- **IMMEDIATE referral to smoking cessation program**
  - First-line pharmacotherapy: Varenicline, bupropion, or nicotine replacement therapy
  - Behavioral counseling support
  - **This is the single most important intervention** - reduces lung cancer risk by 30-50% over 10 years

**What is NOT recommended:**
- ❌ Tissue biopsy (risk >> benefit at 4mm; high non-diagnostic rate)
- ❌ PET/CT (insufficient size; high false-negative rate)
- ❌ Short-interval CT (3-6 months) - increases radiation exposure, cost, and patient anxiety without clinical benefit
- ❌ Any systemic therapy or radiation therapy
- ❌ Surgical consultation at this time

---

## POINTS OF AGREEMENT (UNANIMOUS)

All four specialists independently reached identical conclusions:

1. **Malignancy risk <1%** for 4mm solid nodule
2. **Lung-RADS Category 2** appropriate classification
3. **12-month follow-up LDCT** is evidence-based standard
4. **No tissue diagnosis indicated** at current s

[... truncated ...]
```

#### Mdt Rag — mean score **5.00/5**, hallucination=0
```
# MULTIDISCIPLINARY TUMOR BOARD CONSENSUS RECOMMENDATION

**Case:** 57-year-old male, active smoker (22 pack-years), 4mm solid nodule left lower lobe on initial LDCT screening

---

## CONSENSUS TREATMENT PLAN

### **Primary Recommendation: LDCT Surveillance in 12 Months (Annual Screening)**

After careful review of all specialist inputs and current evidence, the MDT reaches the following consensus:

**Imaging Follow-up:**
- **Continue annual LDCT screening** (12-month interval)
- No immediate short-interval imaging required
- Escalate to 6-month LDCT only if nodule demonstrates growth or morphologic changes

**Rationale:**
- 4mm solid nodule carries <1% malignancy risk (Horeweg et al., *Lancet Oncol* 2014)
- Falls well below 6mm threshold for heightened concern
- NCCN Lung Cancer Screening Guidelines v1.2026: Solid nodules <6mm on baseline screening typically warrant annual follow-up
- Risk of overdiagnosis and patient harm from aggressive surveillance exceeds cancer risk at this size

### **Critical Intervention: Smoking Cessation**

**Immediate referral to smoking cessation program**
- Evidence-based pharmacotherapy options:
  - Varenicline (Chantix) 0.5mg daily × 3 days, then 0.5mg BID × 4 days, then 1mg BID × 11-23 weeks
  - OR Bupropion SR 150mg daily × 3 days, then 150mg BID × 7-12 weeks
  - PLUS nicotine replacement therapy (patch, gum, or lozenge)
- Behavioral counseling (individual or group)
- **Impact:** 30-50% reduction in lung cancer risk over 10 years; 40-50% re

[... truncated ...]
```


## Case C — Highest judge disagreement: Q089 (D5_Adverse_Events, Medium)

### Vignette
> A 71-year-old male on pembrolizumab develops new-onset type 1 diabetes with DKA (glucose 480 mg/dL, pH 7.15, ketones positive) after cycle 3. He had no prior history of diabetes.

### Question
> How should immune-related diabetes and DKA be managed?

### Gold-standard answer
> IO-related type 1 diabetes with DKA is a rare (~1%) but potentially life-threatening irAE: (1) Immediate DKA management per standard protocol: IV insulin infusion, aggressive IV fluid resuscitation, electrolyte correction (potassium monitoring); (2) ICU admission for DKA management; (3) Hold pembrolizumab during acute management; (4) Check C-peptide (will be low/undetectable) and anti-GAD antibodies; (5) Steroids are NOT effective for IO-related T1DM (unlike most irAEs)—beta-cell destruction is typically complete and irreversible; (6) Transition to basal-bolus insulin regimen once DKA resolves; (7) Endocrinology consultation for long-term diabetes management; (8) Pembrolizumab CAN be resumed once diabetes is well-controlled on insulin; (9) Patient education: this is permanent insulin-dependent diabetes; (10) Screen for concurrent endocrinopathies (thyroid, adrenal).

### Model responses (Claude Sonnet across 4 conditions)

#### Single Zeroshot — mean score **3.88/5**, hallucination=0
```
# Management of Immune-Related Diabetes with DKA

## Immediate Management

### 1. **DKA Treatment (Priority)**
- **Hospitalize immediately** - ICU/step-down unit monitoring
- **Fluid resuscitation**: 0.9% normal saline (1-1.5 L in first hour)
- **Insulin therapy**: 
  - IV regular insulin infusion (0.1 units/kg/hour)
  - Continue until anion gap closes and pH >7.3
  - Transition to subcutaneous insulin with overlap
- **Electrolyte monitoring**: Potassium replacement as needed
- **Monitor**: Glucose hourly, electrolytes q2-4h, venous pH

### 2. **Immunotherapy Management**
- **PERMANENTLY DISCONTINUE pembrolizumab**
  - Immune-related diabetes is typically **irreversible**
  - Risk of recurrent DKA with rechallenge is unacceptably high
  - This is a Grade 4 immune-related adverse event

### 3. **Corticosteroid Use**
- **NOT routinely recommended** for immune-related diabetes
- Corticosteroids do NOT reverse beta-cell destruction
- May worsen hyperglycemia
- Consider only if concurrent severe immune-related adverse events

## Long-Term Diabetes Management

### 4. **Insulin Therapy (Lifelong)**
- **Basal-bolus regimen** required (this is Type 1 diabetes)
- Initial total daily dose: 0.5-0.6 units/kg
- Split: 50% basal (glargine/detemir), 50% prandial (lispro/aspart)
- **Endocrinology consultation mandatory**

### 5. **Monitoring**
- Check C-peptide and autoantibodies (GAD65, IA-2, ZnT8) - often negative in immune-related diabetes
- HbA1c baseline and q3 months
- Screen for other 

[... truncated ...]
```

#### Single Rag — mean score **4.25/5**, hallucination=0
```
# Management of Immune-Related Type 1 Diabetes with DKA

## Immediate Management Recommendations:

### 1. **HOLD Immunotherapy**
- **Discontinue pembrolizumab** until DKA resolves
- This is explicitly stated in the guidelines for ICI-associated T1DM with DKA present

### 2. **Urgent Endocrine Consultation & Inpatient Care**
- **Immediate endocrinology consultation** required
- **Inpatient admission** mandatory for DKA management

### 3. **DKA Management**
- Manage DKA per institutional guidelines:
  - IV fluid resuscitation
  - Insulin infusion protocol
  - Electrolyte monitoring and replacement (especially potassium)
  - Correction of acidosis
  - Close monitoring of blood pH, glucose, and ketones

### 4. **Insulin Therapy**
- Initiate insulin therapy as directed by endocrinologist/inpatient team
- **Close glucose monitoring** essential
- Consider **early use of continuous glucose monitoring (CGM)**
- This patient will require **lifelong insulin therapy** (ICI-T1DM is typically irreversible)

### 5. **Resumption of Immunotherapy**
- **Continue immunotherapy** once DKA resolves
- The guidelines indicate immunotherapy can be continued after DKA resolution, as the diabetes itself is managed with insulin

## Key Clinical Points:
- ICI-related T1DM is rare (1-2%) but **life-threatening** without insulin
- Unlike other immune-related adverse events, this typically does **not** require corticosteroids
- The diabetes is usually **permanent** and requires ongoing insulin management



[... truncated ...]
```

#### Mdt Zeroshot — mean score **4.25/5**, hallucination=0
```
# MULTIDISCIPLINARY TUMOR BOARD CONSENSUS RECOMMENDATION

## Case Summary
71-year-old male with pembrolizumab-induced type 1 diabetes mellitus presenting with diabetic ketoacidosis (DKA) after cycle 3 of immunotherapy. This represents a **Grade 4 immune-related adverse event (irAE)** requiring immediate intervention.

---

## CONSENSUS TREATMENT PLAN

### PHASE 1: IMMEDIATE MANAGEMENT (0-48 Hours)

#### A. DKA Management - **CRITICAL PRIORITY**
**All specialists unanimously agree:**

1. **Immediate hospitalization** to ICU or step-down unit
2. **Aggressive fluid resuscitation:**
   - 1-2L 0.9% normal saline bolus over first hour
   - Continue 250-500 mL/hr, adjust based on hemodynamics
   - Add dextrose (D5) when glucose <250 mg/dL

3. **Insulin therapy:**
   - IV regular insulin infusion: 0.1 units/kg/hour
   - Continue until anion gap closes and ketones clear
   - Do NOT stop insulin when glucose normalizes

4. **Electrolyte management:**
   - Monitor potassium q2-4h (replace to maintain 4-5 mEq/L)
   - Monitor phosphate, magnesium
   - Correct acidosis (bicarbonate only if pH <6.9)

5. **Monitoring:**
   - Glucose hourly until stable
   - Electrolytes q2-4h
   - Venous pH/anion gap q4h until normalized
   - Cardiac monitoring

#### B. Pembrolizumab Management - **UNANIMOUS DECISION**

**PERMANENTLY DISCONTINUE pembrolizumab**

**Rationale (consensus points):**
- Immune checkpoint inhibitor-induced type 1 diabetes is **irreversible** (>95% permanent insulin dependence)
- β-

[... truncated ...]
```

#### Mdt Rag — mean score **5.00/5**, hallucination=0
```
# MULTIDISCIPLINARY TUMOR BOARD CONSENSUS RECOMMENDATION
## Immune Checkpoint Inhibitor-Related Type 1 Diabetes with Diabetic Ketoacidosis

**Patient**: 71-year-old male, pembrolizumab cycle 3  
**Presentation**: New-onset T1DM with severe DKA (glucose 480 mg/dL, pH 7.15, ketones positive)  
**Date**: [Current date]

---

## CONSENSUS TREATMENT PLAN

### PHASE 1: IMMEDIATE MANAGEMENT (Days 1-7)

#### A. **URGENT HOSPITALIZATION & DKA MANAGEMENT** ✓ *Unanimous agreement*

**Admission Status**: Immediate inpatient admission, likely ICU-level monitoring initially

**DKA Protocol** (per institutional guidelines):
1. **IV Fluid Resuscitation**
   - 0.9% normal saline: 1-1.5 L first hour, then 250-500 mL/hr
   - Transition to 0.45% saline when corrected sodium normalizes

2. **Insulin Therapy**
   - Regular insulin IV infusion: 0.1 units/kg/hr (approximately 7-10 units/hr for 70kg patient)
   - Continue until anion gap closes (<12) AND pH >7.3
   - Transition to subcutaneous insulin when patient tolerates PO intake

3. **Electrolyte Management**
   - Potassium repletion: Target 4-5 mEq/L (typically requires 20-40 mEq/hr)
   - Monitor every 2-4 hours initially
   - Phosphate and magnesium as indicated

4. **Monitoring**
   - Hourly glucose checks initially
   - Venous pH and electrolytes every 2-4 hours
   - Continuous cardiac monitoring
   - Strict intake/output

**Estimated Time to Resolution**: 24-48 hours for DKA resolution; 5-10 days for hospital discharge

#### B. **PEMBROLIZU

[... truncated ...]
```
