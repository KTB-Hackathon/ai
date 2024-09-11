import pandas as pd
from sklearn.model_selection import train_test_split
from catboost import CatBoostRegressor, Pool

def load_data():
    df_place = pd.read_csv('./tn_visit_area_info.csv')
    df_travel = pd.read_csv('./tn_travel.csv')
    df_traveler = pd.read_csv('./tn_traveller_master.csv')
    return df_place, df_travel, df_traveler

def merge_data(df_place, df_travel, df_traveler):
    df = pd.merge(df_place, df_travel, on='TRAVEL_ID', how='left')
    df = pd.merge(df, df_traveler, on='TRAVELER_ID', how='left')
    return df

def preprocess_data(df):
    df_filter = df[~df['TRAVEL_MISSION_CHECK'].isnull()].copy()
    df_filter.loc[:, 'TRAVEL_MISSION_INT'] = df_filter['TRAVEL_MISSION_CHECK'].str.split(';').str[0].astype(int)
    df_filter = df_filter[[
        'GENDER', 'AGE_GRP', 'TRAVEL_STYL_1', 'TRAVEL_STYL_2', 'TRAVEL_STYL_3',
        'TRAVEL_STYL_4', 'TRAVEL_STYL_5', 'TRAVEL_STYL_6', 'TRAVEL_STYL_7',
        'TRAVEL_STYL_8', 'TRAVEL_MOTIVE_1', 'TRAVEL_COMPANIONS_NUM', 'TRAVEL_MISSION_INT',
        'VISIT_AREA_NM', 'DGSTFN',
    ]]
    df_filter = df_filter.dropna()
    return df_filter

def encode_categorical_data(df_filter):
    categorical_features_names = [
        'GENDER', 'TRAVEL_STYL_1', 'TRAVEL_STYL_2', 'TRAVEL_STYL_3', 'TRAVEL_STYL_4',
        'TRAVEL_STYL_5', 'TRAVEL_STYL_6', 'TRAVEL_STYL_7', 'TRAVEL_STYL_8',
        'TRAVEL_MOTIVE_1', 'TRAVEL_MISSION_INT', 'VISIT_AREA_NM'
    ]
    df_filter[categorical_features_names[1:-1]] = df_filter[categorical_features_names[1:-1]].astype(int)
    return df_filter, categorical_features_names

def split_data(df_filter):
    return train_test_split(df_filter, test_size=0.2, random_state=42)

def create_model(train_data, test_data, categorical_features_names):
    train_pool = Pool(train_data.drop(['DGSTFN'], axis=1), label=train_data['DGSTFN'], cat_features=categorical_features_names)
    test_pool = Pool(test_data.drop(['DGSTFN'], axis=1), label=test_data['DGSTFN'], cat_features=categorical_features_names)
    model = CatBoostRegressor()
    model.load_model('./catboost_model.cbm')
    return model, train_pool, test_pool

def predict_areas(model, df_filter, traveler):
    area_names = df_filter[['VISIT_AREA_NM']].drop_duplicates()
    results = pd.DataFrame([], columns=['AREA', 'SCORE'])
    for area in area_names['VISIT_AREA_NM']:
        input = list(traveler.values())
        input.append(area)
        score = model.predict(input)
        results = pd.concat([results, pd.DataFrame([[area, score]], columns=['AREA', 'SCORE'])])
    return results

def get_top_20_areas(results):
    top_20_results = results.sort_values('SCORE', ascending=False).head(20)
    top_20_areas = top_20_results['AREA']
    return top_20_areas.to_json(orient='values', force_ascii=False)

def main(traveler):
    df_place, df_travel, df_traveler = load_data()
    df = merge_data(df_place, df_travel, df_traveler)
    df_filter = preprocess_data(df)
    df_filter, categorical_features_names = encode_categorical_data(df_filter)
    train_data, test_data = split_data(df_filter)
    model, train_pool, test_pool = create_model(train_data, test_data, categorical_features_names)
    results = predict_areas(model, df_filter, traveler)
    return get_top_20_areas(results)
