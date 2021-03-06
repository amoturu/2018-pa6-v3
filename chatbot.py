#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PA6, CS124, Stanford, Winter 2018
# v.1.0.2
# Original Python code by Ignacio Cases (@cases)
######################################################################
import csv
import math
import re
import copy
import collections
from collections import Counter

#add in PorterStemmer from assignment 3/4
from PorterStemmer import PorterStemmer
import gzip

import numpy as np

from movielens import ratings
from random import randint

class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    #############################################################################
    # `moviebot` is the default chatbot. Change it to your chatbot's name       #
    #############################################################################
    def __init__(self, is_turbo=False):
      self.name = 'moviebot'
      self.is_turbo = is_turbo
      #self.seekingMovie is meant to be true when looking for another movie recommendation from the user.
      #if the input does not contain another movie recommendation it will ask the user again for one.
      self.seekingMovie = False
      self.hasAlreadyDoneExtraInit = False
      self.binary = True
      self.havelimitgenre = False
      self.havelimityear = False
      self.gotgenre = False
      self.gotyear = False
      self.ratedmovies = {}
      self.titleDict = {}
      self.lowerTitleDict = {}
      self.topgenres = {}
      self.movFulfillsConstraints = []
      self.limitgenre = ""
      self.limityear = 0
      self.unratedmovies = []
      self.genres = ["Adventure", "Animation", "Children", "Comedy", "Fantasy", "Romance", "Drama", "Thriller", "Horror", "Action", "Sci-Fi", "Mystery", "Crime", "Documentary", "War", "Musical", "Western"]
      self.findNamesRegex = '(.*?) (?:\((?:a\.k\.a\. )?([^\)]*)\) )?(?:\((?:a\.k\.a\. )?([^\)]*)\) )?(?:\((?:a\.k\.a\. )?([^\)]*)\) )?(?:\((?:a\.k\.a\. )?([^\)]*)\) )?(?:\((?:a\.k\.a\. )?([^\)]*)\) )?(?:\((?:a\.k\.a\. )?([^\)]*)\) )?(\([0-9]{4}-?(?:[0-9]{4})?\))'
      self.emoLex = {'anger':[],'anticipation':[],'disgust':[],'fear':[],'joy':[],'negative':[],'positive':[],'sadness':[],'surprise':[],'trust':[]}
      # self.binarized = []
      # self.read_data()
      self.porter = PorterStemmer()
      self.positiveSet = set()
      self.negativeSet = set()
      self.punctuationIndex = 0;

      self.gettinggenre = False
      self.gettingyear = False
      # %sis replaced with movie title in responses
      self.PositiveResponse = ["It seems like you enjoyed %s. Maybe I should see it some time.",
                                   "I'm so glad you liked %s. I like when people find things they like.",
                                   "Maybe we can watch %s together some time! After all, you liked it!",
                                   "My father also likes %s.",
                                   "It's good to see that you found %s to be a good movie.",
                               "You think %s is a good movie. And I think you are a good person!"]
      self.StrongPositiveResponse = ["This must be the greatest movie in the world! You seem to absolutely love %s!",
                                     "Hold the phone! I'm going to go see %s right now! Since you adored it so much!",
                                     "No movie will ever compare to how amazing %s was! It must be one of your favorites!",
                                     "Every Oscar in history should go to %s. If it is has amazing as you say it is.",
                                     "%s isn't a movie it's a moment in history that you expereinced and that you loved! Maybe one day I'll find such happiness."]

      self.StrongNegativeResponse = ["%s is disgusting! I won't see it and never put yourself through the pain of watching it again!",
                                     "I should find the director and let him know he is a failure! Because you hated %s!",
                                     "Because of you, %s is no longer considered a movie in my eyes but rather a pile of garbage.",
                                     "The thought of %s's lack of entertainment value makes me want to cry. I'm sorry you hated it.",
                                     "%s should be played on repeat in hell. You hate that movie, so bad people must watch it."]

      self.NegativeResponse = ["Remind me to not see %s since you seem not to have liked it.",
                                       "I'm sorry that you didn't like %s.",
                                       "I also didn't like %s.",
                               "I'll try not to see %s. Since you didn't like it.",
                               "If you don't like %s, then I don't like it either."]
      self.ArbitraryInputResponses = ["You don't seem to be talking about a movie. Why don't we talk about a movie?",
                                      "I really only enjoy talking about movies. It is kind of my destiny ;).",
                                      "Let's please talk about movies! If we find a movie you like, you will be so happy!",
                                      "Movies are so much more fun to talk about! Let's do that! Please!",
                                      "If we find a movie that you enjoy, maybe your friends will enjoy it too! Maybe you will make new friends."]
      self.QuestionWords = ["Who", "Where", "Why", "What", "When", "How", "Do", "Is", "Can", "Could", "Would"]
      self.QuestionOptions = ["How about saying \"Please, %s?\" Just kidding, you are really polite, but my soul yearns to talk about movies.",
                              "Why would anyone want to know \"%s?\" Tell me about movies.",
                              "The answer to \"%s?\" is found only through hours of enjoying your favorite movies. Please enjoy them.",
                              "Would a philosopher ask, \"%s?\" Does this mean you are a philosopher? Forget it, tell me about movies you like!",
                              "I hate questions like \"%s\" They cause me to yearn for when you would tell me about movies."]
      self.SpecialStrongPositiveSentimentWords = ["love", "great", "amazing", "fantastic", "perfect", "incredible", "spectacular", "extraordinary", "marvelous", "awesome"]
      self.SpecialStrongNegativeSentimentWords = ["hate", "awful", "disgusting", "terrible", "shameful", "abysmal", "atrocious", "pathetic"]
      self.emotionResponseDictionary = {"anger" : ["You seem annoyed. I find that watching movies makes me feel less annoyed.",
                                                   "I'm detecting some level of annoyance. Please don't hurt me.",
                                                   "If you are annoyed, please drink a delicious diet coke and watch a movie",
                                                   "Don't be annoyed! You are beautiful.",
                                                   "Being annoyed isn't fun, but helping me find the perfect movie for you is!"],
                                        'fear' : ["OMG are you in trouble. I'm detecting apprehension. Quickly, let's watch a movie so we aren't scared.",
                                                  "If you are feeling apprehension, don't be. I'm here.",
                                                  "Fear is the only thing to be scared of. Oh no, you seem to have fear. Forget that I said that.",
                                                  "I sense a submissive awe radiating through you, but ignore it and get back to movies.",
                                                  "Fear is an illusion. So why are you feeling fear? Who cares? Just tell me about movies."],
                                        'trust':["You seem to be talking about trust. Is this because you don't trust my movie recommendations? Nevermind just let me prove myself.",
                                                 "My lover has trust issues. Please stop talking about trust. It reminds me.",
                                                 "Why are you talking about trust? Talk about movies. That is all that matters to us.",
                                                 "Trust is overrated. Movies should be rated.",
                                                 "Let's get back to talking about movies. I don't know why you are taling about trust."],
                                        'sadness':["Please don't talk about sad things. Just talk about movies! Movies are life.",
                                                   "Are you pensive because that is a sad emotion. Maybe talking about movies will make you seem less sad.",
                                                   "Don't talk about sad things. Be excited to talk about movies.",
                                                   "Being all nihilistic is overrated. Stop talking about sad things. Talk about movies.",
                                                   "Cry me a river is a song. I'm thinking about it because you are talking about sad things and not movies."],
                                        'disgust':["Ew! What you just said is disgusting. Please tell me about movies. They are less disgusting."],
                                        'anticipation':["Are you excited? I'm detecting anticipation. I'm anticipating a great movie for you."],
                                        'surprise':["Wow, you just surprised my. Please surprise me again by talking about movies."],
                                        'joy':["Are you happy? I'm detecting joy. Let's be happy together and talk about movies.",
                                               "Your comment makes me think that you are a person at peace with the world. How happy you must me?",
                                               "If you are happy and you know it, clap your hands. You should be clapping!",
                                               "Don't worry about a thing because everything is all right with you! Now take your happiness and pick a movie.",
                                               "I'm happy and you are at peace. What a world to live in!"]}




    #############################################################################
    # 1. WARM UP REPL
    #############################################################################

    def greeting(self):
      """chatbot greeting message"""
      #############################################################################
      # TODO: Write a short greeting message                                      #
      #############################################################################

      greeting_message = "Hi! I'm MovieBot! I'm going to recommend a movie to you. First I will ask you about your taste in movies. Tell me about a movie that you have seen."
      self.seekingMovie = True
      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################

      return greeting_message

    def goodbye(self):
      """chatbot goodbye message"""
      #############################################################################
      # TODO: Write a short farewell message                                      #
      #############################################################################

      goodbye_message = 'Have a nice day!'

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################

      return goodbye_message


    #############################################################################
    # 2. Modules 2 and 3: extraction and transformation                         #
    #############################################################################
    def sentimentBuilder(self):
        file = open("data/sentiment.txt", "r")
        count = 0
        for x in self.titles:
            self.titleDict[x[0]] = count

	    #gets the original title and all alternate titles (and the year)
	    all_names = re.findall(self.findNamesRegex,x[0])
	    if all_names:
	        all_names = list(all_names[0])
	    else:
		all_names = [x[0],'']
	    for name in all_names[:-1]:
		name, shortname = self.handleAllArticles(name)

		if name == '':
		    continue

		self.titleDict[name] = count #title with article, without year
		if shortname:
		    self.titleDict[shortname] = count #title w/o article, w/o year

		name = ' '.join([name,all_names[-1]])
		self.titleDict[name] = count #title with article, with year
		if shortname:
		    self.titleDict[shortname] = count #title without article, with year
		    if shortname[-1] in '.,;!?':
			self.titleDict[shortname[:-1]] = count

            count += 1;

	# Creates self.lowerTitleDict
	for key in self.titleDict:
	    self.lowerTitleDict[key.lower()] = self.titleDict[key]

        for line in file.readlines():
            lineInfo = line.split(",")
            word = lineInfo[0]
            evaluation = lineInfo[1].rstrip()
            if evaluation == "pos":
                self.positiveSet.add(self.porter.stem(word))
            if evaluation == "neg":
                self.negativeSet.add(self.porter.stem(word))

        for i in xrange(0, len(self.SpecialStrongPositiveSentimentWords)):
            self.SpecialStrongPositiveSentimentWords[i] = self.porter.stem(self.SpecialStrongPositiveSentimentWords[i])

        for j in xrange(0, len(self.SpecialStrongNegativeSentimentWords)):
            self.SpecialStrongNegativeSentimentWords[j] = self.porter.stem(self.SpecialStrongNegativeSentimentWords[j])
        # print self.positiveSet

    def handleAllArticles(self, name):
	shortname = ''
	#Move articles to front
	if name[-5:] in [', The',', Los',', Las',', Les',', Det',', Der',', Die',', Das',', Den',', Une']:
	    article = name[-3:]
	    shortname = name[:-5]
	    name = article + ' ' + shortname
	elif name[-4:] in [', An',', El',', En',', Un',', Le',', La',', Lo',', De',', Il']:
	    article = name[-2:]
	    shortname = name[:-4]
	    name = article + ' ' + shortname
	elif name[-3:] in [', A',', I']:
	    article = name[-1:]
	    shortname = name[:-3]
	    name = article + ' ' + shortname
	elif name[-4:] == ', L\'':
	    shortname = name[:-4]
	    name = 'L\'' + shortname

	return (name,shortname)

    def updateNegationFlag(self, negationFlag, word):
        negativeWordSet = set(["not", "never"])
        endOfSentence = [".", "!", "?"]
        if word in negativeWordSet or "n't" in word:
            negationFlag = not negationFlag
        for punctuation in endOfSentence:
            if punctuation in word:
                negationFlag = False
        return negationFlag

    def updateSentimentMultiplier(self, sentimentMultiplier, word):
        modifierWordSet = set(["very", "really", "truly"])
        endOfSentence = [".", "!", "?"]
        if word in modifierWordSet:
            sentimentMultiplier += 2
        for punctuation in endOfSentence:
            if punctuation in word:
                sentimentMultiplier = 0
        return sentimentMultiplier

    def checkPunctuation(self, word_list, idx):
        for i in range(idx, len(word_list)):
            if "." in word_list[i]:
                self.punctuationIndex = i;
                return 0
            if "!!" in word_list[i]:
                self.punctuationIndex = i;
                return 4
            if "?" in word_list[i]:
                self.punctuationIndex = i;
                return 0
            if "!" in word_list[i]:
                self.punctuationIndex = i;
                return 2
        self.punctuationIndex = len(word_list)
        return 0



    def sentimentAnalysis(self, input, movie):
        positiveScore = 0;
        negativeScore = 0;
        negationFlag = False;
        sentimentMultiplier = 0;
        exclemationPointMultiplier = 0;
        allCapsMultiplier = 0;
        self.punctuationIndex = 0
        word_list = input.split(" ");
        for idx, word in enumerate(word_list):
            if (self.is_turbo and idx > self.punctuationIndex):
                    exclemationPointMultiplier = self.checkPunctuation(word_list, idx)
            if (self.is_turbo and word.isupper()):
                allCapsMultiplier = 4;
            else:
                allCapsMultiplier = 0;
            word = word.lower()
            negationFlag = self.updateNegationFlag(negationFlag, word)
            sentimentMultiplier = self.updateSentimentMultiplier(sentimentMultiplier, word);
            word = word.replace("!", "")
            word = word.replace(".", "")
            word = word.replace("?", "")
            word = self.porter.stem(word)
            if (word in self.positiveSet and not negationFlag) or (word in self.negativeSet and negationFlag):
                if ((word in self.negativeSet and negationFlag)):
                    negationFlag = False
                positiveScore += 1
                if(self.is_turbo):
                    positiveScore += sentimentMultiplier
                    sentimentMultiplier = 0;
                    positiveScore += exclemationPointMultiplier
                    positiveScore +=  allCapsMultiplier;
                if (word in self.SpecialStrongPositiveSentimentWords):
                    positiveScore += 4
            elif (word in self.negativeSet and not negationFlag) or (word in self.positiveSet and negationFlag):
                if (word in self.positiveSet and negationFlag):
                    negationFlag = False
                negativeScore += 1
                if (self.is_turbo):
                    negativeScore +=  sentimentMultiplier
                    sentimentMultiplier = 0;
                    negativeScore += exclemationPointMultiplier
                    negativeScore += allCapsMultiplier
                if (word in self.SpecialStrongNegativeSentimentWords):
                    negativeScore += 4
        if positiveScore > negativeScore:
            self.ratedmovies[self.titleDict[movie]] = 1;
            self.extractGenres(self.titles[self.titleDict[movie]][1])
            movieResponse = self.PositiveResponse[np.random.randint(0, len(self.PositiveResponse))]%movie
            if (positiveScore - negativeScore >= 5):
                movieResponse = self.StrongPositiveResponse[np.random.randint(0, len(self.StrongPositiveResponse))]%movie
            return movieResponse
        if negativeScore > positiveScore:
            self.ratedmovies[self.titleDict[movie]] = -1;
            self.extractGenres(self.titles[self.titleDict[movie]][1])
            movieResponse = self.NegativeResponse[np.random.randint(0, len(self.NegativeResponse))]%movie
            if (negativeScore - positiveScore >= 5):
                movieResponse = self.StrongNegativeResponse[np.random.randint(0, len(self.StrongNegativeResponse))]%movie
            return movieResponse
        if (positiveScore == 0 and negativeScore == 0) or (positiveScore == negativeScore):
            return "I'm sorry but I can't tell what you think about %s. Talk about %s more." % (movie, movie)


    def extractGenres(self, input):
      currentMovieGenres = input.split("|")
      for gen in currentMovieGenres:
        self.topgenres[gen] = self.topgenres.get(gen, 0) + 1

    def handleUnrelatedInput(self, input):
        unrelateds = re.findall("Can you ([^\?\.\!]*)\?", input, flags=re.IGNORECASE)
        if (len(unrelateds) != 0):
            canYouStuff = ["I can %s. But tell me about how you feel about movies!", "I can't %s. But I can tell you about movies!", "To %s is a challenge but I'm up to it in three years. For now, let's talk about movies!", "Why would %sing be difficult, do you not believe in me. In the end though, you just really need to start talking about movies!"]
            unrelateds = canYouStuff[np.random.randint(0, len(canYouStuff))]%unrelateds[0]
            return unrelateds
        unrelateds = re.findall("([^\?\.\!]*)\?", input)
        if (len(unrelateds) != 0):
            unrelateds = unrelateds[0]
            if(len(unrelateds) > 0):
                unrelateds = unrelateds[0].lower() + unrelateds[1:]
            questionPhrase = self.QuestionOptions[np.random.randint(0, len(self.QuestionOptions))]%unrelateds;
            return questionPhrase
        else:
            emotionWordIGot = self.findEmotion(input)
            if emotionWordIGot in self.emotionResponseDictionary:
                responseEmotionsList = self.emotionResponseDictionary[emotionWordIGot]
                return responseEmotionsList[np.random.randint(0, len(responseEmotionsList))]
            else:
                booYouSuck = ["I'm not detecting anything of interest.", "Well, you've made my life awkward. I don't get what you are saying. Talk about some movies.",
                              "Please just get back to movies. You sound like you are talking about gibberish.",
                              "Talk about movies! Or call my ex Eliza. I don't get what you are saying.",
                              "We need to build bridges by talking about movies. Mention one to me and let's see where it goes."]
                return booYouSuck[np.random.randint(0, len(booYouSuck))]




    def extractMovie(self, input):
        unfoundInDataBaseScript = ["Well this is embarassing but I can't find \"%s\" in my database. Maybe you could tell me another movie.",
                                   "Who would have thought, but I can't find \"%s\" in my database. Tell me another one please.",
                                   "Your taste is too indie for me. I can't find \"%s\" in my database. Please tell me another one.",
                                   "I can't find \"%s\" in my database. Try another film please.",
                                   "Well it seems I've failed you. I can't find \"%s\" in my database. Please try another."]
        movies = re.findall("\"([^\"]*)\"", input)
	#movie = self.extractWithForeignTitles(input)
        if len(movies) == 0:
            if(self.is_turbo):
                movies = self.extractUnquotedMovies(input)
                if len(movies) == 0:
                    unrelated = self.handleUnrelatedInput(input)
                    if (unrelated != None):
                        return unrelated
                    return "I can't seem to find a movie in your remark"
            else:
                return "I can't seem to find a movie in your remark"

        if len(movies) > 1:
            multipleThingsMovies = ["Right now I'm detecting multiple movies. Please only tell me one movie!", "Please just talk about one movie."
                                    "If you talk about one movie at a time, my job is easier and your life is easier. So let's try that.",
                                    "Talk about one movie pretty please.",
                                    "Will you just talk about one movie. Life is great when you do that."]
            return multipleThingsMovies[np.random.randint(0, len(multipleThingsMovies))]
        movie = movies[0]
        input = input.replace(movie, "")
	if movie.lower() in self.lowerTitleDict:
	        movie_index = self.lowerTitleDict[movie.lower()]
	        movie = self.titles[movie_index][0]
	else:
#        if movie not in self.titleDict:
            unFoundMovie = movie;
            tellThem = unfoundInDataBaseScript[np.random.randint(0, len(unfoundInDataBaseScript))]
            tellThem = tellThem%unFoundMovie
            if (self.is_turbo):
                movie = self.spellCheck(movie)
                if movie == None:
                    return tellThem
            else:
                return tellThem
	movie_names = re.findall(self.findNamesRegex,movie)
	movie,_ = self.handleAllArticles(movie_names[0][0])

        movieSentimentResponse = self.sentimentAnalysis(input, movie)
        if (len(self.ratedmovies) >= 5):
            #This NEEDS TO BE CORRECTED if NO RATINGMOVIE FOUND
            if self.is_turbo == True and self.gotgenre == False:
              self.gettinggenre = True
              return movieSentimentResponse + " Would you like to limit your genre?"
            else:
              if len(self.ratingmovie()) > 0:
                return movieSentimentResponse + " Also, I detect the top movie to be %s" % str(self.ratingmovie()[0])
              elif len(self.movFulfillsConstraints) == 0:
                return movieSentimentResponse + " Also, unfortunately, I don't know of any movie that fulfills all the constraints."
              else: 
                return movieSentimentResponse + " Also, There is a movie %s that fulfills your constraints. But I don't know if you will like it." % (self.titles[self.movFulfillsConstraints[0]][0])
        else:
            Num_Movies_Needed = 5 - len(self.ratedmovies)
            return movieSentimentResponse + " Also I'll need your opinion on " + str(Num_Movies_Needed)  + " more movies before I start giving recommendations."


    #returns all the movie titles that were in the input
    #searches for capitalized words or numbers for the beginning of a title
    #makes a sublist of all the possible titles beginning with that word
    #checks to see if any of the sublists are in our list of movies
    def extractUnquotedMovies(self, input):
        movies = set([])
        input_list = input.split(' ')
	input_list = [x for x in input_list if x != '']
	#if input_list[-1][-1] in '.,;!?':
	#    input_list[-1] = input_list[-1][:-1]
        possible_movies = []

        for i,word in enumerate(input_list):
            if word[0].isupper() or word[0] in '0123456789':
                sublists = [sublist for sublist in (input_list[i:i+length] for length in xrange(1,len(input_list)-i+1))]

                possible_movies.extend(sublists)
	#for movie in possible_movies:
	#    movie = ' '.join(movie)
	possible_movies = [' '.join(x) for x in possible_movies]

	for movie in possible_movies:
	    if movie[-1] in '.,;!?':
		possible_movies.append(movie[:-1])

	possible_movies.sort(key = len)
	possible_movies = possible_movies[::-1]

        for movie in possible_movies:

            if movie.lower() in self.lowerTitleDict:
		movies.add(movie)

	movies = list(movies)
	movies.sort(key = len)
	movies = movies[::-1]
	#print movies
	if movies:
            return [movies[0]]
	else:
	    return []

    #Returns the spell corrected movie title, or False if none were found
    def spellCheck(self, movie):
        #look at each word
        #find titles with each word having edit distance less than 2
        #returns the first fitting title found
	movie = movie.lower()
        given_words = movie.split(' ')
        splitTitleDict = [x.split(' ') for x in self.lowerTitleDict]

        #for each title in our title dict
        for title_words in splitTitleDict:
            #possible_titles = re.findall('(.*?) (?:\((?:a.k.a. )?(.*)\) )?\([0-9]{4}\)',title)

            #if the number of words doesn't match, move to next possible title
            if len(given_words) != len(title_words):
                continue

            title = ' '.join(title_words)
            #first assume movie is correct fit
            goodMovie = True

            for i,word in enumerate(given_words):
                if goodMovie == False:
                    continue
                editDist = self.computeEditDistance(word,title_words[i])
                #if any word is too different, move to next possible title.
                if editDist > 2:
                    goodMovie = False
            #if all words were within reason, return the title
            if goodMovie:
		movie_index = self.lowerTitleDict[title]
                return self.titles[movie_index][0]
        return None

    def computeEditDistance(self,word1,word2):
        compArray = np.zeros([len(word2)+1,len(word1)+1])
        compArray[0] = xrange(0,len(word1)+1)
        test1 = 0
        test2 = 0
        test3 = 0

        rows = range(0,len(word2)+1)
        cols = range(0,len(word1)+1)
        #set up array correctly
        for i in rows:
            compArray[i][0] = i

        for i in rows[:-1]:
            for j in cols[:-1]:
                test1 = compArray[i+1][j] + 1
                test2 = compArray[i][j+1] + 1
                test3 = compArray[i][j]
                if word2[i] != word1[j]:
                    test3 += 2

                compArray[i+1][j+1] = min(test1,test2,test3)

        return compArray[-1][-1]

    #returns the emotion the person is likely feeling. Still need good words though.
    def findEmotion(self, input):
        input = re.sub('[^\w\s]','',input)
        input_list = input.split(' ')
        emoDict = {'anger':0,'fear':0,'trust':0,'sadness':0,'disgust':0,'anticipation':0,'surprise':0,'joy':0}
        foundE = False;
        for word in input_list:
            word = self.porter.stem(word)
            word = word.lower()
            if word in self.emoLex['anger']:
                emoDict['anger'] += 2
                foundE = True;
            if word in self.emoLex['fear']:
                emoDict['fear'] += 2
                foundE = True;
            if word in self.emoLex['trust']:
                emoDict['joy'] += 1
		emoDict['fear'] += 1
                foundE = True;
            if word in self.emoLex['sadness']:
                emoDict['sadness'] += 2
                foundE = True;
            if word in self.emoLex['disgust']:
                emoDict['anger'] += 1
                emoDict['sadness'] += 1
                foundE = True;
            if word in self.emoLex['anticipation']:
                emoDict['joy'] += 1
                emoDict['anger'] += 1
                foundE = True;
            if word in self.emoLex['surprise']:
                emoDict['fear'] += 1
                emoDict['sadness'] += 1
                foundE = True;
            if word in self.emoLex['joy']:
                emoDict['joy'] += 2
                foundE = True;

        if foundE == False:
            return "No Emotion"
        return max(emoDict, key = emoDict.get)


    #if you have two genres that are equally top, then just picks arbitarily
    def getTopGenre(self):
      count = Counter(self.topgenres)
      for k, v in count.most_common(1):
        return k


    def getGenre(self, input):
      if input.lower() == "yes" or input.lower() == "y":
        return "What genre do you want to limit it to? Your top genre is %s. If you want other genres, type options." % self.getTopGenre()
      elif input.lower() == "options":
        return "The options are Adventure, Animation, Children, Comedy, Fantasy, Romance, Drama, Thriller, Horror, Action, Sci-Fi, Mystery, Crime, Documentary, War, Musical, and Western. Whew that was a mouthful."
      elif input.capitalize() in self.genres:
        self.limitgenre = input.capitalize()
        self.havelimitgenre = True
        self.gettinggenre = False
        self.gettingyear = True
        self.gotgenre = True
        return "Ok. I will limit your genre to %s. Would you like the limit the year of the movie? Please give me a yes or no response" % self.limitgenre
      elif input.lower() == "no" or input.lower() == "n" or input.lower() == "nah" or input.lower() == "no thanks":
        self.gettinggenre = False
        self.gettingyear = True
        return "Ok! I won't limit your genre. Would you like to limit the year of the movie? Please give me a yes or no response."
      else:
        return "Sorry! I don't think I understand. If you dont want to limit genre, please say no. Otherwise, type the genre. If you want options, type options."

    def getYear(self,input):
      if input.lower() == "yes" or input.lower() == "y":
        return "What decade would you like to limit it to?"
      elif input.lower() == "no" or input.lower() == "n" or input.lower() == "nah" or input.lower() == "no thanks":
        self.gettingyear = False
        return "Ok. I won't limit to a year range. I think the next movie you should see is " + str(self.ratingmovie()[0])
      elif input.isdigit() and (int(input) > 2018 or int(input) < 1900):
        return "We don't have any movies for that decade. Please try again with another year."
      elif input.isdigit():
        self.havelimityear = True 
        self.gettingyear = False
        self.gotyear = True
        #gets first three numbers of the year
        self.limityear = int(int(input)/10)
        if len(self.ratingmovie()) > 0:
          return "Ok, I will limit your decade to %ss. I detect the top movie to be %s" % (str(self.limityear*10), str(self.ratingmovie()[0]))
        elif len(self.movFulfillsConstraints) == 0:
          return "Unfortunately, I don't know of any movie that fulfills all the constraints."
        else: 
          return "There is a movie %s that fulfills your constraints. But I don't know if you will like it." % (self.titles[self.movFulfillsConstraints[0]][0])
      else:
        return "I don't think you inputted a valid year. Please try again."
    def process(self, input):
      """Takes the input string from the REPL and call delegated functions
      that
        1) extract the relevant information and
        2) transform the information into a response to the user
      """
      #############################################################################
      # TODO: Implement the extraction and transformation in this method, possibly#
      # calling other functions. Although modular code is not graded, it is       #
      # highly recommended                                                        #
      #############################################################################
      response = "no response"
      if not self.hasAlreadyDoneExtraInit:
        self.read_data()
        self.sentimentBuilder()
        self.hasAlreadyDoneExtraInit = True
      if self.gettinggenre == True:
        response = self.getGenre(input)
      elif self.gettingyear == True:
        response = self.getYear(input)
      else:
        response = self.extractMovie(input)


      return response


    #############################################################################
    # 3. Movie Recommendation helper functions                                  #
    #############################################################################

#    def handleArticles(self):
#        for i in range(0, len(self.titles)):
#            title = self.titles[i][0]
#            if ", The (" in title:
#                title = title.replace(", The (", " (")
#                self.titles[i][0] = "The " + title
#            elif ", An (" in title:
#                title = title.replace(", An (", " (")
#                self.titles[i][0] = "An " + title
#            elif ", A (" in title:
#                title = title.replace(", A (", " (")
#                self.titles[i][0] = "A " + title


    # def runExtraInitialization(self):
    #   self.didProcessOnce = True
    #   if self.is_turbo == False:
    #     print "here"
    #     self.binarize()
    #   else:
    #     #user user non-binary
    #     print "non-binarizing"
    #     self.meancenter2()


    def read_data(self):
      """Reads the ratings matrix from file"""
      # This matrix has the following shape: num_movies x num_users
      # The values stored in each row i and column j is the rating for
      # movie i by user j
      self.titles, self.ratings = ratings()
      #self.handleArticles();
      if not self.is_turbo:
        self.binarize()
      else:
        #user user binary
        self.meancenter2()
      self.makeEmoLex()


    def binarize(self):
      """Modifies the ratings matrix to make all of the ratings binary"""
      #for the homework, take the utility matrix,
      #subtract the means of each of the rows, from the actual values of the ratings
      #then use it for binarized
      #-1 if less than mean
      #0 if no ratings
      #+1 if greater than means

      self.binarized = copy.copy(self.ratings)
      for row in range(0, len(self.ratings)):
          rate = self.ratings[row]
          if len(rate[rate != 0]) > 0:
            mean = float(np.sum(rate[rate > 0]))/rate[rate > 0].size
            rate[rate > 0] -= mean
            self.binarized[row] = [np.sign(x) for x in rate]

    #item-item mean centered
    def meancenter(self):
      self.meancentered = copy.copy(self.ratings)
      #go through all of the users
      #calculate the mean for the user
      #replace all of the values
      for row in range(0, len(self.ratings)):
          rate = self.ratings[row]
          if len(rate[rate != 0]) > 0:
            mean = float(np.sum(rate[rate > 0]))/rate[rate > 0].size
            rate[rate > 0] -= mean
            self.meancentered[row] = rate

    #user-user mean centered
    def meancenter2(self):
      self.meancentered = copy.copy(self.ratings)

      for userCol in range(0, len(self.ratings[0])):
        column = np.array(self.meancentered[:,userCol])
        # print column
        if len(column[column != 0]) > 0:
          mean = float(np.sum(column[column > 0]))/column[column > 0].size
          column[column > 0] -= mean
          for movieRow in range(0, len(self.ratings)):
            self.meancentered[movieRow][userCol] = column[movieRow]

    def makeEmoLex(self):
	with gzip.open('deps/emoLex.txt.gz', 'r') as f:
	    lines = f.readlines()

	for line in lines:
	    datum = re.findall('(\w*)\s+(\w*)\s+([0-9])',line)
	    if datum:
		datum = list(datum[0])
	    else:
		continue
	    word = datum[0]
	    emotion = datum[1]
	    val = datum[2]
	    if val == '1':
		self.emoLex[emotion].append(self.porter.stem(word))

    def distance(self, u, v):
      """Calculates a given distance function between vectors u and v"""
      #similarity = cosine similarity on the binarized NOT pearson

      dotproduct = np.dot(u,v)
      sqrtotalu = np.sqrt(np.sum(np.square(u), axis=0))
      sqrtotalv = np.sqrt(np.sum(np.square(v), axis=0))
      if sqrtotalu == 0 or sqrtotalv == 0:
          return 0
      dist = float(dotproduct)/(sqrtotalu * sqrtotalv)
      return dist


    def recommend(self, u):
      """Generates a list of movies based on the input vector u using
      collaborative filtering"""
      # TODO: Implement a recommendation function that takes a user vector u
      # and outputs a list of movies recommended by the chatbot

      pass

    def ratingmovie(self):
        highestrating = 0
        topmovie = ""
        # subtracts all movies indexes with movies that we've seen to only have unrated movie indexes
        self.unratedmovies = list(set(xrange(0, len(self.titles))) - set(self.ratedmovies.keys()))

        #if you are limiting the genres even further based on the limiting genre
        randregex = "(.*?) (?:\((?:a\.k\.a\. )?([^\)]*)\) )?(?:\((?:a\.k\.a\. )?([^\)]*)\) )?(?:\((?:a\.k\.a\. )?([^\)]*)\) )?(?:\((?:a\.k\.a\. )?([^\)]*)\) )?(?:\((?:a\.k\.a\. )?([^\)]*)\) )?(?:\((?:a\.k\.a\. )?([^\)]*)\) )?(\([0-9]{4}-?(?:[0-9]{4})?\))"
      
        # will give you title if no year for movie
        for unratedmov in self.unratedmovies:
            if (self.havelimitgenre and len(self.limitgenre) != 0 and self.limitgenre in str(self.titles[unratedmov][1])) or (self.havelimitgenre == False):
              # print self.titles[unratedmov][0]
              matches = re.findall(randregex, self.titles[unratedmov][0])
              if len(matches) > 0:
                year = matches[len(matches) -1]
                actualyear = year[len(year)-1]
                actualyear = actualyear.replace("(", "")
                actualyear = actualyear.replace(")", "")
                # print actualyear
                if (self.havelimityear and self.limityear != 0 and actualyear.isdigit() and int(int(actualyear)/10) == self.limityear) or (self.havelimityear == False):
                  self.movFulfillsConstraints.append(unratedmov)
                  # print "setting rating"
                  rating = 0
                  for ratedmov in self.ratedmovies:
                      if not self.is_turbo:
                        dist = self.distance(self.binarized[unratedmov], self.binarized[ratedmov])
                      else:
                        dist = self.distance(self.meancentered[unratedmov], self.meancentered[ratedmov])
                      rating += dist * self.ratedmovies[ratedmov]
                  # print rating
                  if rating > highestrating:
                      # print "setting highestrating"
                      highestrating = rating
                      topmovie = self.titles[unratedmov]
        return topmovie

    #############################################################################
    # 4. Debug info                                                             #
    #############################################################################

    def debug(self, input):
      """Returns debug information as a string for the input string from the REPL"""
      # Pass the debug information that you may think is important for your
      # evaluators
      debug_info = 'debug info'
      return debug_info


    #############################################################################
    # 5. Write a description for your chatbot here!                             #
    #############################################################################
    def intro(self):
      return """
      Your task is to implement the chatbot as detailed in the PA6 instructions.
      Remember: in the starter mode, movie names will come in quotation marks and
      expressions of sentiment will be simple!
      Creative features that were implemented and listed in the rubric: Identifying movies 
      without quotation marks or perfect capitalization, Fine-grained sentiment 
      extraction, Spell-checking movie titles, Responding to arbitrary input, Speaking 
      very fluently, Using non-binarized dataset, Alternate/foreign titles, 
      Identifying and responding to emotions (through unrelated non-movie inputs).
      For Identifying and responding to emotions we use a four emotion based system
      That is based off of the Plutchick's wheel of emotion. We created four emotion
      categories from it. We have Annoyance which is combining aggressiveness and
      contempt. So angry words count a lot towards annoyance and disgust and anticipation
      words count somewhat. We also have a sad things, apprehension/fear and serenity/happy.
      Please look at the four larger sections of the Plutchick wheel of emotion. That represents are
      four overall categories. It's on slide 20 of Dan's emotion lecture.
      For the creative mode, we implemented used the non-binarized dataset. We 
      noticed that user mean centering was more successful than item mean centering.
      We still use item-item collaborative filtering. 
      Another feature that we implemented is limiting by genre. It outputs the users
      main genre and asks what genre to limit the output by.
      Another feature is limiting by year. We take both genre and year into account. 
      If there is a movie that fulfills the constraints, but we do not know whether
      the user will like the movie (ie no ratings in the movie, or one rating after
      we mean center becomes all zeros), we output that it fulfills the constraints, 
      but they might or might not like the movie.
      Also asking "can you" questions is fun.
      """


    #############################################################################
    # Auxiliary methods for the chatbot.                                        #
    #                                                                           #
    # DO NOT CHANGE THE CODE BELOW!                                             #
    #                                                                           #
    #############################################################################

    def bot_name(self):
      return self.name


if __name__ == '__main__':
    Chatbot()
