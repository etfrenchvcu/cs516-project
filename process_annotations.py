"""
process_annotations.py
Scope: Process an existing annotation file by comparing the annotated labels with predicted labels using MetaMap.
    Annotations with matching labels will be saved to a new file as silver standard training data.
Authors: Jeffrey Smith, Bill Cramer, Evan French
"""
import sys, getopt, os, re
import metamap_helpers
from classes import Annotation

def main():
    """
	Main function of the application. Call -h or --help for command line inputs.
	"""
    metamap_path, ann_path, silver_ann_path, save_failed = None, None, None, None

    #Process command line entries.
    opts, args = getopt.getopt(sys.argv[1:], 'm:a:g:s:h',["metamap=","ann_path=","silver_ann_path=","save_failed=","help"])
    for opt, arg, in opts:
        if opt in ("-m","--metamap"):
            metamap_path = arg
        elif opt in ("-a","--ann_path"):
            ann_path = arg
        elif opt in ("-g","--silver_ann_path"):
            silver_ann_path = arg
        elif opt in ("-s","--save_failed"):
            save_failed = arg
        elif opt in ("-h","--help"):
            printHelp()
            return

    #Verify if needed command line entries are present.
    if metamap_path == None:
        print("You must specify a path to your MetaMap installation with -m or --metamap. Path must be absolute (i.e. '/opt/public_mm/bin/metamap12').")
        return
    if ann_path == None:
        print("You must specify a directory containing annotation files with -a or --ann_path.")
        return
    if silver_ann_path == None:
        print("You must specify a directory in which silver standard annotation files should be output with -g or --silver_ann_path.")
        return
    if save_failed == None:
        save_failed = False

    #Process the annotations
    ProcessAnnotations(metamap_path, ann_path, silver_ann_path, save_failed)

#Author: Evan French
def printHelp():
	"""
	Prints out the command line help information.
	"""	
	print("Options:")
	print("-m/--metamap DIR : Specify the absolute path of your MetaMap installation (i.e. '/opt/public_mm/bin/metamap12').")
	print("-a/--annotation_path DIR : Specify the directory containing annotation files.")
	print("-g/--silver_ann_path DIR : Specify the directory in which the silver standard annotations should be output.")
	print("-s/--save_failed [True, False] : Should files be created for non-silver standard annotations? ")
	
	return

#Author: Evan French
def ProcessAnnotations(metamap_path, ann_path, silver_ann_path, save_failed = False):
	"""
	Uses MetaMap to corroborate annotations. Annotations where the label on the annotation
	and the label predicted by MetaMap are in agreement are saved to a file with the same name
	in the directory specified by silver_ann_path

	@param metamap_path: Path to MetaMap installation
	@param ann_path: Path to annotation directory
	@param silver_ann_path: Path path for newly identified silver standard annotations
	@param save_failed: Save failed annotations to their own separate file for reference, defaults to false
	"""

	#Variables for tracking effectiveness
	totalAnnotations = 0
	totalSilver = 0
	totalAmbiguous = 0
	totalIncorrect = 0

	cwd = os.getcwd()
	os.chdir(ann_path)

	#Create output directory for newly identified silver standard annotations if it doesn't exist
	if not os.path.exists(silver_ann_path):
		os.makedirs(silver_ann_path)

	#Create output directory for non-silver annotations if save_failed parameter is True
	failed_path = os.path.join(silver_ann_path, "failed")
	if save_failed and not os.path.exists(failed_path):
		os.makedirs(failed_path)

	#Iterate over documents in the ann_path directory
	onlyFiles = [f for f in os.listdir() if os.path.isfile(f)]
	current = 0
	fileCount = len(onlyFiles)
	for document in onlyFiles:

		#Strip the extension from the file to get the document name
		docName = os.path.splitext(document)[0]
		current += 1
		print(f'Processing document {current}/{fileCount}, {document}')		

		#Instantiate a list to hold Annotations for each document
		annotationList = []
		silverList = []
		failedList = []
		ambiguousList = []

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
			isSilver, prediction = metamap_helpers.CheckAnnotationAgainstSemTypes(annotation, mmSemTypes[ix])
			
			#If metamap and annotation file agree, add to silver standard list
			if isSilver:
				silverList.append(annotation.original)
			elif prediction == 'none':
				ambiguousList.append(annotation.original)
			elif save_failed:
				failedList.append(prediction + ' ' + annotation.original)
		
		#Write new silver standard annotations to a new file
		new_silver_file = os.path.join(silver_ann_path, docName + ".con")
		with open(new_silver_file, 'w') as f:
			for item in silverList:
				f.write(item)

		#Write non-silver annotations to a new file if save_failed = True
		if save_failed:
			new_failed_file = os.path.join(failed_path, docName + "_incorrect.con")
			with open(new_failed_file, 'w') as f:
				for item in failedList:
					f.write(item)
			new_ambiguous_file = os.path.join(failed_path, docName + "_ambiguous.con")
			with open(new_ambiguous_file, 'w') as f:
				for item in ambiguousList:
					f.write(item)
	
		#Evaluation metrics
		totalAnnotations += len(annotationList)
		totalSilver += len(silverList)
		totalAmbiguous += len(ambiguousList)
		totalIncorrect += len(failedList)

	print("Total Annotations: ", str(totalAnnotations))
	print("Total Silver: ", str(totalSilver), str(totalSilver/totalAnnotations))
	print("Total Ambiguous: ", str(totalAmbiguous), str(totalAmbiguous/totalAnnotations))
	print("Total Incorrect: ", str(totalIncorrect), str(totalIncorrect/totalAnnotations))
	
	#Return to the original directory
	os.chdir(cwd)

if __name__ == "__main__":
	main()
