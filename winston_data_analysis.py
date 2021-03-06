# -*- coding: utf-8 -*-
"""

Automatically generated by Colaboratory.

Original file is located at:


# Goals and google drive mount + import modules

Import raw data for both BHM and Control datasets
Cleanse the data:
  - Validation
  - Filter out any non-sensical responses
Analyse both audiences and make sure there's fair representation (look out for any causes of bias e.g bad spread of age groups)
Make sure we have enough responses left to be statistically significant
Visualisations
 - Copy the SM visualations for each question, viewed side-by-side for each group
Max Diff on the feature questions from each group
Discuss statistical differences between each group
Questions we want to answer:
1. Are the groups interested in different features?
2. Is there a difference in the amount they are willing to pay?
3. Is there any other subset from the control group that showed strong interest?
4. Does the data suggest the BMH was the right choice?
5. What features should go in the premium subscription?
6. How much should we charge for the premium subscription?

"""

from google.colab import drive
drive.mount("/content/drive", force_remount=True)

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import csv

"""# Loading data from files and pre-processing"""

# Loading csv files to variables
BHM_raw = pd.read_csv("file_1.csv")
control_raw = pd.read_csv("file_2.csv")
both_BHM_age_raw = pd.read_csv("file_3.csv")
both_not_BHM_age_raw = pd.read_csv("file_4.csv")
both_strict_BHM_raw = pd.read_csv("file_5.csv")
both_strict_not_BHM_raw = pd.read_csv("file_6.csv")

def cleaner1(df):
  ''' Function that cleans up response data for survey 1 (BHM and control).
  Specifically: renames columns for brevity;
  removes redundant and repeat columns and rows; removes rows with missing data; casts columns to specified datatypes;
  and labels columns and index.
  Input and returns: pandas DataFrame object'''

  # Rename column labels: "Unnamed: xx" to "optional" answer, and cut descriptions of features, renaming some questions for brevity
  df.columns = ['Respondent ID', 'Collector ID', 'Start Date', 'End Date', 'IP Address',
       'Email Address', 'First Name', 'Last Name', 'Custom Data 1',
       'collector_type_source', 'Q1', 'Q2', "Q3", 'Q4', 'Q5','Q6', "Q7",'Q8', "Q9",
       'Q10','Q11','Q12','Q13','Q14','Q15','Q16','Q17','Q18', 'Q19','Q20', 'Q21','Q22','Q23','Q24',
       'Q25','Q26','Age', 'Device Type', 'Gender']

  # Remove empty columns and repeat columns
  df_clean = df.drop(["IP Address", "Email Address", "First Name", "Last Name",
                      "Age", "Gender"], axis=1) # <---- Repeat data columns

  # Remove redundant first row of repeat labels
  df_clean.drop(0, inplace=True)

  # Delete skipped feature poll questions NOTE: This is evaluated if the first feature poll question is left blank.
  df_clean.dropna(subset=['Feature 1) and 2)'], inplace=True)

  # Casting columns to correct datatypes
  # Forming converter dictionary from list of column headings then passing converter dictionary to DataFrame.astype() method
  col_list = list(df_clean)
  data_type_list = [int, int, str, str, str, str, int, int, str, int, int, int, str, int, str, int, int, int, str, int, int, int, int,
                    int, int, int, int, int, int, int, int, int, str, int] # Specified data types per column

  convert_dict = dict(zip(col_list, data_type_list))
  df_clean = df_clean.astype(convert_dict)

  # Labeling axes
  df_clean.index.name = "respondents"
  df_clean.columns.name = "questions"

  return df_clean

"""# Data Manipulation Functions"""

def surv1FeatureScore(df_clean):
  ''' Function that calculates the feature score per respondant. Input and returns: pandas DataFrame object'''

  # Creating a Dataframe of respondants' feature poll responses
  features_only = df_clean[['Feature 1) AC2) RR',
                            'Feature 1) AC2) CR',
                            'Feature 1) AC2) SGT',
                            'Feature 1) AC2) JA',
                            'Feature 1) RR 2) CR',
                            'Feature 1) RR 2) SGT',
                            'Feature 1) RR 2) JA',
                            'Feature 1) CR 2) SGT',
                            'Feature 1) CR 2) JA',
                            'Feature 1) SGT 2) JA']]

  # Remove skipped answers
  features_only = features_only.dropna()

  # Creating data feature scores for each respondant as a list
  data = []
  for index, row in features_only.iterrows():

    # Score board
    score_hold = {"AC": 0, "RR": 0, "CR": 0, "SGT": 0, "JA": 0}
    # Tally scores
    if row["Feature 1) AC2) RR"] == 1:
      score_hold["AC"] += 1
    else:
      score_hold["RR"] += 1
    if row["Feature 1) AC2) CR"] == 1:
      score_hold["AC"] += 1
    else:
      score_hold["CR"] += 1
    if row["Feature 1) AC2) SGT"] == 1:
      score_hold["AC"] += 1
    else:
      score_hold["SGT"] += 1
    if row["Feature 1) AC2) JA"] == 1:
      score_hold["AC"] += 1
    else:
      score_hold["JA"] += 1
    #---------------------------------------------------------------------
    if row["Feature 1) RR 2) CR"] == 1:
      score_hold["RR"] += 1
    else:
      score_hold["CR"] += 1
    if row["Feature 1) RR 2) SGT"] == 1:
      score_hold["RR"] += 1
    else:
      score_hold["SGT"] += 1
    if row["Feature 1) RR 2) JA"] == 1:
      score_hold["RR"] += 1
    else:
      score_hold["JA"] += 1
    #---------------------------------------------------------------------
    if row["Feature 1) CR 2) SGT"] == 1:
      score_hold["CR"] += 1
    else:
      score_hold["SGT"] += 1
    if row["Feature 1) CR 2) JA"] == 1:
      score_hold["CR"] += 1
    else:
      score_hold["JA"] += 1
    #---------------------------------------------------------------------
    if row["Feature 1) SGT 2) JA"] == 1:
      score_hold["SGT"] += 1
    else:
      score_hold["JA"] += 1

    # Add score board to data
    data.append(list(score_hold.values()))

  # Create Dataframe
  feature_scores = pd.DataFrame(data, columns=["AC", "RR", "CR", "SGT", "JA"],
                                index=features_only.index)

  return feature_scores

def surv1FeatScorePerPB(df_clean):
  '''Function that returns the feature scores per pay bracket as a list of lists. Uses surv1FeatureScore() function.
  Inner list is the feature scores in the order: AC, RR, CR, SGT, JA
  Outer list is pay brackets in ascending order. '''

  # list of dataframes, each containing respondent answers grouped by pay bracket, in ascending order of pay brackets
  pay_bracket_resp_df_list = [ df_clean[df_clean["Pay Question"]==pb] for pb in range(1,8) ]

  # List of lists, each sublist containing the combined feature scores for each pay bracket in the order specified in function description
  pay_bracket_resp__feat_score_df_list = [ list(surv1FeatureScore(x).sum()) for x in pay_bracket_resp_df_list ]

  return pay_bracket_resp__feat_score_df_list

def surv1FeatScorePerBS(df_clean):
  '''Function that returns the feature scores per living situation as a list of lists. Uses surv1FeatureScore() function.
  Inner list is the feature scores in the order: ALB, BIF, UN, NB
  Outer list is buying sentiment in the above order . '''

  # list of dataframes, each containing respondent answers grouped by Buying sentiment
  living_situation_resp_df_list = [ df_clean[df_clean["Buy Question"]==ls] for ls in range(1,5) ]

  # List of lists, each sublist containing the combined feature scores for each buying sentiment in the order specified in function description
  living_situation_resp_feat_score_df_list = [ list(surv1FeatureScore(x).sum()) for x in living_situation_resp_df_list ]

  return living_situation_resp_feat_score_df_list

"""# Custom Data Graphing Functions"""

def plotFeatScoreVsPay(y_values, which_survey="", percentage=False, line=False):
  '''Fuction that plots a graph of feature scores per pay bracket.
  The graph would have discreet price bands on x axis, and each band would have five plotted bars corresponding to different feature scores
  Input: a list of lists containing feature scores per pay bracket,
  optional arguments: which_survey=str; specify what survey is being plotted in graph title
                      percentage=bool; have feature scores as a percentage of the sum of all feature scores for a given pay bracket,
                      line=bool; visualise as line plot instead of bar (may be a good visualization tool) '''

  plt.style.use("fivethirtyeight") # style selector

  # Data and plotting
  #-----------------------------------------------------------------------------

  if percentage:
    y_values_percent = [ [(element/sum(sublist))*100 for element in sublist] for sublist in y_values]
    y_values = y_values_percent


  if line:
    price_bands_indexes = np.arange(len(y_values)) # Generate a numpy array of consecutive integers' length equal to that of number of pay brackets
    width = 0.1 # How much to space out your bars

    AC_scores = [sublist[0] for sublist in y_values] # y-axis data (as a list)
    plt.plot(price_bands_indexes, AC_scores, color="#d01212", label="AC" )

    RR_scores = [sublist[1] for sublist in y_values] # y-axis data (as a list)
    plt.plot(price_bands_indexes, RR_scores, color="#23ba15", label="RR" )

    CR_scores = [sublist[2] for sublist in y_values] # y-axis data (as a list)
    plt.plot(price_bands_indexes, CR_scores, color="#0d2aee", label="CR" )

    SGT_scores = [sublist[3] for sublist in y_values] # y-axis data (as a list)
    plt.plot(price_bands_indexes, SGT_scores, color="#ffbf00", label="SGT" )

    JA_scores = [sublist[4] for sublist in y_values] # y-axis data (as a list)
    plt.plot(price_bands_indexes, JA_scores, color="#ec25cc", label="JA" )

  else:
    price_bands_indexes = np.arange(len(y_values)) # Generate a numpy array of consecutive integers' length equal to that of number of pay brackets
    width = 0.1 # How much to space out your bars

    AC_scores = [sublist[0] for sublist in y_values] # y-axis data (as a list)
    plt.bar(price_bands_indexes-(2*width), AC_scores, width=width, color="#d01212", label="AC" )

    RR_scores = [sublist[1] for sublist in y_values] # y-axis data (as a list)
    plt.bar(price_bands_indexes-width, RR_scores, width=width, color="#23ba15", label="RR" )

    CR_scores = [sublist[2] for sublist in y_values] # y-axis data (as a list)
    plt.bar(price_bands_indexes, CR_scores, width=width, color="#0d2aee", label="CR" )

    SGT_scores = [sublist[3] for sublist in y_values] # y-axis data (as a list)
    plt.bar(price_bands_indexes+width, SGT_scores, width=width, color="#ffbf00", label="SGT" )

    JA_scores = [sublist[4] for sublist in y_values] # y-axis data (as a list)
    plt.bar(price_bands_indexes+(2*width), JA_scores, width=width, color="#ec25cc", label="JA" )
  #-----------------------------------------------------------------------------

  # Labelling
  plt.legend()

  plt.xticks(ticks=price_bands_indexes,
             labels=["Would not pay",
                     "??0.01 -\n ??0.99",
                     "??1.00 -\n ??2.99",
                     "??3.00 -\n ??4.99",
                     "??5.00 -\n ??6.99",
                     "??7.00 -\n ??9.99",
                     "??10.00+"])

  plt.title(f"Feature Scores per Price Band {which_survey}")
  plt.xlabel("Price Band")

  if percentage:
    plt.ylabel("Feature score (%)")
  else:
    plt.ylabel("Feature score")

  plt.tight_layout()

  plt.show()

def plotFeatScoreBuySent(y_values, which_survey="", percentage=False, line=False):
  '''Fuction that plots a graph of feature scores per buying sentiment.
  The graph would have buying sentiment opinions on x axis, and each opinion would have five plotted bars corresponding to different feature scores
  Input: a list of lists containing feature scores per buying sentiment,
  optional arguments: which_survey=str; specify what survey is being plotted in graph title
                      percentage=bool; have feature scores as a percentage of the sum of all feature scores for a given buy sentiment,
                      line=bool; visualise as line plot instead of bar (may be a good visualization tool) '''

  plt.style.use("fivethirtyeight") # style selector

  # Data and plotting
  #-----------------------------------------------------------------------------

  if percentage:
    y_values_percent = [ [(element/sum(sublist))*100 for element in sublist] for sublist in y_values]
    y_values = y_values_percent


  if line:
    price_bands_indexes = np.arange(len(y_values)) # Generate a numpy array of consecutive integers' length equal to that of number of pay brackets
    width = 0.1 # How much to space out your bars

    AC_scores = [sublist[0] for sublist in y_values] # y-axis data (as a list)
    plt.plot(price_bands_indexes, AC_scores, color="#d01212", label="AC" )

    RR_scores = [sublist[1] for sublist in y_values] # y-axis data (as a list)
    plt.plot(price_bands_indexes, RR_scores, color="#23ba15", label="RR" )

    CR_scores = [sublist[2] for sublist in y_values] # y-axis data (as a list)
    plt.plot(price_bands_indexes, CR_scores, color="#0d2aee", label="CR" )

    SGT_scores = [sublist[3] for sublist in y_values] # y-axis data (as a list)
    plt.plot(price_bands_indexes, SGT_scores, color="#ffbf00", label="SGT" )

    JA_scores = [sublist[4] for sublist in y_values] # y-axis data (as a list)
    plt.plot(price_bands_indexes, JA_scores, color="#ec25cc", label="JA" )

  else:
    price_bands_indexes = np.arange(len(y_values)) # Generate a numpy array of consecutive integers' length equal to that of number of pay brackets
    width = 0.1 # How much to space out your bars

    AC_scores = [sublist[0] for sublist in y_values] # y-axis data (as a list)
    plt.bar(price_bands_indexes-(2*width), AC_scores, width=width, color="#d01212", label="AC" )

    RR_scores = [sublist[1] for sublist in y_values] # y-axis data (as a list)
    plt.bar(price_bands_indexes-width, RR_scores, width=width, color="#23ba15", label="RR" )

    CR_scores = [sublist[2] for sublist in y_values] # y-axis data (as a list)
    plt.bar(price_bands_indexes, CR_scores, width=width, color="#0d2aee", label="CR" )

    SGT_scores = [sublist[3] for sublist in y_values] # y-axis data (as a list)
    plt.bar(price_bands_indexes+width, SGT_scores, width=width, color="#ffbf00", label="SGT" )

    JA_scores = [sublist[4] for sublist in y_values] # y-axis data (as a list)
    plt.bar(price_bands_indexes+(2*width), JA_scores, width=width, color="#ec25cc", label="JA" )
  #-----------------------------------------------------------------------------

  # Labelling
  plt.legend()

  plt.xticks(ticks=price_bands_indexes,
             labels=["Label 1",
                     "Label 2",
                     "Label 3",
                     "Label 4"])

  plt.title(f"Feature Scores per BUY {which_survey}")
  plt.xlabel("BS")

  if percentage:
    plt.ylabel("Feature score (%)")
  else:
    plt.ylabel("Feature score")

  plt.tight_layout()

  plt.show()

"""# Debug Window"""

BHM = cleaner1(BHM_raw)
# BHM

surv1FeatScorePerPB(BHM)

"""# Data clean and processing"""

# BHM survey variables
BHM = cleaner1(BHM_raw) # Clean survey

BHM_featscore = surv1FeatureScore(BHM).sum() # Feature scores for each respondent
BHM_featscore_perPB = surv1FeatScorePerPB(BHM) # Feature scores per pay bracket
BHM_featscore_perBS = surv1FeatScorePerBS(BHM)

# Control survey variables
control = cleaner1(control_raw) # Clean survey

control_featscore = surv1FeatureScore(control).sum() # Feature scores for each respondent
control_featscore_perPB = surv1FeatScorePerPB(control) # Feature scores per pay bracket
control_featscore_perBS = surv1FeatScorePerBS(control)

# both survey with strict BHM criteria
both_strict_BHM = cleaner1(both_strict_BHM_raw) # Clean survey

both_strict_BHM_featscore = surv1FeatureScore(both_strict_BHM).sum() # Feature scores for each respondent
both_strict_BHM_featscore_perPB = surv1FeatScorePerPB(both_strict_BHM) # Feature scores per pay bracket
both_strict_BHM_featscore_perBS = surv1FeatScorePerBS(both_strict_BHM)

# both survey with strictly NOT BHM criteria
both_strict_not_BHM = cleaner1(both_strict_not_BHM_raw) # Clean survey

both_strict_not_BHM_featscore = surv1FeatureScore(both_strict_not_BHM).sum() # Feature scores for each respondent
both_strict_not_BHM_featscore_perPB = surv1FeatScorePerPB(both_strict_not_BHM) # Feature scores per pay bracket
both_strict_not_BHM_featscore_perBS = surv1FeatScorePerBS(both_strict_not_BHM)

# both survey BHM age
both_BHM_age = cleaner1(both_BHM_age_raw) # Clean survey

both_BHM_age_featscore = surv1FeatureScore(both_BHM_age).sum() # Feature scores for each respondent
both_BHM_age_featscore_perPB = surv1FeatScorePerPB(both_BHM_age) # Feature scores per pay bracket
both_BHM_age_featscore_perBS = surv1FeatScoreBuySent(both_BHM_age)

# both survey NOT BHM age
both_not_BHM_age = cleaner1(both_not_BHM_age_raw) # Clean survey

both_not_BHM_age_featscore = surv1FeatureScore(both_not_BHM_age).sum() # Feature scores for each respondent
both_not_BHM_age_featscore_perPB = surv1FeatScorePerPB(both_not_BHM_age) # Feature scores per pay bracket
both_not_BHM_age_featscore_perBS = surv1FeatScorePerBS(both_not_BHM_age)

"""# Data Graphing"""

# Plot size parameters
plt.rcParams['figure.figsize'] = [12, 8]
plt.rcParams['figure.dpi'] = 100

"""### Pay Bracket

Single surveys
"""

# BHM Features score
BHM_featscore.plot(kind="bar", title="Total Feature Scores (BHM Survey)")

# BHM feature score per price band plot
plotFeatScoreVsPay(BHM_featscore_perPB, "(BHM survey)", percentage=True)

# Control Features score
control_featscore.plot(kind="bar", title="Total Feature Scores (Control Survey)")

# Control feature score per price band plot
plotFeatScoreVsPay(control_featscore_perPB, "(Control survey)", percentage=True)

"""Both surveys: BHM criteria"""

# Both surveys with strict BHM criteria features score
both_strict_BHM_featscore.plot(kind="bar", title="Total Feature Scores (both surveys: BHM criteria)")

# Both surveys with strict BHM criteria features score per price band
plotFeatScoreVsPay(both_strict_BHM_featscore_perPB, "(Both surveys: BHM Criteria)", percentage=False, line=True)

# Both surveys with strict BHM criteria features score per buying sentiment
plotFeatScoreBuySent(both_strict_BHM_featscore_perBS, "(Both surveys: BHM Criteria)", percentage=False, line=False)



# Both surveys with strictly NOT BHM criteria features score
both_strict_not_BHM_featscore.plot(kind="bar", title="Total Feature Scores (both surveys: not BHM criteria)")

# Both surveys with strictly NOT BHM criteria features score per price band
plotFeatScoreVsPay(both_strict_not_BHM_featscore_perPB, "(Both surveys: not BHM Criteria)", percentage=False, line=True)

# Both surveys with strictly NOT BHM criteria features score buy sentiment
plotFeatScoreBuySent(both_strict_not_BHM_featscore_perBS, "(Both surveys: not BHM Criteria)", percentage=False, line=False)

"""Both Surveys: BHM age"""

# Both surveys BHM age features score
both_BHM_age_featscore.plot(kind="bar", title="Total Feature Scores (both surveys: Age range (25-34))")

# Both surveys BHM age feature score per price band
plotFeatScoreVsPay(both_BHM_age_featscore_perPB, "(both surveys: Age range (25-34))", percentage=False, line=True)

# Both surveys BHM age feature score per buying sentiment
plotFeatScoreBuySent(both_BHM_age_featscore_perBS, "(both surveys: Age range (25-34))", percentage=False, line=False)



# Both surveys not BHM age features score
both_not_BHM_age_featscore.plot(kind="bar", title="Total Feature Scores (both surveys: Outside age range (25-34))")

# Both surveys not BHM age feature score per price band
plotFeatScoreVsPay(both_not_BHM_age_featscore_perPB, "(both surveys: Outside age range (25-34))", percentage=False, line=True)

# Both surveys not BHM age feature score per buying sentiment
plotFeatScoreBuySent(both_not_BHM_age_featscore_perBS, "(both surveys: Outside age range (25-34))", percentage=False, line=False)
