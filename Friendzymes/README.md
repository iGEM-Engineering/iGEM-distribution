# Package: Friendzymes Collection

This collection is aimed at expanding what people are able to do with FreeGenes collections and the iGEM distribution, both in terms of genetic assembly and in terms of biomanufacturing. Friendzymes' primary goals are to democratize strain engineering and recombinant protein manufacturing and purification. For manufacturing, this collection contains an expansion of the FreeGenes Open Yeast Collection, including target P. pastoris-optimized target enzymes for recombinant production (such as Eco31I, an IP-free BsaI isoschizomer and its cognate methyltransferases), additional purification tags, an anti-His tag antibody for protein blotting and quantification, and additional yeast promoters. Further, this collection contains complements to the FreeGenes Bacillus subtilis Secretion Tag Library Plasmids, for recombinant protein production and secretion from B. subtilis. These include B. subtilis  promoters, target proteins for production like Pfu-Sso7d polymerase, and various B. subtilis regulatory elements. For strain engineering, we include E. coli origins or replication, E. coli, B. subtilis and P. pastoris selection markers, counterselection markers for E. coli, an origin of transfer for conjugation from E. coli to other bacterial species, homology arm pairs for genomic integration into B. subtilis and P. pastoris, and 5' and 3' recombinase site parts for insertion, deletion or inversion of synthetic genetic elements. Many of these parts are not elements of a canonical transcription unit, and do not have clearly defined part types in the MoClo/uLoop assembly standard; moreover, for some parts, their insertion into the transcription unit would require changing the overhangs on the core promoter, RBS, CDS, and/or terminator parts. To address this challenge, we designed a high-fidelity, backwards-compatible expansion of the MoClo assembly standard, AllClo (https://docs.google.com/spreadsheets/d/1TICnbGYY96myM7TPXWwBsLvyadgSfmtbVTGsUN5iMI8/edit?usp=sharing), all with a single 26-overhang set that includes all uLoop overhangs and the vector assembly overhangs used in the Open Yeast Collection, and whose predicted ligation fidelity in a 26-part assembly is 96%. We further designed a set of part switching linkers, that take as input canonical uLoop transcription unit components and output those parts with new 5' and 3' overhangs. These part switching reactions enable, for instance, insertion of recombination sites 5' to the promoter and/or 3' to the terminator in a TU, or ribozymes 3' to the promoter and 5' to the RBS/start site. In this way, standard uLoop parts can participate in assembly reactions that construct modular vector backbones, composite 5' and 3' UTRs, and multi-tagged CDSs. The part switching linkers were designed to proceed in two methods: with an orthogonal, linker-specific Type IIS restriction site (BbsI), or with a conditionally methylatable, idempotent BsaI restriction site (mBsaI), that is suppressed when the linker is cloned inside an E. coli cell expressing HpaII and/or MspI, and becomes active when the part is cloned into an MspI-/HpaII- strain or PCR amplified to remove the methylation sites. These parts and this expanded assembly standard have the potential to enable iGEM teams with tools and a framework to manufacture their own enzymatic reagents and perform their own sophisticated modification of strains' genomic background.

### Summary:

- 74 parts
    - CDS: 12
    - assembly_component: 22
    - homologous_region: 10
    - inducible_promoter: 4
    - oriT: 1
    - origin_of_replication: 3
    - polypeptide_fusion: 2
    - polypeptide_motif: 1
    - recombination_signal_sequence: 5
    - ribozyme: 1
    - selection_marker: 7
    - signal_peptide: 2
    - terminator: 4
- 0 vectors
- 72 samples for distribution _<span style="color:red">2 parts not included</span>_

### Parts:

- Bsub_LacI_LacO_Promo (inducible_promoter) in 
- CatA9__LEFT_PARENTHESISBsub_CamR_RIGHT_PARENTHESIS (selection_marker) in 
- Eco31IA_methyltransferase (CDS) in 
- Eco31IB_methyltransferase (CDS) in 
- Eco31I_restriction_enzyme (CDS) in 
- EcoOri_ColE1pMB1pBR32 (origin_of_replication) in 
- Eco_AmpR (selection_marker) in 
- Eco_KanR (selection_marker) in 
- Eco_TetR (selection_marker) in 
- Eco_ccdA (CDS) in 
- Eco_p15a_origin (origin_of_replication) in 
- Eco_pRO1600_ColE1_origin (origin_of_replication) in 
- Eco_sacB (CDS) in 
- Ecoli_KanR (selection_marker) in 
- Ecoli_SpecR (selection_marker) in 
- IDL3_B_BbsI_3_APOSTROPHE_Identity_Linker (assembly_component) in 
- IDL3_B_mBsaI_3_APOSTROPHE_Identity_Linker (assembly_component) in 
- IDL3_C_BbsI_3_APOSTROPHE_Identity_Linker (assembly_component) in 
- IDL3_C_mBsaI_3_APOSTROPHE_Identity_Linker (assembly_component) in 
- IDL5_A_BbsI_5_APOSTROPHE_Identity_Linker (assembly_component) in 
- IDL5_A_mBsaI_5_APOSTROPHE_Identity_Linker (assembly_component) in 
- IDL5_E_BbsI_5_APOSTROPHE_Identity_Linker (assembly_component) in 
- IDL5_E_mBsaI_5_APOSTROPHE_Identity_Linker (assembly_component) in 
- Lambda_T1_Transcriptional_Terminator (terminator) in 
- Lox71_select_Lox66 (recombination_signal_sequence) in 
- PSL3_B_to_A3_BbsI_3_APOSTROPHE_Part_Switch_Linker (assembly_component) in 
- PSL3_B_to_A3_mBsaI_3_APOSTROPHE_Part_Switch_Linker (assembly_component) in 
- PSL3_F9_to_E2_BbsI_3_APOSTROPHE_Part_Switch_Linker (assembly_component) in 
- PSL3_F9_to_E2_mBsaI_3_APOSTROPHE_Part_Switch_Linker (assembly_component) in 
- PSL3_F9_to_F_BbsI_3_APOSTROPHE_Part_Switch_Linker (assembly_component) in 
- PSL3_F9_to_F_mBsaI_3_APOSTROPHE_Part_Switch_Linker (assembly_component) in 
- PSL3_F_to_E2_BbsI_3_APOSTROPHE_Part_Switch_Linker (assembly_component) in 
- PSL3_F_to_E2_mBsaI_3_APOSTROPHE_Part_Switch_Linker (assembly_component) in 
- PSL5_A_to_A2_BbsI_5_APOSTROPHE_Part_Switch_Linker (assembly_component) in 
- PSL5_A_to_A2_mBsaI_5_APOSTROPHE_Part_Switch_Linker (assembly_component) in 
- PSL5_F8_to_A2_BbsI_5_APOSTROPHE_Part_Switch_Linker (assembly_component) in 
- PSL5_F8_to_A2_mBsaI_Part_Switch_Linker (assembly_component) in 
- PSL5_F8_to_A_BbsI_5_APOSTROPHE_Part_Switch_Linker (assembly_component) in 
- PSL5_F8_to_A_mBsaI_Part_Switch_Linker (assembly_component) in 
- Pfu_Sso7d_noCtag_Bsub (CDS) in 
- Pfu_ssod7_yeast (CDS) in 
- Pichia_VPS13_3_APOSTROPHE_Homology (homologous_region) in 
- Pichia_VPS13_5_APOSTROPHE_Homology (homologous_region) in 
- Pichia_VPS8_3_APOSTROPHE_Homology (homologous_region) in 
- Pichia_VPS8_5_APOSTROPHE_Homology (homologous_region) in 
- PurTag_R5 (polypeptide_motif) in 
- Rec3_Lox66 (recombination_signal_sequence) in 
- Rec3_LoxP (recombination_signal_sequence) in 
- Rec5_Lox71 (recombination_signal_sequence) _<span style="color:red">not included in distribution</span>_
- Rec5_LoxP (recombination_signal_sequence) _<span style="color:red">not included in distribution</span>_
- SarJ_Ribozyme_Insulator (ribozyme) in 
- SecTag_ReplacementSpacer_AATG (signal_peptide) in 
- SecTag_ReplacementSpacer_CCAT (signal_peptide) in 
- T4_DNA_Ligase_yeast (CDS) in 
- T7TE_LuxIA_Terminator (terminator) in 
- TU_ccdB_dropout (selection_marker) in 
- Terminator_for_Bacillus_subtilis (terminator) in 
- _6xHis_CenA_TEVcut_yeast (polypeptide_fusion) in 
- _6xHis_Cex_TEVcut_yeast (polypeptide_fusion) in 
- anti_his_tag_single_chain_antibody_yeast (CDS) in 
- fuGFP_yeast (CDS) in 
- openCherry_yeast (CDS) in 
- p50_T4_DNA_Ligase_yeast (CDS) in 
- pBs1C__LEFT_PARENTHESISamyE_RIGHT_PARENTHESIS__LEFT_SQUARE_BRACKET1412_2440_RIGHT_SQUARE_BRACKET_3_APOSTROPHE_homology (homologous_region) in 
- pBs1C__LEFT_PARENTHESISamyE_RIGHT_PARENTHESIS__LEFT_SQUARE_BRACKET5579_6099_RIGHT_SQUARE_BRACKET_5_APOSTROPHE_homology (homologous_region) in 
- pBs2E__LEFT_PARENTHESISlacA_RIGHT_PARENTHESIS__LEFT_SQUARE_BRACKET150_557_RIGHT_SQUARE_BRACKET_3_APOSTROPHE_homology (homologous_region) in 
- pBs2E__LEFT_PARENTHESISlacA_RIGHT_PARENTHESIS__LEFT_SQUARE_BRACKET4104_4619_RIGHT_SQUARE_BRACKET_5_APOSTROPHE_homology (homologous_region) in 
- pBs4S__LEFT_PARENTHESISthRC_RIGHT_PARENTHESIS__LEFT_SQUARE_BRACKET1059_1487_RIGHT_SQUARE_BRACKET_3_APOSTROPHE_homology (homologous_region) in 
- pBs4S__LEFT_PARENTHESISthRC_RIGHT_PARENTHESIS__LEFT_SQUARE_BRACKET4064_4573_RIGHT_SQUARE_BRACKET_5_APOSTROPHE_homology (homologous_region) in 
- pDAS_Pichia_promoter (inducible_promoter) in 
- pFLD1_Pichia_promoter (inducible_promoter) in 
- pGAL1_S__cerevisiae_inducible_promoter (inducible_promoter) in 
- pIP501_Transfer_Origin (oriT) in 
- rrnBT1_T7TE_Terminator (terminator) in 

_Note: automatically generated from package Excel and sequence files; do not edit_
