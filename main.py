#!/usr/bin/env python3
import argparse
import json
import os
import boto3
from pydub import AudioSegment

##########################################################################################
## AWS Polly Annunciator                                                                ##
## Copyright 2021, P5 Software                                                          ##
##########################################################################################
## *** Installation ***                                                                 ##
##                                                                                      ##
##    AWS CLI                                                                           ##
##     curl "https://s3.amazonaws.com/aws-cli/awscli-bundle.zip" -o "awscli-bundle.zip" ##
##     unzip awscli-bundle.zip                                                          ##
##     sudo ./awscli-bundle/install -i /usr/local/aws -b /usr/local/bin/aws             ##
##     aws configure                                                                    ##
##                                                                                      ##
##    ffmpeg                                                                            ##
##      brew update && brew install ffmpeg                                              ##
##                                                                                      ##
##    Python Requirements                                                               ##
##     pip3 install boto3 pydub                                                         ##
##########################################################################################

#You may need to update the location
AudioSegment.converter = "/usr/local/bin/ffmpeg"

def main():

    try:

        #Set the region
        pollyClient = boto3.Session(region_name=region).client('polly')

        #Make sure the json file exists
        if os.path.exists(jsonFilePath) == False:
            raise Exception("JSON file does not exist.")

        #Open the JSON file and load it into a dictionary
        with open(jsonFilePath) as jsonFile:
            annunciations = json.load(jsonFile)

        count = 0
        countCompleted = 0
        countCharacters = 0

        #Iterate through each element
        for annunciation in annunciations:

            #Validate the required fields
            if "name" not in annunciation:
                raise Exception("Missing required element \"name\" not found in element " + str(count))

            if "sentences" not in annunciation:
                raise Exception("Missing required element \"sentences\" not found in element " + str(count) + " (" + annunciation["name"] + ")")

            if len(annunciation["sentences"]) == 0:
                raise Exception("\"sentences\" array empty in element " + str(count) + " (" + annunciation["name"] + ")")

            #Set defaults if they were not overridden by the JSON file
            if "outputFormat" not in annunciation:
                annunciation["outputFormat"] = "mp3"
            
            if "voice" not in annunciation:
                annunciation["voice"] = "Matthew"

            if "engine" not in annunciation:
                annunciation["engine"] = "neural"

            if "language" not in annunciation:
                annunciation["language"] = "en-US"

            #Compose the output file
            outputFile = outputDirectory + (annunciation["name"].lower() + "." + annunciation["outputFormat"].lower()).replace(" ", "_")

            #See if the output file already exists
            if os.path.exists(outputFile) == False or overWrite == True:

                 #Compose the sentences
                text = "<speak>"

                for sentence in annunciation["sentences"]:
                    text = text + "<s>" + sentence + "</s>"

                    countCharacters = countCharacters + len(sentence)

                #Close the text
                text = text + "</speak>"

                #Submit the request to AWS
                pollyResponse = pollyClient.synthesize_speech(
                    Engine = annunciation["engine"],
                    LanguageCode = annunciation["language"],
                    OutputFormat = annunciation["outputFormat"],
                    Text = text,
                    TextType = 'ssml',
                    VoiceId = annunciation["voice"]
                )

                #Write the data to disk
                print("Creating file " + outputFile)
                file = open(outputFile, 'wb')
                file.write(pollyResponse['AudioStream'].read())
                file.close()

                #Prepend an audio file to the spoken text if requested
                if "prepend" in annunciation:

                    if "file" not in annunciation["prepend"]:
                        raise Exception("Prepend file not specified in JSON for annunication \"" + annunciation["name"] + "\"")

                    #Make sure the poly file format is mp3
                    if annunciation["outputFormat"] != "mp3":
                        raise Exception("Prepend requires the Polly file format to be mp3, which \"" + annunciation["name"] + "\" is not")
                    
                    #Make sure the prepend file exists
                    if os.path.exists(annunciation["prepend"]["file"]) == False:
                        raise Exception("Prepend file does not exist for annunication \"" + annunciation["name"] + "\"")

                    if os.path.splitext(annunciation["prepend"]["file"])[1].lower() != ".mp3":
                        raise Exception("Prepend requires the prepend file format to be mp3, which \"" + annunciation["name"] + "\" is not")

                    #Load the audio into memory
                    prependFile = AudioSegment.from_mp3(annunciation["prepend"]["file"])

                    if "volume" in annunciation["prepend"]:

                        #Perform audio transformation as necessary
                        print("Prepending clip...")
                        pollyFile = AudioSegment.from_mp3(outputFile)
                        prependFile = prependFile + annunciation["prepend"]["volume"]

                    #Merge the files
                    print("Merging clips...")
                    mergedFile = prependFile + pollyFile

                    #Merge the audio files
                    mergedFile.export(outputFile, format="mp3")
                    
                countCompleted = countCompleted + 1
            else:
                print("Skipping \"" + annunciation["name"] + "\" because the output file already exists.")

            #Increase the count
            count = count + 1

        print("Finished outputting " + str(countCompleted) + " files.  Approximate total characters processed was " + str(countCharacters) + ".")

    except Exception as ex:
        print("Error:", ex)
        quit()

def setup():

    global jsonFilePath
    global overWrite
    global outputDirectory
    global region

    #Create options that can be called by argument
    parser = argparse.ArgumentParser(description='Converts a formatted JSON request into Polly spoken text')
    parser.add_argument('jsonFilePath', help='Path to the JSON document containing the requested strings')
    parser.add_argument('--outputDirectory', dest='outputDirectory', default=os.path.dirname(__file__) + "/", help='Directory for outputting the completed files.  (default:' + os.path.dirname(__file__) + "/" + ")")
    parser.add_argument('--region', dest='region', default="us-east-1", help='AWS Processing Region  (default: us-east-1)')
    parser.add_argument('--overwrite', dest='overWrite', default=False, action=argparse.BooleanOptionalAction, help='If specified, overwrites existing files.')

    #Parse the arguments
    args = parser.parse_args()

    #Set the gloabl values
    jsonFilePath = args.jsonFilePath
    overWrite = args.overWrite
    outputDirectory = args.outputDirectory
    region = args.region

if __name__ == "__main__":
    setup()
    main()