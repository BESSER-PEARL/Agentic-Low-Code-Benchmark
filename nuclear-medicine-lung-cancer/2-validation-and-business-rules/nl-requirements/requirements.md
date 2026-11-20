# Natural-Language Requirements

## A system for managing PET/CT explorations of lung cancer patients
### Patients
The system keeps a record of every patient who undergoes a PET/CT examination. For each patient it stores the regional health card number (SIP), the clinical history number (NHC), the national identity document number (DNI), the full name, the date of birth and the sex.
Three rules govern the patient's details. A DNI must consist of exactly eight digits followed by a single uppercase letter, with nothing else in it. The sex must be recorded either as M or as F. The date of birth must be earlier than the current date.
A patient may have one record of clinical antecedents, or none. That record states, as a set of yes/no answers, whether the patient has diabetes, is immunosuppressed, has HIV, suffers from heart failure, is a smoker, and has had another tumor. A clinical-antecedent record always belongs to exactly one patient.
### Explorations
An exploration is a PET/CT study performed on a patient. Every exploration belongs to exactly one patient, and a patient may have any number of explorations, or none at all.
For each exploration the system records the date it was performed, the radiopharmaceutical used, the acquisition protocol, the late field acquired and the time at which it was acquired, the administered activity, the patient's blood glucose level, the mediastinal quantification value and the method used to obtain that quantification.
Two values of an exploration are not typed in but worked out automatically. The patient's age is the number of full years between the patient's date of birth and the date of the exploration. The number of findings is the count of findings revealed by the exploration, and is zero for a new exploration. An exploration offers two actions, each of which returns the calculated value: one computes the patient's age at the time of the exploration, and the other counts the findings it revealed.
Two rules govern the measured values of an exploration. The blood glucose level must be greater than zero and lower than 200. The mediastinal quantification value can never be negative.
### Indications and pathologies
An exploration may have one indication, or none, describing why the study was requested. An indication always belongs to exactly one exploration. It records the suspected diagnosis as free text, and states, as yes/no answers, whether the study is requested for staging, for restaging, for radiotherapy planning and for rating the response to a treatment.
To keep the patient's diagnostic history connected, an exploration may also refer to any number of previous indications. A given indication can be referred to as a previous indication by at most one exploration.
The system also records pathologies. Each pathology stores a diagnosis as free text and whether it is only a suspicion. A pathology relates to at least one exploration and may relate to several, and an exploration may be related to any number of pathologies, or none.
### Findings
An exploration may reveal any number of findings, or none. Each finding belongs to exactly one exploration. For every finding the system stores its location, its measurements in the axial, sagittal and coronal planes, its metabolic activity, its density and its categorization.
Three specialised kinds of findings exist, and all of them reuse exactly the same details as a general finding: tumors, lymph nodes and metastases.
A tumor additionally records its type, its morphology, its internal characteristics, its borders and a diagnosis. The type of a tumor can only be one of the following: nodule, mass, infiltrate, effusion, atelectasis, ground-glass opacity or pneumonic-growth tumor.
A tumor may be related to any number of neighboring structures, or none. Each neighboring-structure record belongs to exactly one tumor and stores the name of the structure and how the tumor relates to it.
A lymph node additionally records its appearance. A lymph node may be associated with one tumor, or with none, and a tumor may be associated with any number of lymph nodes.
### Staging, report and result files
From an exploration the system may calculate one staging, or none. A staging always belongs to exactly one exploration and records the date it was established and its result. A staging can never be dated before the exploration it belongs to.
An exploration may generate one report, or none. A report always belongs to exactly one exploration. It stores the draft text written by the physician, the conclusion, the date on which it was finished and the physician's signature. The date on which a report was finished can never be before the date of its exploration.
Every report also has a status, which is not set by hand. It can only be one of two things: draft or signed, and every new report starts as a draft. A report offers a single action: signing it, which reports back whether it succeeded. Signing is refused if the report is already signed, or if it has no conclusion or no signature; otherwise the report becomes signed and the date on which it was finished is set to the current date.
An exploration may also produce any number of result files, or none. Each result file belongs to exactly one exploration and stores its content and a signature.
