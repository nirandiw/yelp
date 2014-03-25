import numpy as np
import time
from netflix.data_loader import DataLoader

__author__ = 'franpena'


class MatrixFactorizer:
    LEARNING_RATE = 0.001
    LAMBDA = 0.02
    NUM_FEATURES = 5
    K = 0.02
    FEATURE_INIT_VALUE = 0.1
    MIN_IMPROVEMENT = 0.0001
    MIN_ITERATIONS = 120

    def __init__(self, review_matrix):
        self.review_matrix = review_matrix
        self.user_feature_matrix = self.create_user_feature_matrix()
        self.movie_feature_matrix = self.create_movie_feature_matrix()
        self.global_average = self.calculate_global_average()

    # OK
    def get_user_ratings(self, user_id):
        """
        Returns a numpy array with the ratings that user_id has made

        :rtype : numpy array
        :param user_id: the id of the user
        :return: a numpy array with the ratings that user_id has made
        """
        user_reviews = self.review_matrix[user_id]
        user_reviews = user_reviews.toarray().ravel()
        user_rated_movies, = np.where(user_reviews > 0)
        user_ratings = user_reviews[user_rated_movies]
        return user_ratings

    # OK
    def get_movie_ratings(self, movie_id):
        """
        Returns a numpy array with the ratings that movie_id has received

        :rtype : numpy array
        :param movie_id: the id of the movie
        :return: a numpy array with the ratings that movie_id has received
        """
        movie_reviews = self.review_matrix[:, movie_id]
        movie_reviews = movie_reviews.toarray().ravel()
        movie_rated_users, = np.where(movie_reviews > 0)
        movie_ratings = movie_reviews[movie_rated_users]
        return movie_ratings

    # OK
    def calculate_global_average(self):
        all_reviews = self.review_matrix.toarray().ravel()
        average = np.average(all_reviews, weights=(all_reviews > 0))
        return average

    # OK
    def create_user_feature_matrix(self):
        """
        Creates a user feature matrix of size NUM_FEATURES X NUM_USERS
        with all cells initialized to FEATURE_INIT_VALUE

        :rtype : numpy matrix
        :return: a matrix of size NUM_FEATURES X NUM_USERS
        with all cells initialized to FEATURE_INIT_VALUE
        """
        num_users = self.review_matrix.shape[0]
        user_feature_matrix = np.empty((self.NUM_FEATURES, num_users))
        user_feature_matrix[:] = self.FEATURE_INIT_VALUE
        return user_feature_matrix

    # OK
    def create_movie_feature_matrix(self):
        """
        Creates a user feature matrix of size NUM_FEATURES X NUM_MOVIES
        with all cells initialized to FEATURE_INIT_VALUE

        :rtype : numpy matrix
        :return: a matrix of size NUM_FEATURES X NUM_MOVIES
        with all cells initialized to FEATURE_INIT_VALUE
        """
        num_movies = self.review_matrix.shape[1]
        movie_feature_matrix = np.empty((self.NUM_FEATURES, num_movies))
        movie_feature_matrix[:] = self.FEATURE_INIT_VALUE
        return movie_feature_matrix

    # OK
    def calculate_pseudo_average_movie_rating(self, movie_id):
        """
        Calculates the weighted average of the movie ratings which deals with
        the cases where there are few ratings for a movie

        :rtype : float
        :param movie_id: the id of the movie
        :return: the weighted average of the movie ratings which deals with
        the cases where there are few ratings for a movie
        """
        movie_ratings = self.get_movie_ratings(movie_id)
        k = 25
        return (self.global_average * k + np.sum(movie_ratings)) / (
            k + np.size(movie_ratings))

    # OK
    def calculate_pseudo_average_user_rating(self, user_id):
        """
        Calculates the weighted average of the user ratings which deals with
        the cases where there are few ratings by a user

        :rtype : float
        :param user_id: the id of the user
        :return: the weighted average of the movie ratings which deals with
        the cases where there are few ratings by a user
        """
        user_ratings = self.get_user_ratings(user_id)
        k = 25
        return (self.global_average * k + np.sum(user_ratings)) / (
            k + np.size(user_ratings))

    # OK
    def calculate_average_movie_offset(self, movie_id):
        """
        Calculates the average movie offset (also called user bias) with respect
        to the global average rating

        :rtype : float
        :param movie_id: the is of the movie
        :return: the average user offset
        """
        return self.calculate_pseudo_average_movie_rating(movie_id) - \
               self.global_average

    # OK
    def calculate_average_user_offset(self, user_id):
        """
        Calculates the average user offset (also called user bias) with respect
        to the global average rating

        :rtype : float
        :param user_id: the is of the user
        :return: the average user offset
        """
        return self.calculate_pseudo_average_user_rating(user_id) - \
               self.global_average

    def calculate_error(self, user_id, movie_id):
        """
        Calculates the difference between the known rating of the user_id for
        the movie_id and the predicted rating of that user for the movie

        :rtype : float
        :param user_id: the id of the user
        :param movie_id: the id of the movie
        :return: the actual rating minus the predicted rating
        """
        #print self.get_rating(user_id, movie_id)
        #print self.global_average
        #print self.calculate_average_user_offset(user_id)
        #print self.calculate_average_movie_offset(movie_id)
        #print self.predict_rating(user_id, movie_id)

        return self.get_rating(user_id, movie_id) -\
               self.global_average -\
               self.calculate_average_user_offset(user_id) -\
               self.calculate_average_movie_offset(movie_id) -\
               self.predict_rating(user_id, movie_id)

    def get_rating(self, user_id, movie_id):
        """
        Returns the known rating that user_id has given to movie_id

        :rtype : float
        :param user_id: the id of the user
        :param movie_id: the id of the movie
        :return: the known rating that user_id has given to movie_id
        """
        return self.review_matrix[user_id, movie_id]

    def predict_rating(self, user_id, movie_id):
        """
        Makes a prediction of the rating that user_id will give to movie_id if
        he/she sees it

        :rtype : float
        :param user_id: the id of the user
        :param movie_id: the id of the movie
        :return: a float in the range [1, 5] with the predicted rating for
        movie_id by user_id
        """
        rating = np.dot(self.user_feature_matrix[:, user_id],
                        self.movie_feature_matrix[:, movie_id])
        # We trim the ratings in case they go above or below the stars range
        if rating > 5:
            rating = 5
        elif rating < 1:
            rating = 1
        return rating

    def train(self, user_id, movie_id, feature_index):
        error = self.calculate_error(user_id, movie_id)

        user_feature_vector = self.user_feature_matrix[feature_index]
        movie_feature_vector = self.movie_feature_matrix[feature_index]

        user_feature_value = user_feature_vector[user_id]
        movie_feature_value = movie_feature_vector[movie_id]
        user_feature_vector[user_id] += \
            self.LEARNING_RATE * \
            (error * movie_feature_value - self.K * user_feature_value)
        movie_feature_vector[movie_id] += \
            self.LEARNING_RATE * \
            (error * user_feature_value - self.K * movie_feature_value)

        #print(error)

        return error ** 2

    def predict_baseline_rating(self, user_id, movie_id):
        return self.calculate_pseudo_average_movie_rating(movie_id) + \
               self.calculate_average_user_offset(user_id)

    def calculate_features(self):
        rmse = 0
        last_rmse = 0
        num_ratings = np.count_nonzero(self.review_matrix.toarray().ravel())
        rows, cols = self.review_matrix.nonzero()
        for feature in xrange(self.NUM_FEATURES):
            j = 0
            while (j < self.MIN_ITERATIONS) or\
                    (rmse < last_rmse - self.MIN_IMPROVEMENT):
                squared_error = 0
                last_rmse = rmse

                for user_id, movie_id in zip(rows, cols):
                    #print('User ID = ' + str(user_id) + '\tMovie ID = '+ str(movie_id))
                    squared_error += self.train(user_id, movie_id, feature)

                rmse = (squared_error / num_ratings) ** 0.5
                print(rmse)
                j += 1





'''
    def hola(self):
        N = self.model.shape[0]  #no of users
        M = self.model.shape[1]  #no of items
        K = 96
        learning_rate = 0.001
        regularization = 0.25
        self.p = np.random.rand(N, K)
        self.q = np.random.rand(M, K)
        rows, cols = self.model.nonzero()
        for step in xrange(steps):
            for u, i in zip(rows, cols):

                #calculate error for gradient
                e = self.model - np.dot(self.p, self.q.T)

                p_temp = learning_rate * (
                    e[u, i] * self.q[i, :] - regularization * self.p[u, :])

                self.q[i, :] += learning_rate * (
                    e[u, i] * self.p[u, :] - regularization * self.q[i, :])

                self.p[u, :] += p_temp
'''

movielens_file_path = 'E:/UCC/Thesis/datasets/ml-100k/u.data'
my_reviews = DataLoader.create_review_matrix(movielens_file_path)
matrix_factorizer = MatrixFactorizer(my_reviews)
time1 = time.time()
print('Time 1 = ' + str(time1))
sqer = matrix_factorizer.train(0, 0, 0)
matrix_factorizer.calculate_features()
time2 = time.time()
print('Time 2 = ' + str(time2))
total_time = (time2 - time1)
print 'Total time = ' + str(total_time)

import cProfile
cProfile.run('matrix_factorizer.train(0, 0, 0)')
