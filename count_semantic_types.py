import sys
import getopt
import os
import re
import metamap_helpers
import csv
import random
import math


def main():
    """
    Main function of the application. Call -h or --help for command line inputs.
    """
    metamap_path, test_file, treatment_file, problem_file, output_dir = None, None, None, None, None

    # Process command line entries.
    opts, args = getopt.getopt(sys.argv[1:], 'm:e:r:p:o:s', [
                               "metamap=", "test=", "treatment=", "problem", "output=", "sample_size="])
    for opt, arg, in opts:
        if opt in ("-m", "--metamap"):
            metamap_path = arg
        elif opt in ("-e", "test"):
            test_file = arg
        elif opt in ("-r", "treatment"):
            treatment_file = arg
        elif opt in ("-p"):
            problem_file = arg
        elif opt in ("-o", "--output"):
            output_dir = arg
        elif opt in ("-s", "--sample_size"):
            sample_size = int(arg)

    # Verify if needed command line entries are present.
    if metamap_path == None:
        print("You must specify a path to your MetaMap installation with -m or --metamap. Path must be absolute (i.e. '/opt/public_mm/bin/metamap12').")
        return
    if test_file == None:
        print("You must specify the test file path with -e or --test.")
        return
    if treatment_file == None:
        print("You must specify treatment file path with -r or --treatment.")
        return
    if problem_file == None:
        print("You must specify problem file with -p.")
        return
    if output_dir == None:
        print("You must specify an output directory.")
        return
    if sample_size == None:
        # Default sample size of sentences for each label type: 20k
        sample_size = 20 * 1000

    # Process files
    semTypeDict = {}
    semTypeDict = ProcessFile(metamap_path, test_file,
                              output_dir, semTypeDict, 'test', sample_size)
    semTypeDict = ProcessFile(
        metamap_path, treatment_file, output_dir, semTypeDict, 'treatment', sample_size)
    semTypeDict = ProcessFile(
        metamap_path, problem_file, output_dir, semTypeDict, 'problem', sample_size)

    # Write output to a new file
    output = os.path.join(output_dir, "semantic_type_counts.txt")
    with open(output, 'w+') as f:
        f.write('semantictype\ttest\ttreatment\tproblem\n')
        for key, value in semTypeDict.items():
            f.write('%s\t%d\t%d\t%d\n' %
                    (key, value['test'], value['treatment'], value['problem']))


def ProcessFile(metamap_path, file, output_dir, semTypeDict, label, sample_size):
    with open(file, "r") as f:
        records = f.readlines()

    # Seed random
    random.seed(0)

    if (len(records) < sample_size):
        # Oversample
        oversampled = records * math.floor(sample_size / len(records))
        records = oversampled + \
            random.sample(records, (sample_size - (len(oversampled))))
    else:
        # Undersample
        records = random.sample(records, sample_size)

    # Run pymetamap over annotations and return list semantic types for each record
    mmsemTypeDict = metamap_helpers.GetMetaMapSemanticTypes(
        metamap_path, records)

    # Count occurences of each semantic type for the given label
    for item in mmsemTypeDict:
        for semtype in item:
            # Add a new semantic type to dictionary
            if semtype not in semTypeDict:
                semTypeDict[semtype] = {key: 0 for key in [
                    'test', 'treatment', 'problem']}

            # Increment the semType count for the given label
            semTypeDict[semtype][label] = semTypeDict[semtype][label] + 1

    return semTypeDict


if __name__ == "__main__":
    main()
