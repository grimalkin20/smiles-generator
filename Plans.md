1. Add a feature that can help the user get multiple results to select from when they enter wrong name, then the user can select the right one instead of giving the error of not found when looking on PubChem instead of the database. And user can look for compounds using, compound name, it's synonyms, its SMILES, or directly PubChem id.
2. In the database, save multiple important properties with different alias names of the same compound, like synonyms and other scientific properties for scientific help and research.
3. Add a feature of making a report file on specific compound with it's whole properties (scientific information) into a form of file, like pdf or docx. for example, if the user is in search compound and searched for compound and received results or user is looking into the database by listing all the compounds in the database. If the user wants the report in pdf or docx form, the user has the access to feature like giving command of generating a pdf or docx of the compound by giving command "generate pdf" or "generate docx", then a secondary window opens and asks the user to select destination to save the pdf or save the pdf in main directory download folder where project has been installed. The name of the file should be of the name of compound.
4. Add the feature of moving back into the "menu" screen by typing "back", instead f opening the menu screen after every search or option selection when needed. for example, when selecting the option for Search Compound, it should stay at the search compound screen until the user input the command "back" it will go one step back in user screen, and when input the command "menu", it will open the menu tab again. These command should run from anywhere in the cli input screen.
5. Keep the cli open for more searched instead of exiting the cli automatically after every search, so one should not concern with running the command of "python src/main.py" again, until they exit by typing "exit/EXIT/eXIT/Exit" or selecting "exit" option from menu.
6. Add a menu section where the user can control what the task or feature one can use,

SMILES Generator — Project Roadmap

Checkpoint 1 — Chemical name to SMILES
Completed
Resolve compound names through PubChem, retrieve identifiers, and validate structures with RDKit.

Checkpoint 2 — Scientific property engine
Core work completed
Calculate molecular descriptors, drug-likeness metrics, and 3D descriptors; retrieve PubChem identifiers, synonyms, and reference properties.

Checkpoint 3 — Experimental property normalization
In progress
Convert published experimental values into structured data without losing units, ranges, temperature conditions, or references.

Future checkpoints to write down
04

Complete experimental properties
Next checkpoint
Features

- Density and relative density
- Boiling point and melting point
- Vapor pressure and flash point
- Solubility in different solvents
- Refractive index and autoignition temperature
- pKa / dissociation constants
  What you’ll learn: How to extract real experimental measurements from scientific sources, preserve units, and distinguish measured values from calculated estimates.
  Completion test: Test each property independently against several compounds and verify that numerical values, ranges, units, conditions, and source references are preserved.

05

Biological activity and molecular targets
Features

- Bioassay results and activity measurements
- Target proteins and biological interactions
- IC50, EC50, Ki, and Kd values where available
- Assay descriptions and experimental context
  What you’ll learn: The difference between binding affinity, potency, and biological activity. These values cannot always be compared directly because assay conditions differ.
  Completion test: Retrieve activity records for selected compounds and retain their units, assay details, targets, and source identifiers.

06

Safety and toxicity information
Features

- Available toxicity and LD50 records
- GHS hazard classifications
- Hazard statements and precautionary statements
- Carcinogenicity information where documented
  What you’ll learn: How to distinguish experimental toxicity results, database classifications, predictions, and missing evidence.
  Completion test: Return traceable safety records with sources and avoid treating missing data as evidence of safety.

07

Drug-likeness and medicinal chemistry filters
Features

- Lipinski Rule of Five and Veber rules
- QED and PAINS screening
- Synthetic accessibility (SA) score
- Ghose, Egan, and Muegge filters
  What you’ll learn: How molecular descriptors support early compound prioritization—and why passing a filter does not establish that a compound is a drug.
  Completion test: Compare results with documented rule thresholds and test known compounds. Keep the SA score implementation separate until its dependency and calculation method are verified.

08

Unified scientific data pipeline
Features

- Combine PubChem data and RDKit calculations
- Organize data into identity, descriptors, experimental, biological, and safety sections
- Mark each value as calculated, database-reported, or experimentally reported
- Handle unavailable or conflicting values consistently
  What you’ll learn: Data models, modular architecture, provenance, and why two sources may report different values for the same compound.
  Completion test: One compound lookup returns a consistent scientific profile without breaking when an optional field is missing.

09

Quality assurance and reliability
Features

- Regression tests for every property normalizer
- Network retry, timeout, and error handling
- PubChem rate limiting and caching
- Validation of units, identifiers, and missing data
  What you’ll learn: Unit testing, integration testing, reproducibility, and how to make a scientific application reliable.
  Completion test: Previously passing tests continue to pass when a new property is added. Known normalization issues are tracked rather than silently forgotten.

10

Database redesign and scientific data storage
Features

- Extend the existing SQLite schema after the data pipeline is stable
- Store chemical identity and aliases separately
- Store descriptors, experimental measurements, and their references in suitable tables
- Prevent duplicate compounds using InChIKey where appropriate
- Support updating records without duplicating data
  What you’ll learn: Relational database design, normalization, foreign keys, and the difference between storing a chemical identity and storing multiple observations about it.
  Completion test: Save, retrieve, update, and search compounds while preserving multiple experimental values and their references.

11

CLI experience and scientific exports
Features

- Search compounds and display a structured scientific report
- View synonyms, descriptors, experimental data, and warnings
- Export results to CSV and Excel
- Generate SDF files and 3D conformers when appropriate
- Clearly identify data source and calculation method
  What you’ll learn: CLI design, data serialization, reporting, and scientific file formats.
  Completion test: A user can search for a compound and export a readable, reproducible report.

12

Structure-to-SMILES recognition
Features

- Recognize molecular structures from uploaded images
- Start with clean 2D skeletal chemical diagrams
- Convert recognized atoms and bonds into a molecular graph
- Validate and generate SMILES with RDKit
- Later explore 3D structure images and more difficult diagrams
  What you’ll learn: Optical chemical structure recognition (OCSR), image processing, graph reconstruction, and molecular validation.
  Completion test: Evaluate against a labeled set of structure images and compare the generated canonical SMILES with known reference structures.
  This is a substantially larger machine-learning/computer-vision feature. Treat it as a separate project phase, not a small addition to the name resolver.

13

Release and documentation
Features

- Clean project structure and dependency list
- Installation and usage instructions
- Example compound reports and tests
- Version control, README, and limitations
- Reproducible setup for another computer
  What you’ll learn: Software packaging, documentation, and preparing a research-oriented tool for other users.
  Completion test: Another person can install the project, run its tests, resolve a compound, and generate a scientific report using the documentation.

The workflow we’ll follow at every checkpoint
Use this as your development rule:

1. Understand: I explain the feature, scientific concepts, data source, and limitations before coding.
2. Plan: We identify the exact files to create or modify and define expected outputs.
3. Implement: We make a focused change rather than rewriting working modules unnecessarily.
4. Test: You run the test and share the output. We fix failures before proceeding.
5. Checkpoint: We record what works, known issues, and the Git commit message.
   What to note on your paper
   Your immediate sequence is:

- [X] Checkpoint 3: Finish experimental property normalization, beginning with Density.
- [X] Checkpoint 4: Finish the remaining experimental properties.
- [X] Checkpoint 5: Add biological activity and molecular target data.
- [ ] Checkpoint 6: Add safety and toxicity data.
- [ ] Checkpoint 7: Complete drug-likeness filters.
- [ ] Checkpoint 8: Integrate all scientific data into one pipeline.
- [ ] Checkpoint 9: Run regression tests, improve reliability, and track known issues.
- [ ] Checkpoint 10: Redesign SQLite only after the scientific fields and data structure are stable.
- [ ] Checkpoint 11: Build scientific reports and exports.
- [ ] Checkpoint 12: Develop structure-image-to-SMILES recognition.
- [ ] Checkpoint 13: Document, package, and release the project.
  Our next task is Density normalization. We will keep the working Solubility V3.1 checkpoint intact, test Density independently, and avoid changing database code until the scientific pipeline is verified. This keeps us moving toward completion without destabilizing the features that already work.
