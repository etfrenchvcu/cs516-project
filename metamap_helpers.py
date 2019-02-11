"""
metamap_helpers.py
Scope: Helper functions for interacting with metamap
Authors: Evan French
"""
from pymetamap import MetaMap, ConceptMMI
from classes import Annotation

#Author: Evan French
#MetaMap semantic types corresponding to medical tests
tests = [
'amas', #Amino Acid Sequence
'mbrt', #Molecular Biology Research Technique
'edac', #Educational Activity
'irda', #Indicator, Reagent, or Diagnostic Aid
'ffas', #Fully Formed Anatomical Structure
'ocdi', #Occupation or Discipline
'elii', #Element, Ion, or Isotope
'enty', #Entity
'comd', #Cell or Molecular Dysfunction
'vita', #Vitamin
'nnon', #Nucleic Acid, Nucleoside, or Nucleotide
'lbpr', #Laboratory Procedure
]

#Author: Evan French
#MetaMap semantic types corresponding to medical treatments
treatments = [
'clnd', #Clinical Drug
'drdd', #Drug Delivery Device
'orgt', #Organization
'bodm', #Biomedical or Dental Material
'mcha', #Machine Activity
'food', #Food
'hcpp', #Human-caused Phenomenon or Process
'tisu', #Tissue
'topp', #Therapeutic or Preventive Procedure
'genf', #Genetic Function
'antb', #Antibiotic
'medd', #Medical Device
'acty', #Activity
'bdsu', #Body Substance
'bsoj', #Body Space or Junction
'bpoc', #Body Part, Organ, or Organ Component
'popg', #Population Group
'orgf', #Organism Function
'plnt', #Plant
'biof', #Biologic Function
'mamm', #Mammal
'blor', #Body Location or Region
'spco', #Spatial Concept
'anst', #Anatomical Structure
'gora', #Governmental or Regulatory Activity
'hlca', #Health Care Activity
]

#Author: Evan French
#MetaMap semantic types corresponding to medical problems
problems = [
'grpa', #Group Attribute
'amph', #Amphibian
'mobd', #Mental or Behavioral Dysfunction
'bhvr', #Behavior
'aggp', #Age Group
'inpo', #Injury or Poisoning
'lang', #Language
'dsyn', #Disease or Syndrome
]

#Author: Evan French
def GetMetamapLabel(semTypeList, testList = None, treatmentList = None, problemList = None):
    """
    Returns a predicted label for the list of MetaMap semantic types.
    All semantic types in the input list must be in a single 'master' list (see problems, tests, treatments above) 
    to be assigned a label other than 'none'.

    @param semTypeList: list of sematic type abbreviations
    @return: predicted label (problem, test, treatment, or none)
    """
    # Use parameters if provided, otherwise default to hardcodes
    testList = testList if testList != None else tests
    treatmentList = treatmentList if treatmentList != None else treatments
    problemList = problemList if problemList != None else problems

    #Default label is 'none'
    label = "none"
    
    semTypeSet = set(semTypeList)

    if not semTypeSet.isdisjoint(problemList) and semTypeSet.isdisjoint(testList) and semTypeSet.isdisjoint(treatmentList):
        label = "problem"
    elif semTypeSet.isdisjoint(problemList) and not semTypeSet.isdisjoint(testList) and semTypeSet.isdisjoint(treatmentList):
        label = "test"
    elif semTypeSet.isdisjoint(problemList) and semTypeSet.isdisjoint(testList) and not semTypeSet.isdisjoint(treatmentList):
        label = "treatment"
        
    return label

def CheckAnnotationAgainstSemTypes(annotation, semTypes, testList = None, treatmentList = None, problemList = None):
    """
    Checks if the label on an annoation matches the predicted label from list of semantic types.

    @param annotation: An Annotation object
    @param semTypes: List of semantic types abbreviations
    @return: True if the labels match and label is not 'none', false otherwise
    """
    mm_label = GetMetamapLabel(semTypes, testList, treatmentList, problemList)
    isSilver = mm_label != 'none' and annotation.label == mm_label
    return isSilver, mm_label

#Author: Evan French
def GetMetaMapSemanticTypes(metamap_path, annotations):
    """
    Uses MetaMap to return a list of sematic types for each annotation

    @param metamap_path: Path to MetaMap installation
    @param annotations: List of concepts parsed from annotation file
    @return: List of lists of sematic types for each annotation
    """
    #Extract concepts from the list of annotations using MetaMap
    metamap = MetaMap.get_instance(metamap_path)
    indexes = range(len(annotations))
    concepts, error = metamap.extract_concepts(annotations, indexes)

    #List to hold a list of semantic types for each annotation
    anSemTypeList = [[] for x in range(len(annotations))]

    #Iterate over the list of concepts extracted from the list of annotations
    for concept in concepts:
        index = int(concept.index)
        if isinstance(concept, ConceptMMI):
            for semtype in concept.semtypes.strip('[]').split(','):
                if semtype not in anSemTypeList[index]:
                    #Create a list of unique semantic types per annotation
                    anSemTypeList[index].append(semtype)
        
    return anSemTypeList
