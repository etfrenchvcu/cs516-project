"""
metamap_helpers.py
Scope: Helper functions for interacting with metamap
Authors: Evan French
"""
from pymetamap import MetaMap
from classes import Annotation

#Author: Evan French
#MetaMap semantic types corresponding to medical problems
problems = [
    'acab', #Acquired Abnormality
    'cgab', #Congenital Abnormality
    'dsyn', #Disease or Syndrome
    'inpo', #Injury or Poisoning
    'mobd', #Mental or Behavioral Dysfunction
    'neop', #Neoplastic Process
    'patf', #Pathologic Function
    'sosy', #Sign or Symptom
]

#Author: Evan French
#MetaMap semantic types corresponding to medical tests
tests = [
    'diap', #Diagnostic Procedure
    'lbpr', #Laboratory Procedure
    'lbtr', #Laboratory or Test Result
]

#Author: Evan French
#MetaMap semantic types corresponding to medical treatments
treatments = [
    'antb', #Antibiotic
    'clnd', #Clinical Drug
    'topp', #Therapeutic or Preventive Procedure
]

#Author: Evan French
def GetMetamapLabel(semTypeList):
    """
    Returns a predicted label for the list of MetaMap semantic types.
    All semantic types in the input list must be in a single 'master' list (see problems, tests, treatments above) 
    to be assigned a label other than 'none'.

    @param semTypeList: list of sematic type abbreviations
    @return: predicted label (problem, test, treatment, or none)
    """
    #Default label is 'none'
    label = "none"
    
    if set(semTypeList).issubset(problems):
        label = "problem"
    elif set(semTypeList).issubset(tests):
        label = "test"
    elif set(semTypeList).issubset(treatments):
        label = "treatment"
        
    return label

def CheckAnnotationAgainstSemTypes(annotation, semTypes):
    """
    Checks if the label on an annoation matches the predicted label from list of semantic types.

    @param annotation: An Annotation object
    @param semTypes: List of semantic types abbreviations
    @return: True if the labels match and label is not 'none', false otherwise
    """
    mm_label = GetMetamapLabel(semTypes)
    return mm_label != 'none' and annotation.label == mm_label

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
        for semtype in concept.semtypes.strip('[]').split(','):
            if semtype not in anSemTypeList[index]:
                #Create a list of unique semantic types per annotation
                anSemTypeList[index].append(semtype)
    
    return anSemTypeList
