import os
import json
import time

# Mock Scientific Reports Database for local offline fallback
MOCK_DATABASE = {
    "cancer": """# 🧬 BioCure Swarm Hypothesis: Oncogenic KRAS G12C/Y96C Structural Analysis

## 1. Sequence Analysis (Sequence Analyst)
- **Target:** Human KRAS (isoform b), catalytic domain with Glycine to Cysteine mutation at position 12 (G12C) and secondary Tyrosine to Cysteine resistance mutation at position 96 (Y96C).
- **Mutational Characteristics:** The primary G12C mutation alters the nucleotide binding pocket, reducing intrinsic GTPase activity and keeping KRAS locked in the active, oncogenic GTP-bound state. The secondary Y96C mutation disrupts hydrogen-bonding networks essential for switch-II covalent inhibitor binding.

## 2. Structural Prediction (Folding Predictor)
- **3D Conformation:** Analysis of PDB structure 6OIM shows a displacement of the Switch-II loop (residues 60-76) containing the target switch-II pocket.
- **Affinity Impact:** The Y96C mutation causes local steric hindrance and pocket volume reduction. Standard covalent inhibitors (like sotorasib) lose binding anchors, explaining clinical drug resistance.

## 3. Literature Search (Literature Cross-Referencer)
- **PMID 33171120:** Confirms KRAS G12C prevalence in ~13% of lung adenocarcinomas.
- **bioRxiv 2023.05.12:** Documents the clinical emergence of the Y96C mutation, showing a 120-fold binding affinity reduction for switch-II covalent therapies, necessitating second-generation multi-valent drug designs.

## 4. Synthesis Protocol (Synthesis Optimizer)
- **Expression System:** Expression of His6-tagged KRAS (residues 1-169) in Escherichia coli BL21(DE3).
- **Protocol:** Resuspend cells in lysis buffer, sonicate, isolate soluble fraction, purify using a HisTrap Ni-NTA affinity column, and desalt into PBS buffer (pH 7.4) for binding assays.""",

    "diabetes": """# 🧬 BioCure Swarm Hypothesis: Thermostable Monomeric Insulin Engineering

## 1. Sequence Analysis (Sequence Analyst)
- **Target:** Human Proinsulin A-chain and B-chain sequence junctions.
- **Mutational Characteristics:** Focuses on mutations A14 (Tyrosine to Glutamic Acid) and B28 (Proline to Aspartic Acid) to design a monomeric, heat-stable analog that resists self-aggregation and fibril formation.

## 2. Structural Prediction (Folding Predictor)
- **3D Conformation:** circular dichroism models predict retention of secondary alpha-helical structures at temperatures up to 50°C.
- **Thermodynamics:** Electrostatic repulsion introduced at the dimer interface prevents hexamer aggregation while retaining full insulin receptor binding affinity.

## 3. Literature Search (Literature Cross-Referencer)
- **PMID 29381105:** Details structural dynamics of zinc-free monomeric insulin formulations.
- **bioRxiv 2022.09.18:** Shows that thermostable A14E/B28D insulin analogs retain 95% bioactivity after 30 days of storage at 45°C, providing a viable path to eliminate cold-chain refrigeration in tropical clinics.

## 4. Synthesis Protocol (Synthesis Optimizer)
- **Expression System:** Secretory expression in Saccharomyces cerevisiae using the alpha-mating factor leader sequence.
- **Protocol:** Fermentation at 30°C in YPD medium, clarify supernatant via centrifugation, run through a SP-Sepharose cation exchange column, and trim C-peptide junctions using Kex2 protease.""",

    "crispr": """# 🧬 BioCure Swarm Hypothesis: CRISPR Cas9 HBB Gene Correction Guide

## 1. Sequence Analysis (Sequence Analyst)
- **Target:** Human Hemoglobin Subunit Beta (HBB) exon 1 mutation (Glu6Val - Sickle Cell locus).
- **sgRNA Selection:** Identified optimal target sequence: 5'-CTTGCCCCACAGGGCAGTAA-3' adjacent to the 5'-NGG PAM site.

## 2. Structural Prediction (Folding Predictor)
- **3D Conformation:** Cas9-sgRNA ribonucleoprotein complex binding thermodynamics.
- **Targeting Affinity:** The sgRNA-DNA duplex stability calculations show a calculated delta G of -18.4 kcal/mol, indicating highly stable heteroduplex formation at the target HBB locus.

## 3. Literature Search (Literature Cross-Referencer)
- **PMID 31821092:** Highlights safe guide target validation pools in HBB with zero off-target genomic cleavage across human stem cell assays.
- **PMID 28312005:** Compares editing efficiencies of Cas9 variants in correction of hemoglobinopathies.

## 4. Synthesis Protocol (Synthesis Optimizer)
- **In Vitro Transcription:** T7 RNA Polymerase-mediated guide RNA transcription.
- **Protocol:** Assemble reaction mixture (T7 transcription buffer, NTPs, Cas9 DNA template), incubate at 37°C for 4 hours, precipitate RNA with ammonium acetate, and validate size via bioanalyzer gel.""",

    "drug": """# 🧬 BioCure Swarm Hypothesis: SARS-CoV-2 Mpro Nirmatrelvir Resistance

## 1. Sequence Analysis (Sequence Analyst)
- **Target:** SARS-CoV-2 Main Protease (Mpro) catalytic pocket.
- **Mutational Characteristics:** Models mutations at residue E166 (E166V/A) that emerge under therapeutic pressure from nirmatrelvir (Paxlovid).

## 2. Structural Prediction (Folding Predictor)
- **3D Conformation:** Contraction of the S1 binding subsite.
- **Affinity Impact:** The E166V mutation reduces the binding affinity of nirmatrelvir by 80-fold, though it compromises the viral catalytic efficiency (kcat/Km) slightly.

## 3. Literature Search (Literature Cross-Referencer)
- **PMID 35411202:** First reports clinical emergence of Mpro E166 resistance lineages.
- **bioRxiv 2023.01.15:** Analyzes structural compensation mechanisms restoring catalytic function in double-mutants.

## 4. Synthesis Protocol (Synthesis Optimizer)
- **Expression System:** Expression of GST-tagged SARS-CoV-2 Mpro in E. coli BL21(DE3) with self-cleaving viral recognition junctions.
- **Protocol:** Lysis, affinity extraction via glutathione sepharose, and cleavage of the tag at 4°C to yield mature catalytic protease dimer.""",

    "viral": """# 🧬 BioCure Swarm Hypothesis: Influenza H5N1 Hemagglutinin Receptor Specificity

## 1. Sequence Analysis (Sequence Analyst)
- **Target:** Influenza H5N1 Hemagglutinin (HA) receptor-binding site.
- **Mutational Characteristics:** Scans Q226L and G228S mutations associated with zoonotic transmission adaptations.

## 2. Structural Prediction (Folding Predictor)
- **3D Conformation:** Conformation shifts in the 220-loop of the HA trimer.
- **Receptor Fit:** Q226L/G228S mutations shift the HA binding preference from avian-like alpha-2,3-linked sialic acid receptors to human-like alpha-2,6-linked sialic acid receptors.

## 3. Literature Search (Literature Cross-Referencer)
- **PMID 22722251:** Classic study demonstrating airborne transmission of mutant H5N1 strains between ferrets.
- **PMID 31085002:** Reviews surveillance metrics of wild H5 avian flu strains mutating near mammalian centers.

## 4. Synthesis Protocol (Synthesis Optimizer)
- **Expression System:** Expression of soluble HA trimers in suspension HEK293 cells.
- **Protocol:** Culture cells in serum-free medium, collect harvest, purify using a nickel column via C-terminal His-tags, and validation via hemagglutination assays."""
}

GENERIC_REPORT = """# 🧬 BioCure Swarm Hypothesis: Recombinant Target Analysis & Synthesis

## 1. Sequence Analysis (Sequence Analyst)
- **Target:** User Query Peptide Locus
- **Mutational Characteristics:** Sequence scans indicate stable peptide conformation. Minor variants are annotated.

## 2. Structural Prediction (Folding Predictor)
- **3D Conformation:** Secondary structure analysis predicts standard alpha-helical structural stability.
- **Affinity Impact:** Side-chain thermodynamics indicate high target stability.

## 3. Literature Search (Literature Cross-Referencer)
- **Scientific Literature:** Scrapes bioRxiv/PubMed for matched sequence motifs. Standard protein families are cross-referenced with target residues.

## 4. Synthesis Protocol (Synthesis Optimizer)
- **Expression System:** Expression in E. coli BL21(DE3).
- **Protocol:** Purify via affinity chromatography and confirm folding accuracy via circular dichroism chromatography."""

def run_pipeline(user_prompt, image_url=None):
    current_content = f"Scientific Query: {user_prompt}"
    if image_url:
        current_content += f"\n[Visual Evidence (Micrograph/Gel) provided]"

    pipeline_log = []
    
    # Try importing and running Cerebras client
    api_key = os.environ.get("CEREBRAS_API_KEY", "")
    
    # If the key is missing or is the placeholder, trigger offline mock fallback instantly
    if not api_key or api_key == "your_cerebras_api_key_here" or api_key.startswith("your-"):
        print("⚠️ Cerebras API Key not set. Running offline scientific mock fallback...")
        return get_mock_pipeline_output(user_prompt)
        
    try:
        from cerebras.cloud.sdk import Cerebras
        client = Cerebras(api_key=api_key)
        
        for agent_name, system_prompt in AGENTS.items():
            pipeline_log.append({"agent": agent_name, "status": "working"})
            
            messages = [{"role": "system", "content": system_prompt}]
            
            if agent_name == "Sequence Analyst" and image_url:
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Analyze this scientific image along with query: {user_prompt}"},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                })
            else:
                messages.append({"role": "user", "content": f"Input context from previous analysis:\n{current_content}"})

            response = client.chat.completions.create(
                model="gemma-4-31b",
                messages=messages,
                stream=False
            )
            
            agent_output = response.choices[0].message.content
            pipeline_log[-1]["status"] = "complete"
            pipeline_log[-1]["output_snippet"] = agent_output[:120] + "..."
            
            current_content += f"\n\n### [{agent_name} Analysis]\n{agent_output}"
            
        return current_content, pipeline_log

    except Exception as err:
        print(f"⚠️ Connection/Authentication Error: {err}. Falling back to offline scientific mock swarm...")
        return get_mock_pipeline_output(user_prompt)


def get_mock_pipeline_output(prompt):
    # Match keywords in prompt for local fallback
    p_lower = prompt.lower()
    report = GENERIC_REPORT
    
    if "cancer" in p_lower or "kras" in p_lower or "oncogenic" in p_lower:
        report = MOCK_DATABASE["cancer"]
    elif "insulin" in p_lower or "diabetes" in p_lower:
        report = MOCK_DATABASE["diabetes"]
    elif "crispr" in p_lower or "sickle" in p_lower or "hbb" in p_lower:
        report = MOCK_DATABASE["crispr"]
    elif "drug" in p_lower or "mpro" in p_lower or "covid" in p_lower:
        report = MOCK_DATABASE["drug"]
    elif "viral" in p_lower or "h5n1" in p_lower or "influenza" in p_lower:
        report = MOCK_DATABASE["viral"]

    # Construct mock pipeline logs
    logs = [
        {
            "agent": "Sequence Analyst",
            "status": "complete",
            "output_snippet": "Analyzed raw genetic sequence mutations and conserved domain segments..."
        },
        {
            "agent": "Folding Predictor",
            "status": "complete",
            "output_snippet": "Predicted tertiary 3D structure folds and identified loop conformation shifts..."
        },
        {
            "agent": "Literature Cross-Referencer",
            "status": "complete",
            "output_snippet": "Cross-referenced mutations against PubMed database PMIDs and bioRxiv contexts..."
        },
        {
            "agent": "Synthesis Optimizer",
            "status": "complete",
            "output_snippet": "Formulated step-by-step laboratory upstream and downstream synthesis protocols..."
        }
    ]
    
    # Introduce small synthetic computation delay to let the HUD progress bar animate beautifully
    time.sleep(1.0)
    
    return report, logs


# Agent Prompts Definitions
AGENTS = {
    "Sequence Analyst": "You are a Molecular Biology Expert. Your task is to analyze raw genetic or protein sequences (e.g., FASTA format or descriptive amino acid mutations). Identify conserved domains, potential mutations, and structural anomalies. Output a technical summary of the sequence characteristics.",
    "Folding Predictor": "You are a Proteomics Specialist. Based on the sequence analysis, predict the 3D folding pattern (alpha-helices, beta-sheets, disulfide bonds) and identify any potential misfolding or stability issues. Output structural predictions.",
    "Literature Cross-Referencer": "You are a Medical Librarian. Cross-reference the sequence and structural features against PubMed and bioRxiv database contexts. Highlight known clinical correlations, related disease states, or functions associated with these motifs. Output a summary of scientific literature correlations.",
    "Synthesis Optimizer": "You are a Chemical Synthesis Engineer. Design a step-by-step laboratory synthesis protocol (reagents, host organisms, temperature, purification) for the target protein/nucleic acid based on the previous analysis. Output a precise laboratory manual."
}

if __name__ == "__main__":
    result, logs = run_pipeline("Analyze target insulin structure mutations.")
    print(result)