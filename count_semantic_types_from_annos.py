import sys, getopt, os, re
import metamap_helpers
from classes import Annotation
import csv

def main():
    """
    Main function of the application. Call -h or --help for command line inputs.
    """
    metamap_path, ann_path, output_dir = None, None, None
    
    metamap_path = '/home/evan/metamap/public_mm/bin/metamap16'
    #ann_path = '../test_data'
    ann_path = '/home/evan/code/data/reference_standard_for_test_data/concepts'
    output_dir = '/home/evan/code/test_data/out'

    #Process the annotations
    ProcessAnnotations(metamap_path, ann_path, output_dir)

#Author: Evan French
def ProcessAnnotations(metamap_path, ann_path, output_dir):
    """
    Uses MetaMap to corroborate annotations. Annotations where the label on the annotation
    and the label predicted by MetaMap are in agreement are saved to a file with the same name
    in the directory specified by gold_ann_path

    @param metamap_path: Path to MetaMap installation
    @param ann_path: Path to annotation directory
    @param gold_ann_path: Path path for newly identified gold standard annotations
    @param save_failed: Save failed annotations to their own separate file for reference, defaults to false
    """

    cwd = os.getcwd()
    os.chdir(ann_path)

    semtypes = {}
    
    #Create output directory for newly identified gold standard annotations if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    #Iterate over documents in the ann_path directory
    for document in [f for f in os.listdir() if os.path.isfile(f)]:

        #Strip the extension from the file to get the document name
        docName = os.path.splitext(document)[0]
                    
        #Instantiate a list to hold Annotations for each document
        annotationList = []
        
        #Create an Annotation object for each line in the document and append the concepts to a list
        doc = open(document, "r")  
        for line in doc.readlines():
            an = Annotation(line)
            annotationList.append(an)
        doc.close()
            
        #Run pymetamap over annotations and return semantic types
        annotated_concepts = [a.concept for a in annotationList]
        mmSemTypes = metamap_helpers.GetMetaMapSemanticTypes(metamap_path, annotated_concepts)
            
        #Check MetaMap prediction vs annotation label
        for ix, annotation in enumerate(annotationList):
            for semtype in mmSemTypes[ix]:
                if semtype not in semtypes:
                    semtypes[semtype] = {key: 0 for key in ['test', 'treatment', 'problem']}
                semtypes[semtype][annotation.label] = semtypes[semtype][annotation.label] + 1
    
    #Write output to a new file
    new_gold_file = os.path.join(output_dir, "output.txt")
    print(new_gold_file)
    with open(new_gold_file, 'w+') as f:
        f.write('semantictype\ttest\ttreatment\tproblem\n')
        for key, value in semtypes.items():
            f.write('%s\t%d\t%d\t%d\n' % (key, value['test'], value['treatment'], value['problem']))

            
    #Return to the original directory
    os.chdir(cwd)

if __name__ == "__main__":
	main()
