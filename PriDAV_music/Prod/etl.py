# ETLs & Transformation pipeline

import os
import sys

sys.dont_write_bytecode = True

import pandas as pd
import numpy as np

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.preprocessing import PolynomialFeatures

from sklearn.impute import SimpleImputer, KNNImputer

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer


# ---------

class ETL(BaseEstimator, TransformerMixin):
    '''Custom ETL model, abstract class, when creating an ETL use class inheritance and overwrite
       self.transform method with custom transformation, must return transformed X.'''

    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        return X
    
    def set_output(self, *, transform = None):
        return self



class FrequencyEncoder(ETL):

    TARGET_COL = 'artist_name'

    def __init__(self, strategy='max'):
        self.frequencies = None
        self.default_value = 0
        self.strategy = strategy
    
    def fit(self, X, y=None):
        freqs = X[self.TARGET_COL].str.split(',').explode().value_counts()
        self.frequencies = freqs.to_dict()
        return self
    

    def transform(self, X, y=None):

        X_new = X.copy()

        if self.strategy == 'max':
            X_new[self.TARGET_COL] = X[self.TARGET_COL].str.split(',').apply(
                lambda artists: max(self.frequencies.get(artist, self.default_value) for artist in artists)
            )

        elif self.strategy == 'sum':
            X_new[self.TARGET_COL] = X[self.TARGET_COL].str.split(',').apply(
                lambda artists: sum(self.frequencies.get(artist, self.default_value) for artist in artists)
            )

        #X_new[self.TARGET_COL] = X[self.TARGET_COL].map(self.frequencies).fillna(self.default_value)

        return X_new



class CircleOfFifthsEncoding(ETL):

    TARGET_COLUMN = 'key'

    # Pôvodný mapping z datasetu (chromatic scale: 0–11)
    # Tento mapping je založený na poltónových intervaloch.
    chromatic_scale = {
        0: "C",
        1: "C#/Db",
        2: "D",
        3: "D#/Eb",
        4: "E",
        5: "F",
        6: "F#/Gb",
        7: "G",
        8: "G#/Ab",
        9: "A",
        10: "A#/Bb",
        11: "B"
    }

    # Korektný ordinal pre Circle of Fifths:
    # Táto sekvencia reflektuje harmonické vzťahy medzi kľúčmi:
    # každý nasledujúci kľúč je vzdialený o kvintu (7 poltónov).
    circle_of_fifths_mapping = {
        0: 0,  # C
        7: 1,  # G
        2: 2,  # D
        9: 3,  # A
        4: 4,  # E
        11: 5, # B
        6: 6,  # F#/Gb
        1: 7,  # C#/Db
        8: 8,  # G#/Ab
        3: 9,  # D#/Eb
        10: 10, # A#/Bb
        5: 11  # F
    }


    def transform(self, X, y=None):

        X_new = X.copy()

        ordinal_remapping = X[self.TARGET_COLUMN].map(self.circle_of_fifths_mapping)

        theta = (2 * np.pi / 12) * ordinal_remapping

        x = np.cos(theta)
        y = np.sin(theta)

        X_new = X_new.drop(self.TARGET_COLUMN, axis=1, errors='ignore')

        X_new['key_x'] = x
        X_new['key_y'] = y

        return X_new



class ConvertNull(ETL):
    
    def __init__(self, columns=None, input_value=-1, output_value=np.nan):

        if columns is None:
            self.columns = []
        else:
            self.columns = columns

        self.input_value = input_value
        self.output_value = output_value

    
    def transform(self, X):
        X_new = X.copy()
        X_new[self.columns] = X_new[self.columns].replace(self.input_value, self.output_value)
        return X_new


# ETLs by Natalia Krebesova -------------

class FollowerCountEncoder(ETL):
    
    TARGET_COL = 'artist_followers'

    def __init__(self, strategy='max'):
        self.strategy = strategy
    
    def transform(self, X, y=None):
        '''Pocitanie statistiky je mozne robit v transform pretoze zavisi od hodnoty v riadku nie stlpca (je to tam delimitovane v stringu)'''
        X_new = X.copy()
        
        def process_values(value):
            if pd.isna(value):
                return np.nan
            if ',' in str(value):
                numbers = [int(val.strip()) for val in str(value).split(',')]
                if self.strategy == 'max':
                    return max(numbers)
                elif self.strategy == 'avg':
                    return sum(numbers) / len(numbers)
            else:
                return int(value)
            
        X_new[self.TARGET_COL] = X[self.TARGET_COL].apply(process_values)
        return X_new



class ArtistPopularityEncoder(ETL):
    
    TARGET_COL = 'artist_popularities'

    def __init__(self, strategy='both'):
        self.strategy = strategy
    
    def transform(self, X, y=None):
        '''Pocitanie statistiky je mozne robit v transform pretoze zavisi od hodnoty v riadku nie stlpca (je to tam delimitovane v stringu)'''
        X_new = X.copy()
        
        def process_max(value):
            if pd.isna(value):
                return np.nan
            if ',' in str(value):
                numbers = [int(val.strip()) for val in str(value).split(',')]
                return max(numbers)
            else:
                return int(value)
            
        def process_avg(value):
            if pd.isna(value):
                return np.nan
            if ',' in str(value):
                numbers = [int(val.strip()) for val in str(value).split(',')]
                return sum(numbers) / len(numbers)
            else:
                return int(value)
            
        if self.strategy == 'max':
            X_new[self.TARGET_COL] = X[self.TARGET_COL].apply(process_max)
        elif self.strategy == 'avg':
            X_new[self.TARGET_COL] = X[self.TARGET_COL].apply(process_avg)
        elif self.strategy == 'both':
            X_new[f'{self.TARGET_COL}_max'] = X[self.TARGET_COL].apply(process_max)
            X_new[f'{self.TARGET_COL}_avg'] = X[self.TARGET_COL].apply(process_avg)
            X_new = X_new.drop(columns=[self.TARGET_COL])
            
        return X_new



class AlbumNameEncoder(ETL):

    TARGET_COL = 'album_name'

    def __init__(self):
        self.frequencies = None
        self.default_value = 0
    
    def fit(self, X, y=None):
        '''Tu sa uz transformacia pocita zo stlpca takze statistika je pocitana len z X_train'''
        freqs = X[self.TARGET_COL].value_counts()
        self.frequencies = freqs.to_dict()
        return self
    

    def transform(self, X, y=None):

        X_new = X.copy()
        X_new[self.TARGET_COL] = X[self.TARGET_COL].map(self.frequencies).fillna(self.default_value)
        return X_new
    
    

class GenreEncoder(ETL):
    
    TARGET_COL = 'artist_genres'

    def __init__(self, strategy='max'):
        self.frequencies = None
        self.default_value = 0
        self.strategy = strategy
    
    def fit(self, X, y=None):
        all_genres = []
        for genres_str in X[self.TARGET_COL]:
            if pd.isna(genres_str):
                continue
            artist_groups = genres_str.split('|')
            for artist_genres in artist_groups:
                genres = [g.strip() for g in artist_genres.split(',')]
                all_genres.extend(genres)
        
        freqs = pd.Series(all_genres).value_counts()
        self.frequencies = freqs.to_dict()
        return self
    
    def transform(self, X, y=None):
        X_new = X.copy()
        
        def process_genres(value):
            if pd.isna(value):
                return np.nan
                
            unique_genres = set()
            artist_groups = value.split('|')
            for artist_genres in artist_groups:
                genres = [g.strip() for g in artist_genres.split(',')]
                unique_genres.update(genres)
            
            genre_scores = [self.frequencies.get(genre, self.default_value) 
                          for genre in unique_genres]
            
            if not genre_scores:
                return 0
            
            if self.strategy == 'max':
                return max(genre_scores)
            elif self.strategy == 'avg':
                return sum(genre_scores) / len(genre_scores)
            elif self.strategy == 'sum':
                return sum(genre_scores)
        
        X_new[self.TARGET_COL] = X[self.TARGET_COL].apply(process_genres)
        return X_new


#  --------------------------------------



# --------- Pipelines

numeric_pipeline = Pipeline(steps=[
    ('scaling', StandardScaler())
])


artist_name_pipeline = Pipeline(steps=[
    ('encoding', FrequencyEncoder()),
    ('scaling', StandardScaler())
])

follower_count_pipeline = Pipeline(steps=[
    ('encoding', FollowerCountEncoder()),
    ('scaling', StandardScaler())
])


artist_popularity_pipeline = Pipeline(steps=[
    ('encoding', ArtistPopularityEncoder()),
    ('scaling', StandardScaler())
])


album_name_pipeline = Pipeline(steps=[
    ('encoding', AlbumNameEncoder()),
    ('scaling', StandardScaler())
])


artist_genres_pipeline = Pipeline(steps=[
    ('encoding', GenreEncoder()),
    ('scaling', StandardScaler())
])


transformations = ColumnTransformer(transformers=[
    
    ('onehot_encoding', OneHotEncoder(sparse_output=False), []),
    ('trigonometric_encoding', CircleOfFifthsEncoding(), []),
    ('artist_encoding', artist_name_pipeline, []),
    ('follower_count_encoding', follower_count_pipeline, []),
    ('popularity_encoding', artist_popularity_pipeline, []),
    ('album_encoding', album_name_pipeline, []),
    ('genres_encoding', artist_genres_pipeline, []),
    ('nummeric_processing', numeric_pipeline, [])

], remainder='drop')


preprocessing = Pipeline(steps=[
    ('null_values', ConvertNull(columns=[])),
    ('transformation', transformations)
])

