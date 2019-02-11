"""
process_annotations_experiment.py
Scope: Process an existing annotation file by comparing the annotated labels with predicted labels using MetaMap.
    Annotations with matching labels will be saved to a new file as silver standard training data.
Authors: Jeffrey Smith, Bill Cramer, Evan French
"""
import sys
import getopt
import os
import re
import metamap_helpers
import csv
import itertools
from classes import Annotation


def main():
    """
        Main function of the application. Call -h or --help for command line inputs.
        """
    metamap_path, ann_path,  output_path, = None, None, None

    # Process command line entries.
    opts, args = getopt.getopt(sys.argv[1:], 'm:a:o:t:h', [
                               "metamap=", "ann_path=", " output_path=", "min_threshold=", "help"])
    for opt, arg, in opts:
        if opt in ("-m", "--metamap"):
            metamap_path = arg
        elif opt in ("-a", "--ann_path"):
            ann_path = arg
        elif opt in ("-o", "-- output_path"):
            output_path = arg
        elif opt in ("-t", "--min_threshold"):
            min_threshold = float(arg)
        elif opt in ("-h", "--help"):
            printHelp()
            return

    # Verify if needed command line entries are present.
    if metamap_path == None:
        print("You must specify a path to your MetaMap installation with -m or --metamap. Path must be absolute (i.e. '/opt/public_mm/bin/metamap12').")
        return
    if ann_path == None:
        print("You must specify a directory containing annotation files with -a or --ann_path.")
        return
    if output_path == None:
        print("You must specify a directory in which the results should be output with -g or -- output_path.")
        return
    if min_threshold == None:
        print("You must specify a minimum threshold with -t or --min_threshold.")
        return

    # Create output directory
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Initialize output file
    output_file = os.path.join(output_path, 'exp_results.txt')
    with open(output_file, 'w+', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Thresholds', 'Label', 'Silver',
                         'Ambiguous', 'Incorrect'])

    # Cartesian product of possible thresholds incrementing by 0.05
    thresholds = [x / 100 for x in range(int(min_threshold * 100), 100, 5)]
    tTests, tTreatments, tProblems = thresholds, thresholds, thresholds
    for tTest, tTreatment, tProblem in itertools.product(tTests, tTreatments, tProblems):
        # Generate semantic type list for each label's threshold
        tests, treatments, problems = GenerateSemanticTypeLists(
            tTest, tTreatment, tProblem, "semantic_type_lists.py")

        # Process annotations with the list generated
        ProcessAnnotations(metamap_path, ann_path,
                           output_path, tTest, tTreatment, tProblem, tests, treatments, problems)

# Author: Evan French


def ProcessAnnotations(metamap_path, ann_path, output_path, tTest, tTreatment, tProblem, tests, treatments, problems):
    """
    Uses MetaMap to corroborate annotations. Annotations where the label on the annotation
    and the label predicted by MetaMap are in agreement are saved to a file with the same name
    in the directory specified by  output_path

    @param metamap_path: Path to MetaMap installation
    @param ann_path: Path to annotation directory
    @param  output_path: Path path for newly identified silver standard annotations
    """
    # Instantiate a list to hold Annotations for each document
    labelDict = {}

    # Change to annotation directory
    cwd = os.getcwd()
    os.chdir(ann_path)

    # Iterate over documents in the ann_path directory
    onlyFiles = [f for f in os.listdir() if os.path.isfile(f)]
    current = 0
    fileCount = len(onlyFiles)
    for document in onlyFiles:
        current += 1
        print(f'Processing document {current}/{fileCount}, {document}')

        # Create an Annotation object for each line in the document and append the concepts to a list
        with open(document, 'r') as doc:
            annotationList = []
            for line in doc.readlines():
                an = Annotation(line)
                annotationList.append(an)

        # Run pymetamap over annotations and return semantic types
        annotated_concepts = [a.concept for a in annotationList]
        mmSemTypes = metamap_helpers.GetMetaMapSemanticTypes(
            metamap_path, annotated_concepts)

        # Check MetaMap prediction vs annotation label
        for ix, annotation in enumerate(annotationList):
            isSilver, prediction = metamap_helpers.CheckAnnotationAgainstSemTypes(
                annotation, mmSemTypes[ix], tests, treatments, problems)

            # Instantiate lists for each label type
            if annotation.label not in labelDict:
                labelDict[annotation.label] = {}
                labelDict[annotation.label]['annotationList'] = []
                labelDict[annotation.label]['silverList'] = []
                labelDict[annotation.label]['failedList'] = []
                labelDict[annotation.label]['ambiguousList'] = []

            # Track totals per label
            labelDict[annotation.label]['annotationList'].append(
                annotation.original)

            # If metamap and annotation file agree, add to silver standard list
            if isSilver:
                labelDict[annotation.label]['silverList'].append(
                    annotation.original)
            elif prediction == 'none':
                labelDict[annotation.label]['ambiguousList'].append(
                    annotation.original)
            else:
                labelDict[annotation.label]['failedList'].append(
                    annotation.original)

    # Return to the original directory
    os.chdir(cwd)

    print("Thresholds: ", tTest, tTreatment, tProblem)
    for key in labelDict:
        total = len(labelDict[key]['annotationList'])
        silver = len(labelDict[key]['silverList'])
        ambiguous = len(labelDict[key]['ambiguousList'])
        incorrect = len(labelDict[key]['failedList'])

        print(key)
        print("Total: ", total)
        print("Silver: ", silver)
        print("Ambiguous: ", ambiguous)
        print("Incorrect: ", incorrect)

        output_file = os.path.join(output_path, 'exp_results.txt')
        with open(output_file, 'a+', newline='') as f:
            writer = csv.writer(f)
            thresholds = str([tTest, tTreatment, tProblem])
            writer.writerow([thresholds, key, silver, ambiguous, incorrect])

# Parameters are thresholds for each label type


def GenerateSemanticTypeLists(tTest, tTreatment, tProblem, list_path):
    tests = []
    treatments = []
    problems = []

    with open('output.txt', 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')

        for row in reader:
            s = SemanticType()
            s.attr = row['semantictype']

            # counts
            s.tests = int(row['test'])
            s.treatments = int(row['treatment'])
            s.problems = int(row['problem'])
            s.total = s.tests + s.treatments + s.problems

            # percents
            s.pTests = float(s.tests / s.total)
            s.pTreatments = float(s.treatments / s.total)
            s.pProblems = float(s.problems / s.total)

            if (s.tests == max(s.tests, s.treatments, s.problems) and s.pTests >= tTest):
                tests.append(s)
            elif (s.treatments == max(s.tests, s.treatments, s.problems) and s.pTreatments >= tTreatment):
                treatments.append(s)
            elif (s.problems == max(s.tests, s.treatments, s.problems) and s.pProblems >= tProblem):
                problems.append(s)

    with open(list_path, 'w+') as f:
        f.write('#Author: Evan French\n')
        f.write('#MetaMap semantic types corresponding to medical tests\n')
        f.write('tests = [\n')
        for x in sorted(tests, key=lambda x: x.pTests, reverse=True):
            f.write('%s\n' % (str(x)))
        f.write(']\n')

        f.write('#Author: Evan French\n')
        f.write('#MetaMap semantic types corresponding to medical treatments\n')
        f.write('treatments = [\n')
        for x in sorted(treatments, key=lambda x: x.pTreatments, reverse=True):
            f.write('%s\n' % (str(x)))
        f.write(']\n')

        f.write('#Author: Evan French\n')
        f.write('#MetaMap semantic types corresponding to medical problems\n')
        f.write('problems = [\n')
        for x in sorted(problems, key=lambda x: x.pProblems, reverse=True):
            f.write('%s\n' % (str(x)))
        f.write(']')

    return tests, treatments, problems

# Author: Evan French


def printHelp():
    """
    Prints out the command line help information.
    """
    print("Options:")
    print("-m/--metamap DIR : Specify the absolute path of your MetaMap installation (i.e. '/opt/public_mm/bin/metamap12').")
    print("-a/--annotation_path DIR : Specify the directory containing annotation files.")
    print("-g/-- output_path DIR : Specify the directory in which the silver standard annotations should be output.")

    return

# Define semantic type class


class SemanticType:
    def __init__(self):
        self.attr = None
        self.name = None

        self.tests = 0
        self.treatments = 0
        self.problems = 0
        self.total = 0

        self.pTests = 0
        self.pTreatments = 0
        self.pProblems = 0

        # Read in semantic type mappings
        self.stMappings = {}

        with open('supplemental_data/semantic_type_mappings.txt', 'r') as f:
            reader = csv.DictReader(f, delimiter='|')
            for row in reader:
                attr = row['attr']
                self.stMappings[attr] = row['name']

    def __str__(self):
        return ("'%s', #%s" % (self.attr, self.stMappings[self.attr]))


if __name__ == "__main__":
    main()
