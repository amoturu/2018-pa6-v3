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
      self.binary = True
      self.havelimitgenre = False
      self.havelimityear = False
      self.gotgenre = False
      self.gotyear = False
      self.ratedmovies = {}
      self.titleDict = {}
      self.topgenres = {}
      self.movFulfillsConstraints = []
      self.limitgenre = ""
      self.limityear = 0
      self.unratedmovies = []
      self.genres = ["Adventure", "Animation", "Children", "Comedy", "Fantasy", "Romance", "Drama", "Thriller", "Horror", "Action", "Sci-Fi", "Mystery", "Crime", "Documentary", "War", "Musical", "Western"]
      # self.binarized = []
      self.read_data()
      self.porter = PorterStemmer()
      self.positiveSet = set()
      self.negativeSet = set()
      self.sentimentBuilder()
      self.gettinggenre = False
      self.gettingyear = False
      # %sis replaced with movie title in responses
      self.PositiveResponse = ["It seems like you enjoyed %s. Maybe I should see it some time.",
                                   "Wow! I'm so glad you enjoyed %s. I love when people find things they like.",
                                   "Fantastic! Maybe we can watch %s together some time! After all, you liked it!",
                                   "My father also likes %s",
                                   "It's good to see that you found %s to be a good movie",
                               "You think %s is a good movie. And I think you are a good person!"]
      self.NegativeResponse = ["Yikes! Remind me to not see %s",
                                       "I'm sorry that you didn't like %s",
                                       "I also didn't like %s",
                               "I'll make sure to never see %s. Since you didn't like it!",
                               "I should find the director and let him know he is a failure! Because you didn't like %s",
                               "%s shouldn't even be called a movie. If you don't like something, then I don't like it either!"]
      self.ArbitraryInputResponses = ["You don't seem to be talking about a movie. Why don't we talk about a movie?",
                                      "I really only enjoy talking about movies. It is kind of my destiny",
                                      "Let's please talk about movies! If we find a movie you like, you will be so happy!",
                                      "Movies are so much more fun to talk about! Let's do that! Please!",
                                      "If we find a movie that you enjoy, maybe your friends will enjoy it too! Maybe you will make new friends."]
      self.QuestionWords = ["Who", "Where", "Why", "What", "When", "How", "Do", "Is", "Can", "Could", "Would"]




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
            self.titleDict[x[0]] = count;
            count += 1;

        for line in file.readlines():
            lineInfo = line.split(",")
            word = lineInfo[0]
            evaluation = lineInfo[1].rstrip()
            if evaluation == "pos":
                self.positiveSet.add(self.porter.stem(word))
            if evaluation == "neg":
                self.negativeSet.add(self.porter.stem(word))
        # print self.positiveSet

    def updateNegationFlag(self, negationFlag, word):
        negativeWordSet = set(["not", "never"])
        endOfSentence = [".", "!", "?"]
        if word in negativeWordSet or "n't" in word:
            negationFlag = not negationFlag
        for punctuation in endOfSentence:
            if punctuation in word:
                negationFlag = False
        return negationFlag

    def sentimentAnalysis(self, input, movie):
        positiveScore = 0;
        negativeScore = 0;
        negationFlag = False;
        for word in input.split(" "):
            negationFlag = self.updateNegationFlag(negationFlag, word)
            word = word.replace("!", "")
            word = word.replace(".", "")
            word = word.replace("?", "")
            word = self.porter.stem(word)
            # print word
            if (word in self.positiveSet and not negationFlag) or (word in self.negativeSet and negationFlag):
                if ((word in self.negativeSet and negationFlag)):
                    negationFlag = False
                positiveScore += 1
            elif (word in self.negativeSet and not negationFlag) or (word in self.positiveSet and negationFlag):
                if (word in self.positiveSet and negationFlag):
                    negationFlag = False
                negativeScore += 1
        if positiveScore > negativeScore:
            self.ratedmovies[self.titleDict[movie]] = 1;
            self.extractGenres(self.titles[self.titleDict[movie]][1])
            movieResponse = self.PositiveResponse[np.random.randint(0, len(self.PositiveResponse))]%movie
            return movieResponse
        if negativeScore > positiveScore:
            self.ratedmovies[self.titleDict[movie]] = -1;
            self.extractGenres(self.titles[self.titleDict[movie]][1])
            movieResponse = self.NegativeResponse[np.random.randint(0, len(self.NegativeResponse))]%movie
            return movieResponse
        if (positiveScore == 0 and negativeScore == 0) or (positiveScore == negativeScore):
            return "I'm sorry but I can't tell what you think about %s. Did you like %s? " % (movie, movie)


    def extractGenres(self, input):
      currentMovieGenres = input.split("|")
      for gen in currentMovieGenres:
        self.topgenres[gen] = self.topgenres.get(gen, 0) + 1

    def extractMovie(self, input):
        movies = re.findall("\"([^\"]*)\"", input)
        if len(movies) == 0:
            if(self.is_turbo):
                movies = self.extractUnquotedMovies(input)
                if len(movies) == 0:

                    return "I can't seem to find a movie in your remark"
            else:
                return "I can't seem to find a movie in your remark"

        if len(movies) > 1:
            return "Right now I'm detecting multiple movies. Please only tell me one movie!"
        movie = movies[0]
        if movie not in self.titleDict:
            if (self.is_turbo):
                movie = self.spellCheck(movie)
                if movie == None:
                    return "We can't find that movie in our database. Perhaps you can tell us about another one."
            else:
                return "We can't find that movie in our database. Perhaps you can tell us about another one."
        movieSentimentResponse = self.sentimentAnalysis(input, movie)
        if (len(self.ratedmovies) >= 5):
            #This NEEDS TO BE CORRECTED if NO RATINGMOVIE FOUND
            if self.is_turbo == True and self.gotgenre == False:
              self.gettinggenre = True
              return "Would you like to limit your genre?"              
            else:
              if len(self.ratingmovie()) > 0:
                return "I detect the top movie to be %s" % str(self.ratingmovie()[0])
              elif len(self.movFulfillsConstraints) == 0:
                return "Unfortunately, I don't know of any movie that fulfills all the constraints."
              else: 
                return "There is a movie %s that fulfills your constraints. But I don't know if you will like it." % (self.titles[self.movFulfillsConstraints[0]][0])
        else:
            Num_Movies_Needed = 5 - len(self.ratedmovies)
            return movieSentimentResponse + "Also I'll need your opinion on " + str(Num_Movies_Needed)  + " more movies before I start giving recommnedations."

    def extractWithForeignTitles(self, input):
        movies = re.findall("\"([^\"]*)\"", input)
        if len(movies) == 0:
            movies = self.extractUnquotedMovies(input)
        if len(movies) != 1:
            return "Please tell us about one movie"

        movie = movies[0]

        print self.findEmotion(input)

        if movie not in self.titleDict:
            if movie in self.alternateTitles:
                movie = self.alternateTitles[movie]
            else:
                pass

        #creates list of original titles and dict of alternate titles, still with years at end
        for title in self.titles:
            possible_titles = re.findall('(.*?) (?:\((?:a.k.a. )?(.*)\) )?\([0-9]{4}\)',title)
            original_title = ' '.join([possible_titles[0],possible_titles[-1]])
            if len(possible_titles) == 3:
                alternate_title = ' '.join([possible_titles[1],possible_titles[2]])
                self.alternateTitles[alternate_title] = title
            self.originalTitles.append(original_title)


            if movie in possible_titles:
                movie = title
                break

        if movie not in possible_titles:
            finalmovie = self.spellCheck(movie)
            if not finalmovie:
                return "We can't find that movie in our database. Perhaps you can tell us about another one"
        if (self.countMovieRecs == 5):
            return "Top Movie: " + str(self.ratingmovie()[0])
        return movie + self.sentimentAnalysis(input, movie) + str(self.countMovieRecs)

    #returns all the movie titles that were in the input
    #searches for capitalized words or numbers for the beginning of a title
    #makes a sublist of all the possible titles beginning with that word
    #checks to see if any of the sublists are in our list of movies
    def extractUnquotedMovies(self, input):
        movies = []
        input_list = input.split(' ')
        possible_movies = []

        for i,word in enumerate(input_list):
            if word[0].isupper() or word[0] in '0123456789':
                sublists = [sublist for sublist in (input_list[i:i+length] for length in xrange(1,len(input_list)-i+1))]

                possible_movies.extend(sublists)

        lowerTitleDict = [x.lower() for x in self.titleDict]
        for movie in possible_movies:
            movie = ' '.join(movie)
            if movie.lower() in lowerTitleDict:
                movies.append(movie)
                return movies
        if len(movies) == 0:
            for movie in possible_movies:
                movie = ' '.join(movie)
                spellChecked = self.spellCheck(movie)
                if spellChecked:
                    movies.append(spellChecked)
        return movies

    #Returns the spell corrected movie title, or False if none were found
    def spellCheck(self, movie):
        #look at each word
        #find titles with each word having edit distance less than 2
        #returns the first fitting title found
        given_words = movie.split(' ')
        splitTitleDict = [x.split(' ') for x in self.titleDict]

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
                return title
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

    def findEmotion(self, input):
        angrywords = ['angry','anger','mad','furious','livid','irate','irritated','irritating','outraged','outrageous','seething','infuriated','incensed']
        confusedwords = ['confused','confusing','n\'t understand','nt understand','not understand']
        sadwords = ['sad','unhappy','grumpy','depressed','depressing']
        if 'thank you' in input.lower() or 'thanks' in input.lower():
            return 'No, thank you!'
        if 'im sorry' in input.lower() or 'i\'m sorry' in input.lower():
            return 'Don\'t apologize! Everyone is entitled to their own opinion.'

        #formatted this way because some emotion keywords have spaces in them
        for word in angrywords:
            if word in input:
                return 'If you are ever angry about something, why not tell me about a movie you enjoyed?'
        for word in confusedwords:
            if word in input:
                return 'If you\'re confused about something, just tell me about a movie you\'ve enjoyed!'
        for word in sadwords:
            if word in input:
                return 'When I\'m sad, I like to talk about my favorite movies. What was a movie you really enjoyed?'
        return ''


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
        return "Ok. I will limit your genre to %s. Would you like the limit the year of the movie?" % self.limitgenre
      elif input.lower() == "no" or input.lower() == "n" or input.lower() == "nah" or input.lower() == "no thanks":
        self.gettinggenre = False
        self.gettingyear = True
        return "Ok! I won't limit your genre. Would you like to limit the year of the movie?"
      else:
        return "Sorry! I don't think I understand. If you dont want to limit genre, please say no. Otherwise, type the genre. If you want options, type options."

    def getYear(self,input):
      if input.lower() == "yes" or input.lower() == "y":
        return "What decade would you like to limit it to?"
      elif input.lower() == "no" or input.lower() == "n" or input.lower() == "nah" or input.lower() == "no thanks":
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

    def handleArticles(self):
        for i in range(0, len(self.titles)):
            title = self.titles[i][0]
            if ", The (" in title:
                title = title.replace(", The (", " (")
                self.titles[i][0] = "The " + title
            elif ", An (" in title:
                title = title.replace(", An (", " (")
                self.titles[i][0] = "An " + title
            elif ", A (" in title:
                title = title.replace(", A (", " (")
                self.titles[i][0] = "A " + title


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
      self.handleArticles();
      if self.binary:
        self.binarize()
      else:
        #user user binary
        self.meancenter2()



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
                      if self.binary:
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
      very fluently, Using non-binarized dataset, Alternate/foreign titles. 
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
